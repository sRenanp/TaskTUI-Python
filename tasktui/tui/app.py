from enum import Enum, IntEnum

from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Input, Static

from tasktui.core import (
    AddTaskCommand,
    DeleteTaskCommand,
    Manager,
    Priority,
    Status,
    Task,
    TaskError,
    UpdateTaskCommand,
)


class Mode(Enum):
    NORMAL = "NORMAL"
    COMMAND = "COMMAND"
    INSERT = "INSERT"


class Section(IntEnum):
    TASK_LIST = 0
    DETAIL = 1


class Field(IntEnum):
    DESCRIPTION = 0
    STATUS = 1
    PRIORITY = 2


STATUS_LABELS = {Status.TODO: "A Fazer", Status.IN_PROGRESS: "Em Andamento", Status.DONE: "Concluído"}
STATUS_SYMBOLS = {Status.TODO: "○", Status.IN_PROGRESS: "◔", Status.DONE: "●"}
PRIORITY_LABELS = {Priority.LOW: "Baixa", Priority.MEDIUM: "Média", Priority.HIGH: "Alta"}
PRIORITY_COLORS = {Priority.LOW: "grey62", Priority.MEDIUM: "orange1", Priority.HIGH: "red"}
SECTION_LABELS = {Section.TASK_LIST: "Lista", Section.DETAIL: "Detalhes"}

# Teclas 1, 2 e 3 no modo insert, na ordem das opções mostradas
STATUS_KEYS = dict(zip("123", Status))
PRIORITY_KEYS = dict(zip("123", Priority))

MESSAGE_SECONDS = 2

