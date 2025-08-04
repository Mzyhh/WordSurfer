from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Input, Static
from textual.containers import Container, CenterMiddle, Horizontal, Vertical

from playground import PlaygroundScreen
import logic


class WordSurfer(App):
    """Main menu with multiple choices."""
    CSS_PATH = 'main_menu.css'

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield CenterMiddle(
            Button("Playground", id="playground"),
            Button("Quiz", id="quiz"),
            Button("Achievements", id="achievements"),
            Button("exit", id="exit"),
            classes="buttons",
            id="main"
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button press."""
            if event.button.id == "playground":
                self.push_screen(PlaygroundScreen())
            elif event.button.id == "quiz":
                self.notify("Start Quiz!")
            elif event.button.id == "achievements":
                self.notify(" Open Achievements...")


if __name__ == "__main__":
    logic.launch()
    app = WordSurfer()
    app.run()
