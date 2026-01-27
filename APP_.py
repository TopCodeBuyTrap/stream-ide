
# Adicione este bloco NO INÍCIO do seu arquivo APP_.py e outros arquivos principais
# Isso corrige o erro "ModuleNotFoundError" quando roda o executável

import sys
import os
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
    if st.button(f'Acesar',use_container_width=True):
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
            st.image('.arquivos/simbolo.png')
        Cria_Projeto_pouppap(st)

    else:



        with st.container(border=True, key='MenuTopo'):
            Top1,Top2 ,Top3 ,Top4,Top5,Top6,Top7,Top8= st.columns([.4,.4,.4,.4,2,1.4,1,.4])

        with Top8:
            from APP_Atualizador import checar_atualizacao
            if Button_Nao_Fecha(f'🔃 :material/queue_play_next: {ultima_versao()}',f'🔂 :material/queue_play_next: {ultima_versao()}','Atualizar_versão'):
                checar_atualizacao()

        with Top6:
            Ttp1,Ttp2 = st.columns(2) # Botão de run e stop

        with Top3:
            Trm1,Trm2 = st.columns([2,8])
            Trm1.write(':material/terminal:')

        with Top4:
            Prw1, Prw2 = st.columns([2, 8])
            Prw1.write(':material/directions_bike:')

        from APP_Menus import Abrir_Menu
        #Abrir_Menu(st)
        # ============================================================= MENU SUPERIOR
        if Top2.button(":material/delete_sweep:",icon='♻️',help='limpar os caches do app'.title()):
            limpar_CASH()
        st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

        #--------------------------------------------------------------------- MENUS DE EDIÇÃO E CRIAÇÃO DE ARQUIVOS
        from  APP_Menus import  Abrir_Menu,Custom
        Pasta_Executavel = _DIRETORIO_EXECUTAVEL_()
        Pasta_Todos_Projetos = _DIRETORIO_PROJETOS_()
        Pasta_Projeto_Atual = caminho
        Meus_Arquivos = listar_arquivos_e_pastas(Pasta_Projeto_Atual)

        # Exemplo de uso
        with Top1:
            btnt = Button_Nao_Fecha(':material/folder_open:'+":material/keyboard_double_arrow_left:",
            ':material/folder:' + ':material/keyboard_double_arrow_right:', key="botao_diretorio")
        if btnt:
            col1, col2 = st.columns([1.2, 7])
            vl = 400
            with col1.container(border=True, width=vl,key='menu_lado_sidebar',height=800):
                # :material/settings:  :material/emoji_symbols:
                Abrir_Menu(st)

                select_arquivo_recente(st)

                if NOME_CUSTOM != 'Padrão':
                    btcst = Button_Nao_Fecha(f'**{NOME_CUSTOM}** - :material/build:' + ":material/keyboard_double_arrow_up:",
                                            f"**{NOME_CUSTOM}** - :material/build:" + ':material/keyboard_double_arrow_down:',
                                            key="bBotao_recustomizar")
                    if btcst:
                        Customization(st,NOME_CUSTOM)
        else:
            col1, col2 = st.columns([.2, 9])
        #------------------z--------------------------------------------------- SIDIBAR LATERAL
        with st.sidebar:
            s1,s2,s3 = st.sidebar.columns(3)
            s2.image(IMAGEM_LOGO)

            caminho_completo = Pasta_Projeto_Atual  # Ex: "C:\\Users\\henri\\PycharmProjects\\IDE_TOP"
            unidade = os.path.splitdrive(caminho_completo)[0]  # Ex: "C:"
            nome_pasta = os.path.basename(caminho_completo)
            Arq_Selec_Nomes, Arq_Selec_Diretorios = Sidebar_Diretorios(st, Meus_Arquivos, 7)

        if Top7.button(f':material/search: {os.path.join(nome_pasta)} :material/folder_open:',use_container_width=True, type="secondary"):
            Open_Explorer(Pasta_Projeto_Atual)


        if len(Arq_Selec_Diretorios) > 0:
            from APP_Editor_Run_Preview import Editor_Simples

            try:
                with col2:
                    arquivos_abertos_nomes, arquivos_abertos_caminhos, arquivo_selecionado_nome, arquivo_selecionado_caminho,arquivo_selecionado_conteudo\
                    = Editor_Simples(col1,Prw2,Top5,Arq_Selec_Diretorios,THEMA_EDITOR, EDITOR_TAM_MENU,Ttp2,Ttp1,)
            except UnicodeDecodeError:
                st.warning('Arquivo não Reconhecido GmeOver!')



            Tab1, Tab2 = st.columns([.4, 9])
            val = ''
            with Tab2.container(border=True, key='Terminal_cmd', width=900):
                with Trm2:
                    altura_term = st.slider( ':material/terminal:', value=300, min_value=200, max_value=800, step=300,label_visibility='collapsed')
                with st.expander(f":material/terminal: Terminal: {val}"):
                    Terminal(altura_term,THEMA_TERMINAL, TERMINAL_TAM_MENU)

            # --------------------------------------------------------------------- BUSCAR ARQUIVO SELECIONADO
            if arquivo_selecionado_caminho and os.path.isfile(arquivo_selecionado_caminho):
                caminho = Path(arquivo_selecionado_caminho)
                nome_sem_extensao = caminho.stem
                extensao_arquivo = caminho.suffix
                nome_arquivo = caminho.name

                # Se for imagem, mostra no container
                if extensao_arquivo.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'):
                    footer_container = Tab2.container(border=True, key="meu_container_unico")
                    with footer_container:
                        st.image(caminho, caption=f"🖼️ {caminho.name}")

        else:
            with col2:
                st.image('.arquivos/simbolo.png',caption='By TopCodeBuyTrap')
