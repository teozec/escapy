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
    AddedToInventoryEvent,
    AskedForCodeEvent,
    InspectedEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    UnlockedEvent,
    WrongCodeEvent,
)
from ..objects import (
    InspectableObject,
    MoveToRoom,
    MoveToRoomAndAddToInventoryObject,
    PickableInspectableObject,
    PickableObject,
    SelfAskCodeLock,
    SelfKeyLock,
    SelfSimpleLock,
    WinMachine,
)
from ..types import Position
from ._test_helpers import FakeGame


def _noop(_):
    return []


def _room_game(object_id: str, obj, position: Position | None = None) -> FakeGame:
    pos = position or Position(x=0.0, y=0.0)
    return FakeGame(
        objects={object_id: obj},
        rooms={"room1": {object_id: pos}},
        current_room_id="room1",
    )


class TestPickableObject:
    def test_interact_picks_up_object(self):
        pos = Position(x=0.0, y=0.0)
        obj = PickableObject(id="coin", width=1.0, height=1.0)
        game = _room_game("coin", obj, pos)
        events = obj.interact(game)
        assert PickedUpEvent("coin") in events
        assert "coin" in game.inventory
        assert "coin" not in game.rooms["room1"]

    def test_interact_inventory_puts_in_hand(self):
        obj = PickableObject(id="coin", width=1.0, height=1.0)
        game = FakeGame(objects={"coin": obj}, inventory=["coin"])
        events = obj.interact_inventory(game)
        assert events == [PutInHandEvent("coin")]
        assert game.in_hand_object_id == "coin"

    def test_has_dimensions(self):
        obj = PickableObject(id="coin", width=32.0, height=16.0)
        assert obj.width == 32.0
        assert obj.height == 16.0


class TestSelfSimpleLock:
    def test_initial_state_is_locked(self):
        obj = SelfSimpleLock(id="chest", on_unlock=_noop, width=1.0, height=1.0)
        assert obj.state == "locked"

    def test_interact_unlocks_when_locked(self):
        obj = SelfSimpleLock(id="chest", on_unlock=_noop, width=1.0, height=1.0)
        game = FakeGame(objects={"chest": obj})
        events = obj.interact(game)
        assert UnlockedEvent("chest") in events
        assert obj.state == "unlocked"

    def test_interact_does_nothing_when_already_unlocked(self):
        obj = SelfSimpleLock(id="chest", on_unlock=_noop, width=1.0, height=1.0)
        obj.state = "unlocked"
        game = FakeGame(objects={"chest": obj})
        events = obj.interact(game)
        assert events == []

    def test_on_unlock_command_fires(self):
        obj = SelfSimpleLock(
            id="chest",
            on_unlock=lambda g: [MovedToRoomEvent("vault")],
            width=1.0,
            height=1.0,
        )
        game = FakeGame(objects={"chest": obj}, rooms={"room1": {}})
        events = obj.interact(game)
        assert MovedToRoomEvent("vault") in events


class TestSelfKeyLock:
    def test_initial_state_is_locked(self):
        obj = SelfKeyLock(id="door", key_id="gold_key", on_unlock=_noop, width=1.0, height=1.0)
        assert obj.state == "locked"

    def test_interact_unlocks_with_correct_key_in_hand(self):
        obj = SelfKeyLock(id="door", key_id="gold_key", on_unlock=_noop, width=1.0, height=1.0)
        game = FakeGame(objects={"door": obj}, in_hand_object_id="gold_key")
        events = obj.interact(game)
        assert UnlockedEvent("door") in events
        assert obj.state == "unlocked"

    def test_interact_returns_locked_event_without_key(self):
        obj = SelfKeyLock(id="door", key_id="gold_key", on_unlock=_noop, width=1.0, height=1.0)
        game = FakeGame(objects={"door": obj}, in_hand_object_id=None)
        events = obj.interact(game)
        assert InteractedWithLockedEvent("door") in events
        assert not any(isinstance(e, UnlockedEvent) for e in events)

    def test_interact_returns_locked_event_with_wrong_key(self):
        obj = SelfKeyLock(id="door", key_id="gold_key", on_unlock=_noop, width=1.0, height=1.0)
        game = FakeGame(objects={"door": obj}, in_hand_object_id="silver_key")
        events = obj.interact(game)
        assert InteractedWithLockedEvent("door") in events

    def test_interact_locked_when_already_unlocked_with_key(self):
        obj = SelfKeyLock(id="door", key_id="gold_key", on_unlock=_noop, width=1.0, height=1.0)
        obj.state = "unlocked"
        game = FakeGame(objects={"door": obj}, in_hand_object_id="gold_key")
        events = obj.interact(game)
        # key_lock returns nothing when already unlocked, locked() does not fire because
        # the chain condition checks state != unlocked
        assert not any(isinstance(e, UnlockedEvent) for e in events)


