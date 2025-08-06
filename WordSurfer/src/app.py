from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button
from textual.containers import CenterMiddle

from screens.playground import PlaygroundScreen
from screens.quiz import QuizScreen
from utils.get_resources import get_resource_file
from config import launch, Config


class WordSurfer(App):
    """Main menu with multiple choices."""
    CSS_PATH = str(get_resource_file("style.css"))

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

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
                self.push_screen(PlaygroundScreen(config))
            elif event.button.id == "quiz":
                self.push_screen(QuizScreen(config))
            elif event.button.id == "achievements":
                self.notify(" Open Achievements...")
            elif event.button.id == "exit":
                self.exit()


if __name__ == "__main__":
    config = launch()
    app = WordSurfer(config)
    app.run()
