# Techie Kid: Key Quest — Unity Edition (Detailed Specs)

> Twin project: the exact same game is specified for Godot in
> [`../key-quest-godot/SPECS.md`](../key-quest-godot/SPECS.md).
> The **Game Design** and **Level Maps** sections below are intentionally
> identical in both documents — only the technical spec differs.
> Implementation progress is tracked in
> [`../KEY_QUEST_IMPLEMENTATION.md`](../KEY_QUEST_IMPLEMENTATION.md).

## 1. Overview

A tiny Mario-Bros-style 2D platformer for a 4–5 year old, built in **Unity
(2022.3 LTS or newer, 2D template)** with C#. Building the same game as the
Godot edition makes the engines directly comparable: GameObject/Component vs
node tree, prefabs vs scene instancing, C# vs GDScript.

**Engine concepts this project teaches**

- GameObjects, components, and prefabs (Player, Key, Elevator, Door)
- `Rigidbody2D` platformer movement, ground checks, coyote time
- Trigger colliders (`OnTriggerEnter2D`) for pickups and the exit door
- A `DontDestroyOnLoad` singleton `GameManager` shared across scenes
- Kinematic moving platforms that carry the player
- Building levels from data (ASCII maps in `TextAsset`s) instead of
  hand-placing objects in the editor

## 2. Game Design (shared with the Godot edition)

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
| Tile size | 32 px (1 Unity unit) | one grid cell of the ASCII maps |
| Player sprite | 32 × 48 px | roughly 1 × 1.5 tiles |
| Move speed | 180 px/s (5.6 units/s) | slow and controllable |
| Jump height | ≥ 3.5 tiles | clears every platform in the maps |
| Max jumpable gap | 4 tiles | widest gap that appears in the maps |
| Gravity | tuned so a full jump lasts ~0.9 s | floaty, forgiving |
| Coyote time | 0.15 s | can still jump just after leaving a ledge |
| Elevator speed | 48 px/s (1.5 units/s) | slow enough to step on/off calmly |

(Pixels-per-unit is set to 32, so 1 tile = 1 Unity unit.)

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
.............K.....|....
.......K....===....|....
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

## 3. Technical Spec (Unity 2022.3 LTS+, 2D)

### 3.1 Project layout

```
key-quest-unity/
  Packages/
    manifest.json               # minimal: 2D sprite, built-in modules
  ProjectSettings/              # minimal committed settings (version, Force Text, 2D mode)
  Assets/
    Scenes/
      Level1.unity              # near-empty: Bootstrap object + camera (HUD built in code)
      Level2.unity
      Level3.unity
      Celebration.unity
    Scripts/
      GameManager.cs
      LevelBuilder.cs
      PlayerController.cs
      KeyPickup.cs
      ElevatorMover.cs
      LevelExit.cs
      HudController.cs
      CameraFollow.cs
      Celebration.cs
    Resources/                  # loaded by path at runtime (no hand-wired scene refs)
      Levels/
        level1.txt              # the ASCII maps as TextAssets (verbatim from §2.5)
        level2.txt
        level3.txt
      Sprites/  (generated PNGs + .meta: Pixels Per Unit = 32, filter = Point)
      Audio/    (generated WAVs)
  .gitignore                    # Unity standard: Library/, Temp/, Logs/, obj/, UserSettings/
```

Sprites/Levels/Audio live under `Assets/Resources/` so every script loads
its assets with `Resources.Load` — no serialized asset references in scene
YAML, which keeps the hand-committable scenes tiny. Jump keys (Space/↑/W)
are read as `KeyCode`s in code, so the default `InputManager` axes suffice.

