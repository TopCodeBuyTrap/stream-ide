import os
import subprocess
import sys
from pathlib import Path
from time import sleep

import streamlit
from code_editor import code_editor

from APP_SUB_Funcitons import Criar_Arquivo_TEXTO, data_sistema, resumo_pasta, Button_Nao_Fecha, Alerta, \
    Sinbolos
from APP_SUB_Janela_Explorer import listar_pythons_windows, Apagar_Arquivos, Janela_PESQUIZA
from Banco_dados import salvar_modulo, listar_modulos, carregar_comando_modulo, ler_CUSTOMIZATION, ler_cut, ATUAL_CUSTOMIZATION_nome, \
    esc_CONTROLE_ARQUIVOS, esc_A_CONTROLE_PROJETOS, ler_A_CONT_ABS_unico
from APP_SUB_Controle_Driretorios import _DIRETORIO_EXECUTAVEL_, _DIRETORIO_PROJETO_ATUAL_, _DIRETORIO_PROJETOS_

# Pega a pasta Downloads do usuário
default_download = os.path.join(os.path.expanduser("~"), "Downloads")



# ===== FIX WINDOWS: NÃO ABRIR JANELA DE CONSOLE =====
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW



# Lista de fontes para campos (inputs, selects, botões) - fontes de programação
FONTES_TEXTO = ["Helvetica", "Arial", "Verdana", "Tahoma", "Times New Roman", "Georgia", "Comic Sans MS",
                "Fira Code", "JetBrains Mono", "Source Code Pro", "Source Sans Pro","Press Start 2P", "Pixelify Sans", "Silkscreen",
                "Share Tech Mono", "Inconsolata", "Consolas", "Courier New", "Monospace"]
# Temas Ace Editor - SEPARADOS CORRETAMENTE por claro e escuro
TEMAS_CLAROS = [
    "chrome",  # Claro padrão/neutro
    "crimson_editor",  # Claro (você confirmou)
    #"dawn",             # Claro suave/bege
    "dreamweaver",  # Claro (você confirmou)
    "eclipse",  # Claro clássico
    "github",  # Claro GitHub
    "iplastic",  # Claro (você confirmou)
    #"katzenmilch",      # Claro creme (você confirmou)
    #"kuroir",           # Claro (você confirmou)
    "solarized_light",  # Solarized claro oficial
    "sqlserver",  # Claro SQL Server (você confirmou)
    #"textmate",         # Claro TextMate

    "xcode"  # Claro Xcode
]

LANGUAGES = [
    "powershell", "abap", "apex", "css", "kotlin", "less", "markdown", "python"]

TEMAS_ESCUROS = [
    "ambiance",  # Escuro clássico
    "chaos",  # Escuro vibrante
    #"clouds_midnight",      # Escuro (você confirmou)
    "cobalt",  # Escuro azul
    "dracula",  # Escuro roxo popular
    "gob",  # Escuro gob
    "idle_fingers",  # Escuro Idle Fingers
    #"kr_theme",             # Escuro KR
    "merbivore",  # Escuro Merbivore
    "merbivore_soft",  # Escuro suave
    "mono_industrial",  # Escuro industrial
    "monokai",  # Escuro Monokai clássico
    #"nord_dark",            # Escuro Nord
    "pastel_on_dark",  # Escuro (você confirmou)
    "solarized_dark",  # Solarized escuro oficial
    "terminal",  # Escuro terminal
    "tomorrow_night",  # Tomorrow Night escuro
    #"tomorrow_night_blue",  # Tomorrow azul escuro
    "tomorrow_night_bright",  # Tomorrow bright escuro
    #"tomorrow_night_eighties", # Tomorrow 80s escuro
    "twilight",  # Escuro Twilight
    "vibrant_ink",  # Claro vibrante (você confirmou)
]

TEMAS_MONACO = ["vs-dark", "vs-light", "hc-black", "hc-light", "Sistema"]


