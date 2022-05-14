# Textual Inputs 🔡

[![Python Versions](https://shields.io/pypi/pyversions/textual-inputs)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Textual Inputs is a collection of input widgets for the [Textual](https://github.com/willmcgugan/textual) TUI framework.

> ⚠️ This library is experimental and its interfaces will change. While
> Textual Inputs is pre-alpha please pin your projects to the minor release
> number to avoid breaking changes. For example: textual-inputs=0.2.\*

## News

### v0.2.5

Adds support for syntax highlighting. To add syntax highlighting to your
input text set the `syntax` argument to a language supported by
`pygments`. Currently this is set to the default theme.

```python
TextInput(
    name="code",
    placeholder="enter some python code...",
    title="Code",
    syntax="python",
)
```

## Quick Start

Installation

```bash
python -m pip install textual-inputs~=0.2
```

To use Textual Inputs

```python
from textual_inputs import TextInput, IntegerInput
```

Checkout the [examples](https://github.com/sirfuzzalot/textual-inputs/tree/main/examples) for reference.

```bash
git clone https://github.com/sirfuzzalot/textual-inputs.git
cd textual-inputs
python3 -m venv venv
source venv/bin/activate
python -m pip install -e .
python examples/simple_form.py
```

## Widgets

### TextInput 🔡

- value - string
- one line of text
- placeholder and title support
- password mode to hide input
- syntax mode to highlight code
- support for Unicode characters
- controls: arrow right/left, home, end, delete, backspace/ctrl+h, escape
- emits - InputOnChange, InputOnFocus messages

### IntegerInput 🔢

- value - integer or None
- placeholder and title support
- type a number or arrow up/down to increment/decrement the integer.
- controls: arrow right/left, home, end, delete, backspace/ctrl+h, escape
- emits - InputOnChange, InputOnFocus messages

## Features

### One-Line Syntax Highlighting

Textual Inputs takes advantage of `rich`'s built-in Syntax feature. To
add highlighting to your input text set the `syntax` argument to a language
supported by `pygments`. Currently this is set to the default theme.

**⚠️ THIS FEATURE IS LIMITED TO ONE LINE OF TEXT**

```python
TextInput(
    name="code",
    placeholder="enter some python code...",
    title="Code",
    syntax="python",
)
```

### Event Handlers

Textual Inputs helps make the event handler process easier by providing
the following convenient properties for inputs.

- on_change_handler_name
- on_focus_handler_name

```python
email = TextInput(name="email", title="Email")
email.on_change_handler_name = "handle_email_on_change"
email.on_focus_handler_name = "handle_email_on_focus"
```

Under the hood setting this attribute this will generate a `Message` class
with the appropriate name for Textual to send it to the handler name provided.
You'll then want add the handler to the input's parent or the App instance.
If you opt not to customize these handlers, their values will be the
default `handle_input_on_change` and `handle_input_on_focus`. See
`examples/simple_form.py` for a working example.

## API Reference

Textual Inputs has two widgets, here are their attributes.

```python
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
```

```python
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

        from textual_inputs import IntegerInput

        age_input = IntegerInput(
            name="age",
            placeholder="enter your age...",
            title="Age",
        )

    """
```

## Contributing

See the [Contributing Guide](https://github.com/sirfuzzalot/textual-inputs/blob/main/CONTRIBUTING.md).
