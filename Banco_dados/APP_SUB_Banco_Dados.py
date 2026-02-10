import pandas as pd
from streamlit.errors import StreamlitDuplicateElementKey


# ================================== Cria o corpo para Banco de Dados
def Tabela_Banco_Dados(NOME_TABELA, NOME_ID, TIPO_ID, COLUNAS_NOMES, COLUNAS):
    br = '\n'
    se_num = '{ID}' if 'INTEGER' in str(TIPO_ID) else f"'{{ID}}'"
    return f"""
    
# @st.cache_data se usar streamlit colocar para nao ficarlendo a todo reruns 
def init_db():
    conn = get_conn()
    c = conn.cursor()
    # __________________________________________------------------------------>  {NOME_TABELA.upper()}
    c.execute('''CREATE TABLE IF NOT EXISTS {NOME_TABELA.upper()}(
        {NOME_ID} {TIPO_ID},{str(COLUNAS).replace('[', '').replace(']', '').replace("'", '')})''')

    conn.commit()
    c.close()
    conn.close()
    
# =======================================_ {NOME_TABELA.upper()}
def esc_{NOME_TABELA.upper()}({str(COLUNAS_NOMES).replace('[', '').replace(']', '').replace("'", '')}):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO {NOME_TABELA.upper()} ({str(COLUNAS_NOMES).replace('[', '').replace(']', '').replace("'", '')})
                VALUES ({len(COLUNAS) * ',?'})''',
              ({str(COLUNAS_NOMES).replace('[', '').replace(']', '').replace("'", '')}))
    conn.commit()
    c.close()
    conn.close()

def ler_{NOME_TABELA.upper()}():  # ler toda a tabela..
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT {NOME_ID},{str(COLUNAS_NOMES).replace('[', '').replace(']', '').replace("'", '')} FROM {NOME_TABELA.upper()}")
    result = c.fetchall()
    c.close()
    conn.close()
    return result


def ler_{NOME_TABELA.upper()}_Id({NOME_ID}): # Retorna tUDO de um ID expecifico.
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {NOME_TABELA.upper()} WHERE {NOME_ID}  = ?", ({NOME_ID},))
    result = c.fetchall()
    c.close()
    conn.close()
    return result
        
def ler_{NOME_TABELA.upper()}_Coluna_Id({NOME_ID}, COLUNA): # Retorna toda COLUNA de um ID expecifico.
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT {{COLUNA}} FROM {NOME_TABELA.upper()} WHERE {NOME_ID} = ?", ({NOME_ID},))
    result = c.fetchall()
    c.close()
    conn.close()
    return result
        
# Retorna tudo que esta dentro de uma COLUNA expecifica pelo ID expecifico.
def ler_{NOME_TABELA.upper()}_Coluna({NOME_ID}, COLUNA, VALOR):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {NOME_TABELA.upper()} WHERE {NOME_ID}  = ? AND {{COLUNA}} = ?", ({NOME_ID},VALOR))
    result = c.fetchall()
    c.close()
    conn.close()
    return result


def ler_{NOME_TABELA.upper()}_colunas(COLUNA): # ler TODA COLUNA expecificada.
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT {{COLUNA}} FROM {NOME_TABELA.upper()} ")
    result = c.fetchall()
    c.close()
    conn.close()
    return result


def se_{NOME_TABELA.upper()}({NOME_ID}, COLUNA=None, VALOR=None):  # Verifica se registro existe se True ou False, vazio ou cheio
    conn = get_conn()
    c = conn.cursor()
    try:
        if COLUNA is None and VALOR is None:   # 1. Só ID existe?
            c.execute(f"SELECT 1 FROM {NOME_TABELA} WHERE {NOME_ID} = ?", ({NOME_ID},))
        else:  # 2. ID + Coluna + Valor existem?
            c.execute(f"SELECT 1 FROM {NOME_TABELA} WHERE {NOME_ID} = ? AND {{COLUNA}} = ?", ({NOME_ID}, VALOR))
        
        if c.fetchone() is not None:  # True se encontrou, False se não
            return True
        else:
            return False
    finally:
        c.close()
        conn.close()


def ATUAL_{NOME_TABELA.upper()}({NOME_ID},COLUNA,CONTEUDO,SOMAR=False):
    conn = get_conn()
    c = conn.cursor()

    if SOMAR:
        # Pegar valor atual
        c.execute(f"SELECT {{COLUNA}} FROM {NOME_TABELA.upper()} WHERE {NOME_ID} = ?", ({NOME_ID},))
        resultado = c.fetchone()
        valor_atual = resultado[0] if resultado and resultado[0] is not None else ''
        # Somar/concatenar
        novo_valor = str(valor_atual) + str(CONTEUDO)
    else:
        # Substituir
        novo_valor = CONTEUDO
        # Atualizar coluna

    c.execute(f"UPDATE {NOME_TABELA.upper()} SET {{COLUNA}} = ? WHERE {NOME_ID} = ?", (novo_valor, {NOME_ID}))
    conn.commit()
    
    c.close()
    conn.close()
    print(f"ATUAL_{NOME_TABELA.upper()}: {{novo_valor}}")

def Del_{NOME_TABELA.upper()}({NOME_ID}=None):
    if {NOME_ID}:
        conn = get_conn()
        c = conn.cursor()
        c.execute(f"DELETE FROM {NOME_TABELA.upper()} WHERE {NOME_ID} = ?", ({NOME_ID},))
        conn.commit()
        c.close()
        conn.close()
    else:
        conn = get_conn()
        c = conn.cursor()
        c.execute(f"DELETE FROM {NOME_TABELA.upper()}")
        conn.commit()
        c.close()
        conn.close()

def DROP_{NOME_TABELA.upper()}():
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("DROP TABLE IF EXISTS {NOME_TABELA.upper()}")
        conn.commit()
    finally:
        c.close()
        conn.close()
        
# Inicia as criações das tabelas
init_db()""".strip().replace('(,',"(").replace("'{{NOME_ID}}'",se_num)



