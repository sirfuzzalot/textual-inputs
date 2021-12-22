from __future__ import annotations

from rich.style import Style
from textual.app import App

from textual_inputs import TextInput
from textual_inputs.styling import BorderStyle, CursorStyle, FieldStyle, TextStyle


class InputStyling(App):
    async def on_mount(self) -> None:
        """Actions that happen when the a mount event occurs."""
        grid = await self.view.dock_grid()

        grid.add_column("col", max_size=100)
        grid.add_row("row", size=3)
        grid.set_repeat(False, True)
        grid.add_areas(styled="col,row-3", default="col,row-4")
        grid.set_align("center", "center")

        styled_field = TextInput(
            name="styling",
            placeholder="styled field...",
            style=FieldStyle(
                cursor=CursorStyle(
                    default=Style(color="yellow", blink=True, bold=True)
                ),
                text=TextStyle(default=Style(color="grey82")),
                border=BorderStyle(
                    default=Style(color="medium_purple4"),
                    focus=Style(color="medium_purple2", bold=True),
                    hover=Style(color="red"),
                ),
            ),
        )

        default_field = TextInput(
            name="default",
            placeholder="default field...",
        )

        # The placeholder only exists as another point of focus for the demo
        grid.place(styled=styled_field)
        grid.place(default=default_field)


if __name__ == "__main__":

    InputStyling.run(title="InputStyling", log="textual.log")
