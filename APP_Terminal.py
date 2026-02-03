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

    full_cmd = f"$OutputEncoding=[console]::OutputEncoding=New-Object System.Text.UTF8Encoding; cd '{root}'; {cmd}"

    # *** DETECTA COMANDOS RÁPIDOS vs SERVIDORES ***
    comandos_rapidos = ["pip list", "pip show", "dir", "ls", "python -c"]
    is_comando_rapido = any(cmd.startswith(c) for c in comandos_rapidos)

    if is_comando_rapido:
        # *** RÁPIDO: subprocess.run() = lista completa ***
        resultado = subprocess.run(
            ["powershell", "-NoLogo", "-NoProfile", "-Command", full_cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )
        state["output_completo"] = resultado.stdout.splitlines()
        state["return_code"] = resultado.returncode
        state["running"] = True
        state["linha_atual"] = 0
    else:
        # *** SERVIDOR: subprocess.Popen() = thread original ***
        proc = subprocess.Popen(
            ["powershell", "-NoLogo", "-NoProfile", "-Command", full_cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            bufsize=1, encoding="utf-8", errors="replace", startupinfo=STARTUPINFO
        )
        state["proc"] = proc
        state["pid"] = proc.pid
        state["cmd"] = cmd
        state["running"] = True
        state["queue"] = queue.Queue()

        threading.Thread(target=reader_thread, args=(proc, state["queue"]), daemon=True).start()


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


def RenderTerminalAba(input_mode,altura, aba, aba_index=0):  # ← ADICIONEI aba_index
    state = get_aba_state(aba)
    prompt = get_prompt()



    with st.container(height=altura):
        st.code(state["buffer"], language="powershell")

    if input_mode == 'Digitar':
        # MODO DIGITAR (INTACTO, só keys corrigidas)
        cht_inpt, col_save, col_radio, info = st.columns([4.5, 0.6, 1.5, 1.3])
        cmd_input = cht_inpt.chat_input('Coloca em mim, vai',
                                        key=f"cmd_input_{aba_index}_{safe_key(aba)}")  # ← KEY ÚNICA

        with col_save:
            save_toggle = st.toggle("💾 Salva", key=f"save_{aba_index}_{safe_key(aba)}")
            if save_toggle and cmd_input:
                with col_radio:
                    tabela = st.radio("rad", ["Módulos", "Diversos"], horizontal=True,
                                      key=f"tabela_radio_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                                      label_visibility='collapsed')

                    if tabela == "Módulos" and "pip install" in cmd_input.lower():
                        nome = cmd_input.split("pip install")[-1].strip().split()[0].split("-")[0]
                        uninstall = cmd_input.replace("pip install", "pip uninstall") + " -y"
                        upgrade = cmd_input.replace("pip install", "pip install --upgrade")
                        salvar_modulo(nome, cmd_input, uninstall, upgrade, "usuario")
                        info.success(f"💾 {nome} (3 versões) em Módulos!")
                    elif tabela == "Diversos":
                        nome = cmd_input.split()[-1] if cmd_input.split() else "comando"
                        salvar_comando_diverso(nome, cmd_input)
                        info.success(f"📋 {nome} em Diversos!")
                    else:
                        info.error("❌ Só 'pip install' em Módulos!")

        if cmd_input:
            state["buffer"] += f"\n{prompt}{cmd_input}\n"
            start_command(aba, cmd_input)
            st.rerun()

    else:  # MODO ESCOLHER
        # Colunas para SELECTBOXES com keys únicas
        col_sel1, col_sel2, col_sel3, col_sel4, col_sel5, col_btn = st.columns([1, 1, 1, 1, 1, 1])

        with col_sel1:
            modulos = listar_modulos()
            nomes_mod = [m["nome"] for m in modulos]
            nomes1 = ["📦 Instalar..."] + nomes_mod

            def install_callback():
                selected = st.session_state[f"install_sel_{aba_index}_{safe_key(aba)}"]
                if selected != "📦 Instalar...":
                    cmd = carregar_comando_modulo(selected, "install")
                    st.session_state.cmd_temp = cmd

            st.selectbox(" ", nomes1, label_visibility="collapsed",
                         key=f"install_sel_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                         on_change=install_callback)

        with col_sel2:
            nomes2 = ["🗑️ Desinstalar..."] + nomes_mod

            def uninstall_callback():
                selected = st.session_state[f"uninstall_sel_{aba_index}_{safe_key(aba)}"]
                if selected != "🗑️ Desinstalar...":
                    cmd = carregar_comando_modulo(selected, "uninstall")
                    st.session_state.cmd_temp = cmd

            st.selectbox(" ", nomes2, label_visibility="collapsed",
                         key=f"uninstall_sel_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                         on_change=uninstall_callback)

        with col_sel3:
            nomes3 = ["🔄 Upgrade..."] + nomes_mod

            def upgrade_callback():
                selected = st.session_state[f"upgrade_sel_{aba_index}_{safe_key(aba)}"]
                if selected != "🔄 Upgrade...":
                    cmd = carregar_comando_modulo(selected, "upgrade")
                    st.session_state.cmd_temp = cmd

            st.selectbox(" ", nomes3, label_visibility="collapsed",
                         key=f"upgrade_sel_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                         on_change=upgrade_callback)

        with col_sel4:
            diversos = listar_diversos()
            nomes_div = diversos if diversos else []
            nomes4 = ["📋 Diversos..."] + nomes_div

            def diversos_callback():
                selected = st.session_state[f"diversos_sel_{aba_index}_{safe_key(aba)}"]
                if selected != "📋 Diversos...":
                    cmd = carregar_diverso(selected)
                    st.session_state[f"cmd_temp_{safe_key(aba)}"] = cmd
                    st.session_state.cmd_temp = cmd

            st.selectbox(" ", nomes4, label_visibility="collapsed",
                         key=f"diversos_sel_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                         on_change=diversos_callback)

        with col_sel5:
            todos = nomes_mod + nomes_div
            nomes_delete = ["🗑️ Deletar..."] + todos
            mod_delete = st.selectbox(" ", nomes_delete, label_visibility="collapsed",
                                      key=f"delete_sel_{aba_index}_{safe_key(aba)}")  # ← KEY ÚNICA

            if st.button("❌", key=f"delete_btn_{aba_index}_{safe_key(aba)}"):
                if mod_delete != "🗑️ Deletar...":
                    conn = sqlite3.connect("Banco_Dados_sudo_pip.db")
                    c = conn.cursor()
                    c.execute("DELETE FROM tabelas_modulos WHERE nome=?", (mod_delete,))
                    c.execute("DELETE FROM comandos_diversos WHERE nome=?", (mod_delete,))
                    conn.commit()
                    conn.close()
                    st.success(f"🗑️ {mod_delete} APAGADO!")
                    st.rerun()

        # Botão EXECUTAR com key única
        if 'cmd_temp' in st.session_state and st.session_state.cmd_temp:
            if col_btn.button(st.session_state.cmd_temp, width='stretch',
                              key=f"exec_btn_{aba_index}_{safe_key(aba)}"):  # ← KEY ÚNICA
                texto = st.session_state.cmd_temp
                state["buffer"] += f"\n{prompt}{texto}\n"
                start_command(aba, texto)
                st.rerun()

    # BOTÕES DE CONTROLE (keys únicas)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    if col1.button("🛑 **PARAR ATUAL**", key=f"kill_all_{aba_index}_{safe_key(aba)}"):
        if state["pid"]:
            kill_process_tree(state["pid"])
        state["running"] = False
        state["proc"] = None
        state["pid"] = None
        state["buffer"] += f"\n⛔ INTERRUPT\n{prompt}"
        st.rerun()

    if col2.button("🔥 **PARAR TODO PROJETO**", key=f"kill_global_{aba_index}_{safe_key(aba)}"):
        for s in st.session_state.terminal_abas.values():
            if s.get("pid"):
                kill_process_tree(s["pid"])
                s["running"] = False
                s["proc"] = None
                s["pid"] = None
        st.rerun()

    if col3.button("🗑️ Limpar", key=f"clear_{aba_index}_{safe_key(aba)}"):
        state["buffer"] = prompt
        state["running"] = False
        state["proc"] = None
        state["pid"] = None
        st.rerun()

    # NO FINAL da RenderTerminalAba()
    prompt = get_prompt()

    # *** MODO LISTA (comandos rápidos) ***
    if "output_completo" in state and state["running"]:
        while state["linha_atual"] < len(state["output_completo"]):
            linha = state["output_completo"][state["linha_atual"]]
            state["buffer"] += linha + "\n"
            state["linha_atual"] += 3
            st.rerun()

        # *** ACABOU LISTA ***
        state["running"] = False
        state["buffer"] += f"\n✅ [{state['cmd'][:40]}...] CONCLUÍDO\n{prompt}"
        st.rerun()

    # *** MODO THREAD (servidores) ***
    elif state["running"] and state.get("proc"):
        new_lines = 0
        while True:
            try:
                line = state["queue"].get_nowait()
                if line is None: break
                state["buffer"] += line
                new_lines += 1
            except queue.Empty:
                break

        # *** SERIDOR: para depois de 10s silêncio ***
        if new_lines == 0 and hasattr(state, 'silencioso_count'):
            state['silencioso_count'] += 1
            if state['silencioso_count'] > 100:
                state["running"] = False
                state["buffer"] += f"\n🚀 [{state['cmd'][:40]}...] SERVIDOR ATIVO\n{prompt}"
        else:
            state['silencioso_count'] = 0

        if new_lines > 0:
            st.rerun()

    sleep(0.02)  # ← SEMPRE NO FINAL


def Terminal():
    if "abas_terminal" not in st.session_state:
        st.session_state.abas_terminal = ["Terminal 1"]

    col1, col2 = st.columns([1, 15])
    with col1:
        altura = controlar_altura(st, "Terminal", altura_inicial=400, passo=200, maximo=600, minimo=200)

        if st.button("➕ Nova aba", key="nova_aba_btn"):
            st.session_state.abas_terminal.append(
                f"Terminal {len(st.session_state.abas_terminal) + 1}"
            )
            st.rerun()
        # Key ÚNICA para RADIO principal (fora das colunas internas)
        input_mode = st.radio('Entrada:', ['Digitar', 'Escolher'])  # ← KEY ÚNICA
    with col2:
        tabs = st.tabs(st.session_state.abas_terminal)
        for i, aba in enumerate(st.session_state.abas_terminal):
            with tabs[i]:
                RenderTerminalAba(input_mode,altura, aba, aba_index=i)  # ← PASSA O ÍNDICE!
            st.write('')
            st.write('')
