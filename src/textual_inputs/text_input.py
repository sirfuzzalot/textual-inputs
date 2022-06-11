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
    """A simple text input widget.

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
        syntax (Optional[str]): The name of the language for syntax highlighting.

    Attributes:
        value (str): The value of the text field
        placeholder (str): The placeholder message.
        title (str): The displayed title of the widget.
        has_password (bool): True if the text field masks the input.
        syntax (Optional[str]): the name of the language for syntax highlighting.
        has_focus (bool): True if the widget is focused.
        cursor (Tuple[str, Style]): The character used for the cursor
            and a rich Style object defining its appearance.
        on_change_handler_name (str): The name of handler function to be
            called when an on change event occurs. Defaults to
            handle_input_on_change.
        on_focus_handler_name (name): The name of handler function to be
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
    """Character and style of the cursor."""
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
        """The value of the text field"""
        self.placeholder = placeholder
        """
        Text that appears in the widget when value is "" and the widget
        is not focused.
        """
        self.title = title
        """The displayed title of the widget."""
        self.has_password = password
        """True if the text field masks the input."""
        self.syntax = syntax
        """The name of the language for syntax highlighting."""
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
        """Produces the text with modifications, such as password concealing."""
        if self.has_password:
            return conceal_text(segment)
        if self.syntax:
            return syntax_highlight_text(segment, self.syntax)
        return segment

    @property
    def _visible_width(self):
        """Width in characters of the inside of the input"""
        # remove 2, 1 for each of the border's edges
        # remove 1 more for the cursor
        # remove 2 for the padding either side of the input
        width, _ = self.size
        if self.border:
            width -= 2
        if self._has_focus:
            width -= 1
        width -= 2
        return width

    def _text_offset_window(self):
        """
        Produce the start and end indices of the visible portions of the
        text value.
        """
        return self._text_offset, self._text_offset + self._visible_width

    def _render_text_with_cursor(self) -> List[Union[str, Text, Tuple[str, Style]]]:
        """Produces the renderable Text object combining value and cursor"""
        text = self._modify_text(self.value)

        # trim the string to fit within the widgets dimensions
        left, right = self._text_offset_window()
        text = text[left:right]

        # convert the cursor to be relative to this view
        cursor_relative_position = self._cursor_position - self._text_offset
        return [
            text[:cursor_relative_position],
            self.cursor,
            text[cursor_relative_position:],
        ]

    async def on_focus(self, event: events.Focus) -> None:
        """Handle Focus events

        Args:
            event (events.Focus): A Textual Focus event
        """
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        """Handle Blur events

        Args:
            event (events.Blur): A Textual Blur event
        """
        self._has_focus = False

    def _update_offset_left(self):
        """
        Decrease the text offset if the cursor moves less than 3 characters
        from the left edge. This will shift the text to the right and keep
        the cursor 3 characters from the left edge. If the text offset is 0
        then the cursor may continue to move until it reaches the left edge.
        """
        visibility_left = 3
        if self._cursor_position < self._text_offset + visibility_left:
            self._text_offset = max(0, self._cursor_position - visibility_left)

    def _update_offset_right(self):
        """
        Increase the text offset if the cursor moves beyond the right
        edge of the widget. This will shift the text left and make the
        cursor visible at the right edge of the widget.
        """
        _, right = self._text_offset_window()
        if self._cursor_position > right:
            self._text_offset = self._cursor_position - self._visible_width

    def _cursor_left(self):
        """Handle key press Left"""
        if self._cursor_position > 0:
            self._cursor_position -= 1
            self._update_offset_left()

    def _cursor_right(self):
        """Handle key press Right"""
        if self._cursor_position < len(self.value):
            self._cursor_position = self._cursor_position + 1
            self._update_offset_right()

    def _cursor_home(self):
        """Handle key press Home"""
        self._cursor_position = 0
        self._update_offset_left()

    def _cursor_end(self):
        """Handle key press End"""
        self._cursor_position = len(self.value)
        self._update_offset_right()

    def _key_backspace(self):
        """Handle key press Backspace"""
        if self._cursor_position > 0:
            self.value = (
                self.value[: self._cursor_position - 1]
                + self.value[self._cursor_position :]
            )
            self._cursor_position -= 1
            self._update_offset_left()

    def _key_delete(self):
        """Handle key press Delete"""
        if self._cursor_position < len(self.value):
            self.value = (
                self.value[: self._cursor_position]
                + self.value[self._cursor_position + 1 :]
            )

    def _key_printable(self, event: events.Key):
        """Handle all printable keys"""
        self.value = (
            self.value[: self._cursor_position]
            + event.key
            + self.value[self._cursor_position :]
        )

        if not self._cursor_position > len(self.value):
            self._cursor_position += 1
            self._update_offset_right()

    async def on_key(self, event: events.Key) -> None:
        """Handle key events

        Args:
            event (events.Key): A Textual Key event
        """
        BACKSPACE = "ctrl+h"
        if event.key == "left":
            self._cursor_left()
        elif event.key == "right":
            self._cursor_right()
        elif event.key == "home":
            self._cursor_home()
        elif event.key == "end":
            self._cursor_end()
        elif event.key == BACKSPACE:
            self._key_backspace()
            await self._emit_on_change(event)
        elif event.key == "delete":
            self._key_delete()
            await self._emit_on_change(event)
        elif len(event.key) == 1 and event.key.isprintable():
            self._key_printable(event)
            await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        """Emit custom message class on Change events"""
        event.stop()
        await self.emit(self._on_change_message_class(self))

    async def _emit_on_focus(self) -> None:
        """Emit custom message class on Focus events"""
        await self.emit(self._on_focus_message_class(self))
