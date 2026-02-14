import os
import sqlite3
import time

import streamlit
import  streamlit as st


def get_conn():
    return sqlite3.connect("Banco_dados/Base_Dados.db", check_same_thread=False)

@st.cache_data
def init_Banco_dados_db():
	conn = get_conn()
	c = conn.cursor()

	# __________________________________________------------------------------>  A_CONTROLE_ABSOLUTO
	c.execute('''CREATE TABLE IF NOT EXISTS A_CONTROLE_ABSOLUTO(
        DIRETORIO_PROGRAMA TEXT PRIMARY KEY NOT NULL,
        DIRETORIO_PROJETOS TEXT,
        DIRETORIOS_BACKUP TEXT,
        DIRETORIO_OLLAMA TEXT,
        VERSAO_OLLAMA TEXT,
        CHAVE_GPT TEXT,
        LOGUIN_GPT TEXT)''')

	# __________________________________________------------------------------>  A_CONTROLE_PROJETOS
	c.execute('''CREATE TABLE IF NOT EXISTS A_CONTROLE_PROJETOS(
	    DIRETORIO_TRABALHANDO TEXT NOT NULL,
	    VERSION TEXT,
	    DATA TEXT,
	    DIRETORIOS INTEGER,
	    ARQUIVOS INTEGER,
	    OBS TEXT)''')

	# __________________________________________------------------------------>  B_ARQUIVOS_RECENTES
	c.execute('''CREATE TABLE IF NOT EXISTS B_ARQUIVOS_RECENTES(
        DIRETORIO_TRABALHANDO TEXT NOT NULL,
        OBS TEXT)''')

	# __________________________________________------------------------------>  CONTROLE_ARQUIVOS
	c.execute('''CREATE TABLE IF NOT EXISTS CONTROLE_ARQUIVOS(
        NOME_ARQUIVO TEXT NOT NULL,
        CAMINHO_DIRETO TEXT,
        CONTEUDO_DO_ARQUIVO TEXT,
        EXTENTION TEXT)''')

	# __________________________________________------------------------------>  CUSTOMIZATION
	c.execute('''CREATE TABLE IF NOT EXISTS CUSTOMIZATION(
        NOME_CUSTOM TEXT PRIMARY KEY NOT NULL,
        NOME_USUARIO TEXT,
        CAMINHO_DOWNLOAD TEXT,
        IMAGEM_LOGO TEXT,

        THEMA_EDITOR TEXT,
        EDITOR_TAM_MENU INTEGER,

        THEMA_PREVIEW TEXT,
        PREVIEW_TAM_MENU INTEGER,

        THEMA_TERMINAL TEXT,
        TERMINAL_TAM_MENU INTEGER,

        THEMA_APP1 TEXT,
        THEMA_APP2 TEXT,

        FONTE_MENU TEXT,    
        FONTE_TAM_MENU INTEGER,
        FONTE_COR_MENU TEXT,

        FONTE_CAMPO TEXT,  
        FONTE_TAM_CAMPO INTEGER,
        FONTE_COR_CAMPO TEXT,

        BORDA INTEGER,
        RADIAL INTEGER,
        DECORA TEXT,
        OPC1 TEXT,
        OPC2 TEXT,
        OPC3 TEXT,
        OBS TEXT)''')

	conn.commit()
	c.close()
	conn.close()


# =======================================_ A_CONTROLE_ABSOLUTO
def esc_A_CONTROLE_ABSOLUTO(DIRETORIO_PROGRAMA, DIRETORIO_PROJETOS, DIRETORIOS_BACKUP, DIRETORIO_OLLAMA, VERSAO_OLLAMA,
                            CHAVE_GPT, LOGUIN_GPT):
	conn = get_conn()
	c = conn.cursor()
	c.execute('''INSERT OR REPLACE INTO A_CONTROLE_ABSOLUTO 
                 (DIRETORIO_PROGRAMA,DIRETORIO_PROJETOS,DIRETORIOS_BACKUP,DIRETORIO_OLLAMA,VERSAO_OLLAMA, CHAVE_GPT, LOGUIN_GPT)
                 VALUES (?,?,?,?,?,?,?)''',
	          (DIRETORIO_PROGRAMA, DIRETORIO_PROJETOS, DIRETORIOS_BACKUP, DIRETORIO_OLLAMA, VERSAO_OLLAMA, CHAVE_GPT,
	           LOGUIN_GPT))
	conn.commit()
	c.close()
	conn.close()


