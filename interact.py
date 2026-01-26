from typing import TYPE_CHECKING, Callable

from game_events import (
    GameEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    RevealedEvent,
    UnlockedEvent,
)
from game_types import Position
from mixins import Unlockable

if TYPE_CHECKING:
    from game import Game

InteractFn = Callable[["Game"], list[GameEvent]]


def no_op() -> InteractFn:
    return lambda _game: []


def pick(id: str) -> InteractFn:
    return lambda _game: [PickedUpEvent(object_id=id)]


def put_in_hand(id: str) -> InteractFn:
    return lambda _game: [PutInHandEvent(object_id=id)]


def simple_lock(id: str) -> InteractFn:
    def unlock(game: Game) -> list[GameEvent]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked":
            return [UnlockedEvent(object_id=id)]
        return []

    return unlock


def key_lock(id: str, key_id: str) -> InteractFn:
    def unlock(game: Game) -> list[GameEvent]:
        obj = game.objects[id]
        if (
            isinstance(obj, Unlockable)
            and obj.state == "locked"
            and game.in_hand_object_id == key_id
        ):
            return [UnlockedEvent(object_id=id)]
        return []

    return unlock


def locked(id: str) -> InteractFn:
    def interact(game: Game) -> list[GameEvent]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked":
            return [InteractedWithLockedEvent(object_id=id)]
        return []

    return interact


def combine(*fns: InteractFn) -> InteractFn:
    def combined(game: Game) -> list[GameEvent]:
        events: list[GameEvent] = []
        for fn in fns:
            events.extend(fn(game))
        return events

    return combined


def reveal(object_id: str, room_id: str, position: Position) -> InteractFn:
    return lambda _game: [
        RevealedEvent(object_id=object_id, room_id=room_id, position=position)
    ]


def move_to_room(room_id: str) -> InteractFn:
    return lambda _game: [MovedToRoomEvent(room_id=room_id)]
