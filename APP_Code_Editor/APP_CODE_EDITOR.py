from pathlib import Path
from typing import Optional, List

from code_editor import code_editor
import streamlit as st
import sys
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from APP_SUB_Funcitons import _LOGS_popover

from APP_Code_Editor.Configurations import Component_props, editor_props, Atalhos, Opcoes_editor, Menu, Snippets
from APP_Code_Editor.Marca_Anota import Marcadores_Anotatios  # Atualizado para usar a versão melhorada
from APP_Code_Editor.Salvamento import salvar_codigo
from Banco_dados import reset_db, scan_project, scan_virtuestream, checar_organizar_codigo
from APP_Code_Editor.Autocomplete import Completar
from Botoes import Botoes, atualizar_cursor_do_editor, Botao_instalar_modulo, Botao_abrir_definicao
from APP_SUB_Janela_Explorer import Abrir_Arquivo_Select_Tabs

# ========================================
# CONSTANTES GLOBAIS
# ========================================
CAMINHO = Path(r"C:\Users\henri\ProjetoSteamIDE\HENRIQUE\main.py")
NOME_ARQ = os.path.basename(CAMINHO)
ABA_ID = 42
SESSION_STATE = st.session_state

# ========================================
# LISTAS PARA LOGS ORGANIZADOS
# ========================================
editor_logs = []  # Logs relacionados ao editor (renderização, props, buttons, etc.)
processing_logs = []  # Logs de processamento geral (código editado, problemas, etc.)
save_logs = []  # Logs de salvamento

def renderizar_editor(conteudo_inicial, falta_modulo=None,
                      botoes_definicao=None, limite_linha: int = 100, ignore_rules: Optional[List[str]] = None,
                      debug: bool = False):
    """
    Renderiza o editor com completions atualizadas no blur.

    Parâmetros:
    - conteudo_inicial: String do código inicial.
    - falta_modulo: Dict {linha: modulo} para botões de instalação.
    - botoes_definicao: Lista de dicts para botões de definição.
    - limite_linha: Limite de caracteres por linha para annotations (padrão 100).
    - ignore_rules: Lista de regras a ignorar (ex.: ["longline", "docstring"]).
    - debug: Se True, exibe logs de debug via st.write.
    """
    editor_key = f"editor_militar_{ABA_ID}_{NOME_ARQ}"
    conteudo_key = f'conteudo_{editor_key}'

    # Inicializa session state se necessário
    if conteudo_key not in SESSION_STATE:
        SESSION_STATE[conteudo_key] = conteudo_inicial

    if debug:
        editor_logs.append("Conteúdo inicial carregado: " +
                           (repr(conteudo_inicial[:100]) + "..." if len(conteudo_inicial) > 100 else repr(
                               conteudo_inicial)))

    # Lógica para buttons (instalar módulos)
    buttons = []
    if falta_modulo and isinstance(falta_modulo, dict) and falta_modulo:
        cursor_atual = SESSION_STATE.get('cursor_pos', {"row": 0, "column": 0})
        for linha, mod in falta_modulo.items():
            if mod:  # Validação básica
                nome_botao = f"Instalar {mod}"
                try:
                    buttons.extend(Botoes([mod], nome_botao, cursor=cursor_atual))
                    SESSION_STATE['botao_atual'] = nome_botao
                except Exception as e:
                    if debug:
                        editor_logs.append(f"Erro ao criar botão para {mod}: {e}")
        if debug and buttons:
            editor_logs.append(f"Buttons criados para módulos: {list(falta_modulo.values())} na posição {cursor_atual}")

    # Adicione botões de definição se fornecidos
    if botoes_definicao and isinstance(botoes_definicao, list):
        for i, btn in enumerate(botoes_definicao):
            if isinstance(btn, dict) and 'caminho' in btn and 'nome' in btn and 'linha' in btn:
                buttons.append({
                    "name": f"{btn['nome']} | {btn['linha']}",
                    "feather": "Info",
                    "hasText": True,
                    "text": f"Ver {btn['nome']}",
                    "primary": False,
                    "commands": ["submit"],
                    "style": {
                        "bottom": f"{i * 30}px",  # Empilha no final
                        "right": "10px",
                    }
                })
                SESSION_STATE[f"caminho_{btn['nome']}"] = btn['caminho']
            else:
                if debug:
                    editor_logs.append(f"Botão de definição inválido: {btn}")

    # Atualiza completions (com cache se possível)
    SESSION_STATE["texto_editor"] = SESSION_STATE.get(conteudo_key, "")
    try:
        completions_atualizadas = Completar(st)
    except Exception as e:
        if debug:
            editor_logs.append(f"Erro ao gerar completions: {e}")
        completions_atualizadas = []

    # Configurações do editor (busca de session state ou padrões)
    font_size = SESSION_STATE.get('font_size', 15)
    thema_editor = 'idle_fingers'.lower()
    fonte = 'Source Code Pro'

    # Gera props com Marcadores_Anotatios melhorado (usando cache)
    try:
        props = Marcadores_Anotatios.get_props_cached(
            SESSION_STATE[conteudo_key],
            limite_linha=limite_linha,
            ignore_rules=ignore_rules or []
        )
    except Exception as e:
        if debug:
            editor_logs.append(f"Erro ao gerar props: {e}")
        props = {"markers": [], "annotations": []}

    try:
        codigo = code_editor(
            SESSION_STATE[conteudo_key],
            lang='python',
            height='500px',
            shortcuts='vscode',
            response_mode="blur",
            allow_reset=True,
            props=props,
            completions=completions_atualizadas,
            buttons=buttons,
            options=Opcoes_editor(font_size, thema_editor, fonte),
            keybindings=Atalhos(),
            component_props=Component_props(),
            menu=Menu(),
            editor_props=editor_props(),
            snippets=Snippets(),
            key=editor_key)

    except Exception as e:
        st.error(f"Erro ao renderizar editor: {e}")
        return None, conteudo_key

    # Atualiza cursor
    SESSION_STATE["cursor_pos"] = codigo.get('cursor', {"row": 0, "column": 0})

    if debug:
        editor_logs.append("Retorno do code_editor (blur): " + repr(codigo))


    _LOGS_popover(st, f":material/code: Logs de Renderização e Configuração do Editor", editor_logs)
    return codigo, conteudo_key


