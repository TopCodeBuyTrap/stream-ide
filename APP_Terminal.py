"""🔗 LIGAÇÃO BANCO ↔ TERMINAL (Fluxo Completo ATUALIZADO):

1. BANCO já inicializado: init_db_modulos() + carregar_modulos_padrao()

2. Terminal chama:
   - modulos = listar_modulos() → preenche selectbox Instalar/Upgrade/Desinstalar
   - divs = listar_diversos() → preenche selectbox Diversos

3. Usuário seleciona:
   - "streamlit" + "Instalar" → carregar_comando_modulo("streamstreamlit", "install")
   - "flask" + "Desinstalar" → carregar_comando_modulo("flask", "uninstall")
   - "git" + "Upgrade" → carregar_comando_modulo("git", "upgrade")
   - "Diversos: pytest" → carregar_diverso("pytest")

4. Botão EXECUTAR → start_command(aba, cmd_banco) → EXECUTA

5. Comando manual digitado → start_command(aba, cmd_usuario)

6. **NOVO: Auto-aprendizado** → salvar_comando_usuario(cmd) → BANCO aprende novos padrões

7. **Processos persistentes**:
   - Detecta servidor ativo (streamlit run, flask run, etc)
   - "🚀 SERVIDOR ATIVO" após 10s sem output
   - Botões 🛑 PARAR / 🧹 LIMPAR matam taskkill /F

DEPENDÊNCIAS:
- Banco_Dados_sudo_pip.py DEVE existir no mesmo diretório
- init_db_modulos() + carregar_modulos_padrao() executados no import
- Tabelas: 'tabelas_modulos' + histórico comandos

FLUXO BIDIRECIONAL:
Terminal → Banco: salvar_comando_usuario() (aprendizado)
Banco → Terminal: listar_modulos() + carregar_comando_modulo() + listar_diversos()

ISOLAMENTO VENV .virto_stream:
- _PYTHON_EXE = .virto_stream\Scripts\python.exe (SEMPRE)
- cwd=_ROOT_PATH (pasta projeto)
- pip/python/streamlit → [_PYTHON_EXE, -m, modulo, args...]
- flask/uvicorn/npm/git → executa direto Scripts\ (PATH venv)

COMANDOS SUPORTADOS:
✅ pip install/uninstall/upgrade/list/show
✅ streamlit run app.py → localhost:8501
✅ python server.py → qualquer servidor
✅ flask run → localhost:5000
✅ uvicorn main:app → localhost:8000
✅ npm start / ng serve / git clone / pytest
✅ QUALQUER comando shell

ESTADO POR ABA:
- session_state.terminal_abas[aba_name] = {buffer, queue, proc, pid, running, cmd, silencioso_count}
- Fragment isolado @st.fragment(run_every=0.2)
- kill_process_tree() + taskkill /F (Windows-proof)

BOTÕES:
🛑 PARAR: mata processo atual + restaura prompt
🧹 LIMPAR: mata + limpa buffer
💥 PARAR TUDO: mata todas abas + restaura prompts

ARQUITETURA:
- ZERO PowerShell (lista subprocess pura)
- 100% shlex.parse → cmd → lista Python
- cwd=_ROOT_PATH sempre
- Fragment performance otimizada
"""
import streamlit as st
import subprocess
import threading
import queue
import re
import psutil

from APP_SUB_Funcitons import controlar_altura
from Banco_dados import *
from APP_SUB_Controle_Driretorios import (
    VENVE_DO_PROJETO
)

STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW




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


import shlex


def normalize_command(cmd: str) -> list:
    """Parseia comando → lista Python PURA. SEM PowerShell."""
    cmd_parts = shlex.split(cmd)

    # pip → [python_virto, -m, pip, args...]
    if cmd_parts[0] in ["pip"]:
        return [_PYTHON_EXE, "-m", "pip"] + cmd_parts[1:]

    # python → [python_virto, args...]
    if cmd_parts[0] in ["python"]:
        return [_PYTHON_EXE] + cmd_parts[1:]

    # streamlit → [python_virto, -m, streamlit, args...]
    if cmd_parts[0] in ["streamlit"]:
        return [_PYTHON_EXE, "-m", "streamlit"] + cmd_parts[1:]

    # TUDO OUTRO → executa direto (flask, uvicorn, npm, git, etc)
    return cmd_parts


