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

from .game import Game
from .game_events import GameEvent, WrongCodeEvent
from .protocols import Decodable, Unlockable


class UnlockableMixin:
    def unlock(self: Unlockable, game: Game) -> list[GameEvent]:
        self.state = "unlocked"
        return self.on_unlock(game)


class DecodableMixin:
    def insert_code(self: Decodable, code: str, game: Game) -> list[GameEvent]:
        if code == self.code:
            return self.on_decode(game)
        else:
            return [WrongCodeEvent()]


GameMixins = UnlockableMixin | DecodableMixin
