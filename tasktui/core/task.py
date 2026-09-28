from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Status(IntEnum):
    TODO = 0
    IN_PROGRESS = 1
    DONE = 2


@dataclass
class Task:
    description: str
    id: str = ""
    priority: Priority = Priority.LOW
    status: Status = Status.TODO
    created_at: datetime | None = None
    updated_at: datetime | None = None
    start_date: datetime | None = None  # Para o Calendário
    end_date: datetime | None = None  # Para o Calendário
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": int(self.priority),
            "status": int(self.status),
            "created_at": _format_date(self.created_at),
            "updated_at": _format_date(self.updated_at),
            "start_date": _format_date(self.start_date),
            "end_date": _format_date(self.end_date),
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            priority=Priority(data.get("priority", Priority.LOW)),
            status=Status(data.get("status", Status.TODO)),
            created_at=_parse_date(data.get("created_at")),
            updated_at=_parse_date(data.get("updated_at")),
            start_date=_parse_date(data.get("start_date")),
            end_date=_parse_date(data.get("end_date")),
            tags=data.get("tags") or [],
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    date = datetime.fromisoformat(value)
    # A versão em Go grava "0001-01-01T00:00:00Z" quando a data não existe
    if date.year == 1:
        return None
    return date


def _format_date(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
