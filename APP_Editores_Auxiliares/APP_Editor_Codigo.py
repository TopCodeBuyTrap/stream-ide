import streamlit
from code_editor import code_editor
import os, time, ast
from pathlib import Path
from typing import List, Dict, Any, Optional

from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida
from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_, VENVE_DO_PROJETO

from Banco_dados import gerar_predefinidos_com_links


# ===== Exemplo de uso no editor =====
def_from, def_predefinidos, from_predefinidos = gerar_predefinidos_com_links()
streamlit.write(def_from)

def carregar_modulos_venv():
    import sys
    import pkgutil
    from pathlib import Path
    streamlit.write(from_predefinidos)
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



def checar_erros(codigo):
    from pyflakes.api import check
    from pyflakes.reporter import Reporter
    import io
    erros_io = io.StringIO()
    reporter = Reporter(erros_io, erros_io)
    check(codigo, filename="<string>", reporter=reporter)
    erros_texto = erros_io.getvalue().strip()
    erros = []
    if erros_texto:
        for linha in erros_texto.splitlines():
            try:
                # Separar linha e mensagem, ignorando coluna
                partes = linha.split(":", 2)
                linha_num = int(partes[1])
                mensagem = partes[2].strip()
                erros.append({"line": f'{linha_num}>', "message": f'{mensagem}'})
            except:
                continue
    return erros


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
        "Ctrl-X": "cut",  # ← RECORTA LINHA INTEIRA (VSCode padrão)

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
            "borderRadius": "0 0 8px 8px",
            "padding": "4px"
        }
    }

def editor_props():
    """EDITOR_PROPS = CSS INTERNO DO EDITOR (funciona no editor_props=)"""
    return {
            "debounceChangePeriod": 500,  # aguarda 0,5s após digitar para atualizar o retorno
            "readOnly": False,  # deixa o editor editável
            "highlightActiveLine": True,  # destaca linha atual
            "highlightGutterLine": True,  # destaca o número da linha atual
        },

