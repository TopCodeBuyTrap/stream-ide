from pathlib import Path
import streamlit as st
from streamlit_ace import st_ace
import re
import subprocess
import threading
import queue

from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_


# ===== FIX WINDOWS: NÃO ABRIR CMD / POWERSHELL =====
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW


def get_prompt():
    try:
        Pasta_RAIZ_projeto = _DIRETORIO_PROJETO_ATUAL_()
        Pasta_RAIZ_projeto = Path(Pasta_RAIZ_projeto)

        venv_path = Pasta_RAIZ_projeto / ".virto_stream"
        venv_name = venv_path.name if venv_path.exists() else ""

        caminho_completo = str(Pasta_RAIZ_projeto)

        if venv_path.exists():
            prompt = f"({venv_name}) PS {caminho_completo}> "
        else:
            prompt = f"PS {caminho_completo}> "

        return prompt

    except Exception as e:
        return "PS ERRO> "


def executar_comando(cmd: str) -> str:
    try:
        Pasta_RAIZ_projeto = Path(_DIRETORIO_PROJETO_ATUAL_())
        venv_path = Pasta_RAIZ_projeto / ".virto_stream"
        activate_script = venv_path / "Scripts" / "Activate.ps1"

        if venv_path.exists():
            ps_cmd = [
                "powershell",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                (
                    "Remove-Module PSReadLine -ErrorAction SilentlyContinue; "
                    f"cd '{Pasta_RAIZ_projeto}'; "
                    f"& '{activate_script}'; "
                    f"{cmd}"
                )
            ]
        else:
            ps_cmd = [
                "powershell",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                f"Remove-Module PSReadLine -ErrorAction SilentlyContinue; cd '{Pasta_RAIZ_projeto}'; {cmd}"
            ]

        result = subprocess.run(
            ps_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            startupinfo=STARTUPINFO,
            creationflags=CREATE_FLAGS
        )

        saida = (result.stdout or "") + (result.stderr or "")
        resultado_final = saida
        return resultado_final

    except subprocess.TimeoutExpired:
        return "❌ Comando demorou demais (30s)"
    except Exception as e:
        return f"❌ Erro: {str(e)}"


def ultima_linha_nao_vazia(linhas):
    for l in reversed(linhas):
        if l.strip():
            return l
    return ""