#---------------------------
if __name__ == "__main__":
    try:
        import streamlit as st
        from datetime import datetime

        from APP_SUB_Customizar import Customization
        from APP_SUB_Funcitons import Identificar_linguagem, escreve, chec_se_arq_do_projeto, contar_estrutura, \
            Button_Nao_Fecha, data_sistema, resumo_pasta, limpar_CASH, Linha_Sep
        from APP_SUB_Janela_Explorer import listar_arquivos_e_pastas, Open_Explorer, Abrir_Arquivo_Select_Tabs
        from APP_Sidebar import Sidebar_Diretorios
        from Banco_dados import ler_A_CONTROLE_PROJETOS, ler_B_ARQUIVOS_RECENTES, ATUAL_B_ARQUIVOS_RECENTES, \
            se_B_ARQUIVOS_RECENTES, esc_B_ARQUIVOS_RECENTES, Del_B_ARQUIVOS_RECENTES, ler_A_CONTROLE_ABSOLUTO, \
            Del_A_CONTROLE_ABSOLUTO, Del_CUSTOMIZATION, esc_A_CONTROLE_PROJETOS
        from APP_SUB_Controle_Driretorios import _DIRETORIO_EXECUTAVEL_, _DIRETORIO_PROJETOS_, _DIRETORIO_PROJETO_ATUAL_

        import os
        from pathlib import Path
        from APP_Terminal import Terminal
        st.set_page_config(page_title="Stream-IDE", layout="wide",page_icon='icon.ico')

        if 'config_absoluta_ok' not in st.session_state:
            st.session_state.config_absoluta_ok = False

        # 🔹 SE JÁ TEM CONFIG → ENTRA DIRETO NA IDE
        if len(ler_A_CONTROLE_ABSOLUTO()) > 0 or st.session_state.config_absoluta_ok:
            from APP_Htmls import Carregamento_BancoDados_Temas
            (IMAGEM_LOGO, NOME_CUSTOM, NOME_USUARIO, COR_CAMPO, COR_MENU, THEMA_EDITOR, EDITOR_TAM_MENU,THEMA_PREVIEW,PREVIEW_TAM_MENU,
             THEMA_TERMINAL,TERMINAL_TAM_MENU,TOP_CAB,FONTE_MENU,FONTE_CAMPO) = Carregamento_BancoDados_Temas(st)

            app( )

        # 🔹 SENÃO → MOSTRA ABERTURA
        else:
            from Abertura_TCBT import Abertura
            Del_CUSTOMIZATION()

            if Abertura() == True:
                st.rerun()
    except Exception as e:
        st.error(f"🚨 ERRO: {e}")
        st.warning("🔄 **FECHE e REABRA o programa**")

