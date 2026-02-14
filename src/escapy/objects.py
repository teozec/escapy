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

from .insert_code import code_lock
from .interact import (
    InteractFn,
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
from .mixins import UnlockableMixin
from .protocols import (
    Decodable,
    Interactable,
    InventoryInteractable,
    Placeable,
    Unlockable,
)


class PickableObject(Interactable, InventoryInteractable, Placeable):
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
    def __init__(self, id: str, on_unlock: InteractFn, width: float, height: float):
        from game_events import UnlockedEvent

        self.interact = chain(
            (lambda _events: True, simple_lock(id)),
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


class SelfKeyLock(UnlockableMixin, Interactable, Unlockable, Placeable):
    def __init__(self, id: str, key_id: str, on_unlock: InteractFn, width: float, height: float):
        from game_events import UnlockedEvent

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


class SelfAskCodeLock(UnlockableMixin, Interactable, Unlockable, Decodable, Placeable):
    def __init__(self, id: str, on_unlock: InteractFn, code: str, width: float, height: float):
        self.interact = cond((lambda: self.state == "locked", ask_for_code(id)))
        self.state = "locked"
        self.on_unlock = on_unlock
        self.insert_code = code_lock(id, expected_code=code)
        self.width = width
        self.height = height


class MoveToRoom(Interactable, Placeable):
    def __init__(self, room_id: str, width: float, height: float):
        self.interact = move_to_room(room_id)
        self.width = width
        self.height = height


class WinMachine(UnlockableMixin, InventoryInteractable, Decodable, Placeable):
    def __init__(self, id: str, code: str, win_room_id: str, width: float, height: float):
        self.interact_inventory = ask_for_code(id)
        self.insert_code = code_lock(id, expected_code=code)
        self.on_unlock = move_to_room(win_room_id)
        self.state = "locked"
        self.width = width
        self.height = height


class InspectableObject(Interactable, Placeable):
    def __init__(self, id: str, width: float, height: float):
        self.interact = inspect(id)
        self.width = width
        self.height = height


class PickableInspectableObject(Interactable, InventoryInteractable, Placeable):
    def __init__(self, id: str, width: float, height: float):
        self.interact = pick(id)
        self.interact_inventory = inspect(id)
        self.width = width
        self.height = height


class MoveToRoomAndAddToInventoryObject(Interactable, Placeable):
    def __init__(self, room_id: str, object_id: str, width: float, height: float):
        self.interact = combine(move_to_room(room_id), add_to_inventory(object_id))
        self.width = width
        self.height = height
