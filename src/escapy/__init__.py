"""Escapy - A lightweight escape-room game library built on pygame.

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

from .game import Game
from .game_types import Position
from .insert_code import code_lock
from .interact import (
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
    # objects
    "PickableObject",
    "SelfSimpleLock",
    "SelfKeyLock",
    "SelfAskCodeLock",
    "MoveToRoom",
    "WinMachine",
    "InspectableObject",
    "PickableInspectableObject",
    "MoveToRoomAndAddToInventoryObject",
    # interact helpers
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
    # code lock
    "code_lock",
    "GameUi",
]
