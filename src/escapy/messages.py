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

"""Message providers that map game events to human-readable strings."""

from typing import Callable

from .events import Event

type MessageProvider = Callable[[Event], str | None]
"""A callable that returns a display string for an event, or ``None``."""


def dict_message_provider(messages: dict[str, str]) -> MessageProvider:
    """Create a :data:`MessageProvider` backed by a dictionary.

    Event instances are looked up by their ``repr()`` string.  If no
    matching entry exists, ``None`` is returned.

    Args:
        messages: Mapping from ``repr(event)`` strings to message text.

    Returns:
        A :data:`MessageProvider` callable.
    """
    return lambda event: messages.get(repr(event), None)
