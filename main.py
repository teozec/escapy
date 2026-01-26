import json
from pathlib import Path
import pygame

from game_events import GameEvent
from game import Game
from game_types import Position
from interact import no_op, reveal
from objects import PickableObject, SelfKeyLock
from protocols import Interactable, InventoryInteractable, Placeable, Unlockable

WIDTH = 800
HEIGHT = 600
FPS = 60


def get_image_key(object_id: str, object: object):
    if isinstance(object, Unlockable):
        return f"{object_id}:{object.state}"
    return object_id


def get_config(path: Path) -> dict:
    with open(path) as f:
        config = json.load(f)

    assets_dir = Path("assets")
    room_images = {
        room: pygame.image.load(assets_dir / image).convert()
        for room, image in config["images"]["rooms"].items()
    }
    object_images = {
        object: pygame.image.load(assets_dir / image).convert_alpha()
        for object, image in config["images"]["objects"].items()
    }

    return {
        "room_images": room_images,
        "object_images": object_images,
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    horizontal_split_line = round(HEIGHT * 0.85)
    vertical_split_line = round(WIDTH * 0.85)
    game_area_rect = pygame.Rect(0, 0, vertical_split_line, horizontal_split_line)
    message_area_rect = pygame.Rect(
        0, horizontal_split_line, vertical_split_line, HEIGHT - horizontal_split_line
    )
    inventory_area_rect = pygame.Rect(
        vertical_split_line, 0, WIDTH - vertical_split_line, HEIGHT
    )
    game_area = screen.subsurface(game_area_rect)
    message_area = screen.subsurface(message_area_rect)
    inventory_area = screen.subsurface(inventory_area_rect)

    config = get_config(Path("config.json"))
    room_images = config["room_images"]
    object_images = config["object_images"]

    objects = {
        "a1-knife": PickableObject("a1-knife", 0.05, 0.05),
        "a2-poster": SelfKeyLock(
            id="a2-poster",
            key_id="a1-knife",
            on_unlock=reveal("a2-key", "room1", Position(x=0.75, y=0.75)),
            width=0.15,
            height=0.25,
        ),
        "a2-key": PickableObject("a2-key", 0.03, 0.03),
        "a3-chest": SelfKeyLock(
            id="a3-chest", key_id="a2-key", on_unlock=no_op(), width=0.2, height=0.15
        ),
    }

    rooms = {
        "room1": {
            "a1-knife": Position(x=0.2, y=0.2),
            "a2-poster": Position(x=0.7, y=0.7),
            "a3-chest": Position(x=0.4, y=0.4),
        }
    }

    game = Game(objects, rooms, [], "room1")

    running = True
    while running:
        clock.tick(FPS)
        game_area_width = game_area.get_width()
        game_area_height = game_area.get_height()

        objects = {}
        for id, position in game.rooms[game.current_room_id].items():
            object = game.objects[id]
            if not isinstance(object, Placeable) or not isinstance(
                object, Interactable
            ):
                raise ValueError("object is not placeable")
            objects[id] = {
                "object": game.objects[id],
                "rect": pygame.Rect(
                    position.x * game_area_width,
                    position.y * game_area_height,
                    object.width * game_area_width,
                    object.height * game_area_height,
                ),
            }

        inventory_object_size = 0.6 * inventory_area_rect.width
        inventory_object_spacing = 0.05 * inventory_area_rect.width
        inventory = {}
        for i, id in enumerate(game.inventory):
            object = game.objects[id]
            if not isinstance(object, InventoryInteractable):
                raise ValueError("object is not inventory interactable")
            inventory[id] = {
                "object": object,
                "rect": pygame.Rect(
                    0.1 * inventory_area_rect.width,
                    i * (inventory_object_size + inventory_object_spacing)
                    + inventory_object_spacing,
                    inventory_object_size,
                    inventory_object_size,
                ),
            }

        events: list[GameEvent] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.is_finished:
                if game_area_rect.collidepoint(event.pos):
                    pos = (
                        event.pos[0] - game_area_rect.left,
                        event.pos[1] - game_area_rect.top,
                    )
                    for object_id, object in objects.items():
                        if object["rect"].collidepoint(pos):
                            events = game.interact(object_id)

                elif inventory_area_rect.collidepoint(event.pos):
                    pos = (
                        event.pos[0] - inventory_area_rect.left,
                        event.pos[1] - inventory_area_rect.top,
                    )
                    for object_id, object in inventory.items():
                        if object["rect"].collidepoint(pos):
                            events = game.interact_inventory(object_id)
                            break
                    else:
                        events = game.interact_inventory(None)

                print(events)

        # Draw room
        room_image = pygame.transform.scale(
            room_images[game.current_room_id], (game_area_width, game_area_height)
        )  # TODO: remove transform from game loop if too slow
        game_area.blit(room_image, (0, 0))

        # Draw objects
        for object_id, object in objects.items():
            rect = object["rect"]
            image = pygame.transform.scale(
                object_images[get_image_key(object_id, object["object"])],
                (rect.width, rect.height),
            )  # TODO: remove transform from game loop if too slow
            game_area.blit(image, rect)

        # Draw inventory
        for object_id, object in inventory.items():
            rect = object["rect"]
            image = pygame.transform.scale(
                object_images[get_image_key(object_id, object["object"])],
                (rect.width, rect.height),
            )  # TODO: remove transform from game loop if too slow
            inventory_area.blit(image, rect)
            if object_id == game.in_hand_object_id:
                pygame.draw.rect(inventory_area, pygame.Color(255, 255, 255), rect, 3)
            else:
                pygame.draw.rect(inventory_area, pygame.Color(0, 0, 0), rect, 3)

        # Draw message box
        if events:
            message_area.fill(pygame.Color(0, 0, 0))
            message_area.blit(
                font.render(str(events), True, (255, 255, 255)),
                (message_area.get_width() * 0.05, message_area.get_height() * 0.4),
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
