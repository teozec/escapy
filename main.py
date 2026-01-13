import json
from operator import itemgetter
from pathlib import Path
import pygame
from typing import Protocol

# ============================================================
# GAME LOGIC LAYER
# ============================================================
class Object(Protocol):
    id: str
    width: float
    height: float

    def __init__(self, id: str, width: float, height: float):
        self.id = id
        self.width = width
        self.height = height

    def interact(self) -> str:
        ...


class Door(Object):
    def __init__(self, id: str, width: float, height: float):
        super().__init__(id, width, height)

    def interact(self) -> str:
        ...


class Room:
    def __init__(self, id: str, objects: list[tuple[Object, tuple[float, float]]]):
        self.id = id
        self.objects = objects

    def interact(self, object_id: str):
        for (object, _) in self.objects:
            if object.id == object_id:
                return object.interact()
        return None


class Game:
    def __init__(self):
        self.rooms = [Room(
                "study",
                [(Door("door", 0.1, 0.12), (0.8, 0.8))],
            )
        ]
        self.current_room = self.rooms[0]
        self.is_finished = False

    def interact(self, object_id: str):
        if object_id == "door":
            self.is_finished = True
            return "win"
        return self.current_room.interact(object_id)



# ============================================================
# PRESENTATION LAYER
# ============================================================
WIDTH = 800
HEIGHT = 600
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    
    split_line = round(HEIGHT * 0.85)
    game_area = screen.subsurface((0, 0, WIDTH, split_line))
    message_area = screen.subsurface((0, split_line, WIDTH, HEIGHT - split_line))

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
            object.id: {
                "rect": pygame.Rect(x * game_area_width, y * game_area_height, object.width * game_area_width, object.height * game_area_height)
            } for object, (x, y) in game.current_room.objects
        }
            

        message: str | None = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.is_finished:
                for object_id, object in objects.items():
                    if object["rect"].collidepoint(event.pos):
                        message = game.interact(object_id)


        # Draw room
        room_image = pygame.transform.scale(room_images[game.current_room.id], (game_area_width, game_area_height)) # TODO: remove transform from game loop if too slow
        game_area.blit(room_image, (0, 0))

        # Draw objects
        for object_id, object in objects.items():
            rect = object["rect"]
            image = pygame.transform.scale(object_images[object_id], (rect.width, rect.height)) # TODO: remove transform from game loop if too slow
            game_area.blit(image, rect)

        # Draw message box
        if message:
            message_area.blit(font.render(message, True, (255, 255, 255)), (message_area.get_width() * 0.05, message_area.get_height() * 0.4))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
