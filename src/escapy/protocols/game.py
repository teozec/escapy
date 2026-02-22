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

from typing import Callable, Protocol

from ..events import Event
from ..types import Room


class GameProtocol(Protocol):
    objects: dict[str, object]
    rooms: dict[str, Room]
    current_room_id: str
    is_finished: bool
    inventory: list[str]
    in_hand_object_id: str | None

    def quit(self) -> list[Event]: ...

    def interact(self, object_id: str) -> list[Event]: ...

    def interact_inventory(self, object_id: str | None) -> list[Event]: ...

    def insert_code(self, object_id: str, code: str) -> list[Event]: ...


type Command = Callable[[GameProtocol], list[Event]]
