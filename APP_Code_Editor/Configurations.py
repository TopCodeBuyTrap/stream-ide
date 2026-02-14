"""
Configuration.py - Configurações avançadas para o Streamlit Code Editor.

Este arquivo contém funções para configurar atalhos, propriedades do componente,
opções do editor, estilos e outras configurações baseadas na documentação
do streamlit-code-editor (https://github.com/bouzidanas/streamlit-code-editor).

Melhorias implementadas:
- Atalhos expandidos com base no Ace Editor.
- Suporte a snippets, temas dinâmicos, menu/info bars, ghost text.
- Validações e fallbacks para robustez.
- Organização por categoria com comentários detalhados.
- Integração com features avançadas como response_mode múltiplo.
"""

def Atalhos():
    return {
        # === SALVAR E EXECUTAR ===
        "Ctrl-S": "save",  # Salva o arquivo atual
        "F5": "execute",  # Executa o código completo
        "Ctrl-F5": "run-selection",  # Executa apenas a seleção atual
        "Ctrl-Shift-F5": "debug",  # Inicia depuração (se suportado)
        "F9": "toggle-breakpoint",  # Adiciona/remover breakpoint

        # === EDIÇÃO BÁSICA ===
        "Ctrl-Z": "undo",  # Desfaz a última ação
        "Ctrl-Y": "redo",  # Refaz a última ação desfeita
        "Ctrl-A": "selectall",  # Seleciona todo o texto
        "Ctrl-X": "cut",  # Corta a seleção ou linha inteira
        "Ctrl-C": "copy",  # Copia a seleção
        "Ctrl-V": "paste",  # Cola o conteúdo da área de transferência
        "Delete": "delete",  # Deleta o caractere à direita
        "Backspace": "backspace",  # Deleta o caractere à esquerda

        # === NAVEGAÇÃO E SELEÇÃO ===
        "Ctrl-Home": "gotostart",  # Vai para o início do arquivo
        "Ctrl-End": "gotoend",  # Vai para o fim do arquivo
        "Ctrl-Left": "gotowordleft",  # Vai para a palavra anterior
        "Ctrl-Right": "gotowordright",  # Vai para a próxima palavra
        "Home": "gotolinestart",  # Vai para o início da linha
        "End": "gotolineend",  # Vai para o fim da linha
        "PageUp": "pageup",  # Rola uma página para cima
        "PageDown": "pagedown",  # Rola uma página para baixo
        "Ctrl-L": "jumptoline",  # Abre diálogo para ir a uma linha específica
        "Ctrl-P": "gotofile",  # Abre diálogo para ir a um arquivo (se suportado)

        # === EDIÇÃO AVANÇADA ===
        "Ctrl-/": "togglecomment",  # Comenta/descomenta a linha ou seleção
        "Ctrl-Shift-/": "toggleblockcomment",  # Comenta bloco (se suportado)
        "Tab": "indent",  # Indenta a linha ou seleção
        "Shift-Tab": "outdent",  # Remove indentação
        "Ctrl-D": "selectnext",  # Seleciona a próxima ocorrência da palavra
        "Ctrl-Shift-D": "selectprevious",  # Seleciona a ocorrência anterior
        "Alt-Up": "moveup",  # Move a linha ou seleção para cima
        "Alt-Down": "movedown",  # Move a linha ou seleção para baixo
        "Ctrl-Shift-Up": "copylinesup",  # Copia a linha para cima
        "Ctrl-Shift-Down": "copylinesdown",  # Copia a linha para baixo
        "Ctrl-Shift-K": "deleteline",  # Deleta a linha inteira
        "Ctrl-Enter": "insertlineafter",  # Insere linha após
        "Ctrl-Shift-Enter": "insertlinebefore",  # Insere linha antes

        # === PESQUISA E SUBSTITUIÇÃO ===
        "Ctrl-F": "find",  # Abre busca
        "Ctrl-H": "replace",  # Abre substituição
        "F3": "findnext",  # Próxima ocorrência
        "Shift-F3": "findprevious",  # Ocorrência anterior
        "Ctrl-Shift-F": "findinfiles",  # Busca em arquivos (se suportado)

        # === FOLDING (DOBRAR CÓDIGO) ===
        "Ctrl-Alt-[": "fold",  # Dobra o bloco atual
        "Ctrl-Alt-]": "unfold",  # Desdobra o bloco atual
        "Ctrl-Alt-0": "foldall",  # Dobra todos os blocos
        "Ctrl-Alt-Shift-0": "unfoldall",  # Desdobra todos os blocos

        # === STREAMLIT ESPECÍFICO ===
        "Ctrl-Shift-R": "rerun",  # Força rerun no Streamlit
        "Ctrl-Shift-S": "stop",  # Para execução (se suportado)

        # === OUTROS ===
        "F1": "help",  # Abre ajuda ou documentação
        "Ctrl-Shift-P": "commandpalette",  # Abre paleta de comandos (se suportado)
        "Ctrl-Shift-L": "selectalloccurrences",  # Seleciona todas as ocorrências

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


# === NOVAS FUNÇÕES PARA FEATURES AVANÇADAS ===
def Snippets():
    """
    Retorna lista de snippets para o code_editor (usado em snippets=).

    Ajustado para lista simples de strings (como esperado pelo componente),
    baseado na documentação. Evita erro "Cannot read properties of undefined (reading 'split')"
    que ocorria com dicts complexos. Placeholders ${1} podem não funcionar em todas as versões.

    Retorna:
        List[str]: Lista de snippets simples.
    """
    return [
        "def function_name(args):\n\t\"\"\"docstring\"\"\"\n\tpass",  # def function
        "if condition:\n\tpass",  # if statement
        "class ClassName:\n\t\"\"\"docstring\"\"\"\n\tdef __init__(self, args):\n\t\tpass",  # class definition
        "try:\n\tcode\nexcept Exception as e:\n\tpass",  # try except
        "for item in iterable:\n\tpass",  # for loop
    ]


def Menu():
    """
    Retorna configuração de menu para o code_editor (usado em menu=).

    Baseado na documentação para barras de menu customizadas.
    Exemplo simples; personalize com submenus e comandos.

    Retorna:
        Dict[str, Any]: Configuração do menu.
    """
    return {
        "items": [
            {
                "label": "Arquivo",
                "submenu": [
                    {"label": "Salvar", "command": "save"},
                    {"label": "Executar", "command": "execute"},
                    {"label": "Executar Seleção", "command": "run-selection"}
                ]
            },
            {
                "label": "Editar",
                "submenu": [
                    {"label": "Desfazer", "command": "undo"},
                    {"label": "Refazer", "command": "redo"},
                    {"label": "Comentar", "command": "togglecomment"}
                ]
            },
            {
                "label": "Ajuda",
                "submenu": [
                    {"label": "Documentação", "command": "help"}
                ]
            }
        ]
    }

