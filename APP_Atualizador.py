import sys
import os
import shutil
import time
import zipfile
import requests
from pathlib import Path
import streamlit as st

from Banco_Predefinitions import ultima_versao, salvar_versao, atualizar_info_versao


def get_app_root():
	if getattr(sys, 'frozen', False):
		return Path(sys.executable).parent.absolute()
	return Path(__file__).parent.parent.absolute()


def checar_atualizacao():
	versao_local = ultima_versao()

	@st.dialog(f":material/format_indent_decrease: Atualizar StreamIDE:  [ {versao_local} ]")
	def menu_principal():
		# ✅ BOTÃO MANUAL SEMPRE VISÍVEL

		try:
			url = f"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt?t={int(time.time())}"
			resp = requests.get(url, timeout=5)

			if resp.status_code == 200:
				versao_nova = resp.text.strip()

				if versao_nova > versao_local:
					st.success(f"🔔 **NOVA VERSÃO DISPONÍVEL:**  [ {versao_nova} ]")
					if st.button(f":material/queue_play_next: ATUALIZAR para Vesão :material/terminal_output:",
					             use_container_width=True):
						atualizar_tudo(versao_nova)
				else:
					st.success(f"✅ App atualizado [ {versao_nova} ]")
			else:
				st.info(f"📱 v{versao_local}")
		except Exception as e:
			st.warning(f"Erro: {e}")

	menu_principal()

def atualizar_tudo(nova_versao):
	app_root = get_app_root()


	# 1. DOWNLOAD ZIP
	zip_url = "https://github.com/TopCodeBuyTrap/stream-ide/archive/refs/heads/main.zip"
	zip_path = app_root / "update.zip"
	st.info("📥 Baixando...")

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
			st.success("✅ ZIP!")
			break
		except:
			if metodo == 3: st.error("❌ Download!"); return

	# 2. EXTRAI
	temp_dir = app_root / "temp_update"
	shutil.rmtree(temp_dir, ignore_errors=True)
	with zipfile.ZipFile(zip_path, "r") as z:
		z.extractall(temp_dir)
	github_root = temp_dir / "stream-ide-main"
	internal_dest = app_root / "_internal"

	# 🛡️ 3. BACKUP certifi/ ANTES da atualização
	st.info("💾 Backup certifi/...")
	certifi_backup = app_root / "certifi_backup"
	if (internal_dest / "certifi").exists():
		shutil.copytree(internal_dest / "certifi", certifi_backup)
		st.text("✅ certifi backup OK")
	else:
		st.text("⚪ certifi não existia")

	# 4. NÃO APAGAR _internal inteiro, apenas atualiza arquivos do GitHub
	st.info("📁 Atualizando _internal sem apagar certifi...")
	internal_dest.mkdir(exist_ok=True)
	contador = 0
	for item in github_root.rglob("*"):
		if item.is_file():
			rel_path = item.relative_to(github_root)
			dest_path = internal_dest / rel_path
			dest_path.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(item, dest_path)
			contador += 1
	st.text(f"✅ {contador} arquivos _internal atualizados")

	# ✅ 5. RESTAURA certifi/
	if certifi_backup.exists():
		shutil.copytree(certifi_backup, internal_dest / "certifi", dirs_exist_ok=True)
		st.success("✅ certifi/ RESTAURADO!")
		shutil.rmtree(certifi_backup)

	# 🧹 6. LIMPA RAIZ .py VELHOS
	st.info("🧹 Limpa raiz...")
	for arq_velho in app_root.glob("*.py"):
		if arq_velho.name not in ["atualizador.py"]:
			try:
				arq_velho.unlink()
				st.text(f"🗑️ {arq_velho.name}")
			except:
				pass

	# 🏠 7. COPIA RAIZ DO GITHUB
	st.info("🏠 Raiz app...")
	arquivos_raiz = ["style.css"]
	for arq in arquivos_raiz:
		src = github_root / arq
		if src.exists():
			shutil.copy2(src, app_root / arq)
			st.success(f"✅ {arq}")
		else:
			st.text(f"⚪ {arq} (não no GitHub)")

	# 📁 8. .arquivos/ RAIZ
	src_arquivos = github_root / ".arquivos"
	if src_arquivos.exists():
		dest_arquivos = app_root / ".arquivos"
		shutil.rmtree(dest_arquivos, ignore_errors=True)
		shutil.copytree(src_arquivos, dest_arquivos)
		st.success("✅ .arquivos/")

	# 9. LIMPA TEMP
	os.remove(zip_path)
	shutil.rmtree(temp_dir)

	st.markdown("---")
	st.success(f"🎉 v{nova_versao} COMPLETO!")
	st.info("✅ _internal/ atualizado")
	st.info("✅ certifi/ PRESERVADO")
	st.info("✅ .arquivos/ atualizado")
	st.info("✅ style.css atualizado")
	st.balloons()
	salvar_versao(nova_versao)
	st.success(f"✅ BANCO v{nova_versao}")
	st.warning("🔄 FECHE E REABRA!")
	time.sleep(5)
	sys.exit(0)


def chek_atual_simples():
	versao_local = ultima_versao()

	try:
		url = f"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt?t={int(time.time())}"
		resp = requests.get(url, timeout=5)

		if resp.status_code == 200:
			versao_nova = resp.text.strip()
			atualizar_info_versao(versao_local, versao_nova)
		else:pass
	except Exception as e:
		print(f"Erro: {e}")