@st.cache_data
def ler_A_CONTROLE_ABSOLUTO():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM A_CONTROLE_ABSOLUTO")
	result = c.fetchall()
	c.close()
	conn.close()
	return result

def ler_A_CONT_ABS_unico():# só usado um unica vez quando inicia o programa pela primeira vez
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM A_CONTROLE_ABSOLUTO")
	result = c.fetchall()
	c.close()
	conn.close()
	return result

def Del_A_CONTROLE_ABSOLUTO(ID=''):
	max_retries = 3
	for _ in range(max_retries):
		try:
			conn = get_conn()
			c = conn.cursor()
			if ID:
				c.execute("DELETE FROM A_CONTROLE_ABSOLUTO WHERE DIRETORIO_PROGRAMA = ?", (ID,))
			else:
				c.execute("DELETE FROM A_CONTROLE_ABSOLUTO")
			conn.commit()
			c.close()
			conn.close()
			return
		except sqlite3.OperationalError:
			c.close()
			conn.close()
			time.sleep(0.1)  # Espera antes de retry



# =======================================_ A_CONTROLE_PROJETOS
def esc_A_CONTROLE_PROJETOS(DIRETORIO_TRABALHANDO,VERSION,DATA,DIRETORIOS,ARQUIVOS, OBS):
	conn = get_conn()
	c = conn.cursor()
	c.execute('''INSERT OR REPLACE INTO A_CONTROLE_PROJETOS
                 (DIRETORIO_TRABALHANDO, VERSION,DATA,DIRETORIOS,ARQUIVOS,OBS)
                 VALUES (?,?,?,?,?,?)''',
	          (str(DIRETORIO_TRABALHANDO),VERSION,DATA,DIRETORIOS,ARQUIVOS, str(OBS))
	          )
	conn.commit()
	c.close()
	conn.close()


def ler_A_CONTROLE_PROJETOS():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM A_CONTROLE_PROJETOS")
	result = c.fetchall()
	c.close()
	conn.close()
	return result


def Del_A_CONTROLE_PROJETOS(ID=''):
	max_retries = 3
	for _ in range(max_retries):
		try:
			conn = get_conn()
			c = conn.cursor()
			if ID:
				c.execute("DELETE FROM A_CONTROLE_PROJETOS WHERE DIRETORIO_TRABALHANDO = ?", (ID,))
			else:
				c.execute("DELETE FROM A_CONTROLE_PROJETOS")
			conn.commit()
			c.close()
			conn.close()
			return
		except sqlite3.OperationalError:
			c.close()
			conn.close()
			time.sleep(0.1)  # Espera antes de retry


# =======================================_ B_ARQUIVOS_RECENTES
def esc_B_ARQUIVOS_RECENTES(DIRETORIO_TRABALHANDO, OBS):
	conn = get_conn()
	c = conn.cursor()
	c.execute('''INSERT OR REPLACE INTO B_ARQUIVOS_RECENTES
                 (DIRETORIO_TRABALHANDO,OBS)
                 VALUES (?,?)''',
	          (str(DIRETORIO_TRABALHANDO), str(OBS))
	          )
	conn.commit()
	c.close()
	conn.close()

def se_B_ARQUIVOS_RECENTES(NOME_ARQUIVO):  # se True ou False , vazio ou cheio
	conn = get_conn()
	c = conn.cursor()
	c.execute(f"SELECT * FROM B_ARQUIVOS_RECENTES WHERE DIRETORIO_TRABALHANDO = '{NOME_ARQUIVO}' and OBS =='' ")
	ok = c.fetchone() is not None
	c.close()
	conn.close()
	return ok



