
from pathlib import Path



def _DIRETORIO_EXECUTAVEL_(arquivo=''):# onde o executavel vai ser instalado
    from Banco_dados import ler_A_CONTROLE_ABSOLUTO
    Pasta_Isntal_exec = Path(ler_A_CONTROLE_ABSOLUTO()[0][0]).resolve() # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
    # Pastas relativas à pasta_projeto
    if arquivo == '.arquivos':
        return Path(Pasta_Isntal_exec,'.arquivos')
    else:
        return Pasta_Isntal_exec


def _DIRETORIO_PROJETOS_():
    from Banco_dados import ler_A_CONTROLE_ABSOLUTO
    Pasta_Projetos = Path(ler_A_CONTROLE_ABSOLUTO()[0][1]).resolve()  # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
    return Pasta_Projetos


def _DIRETORIO_PROJETO_ATUAL_():
    from Banco_dados import ler_B_ARQUIVOS_RECENTES
    try: #  Então esse TRY é só para isso. É só para quando ele abrir a segunda tela depois da abertura, né? Aquela que abre o pop-up para para ele criar um novo projeto e mudar ele.
        Projeto_Atual = Path(ler_B_ARQUIVOS_RECENTES()[0][0]).resolve()  # Caminho absoluto do arquivo atual   HENRIQUE TROCAR ISSO DEPOIS
        return Projeto_Atual
    except IndexError:
        return _DIRETORIO_EXECUTAVEL_()




