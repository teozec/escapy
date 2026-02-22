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

from typing import Literal

from ..events import UnlockedEvent, WrongCodeEvent
from ..mixins import DecodableMixin, UnlockableMixin
from ..protocols import Command
from ._test_helpers import FakeGame


class ConcreteUnlockable(UnlockableMixin):
    """Concrete class that uses UnlockableMixin for testing."""

    state: Literal["locked", "unlocked"] = "locked"

    def __init__(self, on_unlock: Command):
        self.on_unlock = on_unlock


class ConcreteDecodable(DecodableMixin):
    """Concrete class that uses DecodableMixin for testing."""

    def __init__(self, code: str, on_decode: Command):
        self.code = code
        self.on_decode = on_decode


class TestUnlockableMixin:
    def test_unlock_sets_state_to_unlocked(self):
        obj = ConcreteUnlockable(on_unlock=lambda _: [])
        obj.unlock()
        assert obj.state == "unlocked"

    def test_unlock_returns_on_unlock_command(self):
        called = []

        def on_unlock(game):
            called.append(True)
            return []

        obj = ConcreteUnlockable(on_unlock=on_unlock)
        cmd = obj.unlock()
        game = FakeGame()
        cmd(game)
        assert called == [True]

    def test_unlock_command_result_is_returned(self):
        sentinel = UnlockedEvent(object_id="safe")
        obj = ConcreteUnlockable(on_unlock=lambda _: [sentinel])
        cmd = obj.unlock()
        game = FakeGame()
        events = cmd(game)
        assert events == [sentinel]


class TestDecodableMixin:
    def test_correct_code_returns_on_decode_command(self):
        sentinel = UnlockedEvent(object_id="safe")
        obj = ConcreteDecodable(code="1234", on_decode=lambda _: [sentinel])
        cmd = obj.insert_code("1234")
        game = FakeGame()
        events = cmd(game)
        assert events == [sentinel]

    def test_wrong_code_returns_wrong_code_event(self):
        obj = ConcreteDecodable(code="1234", on_decode=lambda _: [])
        cmd = obj.insert_code("wrong")
        game = FakeGame()
        events = cmd(game)
        assert events == [WrongCodeEvent()]

    def test_empty_string_is_wrong_code(self):
        obj = ConcreteDecodable(code="1234", on_decode=lambda _: [])
        cmd = obj.insert_code("")
        game = FakeGame()
        events = cmd(game)
        assert events == [WrongCodeEvent()]

    def test_code_is_case_sensitive(self):
        obj = ConcreteDecodable(code="ABCD", on_decode=lambda _: [])
        cmd = obj.insert_code("abcd")
        game = FakeGame()
        events = cmd(game)
        assert events == [WrongCodeEvent()]
