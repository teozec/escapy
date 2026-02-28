# escapy

Escapy is a small library to build simple escape-room style games using `pygame`.

## Installation

Install from source (development):

```bash
pyenv install   # or alternative way to install python 3.12
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick start

Use `main.example.py` as a runnable example. A minimal usage looks like:

```python
from escapy import Game
from escapy.types import Position
from escapy.messages import dict_message_provider
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

Run tests and linters using the editable dev extras.

```bash
pyenv install   # or alternative way to install python 3.12
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit install
```

Common tasks are wrapped in the `Makefile`:

```bash
make test          # run the test suite
make lint          # run ruff linter
make format        # auto-format code
make docs          # build Sphinx documentation
make build         # build wheel and sdist
make clean         # remove build artefacts
make help          # list all available targets
```

## License

This project is licensed under the GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later). See the [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) files for details.

Copyright (C) 2026