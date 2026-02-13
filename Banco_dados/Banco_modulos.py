import os
import pkgutil
import re
import sqlite3
import ast
import sys
import sysconfig
from pathlib import Path
import streamlit as st

from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida
from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO


# ========================== CONFIGURAÇÃO INICIAL ==========================
_Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
Pasta_Projeto = Path(os.path.dirname(_Venv_path))
DB_PATH = Pasta_Projeto / ".virto_stream" / "Controle_Stream.db"

# ===================== DESCOBRIR STDLIB =====================

stdlib_path = Path(sysconfig.get_paths()["stdlib"])
modulos_stdlib = {m.name for m in pkgutil.iter_modules([str(stdlib_path)])}
modulos_stdlib |= set(sys.builtin_module_names)

# ===================== MÓDULOS DA VENV =====================

site_packages = Path(_Venv_path) / "Lib" / "site-packages"
sys.path.insert(0, str(site_packages))
modulos_venv = {m.name for m in pkgutil.iter_modules([str(site_packages)])}

# ===================== CONJUNTO FINAL A IGNORAR =====================

modulos_ignorar = modulos_venv | modulos_stdlib


# ========================== FUNÇÕES DE BANCO =============================

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # TODO: Tabela que armazena arquivos abertos recentemente, com conteúdo e observações
    c.execute(
        '''CREATE TABLE IF NOT EXISTS CONTROLE_ARQUIVOS_ABERTOS(
            CAMINHO_DIRETO TEXT PRIMARY KEY,
            CONTEUDO_DO_ARQUIVO TEXT,
            OBS TEXT
        )'''
    )

    # TODO: Tabela que registra funções, classes e imports do usuário por arquivo
    c.execute(
        '''CREATE TABLE IF NOT EXISTS ITENS_DO_ARQUIVO(
            ARQUIVO_CAMINHO TEXT,
            TIPO TEXT,
            FUNCAO_IMPORTADA TEXT,
            ONDE_IMPORTOU TEXT,
            FUNCAO_COMPLETA TEXT,
            LINHA INTEGER
        )'''
    )

    # TODO: Tabela que armazena todos os imports (tanto válidos quanto ignorados) por arquivo
    c.execute(
        '''CREATE TABLE IF NOT EXISTS IMPORTS_GERAIS(
            ARQUIVO_CAMINHO TEXT,
            NOME TEXT,
            LINHA INTEGER,
            STATUS TEXT  -- IGNORADO ou VALIDO
        )'''
    )

    # TODO: Tabela que registra os imports que devem ser ignorados (stdlib, venv, etc.) com motivo
    c.execute(""" 
            CREATE TABLE IF NOT EXISTS IMPORTS_IGNORADOS(
                ARQUIVO_CAMINHO TEXT,
                NOME TEXT,
                LINHA INTEGER,
                MOTIVO TEXT
            )
        """)

    conn.commit()
    c.close()
    conn.close()

# TODO: gera dados de auto-complete pro editor (funções, classes e imports)
def gerar_auto_complete_EDITOR():
    def_from = {}
    def_predefinidos = {}  # ✅ APENAS 'function'
    from_predefinidos = {}  # ✅ APENAS 'import'

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT ARQUIVO_CAMINHO, TIPO, FUNCAO_IMPORTADA, ONDE_IMPORTOU, 
               FUNCAO_COMPLETA, LINHA
        FROM ITENS_DO_ARQUIVO
        WHERE TIPO IN ('function', 'class', 'import')
    """)
    rows = c.fetchall()
    c.close()
    conn.close()

    for row in rows:
        arquivo_caminho = row[0]
        tipo = row[1]
        funcao_nome = row[2]
        onde_importar = row[3] or ""
        funcao_completa = row[4]
        linha = row[5] or 0

        # ✅ CHAVE = FUNCAO_COMPLETA INTEIRA
        nome_chave = funcao_completa.strip()

        origem = os.path.splitext(os.path.basename(arquivo_caminho))[0]
        if onde_importar:
            origem = onde_importar.split(".")[0]

        dados = {
            "caminho": arquivo_caminho,
            "modulo": onde_importar,
            "tipo": tipo,
            "linha": linha,
            "origem": origem
        }

        # ✅ SEMPRE no def_from
        def_from[nome_chave] = dados



        if tipo == "function":
            # ✅ def_predefinidos = SÓ FUNCTIONS
            def_predefinidos[funcao_completa] = dados

        elif tipo == "import":
            # ✅ from_predefinidos = SÓ IMPORTS
            from_predefinidos[funcao_completa] = dados


    return def_from, def_predefinidos, from_predefinidos


def reset_db():
    """Apaga todos os dados das tabelas, mantendo a estrutura"""
    conn = get_conn()
    c = conn.cursor()

    # Deleta todos os dados de cada tabela (mantém a estrutura)
    tables = [
        'CONTROLE_ARQUIVOS_ABERTOS',
        'ITENS_DO_ARQUIVO',
        'IMPORTS_GERAIS',
        'IMPORTS_IGNORADOS'
    ]

    for table in tables:
        c.execute(f'DELETE FROM {table}')
        st.write(f"Tabela {table} limpa.")

    conn.commit()
    c.close()
    conn.close()
    st.write("Banco de dados resetado com sucesso!")

init_db()

def esc_CONTROLE_ARQUIVOS_ABERTOS(caminho, conteudo, obs):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        '''INSERT OR REPLACE INTO CONTROLE_ARQUIVOS_ABERTOS(CAMINHO_DIRETO, CONTEUDO_DO_ARQUIVO, OBS)
           VALUES (?,?,?)''',
        (str(caminho), conteudo, obs)
    )
    conn.commit()
    c.close()
    conn.close()

def esc_ITENS_DO_ARQUIVO(arquivo_caminho, tipo, funcao_importada, onde_importou, funcao_completa, linha):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO ITENS_DO_ARQUIVO(ARQUIVO_CAMINHO, TIPO, FUNCAO_IMPORTADA, ONDE_IMPORTOU, FUNCAO_COMPLETA, LINHA)
                 VALUES (?,?,?,?,?,?)''',
              (str(arquivo_caminho), tipo, funcao_importada, onde_importou, funcao_completa, linha))
    conn.commit()
    c.close()
    conn.close()


def esc_IMPORT_GERAL(arquivo_caminho, nome, linha, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        '''INSERT INTO IMPORTS_GERAIS(ARQUIVO_CAMINHO, NOME, LINHA, STATUS)
           VALUES (?,?,?,?)''',
        (str(arquivo_caminho), nome, linha, status)
    )
    conn.commit()
    c.close()
    conn.close()

def esc_IMPORT_IGNORADO(arquivo_caminho, nome, linha, motivo):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO IMPORTS_IGNORADOS(ARQUIVO_CAMINHO, NOME, LINHA, MOTIVO)
        VALUES (?,?,?,?)
    """, (str(arquivo_caminho), nome, linha, motivo))

    conn.commit()
    c.close()
    conn.close()



# ========================== ANALISAR ARQUIVO ===========================

# TODO: monta assinatura da função (nome + parâmetros)
def _extrair_assinatura_funcao(node: ast.FunctionDef) -> str:
    """Monta string com nome + parâmetros da função"""
    params = []

    for arg in node.args.args:
        params.append(arg.arg)

    if node.args.vararg:
        params.append(f"*{node.args.vararg.arg}")

    for arg in node.args.kwonlyargs:
        params.append(arg.arg)

    if node.args.kwarg:
        params.append(f"**{node.args.kwarg.arg}")

    return f"{node.name}({', '.join(params)})"

