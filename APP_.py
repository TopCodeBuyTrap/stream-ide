
# Adicionei este bloco NO INÍCIO do seu arquivo APP_.py e outros arquivos principais
# Isso corrige o erro "ModuleNotFoundError" quando roda o executável

import sys
from pathlib import Path

# Detecta se está rodando como executável (frozen) ou script python normal
if getattr(sys, 'frozen', False):
    # Se for executável, a pasta raiz é onde está o .exe
    app_root = Path(sys.executable).parent.absolute()

    # Adiciona a pasta _internal ao caminho de busca do Python
    sys.path.append(str(app_root / "_internal"))
    sys.path.append(str(app_root))
else:
    # Se for script normal
    app_root = Path(__file__).parent.absolute()
    sys.path.append(str(app_root))


#-----------------------------------------------------------------------------------

def select_arquivo_recente(col2):


    registros = ler_A_CONTROLE_PROJETOS()
    if not registros:
        return None, None, None

    # registros =
    # (DIRETORIO_TRABALHANDO, VERSION, DATA, DIRETORIOS, ARQUIVOS, OBS)
    ordenar_por = st.selectbox(
        "Ordenar por:",
        ["Último usado", "Data", "Versão", "Ordem alfabética (agrupado)"],
        key="ordenacao_recente",label_visibility='collapsed'
    )

    dados = []
    for r in registros:
        caminho, versao, data = r[0], r[1], r[2]
        dados.append({
            "caminho": caminho,
            "nome": os.path.basename(caminho),
            "versao": versao,
            "data": data
        })

    if ordenar_por == "Último usado":
        dados = sorted(
            dados,
            key=lambda x: x["data"] or "",
            reverse=True
        )

    elif ordenar_por == "Data":
        dados = sorted(
            dados,
            key=lambda x: datetime.fromisoformat(x["data"]) if x["data"] else datetime.min,
            reverse=True
        )

    elif ordenar_por == "Versão":
        dados = sorted(
            dados,
            key=lambda x: (x["versao"] or "").lower()
        )

    elif ordenar_por == "Ordem alfabética (agrupado)":
        grupos = {}
        for d in dados:
            grupos.setdefault(d["nome"], []).append(d)

        dados = []
        for nome in sorted(grupos.keys(), key=str.lower):
            grupo = sorted(
                grupos[nome],
                key=lambda x: datetime.fromisoformat(x["data"]) if x["data"] else datetime.min
            )
            dados.extend(grupo)

    if "projeto_idx" not in st.session_state:
        st.session_state.projeto_idx = 0
        st.toast("seleção inicial definida".title())

    selecionado = st.selectbox(
        "Projetos recentes",
        options=range(len(dados)),
        format_func=lambda i: dados[i]["nome"],
        key="projeto_idx",label_visibility='collapsed'
    )

    if "ultimo_idx" not in st.session_state:
        st.session_state.ultimo_idx = selecionado

    if selecionado != st.session_state.ultimo_idx:
        st.toast("projeto trocado".title())
        st.session_state.ultimo_idx = selecionado

    item = dados[selecionado]
    if st.button(f'Acesar',width='stretch'):
        data = contar_estrutura(item["caminho"])
        versao_set = data["versoes"][0]
        esc_A_CONTROLE_PROJETOS(str(item["caminho"]), list(versao_set)[0], data_sistema(), data["pastas"], data["arquivos"] , '')


