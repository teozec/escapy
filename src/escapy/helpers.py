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

from .mixins import GameMixins
from .protocols import (
    GameProtocol,
    Interactable,
    InventoryInteractable,
    Placeable,
    Unlockable,
)


def build_protocol(
    protocol_type: Literal["Interactable", "InventoryInteractable", "Placeable", "Unlockable"],
    **kwargs,
) -> GameProtocol:
    match protocol_type:
        case "Interactable":
            obj = type("InteractableImpl", (Interactable,), {"interact": kwargs["interact"]})()

        case "InventoryInteractable":
            obj = type(
                "InventoryInteractableImpl",
                (InventoryInteractable,),
                {"inventory_interact": kwargs["interact_inventory"]},
            )()

        case "Placeable":
            obj = type(
                "PlaceableImpl",
                (Placeable,),
                {"width": kwargs["width"], "height": kwargs["weight"]},
            )()

        case "Unlockable":
            obj = type(
                "UnlockableImpl",
                (Unlockable,),
                {"state": "locked", "on_unlock": kwargs["on_unlock"]},
            )()

        case _:
            raise ValueError("Unknown protocol type")

    return obj


def build_entity(name: str, mixins: tuple[type[GameMixins]], protocols: list[GameProtocol]):
    attrs = {}
    for protocol in protocols:
        if isinstance(protocol, Interactable):
            attrs["interact"] = protocol.interact
        if isinstance(protocol, InventoryInteractable):
            attrs["interact_inventory"] = protocol.interact_inventory
        if isinstance(protocol, Placeable):
            attrs["width"] = protocol.width
            attrs["height"] = protocol.height
        if isinstance(protocol, Unlockable):
            attrs["state"] = protocol.state
            attrs["on_unlock"] = protocol.on_unlock

    return type(name, mixins, attrs)