HELP_TEXT = """\
📖 AJUDA - TASK-TUI

NAVEGAÇÃO:
  tab/shift+tab  - Alternar entre painéis
  j/k            - Mover para cima/baixo
  enter          - Abrir detalhes / entrar em modo insert
  esc            - Voltar ao modo normal

AÇÕES:
  a              - Adicionar nova tarefa
  d              - Deletar tarefa atual
  :              - Modo comando
  ?              - Mostrar/ocultar esta ajuda
  q              - Sair

COMANDOS:
  :q             - Sair
  :w             - Salvar
  :add <desc>    - Adicionar tarefa
  :delete        - Deletar tarefa atual

Pressione 'q' ou ESC para voltar"""


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("q", "dismiss", "Voltar"),
        Binding("escape", "dismiss", "Voltar"),
        Binding("question_mark", "dismiss", "Voltar"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(HELP_TEXT, id="help")


class TaskTUIApp(App):
    CSS = """
    #title {
        background: $boost;
        color: $accent;
        text-style: bold;
        padding: 0 2;
        margin-bottom: 1;
    }
    #panels { height: 1fr; }
    .panel {
        width: 1fr;
        height: 1fr;
        border: round $primary;
        padding: 0 1;
    }
    .panel.active { border: double $accent; }
    #detail-panel { margin-left: 2; }
    #editor, #command { display: none; }
    #status, #message { height: 1; }
    #message { color: $success; }
    #message.error { color: $error; }
    HelpScreen { align: center middle; }
    #help {
        width: 60;
        height: auto;
        border: round $secondary;
        padding: 1 2;
    }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Sair", priority=True)]

    # Sem foco automático: no modo normal as teclas vão para o app, não para os campos de texto
    AUTO_FOCUS = None

    def __init__(self, manager: Manager, theme: str = "dark"):
        super().__init__()
        self.manager = manager
        self.theme_name = theme
        self.mode = Mode.NORMAL
        self.active_section = Section.TASK_LIST
        self.list_cursor = 0
        self.field_cursor = Field.DESCRIPTION
        self._message_timer: Timer | None = None
        manager.register_observer(self)

    def compose(self) -> ComposeResult:
        yield Static("📅 TASK-TUI - GESTÃO INTEGRADA", id="title")
        with Horizontal(id="panels"):
            yield Static(id="task-list", classes="panel")
            with Vertical(id="detail-panel", classes="panel"):
                yield Static(id="detail")
                yield Input(placeholder="Nova descrição...", max_length=50, id="editor")
        yield Input(id="command", select_on_focus=False)
        yield Static(id="status")
        yield Static(id="message")

    def on_mount(self) -> None:
        self.theme = "textual-light" if self.theme_name == "light" else "textual-dark"
        # A altura dos painéis só é conhecida depois do primeiro layout
        self.call_after_refresh(self.refresh_view)

    def on_resize(self) -> None:
        self.refresh_view()

    # ============ OBSERVER ============

    def on_update(self, tasks: list[Task]) -> None:
        # Atualiza quando o manager notificar mudanças
        self.list_cursor = min(self.list_cursor, max(0, len(tasks) - 1))
        self.refresh_view()

    # ============ TECLADO ============

    def on_key(self, event: events.Key) -> None:
        if isinstance(self.screen, HelpScreen):
            return

        if self.mode is Mode.NORMAL:
            handled = self.handle_normal_key(event)
        elif self.mode is Mode.INSERT:
            handled = self.handle_insert_key(event)
        else:
            handled = self.handle_command_key(event)

        if handled:
            event.stop()
            event.prevent_default()
            self.refresh_view()

    def handle_normal_key(self, event: events.Key) -> bool:
        key = event.key

        if key in ("tab", "shift+tab", "ctrl+l", "ctrl+h"):
            self.active_section = Section(1 - self.active_section)
            self.field_cursor = Field.DESCRIPTION
        elif key in ("j", "down"):
            self.move_cursor(+1)
        elif key in ("k", "up"):
            self.move_cursor(-1)
        elif key == "enter":
            self.handle_enter()
        elif key == "d" and self.active_section is Section.TASK_LIST:
            self.delete_current_task()
        elif key == "a":
            self.enter_command_mode(":add ")
        elif event.character == ":":
            self.enter_command_mode(":")
        elif event.character == "?":
            self.push_screen(HelpScreen())
        elif key == "q":
            self.exit()
        else:
            return False
        return True

    def handle_enter(self) -> None:
        if self.active_section is Section.TASK_LIST:
            if self.current_task():
                self.active_section = Section.DETAIL
                self.field_cursor = Field.DESCRIPTION
            return

        task = self.current_task()
        if task is None:
            return
        self.mode = Mode.INSERT
        if self.field_cursor is Field.DESCRIPTION:
            editor = self.query_one("#editor", Input)
            editor.value = task.description
            editor.display = True
            editor.focus()

    def handle_insert_key(self, event: events.Key) -> bool:
        if event.key == "escape":
            self.leave_insert_mode()
            return True

        # Na descrição quem cuida das teclas é o Input (enter chega em on_input_submitted)
        if self.field_cursor is Field.DESCRIPTION:
            return False

        task = self.current_task()
        if self.field_cursor is Field.STATUS and event.key in STATUS_KEYS:
            self.update_current_task({"status": STATUS_KEYS[event.key]}, task)
        elif self.field_cursor is Field.PRIORITY and event.key in PRIORITY_KEYS:
            self.update_current_task({"priority": PRIORITY_KEYS[event.key]}, task)
        else:
            return False
        self.leave_insert_mode()
        return True

    def handle_command_key(self, event: events.Key) -> bool:
        if event.key == "escape":
            self.leave_command_mode()
            return True
        return False

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "editor":
            task = self.current_task()
            if task is not None:
                self.update_current_task({"description": event.value}, task)
            self.leave_insert_mode()
        else:
            self.execute_command(event.value.strip())
        self.refresh_view()

    def on_input_changed(self, event: Input.Changed) -> None:
        # Apagar o ":" com backspace sai do modo comando, como no Vim
        if event.input.id == "command" and self.mode is Mode.COMMAND and not event.value:
            self.leave_command_mode()
            self.refresh_view()

    # ============ MODOS ============

    def enter_command_mode(self, initial: str) -> None:
        self.mode = Mode.COMMAND
        command = self.query_one("#command", Input)
        command.value = initial
        command.display = True
        command.focus()
        command.cursor_position = len(initial)

    def leave_command_mode(self) -> None:
        self.mode = Mode.NORMAL
        command = self.query_one("#command", Input)
        command.display = False
        command.value = ""
        self.set_focus(None)

    def leave_insert_mode(self) -> None:
        self.mode = Mode.NORMAL
        self.query_one("#editor", Input).display = False
        self.set_focus(None)

    def execute_command(self, command: str) -> None:
        self.leave_command_mode()

        if command == ":q":
            self.exit()
        elif command == ":w":
            # As tarefas já são salvas a cada alteração
            self.show_message("Salvo com sucesso")
        elif command.startswith(":add "):
            self.add_task(command.removeprefix(":add ").strip())
        elif command == ":delete":
            self.delete_current_task()
        elif command != ":":
            self.show_message(f"Erro: comando desconhecido '{command}'")

    # ============ AÇÕES ============

    def current_task(self) -> Task | None:
        tasks = self.manager.get_tasks()
        if 0 <= self.list_cursor < len(tasks):
            return tasks[self.list_cursor]
        return None

    def move_cursor(self, step: int) -> None:
        if self.active_section is Section.TASK_LIST:
            last = max(0, len(self.manager.get_tasks()) - 1)
            self.list_cursor = min(max(self.list_cursor + step, 0), last)
        else:
            self.field_cursor = Field(min(max(self.field_cursor + step, 0), len(Field) - 1))

    def add_task(self, description: str) -> None:
        try:
            self.manager.execute_command(AddTaskCommand(self.manager, Task(description=description)))
        except TaskError as error:
            self.show_message(f"Erro: {error}")
        else:
            self.show_message("Tarefa adicionada")

    def update_current_task(self, updates: dict, task: Task | None) -> None:
        if task is None:
            return
        try:
            self.manager.execute_command(UpdateTaskCommand(self.manager, task.id, updates))
        except TaskError as error:
            self.show_message(f"Erro: {error}")

    def delete_current_task(self) -> None:
        task = self.current_task()
        if task is None:
            return
        try:
            self.manager.execute_command(DeleteTaskCommand(self.manager, task.id))
        except TaskError as error:
            self.show_message(f"Erro ao deletar: {error}")
        else:
            self.show_message("Tarefa deletada")

    def show_message(self, message: str) -> None:
        widget = self.query_one("#message", Static)
        widget.update(message)
        widget.set_class(message.startswith("Erro"), "error")
        if self._message_timer is not None:
            self._message_timer.stop()
        self._message_timer = self.set_timer(MESSAGE_SECONDS, lambda: widget.update(""))

    # ============ RENDERIZAÇÃO ============

    def refresh_view(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#task-list", Static).set_class(self.active_section is Section.TASK_LIST, "active")
        self.query_one("#detail-panel").set_class(self.active_section is Section.DETAIL, "active")
        self.query_one("#task-list", Static).update(self.render_task_list())
        self.query_one("#detail", Static).update(self.render_task_detail())
        status = self.query_one("#status", Static)
        status.display = self.mode is not Mode.COMMAND
        status.update(self.render_status_bar())

    def render_task_list(self) -> Text:
        tasks = self.manager.get_tasks()
        if not tasks:
            return Text(" Nenhuma tarefa encontrada.\n\n Pressione 'a' para adicionar.")

        # Rolagem: mostra só as tarefas que cabem no painel, mantendo o cursor visível
        visible = max(1, self.query_one("#task-list").content_size.height)
        start = max(0, self.list_cursor - visible + 1)

        lines = Text(no_wrap=True, overflow="ellipsis")
        for index, task in enumerate(tasks[start : start + visible], start=start):
            if index == self.list_cursor and self.active_section is Section.TASK_LIST:
                lines.append("▶ ", style="bold magenta")
            else:
                lines.append("  ")
            lines.append(f"{STATUS_SYMBOLS[task.status]} {task.description} ")
            lines.append("●", style=PRIORITY_COLORS[task.priority])
            lines.append("\n")
        lines.rstrip()
        return lines

    def render_task_detail(self) -> Text:
        task = self.current_task()
        if task is None:
            return Text(" Selecione uma tarefa para ver detalhes")

        text = Text()
        text.append(f" 📝 Tarefa #{task.id[:8]}\n\n")

        editing_description = self.mode is Mode.INSERT and self.field_cursor is Field.DESCRIPTION
        if not editing_description:
            self._append_field(text, Field.DESCRIPTION, f"Descrição: {task.description}")

        self._append_field(text, Field.STATUS, f"Status: {STATUS_LABELS[task.status]}")
        if self.mode is Mode.INSERT and self.field_cursor is Field.STATUS:
            text.append("   [1] A Fazer  [2] Em Andamento  [3] Concluído\n", style="italic")

        self._append_field(text, Field.PRIORITY, f"Prioridade: {PRIORITY_LABELS[task.priority]}")
        if self.mode is Mode.INSERT and self.field_cursor is Field.PRIORITY:
            text.append("   [1] Baixa  [2] Média  [3] Alta\n", style="italic")

        if task.end_date:
            text.append(f"\n 📅 Data: {task.end_date:%d/%m/%Y}\n")

        if self.mode is Mode.INSERT:
            text.append("\n -- INSERT --", style="bold")
        return text

    def _append_field(self, text: Text, field: Field, label: str) -> None:
        if self.active_section is Section.DETAIL and self.field_cursor is field:
            text.append("▶ ", style="bold magenta")
        else:
            text.append("  ")
        text.append(f"{label}\n")

    def render_status_bar(self) -> Text:
        if self.mode is Mode.INSERT:
            help_text = "esc:back  enter:save"
        else:
            help_text = "?:help  tab:next  j/k:move  a:add  q:quit"

        left = Text()
        left.append(f" {self.mode.value} ", style="reverse bold")
        left.append(f"  {help_text}")
        right = Text(f"Seção: {SECTION_LABELS[self.active_section]} ")

        spaces = max(1, self.size.width - left.cell_len - right.cell_len)
        return left + Text(" " * spaces) + right