def get_powershell_banner():
    try:
        proc = subprocess.Popen(
            ["powershell"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=STARTUPINFO,
            creationflags=CREATE_FLAGS
        )

        proc.stdin.write("exit\n")
        proc.stdin.flush()
        stdout, _ = proc.communicate()
        linhas = stdout.splitlines()
        banner = []
        for linha in linhas:
            if linha.strip().startswith("PS "):
                break
            banner.append(linha)
        return "\n".join(banner).strip()
    except Exception as e:
        return "PowerShell Banner"


def safe_key(name):
    return re.sub(r'\W', '_', name)


if "process_queues" not in st.session_state:
    st.session_state["process_queues"] = {}


def run_command_async(comando, aba_nome):
    if "process_queues" not in st.session_state:
        st.session_state["process_queues"] = {}

    def target(q):
        try:
            Pasta_RAIZ_projeto = Path(_DIRETORIO_PROJETO_ATUAL_())
            venv_python = Pasta_RAIZ_projeto / ".virto_stream" / "Scripts" / "python.exe"

            # 🚀 SE É PIP → USA PYTHON DA VENV!
            if comando.strip().startswith("pip"):
                novo_comando = f'"{venv_python}" -m pip ' + comando.split("pip", 1)[1]
            else:
                novo_comando = f'"{venv_python}" -c "{comando}"'

            process = subprocess.Popen(
                novo_comando,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                startupinfo=STARTUPINFO,
                creationflags=CREATE_FLAGS
            )

            for line in iter(process.stdout.readline, ''):
                q.put(line)
            process.stdout.close()
            process.wait()
            q.put(None)
        except Exception as e:
            q.put(f"Erro: {str(e)}\n")
            q.put(None)

    q = queue.Queue()
    st.session_state["process_queues"][aba_nome] = q
    thread = threading.Thread(target=target, args=(q,), daemon=True)
    thread.start()


@st.fragment(run_every=1.0)
def RenderTerminalAba(aba_nome, altura, THEMA_TERMINAL, TERMINAL_TAM_MENU):

    if "process_queues" not in st.session_state:
        st.session_state["process_queues"] = {}

    buff_k = f"buffer_{aba_nome}"
    rend_k = f"render_{aba_nome}"
    proc_k = f"running_{aba_nome}"

    if buff_k not in st.session_state:
        st.session_state[buff_k] = f"{get_powershell_banner()}\n\n{get_prompt()}"
    if rend_k not in st.session_state:
        st.session_state[rend_k] = st.session_state[buff_k]
    if proc_k not in st.session_state:
        st.session_state[proc_k] = False

    if st.session_state[proc_k] and aba_nome in st.session_state["process_queues"]:
        q = st.session_state["process_queues"][aba_nome]
        new_content = ""
        while not q.empty():
            line = q.get()
            if line is None:
                st.session_state[proc_k] = False
                new_content += f"\n{get_prompt()}"
                break
            new_content += line

        if new_content:
            st.session_state[buff_k] += new_content
            st.session_state[rend_k] = st.session_state[buff_k]

    # layout interno do fragmento: coluna do botão + coluna do terminal
    col_close, col_main = st.columns([1, 12])

    with col_close:
        if st.button(f"❌{aba_nome}", key=f"cls_{safe_key(aba_nome)}"):
            if "abas_terminal" in st.session_state and aba_nome in st.session_state.abas_terminal:
                st.session_state.abas_terminal.remove(aba_nome)
            st.rerun()

    with col_main:
        conteudo = st_ace(
            value=st.session_state[buff_k],
            language='kotlin',
            theme=THEMA_TERMINAL,
            height=altura + 10,
            font_size=TERMINAL_TAM_MENU,
            auto_update=True,
            wrap=True,
            show_gutter=False,
            show_print_margin=True,
            key=st.session_state[buff_k]  # mesma key do value, como você comentou
        )

        st.write("")

        if (not st.session_state[proc_k]) and conteudo and conteudo != st.session_state[rend_k]:
            if "\n" in conteudo[len(st.session_state[rend_k]):]:
                linhas = conteudo.splitlines()
                ultima = next((l for l in reversed(linhas) if l.strip()), "")
                prompt = get_prompt()

                if ultima.startswith(prompt):
                    cmd = ultima[len(prompt):].strip()
                    if cmd:
                        st.session_state[proc_k] = True
                        st.session_state[buff_k] = conteudo.rstrip() + "\n"
                        st.session_state[rend_k] = st.session_state[buff_k]
                        run_command_async(cmd, aba_nome)
                        st.rerun(scope="fragment")
                    else:
                        res = conteudo.rstrip() + f"\n{prompt}"
                        st.session_state[buff_k] = res
                        st.session_state[rend_k] = res
                        st.rerun(scope="fragment")
                else:
                    st.session_state[rend_k] = conteudo
            else:
                st.session_state[rend_k] = conteudo
def Terminal(altura, THEMA_TERMINAL, TERMINAL_TAM_MENU):
    if "process_queues" not in st.session_state:
        st.session_state["process_queues"] = {}
    if "abas_terminal" not in st.session_state:
        st.session_state.abas_terminal = ["Terminal 1"]
    if "contador_aba" not in st.session_state:
        st.session_state.contador_aba = 1

    t1, t2 = st.columns([1, 12])
    if t1.button("➕ Nova aba"):
        st.session_state.contador_aba += 1
        st.session_state.abas_terminal.append(f"Terminal {st.session_state.contador_aba}")
        st.rerun()

    with t2:
        tabs = st.tabs(st.session_state.abas_terminal)
        for idx, aba_nome in enumerate(st.session_state.abas_terminal):
            with tabs[idx]:
                # agora o fragmento não recebe mais t1
                RenderTerminalAba(aba_nome, altura, THEMA_TERMINAL, TERMINAL_TAM_MENU)
