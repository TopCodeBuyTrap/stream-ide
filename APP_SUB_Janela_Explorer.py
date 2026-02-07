import hashlib
from pathlib import Path
import os
import requests
from PIL import Image
from io import BytesIO

# ===============================
# UTIL
# ===============================
def safe_id(texto: str) -> str:
    return hashlib.md5(texto.encode()).hexdigest()




def listar_apenas_pastas(caminho):
    caminho = os.path.abspath(caminho)

    if not os.path.isdir(caminho):
        return []

    pastas = []
    for item in os.listdir(caminho):
        caminho_completo = os.path.join(caminho, item)
        if os.path.isdir(caminho_completo):
            pastas.append((item, caminho_completo))

    return pastas


def baixar_imagem_e_criar_pasta(raiz,url_imagem, titulo_pasta, texto_conteudo1,nome1,texto_conteudo2=''):
    # Detecta pasta de Downloads do usuário

    pasta_destino = raiz / titulo_pasta
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # Baixa a imagem
    response = requests.get(url_imagem)
    if response.status_code != 200:
        print("Não foi possível baixar a imagem.")
        return

    img = Image.open(BytesIO(response.content))
    caminho_imagem = pasta_destino / "imagem_capa_principal.png"
    img.save(caminho_imagem)
    print(f"Imagem salva em: {caminho_imagem}")

    # Cria arquivo de texto
    caminho_txt = pasta_destino / f"{nome1}.txt"
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto_conteudo1)
    if texto_conteudo2:
        caminho_txt = pasta_destino / "Para Site.txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto_conteudo2)
        print(f"Arquivo de texto salvo em: {caminho_txt}")

        print(f"Tudo pronto! Pasta criada em: {pasta_destino}")


# ===============================
# LISTAGENS
# ===============================

def listar_arquivos_e_pastas(caminho):
    """
    Lista apenas os arquivos e pastas do diretório fornecido
    (sem entrar em subdiretórios).
    Retorna uma lista no formato:
    (nome_do_item, caminho_completo)
    """

    caminho = os.path.abspath(caminho)

    if not os.path.isdir(caminho):
        return []

    itens = []
    for item in os.listdir(caminho):
        caminho_completo = os.path.join(caminho, item)
        itens.append((item, caminho_completo))

    return itens


def Abrir_Arquivo_Select_Tabs_(st, caminho_arquivo):
    # **PRIMEIRO** trata lista (resolve TypeError)
    from pathlib import Path
    import os


    if isinstance(caminho_arquivo, (list, tuple)):
        if not caminho_arquivo:
            st.warning("Lista de caminhos vazia")
            return "ERRO", ""
        caminho_arquivo = caminho_arquivo[0]  # Pega primeiro item

    # AGORA é string válida - faz verificações originais
    if not os.path.exists(caminho_arquivo):
        st.warning(f"Arquivo não encontrado: {caminho_arquivo}")
        return "ERRO", ""

    if not os.path.isfile(caminho_arquivo):
        st.warning(f"'{caminho_arquivo}' é uma pasta, não arquivo")
        return "ERRO", ""

    # IDENTIFICA TIPO por extensão
    path = Path(caminho_arquivo)
    ext = path.suffix.lower()

    # IMAGENS
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        try:
            return "IMAGEM", path.read_bytes()
        except:
            return "ERRO", ""

    # VÍDEOS
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']:
        return "VIDEO", str(path)

    # ÁUDIO
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return "AUDIO", str(path)

    # TEXTO/CÓDIGO (EXATAMENTE COMO ORIGINAL)
    else:
        try:
            os.chmod(caminho_arquivo, 0o666)
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return "TEXTO", f.read()
        except PermissionError:
            st.warning("Sem permissão. Feche outros apps ou rode como admin.")
            return "ERRO", ""
        except Exception as e:
            st.warning(f"Erro: {e}")
            return "ERRO", ""

