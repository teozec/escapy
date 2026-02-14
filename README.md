# escapy

Escapy is a small library to build simple escape-room style games using `pygame`.

## Installation

Install from source (development):

```bash
pyenv install   # or alternative way to install python 3.14
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start

Use `main.example.py` as a runnable example. A minimal usage looks like:

```python
from escapy import Game, Position, dict_message_provider
from escapy.pygame import PyGameUi

# create your game data (objects, rooms, inventory, first_room_id)
# then:
# message_provider = dict_message_provider(messages)
# ui = PyGameUi(config_ui, message_provider)
# ui.init(game)
# while ui.is_running: ...
```

## Package Structure

The library is organized into two main parts:

- **Main package (`escapy`)**: Contains all core game logic, events, objects, and interaction systems
- **Pygame submodule (`escapy.pygame`)**: Contains the PyGameUi implementation (pygame-based UI)

This separation allows you to use the core game logic independently of the pygame UI,
making it easier to implement alternative UI backends if needed.

## Development

Run tests and linters using the dev requirements.

```bash
pyenv install   # or alternative way to install python 3.14
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```