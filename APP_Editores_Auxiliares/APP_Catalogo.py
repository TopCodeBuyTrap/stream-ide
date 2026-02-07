
from APP_SUB_Funcitons import wrap_text, controlar_altura


def catalogar_arquivo_ia(nome_arquivo,caminho,codigo_completo_do_editor,linguagem):
    import os
    import json
    import requests
    import streamlit as st
    from datetime import datetime

    col1, col2 = st.columns([1, 30])
    with col1:
        altura_prev = controlar_altura(st, "Catalogar", altura_inicial=400, passo=300, maximo=800, minimo=200)
    with col2.container(border=True, height=altura_prev):
        col1, col2 = st.columns([3, 1])
        observacao_usuario = col1.text_input("💭 Sua observação:", key=f"obs_{caminho}")
        concluir = col2.button("📚 Gerar catálogo com IA", width='stretch')
        if concluir:

            PASTA_CATALOGO = ".virto_stream"
            CAMINHO_JSON = os.path.join(PASTA_CATALOGO, ".catalogos.json")
            os.makedirs(PASTA_CATALOGO, exist_ok=True)

            caminho_abs = os.path.abspath(caminho)

            if 'catalogos' not in st.session_state:
                if os.path.exists(CAMINHO_JSON):
                    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
                        st.session_state.catalogos = json.load(f)
                else:
                    st.session_state.catalogos = {}

            if not codigo_completo_do_editor.strip():
                st.warning("⚠️ Arquivo vazio")
                return

            prompt = f"""
        Você é um especialista em documentação de código em qualquer linguagem de programação.
        
        Analise o seguinte código e gere um documento organizado exatamente nesse formato:
        
        # BREVE DESCRIÇÃO DO SCRIPT TODO
        Uma ou duas linhas resumindo o que o arquivo inteiro faz.
        
        IMPORTES E MÓDULOS
        - import X  # o que faz, por quê é usado
        - from Y import Z  # breve comentário
        
        DEPOIS EM ORDEM (na sequência que aparecem no código):
        def nome_da_funcao(parametros):  # ou class NomeDaClasse: ou function nome() etc
        # Descrição do que faz, parâmetros importantes, retorno, exceções possíveis.
        
        CHAMADAS E OUTRAS COISAS SOLTAS
        # Comente apenas as linhas ou blocos mais importantes fora de funções/classes
        # ex: x = 10  # valor inicial usado em todo o script
        
        Código do arquivo:
        {codigo_completo_do_editor}
        
        Observação do usuário: {observacao_usuario or "nenhuma"}
        
        Responda somente o documento no formato acima.
        Sem introdução, sem conclusão, sem ``` e sem texto extra.
        """

            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Stream-IDE IA"
            }

            payload = {
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }

            try:
                with st.spinner("🤖 Gerando documentação com IA..."):
                    resp = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=90
                    )
                    resp.raise_for_status()

                documentacao = resp.json()["choices"][0]["message"]["content"].strip()

                catalogo = {
                    "arquivo": nome_arquivo,
                    "caminho": caminho_abs,
                    "linguagem": linguagem,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "documentacao": documentacao
                }

                st.session_state.catalogos[caminho_abs] = catalogo

                with open(CAMINHO_JSON, "w", encoding="utf-8") as f:
                    json.dump(
                        st.session_state.catalogos,
                        f,
                        ensure_ascii=False,
                        indent=2
                    )

                st.success("✅ Documentação salva com sucesso")

                st.markdown("---")
                st.markdown(
                    f"### 📄 Documentação: {nome_arquivo} ({linguagem.upper()})"
                )
                st.code(wrap_text(documentacao, 100), language=linguagem)

                st.download_button(
                    label="📥 Baixar como Markdown",
                    data=documentacao,
                    file_name=f"doc_{nome_arquivo}.txt",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error("🪲 Falha ao gerar documentação")
                st.caption(str(e))


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



def conf_baix_catalogo(st,caminho_completo,nome_pasta):
    import pandas as pd
    import os
    import json
    PASTA_CATALOGO = ".virto_stream"
    CAMINHO_JSON = os.path.join(PASTA_CATALOGO, ".catalogos.json")

    if not os.path.exists(CAMINHO_JSON):
        st.warning("Nenhum catálogo encontrado.")
    else:
        with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
            catalogos = json.load(f)

        if not catalogos:
            st.warning("Catálogo vazio.")
        else:
            dados = []

            for nome_arquivo, info in catalogos.items():
                dados.append({
                    "Arquivo": info.get("arquivo", "desconhecida"),
                    "Data": info.get("data", "sem data")
                })

            df = pd.DataFrame(dados)
            st.dataframe(df, hide_index=True)

        conteudo = "DOCUMENTAÇÃO COMPLETA DO PROJETO\n"
        conteudo += f"{caminho_completo}\n\n\n"

        for nome_arquivo, info in catalogos.items():
            conteudo += (f"--\n\n{info.get('arquivo', 'desconhecida')}\n")
            conteudo += (
                f"{nome_arquivo} / Linguagem: "
                f"{info.get('linguagem', '').upper()}\n\n"
            )
            conteudo += info.get("documentacao", "")

        st.download_button(
            label=f"Download {nome_pasta}",
            data=conteudo.encode("utf-8"),
            file_name=f"{nome_pasta}.txt",
            mime="text/markdown",width='stretch'
        )

def conf_baix_catalogo_bacup(st, caminho_completo, nome_pasta):
    import os
    import json
    import shutil
    from datetime import datetime

    PASTA_CATALOGO = ".virto_stream"
    CAMINHO_JSON = os.path.join(PASTA_CATALOGO, ".catalogos.json")

    PASTA_BACKUP = os.path.join("backup", nome_pasta)
    os.makedirs(PASTA_BACKUP, exist_ok=True)

    if not os.path.exists(CAMINHO_JSON):
        return

    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
        catalogos = json.load(f)

    if not catalogos:
        return

    conteudo = "DOCUMENTAÇÃO COMPLETA DO PROJETO\n\n"
    conteudo += f"{caminho_completo}\n\n"
    conteudo += f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    for nome_arquivo, info in catalogos.items():
        conteudo += f"{info.get('arquivo', 'desconhecida')}\n"
        conteudo += (
            f"{nome_arquivo} / Linguagem: "
            f"{info.get('linguagem', '').upper()}\n\n"
        )
        conteudo += info.get("documentacao", "")
        conteudo += "\n\n---\n\n"

    nome_txt = f"StreamProjet.txt"
    caminho_txt_catalogo = os.path.join(PASTA_CATALOGO, nome_txt)
    caminho_txt_backup = os.path.join(PASTA_BACKUP, nome_txt)

    with open(caminho_txt_catalogo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    shutil.copy2(caminho_txt_catalogo, caminho_txt_backup)
