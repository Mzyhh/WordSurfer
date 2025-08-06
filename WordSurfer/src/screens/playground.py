from textual.containers import CenterMiddle, Container, Vertical, Horizontal
from textual.widgets import Button, Header, Footer, Static, Input
from textual.app import ComposeResult
from textual.compose import compose
from textual.screen import Screen
import typing as t

from utils.get_resources import get_resource_file
from config import Config



class PlaygroundScreen(Screen):

    BINDINGS = [('q', 'quit', 'Go to main menu')]

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

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
            self.add_to_interesting(self.query_one('#expression-input').value, str(self.query_one("#result").renderable))
        elif event.button.id == "boring":
            self.query_one("#expression-input").value = ""
            

    def action_quit(self) -> None:
        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input expression."""
        expression = event.value
        if expression:
            result = 'Sorry but we can\'t compute this expression'
            pos, neg, unk_pos, unk_neg = self.split_positive_negative(expression)
            if len(pos) + len(neg) > 0:
                result = self.compute_expression(pos, neg)
            self.query_one("#result").update(result)

    def split_positive_negative(self, expression: str) -> t.Tuple[t.List[str], t.List[str], t.List[str], t.List[str]]:
        """Split expression on four lists: positive, negative, not-presented pos/neg.
        :param expression: Expression containing letters and +/-
        :returns: a tuple of four lists of strings
        example usage:
        >>> split_positive_negative("aboba - cat + dog - ksljdfv")
        (['dog'], ['cat'], ['aboba'], ['ksljdfv'])"""

        splitted = expression.replace(' ', '').replace('\t', '').replace('\n', '').replace('-', '+-').split('+')
        pos, neg, unk_pos, unk_neg = [], [], [], []
        for word in splitted:
            ref, unk_ref = pos, unk_pos
            if word[0] == '-':
                word = word[1:]
            ref, unk_ref = neg, unk_neg
            if word not in self.config.model.key_to_index:
                unk_ref.append(word)
            else:
                ref.append(word)
        return pos, neg, unk_pos, unk_neg

    def compute_expression(self, positive_words, negative_words) -> str:
        return self.config.model.most_similar(positive=positive_words, negative=negative_words, topn=1)[0][0]

    def add_to_interesting(self, expr: str, res: str) -> None:
        data_path = str(get_resource_file('data')) + '/'
        with open(data_path + self.config.int_filepath, 'a') as f:
            f.write(expr + ' = ' + res + '\n')