def app():
    from Banco_Predefinitions import ultima_versao

    # =====================================================
    # COLOQUE ISSO NO **INÍCIO** do seu app(), ANTES de tudo:

    # =====================================================

    global arquivo_selecionado_caminho, arquivo_selecionado_nome, arquivo_selecionado_conteudo
    try:
        pjt = ler_A_CONTROLE_PROJETOS()[-1]
        caminho = pjt[0]
        versao = pjt[1]
        data = pjt[2]

        if se_B_ARQUIVOS_RECENTES(caminho) == False:
            Del_B_ARQUIVOS_RECENTES()
            esc_B_ARQUIVOS_RECENTES(Path(caminho), str(contar_estrutura(caminho)))
    except IndexError: pass

    if len(ler_B_ARQUIVOS_RECENTES()) == 0:
        st.button('Entar')
        from APP_Menus import Cria_Projeto_pouppap
        footer_container = st.container(border=True)
        with footer_container:
            st.write('Seja Bem Vindo Ordinario/a !')

            carregar_imagem_segura('.arquivos/simbolo.png')
        Cria_Projeto_pouppap(st)

    else:
        with st.container(border=True, key='MenuTopo'):
            cab1, cab2 , cab3 , cab4 = st.columns([8, 1,1,.3])
            cab1.markdown(TOP_CAB,unsafe_allow_html=True, width ='stretch')
            with cab3:pass

            with cab4:
                st.button("♻️",  help='limpar os caches do app'.title(),on_click=limpar_CASH)

        Tab1, Tab2 = st.columns([2, 9])

        #btnt = Button_Nao_Fecha(':material/folder_open:' + ":material/keyboard_double_arrow_left:", ':material/folder:' + ':material/keyboard_double_arrow_right:',
                                        #key="botao_diretorio")



        from APP_Menus import Abrir_Menu
        #Abrir_Menu(st)
        # ============================================================= MENU SUPERIOR

        #st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

        #--------------------------------------------------------------------- MENUS DE EDIÇÃO E CRIAÇÃO DE ARQUIVOS
        from  APP_Menus import  Abrir_Menu,Custom
        Pasta_Executavel = _DIRETORIO_EXECUTAVEL_()
        Pasta_Todos_Projetos = _DIRETORIO_PROJETOS_()
        Pasta_Projeto_Atual = caminho
        Meus_Arquivos = listar_arquivos_e_pastas(Pasta_Projeto_Atual)



        Janela = Tab1.container(border=True,key='menu_lado_sidebar',height=1000)
        with Janela:
            _ = st.session_state
            # :material/settings:  :material/emoji_symbols:
            Tt1, Tt2 = st.columns([1,9])  # Botão de run e stop
            Ttp1, Ttp2 = st.columns(2)  # Botão de run e stop
            Arq_Selec_Nomes, Arq_Selec_Diretorios = Sidebar_Diretorios(st, Meus_Arquivos, 7)


        #------------------z--------------------------------------------------- SIDIBAR LATERAL
        with st.sidebar:
            s1,s2,s3 = st.sidebar.columns(3)
            if Button_Nao_Fecha(f':material/queue_play_next: versão: {ultima_versao()}',
                                f':material/queue_play_next: versão: {ultima_versao()}', 'Atualizar_versão'):
                from APP_Atualizador import checar_atualizacao
                checar_atualizacao()
            #s2.image('.arquivos/logo_.png',caption='By TopCodeBuyTrap')
            Abrir_Menu(st)

            select_arquivo_recente(st)
            caminho_pai = Pasta_Projeto_Atual  # Ex: "C:\\Users\\henri\\PycharmProjects\\IDE_TOP"
            unidade = os.path.splitdrive(caminho_pai)[0]  # Ex: "C:"
            nome_pasta = os.path.basename(caminho_pai)
            caminho_completo = os.path.join(caminho_pai,nome_pasta)
            from APP_SUB_Backup import BAKCUP
            if NOME_CUSTOM != 'Padrão':
                btcst = Button_Nao_Fecha(
                    f'**{NOME_CUSTOM}** - :material/build:' + ":material/keyboard_double_arrow_up:",
                    f"**{NOME_CUSTOM}** - :material/build:" + ':material/keyboard_double_arrow_down:',
                    key="bBotao_recustomizar")
                if btcst:
                    Customization(st, NOME_CUSTOM)
            catalogo = Button_Nao_Fecha("📚 Arquivos Catalogados", "📚 Arquivos Catalogados", 'catalogo')
            if catalogo:
                caminho_pai = Pasta_Projeto_Atual  # Ex: "C:\\Users\\henri\\PycharmProjects\\IDE_TOP"
                nome_pasta = os.path.basename(caminho_pai)
                caminho_pai = Pasta_Projeto_Atual  # Ex: "C:\\Users\\henri\\PycharmProjects\\IDE_TOP"
                caminho_completo = os.path.join(caminho_pai, nome_pasta)

                conf_baix_catalogo(st, caminho_pai, nome_pasta)
            ignores = ['.idea', '.venv', 'build', 'dist','.virto_stream','.gitignore']
            MINUTOS_ATUALIZAR = 60
            BAKCUP(st,MINUTOS_ATUALIZAR, Path(caminho_completo).parent, os.path.join(_DIRETORIO_EXECUTAVEL_('backup'),nome_pasta), ignores)


        if Janela.button(f':material/search: {os.path.join(nome_pasta)} :material/folder_open: ',
                               width='stretch', type="secondary"):
                    Open_Explorer(caminho_completo)


        if len(Arq_Selec_Diretorios) > 0:
            from APP_Editor_Run_Preview import Editor_Simples

            try:
                with Tab2:
                    arquivos_abertos_nomes, arquivos_abertos_caminhos, arquivo_selecionado_nome, arquivo_selecionado_caminho,arquivo_selecionado_conteudo\
                    = Editor_Simples(Janela,Tt2,Arq_Selec_Diretorios,THEMA_EDITOR, EDITOR_TAM_MENU,FONTE_CAMPO,Ttp2,Ttp1,FUNDO_EDTOR)
            except UnicodeDecodeError:
                st.warning('Arquivo não Reconhecido GmeOver!')



        val = ''
        with Tab2.container(border=True, key='Terminal_cmd', width=900):
            if Button_Nao_Fecha(':material/terminal: Terminal:', ':material/terminal: Terminal:', 'BtnTerminal'):
                from APP_Terminal import Terminal
                Terminal()


