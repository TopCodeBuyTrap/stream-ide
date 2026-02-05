import json
from time import sleep

from APP_SUB_Controle_Driretorios import _DIRETORIO_EXECUTAVEL_, _DIRETORIO_PROJETOS_, _DIRETORIO_PROJETO_ATUAL_
from APP_SUB_Funcitons import saudacao_por_hora_sistema, cor_semelhante
from Banco_dados import  ler_B_ARQUIVOS_RECENTES
import base64



def Carregamento_BancoDados_Temas(st):
	# ✅ CORREÇÃO 1: Chama funções ANTES de usar variáveis
	try:
		Pasta_Isntal_exec = _DIRETORIO_EXECUTAVEL_()
		Pasta_RAIZ_projeto = _DIRETORIO_PROJETOS_()
		Pasta_Projeto_Atual = _DIRETORIO_PROJETO_ATUAL_()
	except IndexError: pass
	if "estrutura_projeto" not in st.session_state:
		dados = ler_B_ARQUIVOS_RECENTES()
		st.session_state.estrutura_projeto = dados[0][1] if dados else ""

	Estrutura_projeto = st.session_state.estrutura_projeto

	# --------------------------------------------------------------------- CARREGAMENTO DE CUSTOMIZAÇÃO
	@st.cache_data
	def ler_CUSTOMIZATION_cached():
		from Banco_dados import ler_CUSTOMIZATION_TODOS
		return ler_CUSTOMIZATION_TODOS()

	cfg = ler_CUSTOMIZATION_cached()

	NOME_CUSTOM = cfg.get('NOME_CUSTOM')
	NOME_USUARIO = cfg.get('NOME_USUARIO')
	CAMINHO_DOWNLOAD = cfg.get('CAMINHO_DOWNLOAD')
	IMAGEM_LOGO = cfg.get('IMAGEM_LOGO')

	THEMA_EDITOR = cfg.get('THEMA_EDITOR')
	EDITOR_TAM_MENU = cfg.get('EDITOR_TAM_MENU')

	THEMA_PREVIEW = cfg.get('THEMA_PREVIEW')
	PREVIEW_TAM_MENU = cfg.get('PREVIEW_TAM_MENU')

	TERMINAL_TAM_MENU = cfg.get('TERMINAL_TAM_MENU')
	THEMA_TERMINAL = cfg.get('THEMA_TERMINAL')

	THEMA_APP1 = cfg.get('THEMA_APP1')
	THEMA_APP2 = cfg.get('THEMA_APP2')
	FONTE_MENU = cfg.get('FONTE_MENU')
	TAM_MENU = cfg.get('FONTE_TAM_MENU')
	COR_MENU = cfg.get('FONTE_COR_MENU')
	FONTE_CAMPO = cfg.get('FONTE_CAMPO')
	TAM_CAMPO = cfg.get('FONTE_TAM_CAMPO')
	COR_CAMPO = cfg.get('FONTE_COR_CAMPO')


	RADIO = cfg.get('RADIAL')
	BORDA = cfg.get('BORDA')
	BORDA_STIL = cfg.get('DECORA') # AQUI NO DECORA COLOQUEI TIPOS DE BORDA
	COR_WIDGET = cfg.get('OPC1') # coloquei fundo dos botes e expander etc..
	OPC2 = cfg.get('OPC2')
	OPC3 = cfg.get('OPC3') # COLOQUEI AQUI IMAGEM CONFIG
	OBS = cfg.get('OBS')

	# ✅ FUNÇÕES AUXILIARES (antes do CSS)
	def img_to_base64(img_path):
		try:
			with open(img_path, 'rb') as f:
				return base64.b64encode(f.read()).decode()
		except:
			return ""  # Fallback se imagem não existir
	def hex_to_rgba_inverso(hex_color: str, intensidade):
		try:
			intensidade = float(intensidade) / 100  # 0–1
		except:
			intensidade = 0.3

		# INVERTE A OPACIDADE
		alpha = 1.0 - intensidade
		alpha = max(0.0, min(alpha, 1.0))

		hex_color = hex_color.lstrip("#")
		r = int(hex_color[0:2], 16)
		g = int(hex_color[2:4], 16)
		b = int(hex_color[4:6], 16)

		return f"rgba({r},{g},{b},{alpha})"
	LOGO_BASE64 = img_to_base64(IMAGEM_LOGO)

	# cor base + opacidade vinda do OPC3
	try:
		COR_OVERLAY = hex_to_rgba_inverso(THEMA_APP2, float(OPC3))# NESSA PARTE DO CODIGO COLO OPACIDADE E IMAGEM NO BACKGROUND

		if OPC3 != "":
			BG_STYLE = f'''
		    background:
		        linear-gradient({COR_OVERLAY}, {COR_OVERLAY}),
		        url("data:image/png;base64,{LOGO_BASE64}") !important;
		        background-repeat: no-repeat !important;
			    background-position: center center !important;
			    background-size: cover !important;
		    '''
		else:
			BG_STYLE = f'''
		    background-color: {THEMA_APP2} !important;
		    '''
	except ValueError :
		BG_STYLE = f'''
				    background-color: {THEMA_APP2} !important;
				    '''

	def img_to_base64(image_path):
		with open(image_path, "rb") as img_file:
			return base64.b64encode(img_file.read()).decode()
	SD_STYLE = f'''
		    /* FUNDO COLORIDO PRIMEIRO */
    background-color: {THEMA_APP1} !important;
    
    /* IMAGEM PEQUENA SOBRE O FUNDO */
    background-image: url("data:image/png;base64,{img_to_base64('.arquivos/Logo_simbolo.png')}") !important;
    background-repeat: no-repeat !important;
    background-position: top bottom !important;
    
    
    background-size: 450px 650px !important;  /* ← IMAGEM PEQUENA */
    
'''
	try:
		COR_OVERLAY2 = hex_to_rgba_inverso(COR_WIDGET, float(OPC3))# NESSA PARTE DO CODIGO COLO OPACIDADE NO WIDGET

		if OPC3 != "":
			WD_STYLE = f'''
		    background: {COR_OVERLAY2} !important;
		    '''


		else:
			WD_STYLE = f'''
		    background-color: {COR_WIDGET} !important;
		    '''
	except ValueError :
		WD_STYLE = f'''
				    background-color: {COR_WIDGET} !important;
				    '''


	PASSR_COR = 'red'
	# simblinhado = underline = _____  line-through  underline wavy,  underline dashed = _ _ _  underline dotted = ...
	page_bg = f"""
    <style>
	    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,400;1,400&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;700&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&display=swap');
	    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');


	/* CONTEÚDO CENTRAL */
	section[data-testid="stMain2"] {{ /* REMOVER SCROLL */
	    overflow: hidden !important;
	}}
	

	
    P {{                                                          /* VALORES  SUBHEADERS */
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important; 
    }}
                                                                                          

    
    [data-testid="stMarkdown"] p {{                               /* MARKDOWS E WRITES */
        color: {COR_CAMPO} !important;
        font-size: {FONTE_MENU}px !important;
        font-style: italic !important;        
    }}
        
    input {{                                                        /* PARA TODOS OS INPUTS */ 
        color: {COR_CAMPO} !important;
        font-family: {FONTE_CAMPO} !important;
        font-size: {FONTE_MENU}px !important;
    }}
    
    div[data-testid="stButton"] button {{                               /* Botões */
		color: {COR_MENU} !important;		
		font-family: {FONTE_MENU} !important;
		min-height: 10px !important;
		border-radius: {RADIO}px !important;
		border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;   
		padding: none !important;
		padding-top: 0% !important;
		padding-bottom: 0% !important;           
 
    }}
    
	div[data-testid="stButton"] button:hover {{                             /* AO PASSAR O MAUSE */
	    background-color: {PASSR_COR} !important;  
	    transform: scale(1.01) !important;
	}}
	
	.stButton[data-testid="stButton"] button[kind="primary"] {{             /* AO PASSAR O MAUSE kind */
	    background-color: {cor_semelhante(COR_WIDGET)} !important;  

	}}
	.stButton[data-testid="stButton"] button[kind="secondary"] {{             /* AO PASSAR O MAUSE kind */
	    	    background-color: {cor_semelhante(COR_WIDGET)} !important;  


	}}
	
	div[data-testid="stForm"] {{                                            /* FORM  FORMULARIO */
       	    background-color: {cor_semelhante(COR_WIDGET)} !important;  

	
       padding: none !important;
       padding-top: 0% !important;
       padding-bottom: 0% !important;

	}}
	[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primaryFormSubmit"] {{    /* FORM  BOTAO */
       padding-top: 0% !important;
       padding-left: 0% !important;
       padding-right: 0% !important;
       padding-bottom: 0% !important;
		color: {COR_CAMPO} !important;
		border-radius: {RADIO}px !important;
		border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;

	}}
	div[data-testid="stColumn"] {{                                            /* COLUNAS st.columns() */
		padding-top: 0% !important; 
		padding-left: 0% !important;
		padding-right: 0% !important;
		padding-bottom: 0% !important;

	}}
	
	div[data-testid="stButton"] button[kind="primary"] {{                    /* GARANTE COR DO type="primary" */ 
	    background-color: {PASSR_COR} !important;
	    border: {BORDA}px solid red !important;
	}}         
	                                            
    [data-testid="stSlider"] p {{                                           /* SLIDER */ 
        color: {COR_MENU} !important;
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important;
    }}

    [data-testid="stRadio"] p, {{                                           /* RADIO */ 
        color: {COR_MENU} !important;
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important;
    }}
                                                                                  /* CHECKBOX */
    [data-testid="stCheckbox"] div {{
        text-decoration: underline !important;
        padding: 1px !important;
	    color: white !important;
        
    }}
    
	div[data-testid="stCheckbox"] label:hover {{                             /* AO PASSAR O MAUSE CHECKBOX */
	    background-color: {PASSR_COR} !important;  
	    transform: scale(1.05) !important; 
	}}
	
	
	input[type="checkbox"]:checked + div {{                                 /* checkbox MARCADO */
	    background-color: {COR_WIDGET } !important;
	}}
    
   [data-testid="stColorPicker"] {{                                           /* COLOR PICK */ 
        color: {COR_MENU} !important;
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important;
        
    }}
    
    [data-testid="stNumberInput"]  {{                                      /* NUMBER */ 
        color: {COR_MENU} !important;
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important;
    }}
    
	div[data-testid="stSelectbox"] div[data-baseweb="select"] {{                                         /* SELCTBOX */ 
        background-color: {COR_WIDGET} !important;
        color: {COR_CAMPO} !important;
        font-family: {FONTE_CAMPO} !important;
        font-size: {FONTE_MENU}px !important;
        border-radius: {RADIO}px !important;
        border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
    }}
        [data-testid="stSelectbox"] p{{                           /* LABEL SELCBOX*/
        color: {COR_MENU} !important;
        
    }}
    
	ul[data-testid="stSelectboxVirtualDropdown"]  {{                                         /* SELCTBOX */ 
        background-color: {THEMA_APP1} !important;
        color: {COR_CAMPO} !important;
        font-family: {FONTE_CAMPO} !important;
        font-size: {FONTE_MENU}px !important;
        border-radius: {RADIO}px !important;
        border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
    }}


    [data-testid="stTextInput"] p{{                                            /* TEXT INPUT */ 
        color: {COR_MENU} !important;
        font-family: {FONTE_MENU} !important;
        font-size: {TAM_MENU}px !important;
    }}

    [data-testid="stExpander"] {{                                               /* EXPANDER */ 
        background-color: {COR_WIDGET} !important;
        color: {COR_MENU} !important;
        border-radius: 0px !important;
    }}
    

    [data-testid="stElementContainerTTTT"] {{                               /* TODOS ELEMENTOSCONTAINER INCLUSOVE SELECT E EXPANDER */
        color: {COR_MENU} !important;
        border-radius: {RADIO}px !important;
        border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
    }}
    
        header.stAppHeader {{                                               /* HEADER */
        padding-left: 0% !important;
        margin-top: 15px !important;
        left:auto !important;
        width: 15% !important;
         /* BACKGROUND TRANSPARENTE */
	    background: transparent !important;
	    background-color: transparent !important;
	    
	    /* Borda transparente também */
	    border: none !important;
	    box-shadow: none !important;
	    
    }}
    
    .block-container {{                                                                 /* BLOCO PRINCIPAL BODY*/
        margin-top: -5% !important;
        margin-left: 0px !important;
        padding-left: 3.7% !important;
        margin-right: 0px !important;
        width: 109% !important;
        max-width: none !important;
        {BG_STYLE}
    }}
   
	section[data-testid="stSidebar"] {{                                         /* SIDEBAR */
        {SD_STYLE}
        width: 400px !important;
        height: 110% !important;
        margin-top: -1% !important;
        margin-left: -0% !important;
        
        border: {BORDA+1}px solid {THEMA_APP2} !important;
    }}

    [data-testid="stSidebarCollapseButton"] {{                                  /* BOTÃO DO SIDEBAR DE CIMA >> */
        margin-top: 3% !important;
    
	    position: fixed !important;
	    background-color: {COR_CAMPO} !important;
        border-radius: {RADIO}px !important;
        border: {BORDA}px {BORDA_STIL}ortant;
	}}

    [data-testid="stExpandSidebarButton"] {{                                    /* BOTÃO DO SIDEBAR DE BAIXO << */            
        background-color: {COR_CAMPO} !important;
        position: fixed !important;
        top: 5% !important;
        left: -2px !important;
        height: 11px !important;
        opacity: 1 !important;
        z-index: 9999 !important;
    }}

    div[data-testid="stVerticalBlock"][class*="st-key-Bra-o_Sidebar"] {{ /* MENU de botao POUPAP - AO LADO DO SIDEBAR */
        background-color: {THEMA_APP1} !important;
	    position: absolute !important;
	    top: 3% !important;  /* Alinha no topo do sidebar */
		left: 70% !important;
	    border-radius: {RADIO}px !important;
	    border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
	    z-index: 9999999999 !important;
	    width: 600px; /* Largura fixa do seu bloco */
	    transition: transform .001s ease !important; /* Animação suave */
	}}

	/* Container principal para posicionamento correto */
	section[data-testid="stAppViewContainer"] {{
	    position: relative !important;
	}}

    /*    stElementContainer 
    div[data-testid="stLayoutWrapper"] [class*="stElementContainer element-container st-emotion-cache-3pwa5w e12zf7d51"]{{
        background-color: {THEMA_APP1} !important;
         border-radius: {RADIO}px !important;
        border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important; 

    }}  */
	
	    
    [data-testid="stBaseButton-pills"] {{                               /* ST.PILLS BOTAO */
        background-color: {COR_WIDGET} !important;
        border: 0px solid {COR_CAMPO} !important; 
        margin-bottom: -8% !important;
        
	}}
	
	[data-testid="stBaseButton-pillsActive"] {{
        border: 0px solid {COR_CAMPO} !important; 
		padding: 2px 8px !important;                                    /* mesma altura */
		margin-bottom: 2px !important;  
		border-radius: 0 !important;
		margin-bottom: -4% !important;
	    padding-left: -100% !important;
    }}
    
	[data-testid="stBaseButton-secondary"]:has(kbd[aria-label="Shortcut Ctrl + Entereeeeeee "]){{/* BOTAO RUN */
        margin-top: -11.05% !important;
        background-color: {COR_CAMPO} !important;
        color: {COR_MENU} !important;
        position: fixed !important;
        width: 10% !important;
        right: 45% !important;
        z-index: 9999 !important;
        border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important; 
        
        
         /* ✅ SCROLL HABILITADO */
	    overflow: visible !important;  /* Permite conteúdo maior */
	    max-height: none !important;   /* Remove limitação de altura */
	    height: auto !important;       /* Altura dinâmica */
    }}
    
    [data-testid="stCustomComponentV1 vvvvvv"] {{                                      /* EDITORES DE CODIGOS */
		background-color: {COR_WIDGET} !important;
		border-radius: {RADIO}px !important;
		border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important; 
		
    }}

    div[data-testid="stVerticalBlock"][class*="st-key-menu_lado_sidebar"] {{             /* stVerticalBlock st-key-menu_lado_sidebar st-emotion-cache-1gz5zxc e12zf7d53 */
               {WD_STYLE}

        
    }}
    
    div[data-testid="stButton"][class*="st-key-nome_da_sua_key"] {{             /* CONTAINERS */
        background-color: {COR_WIDGET} !important;
        padding: 0 !important;
        height: 5% !important;
    }}

	[data-testid="stTextarea"][class*="st-dfs___________dd"] {{  /* nao  ta usando */
        background-color: {COR_WIDGET} !important;
		border-radius: {RADIO+8}px !important;
		border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;	
    }}
    	
	[data-baseweb="base-input"] textarea  {{
	    background-color: black !important;  /* Fundo do input */
	    color: white  !important;             /* Cor do texto */
	    border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
	}}
    
    input[data-baseweb="base-input"] textarea  {{
	    background-color: black !important;  /* Fundo do input */
	    color: {COR_CAMPO}  !important;             /* Cor do texto */
	    border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
        font-family: {FONTE_CAMPO} !important;
        font-size: {FONTE_MENU}px !important;
	}}
    
	div[data-testid="stVerticalBlock"] [class*="st-key-MenuTopo"] {{         /* CABEÇALHO MENU TOPO */
		        background-color: {THEMA_APP1} !important;

		height: 4% !important; 
		padding-top: 1% !important;
		padding-bottom: -10% !important;
		position: fixed !important;
		align-items: center !important;
		
		top: -1.5% !important;
		z-index: 99999 !important;
		display: flex !important;


    }} 
    
div[data-testid="stTabs"][class*="st-emotion-cache-8atqhb eh1nhsq0"] {{
    {WD_STYLE}
    border-radius: {RADIO}px !important;
    border: {BORDA}px {BORDA_STIL} {COR_CAMPO} !important;
    padding-left: 0% !important;
}}

/* ABAS NÃO-SELECIONADAS - CINZA */
div[data-testid="stTabs"][class*="st-emotion-cache-8atqhb eh1nhsq0"] [data-baseweb="tab"]:not([aria-selected="true"]) {{
  color: {COR_CAMPO} !important;
  opacity: 0.8 !important;
}}

/* ABA ATIVA - SUA COR */
div[data-testid="stTabs"][class*="st-emotion-cache-8atqhb eh1nhsq0"] [data-baseweb="tab"][aria-selected="true"] {{
  color: {COR_MENU} !important;
}}
	
    div[data-testid="stVerticalBlock"][class*="st-key-Terminal_cmd st-emotion-cache-1gz5zxc e12zf7d53"] {{         /*  TERMINAL  */
       {BG_STYLE}
        position: fixed !important;
        bottom: 0% !important;
        padding-left:0% !important;
        right: 0% !important;
        z-index: 999 !important;
        display: flex !important;
        justify-content: space-between !important;
        padding: 0px !important;
        width: 100% !important;      
          
    }}
    .st-key-BtnTerminal_widget .stButton button > div {{
	    justify-content: flex-start !important;
	    text-align: left !important;
	    margin-left: 20px !important;
	    height: 30px !important;

	}}
	
    
    div[data-testid="stVerticalBlock"][class*="st-key-Preview st-emotion-cache-1gz5zxc e12zf7d53"] {{       /* PREVIEWS  */
       {BG_STYLE}
        position: fixed !important;
        bottom: 0% !important;
        padding-left:0% !important;
        right: 0% !important;
        z-index: 9999 !important;
        display: flex !important;
        justify-content: space-between !important;
        padding: 0px !important;
        width:90% !important; 		
    }}
    .st-key-BtnPreview_widget .stButton button > div {{
	    justify-content: flex-start !important;
	    text-align: left !important;
	    margin-left: 20px !important;
	    height: 30px !important;

	}}
     div[data-testid="stVerticalBlock"][class*="st-key-Preview_Jason st-emotion-cache-1gz5zxc e12zf7d53"] {{       /* JASON  */
       {BG_STYLE}
        position: fixed !important;
        bottom: 0% !important;
        padding-left:0% !important;
        right: 0% !important;
        z-index: 99999 !important;
        display: flex !important;
        justify-content: space-between !important;
        padding: 0px !important;
        width:80% !important; 		
    }}
    .st-key-BtnJson_widget .stButton button > div {{
	    justify-content: flex-start !important;
	    text-align: left !important;
	    margin-left: 20px !important;
	    height: 30px !important;

	}}
     div[data-testid="stVerticalBlock"][class*="st-key-Api_IA st-emotion-cache-1gz5zxc e12zf7d53"] {{       /* CHAT IA  */
       {BG_STYLE}
        position: fixed !important;
        bottom: 0% !important;
        padding-left:0% !important;
        right: 0% !important;
        z-index: 999999 !important;
        display: flex !important;
        justify-content: space-between !important;
        padding: 0px !important;
        width:70% !important; 		
    }}
    .st-key-BtnChat_widget .stButton button > div {{
	    justify-content: flex-start !important;
	    text-align: left !important;
	    margin-left: 20px !important;
	    height: 30px !important;

	}}
     div[data-testid="stVerticalBlock"][class*="st-key-Catalogar_scripts st-emotion-cache-1gz5zxc e12zf7d53"] {{       /* CATALOGAR */
       {BG_STYLE}
        position: fixed !important;
        bottom: 0% !important;
        padding-left:0% !important;
        right: 0% !important;
        z-index: 9999999 !important;
        display: flex !important;
        justify-content: space-between !important;
        padding: 0px !important;
        width:60% !important; 		
    }}
    .st-key-BtnCatalogar_widget .stButton button > div {{
	    justify-content: flex-start !important;
	    text-align: left !important;
	    margin-left: 20px !important;
	    height: 30px !important;

	}}


    
    </style>


    """

	st.markdown(page_bg, unsafe_allow_html=True)


	def resumo_dict_para_html(dados_str: str) -> str:
		import ast
		import os
		from datetime import datetime
		pastas = 0
		arquivos = 0
		extensoes = {}
		criado = "-"
		modificado = "-"
		versoes_str = ""

		try:
			# Tenta diferentes métodos de parsing
			dados = None

			# 1. Tenta ast.literal_eval primeiro (mais seguro)
			try:
				dados = ast.literal_eval(dados_str)
			except (ValueError, SyntaxError):
				pass

			# 2. Se falhar, tenta json.loads
			if dados is None:
				try:
					dados = json.loads(dados_str)
				except:
					pass

			# 3. Se ainda falhar, tenta converter de str para dict simples
			if dados is None and dados_str.strip():
				try:
					# Remove aspas extras se for string simples
					cleaned_str = dados_str.strip().strip("'\"")
					dados = ast.literal_eval(f"{{ {cleaned_str} }}")
				except:
					pass

			# Se conseguiu parsear os dados
			if isinstance(dados, dict):
				pastas = dados.get("pastas", 0)
				arquivos = dados.get("arquivos", 0)
				extensoes = dados.get("extensao", {})
				versoes = dados.get("versoes", [])

				# Formata extensões
				extensoes_str = " / ".join(f"{v}{k}" for k, v in extensoes.items())

				# Formata versões
				if versoes:
					versoes_str = " / ".join(
						", ".join(v) if isinstance(v, (set, list, tuple)) else str(v)
						for v in versoes
					)

				# Processa datas
				datas = dados.get("datas", [])
				if datas and isinstance(datas, list) and len(datas) > 0:
					data_info = datas[0]
					criado_raw = data_info.get("criado", "-")
					modificado_raw = data_info.get("modificado", "-")

					# Converte datas
					try:
						if isinstance(criado_raw, str) and len(criado_raw) >= 19:
							criado = datetime.strptime(criado_raw[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
					except:
						criado = criado_raw if criado_raw != "-" else "-"

					try:
						if isinstance(modificado_raw, str) and len(modificado_raw) >= 19:
							modificado = datetime.strptime(modificado_raw[:19], "%Y-%m-%d %H:%M:%S").strftime(
								"%d/%m/%Y")
					except:
						modificado = modificado_raw if modificado_raw != "-" else "-"


			return f"""
	<span style="color: orange;">{versoes_str}</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">📚{saudacao_por_hora_sistema()} </span>
	<span>{NOME_USUARIO} !</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">Custom atual:</span>
	<span style="font-weight:500;"> {NOME_CUSTOM} </span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">:material/content_paste:Projeto: </span>
	<span style="font-weight:500;"> {os.path.basename(Pasta_Projeto_Atual)} </span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">Criado:</span>
	<span>{criado}</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">Modificado:</span>
	<span>{modificado}</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;"> Conteudo:&nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">:material/folder:</span>
	<span>{pastas}</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">:material/insert_drive_file:</span>
	<span>{arquivos}</span>
	<span style="opacity:0.1;">&nbsp;&nbsp; | &nbsp;&nbsp;</span>
	<span style="color:{COR_MENU}; font-size: {FONTE_MENU}px; opacity:0.85;">:material/dynamic_feed:&nbsp;</span>
	<span>{extensoes_str.lower().replace('/','&nbsp;')}</span>


	"""
		except Exception:
			# Em caso de erro total, usa valores padrão
			pass

	@st.cache_data(ttl=30)  # Cache de 30s - ajustável
	def gerar_footer_html():
		"""Gera o HTML do footer uma vez a cada 30s"""
		return resumo_dict_para_html(Estrutura_projeto)

	TOP_CAB = f"""
	<style>
	.footer {{
		top: 0% !important;
		left: 2% !important;
		padding-left: 2% !important;
		right: 0 !important;
		height: 20px !important;
		z-index: 9!important;
		display: flex !important;
		align-items: left !important;
		padding-bottom: 0px !important;
		color: white !important;
		white-space: nowrap !important;
	    
	    
	}}
	</style>

	<div class="footer">
	{gerar_footer_html()}
	</div>
	"""


	# Injeta CSS para mudar o fundo do Ace Editor.)

	def criar_estilos_botao():  # ainda noa usei
		"""Estilos CSS personalizados"""
		return f"""		         
	    <style>
	    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

	    .main-title {{ font-family: 'Fira Code', monospace; font-size: 3rem; 
	        background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4);
	        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
	        text-align: center; margin-bottom: 2rem; font-weight: 700; }}

	    .stButton > button {{ background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
	        border: none; color: white; font-family: 'JetBrains Mono', monospace;
	        font-weight: 600; border-radius: 12px; padding: 12px 24px; 
	        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}

	    .stButton > button:hover {{ transform: translateY(-2px); 
	        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6); }}

	    .config-section, .sobre-section {{ background: rgba(15, 15, 25, 0.95); padding: 2rem;
	        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); 
	        backdrop-filter: blur(10px); margin-bottom: 1rem; }}

	    .path-section {{ background: linear-gradient(135deg, rgba(0, 170, 255, 0.1), rgba(0, 255, 127, 0.1));
	        border-left: 5px solid #00aaff; padding: 1.5rem; margin: 1rem 0; border-radius: 10px; }}
	    </style>
	    """

	return (IMAGEM_LOGO, NOME_CUSTOM, NOME_USUARIO, COR_CAMPO, COR_MENU, THEMA_EDITOR,EDITOR_TAM_MENU,THEMA_PREVIEW,
	        PREVIEW_TAM_MENU,THEMA_TERMINAL,TERMINAL_TAM_MENU,TOP_CAB,FONTE_MENU,FONTE_CAMPO)

# ✅ IMPORTS NO TOPO (CORRIGIDO)