def Abrir_Arquivo_Select_Tabs(st,caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        st.warning(f"Arquivo não encontrado: {caminho_arquivo}")
    if not os.path.isfile(caminho_arquivo):
        st.warning( f"'{caminho_arquivo}' é uma pasta, não arquivo")

    try:
        # Tenta ajustar permissão (Windows/Linux)
        os.chmod(caminho_arquivo, 0o666)
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        st.warning("Sem permissão. Feche outros apps ou rode como admin.")
    except Exception as e:pass
       # st.warning(f"Erro: {e}")


def Apagar_Arquivos(st, arquivo):
    arquivo = Path(arquivo)

    st.warning(f"Game-Over pra you FDP !    {arquivo.exists()}")

    if not arquivo.exists():
        st.error("Arquivo não encontrado")
        return

    if arquivo.is_dir():
        st.error("É uma PASTA! Use shutil.rmtree()")
        return

    try:
        arquivo.unlink()
        st.error(f"✅ Arquivo apagado: {arquivo.name}")
    except PermissionError:
        st.error("❌ Sem permissão - feche o arquivo/editor")
    except Exception as e:
        st.error(f"❌ Erro: {e}")


def Open_Explorer(caminho_arquivo):
    import streamlit as st

    try:
        pasta = Path(caminho_arquivo).parent
        os.startfile(pasta)
    except Exception as e:
        st.error(f"Não foi possível abrir a pasta: {e}")

def Janela_PESQUIZA(st,DIRETORIO):
    # Inicializa session_state
    if 'editor_ativo' not in st.session_state:
        st.session_state.editor_ativo = None
    if 'expanders_abertos' not in st.session_state:
        st.session_state.expanders_abertos = []
    if 'ultimo_caminho' not in st.session_state:
        st.session_state.ultimo_caminho = None
    if 'arquivos_por_pasta' not in st.session_state:
        st.session_state.arquivos_por_pasta = []
    if 'diretorio_atual' not in st.session_state:
        st.session_state.diretorio_atual = DIRETORIO
    if 'aviso_procurar' not in st.session_state:
        st.session_state.aviso_procurar = ""

    def voltar_pasta():
        atual = Path(st.session_state.diretorio_atual)
        if atual.parent != atual:
            st.session_state.diretorio_atual = str(atual.parent)
            st.session_state.ultimo_caminho = str(atual.parent)
            st.session_state.aviso_procurar = ""
            st.rerun()

    def ir_para_caminho():
        nome_digitado = st.session_state.procura_nome.strip() if 'procura_nome' in st.session_state else ""
        if nome_digitado:
            caminho_completo = os.path.join(st.session_state.diretorio_atual, nome_digitado)
            if os.path.exists(caminho_completo):
                st.session_state.aviso_procurar = ""
                if os.path.isdir(caminho_completo):
                    st.session_state.diretorio_atual = caminho_completo
                    st.session_state.ultimo_caminho = caminho_completo
                else:
                    st.session_state.ultimo_caminho = caminho_completo
                st.rerun()
            else:
                st.session_state.aviso_procurar = f"❌ '{nome_digitado}' não encontrado!"
                st.rerun()
        else:
            st.session_state.aviso_procurar = "Digite um nome!"
            st.rerun()

    def on_pasta_change(pasta_id, caminho):
        if st.session_state[pasta_id]:
            if pasta_id not in st.session_state.expanders_abertos:
                st.session_state.expanders_abertos.append(pasta_id)
            st.session_state.ultimo_caminho = caminho
            st.session_state.diretorio_atual = caminho
            st.session_state.aviso_procurar = ""
        else:
            if pasta_id in st.session_state.expanders_abertos:
                st.session_state.expanders_abertos.remove(pasta_id)
            pasta_pai = Path(caminho).parent
            st.session_state.ultimo_caminho = str(pasta_pai)
            st.session_state.diretorio_atual = str(pasta_pai)
            st.session_state.aviso_procurar = ""

    def on_file_change(chk_id, caminho_item, nome_item, eh_diretorio):
        for k in st.session_state.arquivos_por_pasta:
            if k != chk_id:
                st.session_state[k] = False

        if st.session_state[chk_id]:
            if chk_id not in st.session_state.arquivos_por_pasta:
                st.session_state.arquivos_por_pasta.append(chk_id)
            st.session_state.editor_ativo = nome_item
            st.session_state.ultimo_caminho = caminho_item
            st.session_state.aviso_procurar = ""
        else:
            pasta_pai = Path(caminho_item).parent
            st.session_state.ultimo_caminho = str(pasta_pai)
            st.session_state.aviso_procurar = ""

    def processar_item(nome_item, caminho_item):
        eh_diretorio = os.path.isdir(caminho_item)

        if eh_diretorio:
            pasta_id = f"exp_{caminho_item}"
            st.checkbox(
                '📁 ' + nome_item,
                key=pasta_id,
                value=pasta_id in st.session_state.expanders_abertos,
                on_change=on_pasta_change,
                args=(pasta_id, caminho_item)
            )
            if st.session_state.get(pasta_id):
                l, cont = st.columns([0.5, 9])
                with cont:
                    conteudo_fresco = listar_arquivos_e_pastas(caminho_item)
                    for nome_sub, caminho_sub in conteudo_fresco:
                        processar_item(nome_sub, caminho_sub)
        else:
            chk_id = f"chk_{caminho_item}"
            st.checkbox(
                nome_item,
                key=chk_id,
                on_change=on_file_change,
                args=(chk_id, caminho_item, nome_item, False)
            )

    # HEADER
    # ✅ CORRETO
    st.text_input(label="📁 Diretório Atual", value=st.session_state.diretorio_atual)

    if st.session_state.aviso_procurar:
        st.error(st.session_state.aviso_procurar)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("🔙", width='stretch'):
            voltar_pasta()
    with col2:
        st.text_input(
            'procurar',
            placeholder="Procurar Dentro de:",
            label_visibility='collapsed',
            key="procura_nome"
        )
    with col3:
        if st.button("🔍", width='stretch', type="primary"):
            ir_para_caminho()

    # LISTA PRINCIPAL
    dir_atual_path = Path(st.session_state.diretorio_atual)
    lista_atual = listar_arquivos_e_pastas(dir_atual_path)

    with st.container(height=450):
        for nome_item, caminho_item in lista_atual:
            processar_item(nome_item, caminho_item)

    if st.session_state.ultimo_caminho:
        eh_dir = os.path.isdir(st.session_state.ultimo_caminho)
        tipo = "📁 DIRETÓRIO" if eh_dir else "📄 ARQUIVO"
        return (st.session_state.ultimo_caminho, tipo)
    return ("", "")

# ===============================
# JANELA PRINCIPAL
# ===============================
def Janela_PESQUIZA_PASTAS_ARQUIVOS(st, LISTAR_OQUE, DIRETO_QUE_ESTA_O_EXEC):

    # ---------- SESSION STATE ----------
    st.session_state.setdefault('editor_ativo', None)
    st.session_state.setdefault('expanders_abertos', [])
    st.session_state.setdefault('ultimo_caminho', None)
    st.session_state.setdefault('arquivos_por_pasta', [])
    st.session_state.setdefault('aviso_procurar', "")
    st.session_state.setdefault('nova_pasta_nome', "")
    st.session_state.setdefault('aviso_criar_pasta', "")

    if 'diretorio_atual' not in st.session_state:
        st.session_state.diretorio_atual = str(
            Path(DIRETO_QUE_ESTA_O_EXEC).parent
            if DIRETO_QUE_ESTA_O_EXEC
            else Path.cwd()
        )

    # ---------- AÇÕES ----------
    def voltar_pasta():
        atual = Path(st.session_state.diretorio_atual)
        if atual.parent != atual:
            st.session_state.diretorio_atual = str(atual.parent)
            st.session_state.ultimo_caminho = str(atual.parent)
            st.session_state.aviso_procurar = ""
            st.rerun()

    def ir_para_caminho():
        nome = st.session_state.get("procura_nome", "").strip()
        if not nome:
            st.session_state.aviso_procurar = "Digite um nome!"
            st.rerun()

        caminho = os.path.join(st.session_state.diretorio_atual, nome)
        if os.path.exists(caminho):
            st.session_state.aviso_procurar = ""
            st.session_state.ultimo_caminho = caminho
            if os.path.isdir(caminho):
                st.session_state.diretorio_atual = caminho
            st.rerun()
        else:
            st.session_state.aviso_procurar = f"❌ '{nome}' não encontrado!"
            st.rerun()

    def criar_nova_pasta():
        nome = st.session_state.nova_pasta_nome.strip()

        if not nome:
            st.session_state.aviso_criar_pasta = "Digite um nome para a pasta!"
            return

        caminho_novo = os.path.join(st.session_state.diretorio_atual, nome)

        if os.path.exists(caminho_novo):
            st.session_state.aviso_criar_pasta = "Essa pasta já existe!"
            return

        try:
            os.makedirs(caminho_novo)
            st.session_state.aviso_criar_pasta = ""
            st.session_state.nova_pasta_nome = ""
            st.session_state.ultimo_caminho = caminho_novo
            st.rerun()
        except Exception as e:
            st.session_state.aviso_criar_pasta = f"Erro ao criar pasta: {e}"

    def on_pasta_change(pasta_id, caminho):
        if st.session_state[pasta_id]:
            if pasta_id not in st.session_state.expanders_abertos:
                st.session_state.expanders_abertos.append(pasta_id)
            st.session_state.diretorio_atual = caminho
            st.session_state.ultimo_caminho = caminho
        else:
            if pasta_id in st.session_state.expanders_abertos:
                st.session_state.expanders_abertos.remove(pasta_id)
        st.session_state.aviso_procurar = ""

    def on_file_change(chk_id, caminho_item, nome_item):
        for k in st.session_state.arquivos_por_pasta:
            if k != chk_id:
                st.session_state[k] = False

        if st.session_state[chk_id]:
            if chk_id not in st.session_state.arquivos_por_pasta:
                st.session_state.arquivos_por_pasta.append(chk_id)
            st.session_state.editor_ativo = nome_item
            st.session_state.ultimo_caminho = caminho_item

    # ---------- PROCESSAMENTO ----------
    def processar_item(nome_item, caminho_item):
        if os.path.isdir(caminho_item):
            pasta_id = f"exp_{safe_id(caminho_item)}"

            st.checkbox(
                f"📁 {nome_item}",
                key=pasta_id,
                value=pasta_id in st.session_state.expanders_abertos,
                on_change=on_pasta_change,
                args=(pasta_id, caminho_item)
            )

            if st.session_state.get(pasta_id):
                with st.container():
                    if LISTAR_OQUE.lower() in ('pasta', 'pastas'):
                        conteudo = listar_apenas_pastas(caminho_item)
                    else:
                        conteudo = listar_arquivos_e_pastas(caminho_item)

                    for nome_sub, caminho_sub in conteudo:
                        processar_item(nome_sub, caminho_sub)
        else:
            chk_id = f"chk_{safe_id(caminho_item)}"
            st.checkbox(
                nome_item,
                key=chk_id,
                on_change=on_file_change,
                args=(chk_id, caminho_item, nome_item)
            )

    # ---------- UI ----------
    st.write(f"📂 {st.session_state.diretorio_atual}")

    if st.session_state.aviso_procurar:
        st.error(st.session_state.aviso_procurar)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.button("🔙", width='stretch', on_click=voltar_pasta)
    with col2:
        st.text_input(
            "procurar",
            placeholder="Procurar",
            label_visibility="collapsed",
            key="procura_nome"
        )
    with col3:
        st.button("🔍", width='stretch', type="primary", on_click=ir_para_caminho)

    # ---------- CRIAR PASTA ----------
    st.divider()

    col_a, col_b = st.columns([5, 1])
    with col_a:
        st.text_input(
            "Nova pasta",
            placeholder="Nome da nova pasta",
            key="nova_pasta_nome",
            label_visibility="collapsed"
        )
    with col_b:
        st.button("➕", width='stretch', on_click=criar_nova_pasta)

    if st.session_state.aviso_criar_pasta:
        st.warning(st.session_state.aviso_criar_pasta)

    # ---------- LISTA ----------
    dir_atual = st.session_state.diretorio_atual

    if LISTAR_OQUE.lower() in ('pasta', 'pastas'):
        lista_atual = listar_apenas_pastas(dir_atual)
    else:
        lista_atual = listar_arquivos_e_pastas(dir_atual)

    with st.container(height=450):
        for nome_item, caminho_item in lista_atual:
            processar_item(nome_item, caminho_item)

    # ---------- RETORNO ----------
    if st.session_state.ultimo_caminho:
        eh_dir = os.path.isdir(st.session_state.ultimo_caminho)
        return (
            st.session_state.ultimo_caminho,
            "📁 DIRETÓRIO" if eh_dir else "📄 ARQUIVO"
        )

    return ("", "")


def listar_pythons_windows():
    base = Path.home() / "AppData" / "Local" / "Programs" / "Python"
    pythons = {}
    if not base.exists():
        return pythons

    for pasta in base.iterdir():
        if pasta.is_dir():
            python_exe = pasta / "python.exe"
            if python_exe.exists():
                nome = pasta.name.replace("Python", "")
                if nome.isdigit():
                    versao = f"{nome[0]}.{nome[1:]}"
                else:
                    versao = pasta.name
                pythons[f"Python {versao}"] = str(python_exe)

    return dict(
        sorted(
            pythons.items(),
            key=lambda x: float(x[0].split()[1]),
            reverse=True
        )
    )

