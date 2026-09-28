import json
import tempfile
import unittest
from pathlib import Path

from tasktui import config
from tasktui.core import (
    AddTaskCommand,
    DeleteTaskCommand,
    Manager,
    MarkCompleteCommand,
    Priority,
    Status,
    Task,
    TaskError,
    UpdateTaskCommand,
)
from tasktui.storage import JSONStore

GO_TASKS_JSON = """[
  {
    "id": "2cb2a5ac-2a57-4357-ab33-cac65914f450",
    "description": "fazer trabalho",
    "priority": 1,
    "status": 0,
    "created_at": "2026-03-19T13:25:56.4016785-03:00",
    "updated_at": "2026-03-19T16:04:12.8159351-03:00",
    "start_date": "0001-01-01T00:00:00Z",
    "end_date": "0001-01-01T00:00:00Z",
    "tags": null
  }
]"""


class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "data" / "tasks.json"
        self.manager = Manager(JSONStore(self.path))

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, description):
        task = Task(description=description)
        self.manager.execute_command(AddTaskCommand(self.manager, task))
        return task

    def test_add_generates_id_and_dates_and_saves(self):
        task = self.add("estudar python")
        self.assertTrue(task.id)
        self.assertIsNotNone(task.created_at)
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved[0]["description"], "estudar python")

    def test_add_rejects_empty_description(self):
        with self.assertRaises(TaskError):
            self.add("   ")

    def test_update_status_priority_and_description(self):
        task = self.add("antiga")
        self.manager.execute_command(
            UpdateTaskCommand(
                self.manager,
                task.id,
                {"status": Status.IN_PROGRESS, "priority": Priority.HIGH, "description": "nova"},
            )
        )
        reloaded = Manager(JSONStore(self.path)).get_tasks()[0]
        self.assertEqual(reloaded.status, Status.IN_PROGRESS)
        self.assertEqual(reloaded.priority, Priority.HIGH)
        self.assertEqual(reloaded.description, "nova")

    def test_update_rejects_unknown_field(self):
        task = self.add("x")
        with self.assertRaises(TaskError):
            self.manager.execute_command(UpdateTaskCommand(self.manager, task.id, {"id": "outro"}))

    def test_mark_complete_and_delete(self):
        task = self.add("x")
        self.manager.execute_command(MarkCompleteCommand(self.manager, task.id))
        self.assertEqual(task.status, Status.DONE)
        self.manager.execute_command(DeleteTaskCommand(self.manager, task.id))
        self.assertEqual(self.manager.get_tasks(), [])
        with self.assertRaises(TaskError):
            self.manager.execute_command(DeleteTaskCommand(self.manager, task.id))

    def test_observer_is_notified(self):
        received = []

        class Spy:
            def on_update(self, tasks):
                received.append(len(tasks))

        self.manager.register_observer(Spy())
        self.add("a")
        self.add("b")
        self.assertEqual(received, [1, 2])


class JSONStoreTest(unittest.TestCase):
    def test_reads_file_written_by_go_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            path.write_text(GO_TASKS_JSON, encoding="utf-8")
            task = JSONStore(path).load_tasks()[0]
        self.assertEqual(task.description, "fazer trabalho")
        self.assertEqual(task.priority, Priority.MEDIUM)
        self.assertIsNone(task.end_date)
        self.assertEqual(task.tags, [])
        self.assertEqual(task.created_at.year, 2026)

    def test_missing_or_empty_file_returns_no_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            self.assertEqual(JSONStore(path).load_tasks(), [])
            path.write_text("", encoding="utf-8")
            self.assertEqual(JSONStore(path).load_tasks(), [])


class ConfigTest(unittest.TestCase):
    def test_defaults_when_file_is_missing(self):
        cfg = config.load("nao-existe.toml")
        self.assertEqual(cfg.data_path, "data/tasks.json")
        self.assertEqual(cfg.theme, "dark")

    def test_values_from_toml(self):
        cfg = config.load_from_string('data_path = "outro/tasks.json"\ntheme = "light"')
        self.assertEqual(cfg.data_path, "outro/tasks.json")
        self.assertEqual(cfg.theme, "light")


if __name__ == "__main__":
    unittest.main()
