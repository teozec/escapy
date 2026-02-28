# Events

Events are immutable dataclass instances emitted by commands and consumed by the UI layer.  They describe **what happened** without prescribing how the UI should react.

All event types live in `escapy.events`.

## Event union type

```python
type Event = (
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
```

## Event reference

### `PickedUpEvent`

An object was removed from the room and added to the inventory.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the picked-up object |

### `PutInHandEvent`

The player selected an inventory object as the active hand item.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the object now held in-hand |

### `PutOffHandEvent`

The player deselected the active hand item (hand is now empty).  No fields.

### `InteractedWithLockedEvent`

The player tried to interact with a locked object without the right key.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the locked object |

### `UnlockedEvent`

A locked object was successfully unlocked.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the unlocked object |

### `RevealedEvent`

A hidden object was revealed and placed into a room.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the revealed object |
| `room_id` | `str` | Room where the object was placed |
| `position` | `Position` | Position of the newly placed object |

### `MovedToRoomEvent`

The active room changed.

| Field | Type | Description |
|---|---|---|
| `room_id` | `str` | Identifier of the new current room |

### `AskedForCodeEvent`

The UI should prompt the player to enter a code.

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the object awaiting the code |

### `WrongCodeEvent`

The player entered an incorrect code.  No fields.

### `InspectedEvent`

The player inspected an object (e.g. zoomed in on it).

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the inspected object |

### `GameEndedEvent`

The game has ended (player quit or won).  No fields.

### `AddedToInventoryEvent`

An object was added to the player's inventory directly (not picked up from a room).

| Field | Type | Description |
|---|---|---|
| `object_id` | `str` | Identifier of the added object |

## Using events with messages

To display human-readable text for events, use `dict_message_provider`:

```python
from escapy.messages import dict_message_provider
from escapy.events import PickedUpEvent

messages = {
    repr(PickedUpEvent("key")): "You found a rusty key!",
}
provider = dict_message_provider(messages)
```

The provider returns `None` for events without a matching entry, so unhandled events are silently ignored.
