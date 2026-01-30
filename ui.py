from pathlib import Path
from typing import Protocol
import pygame
# import tkinter as tk

from game_events import GameEndedEvent, GameEvent
from game import Game
from protocols import InventoryInteractable, Placeable, Unlockable


class GameUi(Protocol):
    def init(self, game: Game) -> None:
        ...

    def tick(self) -> None:
        ...

    def input(self) -> list[GameEvent]:
        ...

    def handle(self, events: list[GameEvent]) -> None:
        ...

    def render(self) -> None:
        ...

    def quit(self) -> None:
        ...

    is_running: bool


class PyGameUi(GameUi):
    def __init__(self, config: dict) -> None:
        pygame.init()
        pygame.display.set_caption(config["title"])

        width = config["width"]
        height = config["height"]
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.horizontal_split_line = round(height * 0.85)
        self.vertical_split_line = round(width * 0.85)
        self.game_area_rect = pygame.Rect(
            0, 0, self.vertical_split_line, self.horizontal_split_line
        )
        self.message_area_rect = pygame.Rect(
            0,
            self.horizontal_split_line,
            self.vertical_split_line,
            height - self.horizontal_split_line,
        )
        self.inventory_area_rect = pygame.Rect(
            self.vertical_split_line, 0, width - self.vertical_split_line, height
        )
        self.game_area = self.screen.subsurface(self.game_area_rect)
        self.message_area = self.screen.subsurface(self.message_area_rect)
        self.inventory_area = self.screen.subsurface(self.inventory_area_rect)
        self.game_area_width = self.game_area.get_width()
        self.game_area_height = self.game_area.get_height()
        self.inventory_object_size = 0.6 * self.inventory_area_rect.width
        self.inventory_object_spacing = 0.05 * self.inventory_area_rect.width

        self.fps = config["fps"]

        assets_dir = Path(config["assets_dir"])
        self.room_images = {
            room: pygame.image.load(assets_dir / image).convert()
            for room, image in config["rooms"].items()
        }
        self.object_images = {
            object: pygame.image.load(assets_dir / image).convert_alpha()
            for object, image in config["objects"].items()
        }
        self.is_running = False

    def init(self, game: Game):
        self.game = game
        self._update_objects()
        self.is_running = True

    def tick(self):
        self.clock.tick(self.fps)

    def input(self) -> list[GameEvent]:
        events: list[GameEvent] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events = self.game.quit()

            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game.is_finished:
                if self.game_area_rect.collidepoint(event.pos):
                    pos = (
                        event.pos[0] - self.game_area_rect.left,
                        event.pos[1] - self.game_area_rect.top,
                    )
                    for object_id, object in self.objects.items():
                        if object.collidepoint(pos):
                            events = self.game.interact(object_id)

                elif self.inventory_area_rect.collidepoint(event.pos):
                    pos = (
                        event.pos[0] - self.inventory_area_rect.left,
                        event.pos[1] - self.inventory_area_rect.top,
                    )
                    for object_id, object in self.inventory.items():
                        if object.collidepoint(pos):
                            events = self.game.interact_inventory(object_id)
                            break
                    else:
                        events = self.game.interact_inventory(None)

        return events

    def render(self):
        self._update_objects()

        # Draw room
        room_image = pygame.transform.scale(
            self.room_images[self.game.current_room_id],
            (self.game_area_width, self.game_area_height),
        )  # TODO: remove transform from game loop if too slow
        self.game_area.blit(room_image, (0, 0))

        # Draw objects
        for object_id, rect in self.objects.items():
            image = pygame.transform.scale(
                self.object_images[self._get_repr(object_id)],
                (rect.width, rect.height),
            )  # TODO: remove transform from game loop if too slow
            self.game_area.blit(image, rect)

        # Draw inventory
        for object_id, rect in self.inventory.items():
            image = pygame.transform.scale(
                self.object_images[self._get_repr(object_id)],
                (rect.width, rect.height),
            )  # TODO: remove transform from game loop if too slow
            self.inventory_area.blit(image, rect)
            if object_id == self.game.in_hand_object_id:
                pygame.draw.rect(
                    self.inventory_area, pygame.Color(255, 255, 255), rect, 3
                )
            else:
                pygame.draw.rect(self.inventory_area, pygame.Color(0, 0, 0), rect, 3)

        # Draw message box
        # if events:
        # self.message_area.fill(pygame.Color(0, 0, 0))
        # self.message_area.blit(
        # self.font.render(str(events), True, (255, 255, 255)),
        # (self.message_area.get_width() * 0.05, self.message_area.get_height() * 0.4),
        # )

        pygame.display.flip()

    def handle(self, events: list[GameEvent]) -> None:
        for event in events:
            match event:
                case GameEndedEvent():
                    self.is_running = False
                case _:
                    pass

    def quit(self) -> None:
        pygame.quit()

    def _get_repr(self, object_id: str) -> str:
        object = self.game.objects[object_id]
        if isinstance(object, Unlockable):
            return f"{object_id}:{object.state}"
        return object_id

    def _update_objects(self):
        self.objects: dict[str, pygame.Rect] = {}
        for id, position in self.game.rooms[self.game.current_room_id].items():
            object = self.game.objects[id]
            if not isinstance(object, Placeable):
                raise ValueError("object is not placeable")
            self.objects[id] = pygame.Rect(
                position.x * self.game_area_width,
                position.y * self.game_area_height,
                object.width * self.game_area_width,
                object.height * self.game_area_height,
            )

        self.inventory: dict[str, pygame.Rect] = {}
        for i, id in enumerate(self.game.inventory):
            object = self.game.objects[id]
            if not isinstance(object, InventoryInteractable):
                raise ValueError("object is not inventory interactable")
            self.inventory[id] = pygame.Rect(
                0.1 * self.inventory_area_rect.width,
                i * (self.inventory_object_size + self.inventory_object_spacing)
                + self.inventory_object_spacing,
                self.inventory_object_size,
                self.inventory_object_size,
            )
