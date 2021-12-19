from __future__ import annotations

from rich.style import Style

from textual.app import App
from textual.widgets import Placeholder

from textual_inputs import TextInput
from textual_inputs.styling import BorderElementStyle, CursorElementStyle, InputFieldStyle, TextElementStyle


class InputStyling(App):

    async def on_mount(self) -> None:
        """Actions that happen when the a mount event occurs."""
        grid = await self.view.dock_grid()

        grid.add_column("col", max_size=100)
        grid.add_row("row", size=3)
        grid.set_repeat(False, True)
        grid.add_areas(
            placeholder="col,row-3",
            center="col,row-4")
        grid.set_align("center", "center")

        field_style = InputFieldStyle(
            cursor=CursorElementStyle(default=Style(
                color="yellow", blink=True, bold=True)),
            text=TextElementStyle(default=Style(color="grey82")),
            border=BorderElementStyle(
                default=Style(color="medium_purple4"),
                focus=Style(color="medium_purple2", bold=True),
                hover=Style(color="red")
            ),
        )

        # The placeholder only exists as another point of focus for the demo
        grid.place(placeholder=Placeholder(name="test"))

        input = TextInput(name="styling", style=field_style, placeholder="Enter text...")
        grid.place(center=input)


if __name__ == "__main__":

    InputStyling.run(title="InputStyling", log="textual.log")
