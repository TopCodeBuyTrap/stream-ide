import ast
import json
import re
from pathlib import Path
from platform import java_ver

import streamlit as st
from dynamic_tabs import dynamic_tabs
from streamlit_ace import st_ace
import sys
import threading
import queue
import requests
import os, time

from APP_Catalogo import arquivo_ja_catalogado
from APP_SUB_Funcitons import Identificar_linguagem, Button_Nao_Fecha, Sinbolos, Anotations_Editor, Marcadores_Editor, \
    wrap_text, chec_se_arq_do_projeto
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs


def Editor_Simples_(col1, Top4, ColunaSelect, CAMINHHOS, THEMA_EDITOR, EDITOR_TAM_MENU, colStop, ColunaRun):
    # SUAS FUNÇÕES INTEGRADAS
    def arquivo_ja_catalogado(caminho):
        import os
        import json
        CAMINHO_JSON = os.path.join(".virto_stream", ".catalogos.json")
        if not os.path.exists(CAMINHO_JSON):
            return False, None
        with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
            catalogos = json.load(f)
        chave = os.path.abspath(caminho)
        if chave in catalogos:
            return True, catalogos[chave]
        return False, None

    def nome_curto(nome, limite=8):  # limite=8 como você usa
        base, ext = os.path.splitext(nome)
        if ext:
            return base[:limite] + ext
        return nome[:limite]


    _ = st.session_state

    # ✅ ABAS COM EMOJI + CATALOGADO + NOME CURTO
    nomes_completos = []
    for caminho in CAMINHHOS:
        nome_arquivo = os.path.basename(caminho)
        ja_catalogado, info = arquivo_ja_catalogado(caminho)
        cat = ':material/star_rate:' if ja_catalogado else ''
        em = Sinbolos(nome_arquivo)
        nome_formatado = f"{em}{nome_curto(nome_arquivo, 8)}{cat}"
        nomes_completos.append(nome_formatado)

    # RESULTADO das abas:
    # ⚡javali.js⭐    🐍main.py     🐍teste_2

    abas = st.tabs(nomes_completos)  # ← EMOJIS + ⭐ + NOME CURTO!

    # LOOP DO EDITOR
    for I, aba in enumerate(abas):
        with aba:
            caminho = CAMINHHOS[I]
            nome_arquivo = os.path.basename(caminho)

            # Status catalogado na aba
            ja_catalogado, info = arquivo_ja_catalogado(caminho)
            if ja_catalogado:
                st.info(f"⭐ Arquivo CATALOGADO: {nome_arquivo}")
            else:
                st.info(f"📂 Arquivo NOVO: {nome_arquivo}")

            # SEU EDITOR
            linguagem = "python" if caminho.endswith('.py') else "javascript" if caminho.endswith('.js') else "text"
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
            except:
                conteudo = "# Arquivo vazio"

            cod = st_ace(
                value=conteudo,
                language=linguagem,
                theme=THEMA_EDITOR,
                font_size=EDITOR_TAM_MENU,
                height=700,
                key=f"ace_editor_{I}"
            )

            _.conteudos_abas[I] = cod

    # SELECTBOX COM MESMO FORMATO
    col_apag, col_sel = ColunaSelect.columns([2, 8])
    id_aba_ativa = col_sel.selectbox(
        "Aba ativa ▶️",
        range(len(CAMINHHOS)),
        format_func=lambda i: nomes_completos[i],  # ← usa o mesmo formato!
        index=_.get("id_aba_ativa", 0),
        key="select_aba_ativa"
    )


