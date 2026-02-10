import os
from pathlib import Path
from time import sleep

from code_editor import code_editor
import  streamlit as st

from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs


def carregar_modulos_venv():
    from Banco_dados import gerar_predefinidos_com_links
    from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO

    # ===== Exemplo de uso no editor =====
    def_from, def_predefinidos, from_predefinidos = gerar_predefinidos_com_links()

    import sys
    import pkgutil
    from pathlib import Path
    _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
    site_packages = Path(_Venv_path) / "Lib" / "site-packages"
    sys.path.insert(0, str(site_packages))

    modulos = {}

    # módulos da venv
    for m in pkgutil.iter_modules([str(site_packages)]):
        modulos[m.name] = [m.name]

    # módulos do projeto (def_from)
    for nome, dados in def_from.items():
        modulos[nome] =  os.path.basename(dados["caminho"])

    # 3. Fontes personalizadas
    outras_fontes = [
        {"nome": "filha", "valor": "isadora"},
        {"nome": "amigo", "valor": "joao"}
    ]
    for item in outras_fontes:
        modulos[item["nome"]] = item["valor"]

    return modulos


def Completar(st):
    if "modulos_venv" not in st.session_state:
        st.session_state.modulos_venv = carregar_modulos_venv()

    completions = []
    for nome, origem in st.session_state.modulos_venv.items():
        completions.append({
            "caption": nome,
            "value": nome,
            "meta": origem,
            "name": nome,
            "score": 400
        })

    return completions



# QUANDO USUÁRIO ABRIR UM ARQUIVO
caminho = Path(r"C:\Users\henri\ProjetoSteamIDE\HENRIQUE\main.py")
nome_arquivo = os.path.basename(caminho)

conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, caminho)


def Atalhos():
    return {
        # Salvar/Executar
        "Ctrl-S": "save",
        "F5": "execute",
        "Ctrl-F5": "run-selection",

        # Edição rápida (← ADICIONEI Ctrl+X AQUI!)
        "Ctrl-/": "togglecomment",
        "Ctrl-D": "selectnext",
        "Alt-Up": "moveup",
        "Alt-Down": "movedown",

        # Navegação
        "Ctrl-P": "gotolinestart",
        "Ctrl-L": "jumptoline",

        # Streamlit específico
        "Ctrl-Shift-R": "rerun",
    }


# 📝 EDITOR COM KEY ÚNICA
codigo = code_editor(
    conteudo_inicial,  # ← CARREGA DO CACHE!
    lang='python',
    height=f'300px',
    shortcuts='vscode',
    completions=Completar(st),
    response_mode=["blur"],

    key=f"editor_militar_"  # 🔐 ÚNICA!
)

novo_codigo = codigo.get('text', '') if isinstance(codigo, dict) else str(codigo) if codigo else ""

from Banco_dados import checar_modulos_locais, reset_db, scan_project
# 📥 EXTRAI CÓDIGO ATUAL

checar_modulos_locais( st,5411, novo_codigo, nome_arquivo, caminho)



if st.button(f':material/lock_reset:', key=f"botao_restart_alt{5411}"):
    reset_db()
    scan_project()
