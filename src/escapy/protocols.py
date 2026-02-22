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

from typing import Literal, Protocol, runtime_checkable

from .types import Command


@runtime_checkable
class Interactable(Protocol):
    interact: Command


@runtime_checkable
class InventoryInteractable(Protocol):
    interact_inventory: Command


@runtime_checkable
class Placeable(Protocol):
    width: float
    height: float


@runtime_checkable
class Unlockable(Protocol):
    state: Literal["locked", "unlocked"] = "locked"
    on_unlock: Command

    def unlock(self) -> Command: ...


@runtime_checkable
class Decodable(Protocol):
    code: str
    on_decode: Command

    def insert_code(self, code: str) -> Command: ...


type GameProtocol = Interactable | InventoryInteractable | Placeable | Unlockable | Decodable
