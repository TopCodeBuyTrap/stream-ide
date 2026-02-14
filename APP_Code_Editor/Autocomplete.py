import os
from pathlib import Path
import jedi  # pip install jedi
import inspect
import streamlit as st
import ast  # Para extrair imports com precisão

from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO
from Banco_dados import gerar_auto_complete_EDITOR

# ===== Exemplo de uso no editor =====
def_from, def_predefinidos, from_predefinidos = gerar_auto_complete_EDITOR()


def carregar_modulos_venv():
	import sys
	import pkgutil
	from pathlib import Path
	_Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
	site_packages = Path(_Venv_path) / "Lib" / "site-packages"
	sys.path.insert(0, str(site_packages))

	modulos = {}

	# módulos da venv
	for m in pkgutil.iter_modules([str(site_packages)]):
		modulos[m.name] = [m.name]

	# módulos do projeto (def_predefinidos do DB)
	for nome, dados in def_predefinidos.items():
		modulos[nome] = os.path.basename(dados["caminho"])

	# 3. Fontes personalizadas
	outras_fontes = [
		{"nome": "filha", "valor": "isadora"},
		{"nome": "amigo", "valor": "joao"}
	]
	for item in outras_fontes:
		modulos[item["nome"]] = item["valor"]

	return modulos


def extrair_imports_do_codigo(codigo):
	"""
    Extrai imports do código usando AST (mais preciso que regex).
    Retorna dict {modulo: alias}.
    """
	imports = {}
	try:
		tree = ast.parse(codigo)
		for node in ast.walk(tree):
			if isinstance(node, ast.Import):
				for alias in node.names:
					modulo = alias.name.split('.')[0]  # Pega o módulo base
					alias_name = alias.asname or alias.name
					imports[modulo] = alias_name
			elif isinstance(node, ast.ImportFrom):
				if node.module:
					modulo = node.module.split('.')[0]
					imports[modulo] = modulo  # Alias padrão para from import
	except SyntaxError:
		pass  # Código inválido – pula
	return imports


def gerar_completions_de_modulo(nome_modulo, alias=""):
	"""
    Introspeciona um módulo e gera lista de completions.
    "meta" inclui o módulo pai (ex.: "streamlit.function").
    """
	completions = []
	try:
		modulo = __import__(nome_modulo)

		for attr_name in dir(modulo):
			if not attr_name.startswith('_'):
				attr = getattr(modulo, attr_name)
				tipo = "attribute"
				if inspect.isfunction(attr) or inspect.ismethod(attr) or (callable(attr) and not inspect.isclass(attr)):
					tipo = "function"
				elif inspect.isclass(attr):
					tipo = "class"

				chave = f"{alias}.{attr_name}" if alias else f"{nome_modulo}.{attr_name}"
				meta_com_modulo = f"{nome_modulo}.{tipo}"

				completions.append({
					"caption": chave,
					"value": chave,
					"meta": meta_com_modulo,
					"score": 500
				})
	except ImportError:pass
	except Exception as e:pass

	return completions


def Completar(st):
    """
    Gera completions com filtragem por prefixo da última linha (para trigger manual com Ctrl+Space).
    """
    completions = []

    # Parte 1: DB (funções/classes do projeto)
    if "modulos_venv" not in st.session_state:
        st.session_state.modulos_venv = carregar_modulos_venv()

    for nome, origem in st.session_state.modulos_venv.items():
        completions.append({
            "caption": nome,
            "value": nome,
            "meta": origem,
            "name": nome,
            "score": 400
        })

    # Parte 2: Introspecção dinâmica de módulos importados no código atual
    texto_atual = st.session_state.get("texto_editor", "")
    if texto_atual:
        imports = extrair_imports_do_codigo(texto_atual)
        for modulo, alias in imports.items():
            comps = gerar_completions_de_modulo(modulo, alias)
            completions.extend(comps)

    # Parte 3: jedi (para bibliotecas externas)
    if texto_atual:
        try:
            linhas = texto_atual.splitlines()
            linha = len(linhas) - 1  # Última linha
            coluna = len(linhas[-1]) if linhas else 0
            script = jedi.Script(code=texto_atual, path=None)
            jedi_completions = script.complete(line=linha + 1, column=coluna)

            for comp in jedi_completions:
                tipo = getattr(comp, 'type', 'jedi')
                modulo_pai = comp.name.split('.')[0] if '.' in comp.name else 'unknown'
                #meta_com_modulo = f"{modulo_pai}.{tipo}"
                meta_com_modulo = f"{modulo_pai}.{tipo}" # TODO: mudei aqui para aparecer apenas o modulo pai

                completions.append({
                    "caption": comp.name,
                    "value": comp.name,
                    "meta": meta_com_modulo,
                    "name": comp.name,
                    "score": 500
                })
        except Exception as e:pass

    # Filtragem por prefixo: última palavra da última linha (simples e eficaz)
    if texto_atual:
        linhas = texto_atual.splitlines()
        if linhas:
            linha_atual = linhas[-1]
            palavras = linha_atual.split()
            palavra_atual = palavras[-1] if palavras else ""
            if palavra_atual:
                completions = [comp for comp in completions if comp["value"].startswith(palavra_atual)]

    # Remove duplicatas
    seen = set()
    unique_completions = []
    for comp in completions:
        if comp["value"] not in seen:
            unique_completions.append(comp)
            seen.add(comp["value"])

    return unique_completions