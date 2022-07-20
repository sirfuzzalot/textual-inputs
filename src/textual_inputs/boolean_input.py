"""
Simple boolean input
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import rich.box
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from textual_inputs.events import InputOnChange, InputOnFocus, make_message_class

if TYPE_CHECKING:
    from rich.console import RenderableType


class BooleanInput(Widget):
    """
    A simple boolean input widget.

    Args:
        name (Optional[str]): The unique name of the widget. If None, the
            widget will be automatically named.
        value (Optional[bool]): The starting boolean value.
        title (str, optional): Defaults to "". A title on the top left
            of the widget's border.

    Attributes:
        value (bool): the value of the input field
        title (str): The displayed title of the widget.
        has_focus (bool): True if the widget is focused.
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

        from textual_inputs import BooleanInput

        age_input = BooleanInput(
            name="",
            title="Age",
        )

    """

    value: Reactive[bool] = Reactive(0)
    _has_focus: Reactive[bool] = Reactive(False)
    _cursor_position: Reactive[int] = Reactive(0)

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: Optional[bool] = False,
        title: str = "",
    ) -> None:
        super().__init__(name)
        self.value = value
        self.title = title
        self._on_change_message_class = InputOnChange
        self._on_focus_message_class = InputOnFocus
        self._cursor_position = len(str(self.value))

    def __rich_repr__(self):
        yield "name", self.name
        yield "title", self.title
        yield "value", self.value
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

    @property
    def _value_as_str(self) -> str:
        return str(self.value)

    def _toggle_value(self) -> None:
        """Negates the value"""
        self.value = not (self.value)

    def render(self) -> RenderableType:
        """Produce a Panel object containing value"""
        value = str(self.value)
        text = Text.assemble(value)
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

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self._toggle_value()
            await self._emit_on_change(event)

    async def _emit_on_change(self, event: events.Key) -> None:
        event.stop()
        await self.emit(self._on_change_message_class(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(self._on_focus_message_class(self))
