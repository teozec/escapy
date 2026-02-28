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

"""Mixin classes providing reusable unlock and decode behaviour.

These mixins are designed to be composed with protocol classes via
multiple inheritance.  They supply concrete implementations of
:meth:`unlock` and :meth:`insert_code` so that game-object classes
don't have to re-implement the same logic.
"""

from .events import WrongCodeEvent
from .protocols import Command, Decodable, Unlockable

__all__ = ["UnlockableMixin", "DecodableMixin"]


class UnlockableMixin:
    """Mixin that implements :meth:`unlock` for :class:`~escapy.protocols.Unlockable`.

    Sets :attr:`state` to ``"unlocked"`` and returns the stored
    ``on_unlock`` command so that follow-up effects can be executed.
    """

    def unlock(self: Unlockable) -> Command:
        """Unlock the object and return its ``on_unlock`` command."""
        self.state = "unlocked"

        return self.on_unlock


class DecodableMixin:
    """Mixin that implements :meth:`insert_code` for :class:`~escapy.protocols.Decodable`.

    Compares the supplied code against :attr:`code`.  On a match the
    ``on_decode`` command is returned; otherwise a
    :class:`~escapy.events.WrongCodeEvent` is emitted.
    """

    def insert_code(self: Decodable, code: str) -> Command:
        """Check *code* and return the appropriate command.

        Args:
            code: The code string entered by the player.

        Returns:
            The ``on_decode`` command if the code is correct, or a
            command that emits :class:`~escapy.events.WrongCodeEvent`.
        """
        if code == self.code:
            return self.on_decode
        else:
            return lambda game: [WrongCodeEvent()]
