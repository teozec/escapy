from dataclasses import dataclass
import json
from pathlib import Path

from game import Game
from game_types import Position
from interact import no_op, reveal
from objects import MoveToRoom, PickableObject, SelfKeyLock
from ui import PyGameUi


@dataclass
class Config:
    ui: dict


def get_config(path: Path) -> Config:
    with open(path) as f:
        config = json.load(f)

    return Config(ui=config["ui"])


def main():
    config = get_config(Path("config.json"))

    ui = PyGameUi(config.ui)
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

    ui.init(game)

    while ui.is_running:
        ui.tick()
        events = ui.input()
        if len(events) > 0:
            print(events)
        ui.handle(events)
        ui.render()

    ui.quit()


if __name__ == "__main__":
    main()
