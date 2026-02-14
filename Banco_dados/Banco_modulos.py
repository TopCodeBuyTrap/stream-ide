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


def init_Controle_Stream_db():
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
        '''CREATE TABLE IF NOT EXISTS FUNCTIONS_CRIADAS(
            ARQUIVO_CAMINHO TEXT,
            TIPO TEXT,
            FUNCAO_IMPORTADA TEXT,
            ONDE_IMPORTOU TEXT,
            FUNCAO_COMPLETA TEXT,
            LINHA INTEGER
        )'''
    )

    # TODO: Tabela que armazena todos os imports PIP_MODS_PYTHON por arquivo
    c.execute(
        '''CREATE TABLE IF NOT EXISTS IMPORTS_GERAIS(
            ARQUIVO_CAMINHO TEXT,
            NOME TEXT,
            LINHA INTEGER,
            STATUS TEXT  -- IGNORADO ou VALIDO
        )'''
    )

    # TODO: Tabela que registra os modulos do python e instalados via pip
    c.execute(""" 
            CREATE TABLE IF NOT EXISTS PIP_MODS_PYTHON(
                ARQUIVO_CAMINHO TEXT,
                NOME TEXT,
                LINHA INTEGER,
                MOTIVO TEXT
            )
        """)

    conn.commit()
    c.close()
    conn.close()


def reset_db():
    """Apaga todos os dados das tabelas, mantendo a estrutura"""
    conn = get_conn()
    c = conn.cursor()

    # Deleta todos os dados de cada tabela (mantém a estrutura)
    tables = [
        'CONTROLE_ARQUIVOS_ABERTOS',
        'FUNCTIONS_CRIADAS',
        'IMPORTS_GERAIS',
        'PIP_MODS_PYTHON'
    ]

    for table in tables:
        c.execute(f'DELETE FROM {table}')


    conn.commit()
    c.close()
    conn.close()

    init_Controle_Stream_db()


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