def Custom(st):
    @st.dialog("Customização: ",dismissible=False)
    def menu_principal():
        st1,st2 = st.columns([8,1])
        if st2.button("X", key="Customizar"):
            st.session_state["Customizar_state"] = False
            st.rerun()
        # Lista de customizações existentes
        customs = ler_CUSTOMIZATION()
        lista_customs = [c[0] for c in customs]

        selected_custom = st.selectbox("Selecionar Customização Existente", ["Nova Customização"] + lista_customs,label_visibility='collapsed')

        # Inicializa session_state apenas se a customização selecionada mudou
        if selected_custom != "Nova Customização" and st.session_state['custom_loaded'] != selected_custom:
            dados = ler_cut(selected_custom)
            if dados:
                # Desempacotamento seguro: pega as 18 primeiras variáveis, ignora o resto até OBS
                (NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD, IMAGEM_LOGO,
                 THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_TERMINAL, LINGUA_TERMINAL,
                 THEMA_APP1, THEMA_APP2, THEMA_RUN,
                 FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
                 FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
                 FONTE_TAM_RUN, *resto, OBS) = dados

                st.session_state.update({
                    'NOME_CUSTOM': NOME_CUSTOM,
                    'NOME_USUARIO': NOME_USUARIO,
                    'CAMINHO_DOWNLOAD': CAMINHO_DOWNLOAD,
                    'IMAGEM_LOGO': IMAGEM_LOGO,
                    'THEMA_EDITOR': THEMA_EDITOR.strip(),
                    'EDITOR_TAM_MENU': EDITOR_TAM_MENU,
                    'THEMA_TERMINAL': THEMA_TERMINAL.strip(),
                    'LINGUA_TERMINAL': LINGUA_TERMINAL,
                    'THEMA_APP1': THEMA_APP1,
                    'THEMA_APP2': THEMA_APP2,
                    'THEMA_RUN': THEMA_RUN,
                    'FONTE_MENU': FONTE_MENU,
                    'FONTE_TAM_MENU': FONTE_TAM_MENU,
                    'FONTE_COR_MENU': FONTE_COR_MENU,
                    'FONTE_CAMPO': FONTE_CAMPO,
                    'FONTE_TAM_CAMPO': FONTE_TAM_CAMPO,
                    'FONTE_COR_CAMPO': FONTE_COR_CAMPO,
                    'FONTE_TAM_RUN': FONTE_TAM_RUN,
                    'OBS': OBS
                })

                st.session_state['custom_loaded'] = selected_custom

        elif selected_custom == "Nova Customização":
            # Limpa session_state para nova customização
            for key in ['NOME_CUSTOM', 'NOME_USUARIO', 'CAMINHO_DOWNLOAD', 'IMAGEM_LOGO',
                        'THEMA_EDITOR', 'EDITOR_TAM_MENU', 'THEMA_TERMINAL', 'LINGUA_TERMINAL',
                        'THEMA_APP1', 'THEMA_APP2', 'THEMA_RUN',
                        'FONTE_MENU', 'FONTE_TAM_MENU', 'FONTE_COR_MENU',
                        'FONTE_CAMPO', 'FONTE_TAM_CAMPO', 'FONTE_COR_CAMPO',
                        'FONTE_TAM_RUN', 'BORDA', 'RADIAL', 'DECORA', 'OPC1', 'OPC2', 'OPC3', 'OBS']:
                st.session_state[key] = None
            st.session_state['custom_loaded'] = None

        from Banco_dados import esc_CUSTOMIZATION


        st.session_state.get('IMAGEM_LOGO')

        st1, st2 = st.columns(2)

        if selected_custom == "Nova Customização":

            IMAGEM_LOGO = st1.file_uploader("Escolher imagem", type=["png", "jpg", "jpeg", "gif"])
            if IMAGEM_LOGO:
                st2.image(IMAGEM_LOGO)

            st1, st2 = st.columns(2)

            NOME_CUSTOM = st1.text_input("Nome da customização")
            NOME_USUARIO = st2.text_input("Nome do usuário")
            caminho_download = st.text_input("Caminho de download padrão", default_download)
            # Validação: verifica se o caminho existe
            if not os.path.exists(caminho_download):
                st.warning("O caminho digitado não existe. Será usado o padrão 'Downloads'.")
                CAMINHO_DOWNLOAD = default_download
            else:
                CAMINHO_DOWNLOAD = caminho_download

            st.divider()
            st1, st2, st3 = st.columns([3, 4, 1.5])
            MODO_TEMA_EDITOR = st1.selectbox("Modo Editor", ["Escuro", "Claro"])
            LISTA_TEMAS_EDITOR = TEMAS_CLAROS if MODO_TEMA_EDITOR == "Claro" else TEMAS_ESCUROS
            THEMA_EDITOR = st2.selectbox("Opc do editor", LISTA_TEMAS_EDITOR)
            EDITOR_TAM_MENU = st3.number_input("Tam Edit", 8, 48, 13)

            value = '''from datetime import datetime
    
    def main():
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print("Bem-vindo ao sistema")
        print(f"Data e hora atuais: {agora}")
    
    if __name__ == "__main__":
        main()
    '''


            code_editor(value,
                lang='python',
                options= {"fontSize": EDITOR_TAM_MENU,
                          "theme": f"ace/theme/{THEMA_EDITOR}","showLineNumbers": True,"showInvisibles": True}, # Tamanho da fonte}, ,
                height=f'200px'

            )

            st.divider()
            st1, st2, st3 = st.columns([3, 4, 1.5])

            MODO_TEMA_PREVIEW= st1.selectbox("Modo Preview", ["Escuro", "Claro"])
            LISTA_TEMAS_PREVIEW = TEMAS_CLAROS if MODO_TEMA_PREVIEW == "Claro" else TEMAS_ESCUROS
            THEMA_PREVIEW = st2.selectbox("Opc do Preview", LISTA_TEMAS_PREVIEW)
            PREVIEW_TAM_MENU = st3.number_input("Tam Prev", 8, 48, 13)

            value = r''':\Users\henri\PycharmProjects\IDE_TOP\.venv\Scripts\python.exe 
    2026-01-13 17:34:19,806 | WARNING | Arquivo de tarefas não encontrado. Criando novo.
    2026-01-13 17:34:19,806 | INFO | Tarefa adicionada: Estudar Python
    2026-01-13 17:34:19,807 | INFO | Tarefa adicionada: Criar app Streamlit
    2026-01-13 17:34:19,807 | INFO | Tarefa concluída: Estudar Python
    2026-01-13 17:34:19,809 | INFO | Tarefas salvas.
    
    TAREFAS CONCLUÍDAS:
    - Estudar Python (2026-01-13T17:34:19.804316)
    
    TAREFAS PENDENTES:
    - Criar app Streamlit
    
    Process finished with exit code 0
                '''
            code_editor(value,
                        lang='python',
                        options={"fontSize": PREVIEW_TAM_MENU,
                                 "theme": f"ace/theme/{THEMA_PREVIEW}",
                        "showGutter": False},
            height=f'200px'

                        )
            st.divider()
            value = rf'''O Windows PowerShell
    Copyright (C) Microsoft Corporation. Todos os direitos reservados.
    
    Instale o PowerShell mais recente para obter novos recursos e aprimoramentos! https://aka.ms/PSWindows
    
    (.venv) PS C:\Users\henri\PycharmProjects\IDE_TOP> pip --version
    pip 25.3 from C:\Users\henri\PycharmProjects\IDE_TOP\.vambiente\Lib\site-pacotes\pip (python 3.13)
    (.venv) PS C:\Users\henri\PycharmProjects\IDE_TOP> pip list
    Pacote                   Versão
    ------------------------- -----------
    altair                    6.0.0
    attrs                     25.4.0
    blinker                   1.9.0'''
            st1, st2, st3 = st.columns([3, 4, 1.5])
            MODO_TEMA_PREVIEW = st1.selectbox("Modo Terminal", ["Escuro", "Claro"])
            LISTA_TEMAS_TERMINAL = TEMAS_CLAROS if MODO_TEMA_PREVIEW == "Claro" else TEMAS_ESCUROS
            THEMA_TERMINAL = st2.selectbox("Tema do Terminal", LISTA_TEMAS_TERMINAL)

            TERMINAL_TAM_MENU = st3.number_input("Tam Term", 8, 48, 13)

            code_editor(value,
                        lang='powershell',
                        options={"fontSize": TERMINAL_TAM_MENU,
                                 "theme": f"ace/theme/{THEMA_TERMINAL}",
                                 "showGutter": False,},
                        height=f'200px'

                        )
            st.divider()
            st0, st1, st2, st3 = st.columns([1, 2, 1.5, 1])

            # Cores escuras harmoniosas para temas profissionais
            THEMA_APP2 = st0.color_picker("Corpo", "#24283b")  # Dark Slate (seções secundárias)

            THEMA_APP1 = st0.color_picker("Sidibar/Rodapé", "#1a1b26")  # Deep Charcoal (fundo principal)

            FONTE_MENU = st1.selectbox("Fonte Menus", FONTES_TEXTO)
            FONTE_TAM_MENU = st2.number_input("Tam menu", min_value=8, max_value=48, value=13)
            FONTE_COR_MENU = st3.color_picker("Menu", "#FFA500")

            FONTE_CAMPO = st1.selectbox("Fonte Campos", FONTES_TEXTO)
            FONTE_TAM_CAMPO = st2.number_input("Tam campos", min_value=8, max_value=48, value=13)
            FONTE_COR_CAMPO = st3.color_picker("Campos", "#FFA500")
            TIPO_BORDA = st1.selectbox("Fonte Campos", ['solid','dashed','dotted','ridge','inset','hidden'])

            # Substitua TODOS os st.markdown por ESTE:
            st.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Fira+Code&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,400;1,400&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    
            .preview-box {{
                background: {THEMA_APP1};
                padding: 2rem;
                border-radius: 1rem;
                margin: 1rem 0;
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                font-family: Arial, sans-serif;
                border: 2px {TIPO_BORDA} {FONTE_COR_CAMPO} !important;
                
            }}
    
            .menu-title {{
                font-family: '{FONTE_MENU}', monospace !important;
                font-size: {FONTE_TAM_MENU}px !important;
                color: {FONTE_COR_MENU} !important;
                font-weight: 700 !important;
                padding: 1.5rem;
                background: {THEMA_APP2};
                border-radius: 0.75rem;
                margin-bottom: 1.5rem;
                text-align: center;
    
            }}
    
            .form-section {{
                background: {THEMA_APP1};
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 2px {TIPO_BORDA} {FONTE_COR_CAMPO} !important;
                
            }}
    
            .form-group label {{
                font-family: '{FONTE_MENU}', monospace !important;
                font-size: {FONTE_TAM_MENU}px !important;
                color: {FONTE_COR_MENU} !important;
                font-weight: 600 !important;
                display: block;
                margin-bottom: 0.5rem;
    
            }}
    
            .form-group input,
            .form-group select,
            .form-group textarea {{
                font-family: '{FONTE_CAMPO}', monospace !important;
                font-size: {FONTE_TAM_CAMPO}px !important;
                color: {FONTE_COR_CAMPO} !important;
                width: 100% !important;
                padding: 0.75rem !important;
                border-radius: 0.5rem !important;
            }}
            </style>
            </head>
            <body>
            <div class="preview-box">
                <div class="menu-title">🎛️ CUSTON: * {NOME_CUSTOM} * </div>
                <div class="form-section">
                    <div class="form-group">
                        <label>{FONTE_MENU} ({FONTE_TAM_MENU}px):</label>
                        <input type="text" value="{FONTE_CAMPO} ({FONTE_TAM_CAMPO}px)">
                    </div>
                    <div class="form-group">
                        <label>Seleção:</label>
                        <select><option>Opção 1</option><option selected>Opção 2</option></select>
                    </div>
                </div>
            </div>
            </body>
            </html>
            """, )

            st.divider()

            st.write('')
            submitted = st.button("Salvar Customização", type="primary",width='stretch')
            st.write('')
            st.write('')

            if submitted:
                from pathlib import Path

                # Cria pasta arquivos se não existir
                pasta_arquivos = _DIRETORIO_EXECUTAVEL_('mim_mids')
                pasta_arquivos.mkdir(exist_ok=True)
                if IMAGEM_LOGO is not None:
                    try:
                        # Gera nome único baseado no timestamp
                        nome_arquivo = f"imagem_{st.session_state.get('contador_imagem', 0):03d}.{IMAGEM_LOGO.name.split('.')[-1]}"
                        caminho_completo = pasta_arquivos / nome_arquivo

                        # Salva o arquivo
                        with open(caminho_completo, "wb") as f:
                            f.write(IMAGEM_LOGO.getbuffer())

                        # Incrementa contador
                        if 'contador_imagem' not in st.session_state:
                            st.session_state.contador_imagem = 0
                        st.session_state.contador_imagem += 1

                        # Retorna o caminho absoluto
                        caminho_absoluto = caminho_completo.absolute()

                        st.success(f"✅ Imagem salva com sucesso!")
                        st.info(f"**Caminho da imagem:** `{caminho_absoluto}`")

                        # Copia para clipboard (opcional)
                        st.code(f"{caminho_absoluto}", language="text")

                        esc_CUSTOMIZATION(NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD, str(caminho_absoluto),
                                          THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_PREVIEW, PREVIEW_TAM_MENU,
                                          THEMA_TERMINAL, TERMINAL_TAM_MENU,
                                          THEMA_APP1, THEMA_APP2,
                                          FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
                                          FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
                                          0, 3, TIPO_BORDA, '#04061a',
                                      '',0,'ATIVO')

                        ATUAL_CUSTOMIZATION_nome(NOME_CUSTOM)
                        Alerta(f'Beleza {NOME_CUSTOM} Já pintamos essa Budega!')
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
                else:
                    esc_CUSTOMIZATION(NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD,
                                      os.path.join(pasta_arquivos, 'logo_.png'),
                                      THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_PREVIEW, PREVIEW_TAM_MENU,
                                      THEMA_TERMINAL, TERMINAL_TAM_MENU,
                                      THEMA_APP1, THEMA_APP2,
                                      FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
                                      FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
                                      0, 3, TIPO_BORDA, 	'#04061a',
                                      '',0,'ATIVO')

                    ATUAL_CUSTOMIZATION_nome(NOME_CUSTOM)
                st.session_state.dialog_criar_customizar = False
                st.session_state["Customizar_state"] = False
                st.rerun()
        else:
            if st.session_state.get('IMAGEM_LOGO'):
                st2.image(st.session_state.get('IMAGEM_LOGO'))

            st1.text_input("Nome da customização", st.session_state.get('NOME_CUSTOM'), disabled=True)
            st2.text_input("Nome do usuário", st.session_state.get('NOME_USUARIO'), disabled=True)
            st.text_input("Caminho de download padrão", st.session_state.get('CAMINHO_DOWNLOAD'), disabled=True)

            submitted = st.button("Ultilizar Customização")
            if submitted:
                ATUAL_CUSTOMIZATION_nome(st.session_state.get('NOME_CUSTOM'))
                st.session_state.dialog_criar_customizar = False

                st.rerun()

    menu_principal()

LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "Texto": ".txt",
    "JavaScript": ".js",
    "HTML": ".html",
    "CSS": ".css",
    "JSON": ".json",
    "Markdown": ".md",
    "C++": ".cpp",
    "Java": ".java",
    "PHP": ".php",
    "Ruby": ".rb",
}


def Cria_Arquivos(st):
    @st.dialog("Criar Arquivos Pastas: ", dismissible=False)
    def menu_principal():
        st1, st2 = st.columns([8, 1])

        if st2.button("X", key="Cria_Arquivos"):
            st.session_state["Cria_Arquivos_state"] = False
            st.rerun()

        if "linguagem" not in st.session_state:
            st.session_state.linguagem = None

        if "tipo_criacao" not in st.session_state:
            st.session_state.tipo_criacao = "Arquivo"

        Menu_Principal, Sub_Menu = st.columns([1, 2])

        with Menu_Principal:
            tipo_criacao = st.selectbox(
                "Tipo:",
                ["Arquivo", "Pasta Simples", "Pasta com __init__"],
                label_visibility="collapsed",
                key="select_tipo_criacao"
            )
            st.session_state.tipo_criacao = tipo_criacao

            if tipo_criacao == "Arquivo":
                linguagem = st.selectbox(
                    "Linguagem:",
                    ["Novo:"] + list(LANGUAGE_EXTENSIONS.keys()),
                    index=0,
                    label_visibility="collapsed",
                    key="select_linguagem"
                )
                st.session_state.linguagem = linguagem
            else:
                st.session_state.linguagem = None

        with Sub_Menu:
            nome = st.chat_input("Nome")

            if nome:
                Pasta_RAIZ_projeto = _DIRETORIO_PROJETO_ATUAL_()
                nome_limpo = str(nome).strip().replace(" ", "_")

                if st.session_state.tipo_criacao == "Arquivo":
                    if st.session_state.linguagem and st.session_state.linguagem != "Novo:":
                        extensao = LANGUAGE_EXTENSIONS[st.session_state.linguagem]
                        nome_final = nome_limpo + extensao
                        Caminho_Absoluto = os.path.join(Pasta_RAIZ_projeto, nome_final)

                        Criar_Arquivo_TEXTO(
                            Pasta_RAIZ_projeto,
                            nome_limpo,
                            "",
                            extensao
                        )

                        st.success(f"Arquivo criado: {nome_final}")
                        st.session_state["Cria_Arquivos_state"] = False
                        st.rerun()

                elif st.session_state.tipo_criacao == "Pasta Simples":
                    caminho_pasta = os.path.join(Pasta_RAIZ_projeto, nome_limpo)
                    os.makedirs(caminho_pasta, exist_ok=True)

                    st.success(f"Pasta criada: {nome_limpo}")
                    st.session_state["Cria_Arquivos_state"] = False
                    st.rerun()

                elif st.session_state.tipo_criacao == "Pasta com __init__":
                    caminho_pasta = os.path.join(Pasta_RAIZ_projeto, nome_limpo)
                    os.makedirs(caminho_pasta, exist_ok=True)

                    caminho_init = os.path.join(caminho_pasta, "__init__.py")
                    if not os.path.exists(caminho_init):
                        with open(caminho_init, "w", encoding="utf-8") as f:
                            f.write("")

                    st.success(f"Pasta package criada: {nome_limpo}")
                    st.session_state["Cria_Arquivos_state"] = False
                    st.rerun()

    menu_principal()


def Cria_Arq_loc(st, caminho):
    @st.dialog("Criar Arquivos Pastas :", dismissible=True)
    def menu_principal():

        if "acoes" not in st.session_state:
            st.session_state["acoes"] = []

        col_menu, col_main = st.columns([1, 3])

        with col_menu:


            if st.button("📁 Pasta", use_container_width=True):
                st.session_state["acoes"].append(
                    {"tipo": "Pasta Simples", "nome": ""}
                )

            if st.button("📦 Pasta + __init__", use_container_width=True):
                st.session_state["acoes"].append(
                    {"tipo": "Pasta com __init__", "nome": ""}
                )

            st.divider()

            for lang, ext in LANGUAGE_EXTENSIONS.items():
                icone = Sinbolos("x" + ext)
                if st.button(f"{icone} {lang}", use_container_width=True):
                    st.session_state["acoes"].append(
                        {"tipo": "Arquivo", "ext": ext, "nome": ""}
                    )

        with col_main:

            for i, acao in enumerate(st.session_state["acoes"]):

                icone = ""
                if acao["tipo"] == "Arquivo" and acao.get("ext"):
                    icone = Sinbolos("x" + acao["ext"])
                elif acao["tipo"] == "Pasta Simples":
                    icone = "📁"
                elif acao["tipo"] == "Pasta com __init__":
                    icone = "📦"

                label = f"{icone} {acao['tipo']}"
                if acao.get("ext"):
                    label += f" ({acao['ext']})"

                st.session_state["acoes"][i]["nome"] = st.text_input(
                    f"Nome para {label}",
                    key=f"nome_{i}"
                )

            if st.session_state["acoes"]:
                if st.button("CRIAR TUDO", use_container_width=True):

                    for acao in st.session_state["acoes"]:
                        nome = acao.get("nome", "").strip()
                        if not nome:
                            continue

                        nome_limpo = nome.replace(" ", "_")

                        if acao["tipo"] == "Arquivo":
                            Criar_Arquivo_TEXTO(
                                caminho,
                                nome_limpo,
                                "",
                                acao["ext"]
                            )

                        elif acao["tipo"] == "Pasta Simples":
                            os.makedirs(
                                os.path.join(caminho, nome_limpo),
                                exist_ok=True
                            )

                        elif acao["tipo"] == "Pasta com __init__":
                            pasta = os.path.join(caminho, nome_limpo)
                            os.makedirs(pasta, exist_ok=True)

                            init_file = os.path.join(pasta, "__init__.py")
                            if not os.path.exists(init_file):
                                with open(init_file, "w", encoding="utf-8") as f:
                                    f.write("")

                    st.session_state["acoes"].clear()
                    from APP_SUB_Funcitons import limpar_CASH
                    limpar_CASH()

        return True

    menu_principal()


def Abrir_Projeto(st):
    st.session_state.setdefault("Abrir_Projetos", True)

    @st.dialog("Abrir Projeto:", dismissible=False)
    def menu_principal():
        st1, st2 = st.columns([8, 1])

        # CORREÇÃO: Usar callback ao invés de modificar session_state diretamente
        def fechar_dialogo():
            st.session_state["Abrir_Projeto_state"] = False

        if st2.button("X", key="btn_fechar_projeto", on_click=fechar_dialogo):
            st.rerun()

        RESULTADO = Janela_PESQUIZA(st, _DIRETORIO_PROJETOS_())

        if RESULTADO[0]:
            caminho, tipo = RESULTADO
            nome_arq = os.path.basename(caminho)
            extensao = Path(caminho).suffix

            if tipo == '📄 ARQUIVO':
                if st.button(f"📄 **Abrir: {nome_arq}**", width='stretch', key=f"abrir_arq_{nome_arq}"):
                    try:
                        with open(caminho, "r", encoding="utf-8") as f:
                            conteudo = f.read()
                        esc_CONTROLE_ARQUIVOS(nome_arq, caminho, conteudo, extensao)
                        st.session_state.nova_pasta_selecionada = (nome_arq, caminho)
                        st.success(f"✅ {nome_arq} salvo no banco!")
                        st.session_state.Abrir_Projeto = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao ler: {e}")

            elif tipo == '📁 DIRETÓRIO':
                r = resumo_pasta(RESULTADO[0])
                st.code(f'''{r['pasta']}: Pastas: {r['subpastas']} Arquivos {r['arquivos']}
Criada: {r['criado']} Modificada: {r['modificado']}
Extensões: {r['extensoes']}''')

                if st.button(f"**Abrir Projeto: {nome_arq}**", width='stretch', key=f"abrir_proj_{nome_arq}"):
                    try:
                        pasta_pai = Path(caminho).parent
                        st.write(caminho, pasta_pai)
                        esc_A_CONTROLE_PROJETOS(str(caminho), '', data_sistema(), '', '', '')

                        st.session_state.nova_pasta_selecionada = (nome_arq, caminho)
                        st.success(f"✅ Projeto {nome_arq} salvo no banco!")
                        from APP_SUB_Funcitons import limpar_CASH

                        limpar_CASH()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar projeto: {e}")
                    fechar_dialogo()

                    st.rerun()

    # Inicializar estado do dialog
    if "Abrir_Projeto_state" not in st.session_state:
        st.session_state["Abrir_Projeto_state"] = True

    if st.session_state["Abrir_Projeto_state"]:
        menu_principal()


def Abrir_Menu(st):
    with st.popover("Menu"):

        try:
            #st.link_button(label="",url="https://www.youtube.com/@topcodebuytrap",icon=":material/link:",icon_position="left")
            if Button_Nao_Fecha(':material/dashboard_customize: ',
                                    ':material/dashboard_customize: Cria_Projeto',
                                    key="Cria_Projeto"):
                Cria_Projeto(st)
            if Button_Nao_Fecha(':material/folder_open:',
                                ':material/folder_open: Abrir_Projeto',
                                    key="Abrir_Projeto"):
                Abrir_Projeto(st)

            if Button_Nao_Fecha(':material/library_add:',
                                    ':material/library_add: Cria_Arquivos',
                                    key="Cria_Arquivos"):
                Cria_Arquivos(st)
            if Button_Nao_Fecha(":material/format_paint:", ':material/format_paint: Customizar',
                                key="Customizar"):
                Custom(st)

        except streamlit.errors.StreamlitDuplicateElementKey as e:
            Alerta(st,f'Mano/a YOU Deixou 2 Botões Clicado! \nPtqp...')

def Cria_Projeto_(st):
    import streamlit as st
    st.session_state.setdefault("criar_projeto", True)
    @st.dialog("Criar Projeto: ",dismissible=False ,width='large')
    def menu_principal():
        from Banco_dados import listar_templates, salvar_template, carregar_template
        st1, st2 = st.columns([8, 1])
        st.write("'Henriq colocar para instalar modulos pre configurados!'")
        if st2.button("X", key="Cria_Projeto"):
            st.session_state["Cria_Projeto_state"] = False
            st.rerun()

        col1,col2, col3 = st.columns([5,2,2])

        if "abas" not in st.session_state:
            st.session_state.abas = ["Terminal"]

        if "contador_local" not in st.session_state:
            st.session_state.contador_local = 0

        def abrir_nova_aba():
            st.session_state.contador_local += 1
            nome = f"Local {st.session_state.contador_local}"
            st.session_state.abas.append(nome)
            st.rerun()

        def fechar_aba(nome):
            if nome != "Terminal":
                st.session_state.abas.remove(nome)
                st.rerun()
        # =========================
        # DADOS DO PROJETO
        caminho_base = col1.text_input("**Criar em:**", _DIRETORIO_PROJETOS_())
        nome_projeto = col2.text_input("Nome do projeto")
        # =========================
        # ARQUIVOS INICIAIS
        with st.expander("📁 Arquivos iniciais do projeto", expanded=False):

            if "arquivos_projeto" not in st.session_state:
                st.session_state.arquivos_projeto = [
                    {
                        "nome": "main.py",
                        "conteudo": "# Arquivo principal\n\nif __name__ == '__main__':\n    print('Projeto iniciado')\n"
                    }
                ]

            templates = listar_templates()
            template_sel = st.selectbox(
                "Template salvo",
                ["(novo)"] + templates
            )

            if template_sel != "(novo)":
                st.session_state.arquivos_projeto = carregar_template(template_sel)

            for i, arq in enumerate(st.session_state.arquivos_projeto):
                col1, col2 = st.columns([2, 7])

                #st.markdown(f"**Arquivo {i+1}**")

                arq["nome"] = col1.text_input(
                    "Nome do arquivo",
                    arq["nome"],
                    key=f"nome_arq_{i}"
                )

                if col1.button(f":material/delete_forever: Não Te Quero: {arq["nome"]}", key=f"del_arq_{i}",width='stretch'):
                    st.session_state.arquivos_projeto.pop(i)
                    st.rerun()

                arq["conteudo"] = col2.text_area(
                    "Conteúdo",
                    arq["conteudo"],
                    height=150,
                    key=f"cont_arq_{i}",label_visibility='collapsed'
                )

            if col1.button(":material/add: Adicionar arquivo",width='stretch'):
                st.session_state.arquivos_projeto.append(
                    {"nome": "", "conteudo": ""}
                )
                st.rerun()

            st.divider()
            col1, col2 = st.columns(2)

            nome_template = col1.text_input("Salvar como template")
            col2.space()
            if col2.button(":material/save: Salvar template",width='stretch'):
                if nome_template.strip() and template_sel != '':
                    salvar_template(str(nome_template).title(), st.session_state.arquivos_projeto)
                    st.success("Template salvo com sucesso!")
                else:
                    st.warning('Dê um nome ao template?')
                st.session_state["Cria_Projeto_state"] = False
                st.rerun()

        st.divider()
        # =========================
        # CRIAÇÃO DO PROJETO
        # =========================
        pythons = listar_pythons_windows()

        if not pythons:
            st.error("Nenhum Python encontrado em AppData")
            return

        python_selecionado = col3.selectbox(
            "Python base do projeto",
            list(pythons.keys()),
            index=0
        )

        if st.button("✅ Confirmar criação",width='stretch'):

            if not nome_projeto.strip():
                st.error("Nome do projeto inválido")
                return

            projeto_path = Path(caminho_base) / nome_projeto.replace(" ", "_")
            venv_path = projeto_path / ".virto_stream"
            python_base = pythons[python_selecionado]
            esc_A_CONTROLE_PROJETOS(Path(caminho_base) / nome_projeto.replace(" ", "_"),python_selecionado,data_sistema(),
                                    0,0, 'Criado Com TcbT!')

            progresso = st.progress(0)
            log_area = st.empty()

            logs = []

            def log(msg, pct=None):
                logs.append(msg)
                log_area.code("\n".join(logs), language="bash")
                if pct is not None:
                    progresso.progress(pct)

            try:
                # 1️⃣ Criar pasta do projeto
                log("📁 Criando pasta do projeto...", 5)
                projeto_path.mkdir(parents=True, exist_ok=False)

                # 2️⃣ Criar ambiente virtual
                log("🐍 Criando ambiente virtual...", 25)
                CREATE_NO_WINDOW = 0x08000000

                subprocess.run(
                    [python_base, "-m", "venv", str(venv_path)],
                    check=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_NO_WINDOW)

                python_venv = (
                    venv_path / "Scripts" / "python.exe"
                    if sys.platform == "win32"
                    else venv_path / "bin" / "python"
                )

                # 3️⃣ Atualizar pip
                log("⬆️ Atualizando pip...", 50)
                subprocess.run(
                    [str(python_venv), "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_NO_WINDOW)

                # 4️⃣ Criar arquivos do usuário
                log("📝 Criando arquivos do projeto...", 75)
                for arq in st.session_state.arquivos_projeto:
                    if arq["nome"].strip():
                        caminho = projeto_path / arq["nome"]
                        caminho.parent.mkdir(parents=True, exist_ok=True)
                        caminho.write_text(arq["conteudo"], encoding="utf-8")
                        log(f"   ✔ {arq['nome']}")

                # 5️⃣ Finalização
                log("✅ Projeto criado com sucesso!", 100)
                st.success(f"🎉 Projeto criado com sucesso usando {python_selecionado}")

                st.session_state.criar_projeto = False
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
            except FileExistsError:
                log("❌ Erro: o projeto já existe")
                st.error("O projeto já existe")

            except subprocess.CalledProcessError as e:
                log("❌ Erro ao criar ambiente virtual ou instalar dependências")
                st.exception(e)

            except Exception as e:
                log("❌ Erro inesperado")
            st.exception(e)
    menu_principal()


def Cria_Projeto(st):
    st.session_state.setdefault("criar_projeto", True)

    @st.dialog("Criar Projeto:", dismissible=False, width="large")
    def menu_principal():
        from Banco_dados import listar_templates, salvar_template, carregar_template

        st1, st2 = st.columns([8, 1])
        st1.write("'**Henriq instalar módulos pré-configurados!**'")

        if st2.button("X", key="Cria_Projeto"):
            st.session_state["Cria_Projeto_state"] = False
            st.rerun()

        col1, col2, col3 = st.columns([5, 2, 2])

        if "abas" not in st.session_state:
            st.session_state.abas = ["Terminal"]

        if "contador_local" not in st.session_state:
            st.session_state.contador_local = 0

        def abrir_nova_aba():
            st.session_state.contador_local += 1
            nome = f"Local {st.session_state.contador_local}"
            st.session_state.abas.append(nome)
            st.rerun()

        def fechar_aba(nome):
            if nome != "Terminal":
                st.session_state.abas.remove(nome)
                st.rerun()

        # =========================
        # DADOS DO PROJETO
        caminho_base = col1.text_input("**Criar em:**", _DIRETORIO_PROJETOS_())
        nome_projeto = col2.text_input("Nome do projeto")

        # ARQUIVOS INICIAIS
        with st.expander("📁 Arquivos iniciais do projeto", expanded=False):

            if "arquivos_projeto" not in st.session_state:
                st.session_state.arquivos_projeto = [
                    {
                        "nome": "main.py",
                        "conteudo": "# Arquivo principal\n\nif __name__ == '__main__':\n    print('Projeto iniciado')\n"
                    }
                ]

            templates = listar_templates()
            template_sel = st.selectbox(
                "Template salvo",
                ["(novo)"] + templates
            )

            if template_sel != "(novo)":
                st.session_state.arquivos_projeto = carregar_template(template_sel)

            for i, arq in enumerate(st.session_state.arquivos_projeto):
                col1, col2 = st.columns([2, 7])

                arq["nome"] = col1.text_input(
                    "Nome do arquivo",
                    arq["nome"],
                    key=f"nome_arq_{i}"
                )

                if col1.button(f":material/delete_forever: Não Te Quero: {arq["nome"]}", key=f"del_arq_{i}",
                               width='stretch'):
                    st.session_state.arquivos_projeto.pop(i)
                    st.rerun()

                arq["conteudo"] = col2.text_area(
                    "Conteúdo",
                    arq["conteudo"],
                    height=150,
                    key=f"cont_arq_{i}", label_visibility='collapsed'
                )

            if col1.button(":material/add: Adicionar arquivo", width='stretch'):
                st.session_state.arquivos_projeto.append(
                    {"nome": "", "conteudo": ""}
                )
                st.rerun()

            st.divider()
            col1, col2 = st.columns(2)

            nome_template = col1.text_input("Salvar como template")
            col2.space()
            if col2.button(":material/save: Salvar template", width='stretch'):
                if nome_template.strip() and template_sel != '':
                    salvar_template(str(nome_template).title(), st.session_state.arquivos_projeto)
                    st.success("Template salvo com sucesso!")
                else:
                    st.warning('Dê um nome ao template?')
            try:
                from Banco_dados import Criar_sqlite

                Sqlite, NOME_BANCO, PASTA_BANCO = Criar_sqlite(st)
            except TypeError: pass


        st.divider()

        # =========================
        # SELEÇÃO DE MÓDULOS ✅ NOVO
        st.subheader("📦 **Módulos para instalar**")
        col1, col2 = st.columns(2)

        # Carrega módulos do banco
        modulos_disponiveis = listar_modulos()
        nomes_modulos = [modulo["nome"] for modulo in modulos_disponiveis]

        # Multiselect dos módulos pré-definidos
        modulos_selecionados = col2.multiselect(
            "Escolha os módulos (Ctrl+click para múltiplos):",
            nomes_modulos,key="modulos_projeto"
            #default=["streamlit-desktop"],  # Padrão Streamlit

        )

        # Input para módulos customizados + SALVAR NO BANCO
        novo_modulo = col1.text_input("🔧 Ou digite comando pip customizado:",
                                      placeholder="pip install requests beautifulsoup4",
                                      key="novo_modulo_input")

              # =========================
        # PYTHON SELECIONADO
        pythons = listar_pythons_windows()

        if not pythons:
            st.error("Nenhum Python encontrado em AppData")
            return

        python_selecionado = col3.selectbox(
            "Python base do projeto",
            list(pythons.keys()),
            index=0
        )

        if st.button("✅ Confirmar criação", width='stretch'):

            if not nome_projeto.strip():
                st.error("Nome do projeto inválido")
                return

            projeto_path = Path(caminho_base) / nome_projeto.replace(" ", "_")
            venv_path = projeto_path / ".virto_stream"
            python_base = pythons[python_selecionado]
            esc_A_CONTROLE_PROJETOS(
                Path(caminho_base) / nome_projeto.replace(" ", "_"),
                python_selecionado,
                data_sistema(),
                0, 0, 'Criado Com TcbT!'
            )

            progresso = st.progress(0)
            log_area = st.empty()
            logs = []

            def log(msg, pct=None):
                logs.append(msg)
                log_area.code("\n".join(logs), language="bash")
                if pct is not None:
                    progresso.progress(pct)

            try:

                if novo_modulo.strip():
                    nome = novo_modulo.split("pip install")[-1].strip().split()[0].split("-")[0]
                    uninstall = novo_modulo.replace("pip install", "pip uninstall") + " -y"
                    upgrade = novo_modulo.replace("pip install", "pip install --upgrade")
                    salvar_modulo(nome, novo_modulo, uninstall, upgrade, "Novo Projeto")
                    log(
                        f"💾 Salvo banco [Módulos] pip install {nome}, "
                        f"pip install {nome} --upgrade, pip uninstall {nome} -y",
                        5
                    )

                sleep(1)

                log(f"📁 Criando pasta do projeto...{caminho_base} > {nome_projeto}", 10)
                projeto_path.mkdir(parents=True, exist_ok=False)
                sleep(1)

                if novo_modulo.strip() or modulos_selecionados:

                    log("📄 Criando requirements.txt...", 20)
                    reqs = modulos_selecionados.copy()
                    if novo_modulo.strip():
                        reqs.append(novo_modulo.split()[-1])

                    with open(projeto_path / "requirements.txt", "w", encoding="utf-8") as f:
                        for req in reqs:
                            f.write(req + "\n")

                    sleep(1)

                    log("✅ requirements.txt criado com:", 25)
                    for req in reqs:
                        log(f"   - {req}")
                    sleep(1)

                log("🐍 Criando ambiente virtual...", 30)
                CREATE_NO_WINDOW = 0x08000000
                with st.spinner("🧪 Criando .virto_stream..."):
                    subprocess.run(
                        [python_base, "-m", "venv", str(venv_path)],
                        check=True,
                        startupinfo=STARTUPINFO,
                        creationflags=CREATE_NO_WINDOW
                    )

                    python_venv = (
                        venv_path / "Scripts" / "python.exe"
                        if sys.platform == "win32"
                        else venv_path / "bin" / "python"
                    )

                pct_modulo = 40
                todos_modulos = modulos_selecionados.copy()

                if novo_modulo.strip():
                    todos_modulos.append("custom")

                log("⬆️ Atualizando pip...", 40)
                subprocess.run(
                    [str(python_venv), "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_NO_WINDOW
                )

                if todos_modulos:
                    log("📦 Instalando módulos selecionados...", 50)
                    with st.spinner("⚙️ Instalando pacotes no ambiente virtual..."):
                        for modulo in todos_modulos:
                            if modulo == "custom":
                                log(f"   🔧 Custom: {novo_modulo}", pct_modulo)
                                full_cmd = novo_modulo.replace(
                                    "pip install",
                                    f"{str(python_venv)} -m pip install"
                                )
                                subprocess.run(
                                    full_cmd.split(),
                                    check=True,
                                    startupinfo=STARTUPINFO,
                                    creationflags=CREATE_NO_WINDOW,
                                    capture_output=True
                                )
                                log("   ✅ Custom instalado", pct_modulo + 10)
                                pct_modulo += 10
                            else:
                                cmd_install = carregar_comando_modulo(modulo, "install")
                                if cmd_install:
                                    log(f"   📥 {modulo}...", pct_modulo)
                                    full_cmd = cmd_install.replace(
                                        "pip install",
                                        f"{str(python_venv)} -m pip install"
                                    )
                                    subprocess.run(
                                        full_cmd.split(),
                                        check=True,
                                        startupinfo=STARTUPINFO,
                                        creationflags=CREATE_NO_WINDOW,
                                        capture_output=True
                                    )
                                    log(f"   ✅ {modulo}", pct_modulo + 8)
                                    pct_modulo += 8

                log("📝 Criando arquivos do projeto...", 95)
                for arq in st.session_state.arquivos_projeto:
                    if arq["nome"].strip():
                        caminho = projeto_path / arq["nome"]
                        caminho.parent.mkdir(parents=True, exist_ok=True)
                        caminho.write_text(arq["conteudo"], encoding="utf-8")
                        log(f"   ✔ {arq['nome']}")
                try:
                    if Sqlite and NOME_BANCO and PASTA_BANCO:
                        pasta_banco_path = projeto_path / PASTA_BANCO
                        pasta_banco_path.mkdir(parents=True, exist_ok=True)
                        caminho_arquivo = pasta_banco_path / NOME_BANCO
                        caminho_arquivo.write_text(Sqlite, encoding="utf-8")

                        st.write('tem tudo')
                        st.write('Sqlite', NOME_BANCO, PASTA_BANCO)
                    else:
                        caminho_arquivo = projeto_path / NOME_BANCO
                        caminho_arquivo.write_text(Sqlite, encoding="utf-8")

                        st.write('falta = PASTA_BANCO')
                        st.write('Sqlite', NOME_BANCO, PASTA_BANCO)
                except UnboundLocalError:
                    pass


                log("✅ Projeto criado com sucesso!", 100)
                st.success(f"🎉 Projeto criado com sucesso usando {python_selecionado}")

                st.balloons()
                sleep(2)
                st.session_state.criar_projeto = False
                st.session_state["Cria_Projeto_state"] = False

                from APP_SUB_Funcitons import limpar_CASH
                limpar_CASH()
                st.rerun()
                st.stop()

            except FileExistsError:
                log("❌ Erro: o projeto já existe")
                st.error("O projeto já existe")

            except subprocess.CalledProcessError as e:
                log("❌ Erro ao criar ambiente virtual ou instalar dependências")
                st.exception(e)

            except Exception as e:
                log("❌ Erro inesperado")
                st.exception(e)

    menu_principal()


def Cria_Projeto_pouppap(st):# só usado um unica vez quando inicia o programa pela primeira vez
    from Banco_Predefinitions import listar_templates, salvar_template, carregar_template
    st.session_state.setdefault("dialog_criar_projeto", True)
    @st.dialog("Criar 1° Projeto ")
    def menu_principal():
        st1, st2 = st.columns([8, 1])
        #st1.subheader("Criar Novo Projeto:")
        if st2.button("X", key="Cria_Projeto"):
            st.session_state["Cria_Projeto_state"] = False
            st.rerun()

        st.write("'Henriq colocar para instalar modulos pre configurados!'")
        if "abas" not in st.session_state:
            st.session_state.abas = ["Terminal"]

        if "contador_local" not in st.session_state:
            st.session_state.contador_local = 0

        def abrir_nova_aba():
            st.session_state.contador_local += 1
            nome = f"Local {st.session_state.contador_local}"
            st.session_state.abas.append(nome)
            st.rerun()

        def fechar_aba(nome):
            if nome != "Terminal":
                st.session_state.abas.remove(nome)
                st.rerun()

        # =========================
        # DADOS DO PROJETO
        caminho_base = st.text_input("**Criar em:**", Path(ler_A_CONT_ABS_unico()[0][1]).resolve())
        nome_projeto = st.text_input("Nome do projeto")
        # =========================
        # ARQUIVOS INICIAIS
        with st.expander("📁 Arquivos iniciais do projeto", expanded=False):

            if "arquivos_projeto" not in st.session_state:
                st.session_state.arquivos_projeto = [
                    {
                        "nome": "main.py",
                        "conteudo": "# Arquivo principal\n\nif __name__ == '__main__':\n    print('Projeto iniciado')\n"
                    }
                ]

            templates = listar_templates()
            template_sel = st.selectbox(
                "Template salvo",
                ["(novo)"] + templates
            )

            if template_sel != "(novo)":
                st.session_state.arquivos_projeto = carregar_template(template_sel)

            for i, arq in enumerate(st.session_state.arquivos_projeto):
                st.markdown(f"**Arquivo {i + 1}**")
                col1, col2 = st.columns([4, 1])

                arq["nome"] = col1.text_input(
                    "Nome do arquivo",
                    arq["nome"],
                    key=f"nome_arq_{i}"
                )

                if col2.button("🗑", key=f"del_arq_{i}"):
                    st.session_state.arquivos_projeto.pop(i)
                    st.rerun()

                arq["conteudo"] = st.text_area(
                    "Conteúdo",
                    arq["conteudo"],
                    height=150,
                    key=f"cont_arq_{i}"
                )

            if st.button("➕ Adicionar arquivo"):
                st.session_state.arquivos_projeto.append(
                    {"nome": "", "conteudo": ""}
                )
                st.rerun()

            nome_template = st.text_input("Salvar como template")
            if st.button("💾 Salvar template"):
                if nome_template.strip() and template_sel != '':
                    salvar_template(str(nome_template).title(), st.session_state.arquivos_projeto)
                    st.success("Template salvo com sucesso!")
                else:
                    st.warning('Dê um nome ao template?')

        st.divider()

        # =========================
        # CRIAÇÃO DO PROJETO
        # =========================
        pythons = listar_pythons_windows()

        if not pythons:
            st.error("Nenhum Python encontrado em AppData")
            return

        python_selecionado = st.selectbox(
            "Python base do projeto",
            list(pythons.keys()),
            index=0
        )

        if st.button("✅ Confirmar criação"):

            if not nome_projeto.strip():
                st.error("Nome do projeto inválido")
                return

            projeto_path = Path(caminho_base) / nome_projeto.replace(" ", "_")
            venv_path = projeto_path / ".virto_stream"
            python_base = pythons[python_selecionado]
            esc_A_CONTROLE_PROJETOS(Path(caminho_base) / nome_projeto.replace(" ", "_"), python_selecionado,
                                    data_sistema(),
                                    0, 0, 'Criado Com TcbT!')

            progresso = st.progress(0)
            log_area = st.empty()

            logs = []

            def log(msg, pct=None):
                logs.append(msg)
                log_area.code("\n".join(logs), language="bash")
                if pct is not None:
                    progresso.progress(pct)

            try:
                # 1️⃣ Criar pasta do projeto
                log("📁 Criando pasta do projeto...", 5)
                projeto_path.mkdir(parents=True, exist_ok=False)

                # 2️⃣ Criar ambiente virtual
                log("🐍 Criando ambiente virtual...", 25)
                CREATE_NO_WINDOW = 0x08000000

                subprocess.run(
                    [python_base, "-m", "venv", str(venv_path)],
                    check=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_NO_WINDOW)

                python_venv = (
                    venv_path / "Scripts" / "python.exe"
                    if sys.platform == "win32"
                    else venv_path / "bin" / "python"
                )

                # 3️⃣ Atualizar pip
                log("⬆️ Atualizando pip...", 50)
                subprocess.run(
                    [str(python_venv), "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    startupinfo=STARTUPINFO,
                    creationflags=CREATE_NO_WINDOW)

                # 4️⃣ Criar arquivos do usuário
                log("📝 Criando arquivos do projeto...", 75)
                for arq in st.session_state.arquivos_projeto:
                    if arq["nome"].strip():
                        caminho = projeto_path / arq["nome"]
                        caminho.parent.mkdir(parents=True, exist_ok=True)
                        caminho.write_text(arq["conteudo"], encoding="utf-8")
                        log(f"   ✔ {arq['nome']}")

                # 5️⃣ Finalização
                log("✅ Projeto criado com sucesso!", 100)
                st.success(f"🎉 Projeto criado com sucesso usando {python_selecionado}")

                st.session_state.dialog_criar_projeto = False
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
            except FileExistsError:
                log("❌ Erro: o projeto já existe")
                st.error("O projeto já existe")

            except subprocess.CalledProcessError as e:
                log("❌ Erro ao criar ambiente virtual ou instalar dependências")
                st.exception(e)

            except Exception as e:
                log("❌ Erro inesperado")
            st.exception(e)
    if st.session_state.dialog_criar_projeto:
        menu_principal()






def Apagar_Arq(st,nome,diretorio):
    @st.dialog(f"Apagar {nome}")
    def menu_principal():
        st1, st2 = st.columns([9,1])
        st1.text(f"🗑️ Tem certeza de que deseja apagar?")
        st1.code(f"{diretorio}")
        if st2.button("x", key="fechar_painel", ):
            st.session_state["botao_apagar_arquivos_state"] = False
            st.rerun()

        if st.button(f"**❌ Apagar Sim!**", key=f"{nome}_btn_del2", width='stretch',type="secondary"):
            Apagar_Arquivos(st, diretorio)
            st.session_state.Apagar_Arquivos = False

            sleep(1.5)
            st.session_state["botao_apagar_arquivos_state"] = False
            st.rerun()
    menu_principal()