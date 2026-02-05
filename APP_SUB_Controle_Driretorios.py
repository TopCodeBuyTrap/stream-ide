import sys

import  streamlit as st
from pathlib import Path


@st.cache_data
def _DIRETORIO_EXECUTAVEL_(arquivo=''):# onde o executavel vai ser instalado
    from Banco_dados import ler_A_CONTROLE_ABSOLUTO
    Pasta_Isntal_exec = Path(ler_A_CONTROLE_ABSOLUTO()[0][0]).resolve() # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
    if not Path(Pasta_Isntal_exec.parent, ".mim_mids").exists():
        Path(Pasta_Isntal_exec.parent, ".mim_mids").mkdir()
    # Pastas relativas à pasta_projeto
    if arquivo == '.arquivos':
        return Path(Pasta_Isntal_exec,'.arquivos')
    elif arquivo == 'mim_mids':
        return Path(Pasta_Isntal_exec.parent,'.mim_mids')
    elif arquivo == 'backup':
        return Path(ler_A_CONTROLE_ABSOLUTO()[0][2])
    elif arquivo == 'chave_api':
        return Path(ler_A_CONTROLE_ABSOLUTO()[0][5])
    else:
        return Pasta_Isntal_exec

@st.cache_data
def _DIRETORIO_PROJETOS_():
    from Banco_dados import ler_A_CONTROLE_ABSOLUTO
    Pasta_Projetos = Path(ler_A_CONTROLE_ABSOLUTO()[0][1]).resolve()  # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
    return Pasta_Projetos


def _DIRETORIO_PROJETO_ATUAL_():
    from Banco_dados import ler_B_ARQUIVOS_RECENTES
    try: #  Então esse TRY é só para isso. É só para quando ele abrir a segunda tela depois da abertura, né? Aquela que abre o pop-up para para ele criar um novo projeto e mudar ele.
        Projeto_Atual = Path(ler_B_ARQUIVOS_RECENTES()[0][0]).resolve()  # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
        return Projeto_Atual
    except IndexError:
        return _DIRETORIO_EXECUTAVEL_()




@st.cache_data
def VENVE_DO_PROJETO():
    projeto_path = Path(_DIRETORIO_PROJETO_ATUAL_())
    venv_win = projeto_path / ".virto_stream" / "Scripts" / "python.exe"
    venv = projeto_path / ".virto_stream"
    prompt = f"({venv.name}) PS {projeto_path}> "
    return str(venv_win), str(projeto_path), str(venv), prompt
