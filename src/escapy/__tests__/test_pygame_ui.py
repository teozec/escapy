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

"""Tests for the PyGameUi state machine, handle(), and input dispatch."""

from typing import cast
from unittest.mock import MagicMock, patch

import pygame

from ..events import (
    AskedForCodeEvent,
    GameEndedEvent,
    InspectedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutOffHandEvent,
    UnlockedEvent,
)
from ..pygame.pygame_ui import (
    PyGameUi,
    _InsertCodeState,
    _InspectState,
    _NormalState,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ui() -> PyGameUi:
    """Build a PyGameUi with minimal mocked config (no real window)."""
    config = {
        "title": "Test",
        "width": 800,
        "height": 600,
        "fps": 60,
        "assets_dir": "/dev/null",
        "rooms": {},
        "objects": {},
    }
    provider = lambda event: None  # noqa: E731
    with (
        patch.object(pygame, "init"),
        patch.object(pygame.display, "set_caption"),
        patch.object(pygame.display, "set_mode") as mock_set_mode,
        patch.object(pygame.font, "SysFont") as mock_font,
    ):
        # set_mode returns a Surface-like mock with get_size and subsurface
        screen = MagicMock()
        screen.get_size.return_value = (800, 600)
        # subsurface needs to return mocks that also have get_width / get_height
        sub = MagicMock()
        sub.get_width.return_value = 680
        sub.get_height.return_value = 510
        sub.get_abs_offset.return_value = (0, 0)
        sub.get_rect.return_value = pygame.Rect(0, 0, 680, 510)
        screen.subsurface.return_value = sub
        mock_set_mode.return_value = screen

        font = MagicMock()
        font.get_height.return_value = 20
        mock_font.return_value = font

        ui = PyGameUi(config, provider)
    return ui


def _make_fake_game():
    """Create a minimal mock game object."""
    game = MagicMock()
    game.objects = {}
    game.rooms = {"room1": {}}
    game.current_room_id = "room1"
    game.is_finished = False
    game.inventory = []
    game.in_hand_object_id = None
    game.quit.return_value = [GameEndedEvent()]
    game.interact.return_value = []
    game.interact_inventory.return_value = [PutOffHandEvent()]
    game.insert_code.return_value = []
    return game


# ---------------------------------------------------------------------------
# handle() tests
# ---------------------------------------------------------------------------


class TestHandleGameEndedEvent:
    def test_sets_is_running_false(self):
        ui = _make_ui()
        ui.is_running = True
        ui.handle([GameEndedEvent()])
        assert ui.is_running is False


class TestHandleAskedForCodeEvent:
    def test_transitions_to_insert_code_state(self):
        ui = _make_ui()
        ui._state = _NormalState()
        ui.handle([AskedForCodeEvent(object_id="safe")])
        assert isinstance(ui._state, _InsertCodeState)
        assert ui._state.object_id == "safe"

    def test_insert_code_state_text_starts_empty(self):
        ui = _make_ui()
        ui.handle([AskedForCodeEvent(object_id="safe")])
        assert isinstance(ui._state, _InsertCodeState)
        assert ui._state.text == ""


class TestHandleInspectedEvent:
    def test_transitions_to_inspect_state(self):
        ui = _make_ui()
        ui._state = _NormalState()
        # _show_inspect needs object_images and screen — mock them
        mock_image = MagicMock()
        mock_image.get_size.return_value = (100, 100)
        scaled = MagicMock()
        scaled.get_rect.return_value = pygame.Rect(350, 250, 100, 100)
        ui.object_images = cast(dict, {"painting": mock_image})
        ui.game = _make_fake_game()
        ui.game.objects = {"painting": MagicMock()}
        # painting is not Unlockable, so _get_repr returns plain id
        with patch("escapy.pygame.pygame_ui.isinstance", side_effect=lambda obj, cls: False):
            # Simpler: just set _get_repr to return the id
            pass
        ui._get_repr = lambda object_id: object_id
        with patch.object(pygame.transform, "smoothscale", return_value=scaled):
            ui.handle([InspectedEvent(object_id="painting")])
        assert isinstance(ui._state, _InspectState)
        assert ui._state.object_id == "painting"


class TestHandleMessages:
    def test_event_with_message_is_added(self):
        ui = _make_ui()
        ui._get_event_message = lambda e: "You picked it up!"
        ui.handle([PickedUpEvent(object_id="key")])
        assert "You picked it up!" in ui.messages

    def test_event_without_message_is_not_added(self):
        ui = _make_ui()
        ui._get_event_message = lambda e: None
        ui.handle([MovedToRoomEvent(room_id="room2")])
        assert ui.messages == []

    def test_multiple_events_produce_multiple_messages(self):
        ui = _make_ui()
        call_count = 0

        def provider(event):
            nonlocal call_count
            call_count += 1
            return f"msg-{call_count}"

        ui._get_event_message = provider
        ui.handle([PickedUpEvent("a"), PickedUpEvent("b")])
        assert len(ui.messages) == 2


# ---------------------------------------------------------------------------
# _handle_insert_code_input() tests
# ---------------------------------------------------------------------------


class TestInsertCodeInput:
    def _make_ui_in_code_state(self, object_id="safe"):
        ui = _make_ui()
        ui._state = _InsertCodeState(object_id=object_id, prompt="Enter code")
        ui.game = _make_fake_game()
        return ui

    def test_printable_char_appends_to_text(self):
        ui = self._make_ui_in_code_state()
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_a
        event.unicode = "a"
        ui._handle_insert_code_input(event)
        assert isinstance(ui._state, _InsertCodeState)
        assert ui._state.text == "a"

    def test_multiple_chars_accumulate(self):
        ui = self._make_ui_in_code_state()
        for ch in "1234":
            event = MagicMock()
            event.type = pygame.KEYDOWN
            event.key = 0
            event.unicode = ch
            ui._handle_insert_code_input(event)
        assert isinstance(ui._state, _InsertCodeState)
        assert ui._state.text == "1234"

    def test_backspace_removes_last_char(self):
        ui = self._make_ui_in_code_state()
        assert isinstance(ui._state, _InsertCodeState)
        ui._state.text = "123"
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_BACKSPACE
        event.unicode = ""
        ui._handle_insert_code_input(event)
        assert ui._state.text == "12"

    def test_escape_returns_to_normal_state(self):
        ui = self._make_ui_in_code_state()
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE
        event.unicode = ""
        ui._handle_insert_code_input(event)
        assert isinstance(ui._state, _NormalState)

    def test_enter_submits_code_and_returns_to_normal(self):
        ui = self._make_ui_in_code_state("safe")
        assert isinstance(ui._state, _InsertCodeState)
        ui._state.text = "1234"
        game = ui.game
        assert isinstance(game, MagicMock)
        game.insert_code.return_value = [UnlockedEvent(object_id="safe")]
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_RETURN
        event.unicode = ""
        events = ui._handle_insert_code_input(event)
        game.insert_code.assert_called_once_with("safe", "1234")
        assert isinstance(ui._state, _NormalState)
        assert any(isinstance(e, UnlockedEvent) for e in events)

    def test_non_keydown_event_is_ignored(self):
        ui = self._make_ui_in_code_state()
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        events = ui._handle_insert_code_input(event)
        assert events == []
        assert isinstance(ui._state, _InsertCodeState)


# ---------------------------------------------------------------------------
# _handle_inspect_input() tests
# ---------------------------------------------------------------------------


class TestInspectInput:
    def _make_ui_in_inspect_state(self):
        ui = _make_ui()
        ui._state = _InspectState(
            object_id="painting",
            surface=MagicMock(),
            rect=pygame.Rect(0, 0, 100, 100),
        )
        return ui

    def test_keydown_returns_to_normal(self):
        ui = self._make_ui_in_inspect_state()
        event = MagicMock()
        event.type = pygame.KEYDOWN
        ui._handle_inspect_input(event)
        assert isinstance(ui._state, _NormalState)

    def test_mousedown_returns_to_normal(self):
        ui = self._make_ui_in_inspect_state()
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        ui._handle_inspect_input(event)
        assert isinstance(ui._state, _NormalState)

    def test_other_event_stays_in_inspect(self):
        ui = self._make_ui_in_inspect_state()
        event = MagicMock()
        event.type = pygame.MOUSEMOTION
        ui._handle_inspect_input(event)
        assert isinstance(ui._state, _InspectState)

    def test_returns_empty_events(self):
        ui = self._make_ui_in_inspect_state()
        event = MagicMock()
        event.type = pygame.KEYDOWN
        events = ui._handle_inspect_input(event)
        assert events == []


# ---------------------------------------------------------------------------
# add_message() tests
# ---------------------------------------------------------------------------


class TestAddMessage:
    def test_appends_to_messages_list(self):
        ui = _make_ui()
        ui.add_message("Hello")
        ui.add_message("World")
        assert ui.messages == ["Hello", "World"]
