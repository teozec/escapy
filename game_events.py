from dataclasses import dataclass

from game_types import Position


@dataclass
class PickedUpEvent:
    object_id: str


@dataclass
class PutInHandEvent:
    object_id: str


@dataclass
class PutOffHandEvent:
    ...


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


GameEvent = (
    PickedUpEvent
    | PutInHandEvent
    | PutOffHandEvent
    | InteractedWithLockedEvent
    | UnlockedEvent
    | RevealedEvent
)
