from typing import Literal, Protocol
from collections.abc import Callable

class Object(Protocol):
    width: float
    height: float

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def interact(self, in_hand_object_id: str | None = None) -> str | None:
        ...
    
 
class PickableObject(Object):
    def __init__(self, width: float, height: float):
        super().__init__(width, height)

    def interact(self, in_hand_object_id: str | None = None) -> str | None:
        return "picked"


def reveal_object(object_id: str, object: Object, position: tuple[float, float]):
    return lambda: ("revealed", (object_id, (object, position)))

class Lock(Protocol):
    def unlock(self, key_id: str) -> bool:
        ...

class KeyLock(Lock):
    def __init__(self, key_id: str):
        self.key_id = key_id

    def unlock(self, key_id: str) -> bool:
        return key_id == self.key_id

class SimpleLock(Lock):
    def unlock(self, key_id: str) -> bool:
        return True

class Lockable(Object):
    state: Literal["locked", "unlocked"]

    def __init__(self, width: float, height: float, lock: Lock, on_unlock: Callable | None = None):
        super().__init__(width, height)
        self.state = "locked"
        self.lock = lock
        self.on_unlock = on_unlock

    def interact(self, in_hand_object_id: str | None = None) -> str | None:
        if self.state == "locked":
            if in_hand_object_id and self.lock.unlock(in_hand_object_id):
                self.state = "unlocked"
                if self.on_unlock:
                    return self.on_unlock()
                return "unlocked"
            return "locked"
        return None


class Room:
    def __init__(self, id: str, objects: dict[str, tuple[Object, tuple[float, float]]]):
        self.id = id
        self.objects = objects

    def interact(self, object_id: str, in_hand_object_id: str | None = None) -> str | None:
        object = self.objects[object_id]
        event = object[0].interact(in_hand_object_id)

        match event:
            case "picked":
                self.objects.pop(object_id)
            case ("revealed", (new_object_id, new_object)):
                self.objects[new_object_id] = new_object
                return "revealed"
            
        return event


class Game:
    def __init__(self):
        self.rooms = [Room(
                "room1",
                {
                    "a1-knife": (PickableObject(0.05, 0.05), (0.2, 0.2)),
                    "a2-poster": (Lockable(0.15, 0.25, KeyLock("a1-knife"), reveal_object("a2-key", PickableObject(0.03, 0.03), (0.75, 0.75))), (0.7, 0.7)),
                    "a3-chest": (Lockable(0.2, 0.15, KeyLock("a2-key")), (0.4, 0.4)),
                },
            )
        ]
        self.current_room = self.rooms[0]
        self.is_finished = False
        self.inventory: dict[str, Object] = {}

    def interact(self, object_id: str, in_hand_object_id: str | None = None) -> str | None:
        try:
            object, _location = self.current_room.objects[object_id]
        except KeyError:
            return None

        if in_hand_object_id and in_hand_object_id not in self.inventory:
            return None

        event = self.current_room.interact(object_id, in_hand_object_id)

        match event:
            case "picked":
                self.inventory[object_id] = object

        return event