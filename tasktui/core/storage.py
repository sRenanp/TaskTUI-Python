from typing import Protocol

from .task import Task


class StorageStrategy(Protocol):
    """Define o contrato para persistência de tarefas (padrão Strategy)."""

    def load_tasks(self) -> list[Task]: ...

    def save_tasks(self, tasks: list[Task]) -> None: ...