#---------------------------
if __name__ == "__main__":
    #try:
    import streamlit as st
    from datetime import datetime
    from APP_Catalogo import conf_baix_catalogo
    from APP_SUB_Customizar import Customization
    from APP_SUB_Funcitons import Identificar_linguagem, escreve, chec_se_arq_do_projeto, contar_estrutura, \
    Button_Nao_Fecha, data_sistema, resumo_pasta, limpar_CASH, Linha_Sep, carregar_imagem_segura
    from APP_SUB_Janela_Explorer import listar_arquivos_e_pastas, Open_Explorer, Abrir_Arquivo_Select_Tabs
    from APP_Sidebar import Sidebar_Diretorios
    from Banco_dados import ler_A_CONTROLE_PROJETOS, ler_B_ARQUIVOS_RECENTES, ATUAL_B_ARQUIVOS_RECENTES, \
        se_B_ARQUIVOS_RECENTES, esc_B_ARQUIVOS_RECENTES, Del_B_ARQUIVOS_RECENTES, ler_A_CONTROLE_ABSOLUTO, \
        Del_A_CONTROLE_ABSOLUTO, Del_CUSTOMIZATION, esc_A_CONTROLE_PROJETOS
    from APP_SUB_Controle_Driretorios import _DIRETORIO_EXECUTAVEL_, _DIRETORIO_PROJETOS_, _DIRETORIO_PROJETO_ATUAL_

    import os
    from pathlib import Path
    st.set_page_config(page_title="Stream-IDE", layout="wide",page_icon='icon.ico',initial_sidebar_state='collapsed')

    if 'config_absoluta_ok' not in st.session_state:
        st.session_state.config_absoluta_ok = False

    # 🔹 SE JÁ TEM CONFIG → ENTRA DIRETO NA IDE
    if len(ler_A_CONTROLE_ABSOLUTO()) > 0 or st.session_state.config_absoluta_ok:
        from APP_Htmls import Carregamento_BancoDados_Temas
        (IMAGEM_LOGO, NOME_CUSTOM, NOME_USUARIO, COR_CAMPO, COR_MENU, THEMA_EDITOR, EDITOR_TAM_MENU,THEMA_PREVIEW,PREVIEW_TAM_MENU,
         THEMA_TERMINAL,TERMINAL_TAM_MENU,TOP_CAB,FONTE_MENU,FONTE_CAMPO,FUNDO_EDTOR) = Carregamento_BancoDados_Temas(st)

        app( )

    # 🔹 SENÃO → MOSTRA ABERTURA
    else:
        from Abertura_TCBT import Abertura
        Del_CUSTOMIZATION()

        if Abertura() == True:
                st.rerun()
'''    except Exception as e:
        st.toast(f"🚨 ERRO: {e}")
        st.warning("🔄 **FECHE e REABRA o programa**")
        st.write(f"🚨{e}")'''


