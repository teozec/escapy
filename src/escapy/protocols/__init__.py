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

"""Protocol (structural typing) interfaces for escapy.

This subpackage defines the abstract contracts that the game engine,
game objects, and UI implementations must satisfy.  Using
:class:`typing.Protocol` allows duck-typed interoperability without
forcing concrete inheritance.
"""

from .game import Command, GameProtocol
from .objects import Decodable, Interactable, InventoryInteractable, Placeable, Unlockable
from .ui import GameUiProtocol

__all__ = [
    "Command",
    "GameProtocol",
    "Decodable",
    "Interactable",
    "InventoryInteractable",
    "Placeable",
    "Unlockable",
    "GameUiProtocol",
]
