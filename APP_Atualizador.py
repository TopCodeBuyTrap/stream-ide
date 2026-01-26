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
	versao_local = ultima_versao()

	try:
		# Adiciona timestamp para evitar cache do request
		url = f"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt?t={int(time.time())}"
		resp = requests.get(url, timeout=5)

		if resp.status_code == 200:
			versao_nova = resp.text.strip()
			Coluna.write(f"🌐 GitHub: v{versao_nova} | Banco: v{versao_local}")

			if versao_nova > versao_local:
				Coluna.error(f"🔔 NOVA VERSÃO DISPONÍVEL: v{versao_nova}")
				if Coluna.button(f"🚀 ATUALIZAR AGORA (v{versao_nova})", use_container_width=True):
					atualizar_tudo(versao_nova)
				return
			else:
				Coluna.success(f"✅ Seu App está atualizado (v{versao_local})")
		else:
			Coluna.info(f"📱 Versão Local: v{versao_local}")

	except Exception as e:
		Coluna.warning(f"Sem conexão: {e}")
		Coluna.info(f"📱 Versão Local: v{versao_local}")


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

	# ✅ 3. DELETA _internal VELHO (força Windows)
	st.sidebar.info("🗑️ Limpando _internal antigo...")
	if internal_dest.sidebar.exists():
		for i in range(3):
			try:
				shutil.rmtree(internal_dest)
				break
			except:
				time.sleep(0.5)

	# ✅ 4. COPIA TODOS ARQUIVOS do GitHub PRA _internal/
	st.sidebar.info("🔄 Copiando arquivos PRA _internal/...")

	for item in github_root.rglob("*"):
		if item.is_file():
			# Calcula destino DENTRO de _internal/
			rel_path = item.relative_to(github_root)
			dest_path = internal_dest / rel_path

			# Cria pastas se necessário
			dest_path.parent.mkdir(parents=True, exist_ok=True)

			# COPIA!
			shutil.copy2(item, dest_path)
			st.sidebar.write(f"✅ {rel_path}")

	# 5. style.css pra RAIZ
	if (github_root / "style.css").exists():
		shutil.copy2(github_root / "style.css", app_root / "style.css")

	# 6. LIMPA
	os.remove(zip_path)
	shutil.rmtree(temp_dir)

	st.sidebar.success(f"🎉 TUDO em _internal/ v{nova_versao}!")
	st.sidebar.balloons()
	st.sidebar.warning("🔄 FECHE e REABRA!")
	time.sleep(3)
	sys.exit(0)
