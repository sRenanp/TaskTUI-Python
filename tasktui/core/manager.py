import uuid
from datetime import datetime
from typing import Any, Protocol

from .storage import StorageStrategy
from .task import Task

UPDATABLE_FIELDS = {"description", "status", "priority", "end_date", "tags"}


class TaskError(Exception):
    """Erro de regra de negócio (tarefa não encontrada, descrição vazia...)."""


class Observer(Protocol):
    """Interface para notificar a TUI sobre mudanças (padrão Observer)."""

    def on_update(self, tasks: list[Task]) -> None: ...


class Command(Protocol):
    """Interface para todas as ações do sistema (padrão Command)."""

    def execute(self) -> None: ...


class Manager:
    def __init__(self, storage: StorageStrategy):
        self._storage = storage
        self._tasks = storage.load_tasks()
        self._observers: list[Observer] = []

    def execute_command(self, command: Command) -> None:
        command.execute()

    # ============ AÇÕES (usadas pelos comandos) ============

    def _add_task(self, task: Task) -> None:
        if not task.description.strip():
            raise TaskError("descrição vazia")

        # Se não tiver ID, gera um novo
        if not task.id:
            task.id = str(uuid.uuid4())

        now = _now()
        task.created_at = now
        task.updated_at = now

        self._tasks.append(task)
        self._notify()

    def _update_task(self, task_id: str, updates: dict[str, Any]) -> None:
        unknown = updates.keys() - UPDATABLE_FIELDS
        if unknown:
            raise TaskError(f"campos inválidos: {', '.join(sorted(unknown))}")
        if "description" in updates and not updates["description"].strip():
            raise TaskError("descrição vazia")

        task = self._require_task(task_id)
        for name, value in updates.items():
            setattr(task, name, value)
        task.updated_at = _now()
        self._notify()

    def _delete_task(self, task_id: str) -> None:
        self._tasks.remove(self._require_task(task_id))
        self._notify()

    # ============ MÉTODOS DE CONSULTA ============

    def get_tasks(self) -> list[Task]:
        return list(self._tasks)

    def find_task(self, task_id: str) -> Task | None:
        return next((t for t in self._tasks if t.id == task_id), None)

    def _require_task(self, task_id: str) -> Task:
        task = self.find_task(task_id)
        if task is None:
            raise TaskError("tarefa não encontrada")
        return task

    # ============ OBSERVER ============

    def register_observer(self, observer: Observer) -> None:
        self._observers.append(observer)

    def _notify(self) -> None:
        self._storage.save_tasks(self._tasks)
        for observer in self._observers:
            observer.on_update(self.get_tasks())


def _now() -> datetime:
    return datetime.now().astimezone()