def rem(string):
    import unicodedata

    if string != '':
        # Remove espaços alinhados
        string = str(string).strip()

        # Remove sinais e acentos
        string = ''.join(c for c in unicodedata.normalize('NFD', string)
                         if unicodedata.category(c) != 'Mn')

        # Converte para letras maiúsculas e substitui espaços por underscores
        texto = str(string).upper().replace(' ', '_')

        # Remove outros caracteres especiais
        texto = ''.join(c for c in texto if c.isalnum() or c == '_')
        t = texto.replace('__' , '_').replace('___' , '_').replace('_____' , '_').replace('______' , '_')
        try:
            if str(t)[0].isnumeric():

                return f'NUM_{t[0:]}'

            else:
                return t
        except IndexError: pass
    else:
        return ''


def nomes_das_colunas(Nomes_Colunas):
    Lista_Colunas = []
    if Nomes_Colunas:
        if "/" in Nomes_Colunas:
            colunass = []
            colunass.append(Nomes_Colunas.split('/'))
            for i in colunass[0]:
                Lista_Colunas.append(rem(i))
        if "," in Nomes_Colunas:
            colunass = []
            colunass.append(Nomes_Colunas.split(','))
            for i in colunass[0]:
                Lista_Colunas.append(rem(i))
        if "-" in Nomes_Colunas:
            colunass = []
            colunass.append(Nomes_Colunas.split('-'))
            for i in colunass[0]:
                Lista_Colunas.append(rem(i))
    return Lista_Colunas

