"""
Simple text input
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

import rich.box
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from textual_inputs.events import InputOnChange, InputOnFocus
from textual_inputs.styling import Element, FieldStyle, State

if TYPE_CHECKING:
    from rich.console import RenderableType


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
        style (FieldStyle): FieldStyle contains the styling of each element
            that makes up the input field widget.

    Attributes:
        value (str): the value of the text field
        placeholder (str): The placeholder message.
        title (str): The displayed title of the widget.
        has_password (bool): True if the text field masks the input.
        has_focus (bool): True if the widget is focused.
        cursor (Tuple[str, Style]): The character used for the cursor
            and a rich Style object defining its appearance.

    Messages:
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
        style: Optional[FieldStyle] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self.value = value
        self.placeholder = placeholder
        self.title = title
        self.has_password = password

        self.input_field_style = style or FieldStyle()

        self._cursor_position = len(self.value)

        self.current_state = State.DEFAULT
        self.last_state = State.DEFAULT

        self.cursor_char: str = "|"

    def __rich_repr__(self):
        yield "name", self.name
        yield "title", self.title
        if self.has_password:
            value = "".join("•" for _ in self.value)
        else:
            value = self.value
        yield "value", value

    @property
    def has_focus(self) -> bool:
        """Produces True if widget is focused"""
        return self._has_focus

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
                segments = [self._conceal_or_reveal(self.value)]

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

        style = self.input_field_style.get_element_style_for_state(
            element=Element.TEXT, state=self.current_state
        )
        border_style = self.input_field_style.get_element_style_for_state(
            element=Element.BORDER, state=self.current_state
        )

        dimensions = self.input_field_style.get_dimensions_for_state(
            state=self.current_state
        )

        return Panel(
            text,
            title=title,
            title_align="left",
            height=dimensions[0],
            width=dimensions[1],
            style=style,
            border_style=border_style,
            box=rich.box.DOUBLE if self.has_focus else rich.box.SQUARE,
        )

    def _conceal_or_reveal(self, segment: str) -> str:
        """
        Produce the segment either concealed like a password or as it
        was passed.
        """
        if self.has_password:
            return "".join("•" for _ in segment)
        return segment

    def _render_text_with_cursor(self) -> List[Union[str, Tuple[str, Style]]]:
        """
        Produces the renderable Text object combining value and cursor
        """

        cursor: Tuple[str, Style] = (
            self.cursor_char,
            self.input_field_style.get_element_style_for_state(
                Element.CURSOR, self.current_state
            ),
        )

        if len(self.value) == 0:
            segments = [cursor]
        elif self._cursor_position == 0:
            segments = [cursor, self._conceal_or_reveal(self.value)]
        elif self._cursor_position == len(self.value):
            segments = [self._conceal_or_reveal(self.value), cursor]
        else:
            segments = [
                self._conceal_or_reveal(self.value[: self._cursor_position]),
                cursor,
                self._conceal_or_reveal(self.value[self._cursor_position :]),
            ]

        return segments

    async def on_enter(self, event: events.Enter) -> None:
        self.set_state(State.HOVER, transient=True)

    async def on_leave(self, event: events.Leave) -> None:
        self.set_state(self.last_state, transient=True)

    async def on_focus(self, event: events.Focus) -> None:
        self._has_focus = True
        await self._emit_on_focus()
        self.set_state(state=State.FOCUS)

    async def on_blur(self, event: events.Blur) -> None:
        self._has_focus = False
        self.set_state(state=State.DEFAULT)

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
        await self.emit(InputOnChange(self))

    async def _emit_on_focus(self) -> None:
        await self.emit(InputOnFocus(self))

    def set_state(self, state: State, transient: bool = False) -> None:
        """Sets the current state of the input field.

        States can be set to transient, which means that they will not persist.
        For example, a transient state of "hover" will not persist if the
        user clicks on the input field.

        Args:
            state (InputState): The current state of the input field.
            transient (bool, optional): Sets the state as transient or not.
                Defaults to False.
        """

        self.log(f"State changed to {state}")

        self.current_state = state
        if not transient:
            self.last_state = self.current_state

        self.refresh()
