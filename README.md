# Textual Inputs 🔡

[![Python Versions](https://shields.io/pypi/pyversions/textual-inputs)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Textual Inputs is a collection of input widgets for the [Textual](https://github.com/willmcgugan/textual) TUI framework.

⚠️ This library is experimental and its interfaces are likely
to change, much like the underlying Textual library.

## Supported Widgets

### TextInput 🔡

- value - string
- one line of text
- placeholder and title support
- password mode to hide input
- support for Unicode characters
- controls: arrow right/left, home, end, delete, backspace/ctrl+h, escape
- emits - InputOnChange, InputOnFocus messages

### IntegerInput 🔢

- value - integer or None
- placeholder and title support
- type a number or arrow up/down to increment/decrement the integer.
- controls: arrow right/left, home, end, delete, backspace/ctrl+h, escape
- emits - InputOnChange, InputOnFocus messages

## Quick Start

```bash
python -m pip install textual-inputs
```

Checkout the [examples](https://github.com/sirfuzzalot/textual-inputs/tree/main/examples) for reference.

```bash
git clone https://github.com/sirfuzzalot/textual-inputs.git
cd textual-inputs
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python examples/simple_form.py
```

To use Textual Inputs

```python
from textual_inputs import TextInput, IntegerInput
```
