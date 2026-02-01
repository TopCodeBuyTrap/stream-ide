# ========================================================
# INTEGRAÇÃO BANCO DE DADOS - DEPENDÊNCIA CRÍTICA
# ========================================================

"""
🔗 LIGAÇÃO BANCO ↔ TERMINAL (Fluxo Completo):
1. BANCO já inicializado: init_db_modulos() + carregar_modulos_padrao()
2. Terminal chama: modulos = listar_modulos() → preenche selectbox
3. Usuário seleciona "streamlit" → carregar_comando_modulo("streamlit", "install")
4. Botão clica → start_command(aba, cmd_install) → EXECUTA
5. Comando manual digitado → salvar_comando_usuario(cmd) → BANCO aprende

DEPENDÊNCIAS:
- Banco_Dados_sudo_pip.py DEVE existir no mesmo diretório
- init_db_modulos() e carregar_modulos_padrao() executados no import
- Tabela 'tabelas_modulos' criada automaticamente

FLUXO BIDIRECIONAL:
Terminal → Banco: salvar_comando_usuario() (aprendizado)
Banco → Terminal: listar_modulos() + carregar_comando_modulo() (execução)
"""

from pathlib import Path
from time import sleep

import streamlit as st
import subprocess
import threading
import queue
import re
import psutil

from APP_SUB_Funcitons import controlar_altura
from Banco_Dados_sudo_pip import *  # ← SEU BANCO COMPLETO
from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_

STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE


# SEU CÓDIGO ORIGINAL INTACTO (get_prompt, get_aba_state, etc)
def get_prompt():
    try:
        root = Path(_DIRETORIO_PROJETO_ATUAL_())
        venv = root / ".virto_stream"
        if venv.exists():
            return f"({venv.name}) PS {root}> "
        return f"PS {root}> "
    except:
        return "PS ERRO> "


def get_aba_state(aba):
    if "terminal_abas" not in st.session_state:
        st.session_state.terminal_abas = {}
    if aba not in st.session_state.terminal_abas:
        st.session_state.terminal_abas[aba] = {
            "buffer": get_prompt(),
            "running": False,
            "proc": None,
            "pid": None,
            "cmd": None,
            "queue": queue.Queue()
        }
    return st.session_state.terminal_abas[aba]


def reader_thread(proc, q):
    while True:
        line = proc.stdout.readline()
        if not line:
            q.put(None)
            break
        q.put(line)


