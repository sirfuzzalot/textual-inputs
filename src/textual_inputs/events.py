"""
Events for Textual-Inputs
"""
from __future__ import annotations

from string import ascii_lowercase, digits

from textual.message import Message

HANDLER_SAFE = ascii_lowercase + digits + "_"


class InputOnChange(Message, bubble=True):
    """Generic on change message for inputs"""

    _handler: str = "handle_input_on_change"


class InputOnFocus(Message, bubble=True):
    """Generic on focus message for inputs"""

    _handler: str = "handle_input_on_focus"


def make_message_class(handler_name: str) -> Message:
    """
    Produces an appropriately named Message subclass that will call the
    handler with the same name as handler_name.

    Args:
        handler_name (str): handler function name. Must start with "handle_" and
            contain only lowercase ASCII letters, numbers and underscores.

    Returns:
        Message: a subclass of the Message class.

    Raises:
        ValueError: handler_name must start with 'handle_'.
        ValueError: handler_name must contain only lowercase ASCII
            letters, numbers and underscores.

    Example:

    .. code-block:: python

        >>>make_message_class("handle_username_on_change")
        <class 'textual_inputs.events.username_on_change>
        >>>def handle_username_on_change(self, event: Message) -> None:

    """
    if not handler_name.startswith("handle_"):
        raise ValueError("handler_name must start with 'handle_'")

    if len(handler_name) < 7:
        raise ValueError("handler_name must be greater than 7 characters")

    for char in handler_name:
        if char not in HANDLER_SAFE:
            raise ValueError(
                "handler_name must contain only lowercase ASCII letters, "
                + "numbers and underscores."
            )
    name = handler_name.lower()[7:]
    t = type(name, (Message,), {})
    t._handler = handler_name
    t.bubble = True
    return t
