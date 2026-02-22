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
    PutOffHandEvent,
)
from ..game import Game
from ..types import Position, Room


def make_game(
    objects: dict[str, object] | None = None,
    rooms: dict[str, "Room"] | None = None,
    inventory: list[str] | None = None,
    first_room_id: str = "room1",
) -> Game:
    objs = objects if objects is not None else {}
    rms = rooms if rooms is not None else {"room1": {}}
    inv = inventory if inventory is not None else []
    return Game(objects=objs, rooms=rms, inventory=inv, first_room_id=first_room_id)


class _FakeInteractable:
    """Stub satisfying the Interactable protocol for testing Game."""

    def __init__(self, result_events=None):
        self.interact = lambda game: result_events if result_events is not None else []


class _FakeInventoryInteractable:
    """Stub satisfying the InventoryInteractable protocol for testing Game."""

    def __init__(self, result_events=None):
        self.interact_inventory = lambda game: result_events if result_events is not None else []


class _FakeDecodable:
    """Stub satisfying the Decodable protocol for testing Game."""

    def __init__(self, result_events=None):
        self.code = ""
        self.on_decode = lambda _: []
        self._result_events = result_events if result_events is not None else []

    def insert_code(self, code):
        return lambda game: self._result_events


class TestGameQuit:
    def test_sets_is_finished_true(self):
        game = make_game()
        game.quit()
        assert game.is_finished is True

    def test_returns_game_ended_event(self):
        game = make_game()
        events = game.quit()
        assert events == [GameEndedEvent()]


class TestGameInteract:
    def test_returns_empty_when_object_not_in_current_room(self):
        obj = _FakeInteractable(result_events=[object()])
        game = make_game(objects={"painting": obj}, rooms={"room1": {}})
        events = game.interact("painting")
        assert events == []

    def test_delegates_to_interactable_in_room(self):
        pos = Position(x=0.0, y=0.0)
        sentinel = object()
        obj = _FakeInteractable(result_events=[sentinel])
        game = make_game(
            objects={"painting": obj},
            rooms={"room1": {"painting": pos}},
        )
        events = game.interact("painting")
        assert events == [sentinel]

    def test_returns_empty_when_object_not_interactable(self):
        pos = Position(x=0.0, y=0.0)
        game = make_game(objects={"thing": object()}, rooms={"room1": {"thing": pos}})
        events = game.interact("thing")
        assert events == []


class TestGameInteractInventory:
    def test_none_clears_in_hand_and_returns_put_off_hand_event(self):
        game = make_game(inventory=["sword"])
        game.in_hand_object_id = "sword"
        events = game.interact_inventory(None)
        assert game.in_hand_object_id is None
        assert events == [PutOffHandEvent()]

    def test_object_not_in_inventory_returns_empty(self):
        obj = _FakeInventoryInteractable()
        game = make_game(objects={"axe": obj})
        events = game.interact_inventory("axe")
        assert events == []

    def test_delegates_to_inventory_interactable(self):
        sentinel = object()
        obj = _FakeInventoryInteractable(result_events=[sentinel])
        game = make_game(objects={"key": obj}, inventory=["key"])
        events = game.interact_inventory("key")
        assert events == [sentinel]

    def test_object_not_inventory_interactable_returns_empty(self):
        game = make_game(objects={"thing": object()}, inventory=["thing"])
        events = game.interact_inventory("thing")
        assert events == []


class TestGameInsertCode:
    def test_delegates_to_decodable_object(self):
        sentinel = object()
        obj = _FakeDecodable(result_events=[sentinel])
        game = make_game(objects={"safe": obj})
        events = game.insert_code("safe", "any_code")
        assert events == [sentinel]

    def test_non_decodable_object_returns_empty(self):
        game = make_game(objects={"painting": object()})
        events = game.insert_code("painting", "1234")
        assert events == []
