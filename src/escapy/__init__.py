# Copyright (C) 2026 Matteo Zeccoli Marazzini
#
# This file is part of escapy.
#
# escapy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# escapy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with escapy. If not, see <https://www.gnu.org/licenses/>.

"""escapy - A lightweight escape-room game library built on pygame.

This is the main package containing all the core game logic, events, objects,
and interaction systems.  The ``PyGameUi`` implementation is available as a
separate submodule in ``escapy.pygame``.

Example usage::

    from escapy import Game
    from escapy.messages import dict_message_provider
    from escapy.pygame import PyGameUi
    from escapy.types import Position

    # create your game data (objects, rooms, inventory, first_room_id)
    # then:
    message_provider = dict_message_provider(messages)
    ui = PyGameUi(config_ui, message_provider)
    ui.init(game)
    while ui.is_running:
        ui.tick()
        events = ui.input()
        ui.handle(events)
        ui.render()
"""

from .game import Game
from .protocols import GameProtocol, GameUiProtocol

__all__ = [
    "Game",
    "GameUiProtocol",
    "GameProtocol",
]
