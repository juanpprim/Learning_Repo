# Intro to Godot

## Objectives
- Learn a real, production-grade game engine's workflow: scenes, nodes, signals.
- Understand GDScript basics and how it compares to Python.
- Build a small playable scene with input handling and collision via the engine's
  built-in physics.

## Key concepts
- Scenes and nodes as Godot's core building block (everything is a node tree).
- Signals for decoupled event handling (e.g. `body_entered` on an `Area2D`).
- `_ready()` and `_process(delta)` / `_physics_process(delta)` lifecycle methods.
- `CharacterBody2D` + `move_and_slide()` for built-in physics-based movement.
- Exporting variables (`@export`) to tune values from the editor instead of code.

## Resources
- Godot docs — "Your first 2D game" official tutorial: https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html
- Godot docs — GDScript basics: https://docs.godotengine.org/en/stable/getting_started/scripting/gdscript/gdscript_basics.html
- Download the editor: https://godotengine.org/download

## Checklist
- [ ] Install the Godot editor and create a new project.
- [ ] Build a scene with a player node using `CharacterBody2D` and handle
      keyboard input to move it.
- [ ] Add an `Area2D` (e.g. a coin or obstacle) and connect its `body_entered`
      signal to a script method.
- [ ] Use `@export` to expose a tunable value (speed, health) in the editor.
- [ ] Package the project so it can be re-opened (commit the Godot project
      folder here once started).

## Mini-project
Follow the official "Your first 2D game" tutorial end-to-end (Dodge the
Creeps), then extend it with one original mechanic (power-up, second enemy
type, or a scoring twist). Commit the Godot project into this folder.

## Notes
Godot projects are editor-authored (scenes, resources) rather than pure code,
so there's no meaningful "starter script" to scaffold here — `player.gd`
below is a reference snippet to paste into a `CharacterBody2D` script once you
create the project in the editor.
