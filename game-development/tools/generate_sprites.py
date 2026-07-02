#!/usr/bin/env python3
"""Generate all pixel-art sprites for Techie Kid: Key Quest.

Produces every PNG listed in the specs (key-quest-godot/SPECS.md §2.7 and
key-quest-unity/SPECS.md §2.7) and writes them into both game projects:

    key-quest-godot/assets/sprites/
    key-quest-unity/Assets/Sprites/

Usage:
    python3 generate_sprites.py                 # write into both projects
    python3 generate_sprites.py --out DIR       # write into DIR instead
    python3 generate_sprites.py --contact-sheet sheet.png   # also render a
                                                # 4x-zoom contact sheet
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
DEFAULT_TARGETS = [
    HERE.parent / "key-quest-godot" / "assets" / "sprites",
    HERE.parent / "key-quest-unity" / "Assets" / "Sprites",
]

# Palette from the specs (§2.7) plus supporting shades.
PALETTE = {
    ".": None,                      # transparent
    "H": (0x6B, 0x4A, 0x2B, 255),   # hair brown
    "S": (0xFF, 0xD9, 0xB3, 255),   # kid skin
    "E": (0x2B, 0x21, 0x1A, 255),   # eyes
    "M": (0xC2, 0x54, 0x50, 255),   # smiling mouth
    "R": (0xFF, 0x5C, 0x5C, 255),   # shirt red
    "B": (0xFF, 0x9F, 0x43, 255),   # backpack straps orange
    "J": (0x4A, 0x6C, 0xFF, 255),   # jeans blue
    "K": (0x2B, 0x2F, 0x45, 255),   # shoes dark
    "G": (0xFF, 0xD4, 0x47, 255),   # key gold
    "g": (0xC9, 0xA2, 0x27, 255),   # key gold shadow
    "W": (0xFF, 0xF6, 0xDE, 255),   # shine
}

BOARD_DARK = (0x14, 0x33, 0x1B, 255)
CIRCUIT_GREEN = (0x2E, 0xCC, 0x40, 255)
CIRCUIT_GREEN_LIGHT = (0x58, 0xE0, 0x6C, 255)
CIRCUIT_GREEN_DIM = (0x1F, 0x7A, 0x2E, 255)
CIRCUIT_GREEN_EDGE = (0x1F, 0x9E, 0x30, 255)
CHIP_NAVY = (0x1B, 0x2A, 0x4A, 255)
CHIP_NAVY_LIGHT = (0x33, 0x48, 0x7A, 255)
CHIP_NAVY_MID = (0x24, 0x36, 0x5E, 255)
CHIP_BORDER = (0x0F, 0x18, 0x30, 255)
GOLD = (0xFF, 0xD4, 0x47, 255)
GOLD_DARK = (0xC9, 0xA2, 0x27, 255)
DOOR_GREEN = (0x3D, 0xFF, 0x8B, 255)
DOOR_GREY = (0x88, 0x92, 0xA6, 255)
DOOR_GREY_DARK = (0x6C, 0x77, 0x8F, 255)
STEEL_DARK = (0x39, 0x41, 0x5A, 255)
BG_NAVY = (0x0E, 0x17, 0x26, 255)
LED_CYAN = (0x59, 0xF7, 0xFF, 255)
STEEL_LIGHT = (0xCF, 0xD8, 0xEA, 255)
STEEL_SHINE = (0xEE, 0xF2, 0xFA, 255)

# --------------------------------------------------------------------------
# Kid character: 16x24 pixel grids, rendered at scale 2 -> 32x48.
# --------------------------------------------------------------------------

KID_HEAD = [
    "....HHHHHHHH....",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHSSSSSSSSHH..",
    ".HSSSSSSSSSSSSH.",
    ".HSSSSSSSSSSSSH.",
    ".HSSEESSSSEESSH.",
    ".HSSEESSSSEESSH.",
    "..SSSSSSSSSSSS..",
    "..SSSMMMMMMSSS..",
    "...SSSSSSSSSS...",
    "....SSSSSSSS....",
]

KID_TORSO_IDLE = [
    "...RRBBRRBBRR...",
    "..RRRBBRRBBRRR..",
    "..SRRRRRRRRRRS..",
    "..SRRRRRRRRRRS..",
    "...RRRRRRRRRR...",
    "...JJJJJJJJJJ...",
]

KID_TORSO_JUMP = [
    "...RRBBRRBBRR...",
    "S.RRRBBRRBBRRR.S",
    "SS.RRRRRRRRRR.SS",
    "...RRRRRRRRRR...",
    "...RRRRRRRRRR...",
    "...JJJJJJJJJJ...",
]

KID_LEGS_IDLE = [
    "....JJJJJJJJ....",
    "....JJJ..JJJ....",
    "....JJJ..JJJ....",
    "....JJJ..JJJ....",
    "...KKKK..KKKK...",
    "...KKKK..KKKK...",
]

KID_LEGS_RUN1 = [
    "....JJJJJJJJ....",
    "...JJJ....JJJ...",
    "..JJJ......JJJ..",
    "..JJJ......JJJ..",
    ".KKKK......KKKK.",
    ".KKKK......KKKK.",
]

KID_LEGS_RUN2 = [
    "....JJJJJJJJ....",
    ".....JJJJJJ.....",
    ".....JJJJJJ.....",
    ".....JJJJJJ.....",
    "....KKKKKKKK....",
    "....KKKKKKKK....",
]

KID_LEGS_JUMP = [
    "....JJJJJJJJ....",
    "...JJJJ..JJJJ...",
    "...JJJ....JJJ...",
    "..KKKK....KKKK..",
    "..KKKK....KKKK..",
    "................",
]

# Golden key: 16x16 grid, rendered at scale 2 -> 32x32 (and scale 3 for HUD).
KEY_GRID = [
    "................",
    "................",
    "................",
    "................",
    "..GWWG..........",
    ".GGGGGG.........",
    ".GG..GG.........",
    ".GG..GGGGGGGGGG.",
    ".GG..GGGGGGGGGg.",
    ".GGGGGg...G..G..",
    "..GggG....g..g..",
    "................",
    "................",
    "................",
    "................",
    "................",
]


def grid_image(rows: list[str], scale: int) -> Image.Image:
    width = len(rows[0])
    for row in rows:
        assert len(row) == width, f"ragged grid row: {row!r}"
    img = Image.new("RGBA", (width * scale, len(rows) * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            color = PALETTE[ch]
            if color is not None:
                draw.rectangle(
                    [x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1],
                    fill=color,
                )
    return img


def kid(legs: list[str], torso: list[str] = KID_TORSO_IDLE) -> Image.Image:
    return grid_image(KID_HEAD + torso + legs, scale=2)


def key_frames() -> dict[str, Image.Image]:
    """Coin-style spin: full, squashed, thin bar, mirrored squash."""
    base = grid_image(KEY_GRID, scale=2)  # 32x32
    frames = {"key_1": base}

    def squashed(factor: float) -> Image.Image:
        w = max(2, round(32 * factor))
        small = base.resize((w, 32), Image.NEAREST)
        out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        out.paste(small, ((32 - w) // 2, 0))
        return out

    frames["key_2"] = squashed(0.6)
    thin = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(thin)
    d.rectangle([14, 8, 17, 21], fill=GOLD)
    d.rectangle([14, 8, 15, 21], fill=PALETTE["W"])
    frames["key_3"] = thin
    frames["key_4"] = squashed(0.6).transpose(Image.FLIP_LEFT_RIGHT)
    return frames


def tile_circuit() -> Image.Image:
    img = Image.new("RGBA", (32, 32), BOARD_DARK)
    d = ImageDraw.Draw(img)
    # Bright walkable surface on top.
    d.rectangle([0, 0, 31, 5], fill=CIRCUIT_GREEN)
    d.rectangle([0, 0, 31, 0], fill=CIRCUIT_GREEN_LIGHT)
    d.rectangle([0, 5, 31, 5], fill=CIRCUIT_GREEN_EDGE)
    # Fixed traces that never touch the tile edges (seamless tiling).
    rng = random.Random(42)
    for _ in range(4):
        x = rng.randrange(3, 27)
        y1 = rng.randrange(9, 16)
        y2 = y1 + rng.randrange(6, 12)
        y2 = min(y2, 28)
        d.line([x, y1, x, y2], fill=CIRCUIT_GREEN_DIM)
        xe = min(max(x + rng.choice([-7, -5, 5, 7]), 3), 28)
        d.line([x, y2, xe, y2], fill=CIRCUIT_GREEN_DIM)
        d.rectangle([xe - 1, y2 - 1, xe + 1, y2 + 1], fill=CIRCUIT_GREEN)
        d.rectangle([x - 1, y1 - 1, x + 1, y1 + 1], fill=CIRCUIT_GREEN)
    for _ in range(3):
        x, y = rng.randrange(4, 27), rng.randrange(20, 29)
        d.point((x, y), fill=GOLD)
    return img


def tile_chip() -> Image.Image:
    img = Image.new("RGBA", (32, 32), CHIP_NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], outline=CHIP_BORDER)
    d.rectangle([1, 1, 30, 3], fill=CHIP_NAVY_LIGHT)   # top highlight
    d.rectangle([4, 6, 27, 25], fill=CHIP_NAVY_MID)    # die area
    # Gold pins on left/right edges.
    for y in (6, 14, 22):
        d.rectangle([0, y, 1, y + 3], fill=GOLD)
        d.rectangle([30, y, 31, y + 3], fill=GOLD)
        d.rectangle([0, y + 3, 1, y + 3], fill=GOLD_DARK)
        d.rectangle([30, y + 3, 31, y + 3], fill=GOLD_DARK)
    # IC notch marking + a tiny silicon dot.
    d.ellipse([6, 8, 9, 11], fill=CHIP_NAVY_LIGHT)
    d.rectangle([14, 14, 17, 17], fill=CHIP_NAVY_LIGHT)
    return img


def elevator() -> Image.Image:
    img = Image.new("RGBA", (96, 16), CHIP_NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 95, 2], fill=STEEL_LIGHT)       # walking surface
    d.rectangle([0, 0, 95, 0], fill=STEEL_SHINE)
    d.rectangle([0, 14, 95, 15], fill=CHIP_BORDER)
    for x in range(10, 90, 8):                          # cyan LED strip
        d.rectangle([x, 8, x + 1, 9], fill=LED_CYAN)
    d.rectangle([0, 0, 3, 15], fill=GOLD)               # gold end caps
    d.rectangle([92, 0, 95, 15], fill=GOLD)
    d.rectangle([0, 13, 3, 15], fill=GOLD_DARK)
    d.rectangle([92, 13, 95, 15], fill=GOLD_DARK)
    return img


def door(open_: bool) -> Image.Image:
    img = Image.new("RGBA", (32, 64), STEEL_DARK)
    d = ImageDraw.Draw(img)
    if not open_:
        d.rectangle([3, 3, 28, 60], fill=DOOR_GREY)
        d.rectangle([3, 3, 28, 5], fill=STEEL_LIGHT)
        for y in (20, 38, 52):                          # panel seams
            d.line([4, y, 27, y], fill=DOOR_GREY_DARK)
        d.rectangle([12, 8, 19, 15], fill=CHIP_BORDER)  # dark window
        d.ellipse([13, 40, 18, 45], fill=GOLD)          # keyhole
        d.rectangle([15, 45, 16, 49], fill=GOLD_DARK)
        d.rectangle([13, 30, 14, 33], fill=(0xAA, 0xB4, 0xC6, 255))
    else:
        d.rectangle([3, 3, 28, 60], fill=BG_NAVY)       # open: inside is dark
        d.rectangle([3, 3, 28, 60], outline=DOOR_GREEN, width=2)
        d.rectangle([12, 8, 19, 15], fill=DOOR_GREEN)   # window glows
        d.polygon([(5, 60), (26, 60), (22, 50), (9, 50)],
                  fill=(0x1C, 0x3A, 0x2C, 255))         # light on the floor
        rng = random.Random(7)
        for _ in range(10):                             # sparkles inside
            x, y = rng.randrange(7, 25), rng.randrange(18, 48)
            d.point((x, y), fill=DOOR_GREEN)
        d.rectangle([12, 0, 19, 2], fill=DOOR_GREEN)    # LED strip on top
    return img


def bg_server() -> Image.Image:
    img = Image.new("RGBA", (64, 96), (0x13, 0x1C, 0x30, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 63, 95], outline=(0x0A, 0x11, 0x20, 255), width=2)
    d.rectangle([2, 2, 61, 5], fill=CHIP_NAVY_MID)
    rng = random.Random(1234)
    for y in range(10, 90, 12):                         # rack slots + LEDs
        d.rectangle([5, y, 58, y + 6], fill=(0x0A, 0x11, 0x20, 255))
        for i, x in enumerate(range(9, 40, 6)):
            color = rng.choice([CIRCUIT_GREEN, LED_CYAN, GOLD])
            d.rectangle([x, y + 2, x + 1, y + 3], fill=color)
        d.rectangle([46, y + 2, 55, y + 4], fill=(0x1A, 0x24, 0x3C, 255))
    return img


def bg_led() -> Image.Image:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for radius, alpha in ((7, 40), (5, 90), (3, 170)):
        d.ellipse([8 - radius, 8 - radius, 7 + radius, 7 + radius],
                  fill=(0x59, 0xF7, 0xFF, alpha))
    d.ellipse([6, 6, 9, 9], fill=LED_CYAN)
    d.rectangle([7, 6, 8, 7], fill=(0xE9, 0xFE, 0xFF, 255))
    return img


EXPECTED_SIZES = {
    "kid_idle": (32, 48), "kid_run_1": (32, 48), "kid_run_2": (32, 48),
    "kid_jump": (32, 48),
    "key_1": (32, 32), "key_2": (32, 32), "key_3": (32, 32), "key_4": (32, 32),
    "tile_circuit": (32, 32), "tile_chip": (32, 32),
    "elevator": (96, 16),
    "door_closed": (32, 64), "door_open": (32, 64),
    "hud_key": (48, 48),
    "bg_server": (64, 96), "bg_led": (16, 16),
}


def build_all() -> dict[str, Image.Image]:
    sprites = {
        "kid_idle": kid(KID_LEGS_IDLE),
        "kid_run_1": kid(KID_LEGS_RUN1),
        "kid_run_2": kid(KID_LEGS_RUN2),
        "kid_jump": kid(KID_LEGS_JUMP, torso=KID_TORSO_JUMP),
        **key_frames(),
        "tile_circuit": tile_circuit(),
        "tile_chip": tile_chip(),
        "elevator": elevator(),
        "door_closed": door(open_=False),
        "door_open": door(open_=True),
        "hud_key": grid_image(KEY_GRID, scale=3),
        "bg_server": bg_server(),
        "bg_led": bg_led(),
    }
    for name, img in sprites.items():
        assert img.size == EXPECTED_SIZES[name], (name, img.size)
    return sprites


def contact_sheet(sprites: dict[str, Image.Image], zoom: int = 4) -> Image.Image:
    pad = 12
    cell_w = max(img.width for img in sprites.values()) * zoom + pad
    cell_h = max(img.height for img in sprites.values()) * zoom + pad
    cols = 6
    rows = (len(sprites) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w + pad, rows * cell_h + pad),
                      (0x22, 0x28, 0x33, 255))
    for i, (name, img) in enumerate(sorted(sprites.items())):
        big = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
        x = pad + (i % cols) * cell_w
        y = pad + (i // cols) * cell_h
        sheet.paste(big, (x, y), big)
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None,
                        help="write PNGs to this directory instead of both projects")
    parser.add_argument("--contact-sheet", type=Path, default=None,
                        help="also write a zoomed contact sheet PNG here")
    args = parser.parse_args()

    sprites = build_all()
    targets = [args.out] if args.out else DEFAULT_TARGETS
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for name, img in sprites.items():
            img.save(target / f"{name}.png")
        print(f"wrote {len(sprites)} sprites -> {target}")

    if args.contact_sheet:
        args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
        contact_sheet(sprites).save(args.contact_sheet)
        print(f"wrote contact sheet -> {args.contact_sheet}")


if __name__ == "__main__":
    main()
