"""
Events for Textual-Inputs
"""
from textual.message import Message


class InputOnChange(Message, bubble=True):
    """Emitted when the value of an input changes"""

    pass


class InputOnFocus(Message, bubble=True):
    """Emitted when the input becomes focused"""

    pass
