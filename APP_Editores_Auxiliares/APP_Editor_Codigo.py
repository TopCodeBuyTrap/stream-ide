from code_editor import code_editor
import os, time, ast
from typing import List, Dict, Any, Optional

from APP_Code_Editor.Autocomplete import Completar
from APP_Code_Editor.Botoes import Botoes, atualizar_cursor_do_editor, Botao_abrir_definicao, Botao_instalar_modulo
from APP_Code_Editor.Configurations import Opcoes_editor, Component_props, Atalhos, Menu, editor_props, Snippets
from APP_Code_Editor.Marca_Anota import Marcadores_Anotatios
from APP_Code_Editor.Salvamento import salvar_codigo
from APP_Editores_Auxiliares.SUB_Traduz_terminal import traduzir_saida
from APP_SUB_Funcitons import _LOGS_popover

from Banco_dados import gerar_auto_complete_EDITOR, checar_organizar_codigo


def mostrar_todos_imports(st,aba_id, codigo):

    # ===== Exemplo de uso no editor =====
    def_from, def_predefinidos, from_predefinidos = gerar_auto_complete_EDITOR()

    tokens = set(codigo.strip().split())

    # DEF
    for token in tokens:
        if token in def_predefinidos:
            caminho = def_predefinidos[token]
            with st.popover(f"def {token}"):
                st.write(caminho)

    # coleta
    itens_import = []

    for token in tokens:
        if token in from_predefinidos:
            dados = from_predefinidos[token]

            itens_import.append({
                "label": f"{token} / {os.path.basename(dados['caminho'])} "
                         f"(linha {dados['linha']})",
                "caminho": dados["caminho"]
            })

    # renderização
    if itens_import:
        with st.popover("import"):
            for i, item in enumerate(itens_import):
                if st.button(
                        item["label"],
                        width="stretch",
                        type="tertiary",
                        key=f"{aba_id}_{i}"
                ):
                    st.write(item["caminho"])

def checar_erros(codigo):
    from pyflakes.api import check
    from pyflakes.reporter import Reporter
    import io
    erros_io = io.StringIO()
    reporter = Reporter(erros_io, erros_io)
    check(codigo, filename="<string>", reporter=reporter)
    erros_texto = erros_io.getvalue().strip()
    erros = []
    if erros_texto:
        for linha in erros_texto.splitlines():
            try:
                # Separar linha e mensagem, ignorando coluna
                partes = linha.split(":", 2)
                linha_num = int(partes[1])
                mensagem = partes[2].strip()
                erros.append({"line": f'{linha_num}>', "message": f'{mensagem}'})
            except:
                continue
    return erros



