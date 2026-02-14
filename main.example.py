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
"""

import json
from dataclasses import dataclass
from pathlib import Path

from escapy import (
    Game,
    MoveToRoom,
    PickableObject,
    Position,
    SelfKeyLock,
    dict_message_provider,
    no_op,
    reveal,
)
from escapy.pygame import PyGameUi


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
            "a1-knife": PickableObject("a1-knife", 0.05, 0.05),
            "a2-poster": SelfKeyLock(
                id="a2-poster",
                key_id="a1-knife",
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
        },
        rooms={
            "room1": {
                "a1-knife": Position(x=0.2, y=0.2),
                "a2-poster": Position(x=0.7, y=0.7),
                "a3-chest": Position(x=0.4, y=0.4),
                "calendar-1": Position(x=0.85, y=0.05),
            },
            "room2": {
                "calendar-2": Position(x=0.85, y=0.05),
            },
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
