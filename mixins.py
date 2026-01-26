from game import Game
from game_events import GameEvent
from protocols import Unlockable


class UnlockableMixin:
    def unlock(self: Unlockable, game: Game) -> list[GameEvent]:
        self.state = "unlocked"
        return self.on_unlock(game)


GameMixins = UnlockableMixin
