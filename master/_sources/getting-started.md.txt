# Getting Started

## Requirements

- **Python 3.14+** (uses `type` statement syntax)
- **pygame 2.0+** (optional — only needed if you use `escapy.pygame`)

## Installation

### From source (development)

```bash
pyenv install         # or any other way to install Python 3.14
python -m venv .venv
source .venv/bin/activate

pip install .                        # runtime deps
# or, for development:
pip install -e .[dev]                   # includes ruff, pytest, pre-commit
pre-commit install
```

### As a dependency

```bash
pip install escapy                      # core only
pip install escapy[pygame]              # core + pygame UI
```

## Project layout

```
src/escapy/
├── __init__.py          # Public re-exports
├── types.py             # Position, Room
├── events.py            # All event dataclasses
├── commands.py          # Command factory functions
├── game.py              # Game engine (state + dispatch)
├── messages.py          # MessageProvider utilities
├── mixins.py            # UnlockableMixin, DecodableMixin
├── objects.py           # Ready-made game-object classes
├── protocols/
│   ├── __init__.py      # Protocol re-exports
│   ├── game.py          # GameProtocol, Command type
│   ├── objects.py       # Interactable, Placeable, Unlockable, Decodable
│   └── ui.py            # GameUiProtocol
└── pygame/
    ├── __init__.py      # Re-exports PyGameUi
    └── pygame_ui.py     # Pygame-based UI implementation
```

## Your first game

1. **Define objects** — choose from the built-in classes or create your own:

```python
from escapy import Position, no_op, reveal
from escapy.objects import PickableObject, SelfKeyLock, MoveToRoom

objects = {
    "knife": PickableObject("knife", width=0.05, height=0.05),
    "poster": SelfKeyLock(
        id="poster",
        key_id="knife",
        on_unlock=reveal("hidden-key", "room1", Position(x=0.75, y=0.75)),
        width=0.15,
        height=0.25,
    ),
    "hidden-key": PickableObject("hidden-key", width=0.03, height=0.03),
    "door": MoveToRoom(room_id="room2", width=0.1, height=0.2),
}
```

2. **Define rooms** — a room maps object IDs to positions:

```python
rooms = {
    "room1": {
        "knife": Position(x=0.2, y=0.2),
        "poster": Position(x=0.7, y=0.1),
        "door": Position(x=0.9, y=0.4),
    },
    "room2": {},
}
```

3. **Create the game**:

```python
from escapy import Game

game = Game(objects=objects, rooms=rooms, inventory=[], first_room_id="room1")
```

4. **Set up messages** (optional — maps events to display text):

```python
from escapy import dict_message_provider
from escapy.events import PickedUpEvent, InteractedWithLockedEvent

messages = {
    repr(PickedUpEvent("knife")): "You picked up the knife.",
    repr(InteractedWithLockedEvent("poster")): "It won't budge without a sharp edge.",
}
message_provider = dict_message_provider(messages)
```

5. **Run with the pygame UI**:

```python
from escapy.pygame import PyGameUi

config_ui = {
    "title": "My Escape Room",
    "width": 1024,
    "height": 768,
    "fps": 30,
    "assets_dir": "assets",
    "rooms": {"room1": "room1.png", "room2": "room2.png"},
    "objects": {
        "knife": "knife.png",
        "poster:locked": "poster-locked.png",
        "poster:unlocked": "poster-unlocked.png",
        "hidden-key": "key.png",
        "door": "door.png",
    },
}

ui = PyGameUi(config_ui, message_provider)
ui.init(game)

while ui.is_running:
    ui.tick()
    events = ui.input()
    ui.handle(events)
    ui.render()

ui.quit()
```

## Running tests

```bash
pytest -q
```
