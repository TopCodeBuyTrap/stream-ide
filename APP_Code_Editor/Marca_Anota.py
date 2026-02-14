import ast
import re
import time
from typing import List, Dict, Any, Optional
from pyflakes.api import check
from pyflakes.reporter import Reporter
import io
import streamlit as st

from Banco_dados import extrair_elementos_codigo

# Tente importar flake8; se não, fallback para pyflakes só
try:
	from flake8.api import legacy as flake8

	FLAKE8_DISPONIVEL = True
except ImportError:
	FLAKE8_DISPONIVEL = False

from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida

# Importe a função de extração de elementos do projeto (versão atualizada)


class Marcadores_Anotatios:
	"""Classe para gerar annotations e markers para o code_editor, com análise avançada de código Python, integrada com elementos do projeto via DB."""

	# Constantes configuráveis
	LIMITE_LINHA_PADRAO = 100
	TIMEOUT_PADRAO = 1.0  # segundos

	@st.cache_data(hash_funcs={str: lambda s: hash(s[:1000])}, ttl=30)  # Cache 30s, hash otimizado para strings grandes
	def get_props_cached(codigo: str, limite_linha: int = LIMITE_LINHA_PADRAO, ignore_rules: Optional[List[str]] = None,
	                     timeout: float = TIMEOUT_PADRAO) -> Dict[str, Any]:
		"""Função externa com cache para gerar props. Agora integrada com elementos do projeto."""
		instance = Marcadores_Anotatios()
		return instance.get_props(codigo, limite_linha, ignore_rules, timeout)

	def __init__(self):
		pass

	def get_props(self, codigo: str, limite_linha: int = LIMITE_LINHA_PADRAO, ignore_rules: Optional[List[str]] = None,
	              timeout: float = TIMEOUT_PADRAO) -> Dict[str, Any]:
		"""Retorna props com markers e annotations para o code_editor, com timeout e integração com elementos do projeto."""

		if not codigo.strip():

			return {"markers": [], "annotations": []}

		start_time = time.time()
		ignore_rules = ignore_rules or []

		# Extrai elementos do projeto via DB (com cache implícito se usado em get_props_cached)
		try:
			elementos_projeto = extrair_elementos_codigo(codigo)

		except Exception as e:

			elementos_projeto = []  # Fallback se DB falhar

		try:
			markers = self.get_markers(codigo, limite_linha, ignore_rules, elementos_projeto)
			annotations = self.get_annotations(codigo, limite_linha, ignore_rules, elementos_projeto)


			# Verifica timeout
			if time.time() - start_time > timeout:
				annotations.append({"row": 0, "type": "warning", "text": "⏱️ Análise interrompida por timeout"})
				markers = []  # Limpa markers se timeout


			result = {"markers": markers, "annotations": annotations}

			return result
		except Exception as e:
			# Fallback seguro

			return {
				"markers": [],
				"annotations": [{"row": 0, "type": "error", "text": f"💥 Erro na análise: {str(e)}"}]
			}

	def _parse_ast(self, codigo: str) -> Optional[ast.AST]:
		"""Parse AST seguro com fallback."""
		try:
			return ast.parse(codigo)
		except SyntaxError:
			return None

	def _checar_erros_pyflakes(self, codigo: str) -> List[Dict[str, Any]]:
		"""Checa erros com pyflakes, parsing robusto."""
		erros_io = io.StringIO()
		reporter = Reporter(erros_io, erros_io)
		try:
			check(codigo, filename="<string>", reporter=reporter)
		except Exception:
			return []

		erros_texto = erros_io.getvalue().strip()
		erros = []
		if erros_texto:
			for linha in erros_texto.splitlines():
				match = re.match(r".*:(\d+):\s*(.*)", linha)  # Regex robusto
				if match:
					linha_num = int(match.group(1))
					mensagem = match.group(2).strip()
					erros.append({"line": linha_num, "message": traduzir_saida(mensagem)})
		return erros

	def _checar_erros_flake8(self, codigo: str) -> List[Dict[str, Any]]:
		"""Checa erros com flake8 se disponível."""
		if not FLAKE8_DISPONIVEL:
			return []

		try:
			style_guide = flake8.get_style_guide()
			report = style_guide.check_files([("<string>", codigo)])
			erros = []
			for violation in report.get_violations():
				erros.append({
					"line": violation.line_number,
					"message": traduzir_saida(violation.message)
				})
			return erros
		except Exception:
			return []

	def _calcular_complexidade(self, node: ast.FunctionDef) -> int:
		"""Calcula complexidade ciclomática básica (simplificada)."""
		cc = 1  # Base
		for subnode in ast.walk(node):
			if isinstance(subnode, (ast.If, ast.For, ast.While, ast.Try)):
				cc += 1
		return cc

	def get_annotations(self, codigo: str, limite_linha: int = LIMITE_LINHA_PADRAO,
	                    ignore_rules: Optional[List[str]] = None,
	                    elementos_projeto: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
		"""Gera annotations profissionais com regras configuráveis e integração com elementos do projeto."""
		annotations: List[Dict[str, Any]] = []
		linhas = codigo.split("\n")
		tree = self._parse_ast(codigo)
		ignore_rules = ignore_rules or []
		elementos_projeto = elementos_projeto or []

		def add(row: int, level: str, emoji: str, msg: str, rule: str):
			if rule not in ignore_rules:
				annotations.append({
					"row": row,
					"type": level,
					"text": f"{emoji} {msg}"
				})

		# 1. Erros pyflakes e flake8
		erros_pyflakes = self._checar_erros_pyflakes(codigo)
		for e in erros_pyflakes:
			add(e["line"] - 1, "error", "❌", e["message"], "pyflakes")

		erros_flake8 = self._checar_erros_flake8(codigo)
		for e in erros_flake8:
			add(e["line"] - 1, "error", "🔍", e["message"], "flake8")

		# 2. Análise textual
		for i, linha in enumerate(linhas):
			l = linha.strip()
			if re.search(r"\b(TODO|FIXME|BUG|HACK|XXX|NOTE)\b", l, re.I):
				add(i, "warning", "🧩", "Pendência anotada no código", "todo")
			if len(linha) > limite_linha:
				add(i, "warning", "📏", f"Linha excede {limite_linha} caracteres", "longline")
			if l.startswith("#") and len(linha) > 80:
				add(i, "warning", "💬", "Comentário excessivamente longo", "longcomment")
			if "print(" in l and not l.startswith("#"):
				add(i, "warning", "🐞", "Uso de print como debug", "printdebug")
			if "eval(" in l or "exec(" in l:
				add(i, "error", "☠️", "Uso de eval/exec (risco de segurança)", "evalexec")
			if l.startswith("global "):
				add(i, "warning", "🌍", "Uso de variável global", "globalvar")
			if l == "pass":
				add(i, "warning", "🕳️", "Bloco vazio (pass)", "passblock")
			if l.startswith("except:") or ("except Exception" in l and "as" not in l):
				add(i, "error", "🚫", "Except genérico oculta erros reais", "broadexcept")

		# 3. Análise AST (mantém regras gerais, mas filtra duplicatas com elementos do projeto)
		if tree:
			for node in ast.walk(tree):
				if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
					has_doc = ast.get_docstring(node) is not None
					cc = self._calcular_complexidade(node)
					msg = f"Função '{node.name}'"
					if not has_doc:
						msg += " sem docstring"
						level = "warning"
					else:
						level = "info"
					if cc > 10:
						msg += f" (complexidade alta: {cc})"
						level = "warning"
					add(node.lineno - 1, level, "⚙️", msg, "function")

				elif isinstance(node, ast.ClassDef):
					has_doc = ast.get_docstring(node) is not None
					has_methods = any(isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) for sub in node.body)
					msg = f"Classe '{node.name}'"
					if not has_doc:
						msg += " sem docstring"
						level = "warning"
					elif not has_methods:
						msg += " sem métodos"
						level = "info"
					else:
						level = "info"
					add(node.lineno - 1, level, "🏷️", msg, "class")

				elif isinstance(node, ast.Import):
					for alias in node.names:
						add(node.lineno - 1, "info", "📦", f"Import: {alias.name}", "import")

				elif isinstance(node, ast.ImportFrom):
					add(node.lineno - 1, "info", "📥", f"Import from {node.module or 'unknown'}", "importfrom")
		else:
			try:
				ast.parse(codigo)
			except SyntaxError as e:
				add((e.lineno or 1) - 1, "error", "💥", f"Erro de sintaxe: {e.msg}", "syntax")

		# 4. Integração com elementos do projeto (annotations extras para destacar o que é do usuário/projeto)

		for elem in elementos_projeto:
			row = elem.get("linha", 1) - 1  # Ajusta para 0-based
			nome = elem.get("nome", "desconhecido")
			tipo = elem.get("tipo", "unknown")

			if tipo == "function":
				args = elem.get("args", [])
				doc = elem.get("docstring", "")
				msg = f"Função do projeto: {nome}({', '.join(args)})"
				if doc:
					msg += f" - Doc: {doc[:50]}..." if len(doc) > 50 else f" - Doc: {doc}"
				add(row, "info", "🔧", msg, "projeto_function")

			elif tipo == "class":
				bases = elem.get("bases", [])
				doc = elem.get("docstring", "")
				msg = f"Classe do projeto: {nome}"
				if bases:
					msg += f" (herda de {', '.join(bases)})"
				if doc:
					msg += f" - Doc: {doc[:50]}..." if len(doc) > 50 else f" - Doc: {doc}"
				add(row, "info", "🏗️", msg, "projeto_class")

			elif tipo == "import":
				alias = elem.get("alias", "")
				msg = f"Import do projeto: {nome}"
				if alias:
					msg += f" as {alias}"
				add(row, "info", "📚", msg, "projeto_import")

			elif tipo == "import_from":
				module = elem.get("module", "")
				alias = elem.get("alias", "")
				msg = f"Import from projeto: from {module} import {nome}"
				if alias:
					msg += f" as {alias}"
				add(row, "info", "📖", msg, "projeto_import_from")

			elif tipo == "call_function":
				# Novo: Para chamadas de funções do projeto
				msg = f"Chamada de função do projeto: {nome}"
				add(row, "info", "🔄", msg, "projeto_call_function")

			elif tipo == "call_class":
				# Novo: Para chamadas de classes do projeto
				msg = f"Chamada de classe do projeto: {nome}"
				add(row, "info", "🏭", msg, "projeto_call_class")

			elif tipo == "error":
				msg = elem.get("mensagem", "Erro desconhecido")
				add(row, "error", "🚨", f"Erro no projeto: {msg}", "projeto_error")


		return annotations

	def get_markers(self, codigo: str, limite_linha: int = LIMITE_LINHA_PADRAO,
	                ignore_rules: Optional[List[str]] = None,
	                elementos_projeto: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
		"""Gera markers visuais, com fallbacks e integração com elementos do projeto."""
		markers: List[Dict[str, Any]] = []
		linhas = codigo.split("\n")
		tree = self._parse_ast(codigo)
		ignore_rules = ignore_rules or []
		elementos_projeto = elementos_projeto or []

		for i, linha in enumerate(linhas):
			if len(linha) > limite_linha and "longline" not in ignore_rules:
				markers.append({
					"startRow": i,
					"startCol": limite_linha,
					"endRow": i,
					"endCol": len(linha),
					"className": "marker-longline",
					"type": "range"
				})
			if linha.strip() == "pass" and "passblock" not in ignore_rules:
				markers.append({
					"startRow": i,
					"startCol": 0,
					"endRow": i,
					"endCol": len(linha),
					"className": "marker-pass",
					"type": "fullLine"
				})

		if tree:
			for node in ast.walk(tree):
				if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
					end_lineno = node.end_lineno or node.lineno
					markers.append({
						"startRow": node.lineno - 1,
						"startCol": 0,
						"endRow": end_lineno - 1,
						"endCol": 0,
						"className": "marker-function-scope",
						"type": "fullBlock"
					})
				elif isinstance(node, ast.ClassDef):
					end_lineno = node.end_lineno or node.lineno
					markers.append({
						"startRow": node.lineno - 1,
						"startCol": 0,
						"endRow": end_lineno - 1,
						"endCol": 0,
						"className": "marker-class-scope",
						"type": "fullBlock"
					})

		# Integração com elementos do projeto (markers especiais para destacar blocos do projeto)

		for elem in elementos_projeto:
			row = elem.get("linha", 1) - 1
			tipo = elem.get("tipo", "unknown")

			if tipo in ["function", "class"]:
				# Assume bloco até o próximo elemento ou fim (simplificado; pode ajustar com end_lineno se disponível)
				end_row = row + 1  # Placeholder; em produção, calcule baseado em AST ou DB
				markers.append({
					"startRow": row,
					"startCol": 0,
					"endRow": end_row,
					"endCol": 0,
					"className": f"marker-projeto-{tipo}",
					"type": "fullBlock"
				})

			elif tipo in ["call_function", "call_class"]:
				# Novo: Marker para chamadas (ex.: sublinhado na linha)
				markers.append({
					"startRow": row,
					"startCol": elem.get("coluna", 0),
					"endRow": row,
					"endCol": elem.get("coluna", 0) + len(elem.get("nome", "")),
					"className": f"marker-projeto-{tipo}",
					"type": "range"
				})


		return markers