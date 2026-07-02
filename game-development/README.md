# Game Development

A deliberate stretch track outside data pipelines — good general-purpose
programming and architecture practice (real-time loops, state machines,
performance-sensitive code).

1. [`python-game-basics-pygame/`](python-game-basics-pygame/) — game loop, sprites, collision in pure Python.
2. [`godot-intro/`](godot-intro/) — a real game engine, scenes, and GDScript.
3. [`game-ai-procedural-generation/`](game-ai-procedural-generation/) — pathfinding and procedural level generation.
4. [`key-quest-godot/`](key-quest-godot/) — *Techie Kid: Key Quest* in Godot 4: a hazard-free platformer for a 4–5 year old (kid collects keys in a computer world with elevators).
5. [`key-quest-unity/`](key-quest-unity/) — the same game rebuilt in Unity/C#, for a direct engine-to-engine comparison.

The two Key Quest projects share one design (same levels, art, and rules);
their specs live in each folder's `SPECS.md` and the build is tracked in
[`KEY_QUEST_IMPLEMENTATION.md`](KEY_QUEST_IMPLEMENTATION.md).

Unlike the other tracks, these subtopics are mostly script/project-based
rather than notebooks (games need a real-time loop, not cell-by-cell execution).
