import os
import time

import streamlit
from code_editor import code_editor

import ast
import re
from typing import List, Dict, Any, Optional
import ast
import re
import importlib.util
from typing import List, Dict, Any, Optional

# ============================================================
# HELPER: VERIFICA SE MÓDULO ESTÁ INSTALADO (SEM IMPORTAR)
# ============================================================
def _modulo_instalado(nome_modulo: str) -> bool:
    if not nome_modulo or nome_modulo.startswith(('.', '_')):
        return True  # Ignora relativos, built-ins internos, etc.
    try:
        # Pega só o módulo top-level (ex: "flask" de "flask.Blueprint")
        top_level = nome_modulo.split('.')[0]
        return importlib.util.find_spec(top_level) is not None
    except (ImportError, AttributeError, Exception):
        return False

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
            "type": level,              # "error", "warning", "info" → cor no gutter
            "text": f"{emoji} {msg}"    # Hover rico
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
    # 2. ANÁLISE AST (inclui checagem de módulos faltando!)
    # --------------------------------------------------------
    if tree:
        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                add(
                    node.lineno - 1,
                    "warning" if doc is None else "info",
                    "⚙️",
                    f"Função '{node.name}' sem docstring" if doc is None else f"Função '{node.name}'"
                )

            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                add(
                    node.lineno - 1,
                    "warning" if doc is None else "info",
                    "🏷️",
                    f"Classe '{node.name}' sem docstring" if doc is None else f"Classe '{node.name}'"
                )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    mod_name = alias.name.split('.')[0]
                    if not _modulo_instalado(mod_name):
                        add(node.lineno - 1, "error", "❌", f"{mod_name} NÃO ESTÁ INSTALADO (pip install {mod_name})")
                    else:
                        add(node.lineno - 1, "info", "📦", f"Import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod_name = node.module.split('.')[0]
                    if not _modulo_instalado(mod_name):
                        add(node.lineno - 1, "error", "❌", f"{mod_name} NÃO ESTÁ INSTALADO (pip install {mod_name})")
                    else:
                        add(node.lineno - 1, "info", "📥", f"Import from {node.module}")

    else:
        # Erro de sintaxe
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
# + MARCADORES PARA IMPORTS FALTANDO
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

            # NOVO: Marcador visual para imports faltando
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    names = [alias.name.split('.')[0] for alias in node.names]
                else:
                    names = [node.module.split('.')[0]] if node.module else []
                for mod_name in names:
                    if not _modulo_instalado(mod_name):
                        markers.append({
                            "startRow": node.lineno - 1,
                            "startCol": 0,
                            "endRow": node.lineno - 1,
                            "endCol": len(linhas[node.lineno - 1]),
                            "className": "marker-missing-import",
                            "type": "fullLine"
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

# *** st_ace RETORNA o código ATUALIZADO da aba ***

def Botoes():
    return [{
        "name": "copy",
        "feather": "Copy",
        "hasText": True,
        "alwaysOn": True,
        "commands": ["copyAll"],
        "style": {"top": "0rem", "right": "0.4rem"}
        }, {
        "name": "update",
        "feather": "RefreshCw",
        "primary": True,
        "hasText": True,
        "showWithIcon": True,
        "commands": ["submit"],
        "style": {"bottom": "0rem", "right": "0.4rem"}
    }]


def Atalhos():
    return {
        # Salvar/Executar
        "Ctrl-S": "save", # Salva arquivo
        "F5": "execute", # Executa código
        "Ctrl-F5": "run-selection", # Roda só seleção
        # Edição rápida
        "Ctrl-/": "togglecomment", # Comentar linha
        "Ctrl-D": "selectnext", # Próxima mesma palavra
        "Alt-Up": "moveup", # Move linha pra cima
        "Alt-Down": "movedown", # Move linha pra baixo
        # Navegação
        "Ctrl-P": "gotolinestart", # Início da linha
        "Ctrl-L": "jumptoline", # Vai pra linha (dialog)
        # Streamlit específico
        "Ctrl-Shift-R": "rerun", # Streamlit rerun
    }

def Info_ide():
    return {
        "position": "right",
        "stats": True,
        "errors": True,
        "warnings": True,
        "mode": True,
        "filename": "main.py",
        "linenr": True, # Número da linha atual
        "encoding": "UTF-8",
        "modified": True # * se modificado
    }


def Component_props():
    return  {
        # Configurações internas do React component
        "enableLiveAutocompletion": True, # Autocomplete em tempo real
        "liveAutocompletionDelay": 200, # Delay em ms
        "enableSnippets": True, # Habilita snippets
        "showGutter": True, # Mostrar gutter (margem esquerda)


        # Comportamento do componente
        "autoFocus": True, # Foco automático
        "readOnly": False, # Apenas leitura
        "highlightActiveLine": True, # Destaca linha atual

        # Performance
        "maxLines": 1000, # Máx linhas carregadas
        "minLines": 10, # Mín linhas visíveis

        # Debug/Dev
        "showInvisibles": True, # Mostra espaços/tabs
        "displayIndentGuides": True # Guias de indentação
    }

def Completar():
    return [# Palavras/chaves que aparecem no autocomplete (além das do idioma):
        {"caption": "st_page", "value": "st_page", "meta": "Streamlit", "score": 1000},
        {"caption": "minha_df", "value": "minha_df.head()", "meta": "DataFrame"},
        {"caption": "api_key", "value": "os.getenv('API_KEY')", "meta": "env"},
        {"caption": "debug", "value": "print(f'DEBUG: {var}')", "meta": "debug"}
        ]

def Menus():
    return {
        "file": [
        {"label": "💾 Save", "command": "save"},
        {"label": "🗑️ Delete", "command": "delete"},
        {"label": "📥 Reload", "command": "reload"}
        ],
        "edit": [
        {"label": "✂️ Cut", "command": "cut"},
        {"label": "📋 Copy", "command": "copyAll"},
        {"label": "🔗 Format", "command": "format"}
        ],
        "run": [
        {"label": "▶️ Run", "command": "submit"},
        {"label": "🔍 Debug", "command": "debug"}]}

def Opcoes_editor(font_size,thema,fonte):
    return {
        # VISUAL
        "wrap": True,
        "fontSize": font_size, # Tamanho da fonte
        "fontFamily": f'{fonte}, "Courier New", monospace',  # ← ISSO RESOLVE  # Fonte (use 'Fira Code', 'JetBrains Mono', etc.)
        "showLineNumbers": True, # Mostrar números de linha
        "showPrintMargin": True, # Mostrar margem de impressão
        "printMarginColumn": 100, # Coluna da margem de impressão
        "theme": f"ace/theme/{thema}",

        # CURSOR E SELEÇÃO
        "highlightSelectedWord": True, # Destacar todas ocorrências da palavra selecionada
        "fadeFoldWidgets": True, # Fade nos widgets de fold

        # COMPORTAMENTO
        "tabSize": 4, # Tamanho da tabulação
        "useSoftTabs": True, # Usar spaces em vez de tabs
        "enableBasicAutocompletion": True, # Autocompletar básico
    }

def Estilo(cor):
    return {
    "style": {
        "background": cor,

    }}
def editor_codigo_autosave(st, aba_id, caminho_arquivo, conteudo_inicial, linguagem, thema_editor, font_size,fonte,altura,backgroud=None):

    cod = code_editor(conteudo_inicial,
        lang=linguagem.lower(), # garante minúsculo

        height=f'{altura}px', # Altura dinâmica (min, max linhas) ou fixa "850px"
        shortcuts='vscode', # ["emacs", "vim", "vscode", "sublime"]
        response_mode=["blur"],  # ← ADICIONE AQUI (linha 142, junto com lang=, theme=, etc)

        options = Opcoes_editor(font_size,thema_editor.lower(),fonte),
        keybindings = Atalhos(),
        info = Info_ide(), # NAO ACONTECEU NADA
        props = Estilo(backgroud), # CSS
        component_props = Component_props(), # NAO ACONTECEU NADA
        completions = Completar(), # NAO ACONTECEU NADA
        menu = Menus(), # NAO ACONTECEU NADA
        editor_props={
          "annotations": Anotations_Editor(conteudo_inicial),
          "markers": Marcadores_Editor(conteudo_inicial),
          "debounceChangePeriod": 5000},  # ← 1 SEGUNDO de pausa

        buttons = Botoes(),
        ghost_text="Digita ai bora",
        key=caminho_arquivo
        )

    # Extrai código editado
    novo_codigo = cod.get('text', '') if isinstance(cod, dict) else str(cod) if cod else conteudo_inicial

    return novo_codigo # ← SEMPRE STRING
