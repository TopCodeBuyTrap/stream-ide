import json
import os
import time
from pathlib import Path

from APP_Code_Editor.Botoes import botao_aplica_cursor, Botoes
from Banco_dados import checar_modulos_locais, reset_db, scan_project
from code_editor import code_editor
import streamlit as st
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs
from Banco_dados import gerar_auto_complete_EDITOR
from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO, _DIRETORIO_PROJETO_ATUAL_

def_from, def_predefinidos, from_predefinidos = gerar_auto_complete_EDITOR()


def carregar_modulos_venv():
    import sys
    import pkgutil
    _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
    site_packages = Path(_Venv_path) / "Lib" / "site-packages"
    sys.path.insert(0, str(site_packages))
    modulos = {}
    for m in pkgutil.iter_modules([str(site_packages)]):
        modulos[m.name] = [m.name]
    for nome, dados in def_predefinidos.items():
        modulos[nome] = os.path.basename(dados["caminho"])
    outras_fontes = [{"nome": "filha", "valor": "isadora"}, {"nome": "amigo", "valor": "joao"}]
    for item in outras_fontes:
        modulos[item["nome"]] = item["valor"]
    return modulos


def Completar(st):
    if "modulos_venv" not in st.session_state:
        st.session_state.modulos_venv = carregar_modulos_venv()
    completions = []
    for nome, origem in st.session_state.modulos_venv.items():
        completions.append({"caption": nome, "value": nome, "meta": origem, "name": nome, "score": 400})
    return completions


_ = st.session_state

# ========================================
# 🔥 DETECÇÃO IMEDIATA - PRIMEIRA COISA QUE RODA
# ========================================
caminho = Path(r"C:\Users\henri\ProjetoSteamIDE\HENRIQUE\main.py")
nome_arq = os.path.basename(caminho)
aba_id = 42


# Chave única para hash por aba/arquivo
chave_hash = f"hash_{aba_id}_{nome_arq}"
chave_ultima_checagem = f"ultima_checagem_{aba_id}_{nome_arq}"

# Inicializa se não existir
if chave_ultima_checagem not in _:
    _[chave_ultima_checagem] = 0

def calcular_hash_arquivo(caminho: Path) -> str:
    """Calcula hash simples (tamanho + data mod) do arquivo."""
    if not caminho.exists():
        return ""
    stat = caminho.stat()
    return f"{stat.st_size}_{stat.st_mtime}"  # Hash único se mudar[web:13]

# Detecta mudança no arquivo
hash_atual = calcular_hash_arquivo(caminho)
hash_anterior = _[chave_hash] if chave_hash in _ else None

if hash_atual != hash_anterior:
    # Arquivo MUDOU! Atualiza hashes e força rerun para recarregar TUDO
    _[chave_hash] = hash_atual
    _[chave_ultima_checagem] = 0  # Reset checagem
    st.rerun()  # ✅ Refresh TOTAL: Abrir_Arquivo_Select_Tabs roda de novo → editor atualiza![cite:1][web:15]


# AGORA carrega o conteúdo (roda toda vez após rerun)
conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, caminho)  # Sua função original
conteudo_inicial_ou_modificado, faltando, logs = checar_modulos_locais(aba_id, conteudo_inicial)

with st.popover(f':material/functions: Minhas Funçoes:'):
    with st.container(border=True, height=200):
        st.code("\n".join(logs), language="bash")
        st.write(faltando)
        st.code(conteudo_inicial_ou_modificado)

# ========================================
editor_key = f"editor_militar_{aba_id}_{nome_arq}"

# Prepara dict pro fluxo do botao_aplica_cursor
editor_dict = {
    "text": conteudo_inicial,
    "cursor": st.session_state.get("cursor_pos", {"row": 0, "column": 0}),
    "type": "submit"
}

# Aplica o texto faltando no cursor
editor_dict = botao_aplica_cursor(st,editor_dict,f'{"\n".join(conteudo_inicial_ou_modificado)}\n'
)

# Atualiza cursor na sessão
st.session_state.cursor_pos = editor_dict.get("cursor", {"row": 0, "column": 0})

# Pega texto atualizado
novo_codigo = editor_dict.get("text", "")

st.write(True if len(faltando) > 0 else False)

# Editor CORRIGIDO
codigo = code_editor(
    novo_codigo,  # <- aqui vai o texto atualizado, não conteudo_inicial
    lang='python',
    height='300px',
    shortcuts='vscode',
    completions=Completar(st),
    response_mode=["blur"],
    allow_reset=True if len(faltando) > 0 else False,
    buttons=Botoes(faltando,'\n'.join(faltando),'True'),
    key=editor_key
)

codigo = botao_aplica_cursor(st,codigo,f'{"\n".join(conteudo_inicial_ou_modificado)}\n',)


novo_codigo = codigo.get('text', '') if isinstance(codigo, dict) else str(codigo) if codigo else ""
st.code(f'Código:\n{novo_codigo}')

# AUTOSAVE MILITAR
if novo_codigo.strip() and novo_codigo != conteudo_inicial_ou_modificado and conteudo_inicial:
    cache_key = f"cache_editor_{aba_id}_{nome_arq}"
    _[cache_key] = novo_codigo
    st.success("💾 AUTOSAVE: Cache OK")

    try:
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        backup_path = Path(caminho).with_suffix('.py.bak')
        if Path(caminho).exists():
            Path(caminho).rename(backup_path)
        Path(caminho).write_text(novo_codigo, encoding='utf-8')
        if backup_path.exists():
            backup_path.unlink()
        _['autosave_status'] = f"💾 {nome_arq}"
        st.success("💾 AUTOSAVE: Disco OK")
    except Exception as e:
        emergencia_path = Path(_DIRETORIO_PROJETO_ATUAL_()) / f"EMERGENCIA_{nome_arq}.json"
        emergencia_path.write_text(
            json.dumps({"timestamp": time.time(), "codigo": novo_codigo, "erro": str(e)}, ensure_ascii=False, indent=2),
            encoding='utf-8')
        st.error(f"⚠️ EMERGÊNCIA: {e}")


    # REPROCESSA ANALISE APÓS SALVAR
    _, faltando, logs = checar_modulos_locais(
        aba_id,
        novo_codigo
    )
if st.button(f':material/lock_reset:', key=f"botao_restart_alt{aba_id}"):
    reset_db()
    scan_project()
