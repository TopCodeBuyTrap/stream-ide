# 🛡️ Stream-IDE v0.0.9 `{TcbT}`

**Uma IDE Python mais em Streamlit!**

![Streamlit](https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png)
![Python](https://www.python.org/static/community_logos/python-logo.png)
![Windows](https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg)

---

## 🚀 Executável 60MB (Download)

* **Arquivo:** Stream-IDE-v0.0.1.exe
* **Tamanho:** 60MB
* **Modo:** 100% OFFLINE
* **Sistema:** Windows 10 / 11
* **Inclui:** Editor Ace + Terminal + Projetos

---

## ✨ O que tem dentro

### Núcleo da IDE

| EDITOR         | EXPLORER             | TERMINAL              | PROJETOS              |
| -------------- | -------------------- | --------------------- | --------------------- |
| Ace (27 temas) | Navegador de pastas  | PowerShell multi-abas | Venv automático       |
| Análise AST    | Sync JSON            | Histórico de saída    | Histórico de projetos |
| Score código   | Checkbox de arquivos | Detecta venv          | SQLite integrado      |

### Sistema e Infra

| CUSTOM                          | BANCO            | DESKTOP                 |
| ------------------------------- | ---------------- | ----------------------- |
| 20+ variáveis de personalização | 5 tabelas SQLite | PyInstaller (.exe 60MB) |
| Multi-user                      | Persistente      | Rodando offline         |

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

### Arquitetura de módulos

* `APP_Editor_Run_Preview.py`
  Editor principal e execução de código

* `APP_Terminal.py`
  Terminal integrado com múltiplas abas

* `Banco_dados.py`
  Persistência e controle SQLite

* `APP_SUB_Funcitons.py`
  Funções auxiliares do editor

* `APP_SUB_Janela_Explorer.py`
  Gerenciamento de arquivos e abas

* `APP_SUB_Controle_Driretorios.py`
  Controle de diretórios e projeto ativo

---

## 📦 Como usar

### 1️⃣ Executável (fácil)

* Baixe `TcbT-Stream-IDE-v0.0.1.exe`
* Clique duas vezes
* IDE pronta para uso

### 2️⃣ Desenvolvimento

```bash
git clone https://github.com/TopCodeBuyTrap/stream-ide
```

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
