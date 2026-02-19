# autosave_manager.py
# Versão organizada e unificada: Editor de código com versionamento automático via SQLite.
# Inclui funções de ENTRADA, CONTEUDO e versionamento completo, sem duplicatas.
# Dependências: streamlit, sqlite3, pathlib, difflib, queue, sys, time.

import sqlite3
import os
from datetime import datetime
import difflib  # Para comparações de versões (diff)
from pathlib import Path

from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO

# Configurações iniciais
data = datetime.now()
hora = data.strftime("%H:%M")

# ========================== CONFIGURAÇÃO INICIAL ==========================
_Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
Pasta_Projeto = Path(os.path.dirname(_Venv_path))
DB_PATH = Pasta_Projeto / ".virto_stream" / "Gerente_Estado.db"


# Função para conectar ao banco (com check_same_thread para threads)
def get_conn():
    return sqlite3.connect(DB_PATH , check_same_thread=False)

# Inicializa o banco de dados (cria tabelas se não existirem)
def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Tabela ENTRADA: Para metadados de arquivos
    c.execute('''CREATE TABLE IF NOT EXISTS ENTRADA(
        DIRETORIO TEXT, ARQUIVO TEXT, ATIVO TEXT, ATIVIDADE TEXT)''')

    # Tabela CONTEUDO: Para versões de conteúdo
    c.execute('''CREATE TABLE IF NOT EXISTS CONTEUDO(
        DIRETORIO TEXT, ID INTEGER, CONTEUDO TEXT, HORAS TIME)''')
    conn.commit()
    c.close()
    conn.close()

# ===========================================
# FUNÇÕES PARA TABELA ENTRADA (Metadados)
# ===========================================

def esc_ENTRADA(ID, ARQUIVO, ATIVO, ATIVIDADE):
    """Insere um novo registro na tabela ENTRADA."""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO ENTRADA (DIRETORIO, ARQUIVO, ATIVO, ATIVIDADE)
                VALUES (?, ?, ?, ?)''', (ID, ARQUIVO, ATIVO, ATIVIDADE))
    conn.commit()
    c.close()
    conn.close()

def ler_ENTRADA_Ativos(COLUNA, VALOR):
    """Retorna DIRETORIO e ARQUIVO onde COLUNA = VALOR."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT DIRETORIO, ARQUIVO FROM ENTRADA WHERE {COLUNA} = ?", (VALOR,))
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def se_ENTRADA(DIRETORIO, COLUNA=None, VALOR=None):
    """Verifica se um registro existe na ENTRADA."""
    conn = get_conn()
    c = conn.cursor()
    try:
        if COLUNA is not None and VALOR is not None:
            if not COLUNA.isidentifier():
                raise ValueError("Nome de coluna inválido")
            query = f"SELECT 1 FROM ENTRADA WHERE DIRETORIO = ? AND {COLUNA} = ?"
            c.execute(query, (DIRETORIO, VALOR))
        else:
            query = "SELECT 1 FROM ENTRADA WHERE DIRETORIO = ?"
            c.execute(query, (DIRETORIO,))
        return c.fetchone() is not None
    finally:
        c.close()
        conn.close()

def ATUAL_ENTRADA(DIRETORIO, COLUNA, CONTEUDO, SOMAR=False):
    """Atualiza uma coluna na ENTRADA. Se SOMAR=True, concatena."""
    conn = get_conn()
    c = conn.cursor()
    if SOMAR:
        c.execute(f"SELECT {COLUNA} FROM ENTRADA WHERE DIRETORIO = ?", (DIRETORIO,))
        resultado = c.fetchone()
        valor_atual = resultado[0] if resultado and resultado[0] is not None else ''
        novo_valor = str(valor_atual) + str(CONTEUDO)
    else:
        novo_valor = CONTEUDO
    c.execute(f"UPDATE ENTRADA SET {COLUNA} = ? WHERE DIRETORIO = ?", (novo_valor, DIRETORIO))
    conn.commit()
    c.close()
    conn.close()
    print(f"ATUAL_ENTRADA: {novo_valor}")

def Del_ENTRADA(DIRETORIO=None):
    """Deleta registros da ENTRADA. Se DIRETORIO=None, deleta tudo."""
    conn = get_conn()
    c = conn.cursor()
    if DIRETORIO:
        c.execute("DELETE FROM ENTRADA WHERE DIRETORIO = ?", (DIRETORIO,))
    else:
        c.execute("DELETE FROM ENTRADA")
    conn.commit()
    c.close()
    conn.close()

# ===========================================
# FUNÇÕES PARA TABELA CONTEUDO (Versões)
# ===========================================

def esc_CONTEUDO(DIRETORIO, ID, CONTEUDO):
    """Insere uma nova versão na tabela CONTEUDO."""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO CONTEUDO (DIRETORIO, ID, CONTEUDO, HORAS)
                VALUES (?, ?, ?, ?)''', (DIRETORIO, ID, CONTEUDO, hora))
    conn.commit()
    c.close()
    conn.close()


