import re

import requests

from APP_SUB_Controle_Driretorios import _DIRETORIO_EXECUTAVEL_
from APP_SUB_Funcitons import wrap_text, controlar_altura


def IA_openrouter(st,codigo_completo_do_editor,saida_preview,linguagem):
	col1, col2 = st.columns([1, 30])
	with col1:
		altura_prev = controlar_altura(st, "Ajuda", altura_inicial=400, passo=300, maximo=800, minimo=200)
	with col2.container(border=True, height=altura_prev):

		c1, c2 = st.columns([1, 3])

		# Pega código do editor (ajuste se a key/variável for diferente de "codigo_completo_do_editor")
		# st.write(codigo_completo_do_editor)
		# st.write(saida_preview)
		# Selectbox de ações (fora do expander para sempre visível)
		acao_ia = c1.selectbox(
			"Ação da IA",
			[
				"Gerar código novo",
				"Completar código automaticamente",
				"Refatorar código existente",
				"Explicar código",
				"Encontrar bugs e corrigir",
				"Otimizar performance",
				"Gerar testes",
				"Gerar documentação",
				"Analisar segurança",
				"Converter código entre linguagens"
			],
			index=0
		)

		prompt_ia = c1.text_area(
			"Descreva o pedido (detalhes ajudam!):",
			placeholder="ex: 'otimize esse loop para rodar mais rápido' ou 'gere testes com pytest'",
			key="prompt_ia_unique"
		)
		with c1:
			if c1.button("Gerar / Aplicar", type="primary", width='stretch'):

				with st.spinner("Consultando IA..."):
					# Adapta instrução
					instrucoes = {
						"Gerar código novo": "Gere código Python novo e completo baseado na descrição.",
						"Completar código automaticamente": "Complete o código incompleto mantendo estilo e imports.",
						"Refatorar código existente": "Refatore o código: melhore clareza, performance e robustez.",
						"Explicar código": "Explique o código de forma clara, passo a passo.",
						"Encontrar bugs e corrigir": "Identifique bugs e sugira correções.",
						"Otimizar performance": "Otimize o código para melhor velocidade e eficiência.",
						"Gerar testes": "Gere testes unitários (pytest ou unittest).",
						"Gerar documentação": "Gere docstrings e comentários técnicos.",
						"Analisar segurança": "Analise vulnerabilidades e sugira fixes.",
						"Converter código entre linguagens": "Converta para outra linguagem (especifique qual)."
					}

					contexto = codigo_completo_do_editor + "\n====\n" + saida_preview
					instrucao_base = instrucoes.get(acao_ia, "Auxilie com o código.")

					if acao_ia == "Explicar código":
						full_prompt = f"""
	                            Você é um desenvolvedor sênior.
	                            Explique o código abaixo de forma clara e sequencial.

	                            {contexto}

	                            Pedido do usuário:
	                            {prompt_ia}

	                            Responda somente em texto.
	                            """
					elif acao_ia == "Gerar testes":
						full_prompt = f"""
	                            Você é especialista em testes unitários em linguagens de programação.
	                            Gere testes usando pytest ou unittest para o código abaixo.

	                            {contexto}

	                            Pedido do usuário:
	                            {prompt_ia}

	                            Responda somente com o código dos testes.
	                            """
					elif acao_ia == "Gerar documentação":
						full_prompt = f"""
	                            Você é especialista em documentação técnica.
	                            Adicione docstrings e comentários ao código abaixo.

	                            {contexto}

	                            Pedido do usuário:
	                            {prompt_ia}

	                            Responda somente com o código documentado.
	                            """
					elif acao_ia == "Analisar segurança":
						full_prompt = f"""
	                            Você é especialista em segurança de software.
	                            Analise o código abaixo, descreva vulnerabilidades e apresente correções.

	                            {contexto}

	                            Pedido do usuário:
	                            {prompt_ia}

	                            Responda com análise em texto e, quando aplicável, código corrigido.
	                            """
					else:
						full_prompt = f"""
	                            Você é um desenvolvedor sênior em linguagens de programação.
	                            Aplique a instrução abaixo ao código fornecido.

	                            {contexto}

	                            Pedido do usuário:
	                            {prompt_ia}
	                            {instrucao_base}
	                            Responda somente com o código final."""

					# Chama API do OpenRouter
					headers = {
						"Authorization": f"Bearer {_DIRETORIO_EXECUTAVEL_('chave_api')}",
						"Content-Type": "application/json",
						"HTTP-Referer": "http://localhost:8501",
						"X-Title": "Stream-IDE IA"
					}
					payload = {
						"model": "arcee-ai/trinity-large-preview:free",
						"messages": [{"role": "user", "content": full_prompt}],
						"temperature": 0.7
					}

					try:
						resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers,
						                     json=payload)
						resp.raise_for_status()
						novo_codigo = resp.json()["choices"][0]["message"]["content"].strip()

						# Cola no editor
						_ = novo_codigo
						novo_codigo = re.sub(r'```(?:\w*)', '', novo_codigo, flags=re.MULTILINE | re.IGNORECASE)
						novo_codigo = re.sub(r'```', '', novo_codigo, flags=re.MULTILINE | re.IGNORECASE)
						novo_codigo = novo_codigo.strip()
						with c2:
							# if st.button("📋 Copiar"):
							# st.write(f"Copiado! Cole no editor.")
							# _.clipboard = novo_codigo  # guarda pra uso depois
							st.code(wrap_text(novo_codigo, 100), language=linguagem)


					except Exception as e:
						c2.error(f"🪲 Falha na IA: {str(e)}")
	st.write('')
	st.write('')