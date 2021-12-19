from enum import Enum
from rich.style import Style
from typing import Optional


class Element(Enum):
    CURSOR = "cursor"
    TEXT = "text"
    BORDER = "border"


class InputState(Enum):
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

    def get_style_for_state(self, state: InputState) -> Style:
        return self.style_map[state.value]


class CursorElementStyle(ElementStyle):
    pass

class TextElementStyle(ElementStyle):
    pass

class BorderElementStyle(ElementStyle):
    pass


class InputFieldStyle:
    def __init__(self, cursor: CursorElementStyle, text: TextElementStyle, border: BorderElementStyle):

        self.style_map: dict[Element, ElementStyle] = {
            "cursor": cursor,
            "text": text,
            "border": border,
        }

    def get_element_style_for_state(self, element: Element, state: InputState = InputState.DEFAULT) -> Style:
        """Produces the style for the element in the given state"""
        
        style = self.style_map[element.value]
        style_for_state = style.get_style_for_state(state)
        return style_for_state
