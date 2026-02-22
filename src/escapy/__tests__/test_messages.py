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

from ..events import (
    GameEndedEvent,
    InspectedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
)
from ..messages import dict_message_provider


class TestDictMessageProvider:
    def test_returns_message_for_matching_event(self):
        event = PickedUpEvent(object_id="key")
        provider = dict_message_provider({repr(event): "You picked up the key!"})
        assert provider(event) == "You picked up the key!"

    def test_returns_none_for_unmatched_event(self):
        provider = dict_message_provider({})
        assert provider(PickedUpEvent("key")) is None

    def test_different_events_map_to_different_messages(self):
        e1 = PickedUpEvent("key")
        e2 = InspectedEvent("painting")
        provider = dict_message_provider(
            {
                repr(e1): "You picked up the key.",
                repr(e2): "You inspect the painting.",
            }
        )
        assert provider(e1) == "You picked up the key."
        assert provider(e2) == "You inspect the painting."

    def test_returns_none_when_similar_but_different_event(self):
        e1 = PickedUpEvent("key")
        e2 = PickedUpEvent("sword")
        provider = dict_message_provider({repr(e1): "Picked up key"})
        assert provider(e2) is None

    def test_no_message_event_returns_none(self):
        provider = dict_message_provider({repr(GameEndedEvent()): "Game over"})
        assert provider(MovedToRoomEvent("lobby")) is None

    def test_parameter_less_event_message(self):
        event = GameEndedEvent()
        provider = dict_message_provider({repr(event): "The game has ended."})
        assert provider(GameEndedEvent()) == "The game has ended."
