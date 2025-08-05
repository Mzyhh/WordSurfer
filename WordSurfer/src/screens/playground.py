from textual.containers import CenterMiddle, Container, Vertical, Horizontal
from textual.widgets import Button, Header, Footer, Static, Input
from textual.app import ComposeResult
from textual.compose import compose
from textual.screen import Screen

import logic
from utils.get_resources import get_resource_file


def add_to_interesting(expr: str, res: str) -> None:
    data_path = str(get_resource_file('data')) + '/'
    with open(data_path + 'interesting_expressions.txt', 'a') as f:
        f.write(expr + ' = ' + res + '\n')

class PlaygroundScreen(Screen):

#    CSS_PATH = env.CSS_PATH + "./playground.css"

    BINDINGS = [('q', 'quit', 'Go to main menu')]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Container (
                Input(placeholder="Enter expression...", id="expression-input"),
                Static("Result", id="result"),
                classes="sandbox",
                id="io-box"
            ),
            Container (
                Button("🤩 Interesting", id="interesting", variant="success"),
                Button("😴 Boring", id="boring", variant="warning"),
                classes="feedback-buttons",
                id="feedback"
            ),
            id="interactive-part")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "interesting":
            self.notify(self.query_one('#expression-input').value, timeout=2)
            add_to_interesting(self.query_one('#expression-input').value, str(self.query_one("#result").renderable))
        elif event.button.id == "boring":
            self.query_one("#expression-input").value = ""
            

    def action_quit(self) -> None:
        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input expression."""
        expression = event.value
        if expression:
            result = 'Sorry but we can\'t compute this expression'
            pos, neg, unk_pos, unk_neg = logic.split_positive_negative(expression)
            if len(pos) + len(neg) > 0:
                result = logic.compute_expression(pos, neg)
            self.query_one("#result").update(result)
