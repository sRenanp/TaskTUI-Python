# TUI Task Manager (Python)

Um gerenciador de tarefas baseado em terminal (TUI) escrito em Python, utilizando o [Textual](https://textual.textualize.io/). O projeto foca em produtividade através de comandos rápidos e uma interface intuitiva diretamente no terminal.

Esta é a versão em Python do [TaskTUI em Go](https://github.com/sRenanp/TaskTUI-Uma-Ferramenta-de-Terminal-para-Gest-o-Integrada-de-Tarefas-e-Calend-rio). O arquivo `tasks.json` é compatível entre as duas, então dá pra usar as duas com os mesmos dados.

## 🚀 Funcionalidades

- **Gerenciamento de Tarefas:** Adicione, edite e remova tarefas com facilidade.
- **Interface TUI:** Construída com [Textual](https://github.com/Textualize/textual) e [Rich](https://github.com/Textualize/rich).
- **Sistema de Comandos:** Suporte a comandos estilo Vim para agilidade.
- **Persistência:** Arquitetura preparada para diferentes estratégias de armazenamento (Storage Strategy).
- **Organização:** Prioridades, status (A Fazer, Em Andamento, Concluído) e tags.

## 🛠️ Tecnologias

- **Python 3.11+**
- [Textual](https://github.com/Textualize/textual): Framework TUI.
- [Rich](https://github.com/Textualize/rich): Estilização do texto no terminal.

## 📂 Estrutura do Projeto

- `tasktui/core`: Lógica de negócio, modelo `Task` e padrões de design como Command, Observer e Strategy.
- `tasktui/storage`: Persistência em JSON.
- `tasktui/tui`: Implementação da interface, modos (Normal, Insert, Command) e renderização.
- `tests`: Testes do core e da TUI.

## ⌨️ Atalhos e Comandos

### Navegação

- `tab` / `shift+tab`: Alternar entre painéis.
- `j` / `k`: Mover seleção para cima/baixo.
- `enter`: Abrir detalhes ou entrar no modo de edição.
- `esc`: Voltar ao modo normal.

### Ações

- `a`: Adicionar nova tarefa.
- `d`: Deletar tarefa selecionada.
- `:`: Entrar no modo de comando.
- `?`: Mostrar/ocultar ajuda.
- `q`: Sair da aplicação.

### Modo de comando

- `:add <descrição>`: Adicionar tarefa.
- `:delete`: Deletar tarefa atual.
- `:w`: Salvar.
- `:q`: Sair.

## 🏗️ Como Executar

1. Certifique-se de ter o Python 3.11 ou superior instalado.
2. Clone o repositório e instale as dependências:
   ```bash
   git clone https://github.com/sRenanp/TaskTUI-Python.git
   cd TaskTUI-Python
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```
3. Abra a TUI:
   ```bash
   python -m tasktui
   ```

Também dá pra adicionar tarefa direto pela linha de comando:

```bash
python -m tasktui add Estudar para a prova
```

Para rodar os testes:

```bash
python -m unittest discover -s tests
```

## ⚙️ Configuração

A configuração fica no `config.toml`:

```toml
data_path = "data/tasks.json"
theme = "dark"  # "dark" ou "light"
```
