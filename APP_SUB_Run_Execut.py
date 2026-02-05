from pathlib import Path
import subprocess
import re, os, sys
from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO

STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = subprocess.SW_HIDE
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW

# ================================================================================EXECUTA COM SUBPROCESS PARA STREAMLIT=====


def netstat_streamlit():
    """Parse CORRETO com encoding BR e PID no final"""
    portas_85xx = []

    resultado = subprocess.run(
        'netstat -ano',
        shell=True, capture_output=True, text=True,
        encoding='cp850',  # ← ENCODING BRASILEIRO!
        startupinfo=STARTUPINFO,
        creationflags=CREATE_FLAGS

    )

    for linha in resultado.stdout.splitlines():
        if 'LISTENING' in linha and '850' in linha:
            # Pega campos: Proto Endereço PID no FINAL
            parts = linha.split()
            if len(parts) >= 5:
                pid = parts[-1]  # Último = PID
                # Regex pega porta 850x
                match = re.search(r'0\.0\.0\.0:(\d{4})', linha)
                if match:
                    porta = match.group(1)
                    portas_85xx.append((porta, pid, linha.strip()))

    return portas_85xx


# ===== DETECTA SE É CÓDIGO STREAMLIT =====
def is_streamlit_code(code):
    code_lower = code.lower()
    return 'import streamlit' in code_lower or 'import st' in code_lower or 'st.' in code_lower

# ===== EXECUTA COM SUBPROCESS PARA STREAMLIT =====
def run_streamlit_process(file_path):
    python_exe, root_path, _, _ = VENVE_DO_PROJETO()
    cmd = [python_exe, "-m", "streamlit", "run", str(file_path)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1, cwd=root_path,         startupinfo=STARTUPINFO,
    creationflags=CREATE_FLAGS)
    return process


# ================================================================================EXECUTA COM SUBPROCESS PARA FLEX =====
def is_flask_code(code):
    """Detecta se código tem Flask (igual is_streamlit_code)"""
    if not code:
        return False
    flask_indicators = [
        "from flask import",
        "app = Flask(",
        "Flask(__name__)",
        "@app.route",
        "app.run("
    ]
    code_lower = code.lower()
    return any(indicator in code_lower for indicator in flask_indicators)

def extract_flask_config(code):
    """Extrai configurações de app.run() do código Flask"""
    import re

    # Padrões para capturar app.run(port=..., host=..., debug=...)
    port_pattern = r'app\.run\s*\(\s*(?:[^)]*port\s*=\s*([0-9]+)[^)]*)'
    host_pattern = r'app\.run\s*\(\s*(?:[^)]*host\s*=\s*["\']([^"\']+)["\'][^)]*)'
    debug_pattern = r'app\.run\s*\(\s*(?:[^)]*debug\s*=\s*(True|False)[^)]*)'

    porta = None
    host = None
    debug = None

    # Busca porta
    port_match = re.search(port_pattern, code, re.IGNORECASE | re.DOTALL)
    if port_match:
        porta = int(port_match.group(1))

    # Busca host
    host_match = re.search(host_pattern, code, re.IGNORECASE | re.DOTALL)
    if host_match:
        host = host_match.group(1)

    # Busca debug
    debug_match = re.search(debug_pattern, code, re.IGNORECASE | re.DOTALL)
    if debug_match:
        debug = debug_match.group(1).lower() == 'true'

    return {
        'port': porta,
        'host': host or '127.0.0.1',
        'debug': debug
    }

def stop_flex(porta):
    """Retorna lista de PIDs usando a porta informada no Windows"""
    try:
        # extrair apenas números da porta
        porta_num = re.findall(r'\d+', str(porta))[0]

        # roda netstat sem quebrar se não houver resultado
        result = subprocess.run(
            f'netstat -ano | findstr :{porta_num}',
            shell=True, capture_output=True, text=True
        )

        if not result.stdout.strip():  # nenhum processo encontrado
            return []

        # extrair todos os PIDs da saída
        pids = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and pid not in pids:
                    pids.append(pid)
        return pids

    except Exception as e:
        print(f"Erro ao buscar PID da porta {porta}: {e}", file=sys.stderr)
        return []


def netstat_flex():  # ou netstat_all()
    portas_flex = []
    try:
        resultado = subprocess.run(
            'netstat -ano | findstr LISTENING',
            shell=True, capture_output=True, text=True
        )
        for linha in resultado.stdout.split('\n'):
            if any(palavra in linha.lower() for palavra in ['flex', 'node', 'python']):
                partes = linha.split()
                if len(partes) >= 5:
                    porta = partes[1].split(':')[-1]
                    pid = partes[-1]
                    portas_flex.append((porta, pid, linha))
    except:
        pass
    return portas_flex


def find_port_by_pid(pid):
    """Encontra porta do processo pelo PID usando netstat"""
    portas = netstat_flex()
    for porta, process_pid, _ in portas:
        if process_pid == str(pid):
            return porta
    return None


def run_flex_process(file_path):
    python_exe, root_path, _, _ = VENVE_DO_PROJETO()
    module_name = Path(file_path).stem
    cmd = [python_exe, "-m", module_name]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=root_path,
        startupinfo=STARTUPINFO,
        creationflags=CREATE_FLAGS
    )
    return process

# ================================================================================EXECUTA COM SUBPROCESS PARA DJANGO =====


# ===============================
# Funções de detecção e configuração
# ===============================

def is_django_code(code):
    """Detecta se o código inicializa um servidor Django"""
    if not code:
        return False
    code_lower = code.lower()
    # detecta se chama execute_from_command_line com runserver
    return "execute_from_command_line" in code_lower and "runserver" in code_lower or "manage.py runserver" in code_lower


def extract_django_config(code):
    """Extrai host e porta do comando manage.py runserver"""
    porta = None
    host = "127.0.0.1"

    match = re.search(r'manage\.py\s+runserver\s+([\d\.]*):?(\d+)?', code, re.IGNORECASE)
    if match:
        host_found = match.group(1)
        porta_found = match.group(2)
        if host_found:
            host = host_found
        if porta_found:
            porta = int(porta_found)
    else:
        porta = 8000  # default Django
        host = "127.0.0.1"

    return {
        "port": porta,
        "host": host
    }


# ===============================
# Funções para parar processo via porta
# ===============================

def stop_process_by_port(porta):
    """Retorna lista de PIDs usando a porta informada no Windows"""
    try:
        porta_num = re.findall(r'\d+', str(porta))[0]
        result = subprocess.run(
            f'netstat -ano | findstr :{porta_num}',
            shell=True, capture_output=True, text=True
        )
        if not result.stdout.strip():
            return []

        pids = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and pid not in pids:
                    pids.append(pid)
        return pids
    except Exception as e:
        print(f"Erro ao buscar PID da porta {porta}: {e}", file=sys.stderr)
        return []


# ===============================
# Fluxo Streamlit para Django
# ===============================


