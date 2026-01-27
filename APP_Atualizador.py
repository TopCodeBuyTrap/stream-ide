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


def checar_atualizacao():
	versao_local = ultima_versao()

	@st.dialog(f":material/format_indent_decrease: Atualizar StreamIDE:  [ {versao_local} ]")
	def menu_principal():
		try:
			url = f"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt?t={int(time.time())}"
			resp = None
			for metodo in range(4):
				try:
					if metodo == 0:
						resp = requests.get(url, timeout=10)
					elif metodo == 1:
						resp = requests.get(url, timeout=10)
					elif metodo == 2:
						resp = requests.get(url, timeout=10, verify=False)
					elif metodo == 3:
						session = requests.Session()
						session.headers.update({'User-Agent': 'Mozilla/5.0'})
						resp = session.get(url, timeout=10, verify=False)
					if resp and resp.status_code == 200: break
				except:
					continue

			if resp and resp.status_code == 200:
				versao_nova = resp.text.strip()
				if versao_nova > versao_local:
					st.success(f"🔔 **NOVA VERSÃO DISPONÍVEL:**  [ {versao_nova} ]")
					if st.button(f":material/queue_play_next: ATUALIZAR para Vesão :material/terminal_output:",
					             use_container_width=True):
						atualizar_tudo(versao_nova)
				else:
					st.success(f"✅ App atualizado [ {versao_nova} ]")
			else:
				st.warning("🌐 GitHub offline")
		except Exception as e:
			st.code(f"Erro: {str(e)[:100]}")

	menu_principal()


def atualizar_tudo(nova_versao):
	app_root = get_app_root()
	salvar_versao(nova_versao)
	st.sidebar.success(f"✅ BANCO v{nova_versao}")

	# 1. DOWNLOAD ZIP
	zip_url = "https://github.com/TopCodeBuyTrap/stream-ide/archive/refs/heads/main.zip"
	zip_path = app_root / "update.zip"
	st.sidebar.info("📥 Baixando...")

	for metodo in range(4):
		try:
			if metodo == 0:
				resp = requests.get(zip_url, timeout=120, stream=True)
			elif metodo == 1:
				resp = requests.get(zip_url, timeout=120, stream=True, verify=False)
			elif metodo == 2:
				s = requests.Session();
				s.headers.update({'User-Agent': 'Mozilla/5.0'})
				resp = s.get(zip_url, timeout=120, stream=True, verify=False)
			elif metodo == 3:
				import urllib.request;
				urllib.request.urlretrieve(zip_url, zip_path);
				break
			resp.raise_for_status()
			with open(zip_path, "wb") as f:
				for chunk in resp.iter_content(8192): f.write(chunk)
			st.sidebar.success("✅ ZIP!")
			break
		except:
			if metodo == 3: st.sidebar.error("❌ Download!"); return

	# 2. EXTRAI
	temp_dir = app_root / "temp_update"
	shutil.rmtree(temp_dir, ignore_errors=True)
	with zipfile.ZipFile(zip_path, "r") as z:
		z.extractall(temp_dir)
	github_root = temp_dir / "stream-ide-main"
	internal_dest = app_root / "_internal"

	# 🛡️ 3. BACKUP certifi/ ANTES da limpeza
	st.sidebar.info("💾 Backup certifi/...")
	certifi_backup = app_root / "certifi_backup"
	if (internal_dest / "certifi").exists():
		shutil.copytree(internal_dest / "certifi", certifi_backup)
		st.sidebar.text("✅ certifi backup OK")
	else:
		st.sidebar.text("⚪ certifi não existia")

	# 4. LIMPA _internal (mantém backup separado)
	st.sidebar.info("🗑️ Limpar _internal...")
	if internal_dest.exists():
		for i in range(10):
			try:
				shutil.rmtree(internal_dest)
				break
			except:
				time.sleep(1)

	# 5. COPIA _internal DO GITHUB
	st.sidebar.info("📁 _internal...")
	contador = 0
	internal_dest.mkdir(exist_ok=True)
	for item in github_root.rglob("*"):
		if item.is_file():
			rel_path = item.relative_to(github_root)
			dest_path = internal_dest / rel_path
			dest_path.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(item, dest_path)
			contador += 1
	st.sidebar.text(f"✅ {contador} arquivos _internal")

	# ✅ 6. RESTAURA certifi/
	if certifi_backup.exists():
		shutil.copytree(certifi_backup, internal_dest / "certifi", dirs_exist_ok=True)
		st.sidebar.success("✅ certifi/ RESTAURADO!")
		shutil.rmtree(certifi_backup)

	# 🧹 7. LIMPA RAIZ .py VELHOS
	st.sidebar.info("🧹 Limpa raiz...")
	for arq_velho in app_root.glob("*.py"):
		if arq_velho.name not in ["atualizador.py"]:  # Protege este
			try:
				arq_velho.unlink()
				st.sidebar.text(f"🗑️ {arq_velho.name}")
			except:
				pass

	# 🏠 8. COPIA RAIZ DO GITHUB
	st.sidebar.info("🏠 Raiz app...")
	arquivos_raiz = ["style.css"]  # ← Arquivos na raiz a ser atualizados

	for arq in arquivos_raiz:
		src = github_root / arq
		if src.exists():
			shutil.copy2(src, app_root / arq)
			st.sidebar.success(f"✅ {arq}")
		else:
			st.sidebar.text(f"⚪ {arq} (não no GitHub)")

	# 📁 9. .arquivos/ RAIZ
	src_arquivos = github_root / ".arquivos"
	if src_arquivos.exists():
		dest_arquivos = app_root / ".arquivos"
		shutil.rmtree(dest_arquivos, ignore_errors=True)
		shutil.copytree(src_arquivos, dest_arquivos)
		st.sidebar.success("✅ .arquivos/")

	# 10. LIMPA TEMP
	os.remove(zip_path)
	shutil.rmtree(temp_dir)

	st.sidebar.markdown("---")
	st.sidebar.success(f"🎉 v{nova_versao} COMPLETO!")
	st.sidebar.info("✅ _internal/ atualizado")
	st.sidebar.info("✅ certifi/ PRESERVADO")
	st.sidebar.info("✅ .arquivos/ atualizado")
	st.sidebar.info("✅ style.css atualizado")
	st.sidebar.balloons()
	st.sidebar.warning("🔄 FECHE E REABRA!")
	time.sleep(5)
	sys.exit(0)