# TODO: analisa arquivo Python e registra imports, funções e classes
def analisar_arquivo(caminho_arquivo):
    nome_arquivo = os.path.basename(caminho_arquivo)

    # LEITURA SEMPRE FUNCIONA
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        st.write(f"📄 LEU: {nome_arquivo}")
    except Exception:
        st.write(f"❌ NÃO LEU: {nome_arquivo}")
        return

    esc_CONTROLE_ARQUIVOS_ABERTOS(caminho_arquivo, conteudo, "")

    # AST COM FALLBACK - NUNCA PARA!
    try:
        tree = ast.parse(conteudo)
        st.write(f"✅ AST OK: {nome_arquivo}")
        usar_ast = True
    except Exception:
        st.write(f"🔄 AST FALHOU {nome_arquivo} - usando REGEX FALLBACK")
        usar_ast = False

    caminho_relativo = Path(caminho_arquivo).relative_to(Pasta_Projeto)
    nome_modulo_base = str(caminho_relativo.with_suffix("")).replace(os.sep, ".")

    contador_registros = 0

    if usar_ast:
	    for node in ast.walk(tree):
		    if isinstance(node, ast.Import):
			    for n in node.names:
				    nome_base = n.name.split(".")[0]

				    # Sempre registra no GERAL
				    esc_IMPORT_GERAL(caminho_arquivo, n.name, node.lineno or 1, "ENCONTRADO")

				    # Se for stdlib/venv → registra como ignorado
				    if nome_base in modulos_ignorar:
					    esc_IMPORT_IGNORADO(caminho_arquivo, n.name, node.lineno or 1, "venv/stdlib")
				    else:
					    # Só manda para ITENS_DO_ARQUIVO se não for ignorado (ou seja, módulo do usuário)
					    esc_ITENS_DO_ARQUIVO(
						    caminho_arquivo,
						    "import",
						    "*",
						    n.name,
						    "*",
						    node.lineno or 1
					    )

				    contador_registros += 1

		    elif isinstance(node, ast.ImportFrom):
			    module = node.module if node.module else ""
			    for n in node.names:
				    full_name = f"{module}.{n.name}" if module else n.name
				    nome_base = module.split(".")[0] if module else ""

				    # Sempre registra no GERAL
				    esc_IMPORT_GERAL(caminho_arquivo, full_name, node.lineno or 1, "ENCONTRADO")

				    # Se for stdlib/venv → registra como ignorado
				    if nome_base in modulos_ignorar:
					    esc_IMPORT_IGNORADO(caminho_arquivo, full_name, node.lineno or 1, "venv/stdlib")
				    else:
					    # Só manda para ITENS_DO_ARQUIVO se não for ignorado
					    funcao = "*" if n.name == "*" else n.name
					    esc_ITENS_DO_ARQUIVO(
						    caminho_arquivo,
						    "import",
						    funcao,
						    module or n.name,
						    funcao,
						    node.lineno or 1
					    )

				    contador_registros += 1

		    elif isinstance(node, ast.FunctionDef):
			    assinatura = _extrair_assinatura_funcao(node)
			    esc_ITENS_DO_ARQUIVO(caminho_arquivo, "function", node.name, nome_modulo_base, assinatura,
			                         node.lineno or 1)
			    contador_registros += 1

		    elif isinstance(node, ast.ClassDef):
			    esc_ITENS_DO_ARQUIVO(caminho_arquivo, "class", node.name, nome_modulo_base, node.name, node.lineno or 1)
			    contador_registros += 1

    st.write(f"✅ {nome_arquivo}: {contador_registros} registros (AST: {usar_ast})")

# TODO: varre todo o projeto Python, chamando análise de cada arquivo
def scan_project():
    st.write(f"🔍 Varredura iniciada em: {Pasta_Projeto}")
    total_arquivos = 0

    for root, dirs, files in os.walk(Pasta_Projeto):
        ignore_dirs = ['.virto_stream', '.venv', '.idea', 'build', 'dist', '.git']
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        st.write(f"\n📁 Pasta: {os.path.basename(root)}")
        st.write(f"   Arquivos .py: {[f for f in files if f.endswith('.py')]}")

        for file in files:
            if file.endswith(".py"):
                caminho_completo = Path(root) / file
                total_arquivos += 1
                st.write(f"   🔄 ANALISANDO: {file}")
                analisar_arquivo(caminho_completo)

    st.write(f"\n🎉 FIM! Total arquivos analisados: {total_arquivos}")


# ========================== VARREDURA .VIRTO_STREAM =======================

@st.cache_data

def scan_virtuestream():
    vstream_path = Pasta_Projeto / ".virto_stream"
    if not vstream_path.exists():
        return

    for root, dirs, files in os.walk(vstream_path):
        ignore_dirs = ['__pycache__']
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                analisar_arquivo(Path(root) / file)
from  rich import *

import json
from collections import defaultdict

