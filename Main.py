import subprocess
from pathlib import Path
import streamlit as st
import threading
import queue
import os, time, re, sys, ast

from APP_Editores_Auxiliares.APP_Catalogo import arquivo_ja_catalogado
from APP_Editores_Auxiliares.APP_Editor_Codigo import editor_codigo_autosave

from APP_Menus import Apagar_Arq
from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO
from APP_SUB_Funcitons import Identificar_linguagem, Sinbolos, \
    controlar_altura_horiz
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs
from APP_Editores_Auxiliares.SUB_Run_servidores import netstat_streamlit, run_streamlit_process, is_streamlit_code, is_flask_code, \
    run_flex_process, extract_flask_config, find_port_by_pid, stop_flex, stop_process_by_port, is_django_code, \
    extract_django_config
from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida
from Banco_dados import reset_db, scan_project

# 🔥 USA A FUNÇÃO MESTRE - ZERO Path()
_Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()



def Editor_Simples(Select, CAMINHHOS, THEMA_EDITOR, EDITOR_TAM_MENU, FONTE, colStop, ColunaRun, CorBACK, altura=400):
    def nome_curto(nome, limite=20):
        base, ext = os.path.splitext(nome)
        if ext:
            return (base[:limite - len(ext)] + ext) if len(base) > limite else nome
        return nome[:limite]

    _ = st.session_state
    _.setdefault("output", "")
    _.setdefault("output_queue", queue.Queue())
    _.setdefault("input_queue", queue.Queue())
    _.setdefault("codigo_para_executar", None)
    _.setdefault("thread_running", False)
    _.setdefault("id_aba_ativa", 0)
    _.setdefault("Diretorio", {})
    _.setdefault("Conteudo", {})

    CAMINHHOS = get_arquivos_foi_ativado()

    nomes_arquivos = [os.path.basename(c) for c in CAMINHHOS]
    nomes_completos = []
    for caminho in CAMINHHOS:
        nom_arqu = os.path.basename(caminho)
        ja_catalogado, info = arquivo_ja_catalogado(caminho)
        cat = ':material/star_rate:' if ja_catalogado else ''
        em = Sinbolos(nom_arqu)
        nome_formatado = f"{em}{nome_curto(nom_arqu, 12)}{cat}"
        nomes_completos.append(nome_formatado)

    ativos = get_arquivos_ativos()
    indices_ativos = [i for i, c in enumerate(CAMINHHOS) if c in ativos]
    abas_ativas = [nomes_completos[i] for i in indices_ativos]
    caminhos_ativos = [CAMINHHOS[i] for i in indices_ativos]

    if not abas_ativas:
        st.info("Nenhum arquivo ativo. Marque um arquivo no sidebar para abri-lo como aba.")
        return

    abas = st.tabs(abas_ativas)

    # Loop para abas ativas
    for idx, aba in enumerate(abas):
        with aba:
            EDIT_COL, INFO_COL = st.columns([8, 2])

            i = indices_ativos[idx]
            caminho = caminhos_ativos[idx]

            _.Diretorio[i] = caminho

            nome_arquivo = os.path.basename(caminho)
            Nome_Aba = nomes_arquivos[i]
            linguagem = Identificar_linguagem(caminho)

            conteudo_inicial = carregar_conteudo_session_state(caminho)
            if conteudo_inicial is None:
                conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, caminho)
                salvar_conteudo_session_state(caminho, conteudo_inicial)

            extensao = os.path.splitext(nome_arquivo)[1].lower()
            try:
                with EDIT_COL:
                    contador_key = f"contador_recarga_{hashlib.md5(caminho.encode()).hexdigest()}"
                    contador = _.get(contador_key, 0)
                    key_unica = f"editor_{hashlib.md5(caminho.encode()).hexdigest()}_{contador}"
                    cod = editor_codigo_autosave(st, i, Nome_Aba, _.Diretorio[i], linguagem, THEMA_EDITOR, EDITOR_TAM_MENU, FONTE, altura, INFO_COL, CorBACK, caminho)
            except AttributeError:
                pass