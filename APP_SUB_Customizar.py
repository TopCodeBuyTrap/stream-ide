

import os

from APP_SUB_Funcitons import limpar_CASH

# Pega a pasta Downloads do usuário
default_download = os.path.join(os.path.expanduser("~"), "Downloads")

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


TEMAS_ESCUROS = [
    "ambiance",  # Escuro clássico
    "chaos",  # Escuro vibrante
    #"clouds_midnight",      # Escuro (você confirmou)
    "cobalt",  # Escuro azul
    "dracula",  # Escuro roxo popular
    "gob",  # Escuro gob
    #"gruvbox",              # Escuro Gruvbox
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


def Customization(st,NOME_CUSTOM):
	from Banco_dados import (
		ler_CUSTOMIZATION,
		ler_CUSTOMIZATION_coluna_por_usuario,
		ATUAL_CUSTOM_agora
	)


	# ---------------- USUÁRIOS EXISTENTES
	usuarios_raw = ler_CUSTOMIZATION()

	usuarios = [NOME_CUSTOM] + [row[0] for row in usuarios_raw if row[0] != "Padrão"]  # Remove Padrão
	usuarios =  usuarios  # Coloca Padrão primeiro mas NÃO mostra

	# Começa com "Padrão" selecionado (index=0)
	usuario = NOME_CUSTOM

	# ---------------- LEITURA CONFIGURAÇÕES DO USUÁRIO
	TAM_EDITOR = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'EDITOR_TAM_MENU'))
	TAM_TERM = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'TERMINAL_TAM_MENU'))
	TAM_PREV = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'PREVIEW_TAM_MENU') )
	RADIO = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'RADIAL') )
	BORDA = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'BORDA'))

	THEMA_EDITOR = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'THEMA_EDITOR')
	THEMA_PREVIEW = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'THEMA_PREVIEW')
	THEMA_TERMINAL = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'THEMA_TERMINAL')

	FONTE_MENU = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_MENU')
	FONTE_TAM_MENU = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_TAM_MENU') )
	FONTE_COR_MENU = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_COR_MENU')

	FONTE_CAMPO = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_CAMPO')
	FONTE_TAM_CAMPO = int(ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_TAM_CAMPO') )
	FONTE_COR_CAMPO = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'FONTE_COR_CAMPO')

	THEMA_APP1 = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'THEMA_APP1')
	THEMA_APP2 = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'THEMA_APP2')
	FUNDO_OUTROS = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'OPC1')
	OPC3 = ler_CUSTOMIZATION_coluna_por_usuario(usuario, 'OPC3')

	def detectar_modo_por_tema(tema):
		if tema in TEMAS_CLAROS:
			return "Claro"
		if tema in TEMAS_ESCUROS:
			return "Escuro"
		return "Escuro"  # fallback seguro

	with st.form(key=f"form_custom_{usuario}", clear_on_submit=False, border=False):
		# ---------------- ABAS ORGANIZADAS
		tab1, tab2, tab3, tab4 = st.tabs(["Size", "Fontes", "Temas", "TcbT-IDE"])

		# ---------------- TAB 1: LAYOUT
		with tab1:
			c1, c2, c3 = st.columns(3)
			Tam_Font = c1.number_input("Editor", 5, 40, TAM_EDITOR, key=f'tam_editor_{usuario}')
			Tam_Run = c2.number_input("Preview", 5, 40, TAM_PREV, key=f'tam_preview_{usuario}')
			Tam_Term = c3.number_input("Terminal", 5, 40, TAM_TERM, key=f'tam_term_{usuario}')
			c4, c5 = st.columns(2)
			Radio = c4.number_input("Raio (mx80)", 0, 80, RADIO, key=f'radial_{usuario}')
			Borda = c5.number_input("Borda (max5)", 0, 5, BORDA, key=f'borda_{usuario}')

		# ---------------- TAB 2: FONTES
		with tab2:
			fm1, fm2, fm3 = st.columns([5,2,2])
			Fonte_Menu = fm1.selectbox("Fonte Menu", FONTES_TEXTO,
			                           index=FONTES_TEXTO.index(FONTE_MENU) if FONTE_MENU in FONTES_TEXTO else 0,
			                           key=f'fonte_menu_{usuario}')
			Fonte_Tam_Menu = fm2.number_input("Tam", 6, 40, FONTE_TAM_MENU, key=f'tam_menu_{usuario}')
			Fonte_Cor_Menu = fm3.color_picker("Cor", FONTE_COR_MENU, key=f'cor_menu_{usuario}')

			fc1, fc2, fc3 = st.columns([5,2,2])
			Fonte_Campo = fc1.selectbox("Fonte Campos", FONTES_TEXTO,
			                            index=FONTES_TEXTO.index(FONTE_CAMPO) if FONTE_CAMPO in FONTES_TEXTO else 0,
			                            key=f'fonte_campo_{usuario}')
			Fonte_Tam_Campo = fc2.number_input("Tam", 6, 40, FONTE_TAM_CAMPO, key=f'tam_campo_{usuario}')
			Fonte_Cor_Campo = fc3.color_picker("Cor", FONTE_COR_CAMPO, key=f'cor_campo_{usuario}')

		# ---------------- TAB 3: TEMAS ACE
		with tab3:
			col1, col2 = st.columns(2)

			modo_inicial = detectar_modo_por_tema(THEMA_EDITOR)

			with col1:
				modo_editor = st.selectbox(
					"Modo",
					["Claro", "Escuro"],
					index=0 if modo_inicial == "Claro" else 1,
					key=f"modo_ed_{usuario}"
				)

				temas_base = TEMAS_CLAROS if modo_editor == "Claro" else TEMAS_ESCUROS
				Tema_Preview = st.selectbox(
					"Preview",
					temas_base,
					index=temas_base.index(THEMA_PREVIEW),
					key=f"tema_preview_{usuario}"
				)


			with col2:
				Tema_Editor = st.selectbox(
					"Editor",
					temas_base,
					index=temas_base.index(THEMA_EDITOR),
					key=f"tema_editor_{usuario}"
				)

				Tema_Terminal = st.selectbox(
					"Terminal",
					temas_base,
					index=temas_base.index(THEMA_TERMINAL),
					key=f"tema_terminal_{usuario}"
				)

		# ---------------- TAB 4: CORES APP
		with tab4:
			col1, col2 = st.columns(2)

			THEMA_APP1 = col1.color_picker("Menu", THEMA_APP1, key=f'app1_{usuario}')
			FUNDO_OUTROS = col2.color_picker("Widget", FUNDO_OUTROS, key=f'app3_{usuario}')
			col1, col2 = st.columns(2)

			THEMA_APP2 = col1.color_picker("Corpo", THEMA_APP2, key=f'app2_{usuario}')
			ESCURECER_IMAGEM = col2.selectbox("Opacidade", [OPC3,0,3,5,7,10,20,30,40,50,60,70,80,90],
		                               key=f'IMA_2{usuario}')


		# ---------------- BOTÃO APLICAR (final das tabs)
		if st.form_submit_button("💾 SALVAR TUDO",  use_container_width=True):
			# Layout
			ATUAL_CUSTOM_agora(st, usuario, 'EDITOR_TAM_MENU', Tam_Font)
			ATUAL_CUSTOM_agora(st, usuario, 'PREVIEW_TAM_MENU', Tam_Run)
			ATUAL_CUSTOM_agora(st, usuario, 'TERMINAL_TAM_MENU', Tam_Term)
			ATUAL_CUSTOM_agora(st, usuario, 'RADIAL', Radio)
			ATUAL_CUSTOM_agora(st, usuario, 'BORDA', Borda)

			# Fontes Menu
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_MENU', Fonte_Menu)
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_TAM_MENU', Fonte_Tam_Menu)
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_COR_MENU', Fonte_Cor_Menu)

			# Fontes Campo
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_CAMPO', Fonte_Campo)
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_TAM_CAMPO', Fonte_Tam_Campo)
			ATUAL_CUSTOM_agora(st, usuario, 'FONTE_COR_CAMPO', Fonte_Cor_Campo)

			# Temas
			ATUAL_CUSTOM_agora(st, usuario, 'THEMA_EDITOR', Tema_Editor)
			ATUAL_CUSTOM_agora(st, usuario, 'THEMA_PREVIEW', Tema_Preview)
			ATUAL_CUSTOM_agora(st, usuario, 'THEMA_TERMINAL', Tema_Terminal)
			ATUAL_CUSTOM_agora(st, usuario, 'THEMA_APP1', THEMA_APP1)
			ATUAL_CUSTOM_agora(st, usuario, 'THEMA_APP2', THEMA_APP2)
			ATUAL_CUSTOM_agora(st, usuario, 'OPC1', FUNDO_OUTROS)

			ATUAL_CUSTOM_agora(st, usuario, 'OPC3', ESCURECER_IMAGEM)

			st.success("✅ **TODAS** configs salvas!")
			st.balloons()


			st.rerun()


