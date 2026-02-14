from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from .game_events import GameEvent

if TYPE_CHECKING:
    from .game import Game
    from .insert_code import InsertCodeFn
    from .interact import InteractFn


@runtime_checkable
class Interactable(Protocol):
    interact: InteractFn


@runtime_checkable
class InventoryInteractable(Protocol):
    interact_inventory: InteractFn


@runtime_checkable
class Placeable(Protocol):
    width: float
    height: float


@runtime_checkable
class Unlockable(Protocol):
    state: Literal["locked", "unlocked"] = "locked"
    on_unlock: "InteractFn"

    def unlock(self, game: "Game") -> list[GameEvent]: ...


@runtime_checkable
class Decodable(Protocol):
    insert_code: "InsertCodeFn"


GameProtocol = Interactable | InventoryInteractable | Placeable | Unlockable | Decodable
