from interact import (
    InteractFn,
    combine,
    locked,
    pick,
    put_in_hand,
    key_lock,
    simple_lock,
)
from mixins import UnlockableMixin
from protocols import Interactable, InventoryInteractable, Placeable, Unlockable


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
