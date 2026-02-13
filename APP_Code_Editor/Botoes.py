# Botoes.py - ATUALIZADO PARA USAR O NOME DO MÓDULO NO TEXT E MELHORAR INSTALAÇÃO
import json
import streamlit as st



def inicializar_estado(st):
    if 'cursor_pos' not in st.session_state:
        st.session_state.cursor_pos = {"row": 0, "column": 0}

def Botoes(faltando, nome, cursor=None):
    """BOTÃO EM CIMA DO CURSOR - AGORA USA O NOME DO MÓDULO NO TEXT"""
    inicializar_estado(st)

    # usa cursor passado ou pega da sessão
    if cursor is None:
        cursor = st.session_state.cursor_pos

    # trata se for string
    if isinstance(cursor, str):
        try:
            cursor = json.loads(cursor)
        except:
            cursor = {"row": 0, "column": 0}

    row = cursor.get("row", 0)
    col = cursor.get("column", 0)

    # calcula posição do botão
    top_px = row * 24
    right_px = max(1, 300 - col * 8)

    if len(faltando) > 0:
        return [{
            "name": nome,  # Nome do botão (ex.: "Instalar testando_botao")
            "feather": "Download",  # Ícone mais apropriado para instalar
            "hasText": True,
            "text": nome,  # AGORA USA O NOME PASSADO (ex.: "Instalar testando_botao") EM VEZ DE "X pkgs"
            "primary": True,
            "commands": ["submit"],
            "style": {
                "top": f"{top_px}px",
                "right": f"{right_px}px",
            }
        }]
    return []

def atualizar_cursor_do_editor(saida_editor):
    """🔥 CORRIGIDO - TRATA TODOS OS TIPOS"""
    if isinstance(saida_editor, dict):
        cursor_pos = saida_editor.get("cursor")
        if cursor_pos is None:
            st.session_state.cursor_pos = {"row": 0, "column": 0}
            return True

        # TRATA STRING, DICT, QUALQUER COISA
        if isinstance(cursor_pos, str):
            try:
                cursor = json.loads(cursor_pos)
            except:
                cursor = {"row": 0, "column": 0}
        elif isinstance(cursor_pos, dict):
            cursor = cursor_pos
        else:
            cursor = {"row": 0, "column": 0}

        st.session_state.cursor_pos = cursor
        return True
    return False

def botao_aplica_cursor(st, saida_editor, texto):
    inicializar_estado(st)
    atualizar_cursor_do_editor(saida_editor)

    cursor = st.session_state.cursor_pos
    row = cursor.get("row", 0)
    col = cursor.get("column", 0)

    linhas = saida_editor.get("text", "").split("\n")
    while len(linhas) <= row:
        linhas.append("")

    # garante que a linha existe e col não ultrapassa
    linha_atual = linhas[row]
    if col > len(linha_atual):
        col = len(linha_atual)

    linhas[row] = linha_atual[:col] + texto + linha_atual[col:]
    if saida_editor.get("type") == "submit" and isinstance(saida_editor, dict):

        # atualiza cursor considerando múltiplas linhas no texto inserido
        if "\n" in texto:
            novas_linhas = texto.split("\n")
            row += len(novas_linhas) - 1
            col = len(novas_linhas[-1])
        else:
            col += len(texto)

        saida_editor["text"] = "\n".join(linhas)
        saida_editor["cursor"] = {"row": row, "column": col}
        st.session_state.cursor_pos = saida_editor["cursor"]

    return saida_editor

def Botao_instalar_modulo(modulo):
    # LÓGICA PARA INSTALAR MÓDULO COM SPINNER E FEEDBACK
    import subprocess
    from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO
    _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
    try:
        # Executa pip install com spinner (mas como é função, o spinner é chamado no app)
        result = subprocess.run([_Python_exe, "-m", "pip", "install", modulo], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            st.toast(f"Módulo {modulo} instalado com sucesso!")
            from Banco_dados import scan_project, reset_db
            reset_db()
            scan_project()

            return True
        else:
            st.error(f"Falha ao instalar {modulo}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        st.error(f"Timeout ao instalar {modulo}.")
        return False
    except Exception as e:
        st.error(f"Erro inesperado ao instalar {modulo}: {e}")
        return False