**Bootstrap approach (important):** scenes are kept nearly empty — each level
scene contains only a `Main Camera`, an empty `Bootstrap` GameObject with
`LevelBuilder` (and the level's `TextAsset` assigned), and a HUD `Canvas`.
`LevelBuilder` constructs the whole level at runtime from the ASCII map. This
avoids hand-authoring large scene YAML and guarantees the layouts stay
identical to the Godot edition.

### 3.2 Project settings

- Editor: **Force Text** serialization, **Visible Meta Files** (default in
  modern Unity) so everything commits cleanly.
- Build Settings scene list: `Level1`, `Level2`, `Level3`, `Celebration`.
- Input: classic Input Manager default axes (`Horizontal`, `Jump`) already
  cover ←/→/A/D and Space; `W`/`↑` added as positive buttons for jump.
- Quality: 2D defaults; no extra packages beyond the 2D sprite package.

### 3.3 Component & script specs

**`GameManager.cs`** — singleton, `DontDestroyOnLoad`

- State: `LevelIndex`, `KeysTotal`, `KeysCollected`, `RespawnPosition`.
- API: `RegisterKeys(int total)`, `CollectKey()`, `SetRespawn(Vector2 pos)`,
  `NextLevel()` (`SceneManager.LoadScene` next in Build Settings, or
  `Celebration` after Level 3), `Restart()`.
- Events: `public event Action<int,int> KeyCollected;`
  `public event Action AllKeysCollected;`
- Created lazily by `LevelBuilder` if not present, so any scene can be played
  directly in the editor.

**`LevelBuilder.cs`** — on the `Bootstrap` object in each level scene

- Serialized fields: the level `TextAsset`, sprite references, prefab-less
  builders (it assembles Key/Elevator/Door/Player objects in code, or from
  small prefabs — implementer's choice; assembling in code keeps the repo
  free of hand-edited prefab YAML).
- Parses the ASCII map (same legend as §2.5): `#`/`=` → static tile objects
  with `BoxCollider2D` (contiguous runs merged into one collider per row for
  efficiency); `K` → key object; `E`/`|` → elevator with computed
  bottom/top; `D` → door; `P` → player + `GameManager.SetRespawn`.
- Adds invisible edge walls and a wide "fall zone" trigger below the map
  that respawns the player.
- Computes level bounds and passes them to `CameraFollow`.
- Calls `GameManager.RegisterKeys(count)` and tells `HudController` to build
  its icons.

**`PlayerController.cs`** — on the runtime-built Player object

- Components: `SpriteRenderer`, `Rigidbody2D` (Dynamic, freeze Z rotation,
  interpolate), `BoxCollider2D`, `AudioSource`.
- `Update`: read `Input.GetAxisRaw("Horizontal")` and jump buttons; sprite
  flip; simple sprite-swap animation (idle / 2-frame run / jump) driven by
  state and a frame timer (no Animator asset needed — keeps everything in
  code).
- `FixedUpdate`: set horizontal velocity (5.6 u/s); ground check with
  `Physics2D.OverlapBox` under the feet; jump impulse sized for ≥ 3.5 tiles;
  coyote timer 0.15 s.
- Standing on an elevator parents the player to it (see `ElevatorMover`);
  standing on normal ground updates `GameManager.RespawnPosition`.
- `Respawn()`: brief sprite fade, teleport to `RespawnPosition`, soft boop.

**`KeyPickup.cs`** — key objects

- `CircleCollider2D` (isTrigger), spinning 4-frame sprite swap, small bob.
- `OnTriggerEnter2D` with the player → arpeggio sound + sparkle particle
  burst (`ParticleSystem` created in code), `GameManager.CollectKey()`,
  destroy after the sound finishes.

**`ElevatorMover.cs`** — elevator objects

- Components: `SpriteRenderer` (cab), `BoxCollider2D`, `Rigidbody2D`
  (Kinematic).
- Fields: `bottomPos`, `topPos` (set by `LevelBuilder`), speed 1.5 u/s,
  1 s pause at each end; moves with `Rigidbody2D.MovePosition` in
  `FixedUpdate` (sine-eased ping-pong).
- Parents the player transform while the player stands on top
  (`OnCollisionEnter2D`/`Exit2D` with a top-contact check) so the kid rides
  smoothly.

**`LevelExit.cs`** — the door

- `BoxCollider2D` (isTrigger, initially disabled), closed/open sprites,
  `AudioSource`, gentle sparkle `ParticleSystem` when open.
- Subscribes to `GameManager.AllKeysCollected` → open sprite, chime,
  sparkles, enable trigger.
- `OnTriggerEnter2D` with the player → fanfare, screen fade,
  `GameManager.NextLevel()`.

**`HudController.cs`** — on the HUD `Canvas` (Screen Space – Overlay)

- Builds one `Image` per key (grey tint), top-left, 48 px each.
- Subscribes to `GameManager.KeyCollected` → tint icon gold + scale-pop
  coroutine.

**`CameraFollow.cs`** — on `Main Camera` (orthographic, size ≈ 5)

- Smooth-follows the player, clamped to the level bounds from
  `LevelBuilder`; solid background color `#0e1726` behind the props.

**`Celebration.cs`** — in `Celebration.unity`

- Big kid sprite, confetti `ParticleSystem`, fanfare, icon-only replay
  arrow (UI `Button`); any key or the button → `GameManager.Restart()`.

### 3.4 Build & run

1. Install Unity Hub + Unity **2022.3 LTS or newer** with the 2D template
   modules (https://unity.com/download).
2. Unity Hub → **Add project from disk** → select
   `game-development/key-quest-unity/`.
3. **Double-click `Assets/Scenes/Level1.unity` to open it** — the Hierarchy
   header must read "Level1", not "Untitled". Pressing Play while Unity's
   default empty scene is open shows only a blank blue screen.
4. Press **Play**. Unity regenerates `Library/` on first open (a few
   minutes); no other setup — assets are committed and levels are built from
   the maps at runtime.

If a level scene is ever opened but stays blank, `AutoBoot.cs`
(`[RuntimeInitializeOnLoadMethod]`) rebuilds it from the scene name as a
fallback, so an empty-but-correctly-named scene still plays.

## 4. Implementation checklist

See [`../KEY_QUEST_IMPLEMENTATION.md`](../KEY_QUEST_IMPLEMENTATION.md) —
Phase 0 (shared assets) and Phase 2 (Unity) apply to this project, including
the Definition of Done that must be satisfied before this game is considered
complete.
