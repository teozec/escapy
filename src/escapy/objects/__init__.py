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

"""Ready-made game-object classes for common escape-room mechanics.

Each class composes protocol implementations and mixin behaviour to
provide a complete, reusable game object that can be placed in rooms,
interacted with, and managed by the inventory system.
"""

from .objects import (
    InspectableObject,
    MoveToRoom,
    MoveToRoomAndAddToInventoryObject,
    PickableInspectableObject,
    PickableObject,
    SelfAskCodeLock,
    SelfKeyLock,
    SelfSimpleLock,
    WinMachine,
)

__all__ = [
    "InspectableObject",
    "MoveToRoom",
    "MoveToRoomAndAddToInventoryObject",
    "PickableInspectableObject",
    "PickableObject",
    "SelfAskCodeLock",
    "SelfKeyLock",
    "SelfSimpleLock",
    "WinMachine",
]
