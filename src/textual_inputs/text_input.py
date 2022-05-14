"""
Simple text input
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from textual_inputs.events import InputOnChange, InputOnFocus, make_message_class

if TYPE_CHECKING:
    from rich.console import RenderableType

CONSOLE = Console()


def conceal_text(segment: str) -> str:
    """Produce the segment concealed like a password."""
    return "•" * len(segment)


def syntax_highlight_text(code: str, syntax: str) -> Text:
    """Produces highlighted text based on the syntax."""
    syntax_obj = Syntax(code, syntax)
    with CONSOLE.capture() as capture:
        CONSOLE.print(syntax_obj)
    return Text.from_ansi(capture.get())


class TextInput(Widget):
    """
    A simple text input widget.

    Args:
        name (Optional[str]): The unique name of the widget. If None, the
            widget will be automatically named.
        value (str, optional): Defaults to "". The starting text value.
        placeholder (str, optional): Defaults to "". Text that appears
            in the widget when value is "" and the widget is not focused.
        title (str, optional): Defaults to "". A title on the top left
            of the widget's border.
        password (bool, optional): Defaults to False. Hides the text
            input, replacing it with bullets.
        syntax (Optional[str]): the name of the language for syntax highlighting.

    Attributes:
        value (str): the value of the text field
        placeholder (str): The placeholder message.
        title (str): The displayed title of the widget.
        has_password (bool): True if the text field masks the input.
        syntax (Optional[str]): the name of the language for syntax highlighting.
        has_focus (bool): True if the widget is focused.
        cursor (Tuple[str, Style]): The character used for the cursor
            and a rich Style object defining its appearance.
        on_change_handler_name (str): name of handler function to be
            called when an on change event occurs. Defaults to
            handle_input_on_change.
        on_focus_handler_name (name): name of handler function to be
            called when an on focus event occurs. Defaults to
            handle_input_on_focus.

    Events:
        InputOnChange: Emitted when the contents of the input changes.
        InputOnFocus: Emitted when the widget becomes focused.

    Examples:

    .. code-block:: python

        from textual_inputs import TextInput

        email_input = TextInput(
            name="email",
            placeholder="enter your email address...",
            title="Email",
        )

    """

    value: Reactive[str] = Reactive("")
    cursor: Tuple[str, Style] = (
        "|",
        Style(
            color="white",
            blink=True,
            bold=True,
        ),
    )
    _cursor_position: Reactive[int] = Reactive(0)
    _has_focus: Reactive[bool] = Reactive(False)

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: str = "",
        placeholder: str = "",
        title: str = "",
        password: bool = False,
        syntax: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.value = value
        self.placeholder = placeholder
        self.title = title
        self.has_password = password
        self.syntax = syntax
        self._on_change_message_class = InputOnChange
        self._on_focus_message_class = InputOnFocus
        self._cursor_position = len(self.value)

    def __rich_repr__(self):
        yield "name", self.name
        yield "title", self.title
        if self.has_password:
            value = "".join("•" for _ in self.value)
        else:
            value = self.value
        yield "value", value
        yield "on_change_handler_name", self.on_change_handler_name
        yield "on_focus_handler_name", self.on_focus_handler_name

    @property
    def has_focus(self) -> bool:
        """Produces True if widget is focused"""
        return self._has_focus

    @property
    def on_change_handler_name(self) -> str:
        return self._on_change_message_class._handler

    @on_change_handler_name.setter
    def on_change_handler_name(self, handler_name: str) -> None:
        """
        Name of the handler function for an on change event to be sent to.
        Must start with "handle_" and contain only lowercase ASCII letters,
        numbers and underscores.
        """
        self._on_change_message_class = make_message_class(handler_name)

    @property
    def on_focus_handler_name(self) -> str:
        return self._on_focus_message_class._handler

    @on_focus_handler_name.setter
    def on_focus_handler_name(self, handler_name: str) -> None:
        """
        Name of the handler function for an on focus event to be sent to.
        Must start with "handle_" and contain only lowercase ASCII letters,
        numbers and underscores.
        """
        self._on_focus_message_class = make_message_class(handler_name)

    def render(self) -> RenderableType:
        """
        Produce a Panel object containing placeholder text or value
        and cursor.
        """
        if self.has_focus:
            segments = self._render_text_with_cursor()
        else:
            if len(self.value) == 0:
                if self.title and not self.placeholder:
                    segments = [self.title]
                else:
                    segments = [self.placeholder]
            else:
                segments = [self._modify_text(self.value)]

        text = Text.assemble(*segments)

        if (
            self.title
            and not self.placeholder
            and len(self.value) == 0
            and not self.has_focus
        ):
            title = ""
        else:
            title = self.title

        return Panel(
            text,
            title=title,
            title_align="left",
            height=3,
            style=self.style or "",
            border_style=self.border_style or Style(color="blue"),
            box=rich.box.DOUBLE if self.has_focus else rich.box.SQUARE,
        )

    def _modify_text(self, segment: str) -> Union[str, Text]:
        """
        Produces the text with modifications, such as password concealing.
        """
        if self.has_password:
            return conceal_text(segment)
        if self.syntax:
            return syntax_highlight_text(segment, self.syntax)
        return segment

    def _render_text_with_cursor(self) -> List[Union[str, Text, Tuple[str, Style]]]:
        """
        Produces the renderable Text object combining value and cursor
        """
        text = self._modify_text(self.value)
        return [
            text[: self._cursor_position],
            self.cursor,
            text[self._cursor_position :],
        ]

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    async def on_key(self, event: events.Key) -> None:
        if event.key == "left":
            if self._cursor_position == 0:
                self._cursor_position = 0
            else:
                self._cursor_position -= 1

        elif event.key == "right":
            if self._cursor_position != len(self.value):
                self._cursor_position = self._cursor_position + 1

        elif event.key == "home":
            self._cursor_position = 0

        elif event.key == "end":
            self._cursor_position = len(self.value)

        elif event.key == "ctrl+h":  # Backspace
            if self._cursor_position == 0:
                return
            elif len(self.value) == 1:
                self.value = ""
                self._cursor_position = 0
            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[1]
                    self._cursor_position = 0
                else:
                    self.value = self.value[0]
                    self._cursor_position = 1
            else:
                if self._cursor_position == 1:
                    self.value = self.value[1:]
                    self._cursor_position = 0
                elif self._cursor_position == len(self.value):
                    self.value = self.value[:-1]
                    self._cursor_position -= 1
                else:
                    self.value = (
                        self.value[: self._cursor_position - 1]
                        + self.value[self._cursor_position :]
                    )
                    self._cursor_position -= 1

            await self._emit_on_change(event)

        elif event.key == "delete":
            if self._cursor_position == len(self.value):
                return
            elif len(self.value) == 1:
                self.value = ""
            elif len(self.value) == 2:
                if self._cursor_position == 1:
                    self.value = self.value[0]
                else:
                    self.value = self.value[1]
            else:
                if self._cursor_position == 0:
                    self.value = self.value[1:]
                else:
                    self.value = (
                        self.value[: self._cursor_position]
                        + self.value[self._cursor_position + 1 :]
                    )
            await self._emit_on_change(event)

        elif len(event.key) == 1 and event.key.isprintable():
            if self._cursor_position == 0:
                self.value = event.key + self.value
            elif self._cursor_position == len(self.value):
                self.value = self.value + event.key
            else:
                self.value = (
                    self.value[: self._cursor_position]
                    + event.key
                    + self.value[self._cursor_position :]
                )

            if not self._cursor_position > len(self.value):
                self._cursor_position += 1

            await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        event.stop()
        await self.emit(self._on_change_message_class(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(self._on_focus_message_class(self))
