from typing import Callable

from game_events import GameEvent


MessageProvider = Callable[[GameEvent], str | None]


def dict_message_provider(messages: dict[str, str]) -> MessageProvider:
    return lambda event: messages.get(repr(event), None)
