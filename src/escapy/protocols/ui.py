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

"""Protocol definition for the game UI layer."""

from typing import Protocol

from ..events import Event
from .game import GameProtocol


class GameUiProtocol(Protocol):
    """Structural interface that every UI backend must implement.

    The game loop calls these methods in order::

        ui.init(game)
        while ui.is_running:
            ui.tick()
            events = ui.input()
            ui.handle(events)
            ui.render()
        ui.quit()

    Attributes:
        is_running: ``True`` while the UI is active.
    """

    def init(self, game: GameProtocol) -> None:
        """Initialise the UI with the given game instance."""
        ...

    def tick(self) -> None:
        """Regulate the frame rate / perform per-frame bookkeeping."""
        ...

    def input(self) -> list[Event]:
        """Poll user input and return resulting events."""
        ...

    def handle(self, events: list[Event]) -> None:
        """React to game events (e.g. display messages, switch states)."""
        ...

    def render(self) -> None:
        """Draw the current frame."""
        ...

    def quit(self) -> None:
        """Tear down the UI and release resources."""
        ...

    is_running: bool
