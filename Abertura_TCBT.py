# PAGINA_INICIAL.py - Configuração CORRIGIDA com Projetos_TcbT do LADO
import streamlit as st
import os
from pathlib import Path

from APP_SUB_Janela_Explorer import Janela_PESQUIZA_PASTAS_ARQUIVOS
from Banco_dados import esc_A_CONTROLE_ABSOLUTO, ler_A_CONTROLE_ABSOLUTO, esc_CUSTOMIZATION


def Janela_Lista_Arquivos(st, listar_tipo, caminho_inicial):

    st.session_state.setdefault("caminho_selecionado", None)
    st.session_state.setdefault("dialog_aberto", True)

    @st.dialog("Controle Absoluto:")
    def menu_principal():
        RESULTADO = Janela_PESQUIZA_PASTAS_ARQUIVOS(st, listar_tipo, caminho_inicial)

        if RESULTADO and RESULTADO[0]:
            caminho, tipo = RESULTADO
            nome_arq = os.path.basename(caminho)

            if tipo == '📁 DIRETÓRIO':
                if st.button(
                    f"📁 **Usar este diretório: {nome_arq}**",
                    use_container_width=True
                ):
                    st.session_state.caminho_selecionado = caminho
                    st.session_state.dialog_aberto = False
                    st.rerun()   # ⬅ FECHA O DIALOG

    # 🔐 Só abre o dialog se estiver marcado
    if st.session_state.dialog_aberto:
        menu_principal()

    return st.session_state.caminho_selecionado





def get_diretorio_programa():
    """Pega automaticamente a pasta onde o programa está instalado"""
    return str(Path(__file__).parent.absolute())


def get_nome_pasta_programa():
    """Pega o NOME da pasta atual (sem caminho)"""
    return Path(__file__).parent.name


def verificar_config_absoluta():
    """Verifica se A_CONTROLE_ABSOLUTO já foi configurado"""
    try:
        dados = ler_A_CONTROLE_ABSOLUTO()
        return dados is not None and len(dados) > 0
    except:
        return False


def texto_sobre():
    """Texto pessoal do Henrique"""
    return """
    ## 👨‍💻 **Henrique Leandro**

    **Fundador da TopCode by Trap**  
    Desenvolvedor de Software e criador da **IDE TOP code**.

    **SDE que funciona** - Monaco, Terminal, APIs integradas.
    """


