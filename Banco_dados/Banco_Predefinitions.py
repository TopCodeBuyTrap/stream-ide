import json
import sqlite3
import streamlit as st


def get_conn():
    """Retorna CONEXÃO PRONTA (padrão correto)"""
    return sqlite3.connect("Banco_dados/Base_Dados_PreDefinidos.db", check_same_thread=False)

@st.cache_data
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
    """Cria tabela de versões"""
    c.execute("""
        CREATE TABLE IF NOT EXISTS versoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            data_instalacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            info_extra TEXT
        )
    """)
    c.execute('''CREATE TABLE IF NOT EXISTS BACKUP(
        DATA TEXT PRIMARY KEY NOT NULL,
        HORAS_INICIO  TIME,
        HORAS_ATUALIZOU TIME,
        QTDS_HORAS_ATUALIZOU INTEGER,
        QTDS_BACKUP INTEGER,
        OBS TEXT)''')

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



def salvar_versao(nome, info_extra=None):
    """Salva nova versão ou atualiza info_extra se já existir"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO versoes (nome, info_extra)
        VALUES (?, ?)
    """, (nome, info_extra))
    conn.commit()
    c.close()
    conn.close()


def listar_versoes():
    """Retorna lista de nomes de versões"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nome FROM versoes ORDER BY id ASC")
    nomes = [i[0] for i in c.fetchall()]
    c.close()
    conn.close()
    return nomes

@st.cache_data
def ultima_versao():
    """Retorna a última versão instalada"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nome FROM versoes ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else "0.0.0"

def versao_nova_atualizada():
    """Retorna a última versão instalada"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nome FROM versoes ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    c.close()
    conn.close()
    return row

def atualizar_info_versao(nome_versao, info_extra): # Criei para estar analisando ver se tem versão nova, mas aí eu desisti, porque o programa fica atualizando toda hora.
    """Atualiza o campo info_extra de uma versão existente"""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        UPDATE versoes
        SET info_extra = ?
        WHERE nome = ?
    """, (info_extra, nome_versao))

    conn.commit()
    c.close()
    conn.close()


# ===========================================
# FUNÇÕES DE BACKUP - CONSISTENTES com get_conn()
# ===========================================
# =======================================_ BACKUP

from datetime import datetime, timedelta

DATA = datetime.today().strftime("%Y-%m-%d")
HORAS = datetime.today().strftime("%H:%M")


def Diminui_Horas(hora, diminuir):
    h = datetime.strptime(hora, "%H:%M")
    return (h - timedelta(hours=diminuir)).strftime("%H:%M")


def verifica_minutos(hora: str, minutos: int) -> bool:
    try:
        agora = datetime.now()
        hora_formatada = datetime.strptime(hora, "%H:%M").replace(
            year=agora.year, month=agora.month, day=agora.day
        )
        return agora >= (hora_formatada + timedelta(minutes=minutos))
    except Exception:
        return True


def esc_BACKUP(HORAS_ATUALIZOU):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO BACKUP 
            (DATA, HORAS_INICIO, HORAS_ATUALIZOU, QTDS_HORAS_ATUALIZOU, QTDS_BACKUP, OBS)
            VALUES (?,?,?,?,?,?)
        """, (DATA, HORAS, HORAS_ATUALIZOU, 0, 0, ''))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def esc():
    esc_BACKUP(HORAS)


def ler_BACKUP():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM BACKUP ORDER BY DATA DESC")
    result = c.fetchall()
    conn.close()
    return result


def backups_feito():
    for i in ler_BACKUP():
        return f'Horas: {i[2]}, Atualizou Hoje: {i[3]}, Qunatidade: {i[4]} |'


def ler_BACKUP_HORAS_ATUALIZOU():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT HORAS_ATUALIZOU FROM BACKUP WHERE DATA = ?", (DATA,))
    result = c.fetchall()
    conn.close()
    if result:
        return result[0][0]
    esc()
    return Diminui_Horas(HORAS, 2)


def ler_BACKUP_QTDS_HORAS_ATUALIZOU():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT QTDS_HORAS_ATUALIZOU FROM BACKUP WHERE DATA = ?", (DATA,))
    result = c.fetchall()
    conn.close()
    return result[0][0] if result else 0


def ler_BACKUP_QTDS_BACKUP(data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT QTDS_BACKUP FROM BACKUP WHERE DATA = ?", (data,))
    result = c.fetchall()
    conn.close()
    return result[0][0] if result else 0


def se_BACKUP(data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT DATA FROM BACKUP WHERE DATA = ?", (data,))
    result = c.fetchall()
    conn.close()
    return bool(result)


def ATUAL_BACKUP(COLUNA, CONTEUDO, CONTEUDO2=''):
    conn = get_conn()
    c = conn.cursor()
    if CONTEUDO2 != '':
        c.execute(
            f"UPDATE BACKUP SET {COLUNA} = ?, QTDS_HORAS_ATUALIZOU = ? WHERE DATA = ?",
            (CONTEUDO, CONTEUDO2, DATA)
        )
    else:
        c.execute(
            f"UPDATE BACKUP SET {COLUNA} = ? WHERE DATA = ?",
            (CONTEUDO, DATA)
        )
    conn.commit()
    conn.close()


def Del_BACKUP(ID=''):
    conn = get_conn()
    c = conn.cursor()
    if ID:
        c.execute("DELETE FROM BACKUP WHERE DATA = ?", (ID,))
    else:
        c.execute("DELETE FROM BACKUP")
    conn.commit()
    conn.close()


# Inicializa banco
init_db()
