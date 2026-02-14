from typing import Protocol

from .game import Game
from .game_events import GameEvent


class GameUi(Protocol):
    def init(self, game: Game) -> None: ...

    def tick(self) -> None: ...

    def input(self) -> list[GameEvent]: ...

    def handle(self, events: list[GameEvent]) -> None: ...

    def render(self) -> None: ...

    def quit(self) -> None: ...

    is_running: bool