def contar_imports_detalhado():

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT ARQUIVO_CAMINHO, NOME, LINHA, STATUS FROM IMPORTS_GERAIS
    """)
    rows = c.fetchall()

    c.close()
    conn.close()

    total = 0
    por_modulo = defaultdict(int)
    por_pacote = defaultdict(int)
    por_status = defaultdict(int)

    for _, nome, _, status in rows:
        total += 1

        base = nome.split(".")[0] if nome else ""
        por_modulo[nome] += 1
        por_pacote[base] += 1
        por_status[status] += 1

    resultado = {
        "total_imports": total,
        "por_status": dict(sorted(por_status.items(), key=lambda x: x[1], reverse=True)),
        "por_pacote": dict(sorted(por_pacote.items(), key=lambda x: x[1], reverse=True)),
        "por_modulo": dict(sorted(por_modulo.items(), key=lambda x: x[1], reverse=True)),
    }

    return resultado

@st.cache_data
def Quando_Abrir_APP_primeira():
    init_db()
    reset_db()
    scan_project()

#Quando_Abrir_APP_primeira()

#st.write(contar_imports_detalhado())

# 🔥 DETECTOR MÓDULOS FALTANDO (PIP + SCRIPTS + DB) CHECAGEM PARA O SCRIPT DE APP_Editor_Run_Preview.py
# 🔥 DETECTOR MÓDULOS FALTANDO (LEVE - SEM PIP / SEM SUBPROCESS)




# _Python_exe já vem do VENVE_DO_PROJETO()
# Exemplo: _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()

def instalar_modulo_(modulo):
    import subprocess

    try:
        subprocess.check_call([_Python_exe, "-m", "pip", "install", modulo])
        return True
    except subprocess.CalledProcessError:
        return False


def botoes_instalacao_(modulos_faltando):

    # Botões individuais
    for mod in modulos_faltando:
        if st.button(f"Instalar {mod}"):
            with st.spinner(f"Instalando {mod}..."):
                sucesso = instalar_modulo(mod)
                if sucesso:
                    st.success(f"{mod} instalado com sucesso!")
                else:
                    st.error(f"Falha ao instalar {mod}")

def checar_modulos_pip_(st,codigo):
    with st.popover(f':material/view_module: Pip Modulos Importados:'):
        with st.container(border=True, height=200):
            log_area = st.empty()
            logs = []

            def log(msg):
                logs.append(str(msg))
                if len(logs) <= 50:  # limita quantidade exibida para não travar Streamlit
                    log_area.code("\n".join(logs), language="bash")
    #log(f"Código recebido:\n{codigo}")

    log("==== INICIANDO CHECAGEM DE MÓDULOS ====")

    # ===================== EXTRAIR IMPORTS VIA AST =====================
    todos_modulos = set()
    try:
        tree = ast.parse(codigo)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                todos_modulos.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                todos_modulos.add(node.module.split('.')[0])
        log(f"Total de módulos encontrados: {len(todos_modulos)}")
    except Exception as e:
        log(f"ERRO AST: {e}")
        return []

    # ===================== CARREGAR IMPORTS IGNORADOS =====================
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
    ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
    log(f"Ignorados no banco: {len(ignorados)}")

    # ===================== CARREGAR ITENS DO ARQUIVO (módulos do projeto) ==========
    c.execute("SELECT DISTINCT ONDE_IMPORTOU FROM ITENS_DO_ARQUIVO WHERE TIPO='import'")
    modulos_projeto = {row[0].split('.')[0].lower() for row in c.fetchall()}
    log(f"Itens do arquivo carregados: {len(modulos_projeto)}")
    c.close()
    conn.close()

    # ===================== STD LIB =====================
    stdlib_path = Path(sysconfig.get_paths()["stdlib"])
    modulos_stdlib = {m.name for m in pkgutil.iter_modules([str(stdlib_path)])} | set(sys.builtin_module_names)
    log(f"Stdlib carregada: {len(modulos_stdlib)} módulos")

    # ===================== VENV =====================
    site_packages = Path(_Venv_path) / "Lib" / "site-packages"
    modulos_venv = {m.name for m in pkgutil.iter_modules([str(site_packages)])} if site_packages.exists() else set()
    log(f"Venv encontrada: {len(modulos_venv)} módulos" if modulos_venv else "Venv não encontrada.")

    # ===================== CLASSIFICAÇÃO =====================
    modulos_faltando = {
        mod for mod in todos_modulos
        if mod.lower() not in ignorados
        and mod.lower() not in modulos_stdlib
        and mod.lower() not in modulos_venv
        and mod.lower() not in modulos_projeto
    }

    log("==== FINALIZADO ====")
    log(f"Faltando: {sorted(modulos_faltando)}")

    botoes_instalacao(modulos_faltando)










def botao_importar_faltantes(faltando: list, codigo_entrada: str, key: str):
    import ast
    import streamlit as st

    logs_btn = []

    def log(msg):
        logs_btn.append(str(msg))

    if not faltando:
        return [], logs_btn

    try:
        linhas = codigo_entrada.splitlines(keepends=True)

        modulo_por_nome = {}
        for nome_faltando in faltando:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                SELECT ONDE_IMPORTOU
                FROM ITENS_DO_ARQUIVO
                WHERE (FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?)
                  AND TIPO IN ('function', 'class')
                  AND ONDE_IMPORTOU != ''
                LIMIT 1
            """, (nome_faltando, f"%{nome_faltando}%"))
            resultado = c.fetchone()
            c.close()
            conn.close()

            if resultado and resultado[0]:
                modulo_por_nome[nome_faltando] = resultado[0]
                log(f"✅ {nome_faltando} → {resultado[0]}")
            else:
                log(f"⚠️ {nome_faltando} sem módulo definido")

        if not modulo_por_nome:
            return [], logs_btn

        # Agrupa por módulo
        modulos_agrupados = {}
        for nome, modulo in modulo_por_nome.items():
            modulos_agrupados.setdefault(modulo, set()).add(nome)

        imports_montados = []

        for modulo_base, nomes in modulos_agrupados.items():
            nomes_existentes = set()

            for linha in linhas:
                linha_strip = linha.strip()
                if linha_strip.startswith(f"from {modulo_base} import "):
                    try:
                        tree_linha = ast.parse(linha_strip)
                        for node in ast.walk(tree_linha):
                            if isinstance(node, ast.ImportFrom) and node.module == modulo_base:
                                nomes_existentes.update(alias.name for alias in node.names)
                    except Exception:
                        pass

            todos_nomes = sorted(nomes_existentes.union(nomes))
            linha_import = f"from {modulo_base} import {', '.join(todos_nomes)}"
            imports_montados.append(linha_import)

            log(f"✅ Import montado: {linha_import}")

        return imports_montados, logs_btn

    except Exception as e:
        log(f"ERRO: ❌ {e}")
        return [], logs_btn
