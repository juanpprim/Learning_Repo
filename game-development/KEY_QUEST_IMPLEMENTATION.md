# Techie Kid: Key Quest — Implementation Steps Checklist

Tracks the implementation of the two twin games specified in
[`key-quest-godot/SPECS.md`](key-quest-godot/SPECS.md) and
[`key-quest-unity/SPECS.md`](key-quest-unity/SPECS.md).
Work through the phases in order and tick each box as it lands; a phase is
only done when every box in it is checked. The **Definition of Done** at the
bottom is the acceptance bar for calling either game finished.

## Phase 0 — Shared generated assets

- [x] Write `tools/generate_sprites.py` (Pillow) that produces every PNG in
      the assets table of the specs (§2.7): kid idle/run×2/jump, key spin ×4,
      circuit tile, chip tile, elevator cab, door closed/open, HUD key icon,
      background props — exact sizes and palette from the spec.
- [x] Write `tools/generate_audio.py` that produces the five WAVs (jump, key
      arpeggio, door chime, win fanfare, respawn boop) as short chiptune-style
      waveforms.
- [x] Run both scripts; commit the scripts and copy the generated files into
      `key-quest-godot/assets/` and `key-quest-unity/Assets/Sprites|Audio/`.
- [x] Eyeball every sprite at 4× zoom: bright, high-contrast, readable
      silhouettes; kid looks friendly; key reads as a key.
      (Reviewed via `generate_sprites.py --contact-sheet`.)

## Phase 1 — Godot game (`key-quest-godot/`)

- [ ] Create the Godot 4.x project: `project.godot` with main scene, window
      size 1152×648, `canvas_items` stretch, nearest-neighbor filtering.
- [ ] Define the input map: `move_left` (←/A), `move_right` (→/D),
      `jump` (Space/↑/W).
- [ ] Add `GameState` autoload (`scripts/game_state.gd`): key counters,
      respawn point, level index, `key_collected` / `all_keys_collected`
      signals, `next_level()` / `restart()`.
- [ ] Add `scripts/levels.gd` with the 3 ASCII maps copied **verbatim** from
      SPECS.md §2.5.
- [ ] Build `Player.tscn` + `player.gd`: move 180 px/s, jump ≥ 3.5 tiles,
      coyote time 0.15 s, sprite flip, idle/run/jump animations, jump sound.
- [ ] Build `Key.tscn` + `key.gd`: spin animation, `body_entered` pickup,
      arpeggio + sparkle particles, updates `GameState`.
- [ ] Build `Elevator.tscn` + `elevator.gd`: `AnimatableBody2D`, sine-eased
      looping tween bottom↔top at 48 px/s with 1 s end pauses, carries the
      player.
- [ ] Build `Door.tscn` + `door.gd`: closed/grey until `all_keys_collected`,
      then open/green + chime + sparkles; entering loads the next level.
- [ ] Build `HUD.tscn` + `hud.gd`: one big key icon per key, grey → gold with
      a pop when collected. Icon-only, no text.
- [ ] Build `level_builder.gd` + `Level.tscn`: construct tiles, keys,
      elevators, door, player, edge walls, fall-respawn zone, and camera
      limits from the ASCII map for the current level index.
- [ ] Implement gentle respawn: falling below the map fades and returns the
      kid to the last ground position with a soft boop — no other effect.
- [ ] Build `Celebration.tscn`: confetti, big kid sprite, fanfare, icon-only
      replay that loops back to Level 1.
- [ ] Playtest pass: complete Levels 1→2→3→celebration→loop twice in a row.

## Phase 2 — Unity game (`key-quest-unity/`)

- [ ] Create the project skeleton: `Packages/manifest.json` (2D sprite +
      built-in modules), minimal `ProjectSettings/` (project version, Force
      Text serialization, build scene list, jump buttons W/↑), Unity
      `.gitignore`.
- [ ] Add `Assets/Levels/level1..3.txt` with the 3 ASCII maps copied
      **verbatim** from SPECS.md §2.5.
- [ ] Import generated sprites (Pixels Per Unit = 32, Point filter, no
      compression) and audio.
- [ ] Implement `GameManager.cs`: singleton, key counters, respawn point,
      `KeyCollected` / `AllKeysCollected` events, `NextLevel()` / `Restart()`.
- [ ] Implement `LevelBuilder.cs`: parse the map TextAsset and construct
      tiles (merged colliders), keys, elevators, door, player, edge walls,
      fall-respawn trigger; register key count; pass bounds to the camera.
- [ ] Implement `PlayerController.cs`: Rigidbody2D movement 5.6 u/s, jump
      ≥ 3.5 tiles, coyote time 0.15 s, ground check, sprite-swap animations,
      jump sound, respawn with fade + boop.
- [ ] Implement `KeyPickup.cs`: spin/bob, trigger pickup, arpeggio +
      sparkles, updates `GameManager`.
- [ ] Implement `ElevatorMover.cs`: kinematic sine-eased ping-pong at
      1.5 u/s with 1 s end pauses; parents the player while ridden.
- [ ] Implement `LevelExit.cs`: closed until `AllKeysCollected`, then open +
      chime + sparkles; trigger loads the next scene.
- [ ] Implement `HudController.cs`: icon-only key row, grey → gold pop on
      collect.
- [ ] Implement `CameraFollow.cs`: smooth follow clamped to level bounds,
      background `#0e1726`.
- [ ] Create the four scenes (`Level1..3`, `Celebration`) with only camera +
      Bootstrap + HUD canvas each, and add them to Build Settings.
- [ ] Build `Celebration.cs` scene content: confetti, big kid sprite,
      fanfare, icon-only replay looping back to Level 1.
- [ ] Playtest pass in the editor: complete Levels 1→2→3→celebration→loop
      twice in a row.

## Phase 3 — Wrap-up

- [ ] Update `game-development/README.md` entries if folder contents changed.
- [ ] Verify the Definition of Done below for **each** game, item by item.
- [ ] Commit and push everything to the designated branch.

## Definition of Done (applies to each game independently)

A game is **done** only when all of the following are true:

1. **Opens and runs with one click.** The Godot project opens in Godot 4.x
   with no script/parse errors and runs with F5; the Unity project opens in
   Unity 2022.3+ with no console errors and runs with Play from `Level1`.
2. **Fully completable.** All 3 levels can be finished start-to-finish:
   every key is reachable and collectable, the door opens **only** after all
   keys are collected, elevators can be ridden up and down reliably, level
   transitions work, and the celebration screen shows and loops back to
   Level 1.
3. **Impossible to lose.** No hazards or enemies exist; falling anywhere
   respawns the kid gently on the last platform with no penalty; there are
   no dead-ends or places the player can get stuck; invisible walls stop the
   kid at level edges.
4. **Kid-simple controls & UI.** Input is exactly arrows/WASD + Space; the
   HUD is icon-only (a 4-year-old needs no reading); feedback (sounds,
   sparkles, door color) matches the spec.
5. **Theme & assets complete.** All sprites and sounds are the generated
   pixel-art / chiptune assets from Phase 0 — no engine-default placeholders
   left anywhere; the tech theme (circuit tiles, chips, elevators, terminal
   door) is visible in every level.
6. **Level parity.** The three levels match the ASCII maps in the specs
   exactly, and are identical between the Godot and Unity editions.
7. **Spec-shaped code.** Scripts/scenes follow the structure named in the
   project's SPECS.md (same file names and responsibilities), and everything
   is committed and pushed to the designated branch.
