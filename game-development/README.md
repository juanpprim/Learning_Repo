# Game Development

A deliberate stretch track outside data pipelines — good general-purpose
programming and architecture practice (real-time loops, state machines,
performance-sensitive code).

1. [`python-game-basics-pygame/`](python-game-basics-pygame/) — game loop, sprites, collision in pure Python.
2. [`godot-intro/`](godot-intro/) — a real game engine, scenes, and GDScript.
3. [`game-ai-procedural-generation/`](game-ai-procedural-generation/) — pathfinding and procedural level generation.
4. [`key-quest-godot/`](key-quest-godot/) — *Techie Kid: Key Quest* in Godot 4: a hazard-free platformer for a 4–5 year old (kid collects keys in a computer world with elevators). Open the folder in Godot 4.x and press F5.
5. [`key-quest-unity/`](key-quest-unity/) — the same game rebuilt in Unity/C# (2022.3 LTS+, 2D), for a direct engine-to-engine comparison. Add the folder in Unity Hub, open `Assets/Scenes/Level1.unity`, press Play.

The two Key Quest projects share one design (same levels, art, and rules);
their specs live in each folder's `SPECS.md` and the build is tracked in
[`KEY_QUEST_IMPLEMENTATION.md`](KEY_QUEST_IMPLEMENTATION.md). All pixel-art
sprites, chiptune sounds, Unity metas/scenes, and the automated playtest
come from the scripts in [`tools/`](tools/).

Unlike the other tracks, these subtopics are mostly script/project-based
rather than notebooks (games need a real-time loop, not cell-by-cell execution).
