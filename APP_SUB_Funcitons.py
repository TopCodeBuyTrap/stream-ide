import json
import subprocess
import textwrap
from pathlib import Path

import ast
import re
from typing import List, Dict, Any, Optional


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
    return components.html(HtmL, height=Larg+9, scrolling=False)


# ============================================================
# PARSE AST SEGURO
# ============================================================
def _parse_ast(codigo: str) -> Optional[ast.AST]:
    try:
        return ast.parse(codigo)
    except SyntaxError:
        return None


# ============================================================
# ANNOTATIONS PROFISSIONAIS (GUTTER SIMPLES, HOVER RICO)
# ============================================================
def Anotations_Editor(codigo: str) -> List[Dict[str, Any]]:
    annotations: List[Dict[str, Any]] = []
    linhas = codigo.split("\n")
    tree = _parse_ast(codigo)

    def add(row: int, level: str, emoji: str, msg: str):
        annotations.append({
            "row": row,
            "type": level,              # controla ❌ ou ⚠️
            "text": f"{emoji} {msg}"    # aparece SOMENTE no hover
        })

    # --------------------------------------------------------
    # 1. ANÁLISE TEXTUAL
    # --------------------------------------------------------
    for i, linha in enumerate(linhas):
        l = linha.strip()

        if re.search(r"\b(TODO|FIXME|BUG|HACK|XXX|NOTE)\b", l, re.I):
            add(i, "warning", "🧩", "Pendência anotada no código")

        if len(linha) > 100:
            add(i, "warning", "📏", "Linha excede 100 caracteres")

        if l.startswith("#") and len(linha) > 80:
            add(i, "warning", "💬", "Comentário excessivamente longo")

        if "print(" in l and not l.startswith("#"):
            add(i, "warning", "🐞", "Uso de print como debug")

        if "eval(" in l or "exec(" in l:
            add(i, "error", "☠️", "Uso de eval/exec (risco de segurança)")

        if l.startswith("global "):
            add(i, "warning", "🌍", "Uso de variável global")

        if l == "pass":
            add(i, "warning", "🕳️", "Bloco vazio (pass)")

        if l.startswith("except:") or ("except Exception" in l and "as" not in l):
            add(i, "error", "🚫", "Except genérico oculta erros reais")

    # --------------------------------------------------------
    # 2. ANÁLISE AST
    # --------------------------------------------------------
    if tree:
        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add(
                    node.lineno - 1,
                    "warning" if ast.get_docstring(node) is None else "info",
                    "⚙️",
                    f"Função '{node.name}' sem docstring"
                    if ast.get_docstring(node) is None
                    else f"Função '{node.name}'"
                )

            elif isinstance(node, ast.ClassDef):
                add(
                    node.lineno - 1,
                    "warning" if ast.get_docstring(node) is None else "info",
                    "🏷️",
                    f"Classe '{node.name}' sem docstring"
                    if ast.get_docstring(node) is None
                    else f"Classe '{node.name}'"
                )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    add(node.lineno - 1, "info", "📦", f"Import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                add(node.lineno - 1, "info", "📥", f"Import from {node.module}")

    else:
        try:
            ast.parse(codigo)
        except SyntaxError as e:
            add(
                (e.lineno or 1) - 1,
                "error",
                "💥",
                f"Erro de sintaxe: {e.msg}"
            )

    return annotations


# ============================================================
# MARKERS (VISUAL LIMPO, SEM POLUIÇÃO)
# ============================================================
def Marcadores_Editor(codigo: str) -> List[Dict[str, Any]]:
    markers: List[Dict[str, Any]] = []
    linhas = codigo.split("\n")
    tree = _parse_ast(codigo)

    for i, linha in enumerate(linhas):

        if len(linha) > 100:
            markers.append({
                "startRow": i,
                "startCol": 100,
                "endRow": i,
                "endCol": len(linha),
                "className": "marker-longline",
                "type": "range"
            })

        if linha.strip() == "pass":
            markers.append({
                "startRow": i,
                "startCol": 0,
                "endRow": i,
                "endCol": len(linha),
                "className": "marker-pass",
                "type": "fullLine"
            })

    if tree:
        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                markers.append({
                    "startRow": node.lineno - 1,
                    "startCol": 0,
                    "endRow": (node.end_lineno or node.lineno) - 1,
                    "endCol": 0,
                    "className": "marker-function-scope",
                    "type": "fullBlock"
                })

            elif isinstance(node, ast.ClassDef):
                markers.append({
                    "startRow": node.lineno - 1,
                    "startCol": 0,
                    "endRow": (node.end_lineno or node.lineno) - 1,
                    "endCol": 0,
                    "className": "marker-class-scope",
                    "type": "fullBlock"
                })

    return markers

# ============================================================
# MÉTRICA DE QUALIDADE (DASHBOARD)
# ============================================================
def calcular_qualidade(codigo: str) -> Dict[str, Any]:
    """Score profissional para dashboard da IDE."""
    ann = Anotations_Editor(codigo)

    erros = sum(1 for a in ann if a["type"] == "error")
    warnings = sum(1 for a in ann if a["type"] == "warning")
    info = sum(1 for a in ann if a["type"] == "info")
    success = sum(1 for a in ann if a["type"] == "success")

    score = max(0, 100 - (erros * 25 + warnings * 8))

    return {
        "score": round(score, 1),
        "erros": erros,
        "warnings": warnings,
        "info": info,
        "success": success,
        "total": len(ann),
        "status": "⭐ Excelente" if score > 90 else "⚡ Boa" if score > 70 else "🚨 Crítica"
    }



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

}

    _, ext = os.path.splitext(arquivo)
    return EXT_MAP.get(ext.lower(), "Desconhecido")


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

def Sinbolos(arquivo):
    arquivo = Path(arquivo)

    ICONES_EXT = {
        ".py": "🐍",  # Python - PERFEITO
        ".txt": "📄",  # TXT - PERFEITO
        ".js": "⚡",  # JavaScript - ⚡ Elétrico/Moderno
        ".html": "🌐",  # HTML - PERFEITO
        ".css": "🎨",  # CSS - PERFEITO
        ".json": "📋",    # JSON - Lista/configuração perfeita!
        ".md": "📝",  # Markdown - PERFEITO
        ".cpp": "🔧",  # C++ - 🔧 Ferramenta (compilado)
        ".java": "☕",  # Java - PERFEITO
        ".php": "🐘",  # PHP - PERFEITO
        ".rb": "💎",  # Ruby - PERFEITO
        ".cfg": "⚙️",  # Config
        ".pth": "🧠",  # PTH - PyTorch/Pesos de modelo 🧠
        ".db": "🗄️",  # PTH - PyTorch/Pesos de modelo 🧠

    }

    return ICONES_EXT.get(arquivo.suffix.lower(), "📦")


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
            use_container_width=True,
            type="primary"
        )
    else:
        st.button(
            nome_fechado,
            key=widget_key,
            on_click=toggle,
            use_container_width=True,
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




def escreve(texto):
    import  streamlit as st
    return st.write(texto)
