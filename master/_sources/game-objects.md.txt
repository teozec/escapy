# Game Objects

escapy ships several ready-made game-object classes in `escapy.objects`.  Each class composes one or more protocols and mixins to provide a complete, reusable behaviour.

## Common parameters

All object classes accept **normalised dimensions** (`width`, `height`) expressed as fractions of the game area (e.g. `0.1` means 10 % of the game area).

## PickableObject

An object that can be **picked up** from a room and **held in-hand** from the inventory.

| Behaviour | Effect |
|---|---|
| Room click | Removes from room, adds to inventory (`PickedUpEvent`) |
| Inventory click | Sets as active hand item (`PutInHandEvent`) |

```python
knife = PickableObject("knife", width=0.05, height=0.05)
```

## SelfSimpleLock

A lock that opens with a **single click** (no key required).

| Behaviour | Effect |
|---|---|
| Room click (locked) | Unlocks and fires `on_unlock` command (`UnlockedEvent`) |
| Room click (unlocked) | Nothing |

```python
chest = SelfSimpleLock(
    id="chest",
    on_unlock=reveal("gem", "room1", Position(x=0.5, y=0.5)),
    width=0.2,
    height=0.15,
)
```

## SelfKeyLock

A lock that requires a **specific key** to be held in-hand.

| Behaviour | Effect |
|---|---|
| Room click (locked, correct key in-hand) | Unlocks (`UnlockedEvent` + `on_unlock`) |
| Room click (locked, wrong/no key) | `InteractedWithLockedEvent` |
| Room click (unlocked) | Nothing |

```python
door = SelfKeyLock(
    id="door",
    key_id="gold_key",
    on_unlock=no_op(),
    width=0.15,
    height=0.3,
)
```

## SelfAskCodeLock

A lock that prompts the player to **enter a code**.

| Behaviour | Effect |
|---|---|
| Room click (locked) | `AskedForCodeEvent` → code prompt overlay |
| Code correct | Unlocks (`UnlockedEvent` + `on_unlock`) |
| Code wrong | `WrongCodeEvent` |
| Room click (unlocked) | Nothing |

```python
safe = SelfAskCodeLock(
    id="safe",
    on_unlock=reveal("diamond", "room1", Position(x=0.3, y=0.3)),
    code="1234",
    width=0.2,
    height=0.2,
)
```

## MoveToRoom

A clickable hotspot that **transports the player** to another room.

```python
door = MoveToRoom(room_id="hallway", width=0.1, height=0.2)
```
## InspectableObject

An object that shows a **zoomed-in view** when clicked.

```python
painting = InspectableObject("painting", width=0.2, height=0.3)
```

## PickableInspectableObject

An object that can be **picked up** from a room and **inspected** from the inventory.

| Behaviour | Effect |
|---|---|
| Room click | Picks up (`PickedUpEvent`) |
| Inventory click | Inspects (`InspectedEvent`) |

```python
note = PickableInspectableObject("note", width=0.08, height=0.08)
```

## Creating custom objects

You can create your own objects by composing the available protocols and assigning command instances:

```python
from escapy.protocols import Interactable, Placeable
from escapy.commands import combine, pick, inspect

class PickAndInspect(Interactable, Placeable):
    def __init__(self, id: str, width: float, height: float):
        self.interact = combine(pick(id), inspect(id))
        self.width = width
        self.height = height
```

See the [Protocols](protocols.md) and [Commands](commands.md) pages for the available building blocks.
