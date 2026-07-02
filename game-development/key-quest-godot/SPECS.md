# Techie Kid: Key Quest — Godot Edition (Detailed Specs)

> Twin project: the exact same game is specified for Unity in
> [`../key-quest-unity/SPECS.md`](../key-quest-unity/SPECS.md).
> The **Game Design** and **Level Maps** sections below are intentionally
> identical in both documents — only the technical spec differs.
> Implementation progress is tracked in
> [`../KEY_QUEST_IMPLEMENTATION.md`](../KEY_QUEST_IMPLEMENTATION.md).

## 1. Overview

A tiny Mario-Bros-style 2D platformer for a 4–5 year old, built in **Godot 4.x**
with GDScript. Beyond being a gift for a small player, it exercises the core
Godot workflow from `godot-intro/`: scene composition, `CharacterBody2D`
physics, `Area2D` signals, autoload singletons, tweens, and a `CanvasLayer` HUD.

**Engine concepts this project teaches**

- Scene instancing (Player, Key, Elevator, Door as reusable `.tscn` scenes)
- `CharacterBody2D` + `move_and_slide()` platformer movement with coyote time
- Signals (`body_entered`) and a custom signal (`all_keys_collected`)
- Autoload (singleton) game state shared across levels
- `AnimatableBody2D` + `Tween` for moving platforms that carry the player
- Building levels from data (ASCII maps) instead of hand-placing nodes

## 2. Game Design (shared with the Unity edition)

### 2.1 Concept

- **Title:** Techie Kid: Key Quest
- **Genre:** 2D side-scrolling platformer (Mario-Bros-like)
- **Player:** a curious little kid who shrinks into a giant, friendly computer
- **World theme:** tech style — circuit-board floors, chip platforms, glowing
  LEDs, server-tower backgrounds, and **elevators** (slow "data lifts") that
  carry the kid between floors
- **Goal:** collect all the golden **keys** in the level. When every key is
  collected, the exit **door** (a terminal-styled elevator door) turns from
  grey to glowing green and opens. Walking into it loads the next level.
- **Length:** 3 levels, then a confetti **"You did it!"** celebration screen
  that loops back to Level 1.

### 2.2 Kid-friendly rules (target age 4–5)

These are hard requirements, not suggestions:

1. **Impossible to lose.** No hazards, no enemies, no lives, no timer, no
   game-over screen, no score.
2. **Gentle respawn.** Falling off a platform fades the screen briefly and
   places the kid back on the last platform touched. No penalty, no sound of
   failure — a soft "boop" at most.
3. **Zero reading required.** The HUD shows big key icons that light up as
   they are collected. The door communicates by color (grey → green) and
   sparkles. No text is needed to play.
4. **Forgiving physics.** Wide platforms, small gaps (max 4 tiles), generous
   jump (≥ 3.5 tiles high), coyote time (~0.15 s), and invisible walls at
   level edges so the kid can never walk out of the world.
5. **One-button simplicity.** Move + jump is the whole verb set. Elevators
   move by themselves; the door opens by itself; keys collect on touch.
6. **Bright and big.** High-contrast colors, large sprites, cheerful chiptune
   sounds (jump blip, rising arpeggio on key pickup, fanfare on door open).

### 2.3 Controls

| Action | Keys |
|---|---|
| Move left | `←` or `A` |
| Move right | `→` or `D` |
| Jump | `Space` or `↑` or `W` |

No other input exists. Holding jump does not fly; there is no double jump.

### 2.4 Physics tuning values (same numbers in both engines)

| Parameter | Value | Note |
|---|---|---|
| Tile size | 32 px | one grid cell of the ASCII maps |
| Player sprite | 32 × 48 px | roughly 1 × 1.5 tiles |
| Move speed | 180 px/s | slow and controllable |
| Jump height | ≥ 3.5 tiles (112 px) | clears every platform in the maps |
| Max jumpable gap | 4 tiles | widest gap that appears in the maps |
| Gravity | tuned so a full jump lasts ~0.9 s | floaty, forgiving |
| Coyote time | 0.15 s | can still jump just after leaving a ledge |
| Elevator speed | 48 px/s | slow enough to step on/off calmly |

### 2.5 Level maps (identical in both editions)

Levels are defined as ASCII grids; one character = one 32 px tile.
Both engines build their levels from these exact maps.

**Legend**

| Char | Meaning |
|---|---|
| `.` | empty air |
| `#` | solid circuit-board ground/wall tile |
| `=` | floating chip platform tile (solid) |
| `P` | player start position |
| `K` | golden key |
| `D` | exit door (2 tiles tall, drawn upward from this cell) |
| `E` | elevator platform, at its lowest (start) position |
| `\|` | elevator travel path — the elevator loops slowly between `E` and the topmost `\|` in its column; at the top, its surface aligns with the adjacent platform |