# ========================================
# EXECUÇÃO PRINCIPAL
# ========================================
conteudo_inicial = Abrir_Arquivo_Select_Tabs(st, CAMINHO)
logs_btn_fuction = []
if 'falta_modulo' not in SESSION_STATE:
    SESSION_STATE['falta_modulo'] = {}

# Primeiro, chama checar_organizar_codigo para obter botoes_definicao
editor_key_temp = f"editor_militar_{ABA_ID}_{NOME_ARQ}"

novo_codigo_completo, problemas, falta_functions, falta_modulo, botoes_definicao = checar_organizar_codigo(editor_key_temp, conteudo_inicial)

# Agora renderiza o editor com os botões
codigo, conteudo_key = renderizar_editor(conteudo_inicial, falta_modulo=SESSION_STATE['falta_modulo'],botoes_definicao=botoes_definicao)

if codigo and 'text' in codigo and codigo['text'].strip():
    novo_codigo_editado = codigo['text']

    processing_logs.append("Novo código editado: " +
                           (repr(novo_codigo_editado[:100]) + "..." if len(novo_codigo_editado) > 100 else repr(
                               novo_codigo_editado)))

    atualizar_cursor_do_editor(codigo)

    # Re-chama checar_organizar_codigo com o código editado
    novo_codigo_completo, problemas, falta_functions, falta_modulo, botoes_definicao = checar_organizar_codigo(editor_key_temp, novo_codigo_editado)

    processing_logs.append("Código após funil: " +
                           (repr(novo_codigo_completo[:100]) + "..." if len(novo_codigo_completo) > 100 else repr(
                               novo_codigo_completo)))
    processing_logs.append("Problemas detectados:\n" + str(problemas))
    processing_logs.append("Falta de funções detectados:\n" + str(falta_functions))
    processing_logs.append("Falta de módulos detectados:\n" + str(falta_modulo))

    SESSION_STATE['falta_modulo'] = falta_modulo

    # Lógica de submit/buttons
    if codigo.get('type') == 'submit':
        button_name = SESSION_STATE.get('botao_atual')
        if button_name and button_name.startswith("Instalar "):
            mod_a_instalar = button_name.replace("Instalar ", "")
            st.toast(f"Clique no botão para instalar {mod_a_instalar}")
            with st.spinner(f"Instalando módulo {mod_a_instalar}..."):
                sucesso = Botao_instalar_modulo(mod_a_instalar)
            if sucesso:
                if mod_a_instalar in SESSION_STATE['falta_modulo'].values():
                    linhas_a_remover = [linha for linha, mod in SESSION_STATE['falta_modulo'].items() if
                                        mod == mod_a_instalar]
                    for linha in linhas_a_remover:
                        del SESSION_STATE['falta_modulo'][linha]

        elif button_name and button_name.startswith("Ver "):
            funcao = button_name.replace("Ver ", "")
            caminho = SESSION_STATE.get(f"caminho_{funcao}")
            if caminho:
                # Chama a função separada para abrir definição
                Botao_abrir_definicao(caminho)
            else:
                st.toast(f"Caminho não encontrado para '{funcao}'.")
    else:
        processing_logs.append(f"Não detectado submit. Tipo: {codigo.get('type')}, Keys: {list(codigo.keys())}")

    if novo_codigo_editado != SESSION_STATE[conteudo_key]:
        if novo_codigo_completo != SESSION_STATE[conteudo_key] or falta_functions:
            SESSION_STATE[conteudo_key] = novo_codigo_completo
            processing_logs.append("Session_state atualizado.")

            logs_save = salvar_codigo(SESSION_STATE, novo_codigo_completo, CAMINHO, NOME_ARQ)
            for log in logs_save:
                save_logs.append(log)

else:
    processing_logs.append("Sem blur ou texto válido.")

_LOGS_popover(st, f":material/save: Logs de Persistência e Salvamento de Dados", save_logs)
_LOGS_popover(st, f":material/terminal: Logs de Processamento e Análise do Código", processing_logs)
