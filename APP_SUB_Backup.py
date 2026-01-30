
import os
import shutil

from Banco_Predefinitions import ler_BACKUP_HORAS_ATUALIZOU, verifica_minutos, ATUAL_BACKUP, \
	ler_BACKUP_QTDS_HORAS_ATUALIZOU, backups_feito


from APP_Catalogo import conf_baix_catalogo_bacup




# Função para criar uma pasta
def Criar_pasta(nome_pasta):
	if not os.path.exists(nome_pasta):
		try:
			os.mkdir(nome_pasta)
		except Exception as e:
			pass
	else:
		pass


# Função para apagar uma pasta
def Apagar_Pasta(pasta):
	try:
		try:
			os.remove(pasta)
		except PermissionError:
			shutil.rmtree(pasta)
	except FileNotFoundError:
		pass
	except OSError as e:
		pass


def BAKCUP(st, min, pasta_local, destino, ignores):
    Criar_pasta(destino)
    from datetime import datetime

    HORAS = str(datetime.today())[11:16]
    HORAS_ANTES = ler_BACKUP_HORAS_ATUALIZOU()

    try:
        if verifica_minutos(HORAS_ANTES, min):
            ATUAL_BACKUP(
                "HORAS_ATUALIZOU",
                HORAS,
                int(ler_BACKUP_QTDS_HORAS_ATUALIZOU()) + 1
            )

            pasta_destino = os.path.join(destino, str(datetime.today()).split()[0])

            Apagar_Pasta(pasta_destino)
            Criar_pasta(pasta_destino)

            conf_baix_catalogo_bacup(st, pasta_local, pasta_destino)

            for diretorio in os.listdir(pasta_local):
                origem = os.path.join(pasta_local, diretorio)
                if diretorio not in str(ignores):
                    try:
                        shutil.copy2(origem, pasta_destino)
                    except Exception:
                        try:
                            shutil.copytree(
                                origem,
                                os.path.join(pasta_destino, diretorio)
                            )
                        except Exception:
                            pass

        qr = []
        for diretorio in os.listdir(destino):
            qr.append(diretorio)

        ATUAL_BACKUP("QTDS_BACKUP", len(qr))

        st.toast(f"Backup :\n{backups_feito()}")

    except:
        pass