def checar_modulos_locais(key, codigo_entrada):
    import ast
    import re
    logs = []

    def log(msg):
        logs.append(str(msg))

    log("🔍 Checando indentação...")
    linhas = codigo_entrada.splitlines()
    erros_indent = []

    for i, linha in enumerate(linhas, 1):
        linha_strip = linha.lstrip()
        if linha_strip and linha_strip[0] in [' ', '\t']:
            if '\t' in linha and ' ' in linha:
                erros_indent.append(f"L{i}: Mistura tabs+espaços")
                continue
        espacos = len(linha) - len(linha.lstrip())
        if espacos > 0 and espacos % 4 != 0 and '\t' not in linha:
            erros_indent.append(f"L{i}: Indentação {espacos} espaços (deve ser 4)")

    if erros_indent:
        log(f"❌ Indentação: {len(erros_indent)} erro(s)")
        for erro in erros_indent[:5]:
            log(f"  {erro}")
    else:
        log("✅ Indentação OK")

    log("🔍 Checando código...")
    variaveis_soltas = []
    for linha in linhas:
        palavras = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', linha)
        for palavra in palavras:
            if (len(palavra) > 2 and palavra.islower() and
                    palavra not in ['from', 'import', 'print'] and
                    not re.search(r'\b' + palavra + r'\s*\(', linha) and
                    palavra not in ['co', 'id']):
                variaveis_soltas.append(palavra)

    if variaveis_soltas:
        log(f"⚠️  Variáveis soltas: {set(variaveis_soltas)}")
    else:
        log("✅ Código limpo")

    # ================= SINTAXE (NÃO BLOQUEIA MAIS) =================
    tree = None
    try:
        tree = ast.parse(codigo_entrada)
        log("✅ Sintaxe OK")
    except SyntaxError as e:
        log(f"❌ Erro de sintaxe: {traduzir_saida(e)}")
        tree = None

    if "imports_adicionados" not in st.session_state:
        st.session_state["imports_adicionados"] = set()

    faltando = []
    imports_deste_arquivo = set()
    nomes_usados = set()
    funcoes_importadas_explicitamente = set()
    imports_por_modulo = {}
    modulos_com_wildcard = set()

    # ================= AST OU FALLBACK =================
    try:
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        imports_deste_arquivo.add(mod)
                        imports_por_modulo.setdefault(mod, [])

                elif isinstance(node, ast.ImportFrom) and node.module:
                    mod = node.module.split(".")[0]
                    imports_deste_arquivo.add(mod)
                    imports_por_modulo.setdefault(mod, [])

                    tem_wildcard = any(name.name == '*' for name in node.names)
                    if tem_wildcard:
                        modulos_com_wildcard.add(mod)
                        imports_por_modulo[mod] = ['*']
                        log(f"✅ Módulo {mod} tem wildcard (*)")
                    else:
                        for alias in node.names:
                            imports_por_modulo[mod].append(alias.name)
                            funcoes_importadas_explicitamente.add(alias.name)

                elif isinstance(node, ast.Name):
                    nomes_usados.add(node.id)

        else:
            raise Exception("Forçando fallback")

    except:
        log("🔄 Usando regex fallback")
        nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo_entrada)
        nomes_usados = set(nomes_raw)

        padrao_import = r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*?)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,* ]*)'
        matches = re.findall(padrao_import, codigo_entrada, re.IGNORECASE)
        for modulo, funcs in matches:
            mod_name = modulo.split('.')[0]
            imports_deste_arquivo.add(mod_name)
            imports_por_modulo.setdefault(mod_name, [])

            if '*' in funcs:
                modulos_com_wildcard.add(mod_name)
                imports_por_modulo[mod_name] = ['*']
            else:
                funcs_lista = [f.strip() for f in funcs.replace(',', ' ').split() if f.strip()]
                imports_por_modulo[mod_name].extend(funcs_lista)
                funcoes_importadas_explicitamente.update(funcs_lista)

    # ================= BANCO =================
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT FUNCAO_IMPORTADA FROM ITENS_DO_ARQUIVO 
            WHERE TIPO IN ('function', 'class', 'import')
        """)
        definicoes_brutas = [row[0] for row in c.fetchall()]

        definicoes = set()
        for nome in definicoes_brutas:
            nome_limpo = nome.split("(")[0].strip()
            definicoes.add(nome_limpo.lower())
            if "." in nome_limpo:
                definicoes.add(nome_limpo.split(".")[-1].lower())
                definicoes.add(nome_limpo.split(".")[0].lower())

        c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
        ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
        c.close()
        conn.close()

    except Exception as e:
        log(f"Erro banco: {e}")
        definicoes = set()
        ignorados = set()

    def existe_no_banco(nome, definicoes):
        n = nome.lower()
        return any(n in d or d.endswith("." + n) or n.endswith("." + d) for d in definicoes)

    for nome in nomes_usados:
        if (len(nome) < 6 or
                nome.lower() in ['from', 'import', 'print'] or
                (nome[0].islower() and len(nome) < 15 and not nome.endswith(')'))):
            continue

        n = nome.lower()
        importado = False

        for mod, funcs in imports_por_modulo.items():
            if n in [f.lower() for f in funcs]:
                importado = True
                break

        if not importado and modulos_com_wildcard:
            if existe_no_banco(nome, definicoes):
                importado = True

        if importado:
            continue

        if n not in ignorados and existe_no_banco(nome, definicoes):
            faltando.append(nome)

    faltando = sorted(set(faltando) - st.session_state["imports_adicionados"])

    retorno, logs_btn = botao_importar_faltantes(faltando, codigo_entrada, key)

    log('\n'.join(logs_btn))

    return retorno, faltando, logs


def botao_importar_faltantes__(faltando: list, dir_arq_atual: str, codigo_entrada: str, key: str):
    import ast
    import streamlit as st

    logs_btn = []

    def log(msg):
        logs_btn.append(str(msg))


    if not faltando:pass

    elif st.button(f"Importar {', '.join(faltando)}", key=key):
        try:
            # lê o código linha a linha
            with open(dir_arq_atual, "r", encoding="utf-8") as f:
                linhas = f.readlines()


            # resolve módulo e coleta faltando por módulo
            modulo_por_nome = {}
            for nome_faltando in faltando:
                conn = get_conn()
                c = conn.cursor()
                c.execute("""
                    SELECT DISTINCT ONDE_IMPORTOU
                    FROM ITENS_DO_ARQUIVO
                    WHERE (FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?)
                      AND TIPO IN ('function', 'class')
                      AND ONDE_IMPORTOU != ''
                """, (nome_faltando, f"%{nome_faltando}%"))
                resultado = c.fetchone()
                c.close()
                conn.close()

                if resultado and resultado[0]:
                    modulo_por_nome[nome_faltando] = resultado[0]
                    log(f"✅ {nome_faltando} → {resultado[0]}")
                else:
                    log(f"⚠️ {nome_faltando} sem módulo? (usando primeiro import encontrado)")

            # se não encontrou NENHUM módulo, tenta usar o primeiro módulo que aparecer em FROM
            modulo_base = None
            for nome_faltando, mod in modulo_por_nome.items():
                modulo_base = mod
                break

            # se mesmo assim não achou, força algum módulo base pro primeiro FROM
            if not modulo_base and linhas:
                tree = ast.parse("".join(linhas))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        modulo_base = node.module
                        break

            if not modulo_base:
                modulo_base = "modulo_funcao"  # fallback padrão se não tiver nenhum import ainda
                log(f"💡 Nenhum import encontrado → usando módulo base: {modulo_base}")

            # tenta achar a linha FROM deste módulo no código
            linha_from_target = None
            nomes_existentes = set()

            for i, linha in enumerate(linhas):
                linha_strip = linha.strip()
                if linha_strip.startswith(f"from {modulo_base} import "):
                    linha_from_target = i

                    # extrai os nomes da linha existente usando ast
                    try:
                        tree_linha = ast.parse(linha_strip)
                        for node in ast.walk(tree_linha):
                            if isinstance(node, ast.ImportFrom) and node.module == modulo_base:
                                nomes_existentes = {
                                    alias.name for alias in node.names
                                }
                    except SyntaxError:
                        pass
                    break

            # nomes a importar: os que já tava + os faltando
            nomes_para_importar = set(
                [n for n in faltando if modulo_por_nome.get(n) == modulo_base]
            )
            todos_nomes = sorted(nomes_existentes.union(nomes_para_importar))

            # nova linha de import
            nova_line = f"from {modulo_base} import {', '.join(todos_nomes)}\n"

            if linha_from_target is not None:
                # já tinha FROM desse módulo → só troca a linha
                linhas[linha_from_target] = nova_line
            else:
                # nota na prática: aqui você pode decidir o lugar
                # deixei encostando no começo, MAS respeitando eventuais comentários iniciais
                primeira_oficial = 0
                for i, linha in enumerate(linhas):
                    if not linha.strip().startswith("#") and linha.strip():
                        primeira_oficial = i
                        break

                # insere a linha de import ANTES da primeira linha de código real (ou no começo)
                linhas.insert(primeira_oficial, nova_line)

            # escreve tudo de volta
            with open(dir_arq_atual, "w", encoding="utf-8") as f:
                f.writelines(linhas)

            st.session_state.setdefault("imports_adicionados", set()).update(faltando)
            log(
                f"✅ Import criado/atualizado em {modulo_base}: {', '.join(todos_nomes)}"
            )
            from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs_novo
            novo_codigo = Abrir_Arquivo_Select_Tabs_novo(st, dir_arq_atual)

            return novo_codigo, logs_btn

        except Exception as e:
            st.error(f"❌ {e}")
            log(f"ERRO: {e}")

    log(f"Módulos locais faltando: {faltando if len(faltando) > 0 else 'Nenhum'}")

    return codigo_entrada, logs_btn
def checar_modulos_locais__(st, key,dir_arq_atual, codigo_entrada):
    import ast
    import re
    with st.popover(f':material/functions: Minhas Funçoes:'):
        with st.container(border=True, height=200):
            log_area = st.empty()
            logs = []
            def log(msg):
                logs.append(str(msg))
                log_area.code("\n".join(logs), language="bash")

    #log(f"Recebeu código de: {nome_arquivo}")
    #log(f"Código recebido:\n{codigo}")


    # ================= VALIDAÇÃO DE INDENTAÇÃO =================
    log("🔍 Checando indentação...")
    linhas = codigo_entrada.splitlines()
    erros_indent = []

    for i, linha in enumerate(linhas, 1):
        linha_strip = linha.lstrip()
        if linha_strip and linha_strip[0] in [' ', '\t']:
            if '\t' in linha and ' ' in linha:
                erros_indent.append(f"L{i}: Mistura tabs+espaços")
                continue
        espacos = len(linha) - len(linha.lstrip())
        if espacos > 0 and espacos % 4 != 0 and '\t' not in linha:
            erros_indent.append(f"L{i}: Indentação {espacos} espaços (deve ser 4)")

    if erros_indent:
        log(f"❌ Indentação: {len(erros_indent)} erro(s)")
        for erro in erros_indent[:5]:
            log(f"  {erro}")
    else:
        log("✅ Indentação OK")

    # ================= VALIDAÇÃO DE ERROS/VARIÁVEIS SOLTAS =================
    log("🔍 Checando código...")
    variaveis_soltas = []
    for linha in linhas:
        palavras = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', linha)
        for palavra in palavras:
            if (len(palavra) > 2 and palavra.islower() and
                    palavra not in ['from', 'import', 'print'] and
                    not re.search(r'\b' + palavra + r'\s*\(', linha) and
                    palavra not in ['co', 'id']):
                variaveis_soltas.append(palavra)

    if variaveis_soltas:
        log(f"⚠️  Variáveis soltas: {set(variaveis_soltas)}")
    else:
        log("✅ Código limpo")

    # ================= VALIDAÇÃO SINTÁTICA =================
    try:
        ast.parse(codigo_entrada)
        log("✅ Sintaxe OK")


        if "imports_adicionados" not in st.session_state:
            st.session_state["imports_adicionados"] = set()

        faltando = []
        imports_deste_arquivo = set()
        nomes_usados = set()
        funcoes_importadas_explicitamente = set()
        imports_por_modulo = {}
        modulos_com_wildcard = set()

        # ================= AST/REGEX + DETECÇÃO WILDCARD =================
        try:
            tree = ast.parse(codigo_entrada)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        imports_deste_arquivo.add(mod)
                        if mod not in imports_por_modulo:
                            imports_por_modulo[mod] = []
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mod = node.module.split(".")[0]
                    imports_deste_arquivo.add(mod)
                    if mod not in imports_por_modulo:
                        imports_por_modulo[mod] = []

                    tem_wildcard = any(name.name == '*' for name in node.names)
                    if tem_wildcard:
                        modulos_com_wildcard.add(mod)
                        imports_por_modulo[mod] = ['*']
                        log(f"✅ Módulo {mod} tem wildcard (*)")
                    else:
                        for alias in node.names:
                            imports_por_modulo[mod].append(alias.name)
                            funcoes_importadas_explicitamente.add(alias.name)
                elif isinstance(node, ast.Name):
                    nomes_usados.add(node.id)
        except:
            log("🔄 AST falhou, usando regex fallback")
            nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo_entrada)
            nomes_usados = set(nomes_raw)

            padrao_import = r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*?)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,* ]*)'
            matches = re.findall(padrao_import, codigo_entrada, re.IGNORECASE)
            for modulo, funcs in matches:
                mod_name = modulo.split('.')[0]
                imports_deste_arquivo.add(mod_name)
                if mod_name not in imports_por_modulo:
                    imports_por_modulo[mod_name] = []

                if '*' in funcs:
                    modulos_com_wildcard.add(mod_name)
                    imports_por_modulo[mod_name] = ['*']
                    log(f"✅ Módulo {mod_name} tem wildcard (*)")
                else:
                    funcs_lista = [f.strip() for f in funcs.replace(',', ' ').split() if f.strip()]
                    imports_por_modulo[mod_name].extend(funcs_lista)
                    funcoes_importadas_explicitamente.update(funcs_lista)

        # ================= BANCO =================
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                SELECT DISTINCT FUNCAO_IMPORTADA FROM ITENS_DO_ARQUIVO 
                WHERE TIPO IN ('function', 'class', 'import')
            """)
            definicoes_brutas = [row[0] for row in c.fetchall()]

            definicoes = set()
            for nome in definicoes_brutas:
                nome_limpo = nome.split("(")[0].strip()
                definicoes.add(nome_limpo.lower())
                if "." in nome_limpo:
                    definicoes.add(nome_limpo.split(".")[-1].lower())
                    definicoes.add(nome_limpo.split(".")[0].lower())

            c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
            ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
            c.close()
            conn.close()
        except Exception as e:
            log(f"Erro banco: {e}")
            definicoes = set()
            ignorados = set()

        # ================= MATCH PyCharm-STYLE + WILDCARD RESPEITO =================
        def existe_no_banco(nome, definicoes):
            n = nome.lower()
            return any(n in d or d.endswith("." + n) or n.endswith("." + d) for d in definicoes)

        for nome in nomes_usados:
            if (len(nome) < 6 or
                    nome.lower() in ['from', 'import', 'print'] or
                    (nome[0].islower() and len(nome) < 15 and not nome.endswith(')'))):
                continue

            n = nome.lower()
            importado = False

            # Primeiro: checa funções importadas explicitamente
            for mod, funcs in imports_por_modulo.items():
                if n in [f.lower() for f in funcs]:
                    importado = True
                    log(f"✅ {nome} já importado explicitamente de {mod}")
                    break

            # Segundo: checa wildcard - SIMPLIFICADO
            if not importado and modulos_com_wildcard:
                if existe_no_banco(nome, definicoes):
                    # Assume que wildcard cobre funções locais
                    for mod in modulos_com_wildcard:
                        importado = True
                        log(f"✅ {nome} coberto por wildcard {mod}")
                        break

            if importado:
                continue

            if n not in ignorados and existe_no_banco(nome, definicoes):
                faltando.append(nome)
                log(f"❌ {nome} FALTANDO (sem import específico)")

        faltando = sorted(set(faltando) - st.session_state["imports_adicionados"])
        log(f"Nomes usados: {sorted(nomes_usados)[:10]}...")
        log(f"Funções importadas explicitamente: {sorted(funcoes_importadas_explicitamente)}")
        log(f"Imports por módulo: {imports_por_modulo}")
        log(f"Módulos com wildcard: {sorted(modulos_com_wildcard)}")
        log(f"definicoes banco: {len(definicoes)} itens")

        # ================= BOTÃO CONSOLIDA IMPORTS =================
        retorno, logs_btn =  botao_importar_faltantes(faltando,dir_arq_atual, codigo_entrada, key)
        log('\n'.join(logs_btn))
        return retorno

    except SyntaxError as e:
        st.write(traduzir_saida(e))