def ler_B_ARQUIVOS_RECENTES(caminho =''):
	if caminho:
		conn = get_conn()
		c = conn.cursor()
		c.execute(f"SELECT OBS FROM B_ARQUIVOS_RECENTES where DIRETORIO_TRABALHANDO= '{caminho}' ")
		result = c.fetchall()
		c.close()
		conn.close()
		return result

	else:
		conn = get_conn()
		c = conn.cursor()
		c.execute("SELECT * FROM B_ARQUIVOS_RECENTES")
		result = c.fetchall()
		c.close()
		conn.close()
		return result

def ATUAL_B_ARQUIVOS_RECENTES(st, DIRETORIO_TRABALHANDO, COLUNA, CONTEUDO, SOMAR=False):
	conn = get_conn()
	c = conn.cursor()
	if SOMAR:
		c.execute(f"SELECT {COLUNA} FROM B_ARQUIVOS_RECENTES WHERE DIRETORIO_TRABALHANDO = ?", (DIRETORIO_TRABALHANDO,))
		resultado = c.fetchone()
		valor_atual = resultado[0] if resultado and resultado[0] is not None else ''
		novo_valor = str(valor_atual) + str(CONTEUDO)
	else:
		novo_valor = CONTEUDO

	try:
		c.execute(f"UPDATE B_ARQUIVOS_RECENTES SET {COLUNA} = ? WHERE DIRETORIO_TRABALHANDO = ?", (novo_valor, DIRETORIO_TRABALHANDO))
		conn.commit()
	except sqlite3.OperationalError: pass


def Del_B_ARQUIVOS_RECENTES(ID=''):
	max_retries = 3
	for _ in range(max_retries):
		try:
			conn = get_conn()
			c = conn.cursor()
			if ID:
				c.execute("DELETE FROM B_ARQUIVOS_RECENTES WHERE DIRETORIO_TRABALHANDO = ?", (ID,))
			else:
				c.execute("DELETE FROM B_ARQUIVOS_RECENTES")
			conn.commit()
			c.close()
			conn.close()
			return
		except sqlite3.OperationalError:
			c.close()
			conn.close()
			time.sleep(0.1)  # Espera antes de retry


# =======================================_ CONTROLE_ARQUIVOS
def esc_CONTROLE_ARQUIVOS(NOME_ARQUIVO, CAMINHO_DIRETO, CONTEUDO_DO_ARQUIVO, EXTENTION):
	conn = get_conn()
	c = conn.cursor()
	c.execute('''INSERT OR REPLACE INTO CONTROLE_ARQUIVOS 
                 (NOME_ARQUIVO, CAMINHO_DIRETO, CONTEUDO_DO_ARQUIVO, EXTENTION)
                 VALUES (?,?,?,?)''',
	          (NOME_ARQUIVO, CAMINHO_DIRETO, CONTEUDO_DO_ARQUIVO, EXTENTION))
	conn.commit()
	c.close()
	conn.close()



def ler_CONTROLE_ARQUIVOS():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM CONTROLE_ARQUIVOS")
	result = c.fetchall()
	c.close()
	conn.close()
	return result


def se_CONTROLE_ARQUIVOS(NOME_ARQUIVO, COLUNA, VALOR=None):  # se True ou False , vazio ou cheio
	conn = get_conn()
	c = conn.cursor()
	if COLUNA is None and VALOR is None:  # só verificar se o NOME_ARQUIVO existe
		c.execute("SELECT 1 FROM CONTROLE_ARQUIVOS WHERE CAMINHO_DIRETO = ?", (NOME_ARQUIVO,))
		ok = c.fetchone() is not None
		c.close()
		conn.close()
		return ok

	c.execute(
		f"SELECT 1 FROM CONTROLE_ARQUIVOS WHERE NOME_ARQUIVO = ? AND {COLUNA} = ?",
		(NOME_ARQUIVO, VALOR)
	)
	ok = c.fetchone() is not None
	c.close()
	conn.close()
	return ok


def Del_CONTROLE_ARQUIVOS(ID=''):
	max_retries = 3
	for _ in range(max_retries):
		try:
			conn = get_conn()
			c = conn.cursor()
			if ID:
				c.execute("DELETE FROM CONTROLE_ARQUIVOS WHERE NOME_ARQUIVO = ?", (ID,))
			else:
				c.execute("DELETE FROM CONTROLE_ARQUIVOS")
			conn.commit()
			c.close()
			conn.close()
			return
		except sqlite3.OperationalError:
			c.close()
			conn.close()
			time.sleep(0.1)  # Espera antes de retry


