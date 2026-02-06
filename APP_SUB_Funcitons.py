import json
import subprocess
import textwrap
from pathlib import Path



from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_
# ===== FIX WINDOWS: NÃO ABRIR CMD / POWERSHELL =====
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW

def data_sistema():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def Alerta(st,msg):
    @st.dialog("Alerta ")
    def menu_principal():
        st.warning(msg)
    menu_principal()

def Linha_Sep(Cor,Larg):
    import streamlit.components.v1 as components

    HtmL =f'<div style="display: block; background-color: {Cor}; width: 100%; height: {Larg}px;"></div>'
    return components.html(HtmL, height=Larg, scrolling=False)



def Criar_Arquivo_TEXTO(caminho, titulo, conteudo, ext):
    caminho_txt =rf"{caminho}\\{titulo}{ext}"

    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho_txt

def wrap_text(text, width=80):
    # Quebra o texto nas linhas originais
    lines = text.splitlines()
    wrapped_lines = []
    for line in lines:
        # Aplica wrap apenas em cada linha separadamente
        wrapped_lines.extend(textwrap.wrap(line, width=width) or [""])
    return "\n".join(wrapped_lines)

# Henrique, essa função é só pra olhar na pasta se tem um arquivo com o mesmo nome e se tiver ele procura outro nome diferente.
def gerar_nome_unico(pasta_base: Path, nome_desejado: str) -> Path:
    """
    Gera um caminho único dentro de pasta_base.
    Ex:
    Projeto
    Projeto_2
    Projeto_3
    """
    pasta_base = Path(pasta_base)
    nome_desejado = nome_desejado.strip()

    caminho = pasta_base / nome_desejado
    if not caminho.exists():
        return caminho

    contador = 2
    while True:
        novo_nome = f"{nome_desejado}_{contador}"
        novo_caminho = pasta_base / novo_nome
        if not novo_caminho.exists():
            return novo_caminho
        contador += 1

