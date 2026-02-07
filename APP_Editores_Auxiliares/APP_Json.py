import ast

from APP_SUB_Funcitons import controlar_altura


def Jsnon(st,saida_preview):
	col1, col2 = st.columns([1, 30])
	with col1:
		altura_prev = controlar_altura(st, "Explorer", altura_inicial=400, passo=300, maximo=800, minimo=200)
	try:
		with col2.container(height=altura_prev):

			dados = ast.literal_eval(saida_preview)

			linhas_tabela = []
			codigo_gerado = [
				"# === CÓDIGO PRONTO ===",
				"data = response.json()",
				""
			]

			def montar_caminho(partes):
				caminho = "data"
				for p in partes:
					if isinstance(p, int):
						caminho += "[i]"
					else:
						caminho += f"['{p}']"
				return caminho

			def percorrer(obj, partes=None, indent=0):
				if partes is None:
					partes = []

				esp = " " * indent

				if isinstance(obj, dict):
					for k, v in obj.items():
						percorrer(v, partes + [k], indent)

				elif isinstance(obj, list):
					linhas_tabela.append({
						"Chave": ".".join(map(str, partes)),
						"Tipo": f"list[{len(obj)}]",
						"Valor": f"[{len(obj)} itens]"
					})

					codigo_gerado.append("")
					codigo_gerado.append(
						f"{esp}for i, item in enumerate({montar_caminho(partes)}):"
					)

					for item in obj:
						percorrer(item, partes + ["item"], indent + 4)

				else:
					linhas_tabela.append({
						"Chave": ".".join(map(str, partes)),
						"Tipo": type(obj).__name__,
						"Valor": str(obj)
					})

					nome_var = "_".join(str(p) for p in partes if p != "item")
					codigo_gerado.append(
						f"{esp}{nome_var} = {montar_caminho(partes)}"
					)

			percorrer(dados)

			col1, col2 = st.columns([3, 2])

			with col1:
				st.dataframe(linhas_tabela, width='stretch', hide_index=True)
				st.json(dados)

			with col2:
				st.code("\n".join(codigo_gerado), language="python")
				st.metric("Total de chaves", len(linhas_tabela))

			def percorrer(obj, caminho=""):
				if isinstance(obj, dict):
					for k, v in obj.items():
						novo_caminho = f"{caminho}.{k}" if caminho else k
						percorrer(v, novo_caminho)
				elif isinstance(obj, list):
					for i, item in enumerate(obj):
						percorrer(item, f"{caminho}[{i}]")
					linhas_tabela.append({
						"Chave": caminho,
						"Tipo": f"list[{len(obj)}]",
						"Valor": f"[{len(obj)} itens]"
					})
				else:
					valor = str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj)
					linhas_tabela.append({
						"Chave": caminho,
						"Tipo": type(obj).__name__,
						"Valor": valor
					})
					nome_var = caminho.replace(".", "_").replace("[", "_").replace("]", "").strip("_")
					caminho_json = caminho.replace(".", "['").replace("[", "['")
					codigo_gerado.append(f"{nome_var} = data{caminho_json}")
					codigo_gerado.append(f'print(f"{nome_var.upper()}: {{ {nome_var} }}")')

			percorrer(dados)

			col1.success(f"✅ {len(linhas_tabela)} chaves")

			col2.code("\n".join(codigo_gerado), language="python")
	except SyntaxError:
		pass
	except ValueError:
		pass
	st.write('')
	st.write('')
