"""
🚀 BANCO DE DADOS MÓDULOS - TERMINAL IDE
==================================================
ROLE: Fornece dados estruturados de módulos Python para o TERMINAL
USO: Importado exclusivamente pelo script TERMINAL.PY

FUNÇÕES EXPORTADAS para TERMINAL:
- listar_modulos() → retorna lista completa de módulos
- carregar_comando_modulo(nome, acao) → retorna comando específico
- salvar_comando_usuario(cmd) → salva comandos manuais como secundários
- salvar_modulo() → usado internamente no carregar_modulos_padrao()

INTEGRAÇÃO:
1. TERMINAL importa: from Banco_Dados_sudo_pip import *
2. TERMINAL chama: modulos = listar_modulos()
3. TERMINAL chama: cmd = carregar_comando_modulo("streamlit", "install")
4. EXECUÇÃO → start_command(aba, cmd)

BANCO: Banco_Dados_sudo_pip.db (SQLite independente)
TABELA: tabelas_modulos (nome, install_cmd, uninstall_cmd, upgrade_cmd, tipo)
"""

import sqlite3


def get_conn():
	return sqlite3.connect("Banco_Dados_sudo_pip.db", check_same_thread=False)


def init_db_modulos():
	conn = get_conn()
	c = conn.cursor()
	c.execute("""
    CREATE TABLE IF NOT EXISTS tabelas_modulos (
        nome TEXT PRIMARY KEY,
        install_cmd TEXT,
        uninstall_cmd TEXT,
        upgrade_cmd TEXT,
        tipo TEXT DEFAULT 'principal',
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
	c.execute("""
	CREATE TABLE IF NOT EXISTS comandos_diversos (
	    nome TEXT PRIMARY KEY,
	    comando TEXT,
	    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)
	""")

	conn.commit()
	c.close()
	conn.close()


def salvar_modulo(nome, install, uninstall, upgrade, tipo='principal'):
	conn = get_conn()
	c = conn.cursor()
	c.execute("""
    INSERT OR REPLACE INTO tabelas_modulos 
    (nome, install_cmd, uninstall_cmd, upgrade_cmd, tipo) 
    VALUES (?, ?, ?, ?, ?)
    """, (nome, install, uninstall, upgrade, tipo))
	conn.commit()
	c.close()
	conn.close()


def listar_modulos():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT nome, tipo FROM tabelas_modulos ORDER BY nome")
	modulos = [{"nome": r[0], "tipo": r[1]} for r in c.fetchall()]
	c.close()
	conn.close()
	return modulos


def carregar_comando_modulo(nome_modulo, acao):
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT {}_cmd FROM tabelas_modulos WHERE nome=?".format(acao), (nome_modulo,))
	resultado = c.fetchone()
	c.close()
	conn.close()
	return resultado[0] if resultado else None


def salvar_comando_usuario(comando):
	conn = get_conn()
	c = conn.cursor()
	nome_modulo = comando.split()[0] if comando.split() else "comando_custom"
	tipo = 'secundario'
	c.execute("""
    INSERT OR IGNORE INTO tabelas_modulos 
    (nome, install_cmd, tipo) VALUES (?, ?, ?)
    """, (nome_modulo, comando, tipo))
	conn.commit()
	c.close()
	conn.close()


# ===========================================
# PRE-CARREGA MÓDULOS PRINCIPAIS
# ===========================================
# ===========================================
# PRE-CARREGA MÓDULOS PRINCIPAIS
# ===========================================
def carregar_modulos_padrao():
	modulos = {

		# --- CORE PYTHON ---
		"pip": {
			"install": "python -m pip install --upgrade pip",
			"uninstall": "",
			"upgrade": "python -m pip install --upgrade pip"
		},
		"setuptools": {
			"install": "pip install setuptools",
			"uninstall": "pip uninstall setuptools -y",
			"upgrade": "pip install --upgrade setuptools"
		},
		"wheel": {
			"install": "pip install wheel",
			"uninstall": "pip uninstall wheel -y",
			"upgrade": "pip install --upgrade wheel"
		},

		# --- BASE CIENTÍFICO ---
		"numpy": {
			"install": "pip install numpy",
			"uninstall": "pip uninstall numpy -y",
			"upgrade": "pip install --upgrade numpy"
		},
		"pandas": {
			"install": "pip install pandas",
			"uninstall": "pip uninstall pandas -y",
			"upgrade": "pip install --upgrade pandas"
		},
		"scipy": {
			"install": "pip install scipy",
			"uninstall": "pip uninstall scipy -y",
			"upgrade": "pip install --upgrade scipy"
		},

		# --- STREAMLIT CORE ---
		"streamlit-web": {
			"install": "pip install streamlit",
			"uninstall": "pip uninstall streamlit -y",
			"upgrade": "pip install --upgrade streamlit"
		},
		"streamlit-desktop": {
			"install": "pip install streamlit-desktop-app",
			"uninstall": "pip uninstall streamlit-desktop-app -y",
			"upgrade": "pip install --upgrade streamlit-desktop-app"
		},
		"streamlit-option-menu": {
			"install": "pip install streamlit-option-menu",
			"uninstall": "pip uninstall streamlit-option-menu -y",
			"upgrade": "pip install --upgrade streamlit-option-menu"
		},
		"streamlit-aggrid": {
			"install": "pip install streamlit-aggrid",
			"uninstall": "pip uninstall streamlit-aggrid -y",
			"upgrade": "pip install --upgrade streamlit-aggrid"
		},
		"streamlit-extras": {
			"install": "pip install streamlit-extras",
			"uninstall": "pip uninstall streamlit-extras -y",
			"upgrade": "pip install --upgrade streamlit-extras"
		},

		# --- GRÁFICOS ---
		"matplotlib": {
			"install": "pip install matplotlib",
			"uninstall": "pip uninstall matplotlib -y",
			"upgrade": "pip install --upgrade matplotlib"
		},
		"seaborn": {
			"install": "pip install seaborn",
			"uninstall": "pip uninstall seaborn -y",
			"upgrade": "pip install --upgrade seaborn"
		},
		"plotly": {
			"install": "pip install plotly",
			"uninstall": "pip uninstall plotly -y",
			"upgrade": "pip install --upgrade plotly"
		},
		"altair": {
			"install": "pip install altair",
			"uninstall": "pip uninstall altair -y",
			"upgrade": "pip install --upgrade altair"
		},

		# --- UTILIDADES ---
		"requests": {
			"install": "pip install requests",
			"uninstall": "pip uninstall requests -y",
			"upgrade": "pip install --upgrade requests"
		},
		"python-dotenv": {
			"install": "pip install python-dotenv",
			"uninstall": "pip uninstall python-dotenv -y",
			"upgrade": "pip install --upgrade python-dotenv"
		},
		"rich": {
			"install": "pip install rich",
			"uninstall": "pip uninstall rich -y",
			"upgrade": "pip install --upgrade rich"
		}
	}

	for nome, cmds in modulos.items():
		salvar_modulo(
			nome,
			cmds["install"],
			cmds["uninstall"],
			cmds["upgrade"]
		)



def salvar_comando_diverso(nome, comando):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO comandos_diversos (nome, comando) VALUES (?, ?)",
              (nome, comando))
    conn.commit()
    c.close()
    conn.close()

def listar_diversos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nome FROM comandos_diversos ORDER BY nome")
    nomes = [r[0] for r in c.fetchall()]
    c.close()
    conn.close()
    return nomes

def carregar_diverso(nome):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT comando FROM comandos_diversos WHERE nome=?", (nome,))
    result = c.fetchone()
    c.close()
    conn.close()
    return result[0] if result else None

def deletar_diverso(nome):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM comandos_diversos WHERE nome=?", (nome,))
    conn.commit()
    c.close()
    conn.close()


# INICIALIZAÇÃO
init_db_modulos()
carregar_modulos_padrao()

