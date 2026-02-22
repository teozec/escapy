# Protocols

escapy uses `typing.Protocol` (structural subtyping) to define its interfaces.  Any object that has the right attributes and methods satisfies a protocol — no explicit base-class inheritance is required.

All protocols are defined in `escapy.protocols` and re-exported from the top-level package.

## GameProtocol

The main game-engine interface.

```python
class GameProtocol(Protocol):
    objects: dict[str, object]
    rooms: dict[str, Room]
    current_room_id: str
    is_finished: bool
    inventory: list[str]
    in_hand_object_id: str | None

    def quit(self) -> list[Event]: ...
    def interact(self, object_id: str) -> list[Event]: ...
    def interact_inventory(self, object_id: str | None) -> list[Event]: ...
    def insert_code(self, object_id: str, code: str) -> list[Event]: ...
```

**Attributes:**

| Attribute | Description |
|---|---|
| `objects` | All game objects, keyed by ID |
| `rooms` | Room layouts (`dict[str, Room]`) |
| `current_room_id` | Currently displayed room |
| `is_finished` | `True` after `quit()` |
| `inventory` | Ordered list of carried object IDs |
| `in_hand_object_id` | Currently held item, or `None` |

The concrete implementation is `escapy.Game`.

## Command

```python
type Command = Callable[[GameProtocol], list[Event]]
```

A callable that takes a `GameProtocol`, optionally mutates game state, and returns the list of events that occurred.

## Object protocols

### Interactable

```python
class Interactable(Protocol):
    interact: Command
```

An object that can be clicked in a room.  The `interact` attribute is a command that is called when the player clicks the object.

### InventoryInteractable

```python
class InventoryInteractable(Protocol):
    interact_inventory: Command
```

An object that can be clicked in the inventory sidebar.

### Placeable

```python
class Placeable(Protocol):
    width: float
    height: float
```

An object that occupies visual space.  Dimensions are normalised fractions of the game area (0.0–1.0).

### Unlockable

```python
class Unlockable(Protocol):
    state: Literal["locked", "unlocked"]
    on_unlock: Command

    def unlock(self) -> Command: ...
```

An object with a locking mechanism.  `unlock()` should transition `state` to `"unlocked"` and return `on_unlock`.  See `UnlockableMixin` for the standard implementation.

### Decodable

```python
class Decodable(Protocol):
    code: str
    on_decode: Command

    def insert_code(self, code: str) -> Command: ...
```

An object that accepts a text/numeric code.  `insert_code()` should compare the input against `code` and return either `on_decode` or a `WrongCodeEvent` command.  See `DecodableMixin` for the standard implementation.

## GameUiProtocol

```python
class GameUiProtocol(Protocol):
    is_running: bool

    def init(self, game: GameProtocol) -> None: ...
    def tick(self) -> None: ...
    def input(self) -> list[Event]: ...
    def handle(self, events: list[Event]) -> None: ...
    def render(self) -> None: ...
    def quit(self) -> None: ...
```

The UI backend interface.  The game loop calls these methods in the order shown above.  `escapy.pygame.PyGameUi` is the provided implementation.

## Runtime checking

All object protocols are decorated with `@runtime_checkable`, so you can use `isinstance()` checks:

```python
from escapy.protocols import Interactable

if isinstance(obj, Interactable):
    events = obj.interact(game)
```

This is used internally by `Game` to dispatch interactions only to objects that support them.
