from .game_events import (
    AddedToInventoryEvent,
    AskedForCodeEvent,
    GameEndedEvent,
    GameEvent,
    InspectedEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    PutOffHandEvent,
    RevealedEvent,
    UnlockedEvent,
    WrongCodeEvent,
)
from .game_types import Position
from .protocols import (
    Decodable,
    Interactable,
    InventoryInteractable,
    Unlockable,
)

Room = dict[str, Position]


class Game:
    def __init__(
        self,
        objects: dict[str, object],
        rooms: dict[str, Room],
        inventory: list[str],
        first_room_id: str,
    ):
        self.objects = objects
        self.rooms = rooms
        self.current_room_id = first_room_id
        self.is_finished = False
        self.inventory = inventory
        self.in_hand_object_id: str | None = None

    def quit(self) -> list[GameEvent]:
        events: list[GameEvent] = [GameEndedEvent()]
        for event in events:
            events.extend(self._handle_event(event))
        return events

    def interact(self, object_id: str) -> list[GameEvent]:
        if object_id not in self.rooms[self.current_room_id]:
            return []

        object = self.objects[object_id]

        if not isinstance(object, Interactable):
            return []
        events = object.interact(self)

        for event in events:
            events.extend(self._handle_event(event))

        return events

    def interact_inventory(self, object_id: str | None) -> list[GameEvent]:
        events: list[GameEvent]
        if object_id is None:
            events = [PutOffHandEvent()]
        elif object_id not in self.inventory:
            return []
        else:
            object = self.objects[object_id]
            if not isinstance(object, InventoryInteractable):
                return []
            events = object.interact_inventory(self)

        for event in events:
            events.extend(self._handle_event(event))

        return events

    def insert_code(self, object_id: str, code: str) -> list[GameEvent]:
        object = self.objects[object_id]
        if not isinstance(object, Decodable):
            return []

        events = object.insert_code(code)

        for event in events:
            events.extend(self._handle_event(event))

        return events

    def _handle_event(self, event: GameEvent) -> list[GameEvent]:
        match event:
            case PickedUpEvent(object_id=picked_id):
                del self.rooms[self.current_room_id][picked_id]
                self.inventory.append(picked_id)
                return []
            case PutInHandEvent(object_id=id):
                self.in_hand_object_id = id
                return []
            case PutOffHandEvent():
                self.in_hand_object_id = None
                return []
            case InteractedWithLockedEvent(object_id=id):
                return []
            case UnlockedEvent(object_id=id):
                obj = self.objects[id]
                if isinstance(obj, Unlockable):
                    return obj.unlock(self)
                else:
                    raise ValueError(f"Object {id} is not unlockable")
            case RevealedEvent(object_id=id, room_id=room_id, position=position):
                self.rooms[room_id][id] = position
                return []
            case MovedToRoomEvent(room_id=room_id):
                self.current_room_id = room_id
                return []
            case AskedForCodeEvent(object_id=id):
                return []
            case WrongCodeEvent():
                return []
            case InspectedEvent(object_id=id):
                return []
            case GameEndedEvent():
                self.is_finished = True
                return []
            case AddedToInventoryEvent(object_id=id):
                self.inventory.append(id)
                return []