def start_command(aba, cmd):
    state = get_aba_state(aba)
    root = Path(_DIRETORIO_PROJETO_ATUAL_())

    full_cmd = (
        "$OutputEncoding=[console]::OutputEncoding="
        "New-Object System.Text.UTF8Encoding;"
        f"cd '{root}'; {cmd}"
    )

    proc = subprocess.Popen(
        ["powershell", "-NoLogo", "-NoProfile", "-Command", full_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
        startupinfo=STARTUPINFO
    )

    state["proc"] = proc
    state["pid"] = proc.pid
    state["cmd"] = cmd
    state["running"] = True
    state["queue"] = queue.Queue()

    threading.Thread(
        target=reader_thread,
        args=(proc, state["queue"]),
        daemon=True
    ).start()


def safe_key(name):
    return re.sub(r"\W", "_", name)


def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for c in parent.children(recursive=True):
            c.kill()
        parent.kill()
    except:
        pass

def RenderTerminalAba(col1,altura, aba):
    # NO TOPO da função (ANTES de qualquer widget)
    state = get_aba_state(aba)
    prompt = get_prompt()

    with st.container(height=altura):
        st.code(state["buffer"], language="powershell")

    if col1.radio('Entrada:',['Digitar','Escolher']) == 'Digitar':

        cht_inpt, col_save, col_radio, info = st.columns([4.5, 0.6, 1.5, 1.3])
        # SEU CHAT_INPUT EXATO (INTACTO)
        cmd_input = cht_inpt.chat_input('Coloca em mim, vai',
            key=f"cmd_{safe_key(aba)}"
        )

        with col_save:
            if st.toggle("💾 Salva", key=f"save_{safe_key(aba)}"):
                with col_radio:
                    tabela = st.radio("rad", ["Módulos", "Diversos"], horizontal=True,
                                      key=f"tabela_{safe_key(aba)}", label_visibility='collapsed')

                    if tabela == "Módulos" and cmd_input:
                        if "pip install" in cmd_input.lower():
                            nome = cmd_input.split("pip install")[-1].strip().split()[0].split("-")[0]
                            uninstall = cmd_input.replace("pip install", "pip uninstall") + " -y"
                            upgrade = cmd_input.replace("pip install", "pip install --upgrade")
                            salvar_modulo(nome, cmd_input, uninstall, upgrade, "usuario")
                            info.success(f"💾 {nome} (3 versões) em Módulos!")
                        else:
                            info.error("❌ Só 'pip install' em Módulos!")
                    elif tabela == "Diversos" and cmd_input:
                        nome = cmd_input.split()[-1] if cmd_input.split() else "comando"
                        salvar_comando_diverso(nome, cmd_input)
                        info.success(f"📋 {nome} em Diversos!")

        # RESTO INTACTO
        if cmd_input:
            state["buffer"] += f"\n{prompt}{cmd_input}\n"
            start_command(aba, cmd_input)
            st.rerun()
    else:
        col_sel1, col_sel2, col_sel3, col_sel4, col_sel5,btn_sel = st.columns([1, 1, 1, 1, 1, 1])

        with col1:
            modulos = listar_modulos()
            diversos = listar_diversos()
            nomes_mod = [m["nome"] for m in modulos]
            nomes_div = diversos if diversos else []



            with col_sel1:
                nomes1 = ["📦 Instalar..."] + nomes_mod

                def install_callback():
                    if st.session_state[f"i_{safe_key(aba)}"] != "📦 Instalar...":
                        cmd = carregar_comando_modulo(st.session_state[f"i_{safe_key(aba)}"], "install")
                        st.session_state.cmd_temp = cmd

                st.selectbox(" ", nomes1, label_visibility="collapsed",
                             key=f"i_{safe_key(aba)}", on_change=install_callback)

            with col_sel2:
                nomes2 = ["🗑️ Desinstalar..."] + nomes_mod

                def uninstall_callback():
                    if st.session_state[f"u_{safe_key(aba)}"] != "🗑️ Desinstalar...":
                        cmd = carregar_comando_modulo(st.session_state[f"u_{safe_key(aba)}"], "uninstall")
                        st.session_state.cmd_temp = cmd

                st.selectbox(" ", nomes2, label_visibility="collapsed",
                             key=f"u_{safe_key(aba)}", on_change=uninstall_callback)

            with col_sel3:
                nomes3 = ["🔄 Upgrade..."] + nomes_mod

                def upgrade_callback():
                    if st.session_state[f"g_{safe_key(aba)}"] != "🔄 Upgrade...":
                        cmd = carregar_comando_modulo(st.session_state[f"g_{safe_key(aba)}"], "upgrade")
                        st.session_state.cmd_temp = cmd

                st.selectbox(" ", nomes3, label_visibility="collapsed",
                             key=f"g_{safe_key(aba)}", on_change=upgrade_callback)

            with col_sel4:
                nomes4 = ["📋 Diversos..."] + nomes_div

                def diversos_callback():
                    if st.session_state[f"d_{safe_key(aba)}"] != "📋 Diversos...":
                        cmd = carregar_diverso(st.session_state[f"d_{safe_key(aba)}"])
                        st.session_state[f"cmd_temp_{safe_key(aba)}"] = cmd
                        st.session_state.cmd_temp = cmd

                st.selectbox(" ", nomes4, label_visibility="collapsed",
                             key=f"d_{safe_key(aba)}", on_change=diversos_callback)


            with col_sel5:
                todos = nomes_mod + nomes_div
                nomes_delete = ["🗑️ Deletar..."] + todos
                mod_delete = st.selectbox(" ", nomes_delete, label_visibility="collapsed", key=f"del_{safe_key(aba)}")
                if mod_delete != "🗑️ Deletar...":
                    if st.button("❌", key=f"delbtn_{safe_key(aba)}"):
                        conn = sqlite3.connect("Banco_Dados_sudo_pip.db")
                        c = conn.cursor()
                        c.execute("DELETE FROM tabelas_modulos WHERE nome=?", (mod_delete,))
                        c.execute("DELETE FROM comandos_diversos WHERE nome=?", (mod_delete,))
                        conn.commit()
                        conn.close()
                        st.success(f"🗑️ {mod_delete} APAGADO!")
                        st.rerun()




            if btn_sel.button(st.session_state.cmd_temp,use_container_width=True):
                texto = st.session_state.cmd_temp
                st.session_state[f"cmd_input_{safe_key(aba)}2_enter"] = False
                state["buffer"] += f"\n{prompt}{texto}\n"
                start_command(aba, texto)
                st.rerun()



    if col1.button("🛑 **KILL ALL**", key=f"kill_{safe_key(aba)}"):
            if state["pid"]:
                kill_process_tree(state["pid"])
            state["running"] = False
            state["proc"] = None
            state["pid"] = None
            state["buffer"] += f"\n⛔ INTERRUPT\n{prompt}"
            st.rerun()

    if col1.button("🔥 **KILL GLOBAL**", key=f"killg_{safe_key(aba)}"):
            for s in st.session_state.terminal_abas.values():
                if s.get("pid"):
                    kill_process_tree(s["pid"])
                    s["running"] = False
                    s["proc"] = None
                    s["pid"] = None
            st.rerun()

    if col1.button("🗑️ Limpar", key=f"clear_{safe_key(aba)}"):
            state["buffer"] = prompt
            state["running"] = False
            state["proc"] = None
            state["pid"] = None
            st.rerun()

    if state["running"]:
        try:
            while True:
                line = state["queue"].get_nowait()
                if line is None:
                    state["running"] = False
                    state["proc"] = None
                    state["pid"] = None
                    state["buffer"] += f"\n✅ OK [{state['cmd']}] Terminou <\n{prompt}"
                    break
                else:
                    state["buffer"] += line
        except queue.Empty:
            pass
        sleep(0.01)
        st.rerun()


def Terminal():

    if "abas_terminal" not in st.session_state:
        st.session_state.abas_terminal = ["Terminal 1"]

    col1, col2 = st.columns([1, 15])
    with col1:
        altura = controlar_altura(st, "Terminal", altura_inicial=400, passo=200,maximo=600,minimo=200)

        if st.button("➕ Nova aba"):
            st.session_state.abas_terminal.append(
                f"Terminal {len(st.session_state.abas_terminal) + 1}"
            )
            st.rerun()

    with col2:
        tabs = st.tabs(st.session_state.abas_terminal)
        for i, aba in enumerate(st.session_state.abas_terminal):
            with tabs[i]:
                RenderTerminalAba(col1,altura,aba)
    with col1:
        if st.button("⚡ **KILL ALL PROJECT**"):
            for s in st.session_state.get("terminal_abas", {}).values():
                if s.get("pid"):
                    kill_process_tree(s["pid"])
                    s["running"] = False
                    s["proc"] = None
                    s["pid"] = None
            st.rerun()