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
        self._text_offset = 0

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

    @property
    def _visible_width(self):
        width, _ = self.size
        # remove 2, 1 for each of the border's edges
        # remove 1 more for the cursor
        # remove 2 for the padding either side of the input
        if self.border:
            width -= 2
        if self._has_focus:
            width -= 1
        width -= 2
        return width

    def _text_offset_window(self):
        return self._text_offset, self._text_offset + self._visible_width

    def _render_text_with_cursor(self) -> List[Union[str, Text, Tuple[str, Style]]]:
        """
        Produces the renderable Text object combining value and cursor
        """
        text = self._modify_text(self.value)

        # trim the string to fit within the widgets dimensions
        # we then need to convert the cursor to be relative to this view
        left, right = self._text_offset_window()
        text = text[left:right]
        cursor_relative_position = self._cursor_position - self._text_offset
        return [
            text[: cursor_relative_position],
            self.cursor,
            text[cursor_relative_position :],
        ]

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    def _update_offset_left(self):
        # ensure the cursor always has at least N character to the left
        visibility_left = 3
        if self._cursor_position < self._text_offset + visibility_left:
            # move the text offset to permit the cursor at the end
            self._text_offset = max(0, self._cursor_position - visibility_left)

    def _update_offset_right(self):
        _, right = self._text_offset_window()
        # if we're at the edge of the widget
        # shuffle our text across
        if self._cursor_position > right:
            # move the text offset to permit the cursor at the end
            self._text_offset = self._cursor_position - self._visible_width

    def cursor_left(self):
        if self._cursor_position > 0:
            self._cursor_position -= 1
            self._update_offset_left()

    def cursor_right(self):
        if self._cursor_position < len(self.value):
            self._cursor_position = self._cursor_position + 1
            self._update_offset_right()

    def cursor_home(self):
        self._cursor_position = 0
        self._update_offset_left()

    def cursor_end(self):
        self._cursor_position = len(self.value)
        self._update_offset_right()

    def key_backspace(self):
        if self._cursor_position > 0:
            self.value = (
                self.value[: self._cursor_position - 1]
                + self.value[self._cursor_position :]
            )
            self._cursor_position -= 1
            self._update_offset_left()

    def key_delete(self):
        if self._cursor_position < len(self.value):
            self.value = (
                self.value[: self._cursor_position]
                + self.value[self._cursor_position + 1 :]
            )

    def key_printable(self, event):
        self.value = (
            self.value[: self._cursor_position]
            + event.key
            + self.value[self._cursor_position :]
        )

        if not self._cursor_position > len(self.value):
            self._cursor_position += 1
            self._update_offset_right()

    async def on_key(self, event: events.Key) -> None:
        BACKSPACE = "ctrl+h"
        if event.key == "left":
            self.cursor_left()
        elif event.key == "right":
            self.cursor_right()
        elif event.key == "home":
            self.cursor_home()
        elif event.key == "end":
            self.cursor_end()
        elif event.key == BACKSPACE:
            self.key_backspace()
            await self._emit_on_change(event)
        elif event.key == "delete":
            self.key_delete()
            await self._emit_on_change(event)
        elif len(event.key) == 1 and event.key.isprintable():
            self.key_printable(event)
            await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        event.stop()
        await self.emit(self._on_change_message_class(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(self._on_focus_message_class(self))