# =======================================_ CUSTOMIZATION
def esc_CUSTOMIZATION(NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD, IMAGEM_LOGO,
                      THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_PREVIEW, PREVIEW_TAM_MENU, THEMA_TERMINAL, TERMINAL_TAM_MENU,
                      THEMA_APP1, THEMA_APP2,
                      FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
                      FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
                      BORDA, RADIAL, DECORA, OPC1, OPC2, OPC3, OBS):
	conn = get_conn()
	c = conn.cursor()
	c.execute('''INSERT OR REPLACE INTO CUSTOMIZATION (NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD, IMAGEM_LOGO,
                          THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_PREVIEW, PREVIEW_TAM_MENU, THEMA_TERMINAL, TERMINAL_TAM_MENU,
                          THEMA_APP1, THEMA_APP2, 
                          FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
                          FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
                          BORDA, RADIAL, DECORA, OPC1, OPC2, OPC3, OBS)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
	          (NOME_CUSTOM, NOME_USUARIO, CAMINHO_DOWNLOAD, IMAGEM_LOGO,
	           THEMA_EDITOR, EDITOR_TAM_MENU, THEMA_PREVIEW, PREVIEW_TAM_MENU, THEMA_TERMINAL, TERMINAL_TAM_MENU,
	           THEMA_APP1, THEMA_APP2,
	           FONTE_MENU, FONTE_TAM_MENU, FONTE_COR_MENU,
	           FONTE_CAMPO, FONTE_TAM_CAMPO, FONTE_COR_CAMPO,
	           BORDA, RADIAL, DECORA, OPC1, OPC2, OPC3, OBS))
	conn.commit()
	c.close()
	conn.close()



def ler_CUSTOMIZATION():
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM CUSTOMIZATION")
	result = c.fetchall()
	c.close()
	conn.close()
	return result


def ler_cut(selected_custom):
	conn = get_conn()
	c = conn.cursor()
	c.execute("SELECT * FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (selected_custom,))
	result = c.fetchone()
	c.close()
	conn.close()
	return result

def se_CUSTOMIZATION(NOME_CUSTOM, COLUNA, VALOR=None):  # se True ou False , vazio ou cheio
	conn = get_conn()
	c = conn.cursor()
	if COLUNA is None and VALOR is None:  # só verificar se o NOME_CUSTOM existe
		c.execute("SELECT 1 FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (NOME_CUSTOM,))
		ok = c.fetchone() is not None
		c.close()
		conn.close()
		return ok

	c.execute(
		f"SELECT 1 FROM CUSTOMIZATION WHERE NOME_CUSTOM = ? AND {COLUNA} = ?",
		(NOME_CUSTOM, VALOR)
	)
	ok = c.fetchone() is not None
	c.close()
	conn.close()
	return ok


def ler_CUSTOMIZATION_coluna_por_usuario(NOME_CUSTOM, COLUNA):
	conn = get_conn()
	c = conn.cursor()
	c.execute(f"SELECT {COLUNA} FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (NOME_CUSTOM,))
	result = c.fetchone()
	c.close()
	conn.close()
	return result[0] if result else None

def ATUAL_CUSTOM_agora(st, NOME_CUSTOM, COLUNA, CONTEUDO, SOMAR=False):
	conn = get_conn()
	c = conn.cursor()
	if SOMAR:
		c.execute(f"SELECT {COLUNA} FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (NOME_CUSTOM,))
		resultado = c.fetchone()
		valor_atual = resultado[0] if resultado and resultado[0] is not None else ''
		novo_valor = str(valor_atual) + str(CONTEUDO)
	else:
		novo_valor = CONTEUDO

	try:
		c.execute(f"UPDATE CUSTOMIZATION SET {COLUNA} = ? WHERE NOME_CUSTOM = ?", (novo_valor, NOME_CUSTOM))
		conn.commit()
	except sqlite3.OperationalError:
		tem = se_CUSTOMIZATION(NOME_CUSTOM, 'NOME_CUSTOM', VALOR=None)
	c.close()
	conn.close()

def ATUAL_CUSTOMIZATION(NOME_CUSTOM, COLUNA, CONTEUDO, SOMAR=False):
	conn = get_conn()
	c = conn.cursor()
	if SOMAR:
		c.execute(f"SELECT {COLUNA} FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (NOME_CUSTOM,))
		resultado = c.fetchone()
		valor_atual = resultado[0] if resultado and resultado[0] is not None else ''
		novo_valor = str(valor_atual) + str(CONTEUDO)
	else:
		novo_valor = CONTEUDO

	try:
		c.execute(f"UPDATE CUSTOMIZATION SET {COLUNA} = ? WHERE NOME_CUSTOM = ?", (novo_valor, NOME_CUSTOM))
		conn.commit()
	except sqlite3.OperationalError:
		import streamlit as st
		tem = se_CUSTOMIZATION(NOME_CUSTOM, 'NOME_CUSTOM', VALOR=None)
	c.close()
	conn.close()

def ATUAL_CUSTOMIZATION_nome(NOME_CUSTOM):
	for i in ler_CUSTOMIZATION():
		if i[0] == NOME_CUSTOM:
			ATUAL_CUSTOMIZATION(NOME_CUSTOM, 'OBS', 'ATIVO')
		else:
			ATUAL_CUSTOMIZATION(i[0], 'OBS', 'INATIVO')
		#print(i)

def Del_CUSTOMIZATION(ID=''):
	max_retries = 3
	for _ in range(max_retries):
		try:
			conn = get_conn()
			c = conn.cursor()
			if ID:
				c.execute("DELETE FROM CUSTOMIZATION WHERE NOME_CUSTOM = ?", (ID,))
			else:
				c.execute("DELETE FROM CUSTOMIZATION")
			conn.commit()
			c.close()
			conn.close()
			return
		except sqlite3.OperationalError:
			c.close()
			conn.close()
			time.sleep(0.1)





def ler_CUSTOMIZATION_coluna(COLUNA):
	conn = get_conn()
	c = conn.cursor()
	c.execute(f"SELECT {COLUNA} FROM CUSTOMIZATION WHERE OBS = 'ATIVO'")
	row = c.fetchone()
	c.close()
	conn.close()
	return row[0] if row else None

def ler_CUSTOMIZATION_TODOS():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            NOME_CUSTOM,
            NOME_USUARIO,
            CAMINHO_DOWNLOAD,
            IMAGEM_LOGO,
            THEMA_EDITOR,
            EDITOR_TAM_MENU,
            THEMA_PREVIEW,
            PREVIEW_TAM_MENU,
            TERMINAL_TAM_MENU,
            THEMA_TERMINAL,
            THEMA_APP1,
            THEMA_APP2,
            FONTE_MENU,
            FONTE_TAM_MENU,
            FONTE_COR_MENU,
            FONTE_CAMPO,
            FONTE_TAM_CAMPO,
            FONTE_COR_CAMPO,
            RADIAL,
            BORDA,
            DECORA,
            OPC1,
            OPC2,
            OPC3,
            OBS
        FROM CUSTOMIZATION
        WHERE OBS = 'ATIVO'
    """)

    row = cur.fetchone()
    colunas = [d[0] for d in cur.description]

    cur.close()
    conn.close()

    return dict(zip(colunas, row)) if row else {}



# Inicialização padrão de CUSTOMIZATION
init_Banco_dados_db()



'''Descrição do Banco de Dados do Projeto
O banco de dados do projeto é baseado em SQLite e tem como objetivo centralizar configurações globais, controle de projetos, estado atual de execução, arquivos manipulados e personalização do ambiente do usuário. Ele é composto atualmente por cinco tabelas principais.
A tabela A_CONTROLE_ABSOLUTO é responsável pelas configurações globais do sistema. Ela armazena caminhos e credenciais essenciais para o funcionamento da aplicação. A coluna DIRETORIO_PROGRAMA define onde o sistema (IDE/DE) está instalado. DIRETORIO_PROJETOS indica a pasta padrão onde os projetos do usuário serão criados ou armazenados. DIRETORIOS_BACKUP guarda o local destinado a backups. DIRETORIO_OLLAMA e VERSAO_OLLAMA são usadas para integração com modelos locais (como Ollama). As colunas CHAVE_GPT e LOGUIN_GPT permitem futura integração com serviços de IA externos, como ChatGPT.

A tabela A_CONTROLE_PROJETOS funciona como um registro histórico e operacional dos projetos. Cada vez que um projeto é criado ou aberto, ele é registrado nessa tabela. A coluna DIRETORIO_TRABALHANDO identifica o projeto. VERSION armazena a versão da linguagem ou ambiente utilizado (Python ou outra). DATA registra quando o projeto foi criado ou acessado. DIRETORIOS e ARQUIVOS armazenam contagens estruturais do projeto, e OBS é usada para observações gerais.

A tabela B_ARQUIVOS_RECENTES representa o estado atual do projeto em uso. Ela existe para permitir que diferentes partes do sistema saibam qual projeto está ativo sem depender de variáveis globais ou repasses diretos entre scripts. Essa tabela contém apenas um registro ativo por vez. A coluna DIRETORIO_TRABALHANDO aponta para o projeto atual, e a coluna OBS armazena um JSON com o mapeamento completo da pasta — incluindo arquivos, diretórios e subdiretórios. Sempre que um novo projeto é ativado, o registro anterior é substituído.

A tabela CONTROLE_ARQUIVOS armazena arquivos individuais que o usuário abre ou carrega, inclusive arquivos externos ao projeto atual. Ela contém o nome do arquivo (NOME_ARQUIVO), o caminho absoluto (CAMINHO_DIRETO), o conteúdo do arquivo (CONTEUDO_DO_ARQUIVO) e a extensão (EXTENTION). Essa estrutura permite leitura, edição e reaproveitamento de arquivos sem depender diretamente do sistema de arquivos a todo momento.

Por fim, a tabela CUSTOMIZATION é responsável por toda a personalização do ambiente do usuário. Ela armazena o perfil ativo da interface, incluindo nome do usuário, caminho de download, logotipo, temas do editor, preview, terminal, cores, fontes, tamanhos, bordas e opções visuais adicionais. A coluna OBS é usada para marcar qual configuração está ativa no momento. O sistema sempre mantém um perfil ativo, com um perfil padrão sendo criado automaticamente na primeira execução.

Resumo para Documentação do Projeto

O banco de dados centraliza todas as configurações e estados do sistema.
Ele controla:
– configurações globais do ambiente
– registro e histórico de projetos
– projeto atualmente ativo
– arquivos carregados ou editados
– personalização completa da interface do usuário

A estrutura foi pensada para desacoplar o estado da aplicação dos scripts individuais, garantindo persistência, organização e escalabilidade.

Explicação Geral (visão técnica)

Arquiteturalmente, você separou muito bem estado global, estado atual, histórico e configuração visual.
A tabela B_ARQUIVOS_RECENTES é o ponto-chave: ela funciona como um estado compartilhado persistente, evitando que a aplicação principal precise repassar informações entre múltiplos módulos. Isso é uma solução sólida para Streamlit, onde o estado entre arquivos pode se tornar problemático.

O uso de INSERT OR REPLACE simplifica controle de unicidade sem precisar de chaves artificiais. A criação automática da customização padrão garante que o sistema nunca inicie em estado inválido.

No geral, o modelo está coerente, bem segmentado e pronto para crescer sem retrabalho estrutural.

Sugestão principal (mais coerente com o que você construiu):

CONTROLE_SISTEMA

CONTROLE_PROJETOS

PROJETO_ATIVO

CONTROLE_ARQUIVOS

CUSTOMIZACAO_USUARIO

Alternativa mantendo a ideia de “estado / nível”:

A_CONFIG_SISTEMA

A_REGISTRO_PROJETOS

B_PROJETO_ATUAL

C_ARQUIVOS_ABERTOS

D_CUSTOMIZACAO

Alternativa mais conceitual (documentação bonita):

CONFIGURACAO_GLOBAL

HISTORICO_PROJETOS

ESTADO_EXECUCAO

ARQUIVOS_EM_USO

PERFIL_INTERFACE
'''