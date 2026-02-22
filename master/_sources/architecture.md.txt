# Architecture

## Overview

escapy follows a strict **Model → Command → Event → UI** pipeline:

```
Player Action
     │
     ▼
┌──────────┐
│   Game   │  (model – mutable state)
└────┬─────┘
     │ dispatches to object behaviours
     ▼
┌──────────┐
│ Commands │  (pure-ish functions: GameProtocol → list[Event])
└────┬─────┘
     │ returns events
     ▼
┌──────────┐
│  Events  │  (immutable dataclasses)
└────┬─────┘
     │ consumed by
     ▼
┌──────────┐
│    UI    │  (renders, plays sounds, shows messages)
└──────────┘
```

## Key design decisions

### Commands are first-class values

A `Command` is simply `Callable[[GameProtocol], list[Event]]`.  Object
behaviours are expressed by assigning command instances at construction time
rather than overriding methods.  This makes objects highly composable
without deep inheritance hierarchies.

### Protocols over base classes

All contracts (`GameProtocol`, `Interactable`, `Unlockable`, …) are
defined as `typing.Protocol` classes.  This enables structural (duck)
typing — any object with the right attributes and methods satisfies the
protocol, regardless of its class hierarchy.

### Events decouple logic from presentation

Commands never call the UI directly.  They return event dataclasses.
The UI layer receives the event list and decides how to react (display a
message, play a sound, show an overlay, etc.).

### Mixins for shared behaviour

`UnlockableMixin` and `DecodableMixin` provide concrete implementations
of `unlock()` and `insert_code()`.  Object classes compose these via
multiple inheritance alongside the protocols they satisfy.

## Game loop

The canonical game loop is:

```python
ui.init(game)

while ui.is_running:
    ui.tick()                  # regulate frame rate
    events = ui.input()        # poll and dispatch player actions
    ui.handle(events)          # update UI state (messages, overlays)
    ui.render()                # draw current frame

ui.quit()
```

Note that `ui.input()` internally calls `game.interact()`,
`game.interact_inventory()`, or `game.insert_code()` — so events are
produced during the input phase, not in a separate update step.

## Module dependency graph

```
types ◄── events ◄── protocols ◄── commands
                          ▲            │
                          │            ▼
                        mixins ◄── objects
                          ▲
                          │
                        game
                          ▲
                          │
                      pygame_ui
                          ▲
                          │
                       messages
```

The core library (`escapy`) has **no runtime dependency on pygame**.
The `escapy.pygame` subpackage is the only module that imports `pygame`.