def start_command(col1,aba, cmd):

        state = get_aba_state(aba)
        if state["running"]:
                return

        # TRANSFORMA EM LISTA PYTHON PURA (SEU MÉTODO)
        cmd_list = normalize_command(cmd)

        proc = subprocess.Popen(
            cmd_list,  # <- LISTA DIRETA, SEM POWERSHELL
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            cwd=_ROOT_PATH,  # <- DIRETÓRIO DO PROJETO
            startupinfo=STARTUPINFO,
            creationflags=CREATE_FLAGS
        )

        state["proc"] = proc
        state["pid"] = proc.pid
        state["cmd"] = cmd
        state["running"] = True
        state["silencioso_count"] = 0
        state["queue"] = queue.Queue()

        threading.Thread(target=reader_thread, args=(proc, state["queue"]), daemon=True).start()


def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for c in parent.children(recursive=True):
            c.kill()
        parent.kill()
    except Exception:
        pass


@st.fragment(run_every=0.1)
def terminal_fragment(aba,altura):
    state = get_aba_state(aba)
    if not state["running"]:
        st.code(state["buffer"], language="powershell",height=altura)
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
            state["buffer"] += f"\nCONCLUIDO: {state['cmd']}\n{"-"*150}_TcbT_\n\n{_PROMPT}"
            break
        print('henriq')
        print('ola mundo DE CIMA 2')

        state["buffer"] += line

    st.code(state["buffer"], language="powershell")


def RenderTerminalAba(col1,input_mode, altura, aba, aba_index=0):
    state = get_aba_state(aba)
    with st.container(height=altura):
        terminal_fragment(aba,altura)

    if input_mode == "Digitar":
        cht_inpt, col_save, col_radio, info = st.columns([4.5, 0.6, 1.5, 1.3])

        cmd = cht_inpt.chat_input(
            "Digite o comando",
            key=f"cmd_{aba_index}_{safe_key(aba)}"
        )

        with col_save:
            save_toggle = st.toggle("💾 Salva", key=f"save_{aba_index}_{safe_key(aba)}")
            with col_radio:
                if save_toggle:
                    tabela = st.radio("rad", ["Módulos", "Diversos"], horizontal=True,
                                      key=f"tabela_radio_{aba_index}_{safe_key(aba)}",  # ← KEY ÚNICA
                                          label_visibility='collapsed')
                    if cmd:
                        if tabela == "Módulos" and "pip install" in cmd.lower():
                            nome = cmd.split("pip install")[-1].strip().split()[0].split("-")[0]
                            uninstall = cmd.replace("pip install", "pip uninstall") + " -y"
                            upgrade = cmd.replace("pip install", "pip install --upgrade")
                            salvar_modulo(nome, cmd, uninstall, upgrade, "usuario")
                            info.success(f"💾 {nome} (3 versões) em Módulos!")
                        elif tabela == "Diversos":
                            nome = cmd.split()[-1] if cmd.split() else "comando"
                            salvar_comando_diverso(nome, cmd)
                            info.success(f"📋 {nome} em Diversos!")
                        else:
                            info.error("❌ Só 'pip install' em Módulos!")
        if cmd:
            state["buffer"] += f"\n{_PROMPT}{cmd}\n"
            start_command(col1,aba, cmd)
            st.stop()

    else:
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

            if st.button("❌", key=f"delete_btn_{aba_index}_{safe_key(aba)}",type='secondary'):
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
                state["buffer"] += f"\n{_PROMPT}{texto}\n"
                start_command(col1,aba, texto)
                st.rerun()

    col1_btn, col2_btn, col3_btn = st.columns(3)

    if col1_btn.button("PARAR", key=f"kill_{aba_index}_{safe_key(aba)}"):
        if state["pid"]:
            kill_process_tree(state["pid"])
        state["running"] = False
        state["proc"] = None
        state["pid"] = None
        state["buffer"] += f"\nINTERROMPIDO\n{"-"*150}_TcbT_\n\n{_PROMPT}"

    if col2_btn.button("LIMPAR", key=f"clear_{aba_index}_{safe_key(aba)}"):
        state["buffer"] = _PROMPT
        state["running"] = False
        state["proc"] = None
        state["pid"] = None

    if col3_btn.button("PARAR TUDO", key=f"kill_all_{aba_index}_{safe_key(aba)}"):
        for s in st.session_state.terminal_abas.values():
            if s.get("pid"):
                kill_process_tree(s["pid"])
                s["running"] = False
                s["proc"] = None
                s["pid"] = None

    st.write('')
    st.write('.')
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
                with col1.spinner('processos...'):
                    RenderTerminalAba(col1,input_mode, altura, aba, aba_index=i)
