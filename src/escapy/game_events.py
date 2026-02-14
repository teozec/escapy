from dataclasses import dataclass

from .game_types import Position


@dataclass
class PickedUpEvent:
    object_id: str


@dataclass
class PutInHandEvent:
    object_id: str


@dataclass
class PutOffHandEvent: ...


@dataclass
class InteractedWithLockedEvent:
    object_id: str


@dataclass
class UnlockedEvent:
    object_id: str


@dataclass
class RevealedEvent:
    object_id: str
    room_id: str
    position: Position


@dataclass
class MovedToRoomEvent:
    room_id: str


@dataclass
class AskedForCodeEvent:
    object_id: str


@dataclass
class WrongCodeEvent: ...


@dataclass
class InspectedEvent:
    object_id: str


@dataclass
class GameEndedEvent: ...


@dataclass
class AddedToInventoryEvent:
    object_id: str


GameEvent = (
    PickedUpEvent
    | PutInHandEvent
    | PutOffHandEvent
    | InteractedWithLockedEvent
    | UnlockedEvent
    | RevealedEvent
    | MovedToRoomEvent
    | AskedForCodeEvent
    | WrongCodeEvent
    | InspectedEvent
    | GameEndedEvent
    | AddedToInventoryEvent
)
