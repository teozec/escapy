import json
from pathlib import Path
import pygame
from typing import Literal, Protocol

# ============================================================
# GAME LOGIC LAYER
# ============================================================
class Object(Protocol):
    width: float
    height: float

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def interact(self) -> str | None:
        ...

class PickableObject(Object):
    def __init__(self, width: float, height: float):
        super().__init__(width, height)

    def interact(self) -> str | None:
        pass


class Door(Object):
    def __init__(self, width: float, height: float, state: Literal["open", "closed"]):
        super().__init__(width, height)
        self.state = state

    def interact(self) -> str | None:
        if self.state == "closed":
            self.state = "open"
            return "opened"
        return None


class Room:
    def __init__(self, id: str, objects: dict[str, tuple[Object, tuple[float, float]]]):
        self.id = id
        self.objects = objects

    def interact(self, object_id: str) -> str | None:
        object = self.objects[object_id]
        return object[0].interact()


class Game:
    def __init__(self):
        self.rooms = [Room(
                "study",
                {
                    "door": (Door(0.15, 0.25, "closed"), (0.7, 0.7)),
                    "key": (PickableObject(0.05, 0.05), (0.2, 0.2)),
                },
            )
        ]
        self.current_room = self.rooms[0]
        self.is_finished = False
        self.inventory: dict[str, Object] = {}

    def interact(self, object_id: str, in_hand_object_id: str | None = None) -> str | None:
        try:
            object, _location = self.current_room.objects[object_id]
        except KeyError:
            return None

        if in_hand_object_id and in_hand_object_id not in self.inventory:
            return None

        if isinstance(object, PickableObject):
            self.current_room.objects.pop(object_id)
            self.inventory[object_id] = object
            return

        if object_id == "door" and isinstance(object, Door):
            if object.state == "open":
                self.is_finished = True
                return "win"
            if "key" not in self.inventory:
                return "locked"

        return self.current_room.interact(object_id)



# ============================================================
# PRESENTATION LAYER
# ============================================================
WIDTH = 800
HEIGHT = 600
FPS = 60

def get_image_key(object_id: str, object: Object):
    if isinstance(object, Door):
        return f"{object_id}:{object.state}"
    return object_id

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    
    horizontal_split_line = round(HEIGHT * 0.85)
    vertical_split_line = round(WIDTH * 0.85)
    game_area_rect = pygame.Rect(0, 0, vertical_split_line, horizontal_split_line)
    message_area_rect = pygame.Rect(0, horizontal_split_line, vertical_split_line, HEIGHT - horizontal_split_line)
    inventory_area_rect = pygame.Rect(vertical_split_line, 0, WIDTH - vertical_split_line, HEIGHT)
    game_area = screen.subsurface(game_area_rect)
    message_area = screen.subsurface(message_area_rect)
    inventory_area = screen.subsurface(inventory_area_rect)

    with open("config.json") as f:
        config = json.load(f)

    # --------------------------------------------------------
    # LOAD ASSETS
    # --------------------------------------------------------
    assets_dir = Path("assets")
    room_images = {
        room: pygame.image.load(assets_dir / image).convert()
        for room, image in config["images"]["rooms"].items()
    }
    object_images = {
        object: pygame.image.load(assets_dir / image).convert_alpha()
        for object, image in config["images"]["objects"].items()
    }


    # --------------------------------------------------------
    # CREATE GAME
    # --------------------------------------------------------
    game = Game()


    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------
    running = True
    while running:
        clock.tick(FPS)
        game_area_width = game_area.get_width()
        game_area_height = game_area.get_height()

        objects = {
            id: {
                "object": object,
                "rect": pygame.Rect(x * game_area_width, y * game_area_height, object.width * game_area_width, object.height * game_area_height)
            } for id,  (object, (x, y)) in game.current_room.objects.items()
        }

        inventory_object_size = 0.8 * inventory_area_rect.width
        inventory_object_spacing = 0.05 * inventory_area_rect.width
        inventory = {
            id: {
                "object": object,
                "rect": pygame.Rect(0.1 * inventory_area_rect.width, i * (inventory_object_size + inventory_object_spacing) + inventory_object_spacing, inventory_object_size, inventory_object_size)
            } for i, (id, object) in enumerate(game.inventory.items())
        }
            

        message: str | None = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.is_finished:
                if game_area_rect.collidepoint(event.pos):
                    pos = (event.pos[0] - game_area_rect.top, event.pos[1] - game_area_rect.left)
                    for object_id, object in objects.items():
                        if object["rect"].collidepoint(pos):
                            message = game.interact(object_id)


        # Draw room
        room_image = pygame.transform.scale(room_images[game.current_room.id], (game_area_width, game_area_height)) # TODO: remove transform from game loop if too slow
        game_area.blit(room_image, (0, 0))

        # Draw objects
        for object_id, object in objects.items():
            rect = object["rect"]
            image = pygame.transform.scale(object_images[get_image_key(object_id, object["object"])], (rect.width, rect.height)) # TODO: remove transform from game loop if too slow
            game_area.blit(image, rect)

        # Draw inventory
        for object_id, object in inventory.items():
            rect = object["rect"]
            image = pygame.transform.scale(object_images[get_image_key(object_id, object["object"])], (rect.width, rect.height)) # TODO: remove transform from game loop if too slow
            inventory_area.blit(image, rect)

        # Draw message box
        if message:
            message_area.fill(pygame.Color(0, 0, 0))
            message_area.blit(font.render(message, True, (255, 255, 255)), (message_area.get_width() * 0.05, message_area.get_height() * 0.4))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