def botao_importar_faltantes_(faltando: list, caminho: str, key: str):
    import ast
    import streamlit as st

    log_area = st.empty()
    logs = []

    def log(msg):
        logs.append(str(msg))
        log_area.code("\n".join(logs), language="bash")

    if not faltando:
        st.success("📁 Tudo OK!")
        return

    if st.button(f"Importar {', '.join(faltando)}", key=key):
        try:
            # lê o código linha a linha
            with open(caminho, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            if not linhas:
                st.error("❌ Arquivo vazio!")
                return

            # resolve módulo e coleta faltando por módulo
            modulo_por_nome = {}
            for nome_faltando in faltando:
                conn = get_conn()
                c = conn.cursor()
                c.execute("""
                    SELECT DISTINCT ONDE_IMPORTOU
                    FROM ITENS_DO_ARQUIVO
                    WHERE (FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?)
                      AND TIPO IN ('function', 'class')
                      AND ONDE_IMPORTOU != ''
                """, (nome_faltando, f"%{nome_faltando}%"))
                resultado = c.fetchone()
                c.close()
                conn.close()

                if resultado and resultado[0]:
                    modulo_por_nome[nome_faltando] = resultado[0]
                    log(f"✅ {nome_faltando} → {resultado[0]}")
                else:
                    log(f"⚠️ {nome_faltando} sem módulo? (usando primeiro import encontrado)")

            # se não encontrou NENHUM módulo, tenta usar o primeiro módulo que aparecer em FROM
            modulo_base = None
            for nome_faltando, mod in modulo_por_nome.items():
                modulo_base = mod
                break

            # se mesmo assim não achou, força algum módulo base pro primeiro FROM
            if not modulo_base and linhas:
                tree = ast.parse("".join(linhas))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        modulo_base = node.module
                        break

            if not modulo_base:
                modulo_base = "modulo_funcao"  # fallback padrão se não tiver nenhum import ainda
                log(f"💡 Nenhum import encontrado → usando módulo base: {modulo_base}")

            # tenta achar a linha FROM deste módulo no código
            linha_from_target = None
            nomes_existentes = set()

            for i, linha in enumerate(linhas):
                linha_strip = linha.strip()
                if linha_strip.startswith(f"from {modulo_base} import "):
                    linha_from_target = i

                    # extrai os nomes da linha existente usando ast
                    try:
                        tree_linha = ast.parse(linha_strip)
                        for node in ast.walk(tree_linha):
                            if isinstance(node, ast.ImportFrom) and node.module == modulo_base:
                                nomes_existentes = {
                                    alias.name for alias in node.names
                                }
                    except SyntaxError:
                        pass
                    break

            # nomes a importar: os que já tava + os faltando
            nomes_para_importar = set(
                [n for n in faltando if modulo_por_nome.get(n) == modulo_base]
            )
            todos_nomes = sorted(nomes_existentes.union(nomes_para_importar))

            if not todos_nomes:
                st.error("❌ Nenhum nome para importar!")
                return

            # nova linha de import
            nova_line = f"from {modulo_base} import {', '.join(todos_nomes)}\n"

            if linha_from_target is not None:
                # já tinha FROM desse módulo → só troca a linha
                linhas[linha_from_target] = nova_line
            else:
                # nota na prática: aqui você pode decidir o lugar
                # deixei encostando no começo, MAS respeitando eventuais comentários iniciais
                primeira_oficial = 0
                for i, linha in enumerate(linhas):
                    if not linha.strip().startswith("#") and linha.strip():
                        primeira_oficial = i
                        break

                # insere a linha de import ANTES da primeira linha de código real (ou no começo)
                linhas.insert(primeira_oficial, nova_line)

            # escreve tudo de volta
            with open(caminho, "w", encoding="utf-8") as f:
                f.writelines(linhas)

            st.session_state.setdefault("imports_adicionados", set()).update(faltando)
            st.success(
                f"✅ Import criado/atualizado em {modulo_base}: {', '.join(todos_nomes)}"
            )
            st.rerun()

        except Exception as e:
            st.error(f"❌ {e}")
            log(f"ERRO: {e}")

    st.warning(f"📁 FALTANDO: {', '.join(faltando)}")
def checar_modulos_locais_(st, key, codigo, nome_arquivo, caminho):
    import ast
    import re

    log_area = st.empty()
    logs = []

    def log(msg):
        logs.append(str(msg))
        log_area.code("\n".join(logs), language="bash")

    #log(f"Recebeu código de: {nome_arquivo}")
    #log(f"Código recebido:\n{codigo}")
    #log("=" * 50)

    # ================= VALIDAÇÃO DE INDENTAÇÃO =================
    log("🔍 Checando indentação...")
    linhas = codigo.splitlines()
    erros_indent = []

    for i, linha in enumerate(linhas, 1):
        linha_strip = linha.lstrip()
        if linha_strip and linha_strip[0] in [' ', '\t']:  # Mistura espaços/tabs
            if '\t' in linha and ' ' in linha:
                erros_indent.append(f"L{i}: Mistura tabs+espaços")
                continue

        # Indentação inconsistente (4 espaços vs 2 espaços vs tabs)
        espacos = len(linha) - len(linha.lstrip())
        if espacos > 0 and espacos % 4 != 0 and '\t' not in linha:
            erros_indent.append(f"L{i}: Indentação {espacos} espaços (deve ser 4)")

    if erros_indent:
        log(f"❌ Indentação: {len(erros_indent)} erro(s)")
        for erro in erros_indent[:5]:  # Só mostra 5 primeiros
            log(f"  {erro}")
        if len(erros_indent) > 5:
            log(f"  ... e {len(erros_indent) - 5} mais")
    else:
        log("✅ Indentação OK")

    # ================= VALIDAÇÃO SINTÁTICA =================
    try:
        ast.parse(codigo)
        log("✅ Sintaxe OK")
    except SyntaxError as e:
        log(f"❌ Sintaxe: {e}")
        log(f"  Linha {e.lineno}: {linhas[e.lineno - 1] if e.lineno <= len(linhas) else 'EOF'}")

    if "imports_adicionados" not in st.session_state:
        st.session_state["imports_adicionados"] = set()

    faltando = []

    # ================= AST COM FALLBACK =================
    imports_deste_arquivo = set()
    nomes_usados = set()

    try:
        tree = ast.parse(codigo)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_deste_arquivo.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports_deste_arquivo.add(node.module.split(".")[0])
            elif isinstance(node, ast.Name):
                nomes_usados.add(node.id)
    except:
        log("🔄 AST falhou, usando regex fallback")

        # Nomes usados
        nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo)
        nomes_usados = set(nomes_raw)

        # IMPORTS
        for linha in codigo.splitlines():
            linha_lower = linha.lower()
            if 'from ' in linha_lower and 'import' in linha_lower:
                inicio = linha_lower.find('from ') + 5
                fim = linha_lower.find(' import', inicio)
                if fim == -1:
                    fim = linha_lower.find('import', inicio)
                modulo = linha[inicio:fim].strip().split('.')[0]
                if modulo:
                    imports_deste_arquivo.add(modulo)
                    log(f"✅ Import: {modulo}")

        log(f"Imports encontrados: {imports_deste_arquivo}")

    # ================= BANCO =================
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT FUNCAO_IMPORTADA FROM ITENS_DO_ARQUIVO 
            WHERE TIPO IN ('function', 'class', 'import')
        """)
        definicoes_brutas = [row[0] for row in c.fetchall()]

        definicoes = set()
        for nome in definicoes_brutas:
            nome_limpo = nome.split("(")[0].strip()
            definicoes.add(nome_limpo.lower())
            if "." in nome_limpo:
                definicoes.add(nome_limpo.split(".")[-1].lower())
                definicoes.add(nome_limpo.split(".")[0].lower())

        c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
        ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
        c.close()
        conn.close()
    except Exception as e:
        log(f"Erro banco: {e}")
        definicoes = set()
        ignorados = set()

    # ================= MATCH INTELIGENTE =================
    def ja_importado(nome, codigo):
        n = nome.lower()
        for linha in codigo.lower().splitlines():
            if (linha.startswith("from") and "import" in linha and n in linha) or \
                    (linha.startswith("import") and n in linha):
                return True
        return False

    def existe_no_banco(nome, definicoes):
        n = nome.lower()
        return any(n in d or d.endswith("." + n) or n.endswith("." + d) for d in definicoes)

    for nome in nomes_usados:
        n = nome.lower()
        if len(n) <= 2 or n in ['from', 'import', 'print', 'porra', 'ptuta', 'coco']:
            continue

        modulo_coberto = False
        for imp in imports_deste_arquivo:
            try:
                conn = get_conn()
                c = conn.cursor()
                c.execute("""
                    SELECT COUNT(*) FROM ITENS_DO_ARQUIVO 
                    WHERE ONDE_IMPORTOU = ? AND (FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?)
                    AND TIPO IN ('function', 'class')
                """, (imp, nome, f"%{nome}%"))
                tem_funcao = c.fetchone()[0] > 0
                c.close()
                conn.close()

                if tem_funcao:
                    modulo_coberto = True
                    log(f"✅ {nome} coberto por {imp}")
                    break
            except:
                pass

        if (not modulo_coberto and
                n not in ignorados and
                existe_no_banco(nome, definicoes) and
                not ja_importado(nome, codigo)):
            faltando.append(nome)

    faltando = sorted(set(faltando) - st.session_state["imports_adicionados"])
    log(f"Nomes usados: {sorted(nomes_usados)[:10]}...")
    log(f"definicoes banco: {len(definicoes)} itens")
    log(f"Módulos locais faltando: {faltando}")

    # ================= BOTÃO =================
    if faltando:
        if st.button(f"➕ ADICIONAR {', '.join(faltando)} em {nome_arquivo}", key=key):
            try:
                imports_texto = []
                for nome_faltando in faltando:
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute("""
                        SELECT DISTINCT ONDE_IMPORTOU 
                        FROM ITENS_DO_ARQUIVO 
                        WHERE FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?
                        AND TIPO IN ('function', 'class')
                        AND ONDE_IMPORTOU != ''
                    """, (nome_faltando, f"%{nome_faltando}%"))
                    resultado = c.fetchone()
                    c.close()
                    conn.close()

                    if resultado and resultado[0]:
                        modulo = resultado[0]
                        imports_texto.append(f"from {modulo} import *")
                        log(f"✅ {nome_faltando} → from {modulo} import *")
                    else:
                        imports_texto.append(f"from {nome_faltando} import *")

                novo_codigo = "\n".join(imports_texto) + "\n\n" + codigo
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(novo_codigo)
                st.session_state["imports_adicionados"].update(faltando)
                st.success("✅ OK!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")
        st.warning(f"📁 FALTANDO: {', '.join(faltando)}")
    else:
        st.success("📁 Tudo OK!")

    return faltando


def gerar_json_imports(caminho_saida):
    dados = contar_imports_detalhado()

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    return caminho_saida









def checar_modulos_pip(st, codigo):
    with st.popover(f':material/view_module: Pip Modulos Importados:'):
        with st.container(border=True, height=200):
            log_area = st.empty()
            logs = []

            def log(msg):
                logs.append(str(msg))
                if len(logs) <= 50:  # limita quantidade exibida para não travar Streamlit
                    log_area.code("\n".join(logs), language="bash")

            log("==== INICIANDO CHECAGEM DE MÓDULOS ====")

            # ===================== EXTRAIR IMPORTS VIA AST COM LINHAS =====================
            modulos_por_linha = {}  # {linha: modulo}
            try:
                tree = ast.parse(codigo)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            mod = alias.name.split('.')[0]
                            modulos_por_linha[node.lineno] = mod  # Usa lineno do AST para a linha exata
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        mod = node.module.split('.')[0]
                        modulos_por_linha[node.lineno] = mod
                log(f"Total de módulos encontrados: {len(modulos_por_linha)}")
            except Exception as e:
                log(f"ERRO AST: {e}")
                return {}

            # ===================== CARREGAR IMPORTS IGNORADOS =====================
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
            ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
            log(f"Ignorados no banco: {len(ignorados)}")

            # ===================== CARREGAR ITENS DO ARQUIVO (módulos do projeto) ==========
            c.execute("SELECT DISTINCT ONDE_IMPORTOU FROM ITENS_DO_ARQUIVO WHERE TIPO='import'")
            modulos_projeto = {row[0].split('.')[0].lower() for row in c.fetchall()}
            log(f"Itens do arquivo carregados: {len(modulos_projeto)}")
            c.close()
            conn.close()

            # ===================== CLASSIFICAÇÃO COM LINHAS =====================
            modulos_faltando_por_linha = {}  # {linha: modulo} apenas para faltantes
            for linha, mod in modulos_por_linha.items():
                if mod.lower() not in ignorados and mod.lower() not in modulos_stdlib and mod.lower() not in modulos_venv and mod.lower() not in modulos_projeto:
                    modulos_faltando_por_linha[linha] = mod

            log("==== FINALIZADO ====")
            log(f"Faltando: {list(modulos_faltando_por_linha.values())}")

            return modulos_faltando_por_linha  # Retorna {linha: modulo} para posicionar buttons na linha exata


def from_import_functions(faltando: list, codigo_entrada: str, key: str):
    import ast
    import streamlit as st

    logs_btn = []

    def log(msg):
        logs_btn.append(str(msg))

    if not faltando:
        return codigo_entrada, logs_btn  # Retorna o código original se nada faltar

    try:
        linhas = codigo_entrada.splitlines(keepends=True)

        modulo_por_nome = {}
        for nome_faltando in faltando:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                SELECT ONDE_IMPORTOU
                FROM ITENS_DO_ARQUIVO
                WHERE (FUNCAO_IMPORTADA = ? OR FUNCAO_COMPLETA LIKE ?)
                  AND TIPO IN ('function', 'class')
                  AND ONDE_IMPORTOU != ''
                LIMIT 1
            """, (nome_faltando, f"%{nome_faltando}%"))
            resultado = c.fetchone()
            c.close()
            conn.close()

            if resultado and resultado[0]:
                modulo_por_nome[nome_faltando] = resultado[0]
                log(f"✅ {nome_faltando} → {resultado[0]}")
            else:
                log(f"⚠️ {nome_faltando} sem módulo definido")

        if not modulo_por_nome:
            return codigo_entrada, logs_btn  # Retorna original se nenhum módulo

        # Agrupa por módulo
        modulos_agrupados = {}
        for nome, modulo in modulo_por_nome.items():
            modulos_agrupados.setdefault(modulo, set()).add(nome)

        imports_montados = []

        for modulo_base, nomes in modulos_agrupados.items():
            nomes_existentes = set()

            for linha in linhas:
                linha_strip = linha.strip()
                if linha_strip.startswith(f"from {modulo_base} import "):
                    try:
                        tree_linha = ast.parse(linha_strip)
                        for node in ast.walk(tree_linha):
                            if isinstance(node, ast.ImportFrom) and node.module == modulo_base:
                                nomes_existentes.update(alias.name for alias in node.names)
                    except Exception:
                        pass

            todos_nomes = sorted(nomes_existentes.union(nomes))
            linha_import = f"from {modulo_base} import {', '.join(todos_nomes)}"
            imports_montados.append(linha_import)

            log(f"✅ Import montado: {linha_import}")

        # Insere os imports no topo do código
        if imports_montados:
            linhas_codigo = codigo_entrada.splitlines(keepends=True)
            linhas_codigo.insert(0, '\n'.join(imports_montados) + '\n\n')  # Topo com quebras
            codigo_modificado = ''.join(linhas_codigo)
            # Atualiza session_state
            if "imports_adicionados" not in st.session_state:
                st.session_state["imports_adicionados"] = set()
            st.session_state["imports_adicionados"].update(faltando)
            log(f"✅ Imports adicionados no topo: {imports_montados}")
            return codigo_modificado, logs_btn
        else:
            return codigo_entrada, logs_btn

    except Exception as e:
        log(f"ERRO: ❌ {e}")
        return codigo_entrada, logs_btn  # Retorna original em erro

