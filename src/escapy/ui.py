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

from typing import Protocol

from .game import Game
from .game_events import GameEvent


class GameUi(Protocol):
    def init(self, game: Game) -> None: ...

    def tick(self) -> None: ...

    def input(self) -> list[GameEvent]: ...

    def handle(self, events: list[GameEvent]) -> None: ...

    def render(self) -> None: ...

    def quit(self) -> None: ...

    is_running: bool