def Abrir_Arquivo_Select_Tabs(st,conteudo_inicial):
    if not os.path.exists(conteudo_inicial):
        st.warning(f"Arquivo não encontrado: {conteudo_inicial}")
    if not os.path.isfile(conteudo_inicial):
        st.warning( f"'{conteudo_inicial}' é uma pasta, não arquivo")

    try:
        # Tenta ajustar permissão (Windows/Linux)
        os.chmod(conteudo_inicial, 0o666)
        with open(conteudo_inicial, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        st.warning("Sem permissão. Feche outros apps ou rode como admin.")
    except Exception as e:pass
       # st.warning(f"Erro: {e}")


def editor_codigo_autosave(st, aba_id,nome_arq, diretorio_arquivo,  linguagem, thema_editor, font_size, fonte, altura,Info_Col, backgroud):
    _ = st.session_state

    conteudo_inicial = Abrir_Arquivo_Select_Tabs(st,diretorio_arquivo)

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
        editor_key = f"editor_militar_{aba_id}_{nome_arq}"
        conteudo_key = f'conteudo_{editor_key}'

        # Inicializa session state se necessário
        if conteudo_key not in _:
            _[conteudo_key] = conteudo_inicial

        if debug:
            editor_logs.append("Conteúdo inicial carregado: " +
                               (repr(conteudo_inicial[:100]) + "..." if len(conteudo_inicial) > 100 else repr(
                                   conteudo_inicial)))

        # Lógica para buttons (instalar módulos)
        buttons = []
        if falta_modulo and isinstance(falta_modulo, dict) and falta_modulo:
            cursor_atual = _.get('cursor_pos', {"row": 0, "column": 0})
            for linha, mod in falta_modulo.items():
                if mod:  # Validação básica
                    nome_botao = f"Instalar {mod}"
                    try:
                        buttons.extend(Botoes([mod], nome_botao, cursor=cursor_atual))
                        _['botao_atual'] = nome_botao
                    except Exception as e:
                        if debug:
                            editor_logs.append(f"Erro ao criar botão para {mod}: {e}")
            if debug and buttons:
                editor_logs.append(
                    f"Buttons criados para módulos: {list(falta_modulo.values())} na posição {cursor_atual}")

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
                    _[f"caminho_{btn['nome']}"] = btn['caminho']
                else:
                    if debug:
                        editor_logs.append(f"Botão de definição inválido: {btn}")

        # Atualiza completions (com cache se possível)
        _["texto_editor"] = _.get(conteudo_key, "")
        try:
            completions_atualizadas = Completar(st)
        except Exception as e:
            if debug:
                editor_logs.append(f"Erro ao gerar completions: {e}")
            completions_atualizadas = []

        # Gera props com Marcadores_Anotatios melhorado (usando cache)
        try:
            props = Marcadores_Anotatios.get_props_cached(
                _[conteudo_key],
                limite_linha=limite_linha,
                ignore_rules=ignore_rules or []
            )
        except Exception as e:
            if debug:
                editor_logs.append(f"Erro ao gerar props: {e}")
            props = {"markers": [], "annotations": []}

        with Info_Col.container(border=True):
            st.subheader("Imports & Funções")

            mostrar_todos_imports(st, aba_id, _[conteudo_key])

            st.write('novo_cod_import:', _[conteudo_key])

        try:
            codigo = code_editor(
                _[conteudo_key],
                lang=linguagem,
                height=f'{altura}px',
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
        _["cursor_pos"] = codigo.get('cursor', {"row": 0, "column": 0})

        if debug:
            editor_logs.append("Retorno do code_editor (blur): " + repr(codigo))

        _LOGS_popover(st, f":material/code: Logs de Renderização e Configuração do Editor", editor_logs)
        return codigo, conteudo_key

    # ========================================
    # EXECUÇÃO PRINCIPAL

    logs_btn_fuction = []
    if 'falta_modulo' not in _:
        _['falta_modulo'] = {}

    # Primeiro, chama checar_organizar_codigo para obter botoes_definicao
    editor_key_temp = f"editor_militar_{aba_id}_{nome_arq}"

    novo_codigo_completo, problemas, falta_functions, falta_modulo, botoes_definicao = checar_organizar_codigo(
        editor_key_temp, conteudo_inicial)

    # Agora renderiza o editor com os botões
    codigo, conteudo_key = renderizar_editor(conteudo_inicial, falta_modulo=_['falta_modulo'],
                                             botoes_definicao=botoes_definicao)

    # ===== Exibe os links abaixo do editor =====
    with Info_Col:
        erros = checar_erros(codigo)
        if erros:
            avizo = "\n\n".join([f"Linha {e['line']}: {traduzir_saida(e['message'])}" for e in erros]).replace(">:",'\n')
            with st.popover(f'{len(erros)} Erros'):
                with st.container(border=True,height=200):
                    st.warning(avizo)

    if codigo and 'text' in codigo and codigo['text'].strip():
        novo_codigo_editado = codigo['text']

        processing_logs.append("Novo código editado: " +
                               (repr(novo_codigo_editado[:100]) + "..." if len(novo_codigo_editado) > 100 else repr(
                                   novo_codigo_editado)))

        atualizar_cursor_do_editor(codigo)

        # Re-chama checar_organizar_codigo com o código editado
        novo_codigo_completo, problemas, falta_functions, falta_modulo, botoes_definicao = checar_organizar_codigo(
            editor_key_temp, novo_codigo_editado)

        processing_logs.append("Código após funil: " +
                               (repr(novo_codigo_completo[:100]) + "..." if len(novo_codigo_completo) > 100 else repr(
                                   novo_codigo_completo)))
        processing_logs.append("Problemas detectados:\n" + str(problemas))
        processing_logs.append("Falta de funções detectados:\n" + str(falta_functions))
        processing_logs.append("Falta de módulos detectados:\n" + str(falta_modulo))

        _['falta_modulo'] = falta_modulo

        # Lógica de submit/buttons
        if codigo.get('type') == 'submit':
            button_name = _.get('botao_atual')
            if button_name and button_name.startswith("Instalar "):
                mod_a_instalar = button_name.replace("Instalar ", "")
                st.toast(f"Clique no botão para instalar {mod_a_instalar}")
                with st.spinner(f"Instalando módulo {mod_a_instalar}..."):
                    sucesso = Botao_instalar_modulo(mod_a_instalar)
                if sucesso:
                    if mod_a_instalar in _['falta_modulo'].values():
                        linhas_a_remover = [linha for linha, mod in _['falta_modulo'].items() if
                                            mod == mod_a_instalar]
                        for linha in linhas_a_remover:
                            del _['falta_modulo'][linha]

            elif button_name and button_name.startswith("Ver "):
                funcao = button_name.replace("Ver ", "")
                caminho = _.get(f"caminho_{funcao}")
                if caminho:
                    # Chama a função separada para abrir definição
                    Botao_abrir_definicao(caminho)
                else:
                    st.toast(f"Caminho não encontrado para '{funcao}'.")
        else:
            processing_logs.append(f"Não detectado submit. Tipo: {codigo.get('type')}, Keys: {list(codigo.keys())}")

        if novo_codigo_editado != _[conteudo_key]:
            if novo_codigo_completo != _[conteudo_key] or falta_functions:
                _[conteudo_key] = novo_codigo_completo
                processing_logs.append("_ atualizado.")

                logs_save = salvar_codigo(_, novo_codigo_completo, diretorio_arquivo, nome_arq)
                for log in logs_save:
                    save_logs.append(log)

    else:
        processing_logs.append("Sem blur ou texto válido.")

    _LOGS_popover(st, f":material/save: Logs de Persistência e Salvamento de Dados", save_logs)
    _LOGS_popover(st, f":material/terminal: Logs de Processamento e Análise do Código", processing_logs)


    return codigo
