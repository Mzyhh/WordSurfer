from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button
from textual.containers import Container

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
        print(type(config))
        yield Header()
        yield Footer()
        yield Container(
            Button(self.config.messages['playground button'], id="playground"),
            Button(self.config.messages['quiz button'], id="quiz"),
            Button(self.config.messages['exit button'], id="exit"),
            classes="buttons",
            id="main"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button press."""
            if event.button.id == "playground":
                self.push_screen(PlaygroundScreen(self.config))
            elif event.button.id == "quiz":
                self.push_screen(QuizScreen(self.config))
            elif event.button.id == "exit":
                self.exit()


if __name__ == "__main__":
    config = launch()
    app = WordSurfer(config)
    app.run()
