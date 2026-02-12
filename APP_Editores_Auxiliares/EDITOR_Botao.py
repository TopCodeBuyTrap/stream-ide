import json

def botao_aplica(st, saida_editor, texto, aplicar_no_topo=False):
    """
    Insere 'texto' no editor.

    aplicar_no_topo = True  -> insere em (0,0)
    aplicar_no_topo = False -> insere na posição atual do cursor
    """

    # 🔒 Garante que o retorno sempre seja dict válido
    if not isinstance(saida_editor, dict):
        return {"text": str(saida_editor) if saida_editor else ""}

    # Obtém posição do cursor enviada pelo editor
    cursor_pos = saida_editor.get("cursor", {"row": 0, "column": 0})

    # Se vier como string JSON, converte
    if isinstance(cursor_pos, str):
        try:
            cursor = json.loads(cursor_pos) if cursor_pos else {}
        except Exception:
            cursor = {}
    elif isinstance(cursor_pos, dict):
        cursor = cursor_pos
    else:
        cursor = {}

    # 🔥 Define onde vai aplicar o texto
    if aplicar_no_topo:
        row = 0
        col = 0
    else:
        row = cursor.get("row", 0)
        col = cursor.get("column", 0)

    # Só executa se o botão do editor disparar submit
    if saida_editor.get("type") == "submit":

        # Quebra o código em linhas
        linhas = saida_editor.get("text", "").split("\n")

        # Garante que a linha exista
        while len(linhas) <= row:
            linhas.append("")

        # Insere o texto na posição escolhida
        linhas[row] = linhas[row][:col] + texto + linhas[row][col:]

        # Junta tudo novamente
        novo_texto = "\n".join(linhas)

        # Atualiza cursor após inserção
        novo_cursor = {
            "row": row,
            "column": col + len(texto)
        }

        # Atualiza objeto retornado pelo editor
        saida_editor["text"] = novo_texto
        saida_editor["cursor"] = novo_cursor


        return saida_editor

    # Se não for submit, retorna sem alterar
    return saida_editor
