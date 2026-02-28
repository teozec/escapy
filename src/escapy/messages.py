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

"""Message providers that map game events to human-readable strings.

.. warning::

   The default :func:`dict_message_provider` keys messages by ``repr(event)``.
   This means that adding, removing, or reordering fields on an event
   dataclass will silently invalidate existing message dictionaries.  Users
   must rebuild their message keys whenever the event schema changes.
"""

from typing import Callable

from .events import Event

__all__ = ["MessageProvider", "dict_message_provider"]

type MessageProvider = Callable[[Event], str | None]
"""A callable that returns a display string for an event, or ``None``."""


def dict_message_provider(messages: dict[str, str]) -> MessageProvider:
    """Create a :data:`MessageProvider` backed by a dictionary.

    Event instances are looked up by their ``repr()`` string.  If no
    matching entry exists, ``None`` is returned.

    .. note::

       Because keys are ``repr()`` strings, they are tightly coupled to the
       exact field names and order of each event dataclass.  If the library
       adds a field to an event in a future release, all dictionary entries
       for that event type will stop matching.  Build your dictionaries by
       using ``repr()`` on actual event instances rather than hand-writing
       the strings::

           from escapy.events import PickedUpEvent

           messages = {
               repr(PickedUpEvent("key")): "You found a rusty key!",
           }

    Args:
        messages: Mapping from ``repr(event)`` strings to message text.

    Returns:
        A :data:`MessageProvider` callable.
    """
    return lambda event: messages.get(repr(event), None)
