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

from typing import Callable

from .game_events import (
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
