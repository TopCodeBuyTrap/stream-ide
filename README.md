# 🛡️ Stream-IDE v0.0.1 `{TcbT}
**Uma IDE Python mais em Streamlit!** 🎮

[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-blue)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org) 
[![Windows](https://img.shields.io/badge/Windows-10/11-blue)](https://microsoft.com)

---

## 🚀 Executável 60MB (Download)

💾 Stream-IDE-v0.0.1.exe  
📦 60MB - 100% OFFLINE  
🖥️ Windows 10/11  
⚡ Editor Ace + Terminal + Projetos

---

## ✨ O que tem dentro

| **EDITOR** | **EXPLORER** | **TERMINAL** | **PROJETOS** |
|------------|--------------|--------------|--------------|
| Ace 27 temas | Navegador de pastas | PowerShell multi-abas | Venv automático |
| Análise AST | Sync JSON | Histórico de saída | Histórico de projetos |
| Score de código | Checkbox de arquivos | Detecta venv | Banco SQLite integrado |

| **CUSTOM** | **BANCO** | **DESKTOP** |
|------------|-----------|-------------|
| 20+ variáveis de personalização | 5 tabelas SQLite | PyInstaller .exe 60MB |
| Multi-user | Persistente | Rodando offline |

---

## 🧩 Sobre o projeto

O ** Stream IDE** é uma IDE/Editor de código completo feito em **Streamlit**. Ele roda direto no computador sem usar navegador e permite criar, editar e executar projetos Python de forma prática. Todo o estado da IDE é persistido em **SQLite**, garantindo que:

- As configurações globais do sistema sejam salvas.  
- O histórico de projetos e arquivos recentes seja mantido.  
- O projeto ativo seja sempre identificado.  
- Os arquivos abertos possam ser acessados novamente sem depender do sistema de arquivos.  
- O perfil de interface do usuário seja carregado com temas, cores, fontes e layout.

Arquiteturalmente, ele está separado em módulos:

- `APP_Editor_Run_Preview.py` → Editor principal, execução de código.  
- `APP_Terminal.py` → Terminal multi-abas integrado.  
- `Banco_dados.py` → Funções SQLite para persistência.  
- `APP_SUB_Funcitons.py` → Funções auxiliares de editor.  
- `APP_SUB_Janela_Explorer.py` → Abrir arquivos e gerenciar abas.  
- `APP_SUB_Controle_Driretorios.py` → Gerencia diretórios e projeto ativo.

---

## 📦 Como usar

### 1️⃣ Executável (FÁCIL)
↓ Baixe `TcbT-Stream-IDE-v0.0.1.exe`  
→ Clique 2x  
→ IDE PROFISSIONAL pronta para uso!

### 2️⃣ Desenvolvimento
```bash
git clone https://github.com/TopCodeBuyTrap/stream-ide

#cd stream-ide
pip install -r requirements.txt
streamlit run APP_Editor_Run_Preview.py


💡 Por que este projeto existe

Na real, eu fiz este projeto porque eu precisava de uma IDE só pra mim.
O PyCharm estava me dando muito problema: o terminal não aparecia direito, estava lento, não fazia cópia de arquivos, executava devagar e com lag. Então eu pensei: “vou fazer um editor/IDE só pra mim que funcione do jeito que eu quero.”

Comecei com a ideia de um editor pessoal, mas fui gostando do processo: entender como funcionava o terminal, o preview, como criar projetos e gerenciar ambientes virtuais. Mas, chegando em alguns pontos, comecei a enfrentar lags e problemas que sozinho não consigo resolver totalmente.

Então, a ideia agora é abrir para colaboração. Quero que outras pessoas profissionais ou entusiastas possam ajudar, melhorar o código, sugerir ideias, adicionar funcionalidades.
Se você se interessar, pode entrar em contato comigo na descrição do projeto, e a gente pode fazer isso crescer juntos como open source.

Basicamente:
Começou como um editor pessoal para Python.
Evoluiu para uma IDE completa em Streamlit.
Agora está aberto para colaboração e melhorias.
