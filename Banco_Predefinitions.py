import json
import sqlite3


def get_conn():
	"""Retorna CONEXÃO PRONTA (padrão correto)"""
	return sqlite3.connect("Base_Dados_PreDefinidos.db", check_same_thread=False)


def init_db():
	"""Cria TODAS as tabelas de uma vez"""
	conn = get_conn()
	c = conn.cursor()

	# Tabela templates
	c.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            arquivos TEXT
        )
    """)

	# Tabela config_layout
	c.execute("""
        CREATE TABLE IF NOT EXISTS config_layout (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            containers_order TEXT,
            layout INTEGER,
            height_mode TEXT,
            col_weights TEXT,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

	conn.commit()
	c.close()
	conn.close()


# ===========================================
# TEMPLATES - CONSISTENTES com get_conn()
# ===========================================
def salvar_template(nome, arquivos):
	conn = get_conn()
	c = conn.cursor()
	c.execute(
		"INSERT OR REPLACE INTO templates (nome, arquivos) VALUES (?, ?)",
		(nome, json.dumps(arquivos, ensure_ascii=False))
	)
	conn.commit()
	c.close()
	conn.close()


def listar_templates():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT nome FROM templates")
	nomes = [i[0] for i in c.fetchall()]
	c.close()
	conn.close()
	return nomes


def carregar_template(nome):
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT arquivos FROM templates WHERE nome=?", (nome,))
	row = c.fetchone()
	c.close()
	conn.close()
	return json.loads(row[0]) if row else []


# ===========================================
# CONFIG LAYOUT - CONSISTENTES com get_conn()
# ===========================================
def salvar_config_atual(containers_order, layout, height_mode, col_weights):
	"""Salva configuração atual (SUBSTITUI sempre)"""
	conn = get_conn()
	c = conn.cursor()
	c.execute("""
        INSERT OR REPLACE INTO config_layout 
        (containers_order, layout, height_mode, col_weights) 
        VALUES (?, ?, ?, ?)
    """, (
		json.dumps(containers_order, ensure_ascii=False),
		int(layout),
		str(height_mode),
		json.dumps(col_weights) if col_weights else None
	))
	conn.commit()
	c.close()
	conn.close()


def carregar_config_atual():
	"""Carrega última configuração salva (com validação)"""
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM config_layout ORDER BY id DESC LIMIT 1")
	row = c.fetchone()
	c.close()
	conn.close()

	if row:
		try:
			col_weights = json.loads(row[4]) if row[4] else None
			return {
				'containers_order': json.loads(row[1]) if row[1] else [],
				'layout': int(row[2]) if row[2] else 1,
				'height_mode': row[3] if row[3] else "medio",
				'col_weights': col_weights
			}
		except (json.JSONDecodeError, ValueError):
			return None
	return None


# Inicializa banco
init_db()
