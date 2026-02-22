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

from .commands import (
    Command,
    add_to_inventory,
    ask_for_code,
    chain,
    combine,
    cond,
    inspect,
    key_lock,
    locked,
    move_to_room,
    pick,
    put_in_hand,
    simple_lock,
)
from .events import UnlockedEvent
from .mixins import DecodableMixin, UnlockableMixin
from .protocols import Decodable, Interactable, InventoryInteractable, Placeable, Unlockable


class PickableObject(Interactable, InventoryInteractable, Placeable):
    """An object that can be picked up from a room and held in-hand.

    Clicking the object in the room picks it up (removes it from the room
    and adds it to inventory).  Clicking it in the inventory puts it
    in-hand.

    Args:
        id: Unique object identifier.
        width: Normalised width (fraction of the game area).
        height: Normalised height (fraction of the game area).
    """

    def __init__(
        self,
        id: str,
        width: float,
        height: float,
    ):
        self.interact = pick(id)
        self.interact_inventory = put_in_hand(id)
        self.width = width
        self.height = height


class SelfSimpleLock(UnlockableMixin, Interactable, Unlockable, Placeable):
    """A lock that can be opened with a simple click (no key required).

    Args:
        id: Unique object identifier.
        on_unlock: Command to execute when the lock is opened.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, on_unlock: Command, width: float, height: float):
        self.interact = simple_lock(id)
        self.state = "locked"
        self.on_unlock = on_unlock
        self.width = width
        self.height = height


class SelfKeyLock(UnlockableMixin, Interactable, Unlockable, Placeable):
    """A lock that requires a specific key held in-hand to open.

    If the player interacts without the correct key, an
    :class:`~escapy.events.InteractedWithLockedEvent` is emitted instead.

    Args:
        id: Unique object identifier.
        key_id: Identifier of the key object that opens this lock.
        on_unlock: Command to execute when the lock is opened.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, key_id: str, on_unlock: Command, width: float, height: float):
        self.interact = chain(
            (lambda _events: True, key_lock(id, key_id=key_id)),
            (
                lambda events: (
                    self.state == "locked"
                    and not any(isinstance(e, UnlockedEvent) and e.object_id == id for e in events)
                ),
                locked(id),
            ),
        )
        self.state = "locked"
        self.on_unlock = on_unlock
        self.width = width
        self.height = height


class SelfAskCodeLock(UnlockableMixin, DecodableMixin, Interactable, Unlockable, Decodable, Placeable):
    """A lock that prompts the player to enter a numeric/text code.

    When locked, interaction triggers an
    :class:`~escapy.events.AskedForCodeEvent`.  If the submitted code
    matches, the lock opens and ``on_unlock`` fires.

    Args:
        id: Unique object identifier.
        on_unlock: Command to execute when decoded.
        code: The correct code string.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, on_unlock: Command, code: str, width: float, height: float):
        self.interact = cond((lambda: self.state == "locked", ask_for_code(id)))
        self.state = "locked"
        self.on_unlock = on_unlock
        self.code = code
        self.on_decode = lambda game: self.unlock()(game)
        self.width = width
        self.height = height


class MoveToRoom(Interactable, Placeable):
    """A clickable area that transports the player to another room.

    Args:
        room_id: Destination room identifier.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, room_id: str, width: float, height: float):
        self.interact = move_to_room(room_id)
        self.width = width
        self.height = height


class WinMachine(DecodableMixin, InventoryInteractable, Decodable, Placeable):
    """A special object that ends (wins) the game when the correct code is entered.

    Interacting with it from the inventory triggers a code prompt.  A
    correct code moves the player to the designated win room.

    Args:
        id: Unique object identifier.
        code: The winning code string.
        win_room_id: Room to transition to upon success.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, code: str, win_room_id: str, width: float, height: float):
        self.interact_inventory = ask_for_code(id)
        self.code = code
        self.on_decode = move_to_room(win_room_id)
        self.width = width
        self.height = height


class InspectableObject(Interactable, Placeable):
    """An object that can be inspected (zoomed-in view) when clicked.

    Args:
        id: Unique object identifier.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, width: float, height: float):
        self.interact = inspect(id)
        self.width = width
        self.height = height


class PickableInspectableObject(Interactable, InventoryInteractable, Placeable):
    """An object that can be picked up from a room and inspected from the inventory.

    Args:
        id: Unique object identifier.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, width: float, height: float):
        self.interact = pick(id)
        self.interact_inventory = inspect(id)
        self.width = width
        self.height = height


class MoveToRoomAndAddToInventoryObject(Interactable, Placeable):
    """A clickable area that moves the player to another room and adds an object to the inventory.

    Args:
        room_id: Destination room identifier.
        object_id: Object to add to the inventory on interaction.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, room_id: str, object_id: str, width: float, height: float):
        self.interact = combine(move_to_room(room_id), add_to_inventory(object_id))
        self.width = width
        self.height = height