**Level 1 — "The Motherboard"** (3 keys, no elevator, 20 × 6)

```
....................
......K........K....
.....===......===...
....................
.P...K...........D..
####################
```

**Level 2 — "The Data Lift"** (4 keys, 1 elevator, 24 × 10)

```
.....................D..
...................|####
...................|....
...................|....
..............K....|....
.......K.....===...|....
......===..........|....
...................E....
.P......K...K...........
########################
```

**Level 3 — "The Server Tower"** (5 keys, 2 elevators, 28 × 12)

```
........................KD..
.......................|####
.......................|....
.......................|....
............K......K...|....
........|..====..====..E....
........|...................
........|...................
........|...................
........E...................
.P...K..........K...........
############################
```

### 2.6 HUD & feedback

- Top-left: one big key icon per key in the level (e.g. 3 in Level 1). Icons
  start greyed-out and light up gold, with a small pop animation, as keys are
  collected.
- Key pickup: rising two-note arpeggio + sparkle particles at the key.
- All keys collected: short chime, the door swaps to its open/green sprite
  and emits gentle sparkles.
- Door entered: fanfare + fade to next level.
- Celebration screen after Level 3: confetti particles, a big smiling kid
  sprite, a single icon-only "replay" arrow that restarts at Level 1 (any key
  press also restarts).

### 2.7 Assets (generated, shared list)

All art is simple, bright **generated pixel art** (PNG), produced by a Python
(Pillow) script committed alongside the projects. All audio is short generated
chiptune-style WAV produced by a Python script (sine/square waves). No
external or downloaded assets.

| Asset | File | Size | Notes |
|---|---|---|---|
| Kid idle | `kid_idle.png` | 32×48 | big head, backpack, bright shirt |
| Kid run | `kid_run_1.png`, `kid_run_2.png` | 32×48 | 2-frame run cycle |
| Kid jump | `kid_jump.png` | 32×48 | arms up |
| Key | `key_1.png` … `key_4.png` | 32×32 | golden, 4-frame spin |
| Ground tile | `tile_circuit.png` | 32×32 | green circuit-board traces |
| Platform tile | `tile_chip.png` | 32×32 | dark chip with gold pins |
| Elevator cab | `elevator.png` | 96×16 | 3-tiles-wide platform with lights |
| Door closed | `door_closed.png` | 32×64 | grey terminal door |
| Door open | `door_open.png` | 32×64 | green glowing, open |
| HUD key icon | `hud_key.png` | 48×48 | grey + gold variants (or tinted) |
| Background props | `bg_server.png`, `bg_led.png` | 64×96, 16×16 | decorative only |
| Jump sound | `jump.wav` | ~0.15 s | short blip |
| Key sound | `key.wav` | ~0.3 s | rising arpeggio |
| Door-open sound | `door.wav` | ~0.6 s | chime |
| Fanfare | `win.wav` | ~1.5 s | celebration melody |
| Respawn sound | `boop.wav` | ~0.2 s | soft, friendly |

Palette (bright, high-contrast): circuit green `#2ecc40`, board dark
`#14331b`, chip navy `#1b2a4a`, key gold `#ffd447`, door green `#3dff8b`,
kid skin `#ffd9b3`, shirt red `#ff5c5c`, jeans blue `#4a6cff`, sky/interior
background `#0e1726` with soft LED dots.

## 3. Technical Spec (Godot 4.x)

### 3.1 Project layout

```
key-quest-godot/
  project.godot                 # Godot 4.x project, input map, autoload, window settings
  icon.svg
  scenes/
    Main.tscn                   # entry scene: loads current level via GameState
    Level.tscn                  # generic level scene: LevelBuilder + camera + HUD
    Player.tscn                 # CharacterBody2D
    Key.tscn                    # Area2D
    Elevator.tscn               # AnimatableBody2D
    Door.tscn                   # Area2D + AnimatedSprite2D
    HUD.tscn                    # CanvasLayer
    Celebration.tscn            # end screen
  scripts/
    game_state.gd               # autoload singleton
    level_builder.gd
    player.gd
    key.gd
    elevator.gd
    door.gd
    hud.gd
    celebration.gd
    levels.gd                   # the 3 ASCII maps as constants
  assets/
    sprites/  (generated PNGs)
    audio/    (generated WAVs)
```

### 3.2 Project settings (`project.godot`)

- Godot feature tag `4.x`; main scene `scenes/Main.tscn`.
- Window: 1152 × 648 (Godot default), stretch mode `canvas_items` so it
  scales cleanly full-screen.
