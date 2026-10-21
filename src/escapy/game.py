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

"""Core game engine that manages state and dispatches player actions."""

from collections import Counter
from collections.abc import Mapping
from types import MappingProxyType

from .events import (
    Event,
    GameEndedEvent,
    PutOffHandEvent,
)
from .protocols import Decodable, GameObject, GameProtocol, Interactable, InventoryInteractable
from .types import Room


class Game(GameProtocol):
    """Concrete implementation of :class:`~escapy.protocols.GameProtocol`.

    Holds the mutable game state (rooms, inventory, current room, etc.) and
    routes player actions to the appropriate object behaviours.

    Args:
        objects: All the game objects; they are indexed by their ``id``.
        rooms: Mapping of room IDs to :data:`~escapy.types.Room` dicts.
        inventory: Initial list of object IDs the player carries.
        first_room_id: ID of the room the game starts in.

    Raises:
        TypeError: If an object is not a :class:`~escapy.protocols.GameObject`
            or its ``id`` is not a string.
        ValueError: If an ``id`` is empty or used by more than one object.
    """

    def __init__(
        self,
        objects: list[GameObject],
        rooms: dict[str, Room],
        inventory: list[str],
        first_room_id: str,
    ):
        self.objects = _index_objects(objects)
        self.rooms = rooms
        self.current_room_id = first_room_id
        self.is_finished = False
        self.inventory = inventory
        self.in_hand_object_id: str | None = None

    def quit(self) -> list[Event]:
        """End the game and return a :class:`~escapy.events.GameEndedEvent`."""
        self.is_finished = True
        return [GameEndedEvent()]

    def interact(self, object_id: str) -> list[Event]:
        """Interact with an object in the current room.

        If the object is present in the current room and satisfies the
        :class:`~escapy.protocols.Interactable` protocol, its
        ``interact`` command is executed.

        Args:
            object_id: Identifier of the object to interact with.

        Returns:
            Events produced by the interaction, or an empty list.

        Raises:
            KeyError: If *object_id* is not a registered object.
        """
        if object_id not in self.objects:
            raise KeyError(f"Unknown object id: {object_id!r}")

        if object_id not in self.rooms[self.current_room_id]:
            return []

        object = self.objects[object_id]

        if not isinstance(object, Interactable):
            return []
        return object.interact(self)

    def interact_inventory(self, object_id: str | None) -> list[Event]:
        """Interact with an inventory object, or clear the hand.

        * If *object_id* is ``None``, the hand item is cleared and a
          :class:`~escapy.events.PutOffHandEvent` is emitted.
        * If the object is in the inventory and satisfies
          :class:`~escapy.protocols.InventoryInteractable`, its
          ``interact_inventory`` command is executed.

        Args:
            object_id: Inventory object ID, or ``None`` to deselect.

        Returns:
            Events produced by the interaction, or an empty list.

        Raises:
            KeyError: If *object_id* is not ``None`` and not a registered
                object.
        """
        if object_id is None:
            self.in_hand_object_id = None
            return [PutOffHandEvent()]
        if object_id not in self.objects:
            raise KeyError(f"Unknown object id: {object_id!r}")

        if object_id not in self.inventory:
            return []
        else:
            object = self.objects[object_id]
            if not isinstance(object, InventoryInteractable):
                return []
            return object.interact_inventory(self)

    def insert_code(self, object_id: str, code: str) -> list[Event]:
        """Submit a code to a :class:`~escapy.protocols.Decodable` object.

        Args:
            object_id: Identifier of the object to decode.
            code: The code string entered by the player.

        Returns:
            Events produced by the decode action, or an empty list if the
            object does not implement :class:`~escapy.protocols.Decodable`.

        Raises:
            KeyError: If *object_id* is not a registered object.
        """
        if object_id not in self.objects:
            raise KeyError(f"Unknown object id: {object_id!r}")

        object = self.objects[object_id]
        if not isinstance(object, Decodable):
            return []

        return object.insert_code(code)(self)


def _index_objects(objects: list[GameObject]) -> Mapping[str, GameObject]:
    """Index *objects* by id, checking that every id is a unique non-empty string.

    The result is a read-only view: the set of game objects is fixed after construction.
    """
    for index, object in enumerate(objects):
        if not isinstance(object, GameObject):
            raise TypeError(f"Object at index {index} ({type(object).__name__}) has no 'id' attribute")
        if not isinstance(object.id, str):
            raise TypeError(
                f"Object at index {index} ({type(object).__name__}) has an id of type "
                f"{type(object.id).__name__}, expected str"
            )
        if not object.id:
            raise ValueError(f"Object at index {index} ({type(object).__name__}) has an empty id")

    duplicates = [id for id, count in Counter(object.id for object in objects).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate object ids: {duplicates}")

    return MappingProxyType({object.id: object for object in objects})
