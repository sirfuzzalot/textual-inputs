# app.py
from __future__ import annotations

from typing import TYPE_CHECKING

import rich.box
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Header, Static

from textual_inputs import IntegerInput, TextInput

if TYPE_CHECKING:
    from textual.message import Message


class CustomHeader(Header):
    """Override the default Header for Styling"""

    def __init__(self) -> None:
        super().__init__()
        self.tall = False
        self.style = Style(color="white", bgcolor="rgb(98,98,98)")

    def render(self) -> Table:
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.add_column(justify="left", ratio=0, width=8)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right", width=8)
        header_table.add_row(
            "🔤", self.full_title, self.get_clock() if self.clock else ""
        )
        return header_table

    async def on_click(self, event: events.Click) -> None:
        return await super().on_click(event)


class CustomFooter(Footer):
    """Override the default Footer for Styling"""

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style="white on rgb(98,98,98)",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", "reverse" if hovered else "default on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text


class SimpleForm(App):

    current_index: Reactive[int] = Reactive(-1)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.tab_index = ["username", "password", "age", "code"]

    async def on_load(self) -> None:
        await self.bind("q", "quit", "Quit")
        await self.bind("enter", "submit", "Submit")
        await self.bind("escape", "reset_focus", show=False)
        await self.bind("ctrl+i", "next_tab_index", show=False)
        await self.bind("shift+tab", "previous_tab_index", show=False)

    async def on_mount(self) -> None:

        self.header = CustomHeader()
        await self.view.dock(self.header, edge="top")
        await self.view.dock(CustomFooter(), edge="bottom")

        self.username = TextInput(
            name="username",
            placeholder="enter your username...",
            title="Username",
        )
        self.username.on_change_handler_name = "handle_username_on_change"

        self.password = TextInput(
            name="password",
            title="Password",
            password=True,
        )

        self.age = IntegerInput(
            name="age",
            placeholder="enter your age...",
            title="Age",
        )
        self.age.on_change_handler_name = "handle_age_on_change"
        
        self.code = TextInput(
            name="code",
            placeholder="enter some python code...",
            title="Code",
            syntax="python",
        )
        self.code.on_change_handler_name = "handle_code_on_change"

        self.output = Static(
            renderable=Panel(
                "", title="Report", border_style="blue", box=rich.box.SQUARE
            )
        )
        await self.view.dock(self.output, edge="left", size=40)
        await self.view.dock(self.username, self.password, self.age, self.code, edge="top")

    async def action_next_tab_index(self) -> None:
        """Changes the focus to the next form field"""
        if self.current_index < len(self.tab_index) - 1:
            self.current_index += 1
            await getattr(self, self.tab_index[self.current_index]).focus()

    async def action_previous_tab_index(self) -> None:
        """Changes the focus to the previous form field"""
        self.log(f"PREVIOUS {self.current_index}")
        if self.current_index > 0:
            self.current_index -= 1
            await getattr(self, self.tab_index[self.current_index]).focus()

    async def action_submit(self) -> None:
        formatted = f"""
username: {self.username.value}
password: {"".join("•" for _ in self.password.value)}
     age: {self.age.value}
    code: {self.code.value}
        """
        await self.output.update(
            Panel(formatted, title="Report", border_style="blue", box=rich.box.SQUARE)
        )

    async def action_reset_focus(self) -> None:
        self.current_index = -1
        await self.header.focus()

    async def handle_username_on_change(self, message: Message) -> None:
        self.log(f"Username Field Contains: {message.sender.value}")

    async def handle_age_on_change(self, message: Message) -> None:
        self.log(f"Age Field Contains: {message.sender.value}")

    async def handle_input_on_focus(self, message: Message) -> None:
        self.current_index = self.tab_index.index(message.sender.name)


if __name__ == "__main__":
    SimpleForm.run(title="Textual-Inputs Demo", log="textual.log")
