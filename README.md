# TUI Task Manager (Python)

Versão em Python do TaskTUI, usando o [Textual](https://textual.textualize.io/) no lugar do Bubble Tea. A lógica é a mesma da versão em Go: padrões Command, Observer e Strategy, os modos Normal/Insert/Command e os atalhos estilo Vim.

O arquivo `tasks.json` é compatível com a versão em Go, então dá pra usar as duas com os mesmos dados.

## 🛠️ Tecnologias

- **Python 3.11+**
- [Textual](https://github.com/Textualize/textual): Framework TUI.
- [Rich](https://github.com/Textualize/rich): Estilização do texto no terminal.

## 📂 Estrutura do Projeto

- `tasktui/core`: Modelo `Task`, `Manager` e os comandos.
- `tasktui/storage`: Persistência em JSON.
- `tasktui/tui`: Interface, modos e renderização.
- `tests`: Testes do core e da TUI.

## 🏗️ Como Executar

```bash
cd python
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

Abrir a TUI:

```bash
python -m tasktui
```

Adicionar tarefa direto pela linha de comando:

```bash
python -m tasktui add Estudar para a prova
```

Rodar os testes:

```bash
python -m unittest discover -s tests
```

## ⚙️ Configuração

A configuração fica no `config.toml` (na versão em Go é o `config.lua`):

```toml
data_path = "data/tasks.json"
theme = "dark"
```

Os atalhos são os mesmos da versão em Go, veja o [README principal](../README.md).