def editor_codigo_autosave(st, aba_id, caminho_arquivo, conteudo_inicial, linguagem, thema_editor, font_size, fonte, altura,lateral, backgroud=None):
    _ = st.session_state

    # 🔐 CHAVES ÚNICAS MILITARES (IMPROVÁVEL COLIDIR)
    nome_arq = os.path.basename(caminho_arquivo) if caminho_arquivo else f"aba_{aba_id}"
    cache_key = f"autosave_cache_{aba_id}_{nome_arq}_{hash(caminho_arquivo or '')}"
    save_key = f"autosave_saved_{aba_id}_{nome_arq}_{hash(caminho_arquivo or '')}"

    # 🛡️ CARREGA ESTADO ANTERIOR (persiste reloads)
    codigo_anterior = _.get(cache_key, conteudo_inicial or "")

    # 📝 EDITOR COM KEY ÚNICA
    cod = code_editor(
        codigo_anterior,  # ← CARREGA DO CACHE!
        lang=linguagem.lower(),
        height=f'{altura}px',
        shortcuts='vscode',
        response_mode=["blur"],
        options=Opcoes_editor(font_size, thema_editor.lower(), fonte),
        keybindings=Atalhos(),
        props={"markers": Marcadores_Editor(codigo_anterior), "annotations": Anotations_Editor(codigo_anterior)},
        component_props=Component_props(),
        completions=Completar(st),
        editor_props=editor_props(),
        buttons=Botoes(),
        key=f"editor_militar_{aba_id}_{nome_arq}"  # 🔐 ÚNICA!
    )

    # 📥 EXTRAI CÓDIGO ATUAL
    novo_codigo = cod.get('text', '') if isinstance(cod, dict) else str(cod) if cod else ""
    # ===== Exibe os links abaixo do editor =====
    with lateral:
        erros = checar_erros(novo_codigo)
        if erros:
            avizo = "\n\n".join([f"Linha {e['line']}: {traduzir_saida(e['message'])}" for e in erros]).replace(">:",'\n')
            st.warning(avizo)

    # 🔥 AUTOSAVE MILITAR (3 camadas)
    if novo_codigo.strip() and novo_codigo != codigo_anterior and caminho_arquivo:

        # CAMADA 1: CACHE IMEDIATO (0.001s)
        _[cache_key] = novo_codigo

        # CAMADA 2: DISCO COM BACKUP (0.1s)
        try:
            Path(caminho_arquivo).parent.mkdir(parents=True, exist_ok=True)

            # Backup temporal
            backup_path = Path(caminho_arquivo).with_suffix('.py.bak')
            Path(caminho_arquivo).write_text(novo_codigo, encoding='utf-8')

            # Remove backup antigo se salvo com sucesso
            if backup_path.exists():
                backup_path.unlink()

            _[save_key] = novo_codigo
            _['autosave_status'] = f"💾 {nome_arq}"

        except Exception as e:
            # CAMADA 3: EMERGÊNCIA (JSON no projeto)
            emergencia_path = Path(_DIRETORIO_PROJETO_ATUAL_()) / f"EMERGENCIA_{nome_arq}.json"
            emergencia_path.write_text({
                "timestamp": time.time(),
                "codigo": novo_codigo,
                "erro": str(e)
            }, encoding='utf-8')
            _['autosave_status'] = f"⚠️ Emergência {nome_arq}"




        return novo_codigo  # ← SEMPRE RETORNA ATUALIZADO



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
    import ast
    import re
    from typing import List, Dict, Any, Optional
    from pyflakes.api import check
    from pyflakes.reporter import Reporter
    import io

    def _parse_ast(codigo: str) -> Optional[ast.AST]:
        try:
            return ast.parse(codigo)
        except SyntaxError:
            return None

    def checar_erros(codigo: str) -> List[Dict[str, Any]]:
        erros_io = io.StringIO()
        reporter = Reporter(erros_io, erros_io)
        check(codigo, filename="<string>", reporter=reporter)
        erros_texto = erros_io.getvalue().strip()
        erros = []
        if erros_texto:
            for linha in erros_texto.splitlines():
                try:
                    partes = linha.split(":", 2)
                    linha_num = int(partes[1])
                    mensagem = partes[2].strip()
                    erros.append({"line": linha_num, "message": mensagem})
                except:
                    continue
        return erros

    annotations: List[Dict[str, Any]] = []
    linhas = codigo.split("\n")
    tree = _parse_ast(codigo)

    def add(row: int, level: str, emoji: str, msg: str):
        annotations.append({
            "row": row,
            "type": level,
            "text": f"{emoji} {msg}"
        })

    # =========================================================
    # 1. ANÁLISE DE ERROS PYFLAKES
    # =========================================================
    erros = checar_erros(codigo)
    for e in erros:
        add(e["line"] - 1, "error", "❌", traduzir_saida(e["message"]))

    # =========================================================
    # 2. ANÁLISE TEXTUAL
    # =========================================================
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

    # =========================================================
    # 3. ANÁLISE AST
    # =========================================================
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add(node.lineno - 1,
                    "warning" if ast.get_docstring(node) is None else "info",
                    "⚙️",
                    f"Função '{node.name}' sem docstring"
                    if ast.get_docstring(node) is None
                    else f"Função '{node.name}'")
            elif isinstance(node, ast.ClassDef):
                add(node.lineno - 1,
                    "warning" if ast.get_docstring(node) is None else "info",
                    "🏷️",
                    f"Classe '{node.name}' sem docstring"
                    if ast.get_docstring(node) is None
                    else f"Classe '{node.name}'")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    add(node.lineno - 1, "info", "📦", f"Import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                add(node.lineno - 1, "info", "📥", f"Import from {node.module}")
    else:
        try:
            ast.parse(codigo)
        except SyntaxError as e:
            add((e.lineno or 1) - 1, "error", "💥", f"Erro de sintaxe: {e.msg}")

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