def ler_CONTEUDO_Coluna_Id(DIRETORIO, COLUNA):
    """Retorna uma coluna específica de um DIRETORIO."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT {COLUNA} FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def ler_CONTEUDO_Coluna(DIRETORIO, COLUNA, VALOR):
    """Retorna registros filtrados por DIRETORIO, COLUNA e VALOR."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM CONTEUDO WHERE DIRETORIO = ? AND {COLUNA} = ?", (DIRETORIO, VALOR))
    result = c.fetchall()
    c.close()
    conn.close()
    return result



def Del_CONTEUDO(DIRETORIO=None):
    """Deleta versões da CONTEUDO. Se DIRETORIO=None, deleta tudo."""
    conn = get_conn()
    c = conn.cursor()
    if DIRETORIO:
        c.execute("DELETE FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
    else:
        c.execute("DELETE FROM CONTEUDO")
    conn.commit()
    c.close()
    conn.close()

# ===========================================
# FUNÇÕES DE VERSIONAMENTO (Undo/Redo e Histórico)
# ===========================================

def salvar_versao(DIRETORIO, CONTEUDO):
    """Salva uma nova versão, evitando duplicatas. Limita a 50 versões."""
    conn = get_conn()
    c = conn.cursor()
    # Verifica duplicata
    c.execute("SELECT CONTEUDO FROM CONTEUDO WHERE DIRETORIO = ? ORDER BY ID DESC LIMIT 1", (DIRETORIO,))
    ultimo = c.fetchone()
    if ultimo and ultimo[0] == CONTEUDO:
        c.execute("SELECT MAX(ID) FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
        return c.fetchone()[0] or 0
    # Obtém novo ID
    c.execute("SELECT MAX(ID) FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
    max_id = c.fetchone()[0] or 0
    new_id = max_id + 1
    # Limita versões
    c.execute("SELECT ID FROM CONTEUDO WHERE DIRETORIO = ? ORDER BY ID ASC", (DIRETORIO,))
    ids = [row[0] for row in c.fetchall()]
    if len(ids) >= 50:
        ids_remover = ids[:-49]
        for old_id in ids_remover:
            c.execute("DELETE FROM CONTEUDO WHERE DIRETORIO = ? AND ID = ?", (DIRETORIO, old_id))
    esc_CONTEUDO(DIRETORIO, new_id, CONTEUDO)
    conn.close()
    return new_id

def get_versao(DIRETORIO, VERSION_ID):
    """Retorna o conteúdo de uma versão específica."""
    result = ler_CONTEUDO_Coluna(DIRETORIO, 'ID', VERSION_ID)
    return result[0][2] if result else None

def get_max_version(DIRETORIO):
    """Retorna a versão mais recente."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT MAX(ID) FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
    max_id = c.fetchone()[0] or 0
    conn.close()
    return max_id

def get_min_version(DIRETORIO):
    """Retorna a versão mais antiga."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT MIN(ID) FROM CONTEUDO WHERE DIRETORIO = ?", (DIRETORIO,))
    min_id = c.fetchone()[0] or 0
    conn.close()
    return min_id

def listar_versoes(DIRETORIO):
    """Lista versões com ID, conteúdo e hora."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT ID, CONTEUDO, HORAS FROM CONTEUDO WHERE DIRETORIO = ? ORDER BY ID DESC", (DIRETORIO,))
    result = c.fetchall()
    conn.close()
    return result

def comparar_versoes(conteudo1, conteudo2):
    """Compara duas versões usando diff."""
    diff = difflib.unified_diff(
        conteudo1.splitlines(keepends=True),
        conteudo2.splitlines(keepends=True),
        fromfile='Versão Anterior',
        tofile='Versão Atual',
        lineterm=''
    )
    return ''.join(diff)

def gerenciar_versionamento_completo(st, aba_id, nome_arq, diretorio_arquivo, Info_Col, conteudo_key, version_key, _):
    # Inicializa contador global para chaves únicas (evita duplicatas)
    if 'key_counter' not in st.session_state:
        st.session_state['key_counter'] = 0
    counter = st.session_state['key_counter']
    st.session_state['key_counter'] += 1

    # Inicializa a chave conteudo_key se não existir (evita KeyError)
    if conteudo_key not in _:
        _[conteudo_key] = ""  # Ou algum valor padrão, como string vazia

    if version_key not in _:
        max_v = get_max_version(diretorio_arquivo)
        _[version_key] = max_v if max_v > 0 else 1
        if max_v == 0:
            salvar_versao(diretorio_arquivo, _[conteudo_key])
    max_v = get_max_version(diretorio_arquivo)
    min_v = get_min_version(diretorio_arquivo)

    col_undo, col_redo = st.columns(2)
    if col_undo.button("↶ Undo", key=f"undo_{aba_id}_{nome_arq}_{counter}"):
        if _[version_key] > min_v:
            _[version_key] -= 1
            new_content = get_versao(diretorio_arquivo, _[version_key])
            if new_content:
                _[conteudo_key] = new_content
                st.rerun()
            else:
                st.toast("❌ Versão não encontrada!")
    if col_redo.button("↷ Redo", key=f"redo_{aba_id}_{nome_arq}_{counter}"):
        if _[version_key] < max_v:
            _[version_key] += 1
            new_content = get_versao(diretorio_arquivo, _[version_key])
            if new_content:
                _[conteudo_key] = new_content
                st.rerun()
            else:
                st.toast("❌ Versão não encontrada!")
    with st.expander(f"📝 Versão: {_[version_key]}/{max_v} (Min: {min_v})"):
        versoes = listar_versoes(diretorio_arquivo)
        if versoes:
            for i, (vid, vconteudo, vhora) in enumerate(versoes[:10]):  # Últimas 10
                st.write(f"**Versão {vid}** - {vhora}")
                if st.button(f"🔄 Restaurar {vid}", key=f"restore_{vid}_{aba_id}_{counter}"):
                    _[conteudo_key] = vconteudo
                    _[version_key] = vid
                    st.rerun()
                if i < len(versoes) - 1:
                    if st.button(f"🔍 Comparar {vid} vs {versoes[i + 1][0]}", key=f"compare_{vid}_{aba_id}_{counter}"):
                        diff = comparar_versoes(versoes[i + 1][1], vconteudo)
                        st.code(diff, language='diff')
        else:
            st.write("Nenhuma versão encontrada.")

    st.divider()
    if st.button("🗑️ Limpar Histórico", key=f"clear_hist_{aba_id}_{nome_arq}", type='secondary'):
        Del_CONTEUDO(diretorio_arquivo)
        _[version_key] = 1
        salvar_versao(diretorio_arquivo, _[conteudo_key])
        st.success("Histórico limpo! Mantida versão atual.")
        st.rerun()
# Inicia as criações das tabelas
init_db()