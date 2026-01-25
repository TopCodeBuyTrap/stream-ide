import sys
import os
import shutil
import zipfile
import requests
from pathlib import Path
import streamlit as st


def get_app_root():
	if getattr(sys, 'frozen', False):
		return Path(sys.executable).parent.absolute()
	return Path(__file__).parent.parent.absolute()


def versao_atual():
	vfile = get_app_root() / "version.txt"
	return vfile.read_text().strip() if vfile.exists() else "0.0.0"


def checar_atualizacao(Coluna):
	"""Checa versão e mostra botão se tiver update"""
	app_root = get_app_root()

	# ✅ CRIA version.txt na RAIZ automaticamente
	version_file = app_root / "version.txt"
	if not version_file.exists():
		version_file.write_text("0.0.0")

	versao_local = versao_atual()

	try:
		# ✅ URL EXATA do SEU arquivo (MAIÚSCULO)
		resp = requests.get("https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt",
		                    timeout=5)

		if resp.status_code != 200:
			st.toast("ℹ️ latest_version.txt não encontrado")
			return

		versao_nova = resp.text.strip()

		if versao_nova > versao_local:
			if Coluna.button(f"🔄 ATUALIZAR v{versao_nova}", use_container_width=True):
				atualizar_tudo(versao_nova)
		else:
			st.toast("✅ App atualizado")

	except:
		st.toast("ℹ️ Sem internet para checar updates")


def atualizar_tudo(nova_versao):
	"""Faz update completo"""
	app_root = get_app_root()
	versao_antiga = versao_atual()

	st.toast(f"📂 Atualizando: {app_root}")

	with st.spinner("🔄 **Atualizando...**"):
		try:
			# 1. BACKUP
			backup_dir = app_root / f"backup_v{versao_antiga}"
			if backup_dir.exists():
				shutil.rmtree(backup_dir)
			shutil.copytree(app_root, backup_dir)

			# 2. BAIXA ZIP
			zip_url = "https://github.com/TopCodeBuyTrap/stream-ide/archive/refs/heads/main.zip"
			zip_path = app_root / "update.zip"

			resp = requests.get(zip_url, timeout=30)
			resp.raise_for_status()
			with open(zip_path, "wb") as f:
				f.write(resp.content)

			# 3. EXTRAI
			with zipfile.ZipFile(zip_path, "r") as z:
				z.extractall(app_root / "temp")

			temp_dir = app_root / "temp" / "stream-ide-main"

			# 4. SUBSTITUI _internal COMPLETA
			internal_temp = temp_dir / "_internal"
			if internal_temp.exists():
				shutil.rmtree(app_root / "_internal")
				shutil.move(str(internal_temp), str(app_root / "_internal"))

			# 5. style.css RAIZ
			for css_file in temp_dir.glob("style.css"):
				shutil.copy2(css_file, app_root / "style.css")

			# 6. .arquivos só IMAGENS
			arquivos_temp = temp_dir / ".arquivos"
			if arquivos_temp.exists():
				for img in arquivos_temp.rglob("*"):
					if img.is_file() and img.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
						rel_path = img.relative_to(arquivos_temp)
						dest_path = app_root / ".arquivos" / rel_path
						dest_path.parent.mkdir(parents=True, exist_ok=True)
						shutil.copy2(img, dest_path)

			# 7. SALVA NOVA VERSÃO na RAIZ
			(app_root / "version.txt").write_text(nova_versao)

			# 8. LIMPA
			os.remove(zip_path)
			shutil.rmtree(app_root / "temp")

			st.success(f"🎉 **ATUALIZADO v{nova_versao}!**")
			st.balloons()
			st.rerun()

		except Exception as e:
			st.error(f"❌ Erro: {str(e)}")

