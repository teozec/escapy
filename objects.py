from insert_code import code_lock
from interact import (
    InteractFn,
    ask_for_code,
    combine,
    cond,
    locked,
    move_to_room,
    pick,
    put_in_hand,
    key_lock,
    simple_lock,
)
from mixins import UnlockableMixin
from protocols import (
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
        self.interact = combine(simple_lock(id), locked(id))
        self.state = "locked"
        self.on_unlock = on_unlock
        self.width = width
        self.height = height


class SelfKeyLock(UnlockableMixin, Interactable, Unlockable, Placeable):
    def __init__(
        self, id: str, key_id: str, on_unlock: InteractFn, width: float, height: float
    ):
        self.interact = combine(key_lock(id, key_id=key_id), locked(id))
        self.state = "locked"
        self.on_unlock = on_unlock
        self.width = width
        self.height = height


class SelfAskCodeLock(UnlockableMixin, Interactable, Unlockable, Decodable, Placeable):
    def __init__(
        self, id: str, on_unlock: InteractFn, code: str, width: float, height: float
    ):
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
