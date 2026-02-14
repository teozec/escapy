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

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from .game_events import GameEvent

if TYPE_CHECKING:
    from .game import Game
    from .insert_code import InsertCodeFn
    from .interact import InteractFn


@runtime_checkable
class Interactable(Protocol):
    interact: InteractFn


@runtime_checkable
class InventoryInteractable(Protocol):
    interact_inventory: InteractFn


@runtime_checkable
class Placeable(Protocol):
    width: float
    height: float


@runtime_checkable
class Unlockable(Protocol):
    state: Literal["locked", "unlocked"] = "locked"
    on_unlock: "InteractFn"

    def unlock(self, game: "Game") -> list[GameEvent]: ...


@runtime_checkable
class Decodable(Protocol):
    insert_code: "InsertCodeFn"


GameProtocol = Interactable | InventoryInteractable | Placeable | Unlockable | Decodable
