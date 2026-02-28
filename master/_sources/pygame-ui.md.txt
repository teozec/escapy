# Pygame UI

`escapy.pygame.PyGameUi` is the included UI backend.  It renders the game using [pygame](https://www.pygame.org/) and handles player input (mouse clicks for room/inventory interaction, keyboard input for code prompts).

## Configuration

`PyGameUi` accepts a configuration dictionary and a `MessageProvider`:

```python
from escapy.pygame import PyGameUi
from escapy.messages import dict_message_provider

config_ui = { ... }
message_provider = dict_message_provider(messages)
ui = PyGameUi(config_ui, message_provider)
```

### Required keys

| Key | Type | Description |
|---|---|---|
| `"title"` | `str` | Window title |
| `"width"` | `int` | Window width in pixels |
| `"height"` | `int` | Window height in pixels |
| `"fps"` | `int` | Target frames per second |
| `"assets_dir"` | `str` | Path to the assets directory |
| `"rooms"` | `dict[str, str]` | Mapping of room IDs to background image filenames |
| `"objects"` | `dict[str, str]` | Mapping of object image keys to image filenames |

### Optional keys

| Key | Type | Default | Description |
|---|---|---|---|
| `"game_area_horizontal_fraction"` | `float` | `0.85` | Fraction of screen width for the game area |
| `"game_area_vertical_fraction"` | `float` | `0.85` | Fraction of screen height for the game area |
| `"inventory_columns"` | `int` | `2` | Number of columns in the inventory grid |
| `"inventory_spacing_fraction"` | `float` | `0.05` | Spacing between inventory items (fraction of sidebar width) |

### Object image keys

For most objects, the image key is simply the object ID:

```json
{ "knife": "knife.png" }
```

For `Unlockable` objects, the UI looks up images by `"id:state"`:

```json
{
    "safe:locked": "safe-locked.png",
    "safe:unlocked": "safe-unlocked.png"
}
```

## Screen layout

```
┌──────────────────────────────────┬──────────┐
│                                  │          │
│          Game Area               │ Inventory│
│  (room background + objects)     │ Sidebar  │
│                                  │          │
│                                  │          │
├──────────────────────────────────┤          │
│         Message Bar              │          │
└──────────────────────────────────┴──────────┘
```

- **Game Area** — displays the room background and room objects.  Clicking an object calls `game.interact()`.
- **Inventory Sidebar** — shows carried items in a grid.  Clicking an item calls `game.interact_inventory()`.  The currently held item is highlighted with a white border.  Clicking empty space clears the hand.
- **Message Bar** — shows the latest event messages, scrolling upward when the bar is full.

## UI states

The UI internally manages three states:

### Normal

Default mode.  Mouse clicks dispatch to room objects or inventory items.

### InsertCode

Active when an `AskedForCodeEvent` is received.  Displays a semi-transparent overlay with a text input box.  The player types a code and presses **Enter** to submit or **Escape** to cancel.

### Inspect

Active when an `InspectedEvent` is received.  Displays a centred, scaled-up view of the object image over a dark overlay.  Any key press or mouse click dismisses it.

## Messages

`PyGameUi` uses a `MessageProvider` to convert events into display strings.  If the provider returns a non-`None` string for an event, it is appended to the message bar.

```python
from escapy.messages import dict_message_provider
from escapy.events import PickedUpEvent

messages = {
    repr(PickedUpEvent("key")): "You found a rusty key!",
}
provider = dict_message_provider(messages)
```

## Game loop

```python
ui.init(game)

while ui.is_running:
    ui.tick()
    events = ui.input()
    ui.handle(events)
    ui.render()

ui.quit()
```

The loop is intentionally simple — all game logic lives in `Game` and `Command` functions, while `PyGameUi` focuses on rendering and input.
