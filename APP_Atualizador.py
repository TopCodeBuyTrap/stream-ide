import sys
import os
import shutil
import time
import zipfile
import requests
from pathlib import Path
import streamlit as st

from Banco_Predefinitions import ultima_versao, salvar_versao


def get_app_root():
	if getattr(sys, 'frozen', False):
		return Path(sys.executable).parent.absolute()
	return Path(__file__).parent.parent.absolute()



def checar_atualizacao(Coluna):
	# ✅ DESABILITA SSL VERIFICATION (PyInstaller fix)
	versao_local = ultima_versao()

	try:
		url = f"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt?t={int(time.time())}"

		# FIX SSL PyInstaller
		resp = requests.get(url, timeout=5, verify=False)

		if resp.status_code == 200:
			versao_nova = resp.text.strip()

			if versao_nova > versao_local:
				Coluna.toast(f"🔔 NOVA VERSÃO v{versao_nova}")
				if Coluna.button(f"🚀 ATUALIZAR v{versao_nova}", use_container_width=True):
					atualizar_tudo(versao_nova)
			else:
				Coluna.success(f"✅ v{versao_local}")
		else:
			Coluna.error("GitHub offline")
	except Exception as e:
		Coluna.code(f"Erro: {e}")



def atualizar_tudo(nova_versao):
	app_root = get_app_root()
	versao_antiga = ultima_versao()

	# 1. SALVA BANCO
	salvar_versao(nova_versao)
	st.sidebar.success(f"✅ BANCO v{nova_versao}")

	# 2. DOWNLOAD + EXTRAI
	zip_url = "https://github.com/TopCodeBuyTrap/stream-ide/archive/refs/heads/main.zip"
	zip_path = app_root / "update.zip"

	resp = requests.get(zip_url, timeout=60)
	with open(zip_path, "wb") as f:
		f.write(resp.content)

	temp_dir = app_root / "temp_update"
	shutil.rmtree(temp_dir, ignore_errors=True)
	with zipfile.ZipFile(zip_path, "r") as z:
		z.extractall(temp_dir)

	github_root = temp_dir / "stream-ide-main"
	internal_dest = app_root / "_internal"

	# ✅ 3. DELETA _internal VELHO (CORRIGIDO)
	st.sidebar.info("🗑️ Limpando _internal...")
	if internal_dest.exists():  # ← CORRIGIDO!
		for i in range(3):
			try:
				shutil.rmtree(internal_dest)
				break
			except:
				time.sleep(0.5)

	# ✅ 4. COPIA TODOS ARQUIVOS PRA _internal/
	st.sidebar.info("🔄 Copiando 74 arquivos...")
	contador = 0

	for item in github_root.rglob("*"):
		if item.is_file():
			rel_path = item.relative_to(github_root)
			dest_path = internal_dest / rel_path
			dest_path.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(item, dest_path)
			contador += 1

	st.sidebar.success(f"✅ {contador} arquivos copiados!")

	# 5. style.css pra RAIZ
	if (github_root / "style.css").exists():
		shutil.copy2(github_root / "style.css", app_root / "style.css")
		st.sidebar.success("✅ style.css OK")

	# 6. LIMPA
	os.remove(zip_path)
	shutil.rmtree(temp_dir)

	st.sidebar.success(f"🎉 ATUALIZADO v{nova_versao}!")
	st.sidebar.balloons()
	st.sidebar.warning("🔄 FECHE e REABRA!")
	time.sleep(3)
	sys.exit(0)
