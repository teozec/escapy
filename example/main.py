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

"""Example runner showing how to use the escapy library.

Copy this file and adapt `config.json` to run your own game.
In order to work, you need to add your images to the `assets` directory.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from escapy import Game, Position, dict_message_provider, no_op, reveal
from escapy.commands import add_to_inventory, ask_for_code, combine, move_to_room
from escapy.mixins import DecodableMixin
from escapy.objects import MoveToRoom, PickableObject, SelfKeyLock
from escapy.protocols import Decodable, Interactable, InventoryInteractable, Placeable
from escapy.pygame import PyGameUi


class MoveToRoomAndAddToInventoryObject(Interactable, Placeable):
    """A clickable area that moves the player to another room and adds an object to the inventory.

    Args:
        room_id: Destination room identifier.
        object_id: Object to add to the inventory on interaction.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, room_id: str, object_id: str, width: float, height: float):
        self.interact = combine(move_to_room(room_id), add_to_inventory(object_id))
        self.width = width
        self.height = height


class WinMachine(DecodableMixin, InventoryInteractable, Decodable, Placeable):
    """A special object that ends (wins) the game when the correct code is entered.

    Interacting with it from the inventory triggers a code prompt.  A
    correct code moves the player to the designated win room.

    Args:
        id: Unique object identifier.
        code: The winning code string.
        win_room_id: Room to transition to upon success.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, code: str, win_room_id: str, width: float, height: float):
        self.interact_inventory = ask_for_code(id)
        self.code = code
        self.on_decode = move_to_room(win_room_id)
        self.width = width
        self.height = height


@dataclass
class Config:
    ui: dict
    messages: dict


def get_config(path: Path) -> Config:
    with open(path) as f:
        config = json.load(f)

    return Config(ui=config["ui"], messages=config["messages"])


def main():
    config = get_config(Path("config.json"))

    message_provider = dict_message_provider(config.messages)
    ui = PyGameUi(config.ui, message_provider)
    game = Game(
        objects={
            "a1-key": PickableObject("a1-key", 0.05, 0.05),
            "a2-poster": SelfKeyLock(
                id="a2-poster",
                key_id="a1-key",
                on_unlock=reveal("a2-key", "room1", Position(x=0.75, y=0.75)),
                width=0.15,
                height=0.25,
            ),
            "a2-key": PickableObject("a2-key", 0.03, 0.03),
            "a3-chest": SelfKeyLock(
                id="a3-chest",
                key_id="a2-key",
                on_unlock=no_op(),
                width=0.2,
                height=0.15,
            ),
            "calendar-1": MoveToRoom("room2", 0.1, 0.1),
            "calendar-2": MoveToRoom("room1", 0.1, 0.1),
            "win-machine": WinMachine("win-machine", "12345", "win-room", 0.2, 0.2),
            "init-obj": MoveToRoomAndAddToInventoryObject("room1", "win-machine", width=1.0, height=1.0),
        },
        rooms={
            "init-room": {"init-obj": Position(x=0.0, y=0.0)},
            "room1": {
                "a1-key": Position(x=0.2, y=0.2),
                "a2-poster": Position(x=0.7, y=0.7),
                "a3-chest": Position(x=0.4, y=0.4),
                "calendar-1": Position(x=0.85, y=0.05),
            },
            "room2": {"calendar-2": Position(x=0.85, y=0.05)},
            "win-room": {},
        },
        inventory=[],
        first_room_id="room1",
    )

    debug = False

    ui.init(game)

    while ui.is_running:
        ui.tick()
        events = ui.input()
        if debug and len(events) > 0:
            print(events)
        ui.handle(events)
        ui.render()

    ui.quit()


if __name__ == "__main__":
    main()