def esc_FUNCTIONS_CRIADAS(arquivo_caminho, tipo, funcao_importada, onde_importou, funcao_completa, linha):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO FUNCTIONS_CRIADAS(ARQUIVO_CAMINHO, TIPO, FUNCAO_IMPORTADA, ONDE_IMPORTOU, FUNCAO_COMPLETA, LINHA)
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
        INSERT INTO PIP_MODS_PYTHON(ARQUIVO_CAMINHO, NOME, LINHA, MOTIVO)
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

    except Exception:

        return

    esc_CONTROLE_ARQUIVOS_ABERTOS(caminho_arquivo, conteudo, "")

    # AST COM FALLBACK - NUNCA PARA!
    try:
        tree = ast.parse(conteudo)

        usar_ast = True
    except Exception:

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
                        # Só manda para FUNCTIONS_CRIADAS se não for ignorado (ou seja, módulo do usuário)
                        esc_FUNCTIONS_CRIADAS(
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
                        # Só manda para FUNCTIONS_CRIADAS se não for ignorado
                        funcao = "*" if n.name == "*" else n.name
                        esc_FUNCTIONS_CRIADAS(
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
                esc_FUNCTIONS_CRIADAS(caminho_arquivo, "function", node.name, nome_modulo_base, assinatura,
                                     node.lineno or 1)
                contador_registros += 1

            elif isinstance(node, ast.ClassDef):
                esc_FUNCTIONS_CRIADAS(caminho_arquivo, "class", node.name, nome_modulo_base, node.name, node.lineno or 1)
                contador_registros += 1



# TODO: varre todo o projeto Python, chamando análise de cada arquivo
def scan_project():

    total_arquivos = 0

    for root, dirs, files in os.walk(Pasta_Projeto):
        ignore_dirs = ['.virto_stream', '.venv', '.idea', 'build', 'dist', '.git']
        dirs[:] = [d for d in dirs if d not in ignore_dirs]




        for file in files:
            if file.endswith(".py"):
                caminho_completo = Path(root) / file
                total_arquivos += 1

                analisar_arquivo(caminho_completo)





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
    reset_db()
    scan_project()

#Quando_Abrir_APP_primeira()

#

# 🔥 DETECTOR MÓDULOS FALTANDO (PIP + SCRIPTS + DB) CHECAGEM PARA O SCRIPT DE APP_Editor_Run_Preview.py
# 🔥 DETECTOR MÓDULOS FALTANDO (LEVE - SEM PIP / SEM SUBPROCESS)




# _Python_exe já vem do VENVE_DO_PROJETO()
# Exemplo: _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()


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
        FROM FUNCTIONS_CRIADAS
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


def gerar_json_imports(caminho_saida):
    dados = contar_imports_detalhado()

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    return caminho_saida



#---------------------- pipeline de processamento do código-----------------
# ISO AQUI LISTA OS MODULOS INSTALADOS E MANDA PARA O autocomplit do editor
def listar_bibliotecas_instaladas():
    """Lista módulos instalados no venv que podem ser introspecionados, usando VENVE_DO_PROJETO()."""
    # Usa site_packages já definido com _Venv_path de VENVE_DO_PROJETO()
    bibliotecas = []
    for m in pkgutil.iter_modules([str(site_packages)]):
        bibliotecas.append(m.name)

    return bibliotecas


def checar_modulos_pip(codigo):



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

    except Exception as e:

        return {}

    # ===================== CARREGAR IMPORTS IGNORADOS =====================
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT DISTINCT NOME FROM PIP_MODS_PYTHON")
    ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}


    # ===================== CARREGAR ITENS DO ARQUIVO (módulos do projeto) ==========
    c.execute("SELECT DISTINCT ONDE_IMPORTOU FROM FUNCTIONS_CRIADAS WHERE TIPO='import'")
    modulos_projeto = {row[0].split('.')[0].lower() for row in c.fetchall()}

    c.close()
    conn.close()

    # ===================== CLASSIFICAÇÃO COM LINHAS =====================
    modulos_faltando_por_linha = {}  # {linha: modulo} apenas para faltantes
    for linha, mod in modulos_por_linha.items():
        if mod.lower() not in ignorados and mod.lower() not in modulos_stdlib and mod.lower() not in modulos_venv and mod.lower() not in modulos_projeto:
            modulos_faltando_por_linha[linha] = mod




    # Retorna {linha: modulo} para posicionar buttons na linha exata
    return modulos_faltando_por_linha


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
                FROM FUNCTIONS_CRIADAS
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
            SELECT DISTINCT FUNCAO_IMPORTADA FROM FUNCTIONS_CRIADAS 
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

        c.execute("SELECT DISTINCT NOME FROM PIP_MODS_PYTHON")
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

    falta_modulo = checar_modulos_pip(codigo_entrada)

    # Nova: Detectar funções/classes para botões de definição (só do projeto)
    # Substitua a parte de botoes_definicao por:
    botoes_definicao = []
    try:
        tree = ast.parse(codigo_entrada)
        nomes_detectados = [node.id for node in ast.walk(tree) if
                            isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)]

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                nome = node.id
                linha = node.lineno  # Linha real do AST
                coluna = node.col_offset

                # Consulta DB
                conn = get_conn()
                c = conn.cursor()
                c.execute("SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ?", (nome,))
                row = c.fetchone()
                caminho = row[0] if row else None
                c.close()
                conn.close()
                if caminho:
                    botoes_definicao.append({
                        "linha": linha,
                        "coluna": coluna,
                        "nome": nome,
                        "caminho": caminho
                    })

    except Exception as e: pass

    return codigo_modificado, problemas, falta_fuctions, falta_modulo, botoes_definicao

