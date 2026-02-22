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

"""Event types emitted by commands and consumed by the UI layer.

Every player action or game state change is represented as an immutable
event dataclass.  Commands return lists of events, and the UI layer
reacts to them (e.g. showing a message, switching to code-input mode,
or ending the game).
"""

from dataclasses import dataclass

from .types import Position


@dataclass
class PickedUpEvent:
    """An object was removed from the room and added to the inventory."""

    #: Identifier of the picked-up object.
    object_id: str


@dataclass
class PutInHandEvent:
    """The player selected an inventory object as the active hand item."""

    #: Identifier of the object now held in-hand.
    object_id: str


@dataclass
class PutOffHandEvent:
    """The player deselected the active hand item (hand is now empty)."""

    ...


@dataclass
class InteractedWithLockedEvent:
    """The player tried to interact with a locked object without the right key."""

    #: Identifier of the locked object.
    object_id: str


@dataclass
class UnlockedEvent:
    """A locked object was successfully unlocked."""

    #: Identifier of the now-unlocked object.
    object_id: str


@dataclass
class RevealedEvent:
    """A hidden object was revealed and placed into a room."""

    #: Identifier of the revealed object.
    object_id: str
    #: Room where the object was placed.
    room_id: str
    #: Position of the newly placed object.
    position: Position


@dataclass
class MovedToRoomEvent:
    """The active room changed."""

    #: Identifier of the new current room.
    room_id: str


@dataclass
class AskedForCodeEvent:
    """The UI should prompt the player to enter a code."""

    #: Identifier of the object awaiting the code.
    object_id: str


@dataclass
class WrongCodeEvent:
    """The player entered an incorrect code."""

    ...


@dataclass
class InspectedEvent:
    """The player inspected an object (e.g. zoomed in on it)."""

    #: Identifier of the inspected object.
    object_id: str


@dataclass
class GameEndedEvent:
    """The game has ended (player quit or won)."""

    ...


@dataclass
class AddedToInventoryEvent:
    """An object was added to the player's inventory without being picked up from the room."""

    #: Identifier of the added object.
    object_id: str


type Event = (
    PickedUpEvent
    | PutInHandEvent
    | PutOffHandEvent
    | InteractedWithLockedEvent
    | UnlockedEvent
    | RevealedEvent
    | MovedToRoomEvent
    | AskedForCodeEvent
    | WrongCodeEvent
    | InspectedEvent
    | GameEndedEvent
    | AddedToInventoryEvent
)
"""Union of all event types that can be emitted during gameplay."""
