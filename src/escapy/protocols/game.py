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

"""Game-engine protocol and the Command type alias."""

from typing import Any, Callable, Protocol

from ..events import Event
from ..types import Room


class GameProtocol(Protocol):
    """Structural interface that every game-engine implementation must satisfy.

    Attributes:
        objects: Mapping of object IDs to their game-object instances.
        rooms: Mapping of room IDs to :data:`~escapy.types.Room` dicts.
        current_room_id: ID of the room currently displayed.
        is_finished: ``True`` after the game has ended.
        inventory: Ordered list of object IDs the player is carrying.
        in_hand_object_id: ID of the object currently held, or ``None``.
    """

    objects: dict[str, Any]
    rooms: dict[str, Room]
    current_room_id: str
    is_finished: bool
    inventory: list[str]
    in_hand_object_id: str | None

    def quit(self) -> list[Event]:
        """End the game."""
        ...

    def interact(self, object_id: str) -> list[Event]:
        """Interact with an object in the current room."""
        ...

    def interact_inventory(self, object_id: str | None) -> list[Event]:
        """Interact with an inventory object or clear the hand."""
        ...

    def insert_code(self, object_id: str, code: str) -> list[Event]:
        """Submit a code to a decodable object."""
        ...


type Command = Callable[[GameProtocol], list[Event]]
"""A callable that mutates game state and returns the resulting events."""
