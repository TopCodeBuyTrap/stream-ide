# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('C:\\Users\\henri\\PycharmProjects\\Stream-IDE\\APP_.py', '.')]
binaries = []
hiddenimports = ['APP_Atualizador.checar_atualizacao', 'APP_Catalogo.conf_baix_catalogo', 'APP_Editor_Run_Preview.Editor_Simples', 'APP_Htmls.Carregamento_BancoDados_Temas', 'APP_Menus.Abrir_Menu', 'APP_Menus.Cria_Projeto_pouppap', 'APP_Menus.Custom', 'APP_SUB_Backup.BAKCUP', 'APP_SUB_Controle_Driretorios._DIRETORIO_EXECUTAVEL_', 'APP_SUB_Controle_Driretorios._DIRETORIO_PROJETOS_', 'APP_SUB_Controle_Driretorios._DIRETORIO_PROJETO_ATUAL_', 'APP_SUB_Customizar.Customization', 'APP_SUB_Funcitons.Button_Nao_Fecha', 'APP_SUB_Funcitons.Identificar_linguagem', 'APP_SUB_Funcitons.Linha_Sep', 'APP_SUB_Funcitons.chec_se_arq_do_projeto', 'APP_SUB_Funcitons.contar_estrutura', 'APP_SUB_Funcitons.data_sistema', 'APP_SUB_Funcitons.escreve', 'APP_SUB_Funcitons.limpar_CASH', 'APP_SUB_Funcitons.resumo_pasta', 'APP_SUB_Janela_Explorer.Abrir_Arquivo_Select_Tabs', 'APP_SUB_Janela_Explorer.Open_Explorer', 'APP_SUB_Janela_Explorer.listar_arquivos_e_pastas', 'APP_Sidebar.Sidebar_Diretorios', 'APP_Terminal.Terminal', 'Abertura_TCBT.Abertura', 'Banco_Predefinitions.ultima_versao', 'Banco_dados.ATUAL_B_ARQUIVOS_RECENTES', 'Banco_dados.Del_A_CONTROLE_ABSOLUTO', 'Banco_dados.Del_B_ARQUIVOS_RECENTES', 'Banco_dados.Del_CUSTOMIZATION', 'Banco_dados.esc_A_CONTROLE_PROJETOS', 'Banco_dados.esc_B_ARQUIVOS_RECENTES', 'Banco_dados.ler_A_CONTROLE_ABSOLUTO', 'Banco_dados.ler_A_CONTROLE_PROJETOS', 'Banco_dados.ler_B_ARQUIVOS_RECENTES', 'Banco_dados.se_B_ARQUIVOS_RECENTES', 'datetime.datetime', 'os', 'pathlib.Path', 'streamlit', 'sys']
datas += copy_metadata('streamlit')
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\henri\\AppData\\Local\\Temp\\tmptq1t96oo.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Stream_IDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Stream_IDE',
)
