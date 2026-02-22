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

from ..commands import (
    add_to_inventory,
    ask_for_code,
    chain,
    combine,
    cond,
    inspect,
    key_lock,
    locked,
    move_to_room,
    no_op,
    pick,
    put_in_hand,
    reveal,
    simple_lock,
)
from ..events import (
    AddedToInventoryEvent,
    AskedForCodeEvent,
    InspectedEvent,
    InteractedWithLockedEvent,
    MovedToRoomEvent,
    PickedUpEvent,
    PutInHandEvent,
    RevealedEvent,
    UnlockedEvent,
)
from ..types import Position
from ._test_helpers import FakeGame


class _FakeUnlockable:
    """Minimal stub satisfying the Unlockable protocol for command tests."""

    def __init__(self, on_unlock=None):
        self.state = "locked"
        self.on_unlock = on_unlock or (lambda _: [])

    def unlock(self):
        self.state = "unlocked"
        return self.on_unlock


class TestNoOp:
    def test_returns_empty_list(self):
        game = FakeGame()
        result = no_op()(game)
        assert result == []


class TestPick:
    def test_removes_object_from_room(self):
        game = FakeGame(rooms={"room": {"apple": Position(x=0.0, y=0.0)}}, current_room_id="room")
        pick("apple")(game)
        assert "apple" not in game.rooms["room"]

    def test_adds_object_to_inventory(self):
        game = FakeGame(rooms={"room": {"apple": Position(x=0.0, y=0.0)}}, current_room_id="room")
        pick("apple")(game)
        assert "apple" in game.inventory

    def test_returns_picked_up_event(self):
        game = FakeGame(rooms={"room": {"apple": Position(x=0.0, y=0.0)}}, current_room_id="room")
        events = pick("apple")(game)
        assert events == [PickedUpEvent(object_id="apple")]


class TestPutInHand:
    def test_sets_in_hand_object_id(self):
        game = FakeGame()
        put_in_hand("sword")(game)
        assert game.in_hand_object_id == "sword"

    def test_returns_put_in_hand_event(self):
        game = FakeGame()
        events = put_in_hand("sword")(game)
        assert events == [PutInHandEvent(object_id="sword")]

    def test_replaces_previous_in_hand_object(self):
        game = FakeGame(in_hand_object_id="shield")
        put_in_hand("sword")(game)
        assert game.in_hand_object_id == "sword"


class TestSimpleLock:
    def test_unlocks_when_locked(self):
        obj = _FakeUnlockable()
        game = FakeGame(objects={"chest": obj})
        events = simple_lock("chest")(game)
        assert any(isinstance(e, UnlockedEvent) for e in events)
        assert obj.state == "unlocked"

    def test_no_events_when_already_unlocked(self):
        obj = _FakeUnlockable()
        obj.state = "unlocked"
        game = FakeGame(objects={"chest": obj})
        events = simple_lock("chest")(game)
        assert events == []

    def test_on_unlock_command_is_called(self):
        called = []

        def on_unlock_cmd(game):
            called.append(True)
            return []

        obj = _FakeUnlockable(on_unlock=on_unlock_cmd)
        game = FakeGame(objects={"chest": obj})
        simple_lock("chest")(game)
        assert called == [True]


class TestKeyLock:
    def test_unlocks_when_key_in_hand(self):
        obj = _FakeUnlockable()
        game = FakeGame(objects={"door": obj}, in_hand_object_id="gold_key")
        events = key_lock("door", key_id="gold_key")(game)
        assert any(isinstance(e, UnlockedEvent) for e in events)

    def test_no_unlock_without_key(self):
        obj = _FakeUnlockable()
        game = FakeGame(objects={"door": obj}, in_hand_object_id=None)
        events = key_lock("door", key_id="gold_key")(game)
        assert not any(isinstance(e, UnlockedEvent) for e in events)

    def test_no_unlock_with_wrong_key(self):
        obj = _FakeUnlockable()
        game = FakeGame(objects={"door": obj}, in_hand_object_id="silver_key")
        events = key_lock("door", key_id="gold_key")(game)
        assert not any(isinstance(e, UnlockedEvent) for e in events)

    def test_no_unlock_when_already_unlocked(self):
        obj = _FakeUnlockable()
        obj.state = "unlocked"
        game = FakeGame(objects={"door": obj}, in_hand_object_id="gold_key")
        events = key_lock("door", key_id="gold_key")(game)
        assert not any(isinstance(e, UnlockedEvent) for e in events)


class TestAskForCode:
    def test_returns_asked_for_code_event(self):
        game = FakeGame()
        events = ask_for_code("safe")(game)
        assert events == [AskedForCodeEvent(object_id="safe")]


