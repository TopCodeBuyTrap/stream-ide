import json
import os
import sys
import time
from pathlib import Path


from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from Banco_dados.autosave_manager import esc_CONTEUDO, ler_CONTEUDO_Coluna_Id


def salvar_codigo(SESSION_STATE,codigo_final, caminho_arquivo, nome_arq):
	"""Salva o código no disco com backup e emergência, retornando logs."""
	logs_save = []

	def log_save(msg):
		logs_save.append(str(msg))

	if not codigo_final.strip():
		log_save("⚠️ Código vazio - Salvamento pulado")
		return logs_save

	if codigo_final:
		try:
			ultimo = ler_CONTEUDO_Coluna_Id(caminho_arquivo, 'ID')
			esc_CONTEUDO(caminho_arquivo, int(ultimo[-1][0]) + 1, codigo_final)
		except IndexError:
			esc_CONTEUDO(caminho_arquivo, 1, codigo_final)

	try:
		import streamlit
		Path(caminho_arquivo).parent.mkdir(parents=True, exist_ok=True)
		backup_path = Path(caminho_arquivo).with_suffix('.py.bak')
		if Path(caminho_arquivo).exists():
			Path(caminho_arquivo).rename(backup_path)
			log_save("🔄 Backup criado")
		Path(caminho_arquivo).write_text(codigo_final, encoding='utf-8')
		log_save("💾 Arquivo salvo no disco")
		streamlit.toast("💾")
		if backup_path.exists():
			backup_path.unlink()
			log_save("🗑️ Backup removido")
		SESSION_STATE['autosave_status'] = f"💾 {nome_arq}"
		log_save("✅ AUTOSAVE: Disco OK")
	except Exception as e:
		emergencia_path = Path(_DIRETORIO_PROJETO_ATUAL_()) / f"EMERGENCIA_{nome_arq}.json"
		emergencia_path.write_text(
			json.dumps({"timestamp": time.time(), "codigo": codigo_final, "erro": str(e)},
			           ensure_ascii=False, indent=2),
			encoding='utf-8')
		log_save(f"⚠️ ERRO: {e} - Emergência salva")

	return logs_save

