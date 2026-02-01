from typing import Callable

from game_events import (
    GameEvent,
    UnlockedEvent,
    WrongCodeEvent,
)


InsertCodeFn = Callable[[str], list[GameEvent]]


def code_lock(id: str, expected_code: str) -> InsertCodeFn:
    def insert_code(input_code: str) -> list[GameEvent]:
        if input_code == expected_code:
            return [UnlockedEvent(object_id=id)]
        else:
            return [WrongCodeEvent()]

    return insert_code
