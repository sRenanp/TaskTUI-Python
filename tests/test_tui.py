import tempfile
import unittest
from pathlib import Path

from tasktui.core import AddTaskCommand, Manager, Priority, Status, Task
from tasktui.storage import JSONStore
from tasktui.tui import TaskTUIApp
from tasktui.tui.app import HelpScreen, Mode, Section


class TaskTUIAppTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.manager = Manager(JSONStore(Path(self.tmp.name) / "tasks.json"))
        for description in ("primeira", "segunda"):
            self.manager.execute_command(AddTaskCommand(self.manager, Task(description=description)))
        self.app = TaskTUIApp(self.manager)

    def tearDown(self):
        self.tmp.cleanup()

    def tasks(self):
        return self.manager.get_tasks()

    async def test_navigation_between_tasks_and_panels(self):
        async with self.app.run_test() as pilot:
            await pilot.press("j")
            self.assertEqual(self.app.list_cursor, 1)
            await pilot.press("tab")
            self.assertEqual(self.app.active_section, Section.DETAIL)
            await pilot.press("shift+tab")
            self.assertEqual(self.app.active_section, Section.TASK_LIST)

    async def test_add_task_with_a(self):
        async with self.app.run_test() as pilot:
            await pilot.press("a", *"terceira", "enter")
            self.assertEqual(self.tasks()[-1].description, "terceira")
            self.assertEqual(self.app.mode, Mode.NORMAL)

    async def test_add_task_with_colon_command(self):
        async with self.app.run_test() as pilot:
            await pilot.press(":", *"add quarta", "enter")
            self.assertEqual(self.tasks()[-1].description, "quarta")

    async def test_escape_and_backspace_leave_command_mode(self):
        async with self.app.run_test() as pilot:
            await pilot.press(":", "escape")
            self.assertEqual(self.app.mode, Mode.NORMAL)
            await pilot.press(":", "backspace")
            self.assertEqual(self.app.mode, Mode.NORMAL)

    async def test_delete_task_with_d(self):
        async with self.app.run_test() as pilot:
            await pilot.press("j", "d")
            self.assertEqual([t.description for t in self.tasks()], ["primeira"])
            self.assertEqual(self.app.list_cursor, 0)

    async def test_edit_description(self):
        async with self.app.run_test() as pilot:
            await pilot.press("enter", "enter", "ctrl+a", "ctrl+k", *"editada", "enter")
            self.assertEqual(self.tasks()[0].description, "editada")
            self.assertEqual(self.app.mode, Mode.NORMAL)

    async def test_change_status_and_priority(self):
        async with self.app.run_test() as pilot:
            await pilot.press("enter", "j", "enter", "2")
            self.assertEqual(self.tasks()[0].status, Status.IN_PROGRESS)
            await pilot.press("j", "enter", "3")
            self.assertEqual(self.tasks()[0].priority, Priority.HIGH)

    async def test_help_screen_and_quit(self):
        async with self.app.run_test() as pilot:
            await pilot.press("?")
            self.assertIsInstance(self.app.screen, HelpScreen)
            await pilot.press("q")
            self.assertNotIsInstance(self.app.screen, HelpScreen)
            await pilot.press("q")
            self.assertFalse(self.app.is_running)


if __name__ == "__main__":
    unittest.main()
