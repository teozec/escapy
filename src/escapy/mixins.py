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


from .events import WrongCodeEvent
from .protocols import Decodable, Unlockable
from .types import Command


class UnlockableMixin:
    def unlock(self: Unlockable) -> Command:
        self.state = "unlocked"

        return self.on_unlock


class DecodableMixin:
    def insert_code(self: Decodable, code: str) -> Command:
        if code == self.code:
            return self.on_decode
        else:
            return lambda game: [WrongCodeEvent()]


type GameMixins = UnlockableMixin | DecodableMixin
