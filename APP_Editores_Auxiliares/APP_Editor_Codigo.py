from code_editor import code_editor
import os, time, ast, re
from pathlib import Path
import importlib.util
from typing import List, Dict, Any, Optional

from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_


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

# AUTO-COMPLETE INTELIGENTE (igual VS Code/PyCharm)
# 1. INDEXAR: scripts.py → funções/classes/variáveis
# 2. COMPLETER: Ace custom (from Strean → conta)
# 3. LIVETIME: atualiza quando salva arquivo

def editor_codigo_autosave(st, aba_id, caminho_arquivo, conteudo_inicial, linguagem, thema_editor, font_size, fonte,
                           altura, backgroud=None):
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
        info=Info_ide(),
        props=Estilo(backgroud),
        component_props=Component_props(),
        completions=Completar(),
        menu=Menus(),
        editor_props={
            "annotations": Anotations_Editor(codigo_anterior),
            "markers": Marcadores_Editor(codigo_anterior),
            "debounceChangePeriod": 1500  # 1.5s - PERFEITO
        },
        buttons=Botoes(),
        key=f"editor_militar_{aba_id}_{nome_arq}"  # 🔐 ÚNICA!
    )

    # 📥 EXTRAI CÓDIGO ATUAL
    novo_codigo = cod.get('text', '') if isinstance(cod, dict) else str(cod) if cod else ""

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




def editor_codigo_autosave_(st, aba_id, caminho_arquivo, conteudo_inicial, linguagem, thema_editor, font_size, fonte,
                           altura, backgroud=None):
    _ = st.session_state  # Cache rápido

    # Key ÚNICA por aba+arquivo (evita overwrite entre abas)
    cache_key = f"cache_{aba_id}_{os.path.basename(caminho_arquivo)}"
    save_key = f"saved_{aba_id}_{os.path.basename(caminho_arquivo)}"

    # Pega código anterior do cache (persistente)
    codigo_anterior = _[cache_key] if cache_key in _ else conteudo_inicial

    cod = code_editor(codigo_anterior,  # ← USA CACHE, NÃO conteudo_inicial sempre!
                      lang=linguagem.lower(),
                      height=f'{altura}px',
                      shortcuts='vscode',
                      response_mode=["blur"],
                      options=Opcoes_editor(font_size, thema_editor.lower(), fonte),
                      keybindings=Atalhos(),
                      info=Info_ide(),
                      props=Estilo(backgroud),
                      component_props=Component_props(),
                      completions=Completar(),
                      menu=Menus(),
                      editor_props={
                          "annotations": Anotations_Editor(codigo_anterior),
                          "markers": Marcadores_Editor(codigo_anterior),
                          "debounceChangePeriod": 2000  # ← 2 SEGUNDOS (melhor UX)
                      },
                      buttons=Botoes(),
                      ghost_text="Digita ai bora",
                      key=f"editor_{aba_id}_{caminho_arquivo}"  # ← Key ÚNICA!
                      )

    # Extrai código editado
    novo_codigo = cod.get('text', '') if isinstance(cod, dict) else str(cod) if cod else conteudo_inicial

    # 🔥 AUTOSAVE INVISÍVEL (roda sempre, mas só salva se mudou)
    if novo_codigo.strip() and novo_codigo != codigo_anterior and caminho_arquivo:
        try:
            # 1. Cache imediato (rápido)
            _[cache_key] = novo_codigo

            # 2. Salva no DISCO após debounce (seguro)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(novo_codigo)

            _[save_key] = novo_codigo  # Marca como "salvo"

            # Feedback sutil (opcional)
            st.session_state.autosave_status = f"💾 {os.path.basename(caminho_arquivo)}"

        except Exception as e:
            st.session_state.autosave_status = f"❌ {str(e)[:30]}..."

    return novo_codigo  # ← SEMPRE ATUAL
