import streamlit as st
from streamlit_ace import st_ace
import sys
import threading
import queue
import os, time

from APP_SUB_Funcitons import Identificar_linguagem, Button_Nao_Fecha, Sinbolos
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs


def Editor_Simples(col1,Top4,ColunaSelect, Caminho, THEMA_EDITOR, EDITOR_TAM_MENU,colStop,ColunaRun):
    # Henriq colocar os comentarios no editor
    _ = st.session_state
    qt_col = 8
    # ===== ESTADO DO SISTEMA =====
    st.session_state.setdefault("output", "")
    st.session_state.setdefault("output_queue", queue.Queue())
    st.session_state.setdefault("input_queue", queue.Queue())
    st.session_state.setdefault("codigo_para_executar", None)
    st.session_state.setdefault("thread_running", False)
    _.setdefault("arquivo_ativo_idx", 0)

    # -------------------------------------------------------------------- LEITURA DAS ABAS
    def chec_se_arq_do_projeto(caminho_lista):
        """Verifica se arquivos existem e retorna nomes válidos"""
        nomes_validos = []
        for caminho in caminho_lista:
            if os.path.isfile(caminho):
                nomes_validos.append(os.path.basename(caminho))
            else:
                # Cria arquivo vazio se não existir
                with open(caminho, 'w') as f:
                    f.write('# Novo arquivo criado\n')
                nomes_validos.append(os.path.basename(caminho))
        return nomes_validos
    nomes_abas = chec_se_arq_do_projeto(Caminho)

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
                'st': st  # Permite usar Streamlit no código executado
            })
            output_q.put("PROGRAM_FINISHED")
        except Exception as e:
            output_q.put(f"\n❌ ERRO: {str(e)}\n")
            output_q.put("PROGRAM_FINISHED")
        finally:
            sys.stdout = old_stdout


    with st.form('ola',border=False):
        for im in range(0, len(Caminho), qt_col):
            cols = st.columns(qt_col)
            for j, caminho in enumerate(Caminho[im:im + qt_col]):
                idx_arquivo = im + j
                nome = os.path.basename(caminho)
                ativo = idx_arquivo == _.arquivo_ativo_idx

                with cols[j]:
                    def nome_curto(nome, limite):
                        base, ext = os.path.splitext(nome)
                        if ext:
                            return base[:limite] + ext
                        return nome[:limite]

                    em = Sinbolos(nome)

                    if ativo:
                        if st.form_submit_button(f"{em}{nome_curto(nome,8)}",key=f"btn_{idx_arquivo}",use_container_width=True,type='primary',help=nome):
                            _.arquivo_ativo_idx = idx_arquivo
                            st.rerun()
                    else:
                        if st.form_submit_button(f"{em}{nome_curto(nome,8)}",key=f"btn_{idx_arquivo}",use_container_width=True,type='tertiary',help=nome):
                            _.arquivo_ativo_idx = idx_arquivo
                            st.rerun()

    c1, c2 = ColunaSelect.columns([3, 7])
    with c1:
        if st.button(f'🗑️{nome_curto(nome,5)}', key="botao_apagar_arquivos"):
            st.warning("Funcionalidade de apagar em desenvolvimento")
            st.rerun()

    with c2:
        aba_escolhida = st.selectbox(
            "Arquivo",
            nomes_abas,
            key="select_run_unico",
            label_visibility="collapsed",
        )

    idx = _.arquivo_ativo_idx
    caminho = Caminho[idx]
    nome = os.path.basename(caminho)
    linguagem = Identificar_linguagem(caminho)
    content_key = f"conteudo_{idx}"

    if content_key not in _:
        _[content_key] = Abrir_Arquivo_Select_Tabs(st, caminho)

    _[content_key] = st_ace(
        value=_[content_key],
        language=linguagem,
        theme=THEMA_EDITOR,
        font_size=EDITOR_TAM_MENU,
        height=850,
        auto_update=True,
        wrap=True,
        key=f"ace_editor_{idx}"
    )

    codigo = _[content_key]

    with ColunaRun:
        if st.button(F"▶️", key=f"executar_{idx}",shortcut='Ctrl+Enter'):
            # Limpa output anterior
            st.session_state.output = f"🔄 Executando {ativo}...\n\n"

            # Limpa filas
            while not st.session_state.input_queue.empty():
                st.session_state.input_queue.get()
            while not st.session_state.output_queue.empty():
                st.session_state.output_queue.get()

            # Inicia thread de execução
            st.session_state.thread_running = True
            threading.Thread(
                target=run_code_thread,
                args=(codigo, st.session_state.input_queue, st.session_state.output_queue),
                daemon=True
            ).start()
            st.rerun()

    if colStop.button(F"⏹️", key=f"parar_{idx}",shortcut='Ctrl+Space'):
        st.session_state.thread_running = False
        st.session_state.output += "\n⏹️ Execução interrompida\n"


    # -------------------------------------------------------------------- RETORNOS
    arquivos_abertos_nomes = [os.path.basename(path) for path in Caminho]
    arquivos_abertos_caminhos = Caminho

    idx_select = nomes_abas.index(aba_escolhida) if nomes_abas and aba_escolhida in nomes_abas else 0
    arquivo_selecionado_nome = nomes_abas[idx_select] if idx_select < len(nomes_abas) else ""
    arquivo_selecionado_caminho = Caminho[idx_select] if idx_select < len(Caminho) else ""

    arquivo_selecionado_conteudo = ""
    if arquivo_selecionado_caminho and os.path.isfile(arquivo_selecionado_caminho):
        arquivo_selecionado_conteudo = Abrir_Arquivo_Select_Tabs(st, arquivo_selecionado_caminho)


    # -------------------------------------------------------------------- TERMINAL (col2)
    with st.container(border=True, key='Preview'):
        with Top4:
            altura_prev = st.slider(':material/directions_bike:', value=300, min_value=200, max_value=800, step=300,label_visibility='collapsed')
        expander_key = f"exec_{arquivo_selecionado_nome}"

        if expander_key not in st.session_state:  # manter o expender sempre no estado que o usuario deixar aberto / fechado
            st.session_state[expander_key] = False
        # :material/code:
        with st.expander(f' **{arquivo_selecionado_nome}** :material/directions_bike:'.replace('Executando - None', ''),
                         expanded=st.session_state[expander_key]
                         ):
            # SALVA o estado quando o usuário interage
            st.session_state[expander_key] = True

            # Placeholder para output
            output_placeholder = st.empty()

            # Processa mensagens da fila
            if st.session_state.thread_running:
                new_data = False
                try:
                    while True:
                        msg = st.session_state.output_queue.get_nowait()
                        if msg == "PROGRAM_FINISHED":
                            st.session_state.thread_running = False
                            st.session_state.output += "\n🏁 FINALIZADO!"
                            new_data = True
                            break
                        st.session_state.output += msg
                        new_data = True
                except queue.Empty:
                    pass

                if new_data:
                    output_placeholder.text_area("Saída:", value=st.session_state.output, height=altura_prev, disabled=True,label_visibility='collapsed')
                else:
                    st.text_area("Saída:", value=st.session_state.output, height=altura_prev, disabled=True,label_visibility='collapsed')
            else:
                st.text_area("Saída:", value=st.session_state.output, height=altura_prev, disabled=True,label_visibility='collapsed')

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

    return (
        arquivos_abertos_nomes,
        arquivos_abertos_caminhos,
        arquivo_selecionado_nome,
        arquivo_selecionado_caminho,
        arquivo_selecionado_conteudo
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
