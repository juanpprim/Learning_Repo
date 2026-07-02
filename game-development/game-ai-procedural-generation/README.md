# Game AI & Procedural Generation

## Objectives
- Implement pathfinding (A*) for NPC/enemy movement on a grid.
- Generate procedural levels/terrain using noise functions.
- Understand basic game AI patterns: state machines and behavior trees at a
  conceptual level.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- A* search: heuristics, open/closed sets, and why it beats plain Dijkstra for
  games (goal-directed search).
- Grid vs. navmesh pathfinding.
- Perlin/Simplex noise for terrain height maps and cave generation.
- Cellular automata for cave-like procedural generation (Conway's-Game-of-Life-style rules).
- Finite state machines for simple NPC behavior (patrol -> chase -> attack).

## Resources
- Red Blob Games — "Introduction to A*": https://www.redblobgames.com/pathfinding/a-star/introduction.html
- Red Blob Games — "Noise" (procedural generation): https://www.redblobgames.com/articles/noise/introduction.html
- "Procedural Content Generation in Games" (free book): https://pcgbook.com/

## Checklist
- [ ] Implement A* on a 2D grid with obstacles and visualize the found path.
- [ ] Generate a height map using Perlin/Simplex noise and visualize it as a heatmap.
- [ ] Generate a cave-like map using cellular automata (random fill + smoothing passes).
- [ ] Implement a simple NPC finite state machine (patrol -> chase when player is
      within range -> return to patrol).

## Mini-project
Generate a procedural 2D level (noise-based terrain or cellular-automata cave),
place a start and goal, and run A* to find and visualize a path across it —
tie it back to `python-game-basics-pygame/` if you want it rendered live.
