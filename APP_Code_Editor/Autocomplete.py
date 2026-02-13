import os

from APP_SUB_Controle_Driretorios import VENVE_DO_PROJETO
from Banco_dados import gerar_auto_complete_EDITOR

# ===== Exemplo de uso no editor =====
def_from, def_predefinidos, from_predefinidos = gerar_auto_complete_EDITOR()

def carregar_modulos_venv():
    import sys
    import pkgutil
    from pathlib import Path
    _Python_exe, _Root_path, _Venv_path, _Prompt_venv = VENVE_DO_PROJETO()
    site_packages = Path(_Venv_path) / "Lib" / "site-packages"
    sys.path.insert(0, str(site_packages))

    modulos = {}

    # módulos da venv
    for m in pkgutil.iter_modules([str(site_packages)]):
        modulos[m.name] = [m.name]

    # módulos do projeto (def_predefinidos)
    for nome, dados in def_predefinidos.items():
        modulos[nome] =  os.path.basename(dados["caminho"])

    # 3. Fontes personalizadas
    outras_fontes = [
        {"nome": "filha", "valor": "isadora"},
        {"nome": "amigo", "valor": "joao"}
    ]
    for item in outras_fontes:
        modulos[item["nome"]] = item["valor"]

    return modulos


def Completar(st):
    if "modulos_venv" not in st.session_state:
        st.session_state.modulos_venv = carregar_modulos_venv()

    completions = []
    for nome, origem in st.session_state.modulos_venv.items():
        completions.append({
            "caption": nome,
            "value": nome,
            "meta": origem,
            "name": nome,
            "score": 400
        })

    return completions