# -------------------------------
# 1️⃣ Sincroniza estrutura do projeto corretamente
# -------------------------------
def contar_estrutura(caminho_base):
    caminho_base = Path(caminho_base).resolve()

    nomes_envs = {
        ".venv",
        "venv",
        "env",
        ".virto_stream",
        ".tox",
        ".nox",
        "__pypackages__"
    }

    pastas_excluidas = {
        "__pycache__",
        ".git",
        ".idea"
    }.union(nomes_envs)

    total_pastas = 0
    total_arquivos = 0
    arquivos_por_extensao = defaultdict(int)
    pastas_datas = []
    python_envs = []

    # ambientes Python
    for nome_env in nomes_envs:
        env_path = caminho_base / nome_env
        if not env_path.exists():
            continue

        python_exec = env_path / "Scripts" / "python.exe"
        if not python_exec.exists():
            python_exec = env_path / "bin" / "python"

        if python_exec.exists():
            try:
                versao = subprocess.check_output(
                    [str(python_exec), "--version"],
                    stderr=subprocess.STDOUT,
                    text=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_FLAGS
                ).strip()

            except Exception:
                versao = None

            python_envs.append({
                versao
            })

    for root, dirs, files in os.walk(caminho_base):
        dirs[:] = [d for d in dirs if d not in pastas_excluidas]

        for d in dirs:
            pasta_path = Path(root) / d
            st = pasta_path.stat()
            total_pastas += 1

            pastas_datas.append({
                "criado": datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modificado": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

        for f in files:
            total_arquivos += 1
            ext = Path(f).suffix.lower() or "SEM"
            arquivos_por_extensao[ext] += 1

    return {
        "pastas": total_pastas,
        "arquivos": total_arquivos,
        "extensao": dict(arquivos_por_extensao),
        "datas": pastas_datas,
        "versoes": python_envs
    }

def limpar_CASH():
    import streamlit as st
    st.cache_data.clear()
    st.cache_resource.clear()

def saudacao_por_hora_sistema() -> str:
    hora = datetime.now().hour

    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    elif 18 <= hora < 23:
        return "Boa noite"
    else:
        return "Boa madrugada"

import os
from collections import defaultdict
from datetime import datetime

def resumo_pasta(caminho_pasta):
    caminho_pasta = Path(caminho_pasta).resolve()

    pastas_excluidas = {
        ".venv",
        "venv",
        "env",
        ".virto_stream",
        ".tox",
        ".nox",
        "__pypackages__",
        "__pycache__",
        ".git",
        ".idea"
    }

    total_pastas = 0
    total_arquivos = 0
    arquivos_por_extensao = defaultdict(int)

    for root, dirs, files in os.walk(caminho_pasta):
        dirs[:] = [d for d in dirs if d not in pastas_excluidas]

        total_pastas = len(dirs)

        for f in files:
            total_arquivos += 1
            ext = Path(f).suffix.lower() or "SEM"
            arquivos_por_extensao[ext] += 1

        break

    st = caminho_pasta.stat()

    return {
        "pasta": caminho_pasta.name,
        "criado": datetime.fromtimestamp(st.st_ctime).strftime("%d/%m/%Y %H:%M"),
        "modificado": datetime.fromtimestamp(st.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "subpastas": total_pastas,
        "arquivos": total_arquivos,
        "extensoes": dict(arquivos_por_extensao)
    }

def sincronizar_estrutura(caminho_arquivo=None):
    """
    Varre o projeto em pasta_base e salva JSON dentro de .virto_stream
    SE caminho_arquivo: PRIMEIRO verifica JSON, SE NÃO acha → varre filesystem
    """

    pasta_base = Path(_DIRETORIO_PROJETO_ATUAL_())
    nome_projeto = pasta_base.name
    caminho_raiz_absoluto = str(pasta_base)
    json_dir = pasta_base / ".virto_stream"
    json_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / "Arvore_projeto.json"

    # 2️⃣ VARRE FILESYSTEM
    estrutura = {"pastas": [], "arquivos": []}
    estrutura["pastas"].append(caminho_raiz_absoluto)

    for root, dirs, files in os.walk(pasta_base):
        dirs[:] = [d for d in dirs if d != ".virto_stream"]
        pasta_rel = str(Path(root).relative_to(pasta_base))

        if pasta_rel != "." and pasta_rel not in estrutura["pastas"]:
            estrutura["pastas"].append(pasta_rel)

        for arquivo in files:
            caminho_rel = str(Path(root).joinpath(arquivo).relative_to(pasta_base))
            pasta_completa = str(Path(root).resolve())  # ← COMO VOCÊ QUER

            estrutura["arquivos"].append({
                "nome": arquivo,
                "caminho_rel": caminho_rel,
                "pasta_completa": pasta_completa
            })

    # 3️⃣ SALVA JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(estrutura, f, indent=2, ensure_ascii=False)

    if caminho_arquivo:

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                estrutura = json.load(f)

            # ✅ BUSCA pelo caminho_rel (tolerante a erros)
            for arq in estrutura["arquivos"]:
                print()
                #print(arq["pasta_completa"]) # --------------------------> henrique nao sei pq MAIS AQUI SAINO EDITOR DE PREVIEM

                if str(arq["pasta_completa"]) in str(caminho_arquivo):
                    return True
                else:
                    return False

        except (json.JSONDecodeError, KeyError):pass
    return estrutura

from pathlib import Path

def Identificar_linguagem(arquivo):
    EXT_MAP = {
        ".py": "python",
        ".txt": "texto",
        ".js": "javaScript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".cpp": "c++",
        ".java": "java",
        ".php": "php",
        ".rb": "ruby",

        ".mp4": "video",
        ".avi": "video",
        ".mov": "video",
        ".mkv": "video",

        ".mp3": "audio",
        ".wav": "audio",
        ".ogg": "audio",

        ".png": "imagem",
        ".jpg": "imagem",
        ".jpeg": "imagem",
        ".gif": "imagem",
        ".webp": "imagem",

        ".pdf": "pdf"
    }

    _, ext = os.path.splitext(arquivo)
    return EXT_MAP.get(ext.lower(), "Desconhecido")


def Sinbolos(arquivo):
    arquivo = Path(arquivo)

    ICONES_EXT = {
        ".py": "🐍",
        ".txt": "📄",
        ".js": "⚡",
        ".html": "🌐",
        ".css": "🎨",
        ".json": "📋",
        ".md": "📝",
        ".cpp": "🔧",
        ".java": "☕",
        ".php": "🐘",
        ".rb": "💎",

        ".mp4": "🎬",
        ".avi": "🎬",
        ".mov": "🎬",
        ".mkv": "🎬",

        ".mp3": "🎵",
        ".wav": "🎵",
        ".ogg": "🎵",

        ".png": "🖼️",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".gif": "🖼️",
        ".webp": "🖼️",

        ".pdf": "📕",

        ".cfg": "⚙️",
        ".pth": "🧠",
        ".db": "🗄️"
    }

    return ICONES_EXT.get(arquivo.suffix.lower(), "📦")

def Testar_Fluxo_Run(st, col, marca=None):
    import time
    agora = time.time()

    if "trafego" not in st.session_state:
        st.session_state.trafego = {}

    t = st.session_state.trafego

    if "reruns" not in t:
        t["reruns"] = 0
    if "inicio" not in t:
        t["inicio"] = agora
    if "ultimo" not in t:
        t["ultimo"] = None
    if "intervalos" not in t:
        t["intervalos"] = []
    if "marcas" not in t:
        t["marcas"] = {}

    t["reruns"] += 1

    if t["ultimo"] is not None:
        t["intervalos"].append(agora - t["ultimo"])

    t["ultimo"] = agora

    tempo_total = agora - t["inicio"]

    col.write(f"Fluxo passou: {t['reruns']}\tTempo: {tempo_total:.3f}")

    if marca is not None:
        if marca not in t["marcas"]:
            t["marcas"][marca] = agora
        else:
            delta = agora - t["marcas"][marca]
            col.write(f"Delta '{marca}': {delta:.3f}s")
            del t["marcas"][marca]


def Button_Nao_Fecha(nome_aberto, nome_fechado, key, fechar_outras=None):
    import streamlit as st

    state_key = f"{key}_state"
    widget_key = f"{key}_widget"

    if state_key not in st.session_state:
        st.session_state[state_key] = False

    def toggle():
        st.session_state[state_key] = not st.session_state[state_key]
        if fechar_outras:
            for k in fechar_outras:
                st.session_state[f"{k}_state"] = False

    if st.session_state[state_key]:
        st.button(
            nome_aberto,
            key=widget_key,
            on_click=toggle,
            width='stretch',
            type="primary"
        )
    else:
        st.button(
            nome_fechado,
            key=widget_key,
            on_click=toggle,
            width='stretch',
            type="secondary"
        )

    return st.session_state[state_key]

    '''  EXEMPLI DE USO:
    aberto = Button_Nao_Fecha(
        nome_aberto="Painel aberto",
        nome_fechado="Abrir painel",
        key="painel_exemplo"
    )
    
    if aberto:
        st.markdown("### Conteúdo do painel")
        st.write("Qualquer coisa aqui dentro")
    
        # BOTÃO INTERNO QUE FECHA
        if st.button("Fechar painel", key="fechar_painel"):
            st.session_state["painel_exemplo_state"] = False
            st.rerun()
    '''

def chec_se_arq_do_projeto(Arq_Selec_Diretorios):
    pasta_base = Path(_DIRETORIO_PROJETO_ATUAL_())
    nomes_com_path = []



    for arquivo in Arq_Selec_Diretorios:
        arquivo = Path(arquivo)
        icone = Sinbolos(arquivo)

        try:
            eh_do_projeto = sincronizar_estrutura(str(arquivo)) is True
        except Exception:
            eh_do_projeto = False

        if eh_do_projeto:
            try:
                caminho_rel = arquivo.relative_to(pasta_base)
                exibicao = f"{caminho_rel.name}"
            except Exception:
                exibicao = f"{arquivo.name}"
            nomes_com_path.append(f"{icone} {exibicao}")
        else:
            exibicao = f"{arquivo.name}/{arquivo.parent.name}"
            nomes_com_path.append(f"{icone} {exibicao}")

    return nomes_com_path

def controlar_altura(st,
    chave,
    altura_inicial=100,
    passo=10,
    minimo=0,
    maximo=None
):
    estado_altura = f"{chave}_altura"

    if estado_altura not in st.session_state:
        st.session_state[estado_altura] = altura_inicial


    if st.button(":material/keyboard_double_arrow_up:", key=f"{chave}_mais"):
        st.session_state[estado_altura] += passo

    if st.button(":material/keyboard_double_arrow_down:", key=f"{chave}_menos"):
        st.session_state[estado_altura] -= passo

    if st.session_state[estado_altura] < minimo:
        st.session_state[estado_altura] = minimo

    if maximo is not None and st.session_state[estado_altura] > maximo:
        st.session_state[estado_altura] = maximo

    return st.session_state[estado_altura]

def controlar_altura_horiz(st,
    chave,
    altura_inicial=100,
    passo=10,
    minimo=0,
    maximo=None
):
    estado_altura = f"{chave}_altura1"

    if estado_altura not in st.session_state:
        st.session_state[estado_altura] = altura_inicial
    st1,st2 = st.columns(2)

    if st1.button(":material/keyboard_double_arrow_down:", key=f"{chave}_mais1"):
        st.session_state[estado_altura] += passo

    if st2.button(":material/keyboard_double_arrow_up:", key=f"{chave}_menos1"):
        st.session_state[estado_altura] -= passo

    if st.session_state[estado_altura] < minimo:
        st.session_state[estado_altura] = minimo

    if maximo is not None and st.session_state[estado_altura] > maximo:
        st.session_state[estado_altura] = maximo

    return st.session_state[estado_altura]
import colorsys
import re

def cor_semelhante(cor_css, delta_l=0.08):
    cor_css = cor_css.strip()

    # Tenta extrair HEX
    hex_match = re.search(r'#([0-9a-fA-F]{6})', cor_css)
    if hex_match:
        hex_color = hex_match.group(0)
    else:
        # Tenta extrair rgba(r,g,b,a)
        rgba_match = re.search(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})', cor_css)
        if rgba_match:
            r, g, b = map(int, rgba_match.groups())
            hex_color = '#{:02X}{:02X}{:02X}'.format(r, g, b)
        else:
            raise ValueError(f"Não foi possível extrair cor de: {cor_css}")

    # Conversão para HLS
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0

    h, l, s = colorsys.rgb_to_hls(r, g, b)

    l = max(0.0, min(1.0, l + delta_l))

    r, g, b = colorsys.hls_to_rgb(h, l, s)

    return '#{:02X}{:02X}{:02X}'.format(
        int(r * 255),
        int(g * 255),
        int(b * 255)
    )



def carregar_imagem_segura(caminho_relativo: str, titulo: str = ""):
    import streamlit as st
    import pathlib
    from PIL import Image
    import os

    """
    Função segura para carregar imagens no Streamlit
    """
    # Converte para caminho absoluto
    caminho = pathlib.Path(caminho_relativo)

    # Verifica se existe
    if not caminho.exists():
        st.error(f"❌ Imagem não encontrada: {caminho.absolute()}")
        st.info(f"Pasta atual: {pathlib.Path.cwd()}")
        return None

    # Verifica permissões
    if not os.access(caminho, os.R_OK):
        st.error(f"❌ Sem permissão para ler: {caminho}")
        return None

    try:
        # Carrega com PIL e mostra no Streamlit
        imagem = Image.open(caminho)
        st.image(imagem, caption=titulo, width='stretch')
        return imagem
    except Exception as e:
        st.error(f"❌ Erro ao abrir imagem: {str(e)}")
        return None




def escreve(texto):
    import  streamlit as st
    return st.write(texto)