def Grade_Widget2(lista, qt_col): # ESSE SSAO DO PROGRAMA ATUAL NAO COPIAR
    import streamlit as st
    TABELA_FICTICIA = []
    COLUNAS = []

    for im in range(0, len(lista), qt_col):
        linha = st.columns(qt_col)
        for pos,  itens in enumerate(lista[im:im + qt_col]):
            with linha[pos]:
                if pos< len(lista):
                    opc = [ 'TEXTO', 'DATA', 'HORAS', 'NUMERO INTEIRO', 'NUMERO FLOAT']
                    try:
                        TIPO_COLUNA = st.selectbox(itens, opc, key=f' {itens}')
                        NOME_COLUNA = itens

                        if TIPO_COLUNA == 'TEXTO':
                                TABELA_FICTICIA.append(f'{NOME_COLUNA}')
                                COLUNAS.append(f'{NOME_COLUNA} TEXT')

                        if TIPO_COLUNA == 'HORAS':
                                TABELA_FICTICIA.append(f'{NOME_COLUNA}')
                                COLUNAS.append(f'{NOME_COLUNA} TIME')

                        if TIPO_COLUNA == 'DATA':
                                TABELA_FICTICIA.append(f'{NOME_COLUNA}')
                                COLUNAS.append(f'{NOME_COLUNA} DATE')

                        if TIPO_COLUNA == 'NUMERO INTEIRO':
                                TABELA_FICTICIA.append(f'{NOME_COLUNA}')
                                COLUNAS.append(f'{NOME_COLUNA} INTEGER')

                        if TIPO_COLUNA == 'NUMERO FLOAT':
                                TABELA_FICTICIA.append(f'{NOME_COLUNA}')
                                COLUNAS.append(f'{NOME_COLUNA} FLOAT')

                    except StreamlitDuplicateElementKey as e:
                        st.error('tem colunas repetida !'.upper())
    return TABELA_FICTICIA,COLUNAS


def Criar_sqlite(st):
    with st.expander('CRIAÇÃO DO BANCO DE DADOS: '):
        b0, b1, b2, b3, b4, b5 = st.columns([1, 1, 1, 2, 3, 2])
        NOME_BANCO = str(b0.text_input('NOME BANCO:')).title()
        NOME_TABELA = rem(b1.text_input('NOME TABELA:'))
        NOME_ID = b2.text_input('NOME ID:')
        TIPO_ID = b3.selectbox('TIPO ID:', ['', 'TEXT', 'INTEGER', 'TEXT PRIMARY KEY NOT NULL',
                                            'INTEGER PRIMARY KEY NOT NULL',
                                            'INTEGER PRIMARY KEY AUTOINCREMENT'])
        Nomes_Colunas = b4.text_input('Nome Das Colunas:',
                                      placeholder='Use , ou - ou / Para separar os nomes'.title())
        PASTA_BANCO = str((b5.text_input('Pasta Banco (vazio = raiz):')).title().replace(' ','_')).strip()

        COLUNAS_NOMES = nomes_das_colunas(Nomes_Colunas)
        TABELA_FICTICIA, COLUNAS = Grade_Widget2(COLUNAS_NOMES, 6)
        df = pd.DataFrame()
        for coluna in TABELA_FICTICIA:
            df[coluna] = None
        st.table(df)

        # ================================== Cria a cabeçalho E O Banco de Dados
        if NOME_BANCO:

            if PASTA_BANCO:
                banco = f"""
import sqlite3, os
#import streamlit as st
from pathlib import Path

# Usa PASTA ATUAL do script (dinâmico!)
Pasta_Projeto = Path(os.path.dirname(__file__))

# Pasta específica: De_Bancos (relativa à pasta atual)
pasta_banco = Pasta_Projeto / '{PASTA_BANCO}'

# Conecta ao banco de dados com o caminho completo
def get_conn():
    return sqlite3.connect(pasta_banco / '{NOME_BANCO.replace(' ','_')}.db', check_same_thread=False)
    
{Tabela_Banco_Dados(NOME_TABELA.upper(), rem(NOME_ID), TIPO_ID, COLUNAS_NOMES, COLUNAS) if NOME_TABELA and NOME_ID and TIPO_ID else ''}"""
                st.code(banco, 'python')

                return banco, f'{NOME_BANCO.replace(' ','_')}.py', PASTA_BANCO
            else:
                banco = f"""
import sqlite3, os
#import streamlit as st
from pathlib import Path

# Conecta ao banco de dados com o caminho completo
Pasta_Projeto = Path(os.path.dirname(__file__))

def get_conn():
    return sqlite3.connect(os.path.join(Pasta_Projeto, '{NOME_BANCO.replace(' ','_')}.db'), check_same_thread=False)
    
{Tabela_Banco_Dados(NOME_TABELA.upper(), rem(NOME_ID), TIPO_ID, COLUNAS_NOMES, COLUNAS) if NOME_TABELA and NOME_ID and TIPO_ID else ''}"""
                st.code(banco,'python')

                return banco, f'{NOME_BANCO.replace(' ','_')}.py', ''