def detectar_problemas_codigo(codigo_entrada):
    """
    Função simples: retorna lista de logs SE tiver problemas, senão retorna lista vazia [].
    """
    logs_problemas = []

    # 🔍 Checando indentação...
    linhas = codigo_entrada.splitlines()
    erros_indent = []

    for i, linha in enumerate(linhas, 1):
        linha_strip = linha.lstrip()
        if linha_strip and linha_strip[0] in [' ', '\t']:
            if '\t' in linha and ' ' in linha:
                erros_indent.append(f"L{i}: Mistura tabs+espaços")
                continue
        espacos = len(linha) - len(linha.lstrip())
        if espacos > 0 and espacos % 4 != 0 and '\t' not in linha:
            erros_indent.append(f"L{i}: Indentação {espacos} espaços (deve ser 4)")

    if erros_indent:
        logs_problemas.append(f"❌ Indentação: {len(erros_indent)} erro(s)")
        for erro in erros_indent[:5]:
            logs_problemas.append(f"  {erro}")

    # 🔍 Checando variáveis soltas...
    variaveis_soltas = set()
    for linha in linhas:
        palavras = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', linha)
        for palavra in palavras:
            if (len(palavra) > 2 and palavra.islower() and
                    palavra not in ['from', 'import', 'print'] and
                    not re.search(r'\b' + palavra + r'\s*\$', linha) and
                    palavra not in ['co', 'id']):
                variaveis_soltas.add(palavra)

    if variaveis_soltas:
        logs_problemas.append(f"⚠️ Variáveis soltas: {variaveis_soltas}")

    # 🔍 Checando sintaxe...
    try:
        ast.parse(codigo_entrada)
    except SyntaxError:
        logs_problemas.append("❌ Erro de sintaxe detectado!")

    return logs_problemas  # VAZIO [] se tudo OK, CHEIO se tem problema

