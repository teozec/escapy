from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import pygame

from game_events import AskedForCodeEvent, GameEndedEvent, GameEvent, InspectedEvent
from game import Game
from protocols import InventoryInteractable, Placeable, Unlockable


@dataclass
class _NormalState:
    """Normal gameplay state."""

    pass


@dataclass
class _InsertCodeState:
    """State for inserting a code."""

    object_id: str
    text: str = ""


@dataclass
class _InspectState:
    """State for inspecting an object."""

    object_id: str
    surface: pygame.Surface
    rect: pygame.Rect


type _UIState = _NormalState | _InsertCodeState | _InspectState


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

        # Initialize display
        width = config["width"]
        height = config["height"]
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.fps = config["fps"]

        # Layout configuration (fractions of screen)
        self.game_area_horizontal_fraction = config.get(
            "game_area_horizontal_fraction", 0.85
        )
        self.game_area_vertical_fraction = config.get(
            "game_area_vertical_fraction", 0.85
        )
        self.inventory_columns = config.get("inventory_columns", 2)
        self.inventory_spacing_fraction = config.get("inventory_spacing_fraction", 0.05)

        # Calculate initial layout
        self._calculate_layout()

        # Load assets
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
        self._state: _UIState = _NormalState()

    def _calculate_layout(self) -> None:
        """Calculate all layout dimensions based on current screen size and fractions."""
        screen_width, screen_height = self.screen.get_size()

        # Calculate split lines based on fractions
        horizontal_split = round(screen_height * self.game_area_vertical_fraction)
        vertical_split = round(screen_width * self.game_area_horizontal_fraction)

        # Create subsurfaces (subsurface constructor takes a Rect)
        self.game_area = self.screen.subsurface(
            pygame.Rect(0, 0, vertical_split, horizontal_split)
        )
        self.message_area = self.screen.subsurface(
            pygame.Rect(
                0, horizontal_split, vertical_split, screen_height - horizontal_split
            )
        )
        self.inventory_area = self.screen.subsurface(
            pygame.Rect(vertical_split, 0, screen_width - vertical_split, screen_height)
        )

        # Calculate inventory layout
        inventory_width = self.inventory_area.get_width()
        self.inventory_object_spacing = (
            self.inventory_spacing_fraction * inventory_width
        )
        available_width = inventory_width - (
            self.inventory_object_spacing * (self.inventory_columns + 1)
        )
        self.inventory_object_size = available_width / self.inventory_columns

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
            elif isinstance(self._state, _InspectState):
                events.extend(self._handle_inspect_input(event))
            elif isinstance(self._state, _InsertCodeState):
                events.extend(self._handle_insert_code_input(event))
            else:  # NormalState
                events.extend(self._handle_normal_input(event))

        return events

    def _handle_normal_input(self, event: pygame.event.Event) -> list[GameEvent]:
        """Handle input when in NORMAL state."""
        events: list[GameEvent] = []

        if event.type == pygame.MOUSEBUTTONDOWN and not self.game.is_finished:
            click_pos = event.pos

            # Determine which area was clicked
            game_area_offset = self.game_area.get_abs_offset()
            game_area_abs_rect = self.game_area.get_rect(topleft=game_area_offset)

            inventory_offset = self.inventory_area.get_abs_offset()
            inventory_abs_rect = self.inventory_area.get_rect(topleft=inventory_offset)

            if game_area_abs_rect.collidepoint(click_pos):
                # Click in game area - check objects
                for object_id, object_rect in self.objects.items():
                    abs_rect = object_rect.move(game_area_offset)
                    if abs_rect.collidepoint(click_pos):
                        events = self.game.interact(object_id)

            elif inventory_abs_rect.collidepoint(click_pos):
                # Click in inventory area - check inventory objects
                for object_id, object_rect in self.inventory.items():
                    abs_rect = object_rect.move(inventory_offset)
                    if abs_rect.collidepoint(click_pos):
                        events = self.game.interact_inventory(object_id)
                        break
                else:
                    # Clicked in inventory area but not on any object
                    events = self.game.interact_inventory(None)

            # Clicks in message area are ignored

        return events

    def _handle_insert_code_input(self, event: pygame.event.Event) -> list[GameEvent]:
        """Handle input when in INSERT_CODE state."""
        if not isinstance(self._state, _InsertCodeState):
            return []

        events: list[GameEvent] = []

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                events = self.game.insert_code(self._state.object_id, self._state.text)
                self._state = _NormalState()
            elif event.key == pygame.K_ESCAPE:
                self._state = _NormalState()
            elif event.key == pygame.K_BACKSPACE:
                self._state.text = self._state.text[:-1]
            elif event.unicode and event.unicode.isprintable():
                self._state.text += event.unicode

        return events

    def _handle_inspect_input(self, event: pygame.event.Event) -> list[GameEvent]:
        """Handle input when in INSPECT state."""
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._state = _NormalState()

        return []

    def render(self):
        self._update_objects()

        # Draw room
        game_area_size = (self.game_area.get_width(), self.game_area.get_height())
        room_image = pygame.transform.scale(
            self.room_images[self.game.current_room_id],
            game_area_size,
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
        self.message_area.fill(pygame.Color(0, 0, 0))

        # Render state-specific overlays
        if isinstance(self._state, _InsertCodeState):
            self._render_insert_code_overlay()
        elif isinstance(self._state, _InspectState):
            self._render_inspect_overlay()

        pygame.display.flip()

    def _render_insert_code_overlay(self) -> None:
        """Render the code insertion overlay."""
        if not isinstance(self._state, _InsertCodeState):
            return

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        prompt_text = "Inserisci codice:"
        label = self.font.render(prompt_text, True, (255, 255, 255))

        box_width = int(self.screen.get_size()[0] * 0.6)
        box_height = 40
        box_x = (self.screen.get_size()[0] - box_width) // 2
        box_y = (self.screen.get_size()[1] - box_height) // 2

        label_x = (self.screen.get_size()[0] - label.get_width()) // 2
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

        text_surface = self.font.render(self._state.text, True, (0, 0, 0))
        text_x = box_x + 10
        text_y = box_y + (box_height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))

    def _render_inspect_overlay(self) -> None:
        """Render the inspect overlay."""
        if not isinstance(self._state, _InspectState):
            return

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self._state.surface, self._state.rect)

    def handle(self, events: list[GameEvent]) -> None:
        for event in events:
            match event:
                case GameEndedEvent():
                    self.is_running = False
                case AskedForCodeEvent(object_id=object_id):
                    self._state = _InsertCodeState(object_id=object_id)
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
        game_area_width = self.game_area.get_width()
        game_area_height = self.game_area.get_height()

        for id, position in self.game.rooms[self.game.current_room_id].items():
            object = self.game.objects[id]
            if not isinstance(object, Placeable):
                raise ValueError("object is not placeable")
            self.objects[id] = pygame.Rect(
                position.x * game_area_width,
                position.y * game_area_height,
                object.width * game_area_width,
                object.height * game_area_height,
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

        self._state = _InspectState(object_id=object_id, surface=surface, rect=rect)
