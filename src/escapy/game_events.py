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

from dataclasses import dataclass

from .game_types import Position


@dataclass
class PickedUpEvent:
    object_id: str


@dataclass
class PutInHandEvent:
    object_id: str


@dataclass
class PutOffHandEvent: ...


@dataclass
class InteractedWithLockedEvent:
    object_id: str


@dataclass
class UnlockedEvent:
    object_id: str


@dataclass
class RevealedEvent:
    object_id: str
    room_id: str
    position: Position


@dataclass
class MovedToRoomEvent:
    room_id: str


@dataclass
class AskedForCodeEvent:
    object_id: str


@dataclass
class WrongCodeEvent: ...


@dataclass
class InspectedEvent:
    object_id: str


@dataclass
class GameEndedEvent: ...


@dataclass
class AddedToInventoryEvent:
    object_id: str


GameEvent = (
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
