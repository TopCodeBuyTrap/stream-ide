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
	versao_local = ultima_versao()  # ✅ SÓ BANCO

	try:
		Coluna.write("🔍 Verificando...")
		resp = requests.get(
			"https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/main/LATEST_VERSION.txt",
			timeout=5
		)

		if resp.status_code == 200:
			versao_nova = resp.text.strip()
			Coluna.write(f"🌐 GitHub: v{versao_nova} | Banco: v{versao_local}")

			if versao_nova > versao_local:
				Coluna.error(f"🔔 UPDATE v{versao_nova}")
				if Coluna.button(f"🚀 ATUALIZAR v{versao_nova}", use_container_width=True):
					atualizar_tudo(versao_nova)
				return
			else:
				Coluna.success(f"✅ v{versao_local} ATUAL")
		else:
			Coluna.info(f"📱 Banco: v{versao_local}")

	except:
		Coluna.info(f"📱 Banco: v{versao_local}")


def atualizar_tudo(nova_versao):
	app_root = get_app_root()
	versao_antiga = ultima_versao()

	# ✅ 1º SALVA BANCO
	salvar_versao(nova_versao)
	st.success(f"✅ BANCO v{nova_versao}")

	# 2. FORÇA DELEÇÃO _internal (PyInstaller bug)
	st.info("🗑️ FORÇANDO deleção _internal...")
	internal_path = app_root / "_internal"

	# TENTA VÁRIAS VEZES (Windows trava)
	for i in range(5):
		try:
			if internal_path.exists():
				shutil.rmtree(internal_path, ignore_errors=True)
				time.sleep(0.5)
			break
		except:
			st.warning(f"Tentativa {i + 1}/5...")
			time.sleep(1)

	# 3. BACKUP
	backup_dir = app_root / f"backup_v{versao_antiga}"
	shutil.copytree(app_root, backup_dir)

	# 4. BAIXA + EXTRAI
	zip_url = "https://github.com/TopCodeBuyTrap/stream-ide/archive/refs/heads/main.zip"
	zip_path = app_root / "update.zip"

	resp = requests.get(zip_url, timeout=30)
	with open(zip_path, "wb") as f:
		f.write(resp.content)

	os.makedirs(app_root / "temp", exist_ok=True)
	with zipfile.ZipFile(zip_path, "r") as z:
		z.extractall(app_root / "temp")

	temp_dir = app_root / "temp" / "stream-ide-main"
	internal_temp = temp_dir / "_internal"

	# ✅ 5. MOVE _internal NOVO (força overwrite)
	st.info("🔄 MOVENDO _internal NOVO...")
	if internal_temp.exists():
		shutil.move(str(internal_temp), str(internal_path))
		st.success("✅ _internal SOBRESCRITO!")
	else:
		st.error("❌ _internal NÃO ACHA NO GITHUB!")

	# 6. style.css + imagens (igual)
	css_file = temp_dir / "style.css"
	if css_file.exists():
		shutil.copy2(css_file, app_root / "style.css")

	arquivos_temp = temp_dir / ".arquivos"
	if arquivos_temp.exists():
		for img in arquivos_temp.rglob("*"):
			if img.is_file() and img.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]:
				rel = img.relative_to(arquivos_temp)
				dest = app_root / ".arquivos" / rel
				dest.parent.mkdir(parents=True, exist_ok=True)
				shutil.copy2(img, dest)

	# 7. LIMPA
	os.remove(zip_path)
	shutil.rmtree(app_root / "temp")

	st.success(f"🎉 ARQUIVOS ATUALIZADOS v{nova_versao}")
	st.balloons()
	st.info("⚠️ FECHE O APP e ABRA DE NOVO!")

	# PyInstaller PRECISA fechar completamente
	import sys
	time.sleep(3)
	sys.exit(0)
