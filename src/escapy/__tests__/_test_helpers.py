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

"""Shared test utilities for the escapy test suite."""

from collections.abc import Mapping

from ..events import Event, GameEndedEvent
from ..protocols import GameObject, GameProtocol
from ..types import Room


class FakeGame(GameProtocol):
    """Concrete implementation of GameProtocol used in unit tests.

    Provides fully populated game state so command functions can freely
    read ``objects`` (indexed by id, like :class:`~escapy.game.Game`) and
    read and mutate ``rooms``, ``inventory``, ``current_room_id``, and
    ``in_hand_object_id``.  The ``interact``,
    ``interact_inventory``, and ``insert_code`` methods are no-op stubs —
    tests that exercise game-level routing use the real ``Game`` class.
    """

    def __init__(
        self,
        objects: list[GameObject] | None = None,
        rooms: dict[str, Room] | None = None,
        current_room_id: str = "room1",
        inventory: list[str] | None = None,
        in_hand_object_id: str | None = None,
    ):
        self.objects: Mapping[str, GameObject] = {obj.id: obj for obj in objects or []}
        self.rooms: dict[str, Room] = rooms or {"room1": {}}
        self.current_room_id: str = current_room_id
        self.is_finished: bool = False
        self.inventory: list[str] = inventory or []
        self.in_hand_object_id: str | None = in_hand_object_id

    def quit(self) -> list[Event]:
        self.is_finished = True
        return [GameEndedEvent()]

    def interact(self, object_id: str) -> list[Event]:
        return []

    def interact_inventory(self, object_id: str | None) -> list[Event]:
        return []

    def insert_code(self, object_id: str, code: str) -> list[Event]:
        return []
