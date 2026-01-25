import os
from pathlib import Path

root_dir = Path(".")

# Lista pra controlar o que incluir
itens_para_ignorar = {
	"APP_.py", "dist", "build", "_Criar_Exec", "__pycache__",
	"Base_Dados.db", "Base_Dados_PreDefinidos.db",
	"INSTALL", "LICENSE", "Stream_IDE.spec", "README.md",
	"streamide.spec", ".git", ".gitattributes", ".gitignore",
	".idea", ".venv","_Criar_Exec.py", ""
, "", "", ""
}

print("📁 ARQUIVOS E PASTAS NA RAIZ (FILTRADOS):")
print("=" * 70)

# Lista e filtra
itens_para_incluir = []
for item in root_dir.iterdir():
	if item.name in itens_para_ignorar:
		#print(f"🚫 IGNORADO: {item.name}")
		continue

	if item.is_file():
		emoji = "📄"
		tipo = "ARQUIVO"
	else:
		emoji = "📁"
		tipo = "PASTA"

	print(f"{emoji} {item.name} ({tipo})")
	itens_para_incluir.append(item)

print("\n" + "=" * 70)
print("🚀 COMANDO FINAL (SÓ ITENS INCLUÍDOS) ✅ AGORA ESTÁ CERTO! Copie e cole!:")
print()

cmd_parts = [
	'streamlit-desktop-app build APP_.py',
	'--name Stream_IDE',
	'--streamlit-options --theme.base=dark',
	'--pyinstaller-options --onedir --noconsole --noconfirm'
]

# GERA COMANDO só com itens filtrados
for item in itens_para_incluir:
	if item.is_file():
		cmd_parts.append(f'--add-data "{item.name};."')
	else:
		cmd_parts.append(f'--add-data "{item.name};{item.name}"')

comando_final = " `\n".join(cmd_parts)
print(comando_final)
