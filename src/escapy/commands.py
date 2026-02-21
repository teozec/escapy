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

from typing import Callable

from .game import Game
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

Command = Callable[[Game], list[GameEvent]]


def no_op() -> Command:
    return lambda _game: []


def pick(id: str) -> Command:
    def f(game: Game) -> list[GameEvent]:
        del game.rooms[game.current_room_id][id]
        game.inventory.append(id)
        return [PickedUpEvent(object_id=id)]

    return f


def put_in_hand(id: str) -> Command:
    def f(game: Game) -> list[GameEvent]:
        game.in_hand_object_id = id
        return [PutInHandEvent(object_id=id)]

    return f


def simple_lock(id: str) -> Command:
    def unlock(game: Game) -> list[GameEvent]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked":
            return [UnlockedEvent(object_id=id)] + obj.unlock(game)
        return []

    return unlock


def key_lock(id: str, key_id: str) -> Command:
    def unlock(game: Game) -> list[GameEvent]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked" and game.in_hand_object_id == key_id:
            return [UnlockedEvent(object_id=id)] + obj.unlock(game)
        return []

    return unlock


def ask_for_code(id: str) -> Command:
    return lambda _game: [AskedForCodeEvent(object_id=id)]


def locked(id: str) -> Command:
    return lambda _game: [InteractedWithLockedEvent(object_id=id)]


def inspect(id: str) -> Command:
    return lambda _game: [InspectedEvent(object_id=id)]


def reveal(object_id: str, room_id: str, position: Position) -> Command:
    def f(game: Game) -> list[GameEvent]:
        game.rooms[room_id][object_id] = position
        return [RevealedEvent(object_id=object_id, room_id=room_id, position=position)]

    return f


def move_to_room(room_id: str) -> Command:
    def f(game: Game) -> list[GameEvent]:
        game.current_room_id = room_id
        return [MovedToRoomEvent(room_id=room_id)]

    return f


def add_to_inventory(object_id: str) -> Command:
    def f(game: Game) -> list[GameEvent]:
        game.inventory.append(object_id)
        return [AddedToInventoryEvent(object_id=object_id)]

    return f


def combine(*fns: Command) -> Command:
    def combined(game: Game) -> list[GameEvent]:
        events: list[GameEvent] = []
        for fn in fns:
            events.extend(fn(game))
        return events

    return combined


def cond(*clauses: tuple[Callable[[], bool], Command]) -> Command:
    def conditional(game: Game) -> list[GameEvent]:
        for condition, fn in clauses:
            if condition():
                return fn(game)
        return []

    return conditional


def chain(*clauses: tuple[Callable[[list[GameEvent]], bool], Command]) -> Command:
    """Like combine, but allows conditional execution based on previously emitted events.

    Args:
        *clauses: Tuple of (condition, Command) where condition receives the list of events emitted so far.

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
