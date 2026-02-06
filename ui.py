from pathlib import Path
from typing import Protocol
import pygame

from game_events import AskedForCodeEvent, GameEndedEvent, GameEvent, InspectedEvent
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
        self.inventory_columns = 2
        self.inventory_object_spacing = 0.05 * self.inventory_area_rect.width
        available_width = self.inventory_area_rect.width - (
            self.inventory_object_spacing * (self.inventory_columns + 1)
        )
        self.inventory_object_size = available_width / self.inventory_columns

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
        self._ask_for_code: str | None = None
        self._code_prompt_active = False
        self._code_prompt_text = ""
        self._code_prompt_object_id: str | None = None
        self._inspect_active = False
        self._inspect_object_id: str | None = None
        self._inspect_surface: pygame.Surface | None = None
        self._inspect_rect: pygame.Rect | None = None

    def init(self, game: Game):
        self.game = game
        self._update_objects()
        self.is_running = True

    def tick(self):
        self.clock.tick(self.fps)

    def input(self) -> list[GameEvent]:
        events: list[GameEvent] = []

        if self._ask_for_code is not None and not self._code_prompt_active:
            self._code_prompt_active = True
            self._code_prompt_text = ""
            self._code_prompt_object_id = self._ask_for_code
            self._ask_for_code = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events = self.game.quit()

            elif self._inspect_active:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._inspect_active = False
                    self._inspect_object_id = None
                    self._inspect_surface = None
                    self._inspect_rect = None

            elif self._code_prompt_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self._code_prompt_object_id is not None:
                            events = self.game.insert_code(
                                self._code_prompt_object_id, self._code_prompt_text
                            )
                        self._code_prompt_active = False
                        self._code_prompt_text = ""
                        self._code_prompt_object_id = None
                    elif event.key == pygame.K_ESCAPE:
                        self._code_prompt_active = False
                        self._code_prompt_text = ""
                        self._code_prompt_object_id = None
                    elif event.key == pygame.K_BACKSPACE:
                        self._code_prompt_text = self._code_prompt_text[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        self._code_prompt_text += event.unicode

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
        self.message_area.fill(pygame.Color(0, 0, 0))
        # self.message_area.blit(
        # self.font.render(str(events), True, (255, 255, 255)),
        # (self.message_area.get_width() * 0.05, self.message_area.get_height() * 0.4),
        # )

        if self._code_prompt_active:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            prompt_text = "Inserisci codice:"
            label = self.font.render(prompt_text, True, (255, 255, 255))

            box_width = int(self.screen.get_width() * 0.6)
            box_height = 40
            box_x = (self.screen.get_width() - box_width) // 2
            box_y = (self.screen.get_height() - box_height) // 2

            label_x = (self.screen.get_width() - label.get_width()) // 2
            label_y = box_y - 40
            self.screen.blit(label, (label_x, label_y))

            pygame.draw.rect(
                self.screen,
                pygame.Color(255, 255, 255),
                (box_x, box_y, box_width, box_height),
            )
            pygame.draw.rect(
                self.screen,
                pygame.Color(0, 0, 0),
                (box_x, box_y, box_width, box_height),
                2,
            )

            text_surface = self.font.render(self._code_prompt_text, True, (0, 0, 0))
            text_x = box_x + 10
            text_y = box_y + (box_height - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))

        if self._inspect_active and self._inspect_surface and self._inspect_rect:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(self._inspect_surface, self._inspect_rect)

        pygame.display.flip()

    def handle(self, events: list[GameEvent]) -> None:
        for event in events:
            match event:
                case GameEndedEvent():
                    self.is_running = False
                case AskedForCodeEvent(object_id=object_id):
                    self._ask_for_code = object_id
                case InspectedEvent(object_id=id):
                    self._show_inspect(id)
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
            col = i % self.inventory_columns
            row = i // self.inventory_columns
            x = self.inventory_object_spacing + col * (
                self.inventory_object_size + self.inventory_object_spacing
            )
            y = (
                row * (self.inventory_object_size + self.inventory_object_spacing)
                + self.inventory_object_spacing
            )
            self.inventory[id] = pygame.Rect(
                x,
                y,
                self.inventory_object_size,
                self.inventory_object_size,
            )

    def _show_inspect(self, object_id: str) -> None:
        image = self.object_images[self._get_repr(object_id)]
        screen_w, screen_h = self.screen.get_size()
        max_w = int(screen_w * 0.8)
        max_h = int(screen_h * 0.8)
        img_w, img_h = image.get_size()
        if img_w == 0 or img_h == 0:
            return
        scale = min(max_w / img_w, max_h / img_h)
        target_w = max(1, int(img_w * scale))
        target_h = max(1, int(img_h * scale))
        surface = pygame.transform.smoothscale(image, (target_w, target_h))
        rect = surface.get_rect(center=(screen_w // 2, screen_h // 2))

        self._inspect_active = True
        self._inspect_object_id = object_id
        self._inspect_surface = surface
        self._inspect_rect = rect
