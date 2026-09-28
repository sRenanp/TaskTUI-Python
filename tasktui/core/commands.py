from dataclasses import dataclass
from typing import Any

from .manager import Manager
from .task import Status, Task


@dataclass
class AddTaskCommand:
    manager: Manager
    task: Task

    def execute(self) -> None:
        self.manager._add_task(self.task)


@dataclass
class UpdateTaskCommand:
    manager: Manager
    task_id: str
    updates: dict[str, Any]

    def execute(self) -> None:
        self.manager._update_task(self.task_id, self.updates)


@dataclass
class MarkCompleteCommand:
    manager: Manager
    task_id: str

    def execute(self) -> None:
        self.manager._update_task(self.task_id, {"status": Status.DONE})


@dataclass
class DeleteTaskCommand:
    manager: Manager
    task_id: str

    def execute(self) -> None:
        self.manager._delete_task(self.task_id)
