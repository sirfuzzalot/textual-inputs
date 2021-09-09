"""
Simple integer input
"""
import string
from typing import Any, List, Optional, Tuple, Union

import rich.box
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from textual_inputs.events import InputOnChange, InputOnFocus


class IntegerInput(Widget):
    """
    A simple integer input widget.

    Args:
        name (Optional[str]): The unique name of the widget. If None, the
            widget will be automatically named.
        value (Optional[int]): The starting integer value.
        placeholder (Union[str, int, optional): Defaults to "". Text that
            appears in the widget when value is "" and the widget is not focused.
        title (str, optional): Defaults to "". A title on the top left
            of the widget's border.

    Attributes:
        value (Union[int, None]): the value of the input field
        placeholder (str): The placeholder message.
        title (str): The displayed title of the widget.
        has_focus (bool): True if the widget is focused.
        cursor (Tuple[str, Style]): The character used for the cursor
            and a rich Style object defining its appearance.

    Messages:
        InputOnChange: Emitted when the contents of the input changes.
        InputOnFocus: Emitted when the widget becomes focused.

    Examples:

    .. code-block:: python

        from textual_inputs import IntegerInput

        age_input = IntegerInput(
            name="age",
            placeholder="enter your age...",
            title="Age",
        )

    """

    value: Reactive[Union[int, None]] = Reactive(0)
    cursor: Tuple[str, Style] = (
        "|",
        Style(
            color="white",
            blink=True,
            bold=True,
        ),
    )
    _has_focus: Reactive[bool] = Reactive(False)
    _cursor_position: Reactive[int] = Reactive(0)

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: Optional[int] = None,
        placeholder: Union[str, int] = "",
        title: str = "",
        step: int = 1,
        **kwargs: Any
    ) -> None:
        super().__init__(name, **kwargs)
        self.value = value
        self.placeholder = str(placeholder)
        self.title = title
        self.step = step
        self._cursor_position = len(str(self.value))

    def __rich_repr__(self):
        yield "name", self.name
        yield "title", self.title
        yield "value", self.value

    @property
    def has_focus(self) -> bool:
        """Produces True if widget is focused"""
        return self._has_focus

    @property
    def _value_as_str(self) -> str:
        return "" if self.value is None else str(self.value)

    def _increment_value(self, increment: int) -> None:
        """Increments the value by the increment"""
        if self.value is None:
            self.value = 0
        self.value += increment

    def render(self) -> RenderableType:
        """
        Produce a Panel object containing placeholder text or value
        and cursor.
        """
        if self.value is None:
            value = ""
        else:
            value = str(self.value)

        if self.has_focus:
            segments = self._render_text_with_cursor()
        else:
            if len(value) == 0:
                if self.title and not self.placeholder:
                    segments = [self.title]
                else:
                    segments = [self.placeholder]
            else:
                segments = [value]

        text = Text.assemble(*segments)

        if (
            self.title
            and not self.placeholder
            and self.value is None
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

    def _render_text_with_cursor(self) -> List[Union[str, Tuple[str, Style]]]:
        """
        Produces the renderable Text object with cursor

        Returns:
            List[Union[str, Tuple[str, Style]]]: combination of value
                and cursor.
        """
        value = self._value_as_str

        if len(value) == 0:
            segments = [self.cursor]
        elif self._cursor_position == 0:
            segments = [self.cursor, value]
        elif self._cursor_position == len(value):
            segments = [value, self.cursor]
        else:
            segments = [
                value[: self._cursor_position],
                self.cursor,
                value[self._cursor_position :],
            ]

        return segments

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    async def on_key(self, event: events.Key) -> None:
        value = self._value_as_str
        if event.key == "left":
            if self._cursor_position == 0:
                self._cursor_position = 0
            else:
                self._cursor_position -= 1

        elif event.key == "right":
            if self._cursor_position != len(value):
                self._cursor_position = self._cursor_position + 1

        elif event.key == "up":
            self._increment_value(self.step)
            self._cursor_position = len(self._value_as_str)

        elif event.key == "down":
            self._increment_value(-self.step)
            self._cursor_position = len(self._value_as_str)

        elif event.key == "home":
            self._cursor_position = 0

        elif event.key == "end":
            self._cursor_position = len(value)

        elif event.key == "ctrl+h":  # Backspace
            if self._cursor_position == 0:
                return
            elif len(value) == 1:
                self.value = None
                self._cursor_position = 0
            elif len(value) == 2:
                if self._cursor_position == 1:
                    self.value = int(value[1])
                    self._cursor_position = 0
                else:
                    self.value = int(value[0])
                    self._cursor_position = 1
            else:
                if self._cursor_position == 1:
                    self.value = int(value[1:])
                    self._cursor_position = 0
                elif self._cursor_position == len(value):
                    self.value = int(value[:-1])
                    self._cursor_position -= 1
                else:
                    self.value = int(
                        value[: self._cursor_position - 1]
                        + value[self._cursor_position :]
                    )
                    self._cursor_position -= 1

            await self._emit_on_change(event)

        elif event.key == "delete":
            if self._cursor_position == len(value):
                return
            elif len(value) == 1:
                self.value = None
            elif len(value) == 2:
                if self._cursor_position == 1:
                    self.value = int(value[0])
                else:
                    self.value = int(value[1])
            else:
                if self._cursor_position == 0:
                    self.value = int(value[1:])
                else:
                    self.value = int(
                        value[: self._cursor_position]
                        + value[self._cursor_position + 1 :]
                    )
            await self._emit_on_change(event)

        elif event.key in string.digits:
            if self._cursor_position == 0:
                self.value = int(event.key + value)
            elif self._cursor_position == len(value):
                self.value = int(value + event.key)
            else:
                self.value = int(
                    value[: self._cursor_position]
                    + event.key
                    + value[self._cursor_position :]
                )

            if not self._cursor_position > len(str(self.value)):
                self._cursor_position += 1

            await self._emit_on_change(event)

        elif event.key == "-" and self._cursor_position == 0:
            if value[0] != "-" and value != "0":
                self.value = int(event.key + value)
                await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        event.stop()
        await self.emit(InputOnChange(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(InputOnFocus(self))