def checar_organizar_codigo(key, codigo_entrada):
    """
    Função principal para organizar o código: primeiro detecta problemas, depois analisa imports,
    consulta banco, detecta faltantes e organiza o código com imports.
    Retorna: codigo_modificado, problemas, faltando, logs
    """

    problemas = detectar_problemas_codigo(codigo_entrada)  # Lista vazia [] se OK

    # Agora, continua com o resto: análise de imports, etc.
    if "imports_adicionados" not in st.session_state:
        st.session_state["imports_adicionados"] = set()

    falta_fuctions = []
    imports_deste_arquivo = set()
    nomes_usados = set()
    funcoes_importadas_explicitamente = set()
    imports_por_modulo = {}
    modulos_com_wildcard = set()

    # ================= AST OU FALLBACK =================
    tree = None
    try:
        tree = ast.parse(codigo_entrada)
    except:
        pass  # Já checado em detectar_problemas_codigo

    try:
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        imports_deste_arquivo.add(mod)
                        imports_por_modulo.setdefault(mod, [])

                elif isinstance(node, ast.ImportFrom) and node.module:
                    mod = node.module.split(".")[0]
                    imports_deste_arquivo.add(mod)
                    imports_por_modulo.setdefault(mod, [])

                    tem_wildcard = any(name.name == '*' for name in node.names)
                    if tem_wildcard:
                        modulos_com_wildcard.add(mod)
                        imports_por_modulo[mod] = ['*']
                    else:
                        for alias in node.names:
                            imports_por_modulo[mod].append(alias.name)
                            funcoes_importadas_explicitamente.add(alias.name)

                elif isinstance(node, ast.Name):
                    nomes_usados.add(node.id)

        else:
            raise Exception("Forçando fallback")

    except:
        nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo_entrada)
        nomes_usados = set(nomes_raw)

        padrao_import = r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*?)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,* ]*)'
        matches = re.findall(padrao_import, codigo_entrada, re.IGNORECASE)
        for modulo, funcs in matches:
            mod_name = modulo.split('.')[0]
            imports_deste_arquivo.add(mod_name)
            imports_por_modulo.setdefault(mod_name, [])

            if '*' in funcs:
                modulos_com_wildcard.add(mod_name)
                imports_por_modulo[mod_name] = ['*']
            else:
                funcs_lista = [f.strip() for f in funcs.replace(',', ' ').split() if f.strip()]
                imports_por_modulo[mod_name].extend(funcs_lista)
                funcoes_importadas_explicitamente.update(funcs_lista)

    # ================= BANCO =================
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT FUNCAO_IMPORTADA FROM ITENS_DO_ARQUIVO 
            WHERE TIPO IN ('function', 'class', 'import')
        """)
        definicoes_brutas = [row[0] for row in c.fetchall()]

        definicoes = set()
        for nome in definicoes_brutas:
            nome_limpo = nome.split("(")[0].strip()
            definicoes.add(nome_limpo.lower())
            if "." in nome_limpo:
                definicoes.add(nome_limpo.split(".")[-1].lower())
                definicoes.add(nome_limpo.split(".")[0].lower())

        c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
        ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}
        c.close()
        conn.close()

    except Exception as e:
        definicoes = set()
        ignorados = set()

    def existe_no_banco(nome, definicoes):
        n = nome.lower()
        return any(n in d or d.endswith("." + n) or n.endswith("." + d) for d in definicoes)

    for nome in nomes_usados:
        if (len(nome) < 6 or
                nome.lower() in ['from', 'import', 'print'] or
                (nome[0].islower() and len(nome) < 15)):
            continue

        n = nome.lower()
        importado = False

        for mod, funcs in imports_por_modulo.items():
            if n in [f.lower() for f in funcs]:
                importado = True
                break

        if not importado and modulos_com_wildcard:
            if existe_no_banco(nome, definicoes):
                importado = True

        if importado:
            continue

        if n not in ignorados and existe_no_banco(nome, definicoes):
            falta_fuctions.append(nome)

    # Removido o filtro de session_state["imports_adicionados"] pra sempre detectar
    falta_fuctions = sorted(set(falta_fuctions))

    # Chama from_import_functions pra organizar e retornar o código com imports no topo
    codigo_modificado, logs_btn = from_import_functions(falta_fuctions, codigo_entrada, key)

    falta_modulo = checar_modulos_pip(st, codigo_entrada)

    return codigo_modificado, problemas, falta_fuctions, falta_modulo
