# Copyright (C) 2026 Matteo Zeccoli Marazzini
#
# This file is part of escapy.
#
# escapy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# escapy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with escapy. If not, see <https://www.gnu.org/licenses/>.

from typing import TYPE_CHECKING, Callable

from .game_events import (
    AddedToInventoryEvent,
    AskedForCodeEvent,
    GameEvent,
    InspectedEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    RevealedEvent,
    UnlockedEvent,
)
from .game_types import Position
from .mixins import Unlockable

if TYPE_CHECKING:
    from .game import Game

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
        if isinstance(obj, Unlockable) and obj.state == "locked" and game.in_hand_object_id == key_id:
            return [UnlockedEvent(object_id=id)]
        return []

    return unlock


def ask_for_code(id: str) -> InteractFn:
    return lambda _game: [AskedForCodeEvent(object_id=id)]


def locked(id: str) -> InteractFn:
    return lambda _game: [InteractedWithLockedEvent(object_id=id)]


def inspect(id: str) -> InteractFn:
    return lambda _game: [InspectedEvent(object_id=id)]


def combine(*fns: InteractFn) -> InteractFn:
    def combined(game: Game) -> list[GameEvent]:
        events: list[GameEvent] = []
        for fn in fns:
            events.extend(fn(game))
        return events

    return combined


def cond(*clauses: tuple[Callable[[], bool], InteractFn]) -> InteractFn:
    def conditional(game: Game) -> list[GameEvent]:
        for condition, fn in clauses:
            if condition():
                return fn(game)
        return []

    return conditional


def chain(*clauses: tuple[Callable[[list[GameEvent]], bool], InteractFn]) -> InteractFn:
    """Like combine, but allows conditional execution based on previously emitted events.

    Args:
        *clauses: Tuple of (condition, InteractFn) where condition receives the list of events emitted so far.

    Example:
        chain(
            (lambda _: True, key_lock(id, key_id)),
            (lambda events: not any(isinstance(e, UnlockedEvent) for e in events), locked(id))
        )
    """

    def chained(game: Game) -> list[GameEvent]:
        events: list[GameEvent] = []
        for clause in clauses:
            condition, fn = clause
            if condition(events):
                events.extend(fn(game))
        return events

    return chained


def reveal(object_id: str, room_id: str, position: Position) -> InteractFn:
    return lambda _game: [RevealedEvent(object_id=object_id, room_id=room_id, position=position)]


def move_to_room(room_id: str) -> InteractFn:
    return lambda _game: [MovedToRoomEvent(room_id=room_id)]


def add_to_inventory(object_id: str) -> InteractFn:
    return lambda _game: [AddedToInventoryEvent(object_id=object_id)]
