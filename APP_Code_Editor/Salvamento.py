import json
import time
from pathlib import Path

from APP_SUB_Controle_Driretorios import _DIRETORIO_PROJETO_ATUAL_


def salvar_codigo(SESSION_STATE,codigo_final, caminho_arquivo, nome_arq):
	"""Salva o código no disco com backup e emergência, retornando logs."""
	logs_save = []

	def log_save(msg):
		logs_save.append(str(msg))

	if not codigo_final.strip():
		log_save("⚠️ Código vazio - Salvamento pulado")
		return logs_save

	try:
		Path(caminho_arquivo).parent.mkdir(parents=True, exist_ok=True)
		backup_path = Path(caminho_arquivo).with_suffix('.py.bak')
		if Path(caminho_arquivo).exists():
			Path(caminho_arquivo).rename(backup_path)
			log_save("🔄 Backup criado")
		Path(caminho_arquivo).write_text(codigo_final, encoding='utf-8')
		log_save("💾 Arquivo salvo no disco")
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

