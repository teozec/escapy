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

"""Generate placeholder images for the example game.

Reads `config.json` and writes one image for every file referenced in
`ui.rooms` and `ui.objects` into `ui.assets_dir`: a coloured background
labelled with the file name for rooms, a coloured tile for objects.

Run it once before `main.py`, from any directory:

    python example/make_assets.py

Existing files are left untouched, so you can replace any placeholder with
a real image and re-run the script safely.  Use `--force` to overwrite them.
"""

import argparse
import hashlib
import json
from pathlib import Path

import pygame

EXAMPLE_DIR = Path(__file__).parent

ROOM_SIZE = (800, 600)
OBJECT_SIZE = (200, 200)


def color_for(name: str, lightness: int) -> pygame.Color:
    """Return a stable colour derived from *name* (same name, same colour)."""
    hue = int(hashlib.md5(name.encode()).hexdigest(), 16) % 360
    color = pygame.Color(0)
    color.hsla = (hue, 60, lightness, 100)
    return color


def make_image(
    label: str, size: tuple[int, int], background: pygame.Color, font: pygame.font.Font, centered: bool
) -> pygame.Surface:
    """Draw a bordered rectangle with *label* centred on it, or in the top-left corner."""
    surface = pygame.Surface(size)
    surface.fill(background)
    pygame.draw.rect(surface, pygame.Color("black"), surface.get_rect(), 4)
    text = font.render(label, True, pygame.Color("black"))
    if centered:
        surface.blit(text, text.get_rect(center=surface.get_rect().center))
    else:
        surface.blit(text, (20, 20))
    return surface


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="overwrite existing images")
    args = parser.parse_args()

    with open(EXAMPLE_DIR / "config.json") as f:
        ui_config = json.load(f)["ui"]

    assets_dir = EXAMPLE_DIR / ui_config["assets_dir"]
    assets_dir.mkdir(exist_ok=True)

    pygame.font.init()
    room_font = pygame.font.Font(None, 64)
    object_font = pygame.font.Font(None, 32)

    # Several ids can share the same file (e.g. "calendar.png"): generate each file once.
    # Room labels go in the corner, where objects are less likely to cover them.
    images = {image: (ROOM_SIZE, 85, room_font, False) for image in ui_config["rooms"].values()}
    images |= {image: (OBJECT_SIZE, 60, object_font, True) for image in ui_config["objects"].values()}

    for image, (size, lightness, font, centered) in images.items():
        path = assets_dir / image
        if path.exists() and not args.force:
            print(f"skip    {path.relative_to(EXAMPLE_DIR)}")
            continue
        label = Path(image).stem
        pygame.image.save(make_image(label, size, color_for(label, lightness), font, centered), path)
        print(f"created {path.relative_to(EXAMPLE_DIR)}")


if __name__ == "__main__":
    main()