- Rendering: 2D, `texture_filter = nearest` (crisp pixel art).
- **Input map:** `move_left` (←, A), `move_right` (→, D), `jump` (Space, ↑, W).
- **Autoload:** `GameState` → `scripts/game_state.gd`.

### 3.3 Node & script specs

**`GameState` (autoload, `game_state.gd`)**

- State: `level_index: int`, `keys_total: int`, `keys_collected: int`,
  `respawn_position: Vector2`.
- API: `collect_key()`, `register_keys(total)`, `set_respawn(pos)`,
  `next_level()` (loads `Level.tscn` again with `level_index + 1`, or
  `Celebration.tscn` after level 3), `restart()`.
- Signals: `key_collected(collected, total)`, `all_keys_collected`.

**`LevelBuilder` (`level_builder.gd`, on `Level.tscn` root)**

- Reads the ASCII map for `GameState.level_index` from `levels.gd`.
- For each cell: `#`/`=` → set tile in a `TileMapLayer` (two tile types:
  circuit ground, chip platform); `K` → instance `Key.tscn`; `E`/`|` →
  instance `Elevator.tscn` with computed bottom/top positions; `D` →
  instance `Door.tscn`; `P` → instance `Player.tscn` and set
  `GameState.respawn_position`.
- Adds invisible wall `StaticBody2D`s at both level edges and a fall-detector
  `Area2D` spanning below the map (respawn trigger).
- Sets `Camera2D` limits to the map bounds.

**`Player.tscn` / `player.gd`** — `CharacterBody2D`

- Children: `AnimatedSprite2D` (idle / run / jump), `CollisionShape2D`
  (capsule), `AudioStreamPlayer` ×2 (jump, boop).
- `@export var speed := 180.0`, `@export var jump_velocity := -420.0`
  (tuned to reach ≥ 3.5 tiles with project gravity), coyote timer 0.15 s.
- `_physics_process`: gravity, `Input.get_axis("move_left", "move_right")`,
  jump if `is_on_floor()` or coyote timer alive, `move_and_slide()`;
  flips sprite by direction; picks animation by state.
- `respawn()`: fade sprite, teleport to `GameState.respawn_position`, play boop.
- While standing on ground/platform tiles, updates
  `GameState.respawn_position` to its own position (only when `is_on_floor()`
  and not on an elevator).

**`Key.tscn` / `key.gd`** — `Area2D`

- Children: `AnimatedSprite2D` (4-frame spin), `CollisionShape2D`,
  `AudioStreamPlayer`, `CPUParticles2D` (sparkle burst).
- `body_entered` → if body is the player: play sound + particles, hide
  collision, `GameState.collect_key()`, `queue_free()` after the sound.

**`Elevator.tscn` / `elevator.gd`** — `AnimatableBody2D`

- Children: `Sprite2D` (elevator cab, 3 tiles wide), `CollisionShape2D`.
- `sync_to_physics = true` so it carries the player natively.
- Exported `top_position` / `bottom_position`; on `_ready()` starts a looping
  `Tween` (bottom → top → bottom, `Tween.TRANS_SINE`) at 48 px/s with a 1 s
  pause at each end.

**`Door.tscn` / `door.gd`** — `Area2D`

- Children: `AnimatedSprite2D` (closed / open), `CollisionShape2D`,
  `AudioStreamPlayer`, `CPUParticles2D` (gentle sparkles when open).
- Starts closed and inert. On `GameState.all_keys_collected`: swap to open
  sprite, play chime, start sparkles, enable its trigger.
- `body_entered` (only when open) → play fanfare, fade out,
  `GameState.next_level()`.

**`HUD.tscn` / `hud.gd`** — `CanvasLayer`

- `HBoxContainer` of `TextureRect` key icons, created from
  `GameState.keys_total` on level start; greyed (modulate) until collected.
- Listens to `GameState.key_collected` → light up icon with a small
  scale-pop `Tween`.

**`Celebration.tscn` / `celebration.gd`**

- Big kid sprite, `CPUParticles2D` confetti, fanfare sound, icon-only replay
  arrow (`TextureButton`). Any input or the button → `GameState.restart()`.

### 3.4 Build & run

1. Install Godot 4.x (https://godotengine.org/download).
2. Open the Godot Project Manager → **Import** → select
   `game-development/key-quest-godot/project.godot`.
3. Press **F5** (Play). No other setup: assets are committed, levels are
   generated from the maps at runtime.

## 4. Implementation checklist

See [`../KEY_QUEST_IMPLEMENTATION.md`](../KEY_QUEST_IMPLEMENTATION.md) —
Phase 0 (shared assets) and Phase 1 (Godot) apply to this project, including
the Definition of Done that must be satisfied before this game is considered
complete.
