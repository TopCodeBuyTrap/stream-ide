# ========================================================
# INTEGRAÇÃO BANCO DE DADOS - DEPENDÊNCIA CRÍTICA
# ========================================================

import sys
from pathlib import Path
import streamlit as st
import subprocess
import threading
import queue
import re
import psutil

from APP_SUB_Funcitons import controlar_altura
from Banco_Dados_sudo_pip import *
from APP_SUB_Controle_Driretorios import (
    _DIRETORIO_PROJETO_ATUAL_,
    _DIRETORIO_EXECUTAVEL_
)

STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE


def VENVE_DO_PROJETO():
    projeto_path = Path(_DIRETORIO_PROJETO_ATUAL_())
    venv_win = projeto_path / ".virto_stream" / "Scripts" / "python.exe"
    venv = projeto_path / ".virto_stream"
    prompt = f"({venv.name}) PS {projeto_path}> "
    return str(venv_win), str(projeto_path), str(venv), prompt


_PYTHON_EXE, _ROOT_PATH, _VENV_PATH, _PROMPT = VENVE_DO_PROJETO()


def safe_key(name):
    return re.sub(r"\W", "_", name)


def get_aba_state(aba):
    if "terminal_abas" not in st.session_state:
        st.session_state.terminal_abas = {}

    if aba not in st.session_state.terminal_abas:
        st.session_state.terminal_abas[aba] = {
            "buffer": _PROMPT,
            "queue": queue.Queue(),
            "proc": None,
            "pid": None,
            "running": False,
            "cmd": None,
        }

    return st.session_state.terminal_abas[aba]


def reader_thread(proc, q):
    for line in iter(proc.stdout.readline, ""):
        q.put(line)
    q.put(None)


def start_command(aba, cmd):
    state = get_aba_state(aba)

    if state["running"]:
        return

    full_cmd = (
        "$global:prompt={''}; "
        "$OutputEncoding=[console]::OutputEncoding="
        "New-Object System.Text.UTF8Encoding; "
        f"cd '{_ROOT_PATH}'; {cmd}"
    )

    proc = subprocess.Popen(
        ["powershell", "-NoLogo", "-NoProfile", "-Command", full_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
        startupinfo=STARTUPINFO,
    )

    state["proc"] = proc
    state["pid"] = proc.pid
    state["cmd"] = cmd
    state["running"] = True
    state["queue"] = queue.Queue()

    threading.Thread(
        target=reader_thread,
        args=(proc, state["queue"]),
        daemon=True,
    ).start()


def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for c in parent.children(recursive=True):
            c.kill()
        parent.kill()
    except Exception:
        pass


@st.fragment(run_every=0.1)
def terminal_fragment(aba):
    state = get_aba_state(aba)

    if not state["running"]:
        st.code(state["buffer"], language="powershell")
        return

    while True:
        try:
            line = state["queue"].get_nowait()
        except queue.Empty:
            break

        if line is None:
            state["running"] = False
            state["proc"] = None
            state["pid"] = None
            state["buffer"] += f"\nCONCLUIDO: {state['cmd']}\n{_PROMPT}"
            break

        state["buffer"] += line

    st.code(state["buffer"], language="powershell")


def RenderTerminalAba(input_mode, altura, aba, aba_index=0):
    state = get_aba_state(aba)
    with st.container(height=altura):
        terminal_fragment(aba)

    if input_mode == "Digitar":
        cmd = st.chat_input(
            "Digite o comando",
            key=f"cmd_{aba_index}_{safe_key(aba)}"
        )

        if cmd:
            state["buffer"] += f"\n{_PROMPT}{cmd}\n"
            start_command(aba, cmd)
            st.stop()

    else:
        col1, col2, col3, col4, col5, col_btn = st.columns(6)

        with col1:
            modulos = listar_modulos()
            nomes = [m["nome"] for m in modulos]
            sel = st.selectbox(
                "Instalar",
                [""] + nomes,
                key=f"inst_{aba_index}_{safe_key(aba)}",
            )
            if sel:
                st.session_state.cmd_temp = carregar_comando_modulo(sel, "install")

        with col2:
            sel = st.selectbox(
                "Desinstalar",
                [""] + nomes,
                key=f"unist_{aba_index}_{safe_key(aba)}",
            )
            if sel:
                st.session_state.cmd_temp = carregar_comando_modulo(sel, "uninstall")

        with col3:
            sel = st.selectbox(
                "Upgrade",
                [""] + nomes,
                key=f"up_{aba_index}_{safe_key(aba)}",
            )
            if sel:
                st.session_state.cmd_temp = carregar_comando_modulo(sel, "upgrade")

        with col4:
            divs = listar_diversos()
            sel = st.selectbox(
                "Diversos",
                [""] + divs,
                key=f"div_{aba_index}_{safe_key(aba)}",
            )
            if sel:
                st.session_state.cmd_temp = carregar_diverso(sel)

        with col_btn:
            if "cmd_temp" in st.session_state:
                if st.button(
                    "EXECUTAR",
                    key=f"exec_{aba_index}_{safe_key(aba)}"
                ):
                    texto = st.session_state.cmd_temp
                    state["buffer"] += f"\n{_PROMPT}{texto}\n"
                    start_command(aba, texto)

    col1, col2, col3 = st.columns(3)

    if col1.button("PARAR", key=f"kill_{aba_index}_{safe_key(aba)}"):
        if state["pid"]:
            kill_process_tree(state["pid"])
        state["running"] = False
        state["proc"] = None
        state["pid"] = None
        state["buffer"] += f"\nINTERRUPT\n{_PROMPT}"

    if col2.button("LIMPAR", key=f"clear_{aba_index}_{safe_key(aba)}"):
        state["buffer"] = _PROMPT
        state["running"] = False
        state["proc"] = None
        state["pid"] = None

    if col3.button("PARAR TUDO", key=f"kill_all_{aba_index}_{safe_key(aba)}"):
        for s in st.session_state.terminal_abas.values():
            if s.get("pid"):
                kill_process_tree(s["pid"])
                s["running"] = False
                s["proc"] = None
                s["pid"] = None


def Terminal():
    if "abas_terminal" not in st.session_state:
        st.session_state.abas_terminal = ["Terminal 1"]

    col1, col2 = st.columns([1, 15])

    with col1:
        altura = controlar_altura(
            st, "Terminal",
            altura_inicial=400,
            passo=200,
            maximo=600,
            minimo=200
        )

        if st.button("Nova aba"):
            st.session_state.abas_terminal.append(
                f"Terminal {len(st.session_state.abas_terminal) + 1}"
            )

        input_mode = st.radio("Entrada", ["Digitar", "Escolher"])

    with col2:
        tabs = st.tabs(st.session_state.abas_terminal)
        for i, aba in enumerate(st.session_state.abas_terminal):
            with tabs[i]:
                RenderTerminalAba(input_mode, altura, aba, aba_index=i)
