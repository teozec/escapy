# Getting Started

## Requirements

- **Python 3.12+** (uses `type` statement syntax)
- **pygame 2.0+** (optional — only needed if you use `escapy.pygame`)

## Installation

### From source (development)

```bash
pyenv install         # or any other way to install Python 3.12
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

The repository uses a **src-layout** so that all importable code lives under `src/escapy`. A minimal overview of the tree is shown below — additional top‑level directories include tests, examples, and the documentation sources.

```
.
├── docs/                 # Sphinx sources and _build output (see Makefile)
├── example/              # simple demo game using escapy
├── escape/               # alternate example which mirrors iOS asset layout
├── src/
│   └── escapy/           # library package
│       ├── __init__.py          # Public re‑exports
│       ├── types.py             # Position, Room
│       ├── events.py            # All event dataclasses
│       ├── commands.py          # Command factory functions
│       ├── game.py              # Game engine (state + dispatch)
│       ├── messages.py          # MessageProvider utilities
│       ├── mixins.py            # UnlockableMixin, DecodableMixin
│       ├── objects.py           # Ready‑made game‑object classes
│       ├── protocols/           # protocol definitions used by consumers
│       │   ├── __init__.py      # re‑exports
│       │   ├── game.py          # GameProtocol, Command type
│       │   ├── objects.py       # Interactable, Placeable, Unlockable, Decodable
│       │   └── ui.py            # GameUiProtocol
│       ├── pygame/             # optional pygame UI implementation
│       │   ├── __init__.py      # re‑exports PyGameUi
│       │   └── pygame_ui.py     # pygame‑based UI implementation
│       └── __tests__/          # unit tests (used by pytest)
├── pyproject.toml       # project metadata / dependencies
├── Makefile             # helper commands (lint, test, docs, etc.)
├── README.md            # overview & installation instructions
└── CHANGELOG.md         # package changelog
```

Using this layout keeps the import path clean (`import escapy`) and clearly separates the library source from ancillary files such as examples and documentation.

## Your first game

1. **Define objects** — choose from the built-in classes or create your own:

```python
from escapy.types import Position
from escapy.commands import no_op, reveal
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
from escapy.messages import dict_message_provider
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
