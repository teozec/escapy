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

from typing import Any

import pytest

from ..events import (
    GameEndedEvent,
    PutOffHandEvent,
)
from ..game import Game
from ..types import Position, Room


def make_game(
    objects: list[Any] | None = None,  # Any: some tests pass invalid objects on purpose
    rooms: dict[str, "Room"] | None = None,
    inventory: list[str] | None = None,
    first_room_id: str = "room1",
) -> Game:
    objs = objects if objects is not None else []
    rms = rooms if rooms is not None else {"room1": {}}
    inv = inventory if inventory is not None else []
    return Game(objects=objs, rooms=rms, inventory=inv, first_room_id=first_room_id)


class _FakeObject:
    """Stub satisfying only the GameObject protocol."""

    def __init__(self, id):
        self.id = id


class _FakeInteractable:
    """Stub satisfying the Interactable protocol for testing Game."""

    def __init__(self, id, result_events=None):
        self.id = id
        self.interact = lambda game: result_events if result_events is not None else []


class _FakeInventoryInteractable:
    """Stub satisfying the InventoryInteractable protocol for testing Game."""

    def __init__(self, id, result_events=None):
        self.id = id
        self.interact_inventory = lambda game: result_events if result_events is not None else []


class _FakeDecodable:
    """Stub satisfying the Decodable protocol for testing Game."""

    def __init__(self, id, result_events=None):
        self.id = id
        self.code = ""
        self.on_decode = lambda _: []
        self._result_events = result_events if result_events is not None else []

    def insert_code(self, code):
        return lambda game: self._result_events


class TestGameObjects:
    def test_indexes_objects_by_id(self):
        key = _FakeObject("key")
        door = _FakeObject("door")
        game = make_game(objects=[key, door])
        assert game.objects == {"key": key, "door": door}

    def test_rejects_object_without_id(self):
        with pytest.raises(TypeError, match="index 1"):
            make_game(objects=[_FakeObject("key"), object()])

    def test_rejects_non_string_id(self):
        with pytest.raises(TypeError, match="expected str"):
            make_game(objects=[_FakeObject(42)])

    def test_rejects_empty_id(self):
        with pytest.raises(ValueError, match="empty id"):
            make_game(objects=[_FakeObject("")])

    def test_rejects_duplicate_ids(self):
        with pytest.raises(ValueError, match="'key'"):
            make_game(objects=[_FakeObject("key"), _FakeObject("key")])

    def test_reports_all_duplicate_ids(self):
        objects = [_FakeObject(id) for id in ["key", "door", "key", "box", "door"]]
        with pytest.raises(ValueError, match=r"\['key', 'door'\]"):
            make_game(objects=objects)

    def test_objects_are_read_only(self):
        game = make_game(objects=[_FakeObject("key")])
        with pytest.raises(TypeError):
            game.objects["door"] = _FakeObject("door")  # type: ignore[index]


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
    def test_raises_key_error_for_unknown_object_id(self):
        game = make_game(objects=[], rooms={"room1": {}})
        with pytest.raises(KeyError):
            game.interact("nonexistent")

    def test_returns_empty_when_object_not_in_current_room(self):
        obj = _FakeInteractable("painting", result_events=[object()])
        game = make_game(objects=[obj], rooms={"room1": {}})
        events = game.interact("painting")
        assert events == []

    def test_delegates_to_interactable_in_room(self):
        pos = Position(x=0.0, y=0.0)
        sentinel = object()
        obj = _FakeInteractable("painting", result_events=[sentinel])
        game = make_game(
            objects=[obj],
            rooms={"room1": {"painting": pos}},
        )
        events = game.interact("painting")
        assert events == [sentinel]

    def test_returns_empty_when_object_not_interactable(self):
        pos = Position(x=0.0, y=0.0)
        game = make_game(objects=[_FakeObject("thing")], rooms={"room1": {"thing": pos}})
        events = game.interact("thing")
        assert events == []


class TestGameInteractInventory:
    def test_raises_key_error_for_unknown_object_id(self):
        game = make_game(objects=[], inventory=[])
        with pytest.raises(KeyError):
            game.interact_inventory("nonexistent")

    def test_none_clears_in_hand_and_returns_put_off_hand_event(self):
        game = make_game(inventory=["sword"])
        game.in_hand_object_id = "sword"
        events = game.interact_inventory(None)
        assert game.in_hand_object_id is None
        assert events == [PutOffHandEvent()]

    def test_object_not_in_inventory_returns_empty(self):
        obj = _FakeInventoryInteractable("axe")
        game = make_game(objects=[obj])
        events = game.interact_inventory("axe")
        assert events == []

    def test_delegates_to_inventory_interactable(self):
        sentinel = object()
        obj = _FakeInventoryInteractable("key", result_events=[sentinel])
        game = make_game(objects=[obj], inventory=["key"])
        events = game.interact_inventory("key")
        assert events == [sentinel]

    def test_object_not_inventory_interactable_returns_empty(self):
        game = make_game(objects=[_FakeObject("thing")], inventory=["thing"])
        events = game.interact_inventory("thing")
        assert events == []


class TestGameInsertCode:
    def test_raises_key_error_for_unknown_object_id(self):
        game = make_game(objects=[])
        with pytest.raises(KeyError):
            game.insert_code("nonexistent", "1234")

    def test_delegates_to_decodable_object(self):
        sentinel = object()
        obj = _FakeDecodable("safe", result_events=[sentinel])
        game = make_game(objects=[obj])
        events = game.insert_code("safe", "any_code")
        assert events == [sentinel]

    def test_non_decodable_object_returns_empty(self):
        game = make_game(objects=[_FakeObject("painting")])
        events = game.insert_code("painting", "1234")
        assert events == []
