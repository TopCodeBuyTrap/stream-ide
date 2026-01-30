import json
import subprocess
import textwrap
from datetime import datetime



from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_
# ===== FIX WINDOWS: NÃO ABRIR CMD / POWERSHELL =====
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW

def data_sistema():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def Alerta(st,msg):
    @st.dialog("Alerta ")
    def menu_principal():
        st.warning(msg)
    menu_principal()

def Linha_Sep(Cor,Larg):
    import streamlit.components.v1 as components

    HtmL =f'<div style="display: block; background-color: {Cor}; width: 100%; height: {Larg}px;"></div>'
    return components.html(HtmL, height=Larg+9, scrolling=False)