# Tira todos os dados
from typing import List, Dict, Any, Optional
import streamlit as st
def extrair_elementos_codigo(codigo: str) -> List[Dict[str, Any]]:
    """
    Extrai elementos importantes do código via AST, consultando DB para filtrar apenas do projeto.
    Agora inclui chamadas de funções/classes do projeto detectadas via ast.Call.
    Retorna lista de dicionários com 'tipo', 'nome', 'linha', 'coluna', etc.
    Adicionados logs de debug para rastrear o que está sendo processado.
    """
    elementos = []
    print("DEBUG: Iniciando extração de elementos do código.")  # Log inicial
    try:
        tree = ast.parse(codigo)


        # Primeiro, coleta definições e imports (como antes)
        print("DEBUG: Coletando definições e imports...")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                # Consulta DB para verificar se é função do projeto
                conn = get_conn()
                c = conn.cursor()
                c.execute(
                    "SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'function'",
                    (node.name,))
                row = c.fetchone()
                c.close()
                conn.close()
                if row:  # Só adiciona se existir no DB (do projeto)

                    elementos.append({
                        "tipo": "function",
                        "nome": node.name,
                        "linha": node.lineno,
                        "coluna": node.col_offset,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "caminho": row[0]  # Caminho do arquivo do projeto
                    })

            elif isinstance(node, ast.ClassDef):

                # Consulta DB para classes do projeto
                conn = get_conn()
                c = conn.cursor()
                c.execute("SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'class'",
                          (node.name,))
                row = c.fetchone()
                c.close()
                conn.close()
                if row:  # Só adiciona se existir no DB (do projeto)

                    elementos.append({
                        "tipo": "class",
                        "nome": node.name,
                        "linha": node.lineno,
                        "coluna": node.col_offset,
                        "docstring": ast.get_docstring(node),
                        "bases": [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                        "caminho": row[0]
                    })

            elif isinstance(node, ast.Import):

                # Para imports, consultar DB se for módulo do projeto
                for alias in node.names:

                    conn = get_conn()
                    c = conn.cursor()
                    c.execute(
                        "SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'import'",
                        (alias.name,))
                    row = c.fetchone()
                    c.close()
                    conn.close()
                    if row:  # Só adiciona se for do projeto

                        elementos.append({
                            "tipo": "import",
                            "nome": alias.name,
                            "linha": node.lineno,
                            "coluna": node.col_offset,
                            "alias": alias.asname,
                            "caminho": row[0]
                        })

            elif isinstance(node, ast.ImportFrom):

                # Similar para import_from
                conn = get_conn()
                c = conn.cursor()
                c.execute(
                    "SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'import_from'",
                    (node.module,))
                row = c.fetchone()
                c.close()
                conn.close()
                if row:  # Só adiciona se for do projeto

                    for alias in node.names:
                        elementos.append({
                            "tipo": "import_from",
                            "nome": alias.name,
                            "linha": node.lineno,
                            "coluna": node.col_offset,
                            "module": node.module,
                            "alias": alias.asname,
                            "caminho": row[0]
                        })

        # Novo: Detecta chamadas de funções/classes do projeto via ast.Call
        print("DEBUG: Detectando chamadas de funções/classes...")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):

                # Verifica se é uma chamada simples (ex.: func() ou Class())
                if isinstance(node.func, ast.Name):
                    nome_chamado = node.func.id

                    # Consulta DB para ver se é função ou classe do projeto
                    conn = get_conn()
                    c = conn.cursor()
                    # Primeiro, tenta função
                    c.execute(
                        "SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'function'",
                        (nome_chamado,))
                    row_func = c.fetchone()
                    if row_func:

                        elementos.append({
                            "tipo": "call_function",
                            "nome": nome_chamado,
                            "linha": node.lineno,
                            "coluna": node.col_offset,
                            "caminho": row_func[0]
                        })
                    else:
                        # Se não for função, tenta classe
                        c.execute(
                            "SELECT ARQUIVO_CAMINHO FROM FUNCTIONS_CRIADAS WHERE FUNCAO_IMPORTADA = ? AND TIPO = 'class'",
                            (nome_chamado,))
                        row_class = c.fetchone()
                        if row_class:

                            elementos.append({
                                "tipo": "call_class",
                                "nome": nome_chamado,
                                "linha": node.lineno,
                                "coluna": node.col_offset,
                                "caminho": row_class[0]
                            })
                    c.close()
                    conn.close()





    except SyntaxError as e:

        elementos.append({
            "tipo": "error",
            "nome": "SyntaxError",
            "linha": e.lineno or 1,
            "coluna": e.offset or 0,
            "mensagem": str(e)
        })
    except Exception as e:

        elementos.append({
            "tipo": "error",
            "nome": "Exception",
            "linha": 1,
            "coluna": 0,
            "mensagem": str(e)
        })
    return elementos