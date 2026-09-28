import argparse
import sys

from tasktui import config
from tasktui.core import AddTaskCommand, Manager, Task, TaskError
from tasktui.storage import JSONStore


def initialize_app() -> tuple[Manager, config.Config]:
    """Centraliza a criação do manager e do storage para evitar repetição."""
    cfg = config.load()
    store = JSONStore(cfg.data_path)
    return Manager(store), cfg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tasktui", description="Gestor de tarefas com interface TUI e CLI")
    subcommands = parser.add_subparsers(dest="command")
    add_parser = subcommands.add_parser("add", help="Adiciona uma nova tarefa via linha de comando")
    add_parser.add_argument("description", nargs="+", help="descrição da tarefa")
    args = parser.parse_args(argv)

    try:
        manager, cfg = initialize_app()
    except (OSError, ValueError) as error:
        print(f"Erro ao iniciar: {error}")
        return 1

    if args.command == "add":
        description = " ".join(args.description)
        try:
            manager.execute_command(AddTaskCommand(manager, Task(description=description)))
        except TaskError as error:
            print(f"Erro ao adicionar tarefa: {error}")
            return 1
        print(f"✅ Tarefa '{description}' adicionada com sucesso!")
        return 0

    # Sem subcomando: abre a TUI (importada aqui para o "add" não carregar o Textual)
    from tasktui.tui import TaskTUIApp

    TaskTUIApp(manager, theme=cfg.theme).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
