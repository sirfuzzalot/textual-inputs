from __future__ import annotations

from enum import Enum
from typing import Optional

from rich.style import Style


class Element(Enum):
    CURSOR = "cursor"
    TEXT = "text"
    BORDER = "border"

class State(Enum):
    DEFAULT = "default"
    FOCUS = "focus"
    HOVER = "hover"


class ElementStyle:
    """
    Styles mapped to states
    """

    def __init__(
        self,
        default: Style,
        *,
        focus: Optional[Style] = None,
        hover: Optional[Style] = None,
    ) -> None:

        self.style_map: dict[str, Style] = {
            "default": default,
            "focus": focus or default,
            "hover": hover or default,
        }

    def get_style_for_state(self, state: State) -> Style:
        return self.style_map[state.value]


class CursorStyle(ElementStyle):
    pass


class TextStyle(ElementStyle):
    pass


class BorderStyle(ElementStyle):
    pass


class FieldStyle:
    def __init__(
        self,
        *,
        cursor: CursorStyle | None = None,
        text: TextStyle | None = None,
        border: BorderStyle | None = None,
    ) -> None:

        default_cursor = CursorStyle(
            default=Style(color="white", blink=True, bold=True),
        )
        default_text = TextStyle(
            default=Style(color="grey82"),
        )
        default_border = BorderStyle(
            default=Style(color="blue")
        )

        self.style_map: dict[str, ElementStyle] = {
            "cursor": cursor or default_cursor,
            "text": text or default_text,
            "border": border or default_border,
        }

    def get_element_style_for_state(
        self, element: Element, state: State = State.DEFAULT
    ) -> Style:
        """Produces the style for the element in the given state"""

        style = self.style_map[element.value]
        style_for_state = style.get_style_for_state(state)
        return style_for_state
