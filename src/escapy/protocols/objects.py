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

"""Protocol definitions for game-object capabilities.

Each protocol represents a single capability (interacting, being placed,
being unlocked, etc.) and may be composed via multiple inheritance.
"""

from typing import Literal, Protocol, runtime_checkable

from .game import Command


@runtime_checkable
class Interactable(Protocol):
    """An object that can be interacted with when clicked in a room.

    Attributes:
        interact: Command executed on interaction.
    """

    interact: Command


@runtime_checkable
class InventoryInteractable(Protocol):
    """An object that can be interacted with from the inventory panel.

    Attributes:
        interact_inventory: Command executed on inventory interaction.
    """

    interact_inventory: Command


@runtime_checkable
class Placeable(Protocol):
    """An object that occupies visual space in the game area.

    Dimensions are expressed as normalised fractions of the game area
    (same coordinate system as :class:`~escapy.types.Position`).

    Attributes:
        width: Normalised width.
        height: Normalised height.
    """

    width: float
    height: float


@runtime_checkable
class Unlockable(Protocol):
    """An object that has a locked/unlocked state.

    Attributes:
        state: Current lock state.
        on_unlock: Command to execute when unlocked.
    """

    state: Literal["locked", "unlocked"] = "locked"
    on_unlock: Command

    def unlock(self) -> Command:
        """Transition the object to the unlocked state and return ``on_unlock``."""
        ...


@runtime_checkable
class Decodable(Protocol):
    """An object that can be decoded with a text/numeric code.

    Attributes:
        code: The correct code string.
        on_decode: Command to execute on a correct code.
    """

    code: str
    on_decode: Command

    def insert_code(self, code: str) -> Command:
        """Validate *code* and return the appropriate command."""
        ...
