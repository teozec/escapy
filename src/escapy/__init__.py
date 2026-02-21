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
and interaction systems. The PyGameUi implementation is available as a separate
submodule in escapy.ui.

Example usage:
    from escapy import Game, Position, dict_message_provider
    from escapy.ui import PyGameUi

    # create your game data (objects, rooms, inventory, first_room_id)
    # then:
    message_provider = dict_message_provider(messages)
    ui = PyGameUi(config_ui, message_provider)
    ui.init(game)
    while ui.is_running:
        ui.tick()
        events = ui.input()
        events = game.process_events(events)
        ui.handle(events)
        ui.render()
"""

from .commands import (
    add_to_inventory,
    ask_for_code,
    chain,
    combine,
    cond,
    inspect,
    key_lock,
    locked,
    move_to_room,
    no_op,
    pick,
    put_in_hand,
    reveal,
    simple_lock,
)
from .game import Game
from .game_types import Position
from .messages import dict_message_provider
from .objects import (
    InspectableObject,
    MoveToRoom,
    MoveToRoomAndAddToInventoryObject,
    PickableInspectableObject,
    PickableObject,
    SelfAskCodeLock,
    SelfKeyLock,
    SelfSimpleLock,
    WinMachine,
)
from .ui import GameUi

__all__ = [
    "Game",
    "Position",
    "dict_message_provider",
    "PickableObject",
    "SelfSimpleLock",
    "SelfKeyLock",
    "SelfAskCodeLock",
    "MoveToRoom",
    "WinMachine",
    "InspectableObject",
    "PickableInspectableObject",
    "MoveToRoomAndAddToInventoryObject",
    "no_op",
    "pick",
    "put_in_hand",
    "simple_lock",
    "key_lock",
    "ask_for_code",
    "locked",
    "inspect",
    "combine",
    "cond",
    "chain",
    "reveal",
    "move_to_room",
    "add_to_inventory",
    "GameUi",
]
