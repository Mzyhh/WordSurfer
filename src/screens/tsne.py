from sklearn.manifold import TSNE
import pandas as pd
import plotly.express as px
import os
import typing as t

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer, Static, Label, LoadingIndicator
from textual import work
from textual.worker import Worker, get_current_worker

from utils.get_resources import get_resource_file
from config import Config


class LoadTSNEScreen(Screen):

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id='loading-indicator-tsne')

    @work(thread=True)
    def load_tsne(self, perplexity=30) -> None:
        data_path = str(get_resource_file('data')) + '/'
        tsne_file = data_path + f'tsne_p{perplexity}.csv'
        if os.path.exists(tsne_file):
            df = pd.read_csv(tsne_file)
        else:
            tsne_embedding = TSNE(
                n_components=2,
                learning_rate='auto',
                perplexity=perplexity
            ).fit_transform(self.config.model.vectors)

            df = pd.DataFrame(tsne_embedding)
            df.insert(1, 'word', self.config.model.index_to_key)
            df.to_csv(tsne_file)
        self.app.call_from_thread(self.dismiss, df)

    def on_mount(self) -> None:
        self.load_tsne(50)


class TSNEScreen(Screen):

    BINDINGS = [('q', 'quit', 'Go to main menu')]

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.data: t.Optional[pd.DataFrame] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("Plot is shown in your browser.")
        yield Button("Show plot", id='plt-btn', disabled=True, )

    async def run_plot(self):
        if self.data is None:
            self.notify("No data available to plot", severity="error")
            return
        try:
            fig = px.scatter(
                self.data,
                x='0',
                y='1',
                hover_data=['word'])
            fig.show(renderer="browser")
        except Exception as e:
            self.notify(f"Failed to show plot: {e}", severity="error")
            self.log.error(f"Plotting error: {e}")

    @work
    async def load_data(self) -> None:
        worker = get_current_worker()
        self.data = await self.app.push_screen_wait(LoadTSNEScreen(self.config))
        if not worker.is_cancelled:
            self.query_one('#plt-btn', Button).disabled = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'plt-btn':
            if self.data is not None:
                await self.run_plot()
            else:
                self.notify('Data not loaded yet', severity='error')

    def on_mount(self) -> None:
        self.load_data()