def Editor_Simples(col1, Top4, ColunaSelect, CAMINHHOS, THEMA_EDITOR, EDITOR_TAM_MENU, colStop, ColunaRun):
    # Função para nome curto (mantida)
    def nome_curto(nome, limite=20):
        base, ext = os.path.splitext(nome)
        if ext:
            return (base[:limite - len(ext)] + ext) if len(base) > limite else nome
        return nome[:limite]

    _ = st.session_state

    # ===== ESTADO DO SISTEMA - CORRIGIDO PARA MÚLTIPLAS ABAS =====
    if "conteudos_abas" not in _:
        _.conteudos_abas = {}  # {id_aba: conteudo}
    if "Diretorio" not in _:
        _.Diretorio = {}  # {id_aba: caminho}
    _.setdefault("output", "")
    _.setdefault("output_queue", queue.Queue())
    _.setdefault("input_queue", queue.Queue())
    _.setdefault("codigo_para_executar", None)
    _.setdefault("thread_running", False)
    _.setdefault("id_aba_ativa", 0)  # ABA ATIVA pelo usuário


    # -------------------------------------------------------------------- RUN ÚNICO (FORA DAS TABS)
    _.setdefault("aba_executando_id", None)
    _.setdefault("aba_executando", None)

    def run_code_thread(code, input_q, output_q):
        def custom_input(prompt=""):
            if prompt:
                output_q.put(prompt)
            val = input_q.get()
            return val

        class CustomStdout:
            def write(self, s):
                if s:
                    output_q.put(s)

            def flush(self):
                pass

        old_stdout = sys.stdout
        sys.stdout = CustomStdout()

        try:
            exec(code, {
                'input': custom_input,
                'print': lambda *args: output_q.put(" ".join(map(str, args)) + "\n"),
                'time': time,
                'sleep': time.sleep,
                '__name__': '__main__',
                'st': st
            })
            output_q.put("PROGRAM_FINISHED")
        except Exception as e:
            output_q.put(f"\n❌ ERRO: {str(e)}\n")
            output_q.put("PROGRAM_FINISHED")
        finally:
            sys.stdout = old_stdout

    nomes_arquivos = [os.path.basename(c) for c in CAMINHHOS]
    nomes_completos = []
    for caminho in CAMINHHOS:
        nome_arquivo = os.path.basename(caminho)
        ja_catalogado, info = arquivo_ja_catalogado(caminho)
        cat = ':material/star_rate:' if ja_catalogado else ''
        em = Sinbolos(nome_arquivo)
        nome_formatado = f"{em}{nome_curto(nome_arquivo, 8)}{cat}"
        nomes_completos.append(nome_formatado)

    # RESULTADO das abas:
    # ⚡javali.js⭐    🐍main.py     🐍teste_2

    abas = st.tabs(nomes_completos)

    # *** LOOP PRINCIPAL DAS TABS - CORRIGIDO ***
    for I, aba in enumerate(abas):
        with aba:
            # Salva estado da aba ATUAL
            _.Diretorio[I] = CAMINHHOS[I]

            caminho = CAMINHHOS[I]
            nome_arquivo = os.path.basename(caminho)
            linguagem = Identificar_linguagem(CAMINHHOS[I])

            # Conteúdo inicial
            conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, CAMINHHOS[I])

            # *** st_ace RETORNA o código ATUALIZADO da aba ***
            cod = st_ace(
                value=conteudo_inicial,
                language=linguagem,
                theme=THEMA_EDITOR,
                font_size=EDITOR_TAM_MENU,
                height=850,
                auto_update=True,
                annotations=Anotations_Editor(conteudo_inicial),
                markers=Marcadores_Editor(conteudo_inicial),
                wrap=True,
                key=f"ace_editor_{I}"  # Key única por aba
            )

            # Salva no session_state por aba
            _.conteudos_abas[I] = cod
            st.info(f"✅ Aba {I}: {len(cod)} chars carregados")  # Debug opcional

    # Ao final, usa o conteúdo da aba ativa
    codigo = _.Conteudo if hasattr(_, 'Conteudo') else ""

    col_apag, col_sel = ColunaSelect.columns([2,8])
    id_aba_ativa = col_sel.selectbox(
        "Aba ativa ▶️",
        range(len(nomes_arquivos)),
        format_func=lambda i: nomes_arquivos[i],
        index=_.id_aba_ativa,
        key="select_aba_ativa" ,label_visibility='collapsed')

    _.id_aba_ativa = id_aba_ativa  # Atualiza estado

    # *** CÓDIGO ATUAL DA ABA ATIVA ***
    codigo = _.conteudos_abas.get(_.id_aba_ativa, "")
    nome_arquivo_ativo = nomes_arquivos[_.id_aba_ativa]

    # Salva no disco a aba ativa (auto-save)
    if codigo:
        try:
            with open(_.Diretorio[_.id_aba_ativa], 'w', encoding='utf-8') as f:
                f.write(codigo)
        except Exception as e:
            st.error(f"Erro salvar {nome_arquivo_ativo}: {e}")


    with col_apag:
        if st.button(f'🗑️{nome_curto(nome_arquivo_ativo, 5)}', key="botao_apagar_arquivos"):
            st.warning("Funcionalidade de apagar em desenvolvimento")
            st.rerun()

    # EXECUÇÃO - usa 'codigo' da aba ativa
    if ColunaRun.button("▶️ Run", key="executar_aba_ativa", shortcut='Ctrl+Enter'):
        st.session_state.output = f"{_.Diretorio}>\n"
        # Limpa queues...
        while not st.session_state.input_queue.empty():
            st.session_state.input_queue.get()
        while not st.session_state.output_queue.empty():
            st.session_state.output_queue.get()
        st.session_state.thread_running = True
        threading.Thread(
            target=run_code_thread,
            args=(codigo, st.session_state.input_queue, st.session_state.output_queue),
            daemon=True
        ).start()
        st.rerun()

    if colStop.button("⏹️", key=f"parar_{id_aba_ativa}", shortcut='Ctrl+Space'):  # *** BOTÃO STOP DE VOLTA! ***
        _.thread_running = False
        _.output += "\n⏹️ Execução interrompida\n"

    arquivos_abertos_nomes = nomes_arquivos
    arquivos_abertos_caminhos = CAMINHHOS

    arquivo_selecionado_nome = nome_arquivo_ativo
    arquivo_selecionado_caminho = _.Diretorio.get(_.id_aba_ativa, "")
    arquivo_selecionado_conteudo = codigo

    # -------------------------------------------------------------------- TERMINAL Preview
    with st.container(border=True, key='Preview'):
        with Top4:
            altura_prev = st.slider(':material/directions_bike:', value=300, min_value=200, max_value=800, step=300,
                                    label_visibility='collapsed')

        with st.expander(
                f' **{arquivo_selecionado_nome}** :material/directions_bike:'.replace('Executando - None', '')):
            output_placeholder = st.empty()

            # Processa mensagens da fila
            if st.session_state.thread_running:
                new_data = False
                try:
                    while True:
                        msg = st.session_state.output_queue.get_nowait()
                        if msg == "PROGRAM_FINISHED":
                            st.session_state.thread_running = False
                            st.session_state.output += "🏁 Fim do Codigo!"
                            new_data = True
                            break
                        st.session_state.output += msg
                        new_data = True
                except queue.Empty:
                    pass

                if new_data:
                    output_placeholder.text_area("Saída:", value=st.session_state.output, height=altura_prev,
                                                 disabled=True, label_visibility='collapsed')
                else:
                    st.text_area("Saída:", value=st.session_state.output, height=altura_prev, disabled=True,
                                 label_visibility='collapsed')
            else:
                st.text_area("Saída:", value=st.session_state.output, height=altura_prev, disabled=True,
                             label_visibility='collapsed')

            # Input do usuário (apenas quando executando)
            if st.session_state.thread_running:
                user_input = st.chat_input("Digite sua entrada aqui: ")
                if user_input:
                    st.session_state.input_queue.put(user_input)
                    st.session_state.output += f"> {user_input}\n"
                    st.rerun()

        # Auto-refresh enquanto rodando
        if st.session_state.thread_running:
            time.sleep(0.1)
            st.rerun()

    # -------------------------------------------------------------------- Explorer Jason
    codigo_completo_do_editor = codigo
    saida_preview = st.session_state.output.strip().replace(f'{_.Diretorio}>', '').replace('🏁 Fim do Codigo!', '')
    st.write(saida_preview)
    with st.container(border=True, key='Preview_Jason'):
        with st.expander('Explorer Jason', expanded=False, ):

            try:
                with st.container(height=500):

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
                        st.dataframe(linhas_tabela, use_container_width=True, hide_index=True)
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

        # -------------------------------------------------------------------- Api IA
    with st.container(border=True, key='Api_IA'):
        with st.expander('Ajuda IA', expanded=False, ):
            with st.container(border=False, height=400):

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
                    if c1.button("Gerar / Aplicar", type="primary", use_container_width=True):

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
                                "Authorization": "Bearer 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",
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
                                    # st.session_state.clipboard = novo_codigo  # guarda pra uso depois
                                    st.code(wrap_text(novo_codigo, 100), language=linguagem)


                            except Exception as e:
                                c2.error(f"🪲 Falha na IA: {str(e)}")
    # -------------------------------------------------------------------- Catalogar scripts
    with st.container(border=True, key='Catalogar_scripts'):
        from APP_Catalogo import catalogar_arquivo_ia
        with st.expander(f"🔍 Catalogar este arquivo: {nome_arquivo}", expanded=False):
            with st.container(border=False, height=300):
                col1, col2 = st.columns([3, 1])
                observacao_usuario = col1.text_input("💭 Sua observação:", key=f"obs_{nome_arquivo}")
                concluir = col2.button("📚 Gerar catálogo com IA", use_container_width=True)
                if concluir:
                    # aqui começa a porro das chamada desse codogo
                    catalogar_arquivo_ia(nome_arquivo, _.Diretorio, codigo_completo_do_editor, linguagem,
                                         observacao_usuario)

    return (
        arquivos_abertos_nomes,
        arquivos_abertos_caminhos,
        arquivo_selecionado_nome,
        arquivo_selecionado_caminho,
        arquivo_selecionado_conteudo  # ✅ AGORA RETORNA o código da aba ativa!
    )


'''
Fonte principal (texto normal): #D6D6D6
Fonte secundária (labels, hints): #9A9A9A

Background: #000000

Menu: #1C1C1C

Botões: #3A1C4A

Cinza muito escuro: #1A1A1A
Cinza escuro: #333333

Azul escuro antigo: #001A4D

Verde escuro antigo: #004D1A
Amarelo escuro antigo: #7A6A00

Roxo escuro antigo: #3D005C
Ciano escuro antigo: #004D4D

Marrom escuro antigo: #4A2A0A'''
