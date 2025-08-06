from textual.containers import CenterMiddle, Container, Vertical, Horizontal
from textual.widgets import Button, Header, Footer, Static, Label, OptionList
from textual.widgets.option_list import Option
from textual.app import ComposeResult
from textual.compose import compose
from textual.screen import Screen
import typing as t
from random import sample
import numpy as np

from utils.get_resources import get_resource_file
from config import Config


class QuizScreen(Screen):

    BINDINGS = [('q', 'quit', 'Go to main menu')]
     

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.n_words = 1
        self.n_options = self.config.n_options
        self.user_score = 0
        self.is_answered = False

    def compose(self) -> ComposeResult:
        self.cur_expr, self.cur_target, self.cur_opt_words = self.rand_expr(self.n_words, self.n_options)
        yield Header()
        yield Footer()
        yield Container(
            Container(
                Label(self.config.messages['number of words']),
                OptionList(
                    *self.config.messages['number of words list'].split('\n'),
                    id="num_of_words"
                ),
                Static(self.config.messages['score'] + str(self.user_score),
                       id='user-score'),
                id="quiz-options"
            ),
            Container(
                Static(self.cur_expr, id="quiz-out"),
                OptionList(*self.cur_opt_words, id='opt-words'),
                Button(self.config.messages['continue button'], disabled=True,
                       id='next-question'),
                id="quiz-main"
            ),
            id="quiz-body"
        )

    def action_quit(self) -> None:
        self.app.pop_screen()

    def on_option_list_option_selected(self, option_selected):
        if option_selected.option_list.id == 'num_of_words':
            self.n_words = option_selected.option_index + 1
            self.update_question()
        elif not self.is_answered and option_selected.option_list.id == 'opt-words':
            user_ans = self.cur_opt_words[option_selected.option_index]
            if user_ans == self.cur_target:
                self.user_score += 1
                self.query_one('#user-score').update('Score: ' + str(self.user_score))
            self.query_one('#next-question').disabled = False
            self.is_answered = True

            self.show_correct(user_ans)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'next-question':
            self.update_question()

    def show_correct(self, user_ans: str) -> None:
        opt_words = self.query_one('#opt-words')
        opt_words.clear_options()
        for w in self.cur_opt_words:
            if w == self.cur_target:
                w = '[green]' + w + '[/]'
            elif w == user_ans:
                w = '[red]' + w + '[/]'
            opt_words.add_option(w)

    def update_question(self) -> None:
        self.cur_expr, self.cur_target, self.cur_opt_words = self.rand_expr(self.n_words, self.n_options)
        self.query_one('#quiz-out').update(self.cur_expr)
        opt_words = self.query_one('#opt-words')
        opt_words.clear_options()
        opt_words.add_options(self.cur_opt_words)
        self.is_answered = False
        self.query_one('#next-question').disabled = True

    def rand_expr(self, n_words: int, n_options: int) -> t.Tuple[str, str, t.List[str]]:
        """Generate random word expression.
        :param n_words: number of words expression consists of.
        :param n_options: number of presented words.
        :return: Tuple of expression, target word and list of optional words (of length n_options)."""
        n_positive = np.random.randint(1, n_words + 1)
        positive = sample(self.config.vocabulary, n_positive)
        negative = sample(self.config.vocabulary, n_words - n_positive)
        top_similar = self.config.model.most_similar(positive=positive, negative=negative, topn=max(10, n_options))
        target = top_similar[0][0]
        all_words = [target] + [w for w, _ in top_similar[-n_options + 1:]]
        expr = ' + '.join(positive) + (' - ' if len(negative) else '') + ' - '.join(negative)
        np.random.shuffle(all_words)
        return expr, target, all_words
