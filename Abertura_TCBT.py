# PAGINA_INICIAL.py - Configuração CORRIGIDA com ProjetoSTR do LADO
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
					st.rerun()  # ⬅ FECHA O DIALOG

	# 🔐 Só abre o dialog se estiver marcado
	if st.session_state.dialog_aberto:
		menu_principal()

	return st.session_state.caminho_selecionado


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
    ## **Fundador da TopCode by Trap**  
    Desenvolvedor de Software e criador da **Stream-IDE**.
    Editor de Codigos, Preview Run, Terminal, 
    APIs integradas.
    """


def texto_reconhencimento():
	"""Texto pessoal do Henrique"""
	return """
    ## **Reconchecimentos**  
     **Desenvolvedores e Modulos**.

    #----------------- Author: **ohtaman**\n
    streamlit-desktop-app:
    https://github.com/ohtaman/streamlit-desktop-app
\n\n
    #----------------- Author: **okld**\n
    streamlit_ace:
    https://share.streamlit.io/okld/streamlit-gallery/main?p=ace-editor
    """


def Abertura():
	# LAYOUT EM DUAS COLUNAS
	col_vazia, col_esquerda, col_direita, col_vazia2 = st.columns([1, 3, 2, 1])

	with col_esquerda:
		st.markdown('<h1 class="main-title">🛡️ Stream-IDE - Configuração Absoluta { v0.0.1 }</h1>',
		            unsafe_allow_html=True, text_alignment='center')

		st.markdown('<div class="config-section">', unsafe_allow_html=True)

		# ✅ PASSO 1: CONTROLE ABSOLUTO
		config_absoluta_ok = verificar_config_absoluta()

		if config_absoluta_ok:
			st.success("✅ **Sistema já configurado e pronto!**")
			st.balloons()



		else:
			with st.container(border=True):
				st.info("👇 Configure os diretórios principais do sistema")

				# AUTO-DETECT PROGRAMA
				diretorio_programa = Path(__file__).parent.absolute()
				nome_pasta_programa = Path(__file__).parent.parent.name
				caminho_do_programa = Path(diretorio_programa).parent
				caminho_Anterior_programa = Path(caminho_do_programa).parent
				st.markdown('<h3 style="color: #00d4ff;"><strong>1. Diretório do Programa</strong><br>(AUTO-DETECTADO)</h3>', unsafe_allow_html=True,text_alignment='center')
				st.markdown(f"""
                <div class="path-section">
                    <strong>✅ INSTALAÇÃO:</strong> {diretorio_programa}<br>
                    <strong>📂 Caminho da pasta:</strong> {caminho_do_programa} <br><br>
                    <small>🔒 *Pasta onde a IDE está instalada. Arquivos de imagem, banco de dados e configurações ficam aqui.<br>
                     PARA ALTERAR TROQUE A PASTA DE LUGAR MANUALMENTE!*</small>
                </div>
                """, unsafe_allow_html=True)

			# ✅ PROJETOSTR NO MESMO NÍVEL (DO LADO)
			ProjetoSteamIDE = f"\\ProjetoSteamIDE"
			diretorio_projetos_auto = rf"{caminho_Anterior_programa}{ProjetoSteamIDE}"

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

			# Backup DENTRO da pasta Projetos
			diretorio_backup_auto = f"{diretorio_projetos_auto}\\BackupSTR"
			col1, col2 = st.columns([6, 1])

			with col2:
				camiho = ''
				if st.pills(f'2', ":material/folder_shared:", label_visibility='collapsed'):
					camiho = Janela_Lista_Arquivos(st, 'pastas', nome_pasta_programa)
			with col1:
				diretorio_backup = st.text_input(
					"{ 💾 **3. _Diretório Para Futuros Backup_** }",
					value=diretorio_backup_auto if camiho == '' else camiho,
					placeholder="Ex: C:/Projetos_IDE_TOPcode/BackupSTR"
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
						str(diretorio_programa),
						str(diretorio_projetos_input), # problema se usuario abrir a janela e nao escolher nada, vem none
						str(diretorio_backup),
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

						'#1a1a1a',
						'#024a4e',
						'Silkscreen',
						12,
						'#e9e9ff',

						'Pixelify Sans',
						15,
						'#01848c',

						1,
						3,

						'',

						'#333333',
						'',
						0,

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
		st.markdown('<h3 style="color: #00ffea;">👨‍💻 HENRIQUE LIANDRO</h3>', unsafe_allow_html=True)
		st.markdown(texto_sobre(), unsafe_allow_html=False, text_alignment='center')
		st.markdown(texto_reconhencimento(), unsafe_allow_html=False)

		st.markdown('</div>', unsafe_allow_html=True)
		# =========================
		# 🎮 ESTILO GAMER RETRÔ (8-bit / 16-bit)
		# NÃO ALTERA NADA DA LÓGICA DA PÁGINA
		# =========================

		st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

        /* Fonte base */
        html, body, [class*="css"] {
            font-family: 'VT323', monospace !important;
            letter-spacing: 0.5px;
        }

        /* Títulos principais */
        .main-title, h1, h2, h3 {
            font-family: 'Press Start 2P', monospace !important;
            font-size: 20px !important;

        }

        /* Containers */
        .config-section, .sobre-section {
            background: linear-gradient(145deg, #0a0f2c, #050816);
            border: 2px solid #00d4ff;
            border-radius: 8px;
            box-shadow: 0 0 0 2px #000, 0 0 20px rgba(0,212,255,0.3);
        }

        /* Inputs */
        input, textarea {
            background-color: #050816 !important;
            color: #00ffea !important;
            border: 2px solid #0022ff !important;
            font-family: 'VT323', monospace !important;
            font-size: 18px !important;
        }

        /* Botões */
        button {
            font-family: 'Press Start 2P', monospace !important;
            font-size: 10px !important;
            background: #0022ff !important;
            color: #ffffff !important;
            border: 2px solid #00d4ff !important;
            box-shadow: 3px 3px 0 #000;
        }

        button:hover {
            background: #00d4ff !important;
            color: #000 !important;
        }

        /* Texto auxiliar */
        small, label, p {
            font-family: 'VT323', monospace !important;
            font-size: 16px !important;
        }
        </style>
        """, unsafe_allow_html=True)


