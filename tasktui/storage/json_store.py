import json
from pathlib import Path

from tasktui.core import Task


class JSONStore:
    def __init__(self, path: str | Path):
        self.file_path = Path(path).resolve()

    def load_tasks(self) -> list[Task]:
        if not self.file_path.exists():
            return []

        text = self.file_path.read_text(encoding="utf-8")
        if not text.strip():
            return []

        # "or []" cobre o arquivo contendo "null"
        return [Task.from_dict(item) for item in json.loads(text) or []]

    def save_tasks(self, tasks: list[Task]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # indent facilita a leitura humana se o usuário quiser editar o JSON manualmente
        data = json.dumps([t.to_dict() for t in tasks], indent=2, ensure_ascii=False)
        self.file_path.write_text(data, encoding="utf-8")
