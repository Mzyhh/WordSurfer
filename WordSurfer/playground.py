from textual.containers import CenterMiddle, Container, Vertical, Horizontal
from textual.widgets import Button, Header, Footer, Static, Input
from textual.app import ComposeResult
from textual.compose import compose
from textual.screen import Screen

import logic

class PlaygroundScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(name="Playground")
        yield Footer()
        with Vertical(id="main-container"):
            yield Button("← Main menu", id="exit-btn", variant="error")
            
            yield Static("Enter expression:", classes="instruction")
            
            with Container(id="input-container"):
                yield Input(placeholder="Expression...", id="expression-input")
            
            yield Static("Result", id="result")
            
            with Horizontal(id="feedback-buttons"):
                yield Button("🤩 Interesting", id="interesting", variant="success")
                yield Button("😴 Boring", id="boring", variant="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-btn":
            self.app.pop_screen()
        elif event.button.id in ("interesting", "boring"):
            self.query_one("#expression-input").value = ""
            self.notify("Thank you for feedback!", timeout=2)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input expression."""
        expression = event.value
        if expression:
            result = 'Sorry but we can\'t compute this expression'
            pos, neg, unk_pos, unk_neg = logic.split_positive_negative(expression)
            if len(pos) + len(neg) > 0:
                result = logic.compute_expression(pos, neg)
            self.query_one("#result").update(result)
