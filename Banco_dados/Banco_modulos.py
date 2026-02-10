import os
import pkgutil
import sqlite3
import ast
import sys
import sysconfig
from pathlib import Path
import streamlit as st

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

    c.execute(
        '''CREATE TABLE IF NOT EXISTS CONTROLE_ARQUIVOS_ABERTOS(
            CAMINHO_DIRETO TEXT PRIMARY KEY,
            CONTEUDO_DO_ARQUIVO TEXT,
            OBS TEXT
        )'''
    )

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

    # NOVA TABELA → TODOS OS IMPORTS (ignorados + válidos)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS IMPORTS_GERAIS(
            ARQUIVO_CAMINHO TEXT,
            NOME TEXT,
            LINHA INTEGER,
            STATUS TEXT  -- IGNORADO ou VALIDO
        )'''
    )
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

# Para tipo "function" ou "class" → gerar botão, que quando clicado chama abrir_script(caminho).
#Para tipo "import" → retornar lista simples, apenas exibindo nomes e caminhos, sem botão.
#Sempre priorizar o arquivo que CRIOU a função/classe, não quem importou.
#Considerar antes e depois do ponto.

def gerar_predefinidos_com_links():
    def_predefinidos = {}
    from_predefinidos = {}
    def_from = {}

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT ARQUIVO_CAMINHO, TIPO, FUNCAO_IMPORTADA, ONDE_IMPORTOU, FUNCAO_COMPLETA, LINHA
        FROM ITENS_DO_ARQUIVO
    """)
    rows = c.fetchall()
    c.close()
    conn.close()

    for row in rows:
        nome = row[0]
        tipo = row[1]
        caminho = str(row[2])
        linha = row[3] if len(row) > 3 else None

        chave = nome.split(".")[-1]
        base = nome.split(".")[0]

        if tipo in ("function", "class"):
            dados = {
                "caminho": caminho,
                "tipo": tipo,
                "linha": linha,
            }

            def_predefinidos[chave] = dados
            def_from[chave] = dados

            if base not in def_predefinidos:
                def_predefinidos[base] = dados
                def_from[base] = dados

        elif tipo == "import":
            dados = {
                "caminho": caminho,
                "tipo": tipo,
                "linha": linha,
            }

            from_predefinidos[chave] = dados
            def_from[chave] = dados

            if base not in from_predefinidos:
                from_predefinidos[base] = dados
                def_from[base] = dados
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

    nome_modulo_base = os.path.basename(caminho_arquivo).replace('.py', '')
    contador_registros = 0

    if usar_ast:
        # AST NORMAL (código perfeito)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    nome_base = n.name.split(".")[0]
                    if nome_base in modulos_ignorar:
                        esc_IMPORT_IGNORADO(caminho_arquivo, n.name, node.lineno or 1, "venv/stdlib")
                    else:
                        esc_IMPORT_GERAL(caminho_arquivo, n.name, node.lineno or 1, "VALIDO")
                    esc_ITENS_DO_ARQUIVO(caminho_arquivo, "import", "*", n.name, "*", node.lineno or 1)
                    contador_registros += 1

            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for n in node.names:
                    full_name = f"{module}.{n.name}" if module else n.name
                    nome_base = module.split(".")[0] if module else ""
                    if nome_base in modulos_ignorar:
                        esc_IMPORT_IGNORADO(caminho_arquivo, full_name, node.lineno or 1, "venv/stdlib")
                    else:
                        esc_IMPORT_GERAL(caminho_arquivo, full_name, node.lineno or 1, "VALIDO")
                    funcao = "*" if n.name == "*" else n.name
                    esc_ITENS_DO_ARQUIVO(caminho_arquivo, "import", funcao, module or n.name, funcao, node.lineno or 1)
                    contador_registros += 1

            elif isinstance(node, ast.FunctionDef):
                assinatura = _extrair_assinatura_funcao(node)
                esc_ITENS_DO_ARQUIVO(caminho_arquivo, "function", node.name, nome_modulo_base, assinatura,
                                     node.lineno or 1)
                contador_registros += 1

            elif isinstance(node, ast.ClassDef):
                esc_ITENS_DO_ARQUIVO(caminho_arquivo, "class", node.name, nome_modulo_base, node.name, node.lineno or 1)
                contador_registros += 1

    else:
        # REGEX FALLBACK (código cagado) - EXTRAI FUNÇÕES MESMO ASSIM
        import re
        # Pega def função(params):
        funcoes = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', conteudo)
        # Pega class Nome:
        classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:', conteudo)
        # Pega from X import Y
        imports_from = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)', conteudo)
        # Pega import X
        imports = re.findall(r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)', conteudo)

        # REGISTRA FUNÇÕES
        for func in funcoes:
            esc_ITENS_DO_ARQUIVO(caminho_arquivo, "function", func, nome_modulo_base, f"{func}()", 1)
            contador_registros += 1

        # REGISTRA CLASSES
        for cls in classes:
            esc_ITENS_DO_ARQUIVO(caminho_arquivo, "class", cls, nome_modulo_base, cls, 1)
            contador_registros += 1

        # REGISTRA IMPORTS
        for imp in imports:
            nome_base = imp.split(".")[0]
            if nome_base not in modulos_ignorar:
                esc_IMPORT_GERAL(caminho_arquivo, imp, 1, "VALIDO")
            esc_ITENS_DO_ARQUIVO(caminho_arquivo, "import", "*", imp, "*", 1)
            contador_registros += 1

    st.write(f"✅ {nome_arquivo}: {contador_registros} registros (AST: {usar_ast})")


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

Quando_Abrir_APP_primeira()

#st.write(contar_imports_detalhado())

# 🔥 DETECTOR MÓDULOS FALTANDO (PIP + SCRIPTS + DB) CHECAGEM PARA O SCRIPT DE APP_Editor_Run_Preview.py
def checar_modulos_pip(codigo):
    """Detecta módulos externos faltando (pip/venv)"""

    modulos_faltando_pip = set()

    # Extrai imports deste arquivo
    try:
        tree = ast.parse(codigo)
        todos_modulos = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    todos_modulos.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                todos_modulos.add(node.module.split('.')[0])
    except:
        return []

    # Consulta banco - o que já está instalado/ignorado
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT DISTINCT NOME FROM IMPORTS_IGNORADOS")
    ignorados = {row[0].split('.')[0].lower() for row in c.fetchall()}

    c.execute("""
        SELECT DISTINCT SUBSTR(NOME, 1, INSTR(NOME||'.', '.')-1)
        FROM ITENS_DO_ARQUIVO WHERE TIPO = 'import'
    """)
    instalados_projeto = {row[0].lower() for row in c.fetchall()}

    c.close()
    conn.close()

    # Verifica pip real do venv
    pip_list = os.popen(f'"{_Python_exe}" -m pip list').read().lower()

    # Classifica
    for mod in todos_modulos:
        mod_lower = mod.lower()

        # Ignora: stdlib/venv/projeto
        if (mod_lower in ignorados or
                mod_lower in instalados_projeto or
                mod_lower in pip_list):
            continue

        # Tenta importar do venv
        try:
            __import__(mod)
        except ImportError:
            modulos_faltando_pip.add(mod)

    return sorted(modulos_faltando_pip)


import ast


def checar_modulos_locais(st, key, codigo, nome_arquivo, caminho):
    import ast
    import re

    log_area = st.empty()
    logs = []

    def log(msg):
        logs.append(str(msg))
        log_area.code("\n".join(logs), language="bash")

    log(f"Recebeu código de: {nome_arquivo}")
    log(f"Código recebido:\n{codigo}")
    log("=" * 50)

    # ================= VALIDAÇÃO DE INDENTAÇÃO =================
    log("🔍 Checando indentação...")
    linhas = codigo.splitlines()
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
        ast.parse(codigo)
        log("✅ Sintaxe OK")
    except SyntaxError as e:
        log(f"❌ Sintaxe: {e}")

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
        tree = ast.parse(codigo)
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
        nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo)
        nomes_usados = set(nomes_raw)

        padrao_import = r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*?)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,* ]*)'
        matches = re.findall(padrao_import, codigo, re.IGNORECASE)
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
    log(f"Módulos locais faltando: {faltando}")

    # ================= BOTÃO CONSOLIDA IMPORTS =================
    if faltando:
        if st.button(f"➕ ADICIONAR {', '.join(faltando)} em {nome_arquivo}", key=key):
            try:
                imports_consolidados = {}
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
                        if modulo not in imports_consolidados:
                            imports_consolidados[modulo] = []
                        imports_consolidados[modulo].append(nome_faltando)
                        log(f"✅ {nome_faltando} → {modulo}")

                imports_texto = []
                for modulo, funcs in imports_consolidados.items():
                    imports_texto.append(f"from {modulo} import {', '.join(funcs)}")

                novo_codigo = "\n".join(imports_texto) + "\n\n" + codigo
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(novo_codigo)
                st.session_state["imports_adicionados"].update(faltando)
                st.success("✅ OK! Imports consolidados!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")
        st.warning(f"📁 FALTANDO: {', '.join(faltando)}")
    else:
        st.success("📁 Tudo OK!")

    return faltando


def checar_modulos_locais__(st, key, codigo, nome_arquivo, caminho):
    import ast
    import re

    log_area = st.empty()
    logs = []

    def log(msg):
        logs.append(str(msg))
        log_area.code("\n".join(logs), language="bash")

    log(f"Recebeu código de: {nome_arquivo}")
    log(f"Código recebido:\n{codigo}")
    log("=" * 50)

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


def checar_modulos_locais_(st, key, codigo, nome_arquivo, caminho):
    import ast

    log_area = st.empty()
    logs = []

    def log(msg):
        logs.append(str(msg))
        log_area.code("\n".join(logs), language="bash")

    log(f"Recebeu código de: {nome_arquivo}")
    log(f"Código recebido:\n{codigo}")
    log("=" * 50)

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
        import re
        log("🔄 AST falhou, usando regex fallback")

        # Nomes usados
        nomes_raw = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo)
        nomes_usados = set(nomes_raw)

        # IMPORTS: pega TODAS linhas "from X import Y/*"
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

    # ================= MATCH INTELIGENTE NO BANCO =================
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

    # ✅ CHECAGEM INTELIGENTE: MÓDULO IMPORTADO TEM A FUNÇÃO?
    for nome in nomes_usados:
        n = nome.lower()
        if len(n) <= 2 or n in ['from', 'import', 'print', 'porra', 'ptuta', 'coco']:
            continue

        # ✅ VERIFICA SE ALGUM IMPORT EXISTENTE COBRE ESSA FUNÇÃO
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

        # SÓ adiciona se NÃO coberto por nenhum import E outras condições
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

