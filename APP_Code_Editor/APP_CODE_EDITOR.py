import os
from pathlib import Path

from code_editor import code_editor
import streamlit as st
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from APP_Code_Editor.Salvamento import salvar_codigo
from Banco_dados import checar_organizar_codigo
from APP_Code_Editor.Autocomplete import Completar
from Botoes import Botoes, atualizar_cursor_do_editor, Botao_instalar_modulo  # Importando as funções de Botoes.py

from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs

# ========================================
# CONSTANTES GLOBAIS
# ========================================
CAMINHO = Path(r"C:\Users\henri\ProjetoSteamIDE\HENRIQUE\main.py")
NOME_ARQ = os.path.basename(CAMINHO)
ABA_ID = 42
SESSION_STATE = st.session_state

def renderizar_editor(conteudo_inicial, falta_modulo=None):
    """Renderiza o editor e retorna o código do blur e a key do session_state."""
    editor_key = f"editor_militar_{ABA_ID}_{NOME_ARQ}"
    conteudo_key = f'conteudo_{editor_key}'

    if conteudo_key not in SESSION_STATE:
        SESSION_STATE[conteudo_key] = conteudo_inicial

    st.write("LOG: Conteúdo inicial carregado:",
             repr(conteudo_inicial[:100]) + "..." if len(conteudo_inicial) > 100 else repr(conteudo_inicial))

    # Lógica para buttons: se falta_modulo for passado e não vazio, cria botões para instalar módulos na posição do cursor atual
    buttons = []
    if falta_modulo and isinstance(falta_modulo, dict) and len(falta_modulo) > 0:
        # Usa o cursor atual do session_state para posicionar os botões
        cursor_atual = SESSION_STATE.get('cursor_pos', {"row": 0, "column": 0})
        for linha, mod in falta_modulo.items():  # Itera sobre items para pegar linha e mod
            nome_botao = f"Instalar {mod}"
            buttons.extend(Botoes([mod], nome_botao, cursor=cursor_atual))
            # Armazena o nome do botão no session_state para usar no submit
            SESSION_STATE['botao_atual'] = nome_botao
        st.write(f"LOG: Buttons criados para módulos: {list(falta_modulo.values())} na posição {cursor_atual}")  # Log para debug

    codigo = code_editor(
        SESSION_STATE[conteudo_key],
        lang='python',
        height='300px',
        shortcuts='vscode',
        response_mode="blur",  # Blur controlado pela condição
        allow_reset=True,  # Permite atualização imediata do editor com mudanças do funil
        completions=Completar(st),
        buttons=buttons,  # Buttons dinâmicos baseados em falta_modulo
        key=editor_key
    )

    st.write("LOG: Retorno do code_editor (blur):", repr(codigo))

    return codigo, conteudo_key

# ========================================
# EXECUÇÃO PRINCIPAL
# ========================================
conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, CAMINHO)

# Inicializa falta_modulo se não existir
if 'falta_modulo' not in SESSION_STATE:
    SESSION_STATE['falta_modulo'] = {}

# Renderiza o editor com buttons baseados em falta_modulo atual
codigo, conteudo_key = renderizar_editor(conteudo_inicial, falta_modulo=SESSION_STATE['falta_modulo'])

if codigo and 'text' in codigo and codigo['text'].strip():
    novo_codigo_editado = codigo['text']

    st.write("LOG: Novo código editado:",
             repr(novo_codigo_editado[:100]) + "..." if len(novo_codigo_editado) > 100 else repr(novo_codigo_editado))

    # Atualiza o cursor no session_state com o cursor do blur
    atualizar_cursor_do_editor(codigo)

    # Sempre processa no blur (independentemente de mudança) para detectar módulos faltando e atualizar buttons
    editor_key = f"editor_militar_{ABA_ID}_{NOME_ARQ}"
    novo_codigo_completo, problemas, falta_fuctions, falta_modulo = checar_organizar_codigo(editor_key, novo_codigo_editado)

    st.write("LOG: Código após funil:",
             repr(novo_codigo_completo[:100]) + "..." if len(novo_codigo_completo) > 100 else repr(
                 novo_codigo_completo))
    st.write("LOG: Problemas detectados:\n", problemas)
    st.write("LOG: falta de funções detectados:\n", falta_fuctions)
    st.write("LOG: falta de módulos detectados:\n", falta_modulo)

    # Atualiza falta_modulo no session_state para os buttons
    SESSION_STATE['falta_modulo'] = falta_modulo

    # Verifica se o tipo é 'submit' (botão clicado) e instala o módulo correspondente
    if codigo.get('type') == 'submit':
        # Usa o nome do botão armazenado no session_state
        button_name = SESSION_STATE.get('botao_atual')
        if button_name and button_name.startswith("Instalar "):
            mod_a_instalar = button_name.replace("Instalar ", "")  # Extrai o nome do módulo
            st.toast(f"Clique no botão para instalar {mod_a_instalar}")  # Log para debug
            with st.spinner(f"Instalando módulo {mod_a_instalar}..."):
                sucesso = Botao_instalar_modulo(mod_a_instalar)
            if sucesso:
                # Remove o módulo da lista de faltantes
                if mod_a_instalar in SESSION_STATE['falta_modulo'].values():
                    linhas_a_remover = [linha for linha, mod in SESSION_STATE['falta_modulo'].items() if mod == mod_a_instalar]
                    for linha in linhas_a_remover:
                        del SESSION_STATE['falta_modulo'][linha]
        else:
            st.write(f"LOG: Botão clicado mas nome inválido: {button_name}")  # Log para debug
    else:
        st.write(f"LOG: Não detectado submit. Tipo: {codigo.get('type')}, Keys: {list(codigo.keys())}")  # Log para debug

    # Verifica se houve mudança real no código editado (controla blurs falsos)
    if novo_codigo_editado != SESSION_STATE[conteudo_key]:
        # Sempre atualiza se o código mudou ou se falta_fuctions > 0 (força aplicação de imports)
        if novo_codigo_completo != SESSION_STATE[conteudo_key] or falta_fuctions:
            SESSION_STATE[conteudo_key] = novo_codigo_completo
            st.write("LOG: Session_state atualizado.")

            logs_save = salvar_codigo(SESSION_STATE, novo_codigo_completo, CAMINHO, NOME_ARQ)
            for log in logs_save:
                st.write(f"LOG SAVE: {log}")

else:
    st.write("LOG: Sem blur ou texto válido.")