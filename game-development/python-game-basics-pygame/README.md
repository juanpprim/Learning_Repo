# Python Game Basics with Pygame

## Objectives
- Build and understand the core game loop: input -> update -> render, at a fixed tick rate.
- Handle sprites, collision detection, and basic physics (gravity, velocity).
- Manage simple game state (menu -> playing -> game over).

## Key concepts
- The game loop and frame rate (`clock.tick(FPS)`), and why it must run at a
  consistent rate regardless of hardware speed.
- `pygame.sprite.Sprite` / `Group` for organizing and updating game objects.
- Rect-based collision detection (`colliderect`) vs. pixel-perfect collision.
- Delta time for frame-rate-independent movement.
- A simple state machine for game screens (menu, playing, game over).

## Resources
- Pygame docs: https://www.pygame.org/docs/
- "Making Games with Python & Pygame" (free ebook by Al Sweigart): https://inventwithpython.com/pygame/

## Checklist
- [ ] Get a window open with a game loop running at a fixed FPS.
- [ ] Move a sprite with keyboard input, frame-rate independent (using delta time).
- [ ] Add a second sprite and detect collisions between them.
- [ ] Add a simple state machine: start menu -> playing -> game-over screen.
- [ ] Add a score or health value that changes based on collisions/events.

## Mini-project
Build a small complete game (e.g. a Breakout/Pong/simple shooter clone) in
`src/` with a menu, playing state, collision-based scoring, and a game-over
screen. Playable end-to-end with `python src/main.py`.
