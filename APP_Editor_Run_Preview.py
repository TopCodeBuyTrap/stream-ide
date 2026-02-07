import subprocess
from pathlib import Path
import streamlit as st
import threading
import queue
import os, time, re, sys, ast

from APP_Editores_Auxiliares.APP_Catalogo import arquivo_ja_catalogado
from APP_Editores_Auxiliares.APP_Editor_Codigo import editor_codigo_autosave

from APP_Menus import Apagar_Arq
from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO
from APP_SUB_Funcitons import Identificar_linguagem, Button_Nao_Fecha, Sinbolos, \
    controlar_altura, controlar_altura_horiz
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs
from APP_Editores_Auxiliares.SUB_Run_servidores import netstat_streamlit, run_streamlit_process, is_streamlit_code, is_flask_code, \
    run_flex_process, extract_flask_config, find_port_by_pid, stop_flex, stop_process_by_port, is_django_code, \
    extract_django_config
from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida

# 🔥 USA A FUNÇÃO MESTRE - ZERO Path()
_Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()



def scrl(val):
    if val == False:
        sc= """<style>
section[data-testid="stMain"] { /* REMOVER SCROLL */
    overflow: hidden !important
</style>"""
        st.markdown(sc,unsafe_allow_html=True)
def status_bar_pro(
    state,
    linguagem,
    cod,
    linha_atual=1,
    coluna_atual=1,
    arquivo_path=None,
    readonly=False,
):
    if not isinstance(cod, str):
        cod = ""

    total_linhas = cod.count("\n") + 1 if cod else 0
    total_chars = len(cod)
    tamanho_bytes = len(cod.encode("utf-8"))

    modificado = False
    if hasattr(state, "Conteudo") and hasattr(state, "id_aba_ativa"):
        anterior = state.Conteudo.get(state.id_aba_ativa)
        if anterior is not None:
            modificado = anterior != cod

    encoding = "UTF-8"
    modo = "READONLY" if readonly else "EDIT"

    nome_arquivo = ""
    if arquivo_path:
        nome_arquivo = os.path.basename(arquivo_path)

    col1, col2, col3, col4, col5, col6 = st.columns(
        [1.2, 1.6, 2.2, 1.6, 2.4, 2.8]
    )

    with col1:
        st.caption(f"{total_linhas} linhas")

    with col2:
        st.caption(f"{total_chars} chars")

    with col3:
        st.caption(f"{tamanho_bytes} bytes")

    with col4:
        if hasattr(state, "autosave_status"):
            st.caption(state.autosave_status)
        else:
            st.caption("")

    with col5:
        status_mod = "MOD" if modificado else "OK"
        st.caption(f"{modo} | {status_mod} | {encoding}")

    with col6:
        st.caption(
            f"{nome_arquivo}  Ln {linha_atual}, Col {coluna_atual} | {linguagem}"
        )


# 🔥 DETECTOR MÓDULOS SIMPLES (sem dicionário inútil)
def checar_modulos_no_venv_(codigo, _Python_exe):
    """Checa se módulo tá NO VENV ANTES de instalar"""
    faltando = []
    try:
        tree = ast.parse(codigo)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    # CHECA NO VENV COM PIP LIST!
                    resultado = os.popen(f'"{_Python_exe}" -m pip list').read()
                    if mod.lower() not in resultado.lower():
                        faltando.append(mod)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split('.')[0]
                resultado = os.popen(f'"{_Python_exe}" -m pip list').read()
                if mod.lower() not in resultado.lower():
                    faltando.append(mod)
        return list(set(faltando))
    except:
        return []


# 🔥 DETECTOR MÓDULOS FALTANDO (PIP + SCRIPTS)
def checar_modulos_no_venv(codigo, nome_arquivo, caminho, _Python_exe):
    """Retorna: {'pip': [...], 'local': [...]}"""
    modulos_pip = []
    modulos_local = []

    try:
        tree = ast.parse(codigo)

        todos_modulos = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    todos_modulos.add(mod)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split('.')[0]
                todos_modulos.add(mod)

        # PIP
        pip_resultado = os.popen(f'"{_Python_exe}" -m pip list').read().lower()
        arquivos_locais = [f[:-3].lower() for f in os.listdir('.') if f.endswith('.py')]

        for mod in todos_modulos:
            mod_lower = mod.lower()
            if mod_lower not in arquivos_locais and mod_lower not in pip_resultado:
                # É pip ou local? (tenta importar)
                try:
                    __import__(mod)
                except ImportError:
                    modulos_pip.append(mod)
                else:
                    modulos_local.append(mod)

    except:
        pass

    return {'pip': modulos_pip, 'local': modulos_local}


