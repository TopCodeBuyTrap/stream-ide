import os
from APP_SUB_Funcitons import Identificar_linguagem, sincronizar_estrutura, Sinbolos
from APP_SUB_Janela_Explorer import listar_arquivos_e_pastas
from Banco_dados import ler_CONTROLE_ARQUIVOS, Del_CONTROLE_ARQUIVOS, se_CONTROLE_ARQUIVOS
import streamlit as st


# com pills
def Sidebar_Diretorios_(st, lista_projeto, qt_col):

	"""Sidebar: Projeto + Banco NUM MESMO LUGAR - VERSÃO CORRIGIDA SEM DUPLICAÇÃO"""

	# Inicializa estados específicos da sidebar (CORRIGIDO)
	if 'file_status_sidebar' not in st.session_state:
		st.session_state.file_status_sidebar = {}
	if 'editor_ativo_sidebar' not in st.session_state:
		st.session_state.editor_ativo_sidebar = None
	if 'expanders_abertos_sidebar' not in st.session_state:
		st.session_state.expanders_abertos_sidebar = set()

	todos_abertos = []

	# 1. PROCESSA PROJETO
	def processar_projeto(nome_item, caminho_item, nivel=0):
		abertos_locais = []

		if os.path.isdir(caminho_item):
			pasta_id = f"exp_sidebar_{caminho_item.replace('/', '_').replace('\\', '_')}"
			is_venv = any(venv in nome_item.lower() for venv in ['.venv', 'virtual'])
			emoji = '🛠️' if is_venv else '📁'  # 🐍 para venv, ➤ para outros

			mostrar_conteudo = st.checkbox(
				f"{nome_item} {emoji}",
				key=pasta_id,
				value=pasta_id in st.session_state.expanders_abertos_sidebar
			)
			'''mostrar_conteudo = st.pills(
				label=f"📁{nome_item}",  # obrigatoriamente o primeiro argumento
				options=[f"📁{nome_item}"],  # lista de opções
				key=pasta_id,
				selection_mode="single",
				width='stretch',
				label_visibility="collapsed"
			)'''
			if mostrar_conteudo:
				st.session_state.expanders_abertos_sidebar.add(pasta_id)
				l, Container_Sidebar = st.columns([0.5, 9])
				with Container_Sidebar:
					if caminho_item not in st.session_state:
						st.session_state[caminho_item] = listar_arquivos_e_pastas(caminho_item)
					for nome_sub, caminho_sub in st.session_state[caminho_item]:
						sub_abertos = processar_projeto(nome_sub, caminho_sub, nivel + 1)
						abertos_locais.extend(sub_abertos)
			else:
				st.session_state.expanders_abertos_sidebar.discard(pasta_id)
		else:
			if nome_item not in st.session_state.file_status_sidebar:
				st.session_state.file_status_sidebar[nome_item] = True
			em = Sinbolos(nome_item)
			status = st.pills('caminho_item',f'{em}{nome_item}', key=f"chk_sidebar_{caminho_item.replace('/', '_').replace('\\', '_')}",
             selection_mode="single",width='stretch',label_visibility="collapsed",)
			st.session_state.file_status_sidebar[nome_item] = status
			if status:
				abertos_locais.append((nome_item, caminho_item, "projeto"))
		return abertos_locais

	# Processa PROJETO
	lista_projeto = [item for item in lista_projeto if item is not None and len(item) == 2]
	with st.container(border=True):
		for nome_item, caminho_item in lista_projeto:
			abertos_item = processar_projeto(nome_item, caminho_item)
			todos_abertos.extend(abertos_item)

	# 2. ADICIONA BANCO (SEM DUPLICAR)
	banco_arquivos = ler_CONTROLE_ARQUIVOS()
	for nome_arq, caminho, conteudo, ext in banco_arquivos:
		if sincronizar_estrutura(caminho) == False:# verifica se o aruivo esta no ".virto_stream" / "Arvore_projeto.json"
			if se_CONTROLE_ARQUIVOS(caminho, None):
					todos_abertos.append((nome_arq, caminho, "banco"))

	# Remove duplicatas mantendo último (MELHORADO)
	vistos = set()
	todos_abertos_unicos = []
	for item in reversed(todos_abertos):
		todos_abertos_unicos.append(item)
		vistos.add(item[0])
	todos_abertos = todos_abertos_unicos[::-1]

	# 3. LOOP PRINCIPAL - PROJETO + BANCO
	Arquivo_Selecionado_Completo = []
	Arquivo_Selecionado_Nomes = []
	if todos_abertos:
		with st.container(border=True):
			for im in range(0, len(todos_abertos), qt_col):
				for j, (arquivo, diretorio, origem) in enumerate(todos_abertos[im:im + qt_col]):
					Arquivo_Selecionado_Completo.append(diretorio)
					Arquivo_Selecionado_Nomes.append(arquivo)
					if origem == "banco":
						if st.button(f"{Sinbolos(arquivo)}{arquivo}' X",key=f"btn_banco_{arquivo}_{j}",width='stretch',type='tertiary'):
							Del_CONTROLE_ARQUIVOS(arquivo)
							st.rerun()



	return Arquivo_Selecionado_Nomes, Arquivo_Selecionado_Completo

