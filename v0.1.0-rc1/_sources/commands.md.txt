# Commands

Commands are the fundamental building blocks of game-object behaviour in escapy.  A **command** is a callable with the signature:

```python
Command = Callable[[GameProtocol], list[Event]]
```

It receives the current game state, optionally mutates it, and returns a list of events describing what happened.

All command factory functions live in `escapy.commands` and are re-exported from the top-level `escapy` package.

## Basic commands

### `no_op() → Command`

Does nothing; returns an empty event list.  Useful as a default `on_unlock` value.

### `pick(id) → Command`

Removes the object from the current room and adds it to the player's inventory.

**Emits:** `PickedUpEvent(object_id=id)`

### `put_in_hand(id) → Command`

Sets the object as the active hand item.

**Emits:** `PutInHandEvent(object_id=id)`

### `inspect(id) → Command`

Triggers a zoomed-in view of the object.

**Emits:** `InspectedEvent(object_id=id)`

### `reveal(object_id, room_id, position) → Command`

Places a previously hidden object into a room at the given position.

**Emits:** `RevealedEvent(object_id, room_id, position)`

### `move_to_room(room_id) → Command`

Changes the current room.

**Emits:** `MovedToRoomEvent(room_id)`

### `add_to_inventory(object_id) → Command`

Adds an object to the inventory without removing it from a room.

**Emits:** `AddedToInventoryEvent(object_id)`

## Lock commands

### `simple_lock(id) → Command`

Unlocks the object if it is `Unlockable` and currently locked, then executes its `on_unlock` command.

**Emits:** `UnlockedEvent(object_id=id)` + events from `on_unlock`.

### `key_lock(id, key_id) → Command`

Same as `simple_lock`, but only fires when `game.in_hand_object_id == key_id`.

### `ask_for_code(id) → Command`

Asks the UI to prompt the player for a code.

**Emits:** `AskedForCodeEvent(object_id=id)`

### `locked(id) → Command`

Signals that the player interacted with a locked object (usually paired with `chain` as a fallback).

**Emits:** `InteractedWithLockedEvent(object_id=id)`

## Combinators

Combinators let you compose multiple commands into richer behaviours.

### `combine(*commands) → Command`

Executes all commands **in sequence** and returns their events as a flat list.

```python
cmd = combine(
    move_to_room("cellar"),
    add_to_inventory("torch"),
)
```

### `cond(*clauses) → Command`

Evaluates conditions in order and executes only the **first matching** clause.

```python
cmd = cond(
    (lambda: obj.state == "locked", ask_for_code("safe")),
    # implicit: no match → empty list
)
```

Each clause is a tuple `(condition: () → bool, command: Command)`.

### `chain(*clauses) → Command`

Like `combine`, but each clause's condition receives the **events emitted so far**, enabling conditional follow-ups.

```python
cmd = chain(
    (lambda _events: True, key_lock("door", key_id="gold_key")),
    (
        lambda events: not any(isinstance(e, UnlockedEvent) for e in events),
        locked("door"),
    ),
)
```

Each clause is a tuple `(condition: (list[Event]) → bool, command: Command)`.  All matching clauses execute (unlike `cond`, which stops at the first match).
