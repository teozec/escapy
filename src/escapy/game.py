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

from .game_events import (
    GameEndedEvent,
    GameEvent,
    PutOffHandEvent,
)
from .game_types import Position
from .protocols import (
    Decodable,
    Interactable,
    InventoryInteractable,
)

Room = dict[str, Position]


class Game:
    def __init__(
        self,
        objects: dict[str, object],
        rooms: dict[str, Room],
        inventory: list[str],
        first_room_id: str,
    ):
        self.objects = objects
        self.rooms = rooms
        self.current_room_id = first_room_id
        self.is_finished = False
        self.inventory = inventory
        self.in_hand_object_id: str | None = None

    def quit(self) -> list[GameEvent]:
        self.is_finished = True
        return [GameEndedEvent()]

    def interact(self, object_id: str) -> list[GameEvent]:
        if object_id not in self.rooms[self.current_room_id]:
            return []

        object = self.objects[object_id]

        if not isinstance(object, Interactable):
            return []
        return object.interact(self)

    def interact_inventory(self, object_id: str | None) -> list[GameEvent]:
        if object_id is None:
            self.in_hand_object_id = None
            return [PutOffHandEvent()]
        elif object_id not in self.inventory:
            return []
        else:
            object = self.objects[object_id]
            if not isinstance(object, InventoryInteractable):
                return []
            return object.interact_inventory(self)

    def insert_code(self, object_id: str, code: str) -> list[GameEvent]:
        object = self.objects[object_id]
        if not isinstance(object, Decodable):
            return []

        return object.insert_code(code, self)
