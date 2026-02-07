![Assista o vídeo](https://raw.githubusercontent.com/TopCodeBuyTrap/stream-ide/refs/heads/main/.arquivos/logo_.png)([PRIMEIRO VIDEO](https://www.youtube.com/watch?v=w04XjMlDvGA&t=7s))

# 🛡️ Stream-IDE v0.2.6 `{TcbT}`

**Uma IDE Python mais em Streamlit!**

![Streamlit](https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png)
![Python](https://www.python.org/static/community_logos/python-logo.png)
![Windows](https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg)
[![YouTube](https://img.shields.io/badge/YouTube-Canal-red?logo=youtube&logoColor=white)](https://www.youtube.com/channel/UCioh95X0Kx-ttmBSW7rD3xQ)


---

## ✨ O que tem dentro

### Núcleo da IDE

| EDITOR                         | EXPLORER                         | TERMINAL                          | PROJETOS                          |
|-------------------------------|----------------------------------|-----------------------------------|-----------------------------------|
| Ace Editor (27+ temas)        | Navegador de arquivos/pastas     | PowerShell multi-abas             | Criação de projetos Python        |
| Autosave em camadas           | Sincronização com filesystem     | Execução silenciosa no Windows    | VENV automático por projeto       |
| Análise AST em tempo real     | Detecção de linguagem            | Integração total com VENV         | Histórico de projetos             |
| Score e métricas de código    | Checkbox e seleção múltipla      | Histórico de comandos e saída     | Persistência em SQLite            |
| Snippets e atalhos            | Preview de arquivos e mídia      | Kill por PID ou porta             | Backup automático                 |

---

### Sistema e Infra

| CUSTOM                                   | BANCO DE DADOS            | DESKTOP / BUILD              |
|-----------------------------------------|---------------------------|------------------------------|
| Temas, cores, fontes e layout            | SQLite (múltiplas tabelas)| PyInstaller (.exe ~60MB)     |
| Perfis de customização persistentes      | Estado global da IDE      | Aplicação 100% offline      |
| CSS dinâmico gerado em runtime           | Histórico e cache local   | Windows 10 / 11              |
| Interface totalmente configurável        | Terminal e projetos       | Streamlit Desktop App        |


---

## 🧩 Sobre o projeto

O **Stream IDE** é uma IDE / Editor de código completo feito em **Streamlit**.
Ele roda direto no computador **sem navegador** e permite criar, editar e
executar projetos Python de forma prática.

Todo o estado da IDE é persistido em **SQLite**, garantindo que:

* Configurações globais do sistema sejam salvas
* Histórico de projetos e arquivos recentes seja mantido
* Projeto ativo seja sempre identificado
* Arquivos abertos possam ser restaurados
* Perfil de interface carregue temas, cores, fontes e layout

## Arquitetura de Módulos

A Stream-IDE é organizada de forma modular, separando interface, execução,
infraestrutura, persistência e funcionalidades avançadas.

### Núcleo da Aplicação

* `APP_.py`  
  Aplicação principal da IDE. Gerencia layout, menus, sidebar, editor,
  terminal, preview, backup e fluxo geral da aplicação.

* `Abertura_TCBT.py`  
  Tela inicial de configuração absoluta da IDE. Define diretórios globais,
  projetos, backups, VENV e credenciais.

---

### Editor e Execução

* `APP_Editor_Run_Preview.py`  
  Editor multi-aba com execução de código, preview em tempo real, detecção de
  dependências, controle de threads e subprocess.

* `APP_Editor_Codigo.py`  
  Editor Ace avançado com autosave, análise AST, métricas de qualidade,
  anotações e marcadores visuais.

* `APP_Preview.py`  
  Sistema de preview de execução em tempo real com suporte a entrada
  interativa e streaming de saída.

* `SUB_Run_servidores.py`  
  Gerenciador de execução para Streamlit, Flask e Django, com controle de
  portas, PID e subprocess no Windows.

---

### Terminal

* `APP_Terminal.py`  
  Terminal integrado multi-aba com execução silenciosa, integração com VENV,
  controle de processos e histórico de comandos.

* `Banco_Dados_sudo_pip.py`  
  Banco SQLite dedicado ao terminal para comandos pip, módulos pré-definidos
  e aprendizado automático de comandos.

---

### IA e Catalogação

* `APP_Api_IAs.py`  
  Interface de IA integrada via OpenRouter para análise, geração,
  refatoração e documentação de código.

* `APP_Catalogo.py`  
  Sistema de catalogação automática de código com IA, persistência em JSON,
  exportação e backup.

---

### Navegação e Interface

* `APP_Sidebar.py`  
  Sidebar de navegação com árvore de arquivos, seleção por checkbox e
  sincronização com o filesystem.

* `APP_Menus.py`  
  Menus principais da IDE, criação de projetos, arquivos, pastas,
  customização visual e templates.

* `APP_Json.py`  
  Explorer visual para análise de JSON e respostas de API, com geração
  automática de código Python.

---

### Sistema e Infraestrutura

* `APP_SUB_Controle_Driretorios.py`  
  Controle centralizado de diretórios absolutos, projeto ativo e ambiente
  virtual (.virto_stream).

* `APP_SUB_Janela_Explorer.py`  
  Explorer visual de arquivos e pastas com navegação recursiva, busca,
  criação e preview de mídia.

* `APP_SUB_Funcitons.py`  
  Funções utilitárias gerais: criação de arquivos, análise de estrutura,
  sincronização, cache, UI helpers e subprocess.

* `APP_SUB_Backup.py`  
  Sistema de backup automático por tempo, com histórico diário e exclusões
  inteligentes.

---

### Atualização e Temas

* `APP_Atualizador.py`  
  Sistema de verificação e atualização automática via GitHub, com
  preservação de certificados e arquivos críticos.

* `APP_Htmls.py`  
  Sistema de temas e customização visual. Geração dinâmica de CSS,
  carregamento de fontes, cores, imagens e layout da IDE.

---

### Persistência de Dados

* `Banco_dados.py`  
  Banco SQLite central da IDE. Armazena configurações globais, projetos,
  arquivos abertos, histórico e customizações.

* `Banco_Predefinitions.py`  
  Banco SQLite de pré-definições, templates de projetos, versões instaladas,
  layout da interface e controle temporal de backups.


---

## 📦 Como usar

---

## 🛠️ INSTALL / BUILD

### 1️⃣ Executável (fácil)

* Baixe `TcbT-Stream-IDE-v0.0.1.exe`
* Clique duas vezes
* IDE pronta para uso

### 2️⃣ Desenvolvimento

````bash
# Atualiza pip, setuptools e wheel
python.exe -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# Streamlit Desktop App (empacotamento)
pip install streamlit-desktop-app==0.3.3
# https://github.com/ohtaman/streamlit-desktop-app

# Editor Ace
pip install streamlit_ace==0.1.1
# https://share.streamlit.io/okld/streamlit-gallery/main?p=ace-editor

# Rodar em modo desenvolvimento
streamlit run APP_.py

# Criar executável
streamlit-desktop-app build APP_.py \
  --name Stream_IDE \
  --streamlit-options --theme.base=dark \
  --pyinstaller-options \
    --onedir --noconsole --noconfirm
```bash
git clone https://github.com/TopCodeBuyTrap/stream-ide
````

---

## 💡 Por que este projeto existe

Na real, eu fiz este projeto porque eu precisava de uma IDE só pra mim.

O PyCharm estava me dando muito problema: terminal bugado, lentidão,
dificuldade para copiar arquivos, execução lenta e com lag.

Então pensei:
“Vou fazer um editor / IDE que funcione do jeito que eu quero.”

Começou como um editor pessoal.
Depois virei obcecado em entender como funcionava:

* Terminal
* Preview
* Criação de projetos
* Gerenciamento de ambientes virtuais

Chegando em alguns pontos, surgiram lags e limitações que sozinho não consigo
resolver totalmente.

A ideia agora é abrir para colaboração.

Quero que profissionais ou entusiastas ajudem, sugiram melhorias e adicionem
funcionalidades.

Resumo:

* Começou como editor pessoal para Python
* Evoluiu para uma IDE completa em Streamlit
* Agora está aberta para colaboração open source

---

## 🆕 Últimas Implementações (Jan/2026)

**Foco total nas novidades recentes (últimos dias)**

### 📄 Documentação Automática com IA (OpenRouter)

* Gera documentação estruturada de qualquer arquivo aberto
* Funciona com qualquer linguagem
* Formato fixo:

  * Breve descrição do script
  * Imports e módulos
  * Funções e classes em ordem
  * Chamadas e blocos soltos
* Observação do usuário antes do botão (opcional)
* Salva em `.virto_stream/.catalogos.json`
* Exibe imediatamente após gerar
* Botões:

  * Copiar
  * Baixar como `.md`

---

### 📁 Salvar Estrutura Completa do Projeto

* Botão: **Salvar estrutura catalogada**
* Solicita:

  * Pasta destino (ex: `C:\\meus\\projetos`)
  * Nome do projeto (ex: `MeuApp`)
* Cria automaticamente:

  * `C:\\meus\\projetos\\MeuApp\\estrutura_catalogada.md`

O arquivo `.md` contém:

* Todos os arquivos catalogados
* Linguagem
* Data
* Documentação completa

---

### 🔍 Lista de Catálogos Salvos

* Expander: **Ver Catálogos Salvos**
* Exibe tabela com:

  * Nome do arquivo
  * Linguagem
  * Data de geração
  * Total de arquivos catalogados

---

### Outras melhorias recentes

* Suporte total a qualquer linguagem
* Salvamento persistente em pasta oculta `.virto_stream`
* Download direto como Markdown
* Integração OpenRouter

  * Modelo: `arcee-ai/trinity-large-preview:free`

---

## 🔮 Próximos passos sugeridos

* Filtro e pesquisa nos catálogos salvos
* Diagrama de fluxo automático (opcional)
* Exportação ZIP com arquivos + documentação

---

Feito com carinho e raiva.
Henrique (TcbT) – Jan/2026
## 🚀 Executável atual (v0.2.6)

- **Nome:** Stream-IDE.exe  
- **Tamanho:** ~60–80 MB (depende do PyInstaller)  
- **Modo:** 100% offline depois de instalado  
- **Sistema:** Windows 10/11 (testado)  
- **O que roda:** editor, terminal, preview, venv, IA, backup, tudo junto

Não é perfeito. Mas roda. E é minha.

---

## O que já funciona de verdade (não promessa)

- Editor Ace multi-aba com autosave militar  
- Análise estática (AST) + score de código + sugestão de pip  
- Preview em tempo real (Python puro, Streamlit, Flask, Django)  
- Terminal multi-aba que realmente usa o venv do projeto  
- Detecta e mata portas ocupadas (8501, 5000, 8000…)  
- Cria projeto com venv + arquivos iniciais  
- Customização pesada (cores, fontes, gradientes, temas)  
- Backup automático silencioso (ignora .venv, .idea, etc)  
- Atualização automática do GitHub (preserva certifi)  
- IA (OpenRouter) que explica, refatora, gera testes, documenta  
- Catálogo automático de código → salva em JSON + exporta Markdown  
- Sidebar com árvore de arquivos + checkboxes persistentes  
- SQLite em tudo: configs, projetos recentes, arquivos abertos, temas

---

## O que ainda tá uma merda ou pela metade (2026)

- Download de arquivos pela interface → ainda não tem  
- Pré-instalar pacotes ao criar projeto → falta  
- Traduzir saída/erro do terminal pro português → to tentando  
- Git real (commit, push, pull) → só checa update por enquanto  
- Terminal no Windows ainda dá dor de cabeça (encoding, powershell)  
- Executável às vezes reclama de certifi ou paths quebrados

Se liga: não é produto final. É ferramenta que eu uso todo dia e vou consertando na marra.

---

## Como buildar (se quiser fazer você mesmo)

```bash
# Atualiza tudo antes
python -m pip install --upgrade pip setuptools wheel

# Pacotes principais
pip install streamlit streamlit-code-editor streamlit-desktop-app

# Gera o .exe
streamlit-desktop-app build APP_.py ^
  --name Stream_IDE ^
  --streamlit-options --theme.base=dark ^
  --pyinstaller-options ^
    --onedir --noconfirm ^
    --collect-data certifi ^
  --icon icon.ico

