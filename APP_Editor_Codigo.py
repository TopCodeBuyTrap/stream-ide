import os
import time

import streamlit
from code_editor import code_editor

from APP_SUB_Funcitons import Anotations_Editor, Marcadores_Editor


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

        # Estados avançados
        "showPrintMargin": True, # Margem de impressão
        "printMarginColumn": 80, # Coluna da margem

        # Performance
        "maxLines": 1000, # Máx linhas carregadas
        "minLines": 10, # Mín linhas visíveis

        # Debug/Dev
        "showInvisibles": False, # Mostra espaços/tabs
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
        "printMarginColumn": -.1, # Coluna da margem de impressão
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
def editor_codigo_autosave(st, aba_id, caminho_arquivo, conteudo_inicial, linguagem, thema_editor, font_size,fonte):
    _ = st.session_state

    # Estado local da aba
    content_key = f"editor_content_{aba_id}"
    _.setdefault(content_key, conteudo_inicial or "")

    # Conteúdo atualizado do session_state
    conteudo_atual = _[content_key]
    if not isinstance(conteudo_atual, str):
        conteudo_atual = str(conteudo_atual)

    # Opções personalizadas para parecer profissional



    cod = code_editor(conteudo_inicial,
        lang=linguagem.lower(), # garante minúsculo

        height=f'770px', # Altura dinâmica (min, max linhas) ou fixa "850px"
        shortcuts='vscode', # ["emacs", "vim", "vscode", "sublime"]
        response_mode=["blur"],  # ← ADICIONE AQUI (linha 142, junto com lang=, theme=, etc)

        options = Opcoes_editor(font_size,thema_editor.lower(),fonte),
        keybindings = Atalhos(),
        info = Info_ide(), # NAO ACONTECEU NADA
        props = Estilo('black'), # CSS
        component_props = Component_props(), # NAO ACONTECEU NADA
        completions = Completar(), # NAO ACONTECEU NADA
        menu = Menus(), # NAO ACONTECEU NADA
        editor_props={
          "annotations": Anotations_Editor(conteudo_inicial),
          "markers": Marcadores_Editor(conteudo_inicial),
          "debounceChangePeriod": 5000},  # ← 1 SEGUNDO de pausa

        buttons = Botoes(),
        ghost_text="Digita ai bora",
        key=content_key
        )

    # Extrai código editado
    novo_codigo = cod.get('text', '') if isinstance(cod, dict) else str(cod) if cod else conteudo_atual

    save_key = f"last_saved_{aba_id}"
    if novo_codigo.strip() and novo_codigo != _.get(save_key, "") and caminho_arquivo:
        _[save_key] = novo_codigo
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(novo_codigo)

    return novo_codigo # ← SEMPRE STRING
