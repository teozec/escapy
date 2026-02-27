from escapy.commands import add_to_inventory, ask_for_code, combine, move_to_room
from escapy.mixins import DecodableMixin
from escapy.protocols import Decodable, Interactable, InventoryInteractable, Placeable


class MoveToRoomAndAddToInventoryObject(Interactable, Placeable):
    """A clickable area that moves the player to another room and adds an object to the inventory.

    Args:
        room_id: Destination room identifier.
        object_id: Object to add to the inventory on interaction.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, room_id: str, object_id: str, width: float, height: float):
        self.interact = combine(move_to_room(room_id), add_to_inventory(object_id))
        self.width = width
        self.height = height


class WinMachine(DecodableMixin, InventoryInteractable, Decodable, Placeable):
    """A special object that ends (wins) the game when the correct code is entered.

    Interacting with it from the inventory triggers a code prompt.  A
    correct code moves the player to the designated win room.

    Args:
        id: Unique object identifier.
        code: The winning code string.
        win_room_id: Room to transition to upon success.
        width: Normalised width.
        height: Normalised height.
    """

    def __init__(self, id: str, code: str, win_room_id: str, width: float, height: float):
        self.interact_inventory = ask_for_code(id)
        self.code = code
        self.on_decode = move_to_room(win_room_id)
        self.width = width
        self.height = height
