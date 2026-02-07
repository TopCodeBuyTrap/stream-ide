import os
import shutil
import time
from pathlib import Path
from datetime import datetime
from Banco_Predefinitions import (
	ler_BACKUP_HORAS_ATUALIZOU, verifica_minutos, ATUAL_BACKUP,
	ler_BACKUP_QTDS_HORAS_ATUALIZOU, backups_feito
)
from APP_Editores_Auxiliares.APP_Catalogo import conf_baix_catalogo_bacup


def Criar_pasta(nome_pasta):
	Path(nome_pasta).mkdir(parents=True, exist_ok=True)


def Apagar_Pasta(pasta):
	try:
		if os.path.isfile(pasta):
			os.remove(pasta)
		elif os.path.isdir(pasta):
			shutil.rmtree(pasta)
	except:
		pass


def BAKCUP(st, minutos_atualizar, pasta_local, destino, ignores=None):
	"""
	Backup AUTOMÁTICO a cada X minutos SEM PISCAR
	"""
	if ignores is None:
		ignores = ['.idea', '.venv', 'build', 'dist', '.virto_stream', '.gitignore']

	# ✅ INICIALIZAÇÃO DO SESSION_STATE DENTRO DA FUNÇÃO (CORREÇÃO DO ERRO!)
	if 'backup_ultimo_check' not in st.session_state:
		st.session_state.backup_ultimo_check = 0
	if 'backup_executando' not in st.session_state:
		st.session_state.backup_executando = False

	agora = datetime.now()
	tempo_atual = time.time()

	# Timer interno: só checa a cada X minutos
	if tempo_atual - st.session_state.backup_ultimo_check < (minutos_atualizar * 60):
		return  # Sai silenciosamente

	# Verifica se precisa fazer backup mesmo
	hora_atual = agora.strftime("%H:%M")
	hora_ultimo_backup = ler_BACKUP_HORAS_ATUALIZOU()

	if not verifica_minutos(hora_ultimo_backup, minutos_atualizar):
		st.session_state.backup_ultimo_check = tempo_atual  # Só atualiza timer
		return

	# 🚫 PREVINE BACKUP DUPLICADO
	if st.session_state.backup_executando:
		return

	st.session_state.backup_executando = True

	try:
		# Marca como feito PRIMEIRO (evita loop)
		ATUAL_BACKUP(
			"HORAS_ATUALIZOU",
			hora_atual,
			int(ler_BACKUP_QTDS_HORAS_ATUALIZOU()) + 1
		)

		# Cria pasta do dia
		pasta_dia = os.path.join(destino, agora.strftime("%Y-%m-%d"))
		Apagar_Pasta(pasta_dia)
		Criar_pasta(pasta_dia)

		# Backup catálogo
		conf_baix_catalogo_bacup(st, pasta_local, pasta_dia)

		# Copia com progresso
		progress_bar = st.progress(0)
		status_text = st.empty()

		itens_totais = sum(1 for d in os.listdir(pasta_local) if d not in ignores)
		contador = 0

		for diretorio in os.listdir(pasta_local):
			if diretorio in ignores:
				continue

			origem = os.path.join(pasta_local, diretorio)
			destino_item = os.path.join(pasta_dia, diretorio)

			try:
				if os.path.isfile(origem):
					shutil.copy2(origem, destino_item)
				else:
					shutil.copytree(origem, destino_item, dirs_exist_ok=True)
			except:
				pass

			contador += 1
			progress_bar.progress(contador / itens_totais)
			status_text.text(f"Copiando: {diretorio} ({contador}/{itens_totais})")

		# Finaliza
		backups_totais = len([d for d in os.listdir(destino) if os.path.isdir(os.path.join(destino, d))])
		ATUAL_BACKUP("QTDS_BACKUP", backups_totais)

		progress_bar.empty()
		status_text.success(f"✅ Backup concluído! {backups_feito()}")

	except Exception as e:
		st.error(f"❌ Backup falhou: {str(e)}")

	finally:
		# ✅ SEMPRE atualiza timer e libera
		st.session_state.backup_ultimo_check = tempo_atual
		st.session_state.backup_executando = False