def Abertura():

    # TÍTULO PRINCIPAL
    st.markdown('<h1 class="main-title">🚀 IDE TOP code - Configuração Absoluta { v0.0.1 }</h1>', unsafe_allow_html=True)

    # LAYOUT EM DUAS COLUNAS
    col_vazia, col_esquerda, col_direita,col_vazia2 = st.columns([1,2, 1,1])

    with col_esquerda:
        st.markdown('<div class="config-section">', unsafe_allow_html=True)

        # ✅ PASSO 1: CONTROLE ABSOLUTO
        st.markdown("## 🛡️ **CONTROLE ABSOLUTO DO SISTEMA**")

        config_absoluta_ok = verificar_config_absoluta()

        if config_absoluta_ok:
            st.success("✅ **Sistema já configurado e pronto!**")
            st.balloons()



        else:
            with st.container(border=True):
                st.warning("⚠️ **CONFIGURAÇÃO INICIAL OBRIGATÓRIA**")
                st.info("👇 Configure os diretórios principais do sistema")

                # AUTO-DETECT PROGRAMA
                diretorio_programa = get_diretorio_programa()
                nome_pasta_programa = get_nome_pasta_programa()

                st.markdown("### 📁 **1. Diretório do Programa** *(AUTO-DETECTADO)*")
                st.markdown(f"""
                <div class="path-section">
                    <strong>✅ INSTALAÇÃO:</strong> `{diretorio_programa}`<br>
                    <strong>📂 Nome da pasta:</strong> `{nome_pasta_programa}`<br><br>
                    <small>🔒 *Pasta onde a IDE está instalada. Arquivos de imagem, banco de dados e configurações ficam aqui.<br>
                     PARA ALTERAR TROQUE A PASTA DE LUGAR MANUALMENTE!*</small>
                </div>
                """, unsafe_allow_html=True)

            # ✅ PROJETOS_TcbT NO MESMO NÍVEL (DO LADO)
            diretorio_projetos_auto = str(Path(__file__).parent.parent / f"Projetos_{nome_pasta_programa}")

            col1, col2 = st.columns([6, 1])
            with col2:
                camiho1 = ''
                if st.pills(f'1', ":material/folder_shared:", label_visibility='collapsed'):
                    camiho1 = Janela_Lista_Arquivos(st, 'pastas', diretorio_projetos_auto)
            with col1:
                diretorio_projetos_input = st.text_input(
                    "{ 📂 **2. Diretório Para Futuros Projetos** }",
                    value=diretorio_projetos_auto if camiho1 == '' else camiho1,
                    placeholder="Ex: C:/Users/Henrique/Projetos_IDE_TOPcode",
                    help="💡 AUTO: Projetos_[NOME_DA_PASTA] no MESMO nível da pasta do programa")


            st.markdown("### 🗂️ **3. Diretórios dentro de Projetos_TcbT**")

            # Backup DENTRO da pasta Projetos
            diretorio_backup_auto = f"{diretorio_projetos_auto}/Backups_TcbT"
            col1, col2 = st.columns([6, 1])

            with col2:
                camiho = ''
                if st.pills(f'2', ":material/folder_shared:", label_visibility='collapsed'):
                    camiho = Janela_Lista_Arquivos(st, 'pastas', nome_pasta_programa)
            with col1:
                diretorio_backup = st.text_input(
                "{ 💾 **_Diretório Para Futuros Backup_** }",
                value=diretorio_backup_auto if camiho == '' else camiho,
                placeholder="Ex: C:/Projetos_IDE_TOPcode/Backups_TcbT"
            )

            diretorio_ollama = st.text_input(
                "🤖 Diretório Ollama",
                placeholder="Ex: C:/Ollama"
            )

            versao_ollama = st.text_input(
                "📊 Versão Ollama",
                placeholder="Ex: llama3.2"
            )

            st.markdown("### 🔑 **4. Credenciais GPT** *(Opcional)*")
            col_gpt1, col_gpt2 = st.columns(2)
            with col_gpt1:
                login_gpt = st.text_input("👤 Login GPT", placeholder="seu@email.com")
            with col_gpt2:
                chave_gpt = st.text_input("🔑 Chave GPT", type="password", placeholder="sk-...")

            if st.button("💾 **SALVAR CONFIGURAÇÃO ABSOLUTA**", type="primary", use_container_width=True):
                try:
                    Path(diretorio_backup).mkdir(parents=True, exist_ok=True)

                    esc_A_CONTROLE_ABSOLUTO(
                        diretorio_programa,
                        diretorio_projetos_input,
                        diretorio_backup,
                        diretorio_ollama or "",
                        versao_ollama or "",
                        chave_gpt or "",
                        login_gpt or ""
                    )
                    default_download = os.path.join(os.path.expanduser("~"), "Downloads")
                    esc_CUSTOMIZATION(
                        'Padrão',
                        'HenriqLs',
                        default_download,
                        r'.arquivos\logo_.png',

                        'dracula',
                        15,

                        "chaos",
                        14,

                        "terminal",
                        13,

                        '#04061a',
                        '#24283b',
                        'JetBrains Mono',
                        13,
                        '#0022ff',

                        'Fira Code',
                        13,
                        '#A86E04',

                        0,
                        3,

                        '',

                        '',
                        '',
                        '',

                        'ATIVO')

                    st.success("✅ **CONFIGURAÇÃO ABSOLUTA SALVA!** 🎉")
                    st.balloons()

                    # 🔥 CONTROLE DE FLUXO REAL
                    st.session_state.config_absoluta_ok = True
                    return st.session_state.config_absoluta_ok

                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # COLUNA DIREITA - SOBRE
    with col_direita:
        st.markdown('<div class="sobre-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #00d4ff;">👨‍💻 HENRIQUE LEANDRO</h3>', unsafe_allow_html=True)
        st.markdown(texto_sobre(), unsafe_allow_html=False)
        st.markdown('</div>', unsafe_allow_html=True)

