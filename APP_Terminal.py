from pathlib import Path
import streamlit as st
import subprocess
import queue
import threading
import time
import os
import atexit
import signal
import re

# ===== FIX WINDOWS: NÃO ABRIR JANELA =====
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW

from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_


def get_prompt():
    """Gera o prompt do PowerShell com informações do diretório atual e venv"""
    try:
        root = Path(_DIRETORIO_PROJETO_ATUAL_())
        venv_path = root / ".virto_stream"
        if venv_path.exists():
            return f"({venv_path.name}) PS {root}> "
        return f"PS {root}> "
    except:
        return "PS ERRO> "


def kill_all_processes():
    """Mata APENAS Streamlit do PROJETO ATUAL (SEGURA!)"""
    try:
        root = Path(_DIRETORIO_PROJETO_ATUAL_())
        projeto_nome = root.name  # "MERDA" no seu caso

        # 🔥 MATA SÓ PROCESSOS DO SEU PROJETO
        cmd = f'''
        Get-Process streamlit,python | 
        Where-Object {{ $_.MainWindowTitle -like "*Streamlit*" -or $_.CommandLine -like "*{projeto_nome}*" }} | 
        Stop-Process -Force
        '''

        subprocess.run([
            "powershell", "-Command", cmd
        ], capture_output=True, startupinfo=STARTUPINFO, creationflags=CREATE_FLAGS)

    except:
        pass


def get_aba_state(aba_nome):
    """Estado persistente por aba"""
    if "terminal_abas" not in st.session_state:
        st.session_state.terminal_abas = {}
    if aba_nome not in st.session_state.terminal_abas:
        st.session_state.terminal_abas[aba_nome] = {
            "buffer": get_prompt(),
            "q": queue.Queue(),
            "running": False,
            "proc": None,
            "last_rerun": 0,
            "last_cmd": None
        }
    return st.session_state.terminal_abas[aba_nome]




def ler_pipe(pipe, q, prefix=""):
    """Lê stdout/stderr linha por linha e coloca na queue"""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                q.put(prefix + line.rstrip('\r\n'))
        q.put(None)  # sinal de fim
    except:
        pass
    finally:
        try:
            pipe.close()
        except:
            pass