# USO:




def Editor_Simples(Janela,Select, CAMINHHOS, THEMA_EDITOR, EDITOR_TAM_MENU,FONTE, colStop, ColunaRun,CorBACK):
    msg_fim_cod = "🏁 Fim do Codigo!"
    Most_Logs = False


    # Função para nome curto (mantida)
    def nome_curto(nome, limite=20):
        base, ext = os.path.splitext(nome)
        if ext:
            return (base[:limite - len(ext)] + ext) if len(base) > limite else nome
        return nome[:limite]

    _ = st.session_state
    # ===== ESTADO DO SISTEMA - CORRIGIDO PARA MÚLTIPLAS ABAS =====

    _.setdefault("output", "")
    _.setdefault("output_queue", queue.Queue())
    _.setdefault("input_queue", queue.Queue())
    _.setdefault("codigo_para_executar", None)
    _.setdefault("thread_running", False)
    _.setdefault("id_aba_ativa", 0)
    _.setdefault("Diretorio", {})
    _.setdefault("Conteudo", {})

    Nome_Aba = ''

    with st.container(border=True,key='MenuServidor'):
        MS1,MS2,MS3 = st.columns([8,1.5,1.2])
        with MS2:
            altura = controlar_altura_horiz(st, "Preview", altura_inicial=700, passo=50, maximo=900, minimo=200)

        with MS3:
            scrl(st.toggle('|'))

        menuserv = MS1.expander('Menu Servidor')

    def run_code_thread(codigo, input_q, output_q, caminho_sectbox):

        # 🔥 LOGS DE DEBUG

        output_q.put("🔍 [DEBUG] Thread iniciada\n") if Most_Logs == True else ''

        script_path = Path(caminho_sectbox).resolve()
        project_dir = script_path.parent

        output_q.put(f"🔍 [DEBUG] Script: {script_path}\n") if Most_Logs == True else ''
        output_q.put(f"🔍 [DEBUG] Pasta: {project_dir}\n") if Most_Logs == True else ''
        output_q.put(f"🔍 [DEBUG] sys.path ANTES: {sys.path[0]}\n") if Most_Logs == True else ''

        # sys.path (SEM chdir)
        if str(project_dir) not in sys.path:
            sys.path.insert(0, str(project_dir))
            output_q.put(f"✅ [DEBUG] Pasta adicionada: {project_dir}\n") if Most_Logs == True else ''
        output_q.put(f"🔍 [DEBUG] sys.path DEPOIS: {sys.path[0]}\n") if Most_Logs == True else ''

        # VENV
        try:
            if Path(_Venv_path).exists():
                site_packages = Path(_Venv_path) / "Lib" / "site-packages"
                if site_packages.exists():
                    sys.path.insert(0, str(site_packages))
                    output_q.put(f"✅ [DEBUG] VENV adicionado: {site_packages}\n") if Most_Logs == True else ''
        except:
            output_q.put("⚠️ [DEBUG] VENV não encontrado\n") if Most_Logs == True else ''

        output_q.put("🚀 [DEBUG] Iniciando exec...\n") if Most_Logs == True else ''
        output_q.put(f"📝 [DEBUG] Código: {codigo[:100]}...\n") if Most_Logs == True else ''

        def custom_input(prompt=""):
            if prompt:
                output_q.put(prompt)
            return input_q.get()

        class CustomStdout:
            def write(self, s):
                if s and s.strip():
                    output_q.put(s)

            def flush(self):
                pass

        old_stdout = sys.stdout
        sys.stdout = CustomStdout()

        try:
            exec(codigo, {
                '__name__': '__main__',
                '__file__': str(script_path),
                'input': custom_input,
                'print': lambda *args: output_q.put(" ".join(map(str, args)) + "\n"),
                'time': time,
                'sleep': time.sleep,
                'st': st
            })
            output_q.put("✅ PROGRAM_FINISHED\n")
        except Exception as e:
            output_q.put(f"\n❌ ERRO: {str(e)}\n")
            output_q.put(f"❌ TRACEBACK: {str(e.__traceback__)}\n")
            output_q.put("❌ PROGRAM_FINISHED\n")
        finally:
            sys.stdout = old_stdout
            output_q.put("🔍 [DEBUG] Thread finalizada\n") if Most_Logs == True else ''

    nomes_arquivos = [os.path.basename(c) for c in CAMINHHOS]
    nomes_completos = []
    for caminho in CAMINHHOS:
        nom_arqu = os.path.basename(caminho)
        ja_catalogado, info = arquivo_ja_catalogado(caminho)
        cat = ':material/star_rate:' if ja_catalogado else ''
        em = Sinbolos(nom_arqu)
        nome_formatado = f"{em}{nome_curto(nom_arqu, 8)}{cat}"
        nomes_completos.append(nome_formatado)

    abas = st.tabs(nomes_completos)

    # *** CORREÇÃO: INICIALIZA 'cod' COMO None ANTES DO LOOP ***
    cod = None
    midia_exts = {
        '.mp3', '.wav', '.ogg', '.flac',  # áudio
        '.mp4', '.avi', '.mkv', '.webm',  # vídeo
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff',  # imagens
        '.pdf',  # pdf
        '.zip', '.rar', '.7z', '.exe', '.dll'  # binários genéricos
    }

    # *** LOOP PRINCIPAL DAS TABS - CORRIGIDO ***
    for I, aba in enumerate(abas):
        with aba:
            # Salva estado da aba ATUAL
            _.Diretorio[I] = CAMINHHOS[I]

            caminho = CAMINHHOS[I]
            nome_arquivo = os.path.basename(caminho)
            Nome_Aba = nomes_arquivos
            linguagem = Identificar_linguagem(CAMINHHOS[I])

            # Conteúdo inicial
            conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, CAMINHHOS[I])

            # ===== NOVA VERIFICAÇÃO DE TIPO DE ARQUIVO =====
            extensao = os.path.splitext(nome_arquivo)[1].lower()
            try:
                # *** st_ace RETORNA o código ATUALIZADO da aba ***
                cod = editor_codigo_autosave(st=st,aba_id=I,
                    caminho_arquivo=_.Diretorio[I],
                    conteudo_inicial=conteudo_inicial,
                    linguagem=linguagem,
                    thema_editor=THEMA_EDITOR,font_size=EDITOR_TAM_MENU,
                    fonte=FONTE, altura=altura, backgroud = CorBACK,
                )

                with Janela:
                    if is_streamlit_code(cod):
                        st.code(f'streamlit run {nome_arquivo}')
                    if is_flask_code(cod):
                        st.code(f'python {nome_arquivo} # flask')
                bot1,bot2,bot3 = st.columns([2,3,5])

                if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                    Apagar_Arq(st, nome_arquivo, caminho)

                # Salva no session_state por aba
                # 🔥 FIX LINHAS VAZIAS
                cod = cod.rstrip('\n')
                while cod.endswith('\n\n'):
                    cod = cod[:-2]

                _.Conteudo[I] = cod

                # 🔥 DETECTOR MÓDULOS FALTANDO (PREVIEW)
                modulos_faltando = checar_modulos_no_venv(cod, nome_arquivo, caminho, _Python_exe)

                with bot2:
                    if modulos_faltando['pip'] or modulos_faltando['local']:
                        col1, col2, col3 = st.columns([1, 1, 1])

                        if modulos_faltando['pip']:
                            col1.write(f"📦 PIP: {', '.join(modulos_faltando['pip'])}")
                            if col2.button(f"🔧 INSTALAR PIP", type="primary"):
                                for mod in modulos_faltando['pip']:
                                    with st.spinner(f"📦 {mod}..."):
                                        os.system(f'"{_Python_exe}" -m pip install {mod}')
                                st.success("✅ PIP Instalado!")
                                st.rerun()

                        if modulos_faltando['local']:
                            col1.write(f"📁 LOCAL: {', '.join(modulos_faltando['local'])}")
                            if col3.button(f"➕ COLOCAR IMPORTS", type="secondary",key=I):
                                # 🔥 ESCREVE NO TOPO DO ARQUIVO
                                imports_locais = "\n".join(
                                    [f"from {mod} import *" for mod in modulos_faltando['local']])
                                novo_codigo = f"{imports_locais}\n\n{cod}"

                                # SALVA ARQUIVO
                                with open(caminho, 'w', encoding='utf-8') as f:
                                    f.write(novo_codigo)

                                st.success(f"✅ Imports adicionados em {nome_arquivo}!")
                                st.rerun()
                    else:
                        st.write("✅ Tudo instalado - pode rodar!")

                # CHAMA STATUS BAR (só na aba ativa)
                if len(nomes_arquivos) > 0:
                    with bot3:
                        status_bar_pro(_, linguagem, cod)
            except AttributeError:
                with st.container(border=True,height=altura):
                    if extensao in midia_exts or not conteudo_inicial or '�' in conteudo_inicial[:100]:
                        tp1, tp2 = st.columns([1, 1])
                        bot1, bot2, bot3 = st.columns(3)
                        # VISUALIZAÇÃO POR TIPO
                        if extensao in {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}:
                            tp1.image(caminho,width=600)
                            if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                                Apagar_Arq(st, nome_arquivo, caminho)
                        elif extensao == '.pdf':
                            with open(caminho, 'rb') as f:
                                tp1.download_button("📥 Download PDF", f.read(), nome_arquivo)
                            if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                                Apagar_Arq(st, nome_arquivo, caminho)
                        elif extensao in {'.mp3', '.wav', '.ogg'}:
                            tp1.audio(caminho)
                            if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                                Apagar_Arq(st, nome_arquivo, caminho)
                        elif extensao in {'.mp4', '.avi', '.mkv'}:
                            tp1.video(caminho,width=300)
                            if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                                Apagar_Arq(st, nome_arquivo, caminho)
                        else:  # Binários genéricos
                            with open(caminho, 'rb') as f:
                                tp2.download_button("📥 Download", f.read(), nome_arquivo,
                                                   mime="application/octet-stream")
                                if bot1.button(f'🗑️Apagar: {nome_arquivo}', key=f"botao_apagar_arquivos{I}"):
                                    Apagar_Arq(st, nome_arquivo, caminho)

                    # *** CORREÇÃO: Define 'cod' como string vazia para arquivos de mídia ***
                    cod = ""

    # ✅ VALIDAÇÃO SEGURA ANTES DO SELECTBOX
    if len(nomes_arquivos) == 0:
        st.warning("Nenhum arquivo aberto!")
        return ([], [], "", "", "")

    # ✅ CORREÇÃO: Garante index válido
    total_abas = len(nomes_arquivos)
    index_seguro = 0
    if hasattr(_.get('id_aba_ativa'), '__index__'):
        index_seguro = min(max(_.id_aba_ativa, 0), total_abas - 1)

    id_aba_ativa = Select.selectbox("Aselec",range(total_abas), format_func=lambda i: nomes_arquivos[i], index=index_seguro,  key="select_aba_ativa",
        label_visibility='collapsed' )

    # *** CÓDIGO ATUAL DA ABA ATIVA (SEGURO) ***
    nome_arquivo_sectbox = nomes_arquivos[id_aba_ativa]
    caminho_sectbox = _.Diretorio.get(id_aba_ativa, "")
    codigo_sectbox = _.Conteudo.get(id_aba_ativa, "")

    #st.write('nome_arquivo_sectbox>',nome_arquivo_sectbox)
    #st.write('caminho_sectbox>',caminho_sectbox)
    #st.write('codigo>',codigo_sectbox)


    # INICIALIZA output
    if 'streamlit_output' not in _:
        _['streamlit_output'] = []

    _.setdefault("flask_port", [])

    if 'django_port' not in _:
        _['django_port'] = []

    # EXECUÇÃO - usa 'codigo' da aba ativa
    if ColunaRun.button("▶️", key="executar_aba_ativa", shortcut='Ctrl+Enter',width="stretch"):
        _.output = f"{caminho_sectbox}>\n"
        # Limpa queues...
        # ✅ DETECTA SE É STREAMLIT E USA SUBPROCESS
        if is_streamlit_code(codigo_sectbox):
            _.process_running = True
            _.current_process = run_streamlit_process(caminho_sectbox)

            # *** WHILE TRUE CONTÍNUO (atualiza sempre!) ***
            process = _.current_process

            while True:
                try:
                    # LÊ UMA LINHA (igual PyCharm)
                    line = process.stdout.readline()
                    if line:
                        _['streamlit_output'].append(line)
                        time.sleep(0.01)  # ← SEMPRE NO FINAL
                        st.rerun()  # ← ATUALIZA NA HORA!
                    else:
                        # Processo acabou ou sem output
                        break
                except:
                    break
            Exct = f'''
{''.join(_['streamlit_output'])}\n{msg_fim_cod}'''
            _.output = Exct
        elif is_flask_code(codigo_sectbox):
            _.process_running = True

            # 1. Primeiro tenta extrair config do código do usuário
            config = extract_flask_config(codigo_sectbox)
            porta_detectada = config['port']
            host = config['host']
            debug = config['debug']

            print(
                f"🔍 Config detectada: Porta={'Específica: ' + str(porta_detectada) if porta_detectada else 'Automática'} | Host={host} | Debug={debug}")

            _.current_process = run_flex_process(caminho_sectbox)
            process = _.current_process

            # Armazena PID para busca posterior de porta
            pid = process.pid
            _.flask_pid = pid

            # 2. Lê output em tempo real (melhorado)
            _['flask_output'] = []
            _['flask_port'] = []

            while _.process_running:
                try:
                    line = process.stdout.readline()
                    if line:
                        _['flask_output'].append(line)
                        # Procura por linha com porta no output
                        if not porta_detectada and 'Running on http' in line:
                            port_match = re.search(r'http[^:]*:([0-9]+)', line)
                            if port_match:
                                porta_detectada = int(port_match.group(1))
                                print(f"📡 Porta encontrada no output: {porta_detectada}")
                        time.sleep(0.01)
                        st.rerun()
                    elif process.poll() is not None:  # Processo terminou
                        break
                except:
                    break

            # 3. Se ainda não achou porta, usa netstat
            if not porta_detectada:
                print("🔎 Procurando porta via netstat...")
                porta_detectada = find_port_by_pid(pid)
                if porta_detectada:
                    print(f"✅ Porta encontrada via netstat: {porta_detectada}")
                else:
                    porta_detectada = "5000"  # Default Flask

            # 4. Monta resultado final com info da porta
            msg_porta = f'🔌 Servidor Flask rodando em: http://localhost:{porta_detectada}'
            Exct = f'''
{''.join(_['flask_output'])}
{msg_porta}
{msg_fim_cod}
            '''
            _['flask_port'].append(porta_detectada)
            _.output = Exct
            # Django
        elif is_django_code(codigo_sectbox):
            _.process_running = True
            config = extract_django_config(codigo_sectbox)
            porta_detectada = config['port']
            host = config['host']

            # Inicia Django via subprocess
            _.current_process = subprocess.Popen(
                f'python manage.py runserver {host}:{porta_detectada}',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            process = _.current_process
            _.django_pid = process.pid

            # Inicializa lista de output e portas
            _['django_output'] = []
            _['django_port'].append(porta_detectada)

            while _.process_running:
                try:
                    line = process.stdout.readline()
                    if line:
                        _['django_output'].append(line)
                        time.sleep(0.01)
                        st.rerun()
                    elif process.poll() is not None:
                        break
                except:
                    break

            msg_porta = f'🔌 Servidor Django rodando em: http://{host}:{porta_detectada}'
            _.output = f"{''.join(_['django_output'])}\n{msg_porta}\n{msg_fim_cod}"
        else:
            # Limpa tudo
            _.output = f"{caminho_sectbox}>\n"
            while not _.input_queue.empty():
                _.input_queue.get()
            while not _.output_queue.empty():
                _.output_queue.get()
            # 🔥 TESTE IMEDIATO (USA _.output_queue)
            _.output_queue.put("🔥 [TESTE] QUEUE VIVA!\n") if Most_Logs == True else ''
            _.thread_running = True
            # Thread
            thread = threading.Thread(
                target=run_code_thread,
                args=(codigo_sectbox, _.input_queue, _.output_queue, caminho_sectbox),
                daemon=True
            )
            thread.start()
            # 🔥 LEITOR SIMPLES COM TIMEOUT
            start_time = time.time()
            st.toast("🔍 Executando...")
            while _.thread_running and (time.time() - start_time) < 5:
                try:
                    if not _.output_queue.empty():
                        line = _.output_queue.get_nowait()
                        _.output += line
                        st.write(f"📨 DEBUG: {repr(line)}")  if Most_Logs == True else ''
                        if "PROGRAM_FINISHED" in line:
                            _.thread_running = False
                            _.output += "\n🏁 Fim do Código!\n"
                            break
                    time.sleep(0.05)
                    st.rerun()
                except:
                    time.sleep(0.05)
                    continue

            _.thread_running = False
            st.success("✅ Execução finalizada!")

    if colStop.button("⏹️", key=f"parar_{id_aba_ativa}", shortcut='Ctrl+Space',width='stretch'):  # *** BOTÃO STOP DE VOLTA! ***
        _.thread_running = False
        _.output += "\n⏹️ Execução interrompida\n"

    with menuserv:
        portas = netstat_streamlit()
        for porta, pid, linha in portas:
            st.write(f"[**http://streamlit:{porta}**](http://localhost:{porta})")

            if st.button(f"🛑 Parar {porta}", key=f"kill_{porta}"):
                os.system(f'taskkill /PID {pid} /F')
                st.rerun()

        for porta in _.flask_port.copy():
            st.markdown(f"[http://flask:{porta}](http://localhost:{porta})")
            if st.button(f"🛑 Parar {porta}", key=f"kill_{porta}"):
                try:
                    pids = stop_flex(porta)
                    if pids:
                        for pid in pids:
                            os.system(f'taskkill /PID {pid} /F')
                    # limpa toda a lista de portas
                    _['flask_port'].clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao tentar parar a porta {porta}: {e}")
        # Django
        for porta in _.django_port.copy():
            st.markdown(f"[http://django:{porta}](http://localhost:{porta})")
            if st.button(f"🛑 Parar {porta}", key=f"kill_django_{porta}"):
                try:
                    pids = stop_process_by_port(porta)
                    for pid in pids:
                        os.system(f'taskkill /PID {pid} /F')
                    _['django_port'].clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao tentar parar a porta {porta}: {e}")
    # -------------------------------------------------------------------- TERMINAL Preview
    with st.container(border=True, key='Preview'):
        if Button_Nao_Fecha(f':material/directions_bike: **{nome_arquivo_sectbox}**', f':material/directions_bike: '
                                                                                          f'**{nome_arquivo_sectbox}**','BtnPreview'):
            from APP_Editores_Auxiliares.APP_Preview import Previews

            Previews(st, _, linguagem, msg_fim_cod)
        # Auto-refresh enquanto rodando
        if _.thread_running:
            time.sleep(0.1)
            st.rerun()

    # -------------------------------------------------------------------- Explorer Jason
    saida_preview = _.output.strip().replace(f'{caminho_sectbox}>', '').replace(msg_fim_cod, '')

    with st.container(border=True, key='Preview_Jason'):
        if Button_Nao_Fecha(f':material/data_object: Explorer Jason', f':material/data_object: Explorer Jason',
                            'BtnJson'):
            from APP_Editores_Auxiliares.APP_Json import Jsnon
            Jsnon(st, saida_preview)

    # -------------------------------------------------------------------- Api IA
    with st.container(border=True, key='Api_IA'):
        if Button_Nao_Fecha(f':material/psychology: Chat IA', f':material/psychology: Chat IA','BtnChat'):
            from APP_Editores_Auxiliares.APP_Api_IAs import IA_openrouter
            IA_openrouter(st, codigo_sectbox, saida_preview, linguagem)

    # -------------------------------------------------------------------- Catalogar scripts
    with st.container(border=True, key='Catalogar_scripts'):
        from APP_Editores_Auxiliares.APP_Catalogo import catalogar_arquivo_ia

        if Button_Nao_Fecha(f':material/inventory: Catalogar: {nome_arquivo_sectbox}', f':material/inventory_2: Catalogar: {nome_arquivo_sectbox}', 'BtnCatalogar'):
           # aqui começa a porro das chamada desse codogo
            try:
                catalogar_arquivo_ia(nome_arquivo_sectbox, caminho_sectbox, codigo_sectbox, linguagem)
            except TypeError as e:
                st.write(traduzir_saida(e))
            st.write('')
            st.write('')

    # 🔥 AUTOSAVE MILITAR - LIMPEZA AUTOMÁTICA
    def limpar_autosave_velho():
        """Limpa autosave sem quebrar session_state"""
        session_state = st.session_state  # ✅ REFERÊNCIA SEGURA!

        agora = time.time()
        chaves_para_limpar = []

        # ✅ sÓ executa se session_state é dict
        if isinstance(session_state, dict):
            for key in list(session_state.keys()):
                if key.startswith(('autosave_cache_', 'autosave_saved_')):
                    if agora - session_state.get(key + '_timestamp', 0) > 3600:
                        chaves_para_limpar.append(key)

            for key in chaves_para_limpar:
                if key in session_state:
                    del session_state[key]
                timestamp_key = key + '_timestamp'
                if timestamp_key in session_state:
                    del session_state[timestamp_key]

    limpar_autosave_velho()  # Executa sempre