class TestLocked:
    def test_returns_interacted_with_locked_event(self):
        game = FakeGame()
        events = locked("safe")(game)
        assert events == [InteractedWithLockedEvent(object_id="safe")]


class TestInspect:
    def test_returns_inspected_event(self):
        game = FakeGame()
        events = inspect("painting")(game)
        assert events == [InspectedEvent(object_id="painting")]


class TestReveal:
    def test_adds_object_to_room(self):
        game = FakeGame(rooms={"room1": {}})
        pos = Position(x=5.0, y=3.0)
        reveal("secret_key", "room1", pos)(game)
        assert "secret_key" in game.rooms["room1"]
        assert game.rooms["room1"]["secret_key"] == pos

    def test_returns_revealed_event(self):
        game = FakeGame(rooms={"room1": {}})
        pos = Position(x=5.0, y=3.0)
        events = reveal("secret_key", "room1", pos)(game)
        assert events == [RevealedEvent(object_id="secret_key", room_id="room1", position=pos)]


class TestMoveToRoom:
    def test_changes_current_room_id(self):
        game = FakeGame(current_room_id="room1")
        move_to_room("room2")(game)
        assert game.current_room_id == "room2"

    def test_returns_moved_to_room_event(self):
        game = FakeGame()
        events = move_to_room("lobby")(game)
        assert events == [MovedToRoomEvent(room_id="lobby")]


class TestAddToInventory:
    def test_adds_object_to_inventory(self):
        game = FakeGame()
        add_to_inventory("coin")(game)
        assert "coin" in game.inventory

    def test_returns_added_to_inventory_event(self):
        game = FakeGame()
        events = add_to_inventory("coin")(game)
        assert events == [AddedToInventoryEvent(object_id="coin")]


class TestCombine:
    def test_executes_all_commands(self):
        game = FakeGame(rooms={"room1": {}})
        cmd = combine(
            add_to_inventory("coin"),
            move_to_room("room2"),
        )
        events = cmd(game)
        assert AddedToInventoryEvent(object_id="coin") in events
        assert MovedToRoomEvent(room_id="room2") in events

    def test_returns_all_events_in_order(self):
        game = FakeGame(rooms={"room1": {}})
        cmd = combine(move_to_room("room2"), move_to_room("room3"))
        events = cmd(game)
        assert events == [MovedToRoomEvent("room2"), MovedToRoomEvent("room3")]

    def test_empty_combine_returns_empty(self):
        game = FakeGame()
        events = combine()(game)
        assert events == []


class TestCond:
    def test_executes_matching_clause(self):
        game = FakeGame()
        cmd = cond(
            (lambda: True, ask_for_code("safe")),
        )
        events = cmd(game)
        assert events == [AskedForCodeEvent(object_id="safe")]

    def test_skips_non_matching_clause(self):
        game = FakeGame()
        cmd = cond(
            (lambda: False, ask_for_code("safe")),
        )
        events = cmd(game)
        assert events == []

    def test_only_first_matching_clause_executes(self):
        game = FakeGame()
        cmd = cond(
            (lambda: True, ask_for_code("safe1")),
            (lambda: True, ask_for_code("safe2")),
        )
        events = cmd(game)
        assert events == [AskedForCodeEvent(object_id="safe1")]

    def test_falls_through_to_second_clause(self):
        game = FakeGame()
        cmd = cond(
            (lambda: False, ask_for_code("safe1")),
            (lambda: True, ask_for_code("safe2")),
        )
        events = cmd(game)
        assert events == [AskedForCodeEvent(object_id="safe2")]


class TestChain:
    def test_executes_all_true_conditions(self):
        game = FakeGame(rooms={"room1": {}})
        cmd = chain(
            (lambda _: True, add_to_inventory("coin")),
            (lambda _: True, move_to_room("room2")),
        )
        events = cmd(game)
        assert AddedToInventoryEvent("coin") in events
        assert MovedToRoomEvent("room2") in events

    def test_later_condition_sees_earlier_events(self):
        obj = _FakeUnlockable()
        game = FakeGame(objects={"box": obj})

        # Second clause fires only if no UnlockedEvent was produced
        cmd = chain(
            (lambda _: True, simple_lock("box")),
            (
                lambda events: not any(isinstance(e, UnlockedEvent) and e.object_id == "box" for e in events),
                locked("box"),
            ),
        )
        events = cmd(game)
        # simple_lock should produce UnlockedEvent, so locked() should NOT fire
        assert any(isinstance(e, UnlockedEvent) for e in events)
        assert not any(isinstance(e, InteractedWithLockedEvent) for e in events)

    def test_chain_with_false_first_condition(self):
        game = FakeGame()
        cmd = chain(
            (lambda _: False, ask_for_code("safe")),
            (lambda _: True, inspect("note")),
        )
        events = cmd(game)
        assert events == [InspectedEvent("note")]