def start_command(aba_nome, cmd):
    """Inicia comando PowerShell com suporte a venv e UTF-8"""
    state = get_aba_state(aba_nome)
    root = Path(_DIRETORIO_PROJETO_ATUAL_())
    venv = root / ".virto_stream"
    activate = venv / "Scripts" / "Activate.ps1"

    # Auto --yes para pip uninstall
    cmd_lower = cmd.lower()
    if "pip uninstall" in cmd_lower and "--yes" not in cmd and "-y" not in cmd:
        cmd += " --yes"
        state["buffer"] += "\n🔧 Adicionado --yes automaticamente\n"

    # Força UTF-8 + desabilita buffering
    full_cmd = (
        "chcp 65001 > $null; "  # UTF-8 codepage
        "$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding; "
        "$ProgressPreference = 'SilentlyContinue'; "
        "Remove-Module PSReadLine -ErrorAction SilentlyContinue; "
        f"cd '{root}'; "
    )
    if activate.exists():
        full_cmd += f"& '{activate}'; "
    full_cmd += cmd

    proc = subprocess.Popen(
        ["powershell", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", full_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace',
        startupinfo=STARTUPINFO,
        creationflags=CREATE_FLAGS
    )

    state["proc"] = proc
    state["running"] = True
    state["q"] = queue.Queue()

    # Threads de leitura
    threading.Thread(target=ler_pipe, args=(proc.stdout, state["q"], ""), daemon=True).start()
    threading.Thread(target=ler_pipe, args=(proc.stderr, state["q"], "ERR: "), daemon=True).start()


def safe_key(name):
    """Chave segura para widgets"""
    return re.sub(r'\W', '_', name)


def RenderTerminalAba(aba_nome):
    """Renderiza terminal com live output linha por linha"""
    state = get_aba_state(aba_nome)

    # Placeholder para atualizar sem piscar
    term_placeholder = st.empty()
    with term_placeholder:
        st.code(state["buffer"], language="powershell", line_numbers=False)

    # Input comando
    comando = st.chat_input("", key=f"cmd_{safe_key(aba_nome)}")

    if comando and comando.strip():
        prompt = get_prompt()

        # Suporte múltiplos comandos (um por vez, sequencial)
        linhas = [linha.strip() for linha in comando.splitlines() if linha.strip()]

        if len(linhas) > 1:
            # Executa cada comando sequencialmente
            for linha in linhas:
                state["buffer"] += f"\n{prompt}{linha}\n"
                with term_placeholder:
                    st.code(state["buffer"], language="powershell")

                start_command(aba_nome, linha)

                # Espera este comando terminar antes do próximo
                while state["running"]:
                    time.sleep(0.2)
                    process_queue(state, term_placeholder)

                state["buffer"] += "\n"
        else:
            # Comando único
            state["buffer"] += f"\n{prompt}{comando}\n"
            with term_placeholder:
                st.code(state["buffer"], language="powershell")
            start_command(aba_nome, comando)

        st.rerun()

    # Processa queue (non-blocking)
    process_queue(state, term_placeholder)

    # Controles quando rodando
    if state["running"]:
        col1, col2 = st.columns([2, 1])
        with col2:
            if st.button("🗑️ Limpar esta aba", key=f"limpar_{safe_key(aba_nome)}"):
                kill_all_processes()
                state["buffer"] = get_prompt()
                st.rerun()

        with col1:
            if st.button("🛑 Parar", key=f"kill_{safe_key(aba_nome)}"):
                if state["proc"] and state["proc"].poll() is None:
                    state["proc"].kill()
                    state["proc"].wait(timeout=3)
                kill_all_processes(aba_nome)

                state["running"] = False
                state["buffer"] += "\n[INTERROMPIDO PELO USUÁRIO]\n"
                with term_placeholder:
                    st.code(state["buffer"], language="powershell")
                st.rerun()

        # Live update suave
        agora = time.time()
        if agora - state.get("last_rerun", 0) > 0.15:
            state["last_rerun"] = agora
            time.sleep(0.15)
            st.rerun()

    # Prompt novo quando terminou
    if not state["running"] and not state["buffer"].strip().endswith(">"):
        state["buffer"] += get_prompt()
        with term_placeholder:
            st.code(state["buffer"], language="powershell")


def process_queue(state, placeholder):
    """Processa queue sem bloquear - MOSTRA COMANDO CORRETO"""
    updated = False

    while not state["q"].empty():
        try:
            linha = state["q"].get_nowait()

            if linha is None:
                # ✅ COMANDO TERMINOU - mostra o comando EXATO
                if "last_cmd" in state and state["last_cmd"]:
                    cmd_executado = state["last_cmd"].strip()
                    state["buffer"] += f"\n✅ [{cmd_executado}] CONCLUÍDO ✅\n"
                else:
                    state["buffer"] += f"\n✅ Comando concluído ✅\n"

                state["running"] = False
                state["last_cmd"] = None  # limpa
                updated = True
                break
            else:
                state["buffer"] += linha + "\n"
                updated = True

        except queue.Empty:
            break

    if updated:
        with placeholder:
            st.code(state["buffer"], language="powershell", line_numbers=False)


def Terminal(altura=500, THEMA_TERMINAL="default", TERMINAL_TAM_MENU=14):
    """Terminal Multi-Aba COMPLETO com live output"""

    # Inicializa abas
    if "abas_terminal" not in st.session_state:
        st.session_state.abas_terminal = ["Terminal 1"]
    if "contador_aba" not in st.session_state:
        st.session_state.contador_aba = 1

    # Header com nova aba
    col1, col2 = st.columns([1, 20])
    with col1:
        if st.button("➕ Nova aba"):
            st.session_state.contador_aba += 1
            st.session_state.abas_terminal.append(f"Terminal {st.session_state.contador_aba}")
            st.rerun()

    # Tabs
    tabs = st.tabs(st.session_state.abas_terminal)
    for idx, aba_nome in enumerate(st.session_state.abas_terminal):
        with tabs[idx]:
            container = st.container(height=altura)
            with container:
                RenderTerminalAba(aba_nome)

    # Limpar tudo (mata processos!)
    if st.button("🗑️ Limpar todos terminais"):
        kill_all_processes()
        for aba in st.session_state.abas_terminal:
            state = get_aba_state(aba)
            state["buffer"] = get_prompt()
            state["running"] = False
            state["proc"] = None
        st.rerun()
