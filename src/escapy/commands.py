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

"""Command factory functions that drive game-state mutations.

A *command* is a callable ``(GameProtocol) -> list[Event]``.  Each factory
function in this module returns a command that performs a single, composable
action — for example picking up an object, unlocking a lock, or moving the
player to another room.  Higher-order combinators such as :func:`combine`,
:func:`cond`, and :func:`chain` allow commands to be composed.
"""

from typing import Callable

from .events import (
    AddedToInventoryEvent,
    AskedForCodeEvent,
    Event,
    InspectedEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    RevealedEvent,
    UnlockedEvent,
)
from .mixins import Unlockable
from .protocols import Command, GameProtocol
from .types import Position


def no_op() -> Command:
    """Return a command that does nothing and emits no events."""
    return lambda _game: []


def pick(id: str) -> Command:
    """Return a command that picks up an object from the current room.

    The object is removed from the room and added to the player's inventory.

    Args:
        id: Identifier of the object to pick up.

    Returns:
        A command that emits a :class:`~escapy.events.PickedUpEvent`.
    """

    def f(game: GameProtocol) -> list[Event]:
        del game.rooms[game.current_room_id][id]
        game.inventory.append(id)
        return [PickedUpEvent(object_id=id)]

    return f


def put_in_hand(id: str) -> Command:
    """Return a command that sets an object as the active hand item.

    Args:
        id: Identifier of the object to hold.

    Returns:
        A command that emits a :class:`~escapy.events.PutInHandEvent`.
    """

    def f(game: GameProtocol) -> list[Event]:
        game.in_hand_object_id = id
        return [PutInHandEvent(object_id=id)]

    return f


def simple_lock(id: str) -> Command:
    """Return a command that unlocks a locked object unconditionally.

    If the object implements :class:`~escapy.protocols.Unlockable` and its
    state is ``"locked"``, it will be unlocked and its ``on_unlock`` command
    will be executed.

    Args:
        id: Identifier of the lockable object.

    Returns:
        A command that emits an :class:`~escapy.events.UnlockedEvent`
        followed by the events from the object's ``on_unlock`` command,
        or an empty list if the object is already unlocked.
    """

    def unlock(game: GameProtocol) -> list[Event]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked":
            return [UnlockedEvent(object_id=id)] + obj.unlock()(game)
        return []

    return unlock


def key_lock(id: str, key_id: str) -> Command:
    """Return a command that unlocks a locked object only if the player holds the right key.

    The object is unlocked when:

    * it implements :class:`~escapy.protocols.Unlockable`,
    * its state is ``"locked"``, **and**
    * ``game.in_hand_object_id`` matches *key_id*.

    Args:
        id: Identifier of the lockable object.
        key_id: Identifier of the required key object.

    Returns:
        A command that emits an :class:`~escapy.events.UnlockedEvent` (plus
        the ``on_unlock`` follow-up events), or an empty list on failure.
    """

    def unlock(game: GameProtocol) -> list[Event]:
        obj = game.objects[id]
        if isinstance(obj, Unlockable) and obj.state == "locked" and game.in_hand_object_id == key_id:
            return [UnlockedEvent(object_id=id)] + obj.unlock()(game)
        return []

    return unlock


def ask_for_code(id: str) -> Command:
    """Return a command that requests the UI to prompt the player for a code.

    Args:
        id: Identifier of the object awaiting the code.

    Returns:
        A command that emits an :class:`~escapy.events.AskedForCodeEvent`.
    """
    return lambda _game: [AskedForCodeEvent(object_id=id)]


def locked(id: str) -> Command:
    """Return a command that signals the player interacted with a locked object.

    Args:
        id: Identifier of the locked object.

    Returns:
        A command that emits an
        :class:`~escapy.events.InteractedWithLockedEvent`.
    """
    return lambda _game: [InteractedWithLockedEvent(object_id=id)]


def inspect(id: str) -> Command:
    """Return a command that inspects an object (e.g. zoom-in view).

    Args:
        id: Identifier of the object to inspect.

    Returns:
        A command that emits an :class:`~escapy.events.InspectedEvent`.
    """
    return lambda _game: [InspectedEvent(object_id=id)]


def reveal(object_id: str, room_id: str, position: Position) -> Command:
    """Return a command that reveals a hidden object by placing it in a room.

    Args:
        object_id: Identifier of the object to reveal.
        room_id: Room in which the object should appear.
        position: Position within the room.

    Returns:
        A command that emits a :class:`~escapy.events.RevealedEvent`.
    """

    def f(game: GameProtocol) -> list[Event]:
        game.rooms[room_id][object_id] = position
        return [RevealedEvent(object_id=object_id, room_id=room_id, position=position)]

    return f


def move_to_room(room_id: str) -> Command:
    """Return a command that changes the current room.

    Args:
        room_id: Identifier of the destination room.

    Returns:
        A command that emits a :class:`~escapy.events.MovedToRoomEvent`.
    """

    def f(game: GameProtocol) -> list[Event]:
        game.current_room_id = room_id
        return [MovedToRoomEvent(room_id=room_id)]

    return f


def add_to_inventory(object_id: str) -> Command:
    """Return a command that adds an object directly to the player's inventory.

    Unlike :func:`pick`, this does **not** remove the object from a room.

    Args:
        object_id: Identifier of the object to add.

    Returns:
        A command that emits an
        :class:`~escapy.events.AddedToInventoryEvent`.
    """

    def f(game: GameProtocol) -> list[Event]:
        game.inventory.append(object_id)
        return [AddedToInventoryEvent(object_id=object_id)]

    return f


def combine(*fns: Command) -> Command:
    """Return a command that executes multiple commands in sequence.

    All events are collected in order and returned as a single flat list.

    Args:
        *fns: Commands to execute sequentially.
    """

    def combined(game: GameProtocol) -> list[Event]:
        events: list[Event] = []
        for fn in fns:
            events.extend(fn(game))
        return events

    return combined


def cond(*clauses: tuple[Callable[[], bool], Command]) -> Command:
    """Return a command that executes the first clause whose condition is true.

    Clauses are evaluated in order.  Only the command of the **first**
    matching clause is executed; the rest are skipped.

    Args:
        *clauses: ``(condition, command)`` pairs.  *condition* is a
            zero-argument callable returning a bool.
    """

    def conditional(game: GameProtocol) -> list[Event]:
        for condition, fn in clauses:
            if condition():
                return fn(game)
        return []

    return conditional


def chain(*clauses: tuple[Callable[[list[Event]], bool], Command]) -> Command:
    """Like combine, but allows conditional execution based on previously emitted events.

    Args:
        *clauses: Tuple of ``(condition, Command)`` where *condition*
            receives the list of events emitted so far.

    Example::

        chain(
            (lambda _: True, key_lock(id, key_id)),
            (lambda events: not any(isinstance(e, UnlockedEvent) for e in events), locked(id)),
        )
    """

    def chained(game: GameProtocol) -> list[Event]:
        events: list[Event] = []
        for clause in clauses:
            condition, fn = clause
            if condition(events):
                events.extend(fn(game))
        return events

    return chained