class TestSelfAskCodeLock:
    def test_initial_state_is_locked(self):
        obj = SelfAskCodeLock(id="safe", on_unlock=_noop, code="1234", width=1.0, height=1.0)
        assert obj.state == "locked"

    def test_interact_asks_for_code_when_locked(self):
        obj = SelfAskCodeLock(id="safe", on_unlock=_noop, code="1234", width=1.0, height=1.0)
        game = FakeGame(objects={"safe": obj})
        events = obj.interact(game)
        assert events == [AskedForCodeEvent("safe")]

    def test_interact_returns_empty_when_unlocked(self):
        obj = SelfAskCodeLock(id="safe", on_unlock=_noop, code="1234", width=1.0, height=1.0)
        obj.state = "unlocked"
        game = FakeGame(objects={"safe": obj})
        events = obj.interact(game)
        assert events == []

    def test_insert_code_correct_unlocks(self):
        obj = SelfAskCodeLock(id="safe", on_unlock=_noop, code="1234", width=1.0, height=1.0)
        game = FakeGame(objects={"safe": obj})
        obj.insert_code("1234")(game)
        assert obj.state == "unlocked"

    def test_insert_code_wrong_returns_wrong_code_event(self):
        obj = SelfAskCodeLock(id="safe", on_unlock=_noop, code="1234", width=1.0, height=1.0)
        game = FakeGame(objects={"safe": obj})
        events = obj.insert_code("9999")(game)
        assert events == [WrongCodeEvent()]


class TestMoveToRoom:
    def test_interact_changes_current_room(self):
        obj = MoveToRoom(room_id="cellar", width=1.0, height=1.0)
        game = FakeGame(current_room_id="room1")
        obj.interact(game)
        assert game.current_room_id == "cellar"

    def test_interact_returns_moved_event(self):
        obj = MoveToRoom(room_id="cellar", width=1.0, height=1.0)
        game = FakeGame()
        events = obj.interact(game)
        assert events == [MovedToRoomEvent("cellar")]


class TestWinMachine:
    def test_interact_inventory_asks_for_code(self):
        obj = WinMachine(id="machine", code="0000", win_room_id="win", width=1.0, height=1.0)
        game = FakeGame(objects={"machine": obj})
        events = obj.interact_inventory(game)
        assert events == [AskedForCodeEvent("machine")]

    def test_insert_code_correct_moves_to_win_room(self):
        obj = WinMachine(id="machine", code="0000", win_room_id="win", width=1.0, height=1.0)
        game = FakeGame(objects={"machine": obj})
        events = obj.insert_code("0000")(game)
        assert MovedToRoomEvent("win") in events

    def test_insert_code_wrong_returns_wrong_code_event(self):
        obj = WinMachine(id="machine", code="0000", win_room_id="win", width=1.0, height=1.0)
        game = FakeGame(objects={"machine": obj})
        events = obj.insert_code("9999")(game)
        assert events == [WrongCodeEvent()]


class TestInspectableObject:
    def test_interact_returns_inspected_event(self):
        obj = InspectableObject(id="painting", width=1.0, height=1.0)
        game = FakeGame()
        events = obj.interact(game)
        assert events == [InspectedEvent("painting")]


class TestPickableInspectableObject:
    def test_interact_picks_up(self):
        pos = Position(x=0.0, y=0.0)
        obj = PickableInspectableObject(id="note", width=1.0, height=1.0)
        game = _room_game("note", obj, pos)
        events = obj.interact(game)
        assert PickedUpEvent("note") in events

    def test_interact_inventory_inspects(self):
        obj = PickableInspectableObject(id="note", width=1.0, height=1.0)
        game = FakeGame(objects={"note": obj}, inventory=["note"])
        events = obj.interact_inventory(game)
        assert events == [InspectedEvent("note")]


class TestMoveToRoomAndAddToInventoryObject:
    def test_interact_moves_and_adds_to_inventory(self):
        obj = MoveToRoomAndAddToInventoryObject(room_id="garden", object_id="flower", width=1.0, height=1.0)
        game = FakeGame(rooms={"room1": {}})
        events = obj.interact(game)
        assert MovedToRoomEvent("garden") in events
        assert AddedToInventoryEvent("flower") in events
        assert game.current_room_id == "garden"
        assert "flower" in game.inventory