# com checbox
def Sidebar_Diretorios(st, lista_projeto, qt_col):

	"""Sidebar: Projeto + Banco NUM MESMO LUGAR - VERSÃO CORRIGIDA SEM DUPLICAÇÃO"""

	# Inicializa estados específicos da sidebar (CORRIGIDO)
	if 'file_status_sidebar' not in st.session_state:
		st.session_state.file_status_sidebar = {}
	if 'editor_ativo_sidebar' not in st.session_state:
		st.session_state.editor_ativo_sidebar = None
	if 'expanders_abertos_sidebar' not in st.session_state:
		st.session_state.expanders_abertos_sidebar = set()

	todos_abertos = []

	# 1. PROCESSA PROJETO
	def processar_projeto(nome_item, caminho_item, nivel=0):
		abertos_locais = []

		if os.path.isdir(caminho_item):
			pasta_id = f"exp_sidebar_{caminho_item.replace('/', '_').replace('\\', '_')}"
			is_venv = any(venv in nome_item.lower() for venv in ['.venv', 'virtual'])
			emoji = '🛠️' if is_venv else '📁'  # 🐍 para venv, ➤ para outros

			mostrar_conteudo = st.checkbox(
				f"{nome_item} {emoji}",
				key=pasta_id,
				value=pasta_id in st.session_state.expanders_abertos_sidebar
			)

			if mostrar_conteudo:
				st.session_state.expanders_abertos_sidebar.add(pasta_id)
				l, Container_Sidebar = st.columns([0.5, 9])
				with Container_Sidebar:
					if caminho_item not in st.session_state:
						st.session_state[caminho_item] = listar_arquivos_e_pastas(caminho_item)
					for nome_sub, caminho_sub in st.session_state[caminho_item]:
						sub_abertos = processar_projeto(nome_sub, caminho_sub, nivel + 1)
						abertos_locais.extend(sub_abertos)
			else:
				st.session_state.expanders_abertos_sidebar.discard(pasta_id)
		else:
			if nome_item not in st.session_state.file_status_sidebar:
				st.session_state.file_status_sidebar[nome_item] = True
			em = Sinbolos(nome_item)
			status = st.checkbox(f'{em}{nome_item}', key=f"chk_sidebar_{caminho_item.replace('/', '_').replace('\\', '_')}")
			st.session_state.file_status_sidebar[nome_item] = status
			if status:
				abertos_locais.append((nome_item, caminho_item, "projeto"))
		return abertos_locais

	# Processa PROJETO
	lista_projeto = [item for item in lista_projeto if item is not None and len(item) == 2]
	with st.container(border=True):
		for nome_item, caminho_item in lista_projeto:
			abertos_item = processar_projeto(nome_item, caminho_item)
			todos_abertos.extend(abertos_item)

	# 2. ADICIONA BANCO (SEM DUPLICAR)
	banco_arquivos = ler_CONTROLE_ARQUIVOS()
	for nome_arq, caminho, conteudo, ext in banco_arquivos:
		if sincronizar_estrutura(caminho) == False:# verifica se o aruivo esta no ".virto_stream" / "Arvore_projeto.json"
			if se_CONTROLE_ARQUIVOS(caminho, None):
					todos_abertos.append((nome_arq, caminho, "banco"))

	# Remove duplicatas mantendo último (MELHORADO)
	vistos = set()
	todos_abertos_unicos = []
	for item in reversed(todos_abertos):
		todos_abertos_unicos.append(item)
		vistos.add(item[0])
	todos_abertos = todos_abertos_unicos[::-1]

	# 3. LOOP PRINCIPAL - PROJETO + BANCO
	Arquivo_Selecionado_Completo = []
	Arquivo_Selecionado_Nomes = []
	if todos_abertos:
		with st.container(border=True):
			for im in range(0, len(todos_abertos), qt_col):
				for j, (arquivo, diretorio, origem) in enumerate(todos_abertos[im:im + qt_col]):
					Arquivo_Selecionado_Completo.append(diretorio)
					Arquivo_Selecionado_Nomes.append(arquivo)
					if origem == "banco":
						if st.button(f"{Sinbolos(arquivo)}{arquivo}' X",key=f"btn_banco_{arquivo}_{j}",width='stretch',type='tertiary'):
							Del_CONTROLE_ARQUIVOS(arquivo)
							st.rerun()



	return Arquivo_Selecionado_Nomes, Arquivo_Selecionado_Completo






