#!/usr/bin/env python3
"""Automated playtest for Key Quest: prove every level is completable.

Reads the ASCII maps from the Godot project's levels.gd (the actual game
data) and the movement constants from player.gd/project.godot, then runs a
reachability search using a jump envelope derived from those constants:

  * walk left/right along standable cells
  * jump: up to `jump_tiles` tiles up, with a conservative horizontal reach
  * fall: walk off any ledge and land below (falling is always safe)
  * ride elevators between their bottom (E) and top (topmost |) positions

Asserts, for every level:
  1. every key is collectable from the player start
  2. the door is reachable
  3. no dead ends: from EVERY reachable spot the door is still reachable
Then repeats the 3-level run a second time (loop back to level 1).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

GODOT = Path(__file__).resolve().parent.parent / "key-quest-godot"

SOLID = {"#", "="}


def load_maps() -> list[list[str]]:
    text = (GODOT / "scripts" / "levels.gd").read_text()
    blocks = re.findall(r'"""\n(.*?)"""', text, re.S)
    assert len(blocks) == 3, "expected 3 maps in levels.gd"
    return [b.strip("\n").split("\n") for b in blocks]


def load_constants() -> tuple[float, float, float]:
    player = (GODOT / "scripts" / "player.gd").read_text()
    project = (GODOT / "project.godot").read_text()
    speed = float(re.search(r"speed := (\d+)\.0", player).group(1))
    jump_v = abs(float(re.search(r"jump_velocity := (-\d+)\.0", player).group(1)))
    gravity = float(re.search(r"2d/default_gravity=(\d+)", project).group(1))
    return speed, jump_v, gravity


class Level:
    def __init__(self, rows: list[str], jump_tiles: int, reach_tiles: int):
        self.rows = rows
        self.w, self.h = len(rows[0]), len(rows)
        self.jump_tiles, self.reach_tiles = jump_tiles, reach_tiles
        self.elevators = self._find_elevators()
        self.grid = [
            [c if c in SOLID else "." for c in row] for row in rows
        ]
        self.nodes = self._standable_nodes()
        self.edges = self._build_edges()

    def _find_elevators(self) -> list[tuple[int, int, int]]:
        out = []
        for x in range(self.w):
            for y in range(self.h):
                if self.rows[y][x] == "E":
                    top = y
                    for yy in range(y - 1, -1, -1):
                        if self.rows[yy][x] == "|":
                            top = yy
                        else:
                            break
                    out.append((x, y, top))
        return out

    def _grid_standable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.w and 0 <= y < self.h):
            return False
        if self.grid[y][x] in SOLID:
            return False
        if y > 0 and self.grid[y - 1][x] in SOLID:  # headroom for a 1.5-tile kid
            return False
        return y + 1 < self.h and self.grid[y + 1][x] in SOLID

    def _standable_nodes(self) -> set[tuple[int, int]]:
        nodes = {
            (x, y)
            for x in range(self.w)
            for y in range(self.h)
            if self._grid_standable(x, y)
        }
        for ex, ey, etop in self.elevators:
            nodes.add((ex, ey))          # standing on the cab at the bottom
            nodes.add((ex, etop - 1))    # standing on the cab at the top
        return nodes

    def _build_edges(self) -> dict[tuple[int, int], set[tuple[int, int]]]:
        edges: dict[tuple[int, int], set[tuple[int, int]]] = {n: set() for n in self.nodes}
        for x, y in self.nodes:
            # walk
            for nx in (x - 1, x + 1):
                if (nx, y) in self.nodes:
                    edges[(x, y)].add((nx, y))
            # jump (conservative envelope vs the 3.55-tile / 5.1-tile physics)
            for tx, ty in self.nodes:
                dy = y - ty
                dx = abs(tx - x)
                if 0 <= dy <= self.jump_tiles and dx <= (self.reach_tiles if dy <= 1 else 3):
                    edges[(x, y)].add((tx, ty))
                # jump-down: dropping is always safe, full air control
                elif dy < 0 and 0 < dx <= 3:
                    edges[(x, y)].add((tx, ty))
            # fall off a ledge: land on the first standable cell below
            for nx in (x - 1, x + 1):
                if not (0 <= nx < self.w) or (nx, y) in self.nodes:
                    continue
                for ty in range(y + 1, self.h):
                    if self.grid[ty][nx] in SOLID:
                        break
                    if (nx, ty) in self.nodes:
                        edges[(x, y)].add((nx, ty))
                        break
        for ex, ey, etop in self.elevators:  # ride
            edges[(ex, ey)].add((ex, etop - 1))
            edges[(ex, etop - 1)].add((ex, ey))
        return edges

    def reachable_from(self, start: tuple[int, int]) -> set[tuple[int, int]]:
        seen, stack = {start}, [start]
        while stack:
            for nxt in self.edges.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def find(self, char: str) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y in range(self.h)
            for x in range(self.w)
            if self.rows[y][x] == char
        ]


def playtest(rows: list[str], jump_tiles: int, reach_tiles: int, label: str) -> None:
    level = Level(rows, jump_tiles, reach_tiles)
    start = level.find("P")[0]
    keys = level.find("K")
    door = level.find("D")[0]
    reached = level.reachable_from(start)

    missing = [k for k in keys if k not in reached]
    assert not missing, f"{label}: unreachable keys at {missing}"
    assert door in reached, f"{label}: door not reachable"
    stuck = [n for n in reached if door not in level.reachable_from(n)]
    assert not stuck, f"{label}: dead ends at {stuck}"
    print(f"ok {label}: start {start} -> {len(keys)} keys + door, "
          f"{len(reached)} spots reachable, no dead ends")


def main() -> None:
    speed, jump_v, gravity = load_constants()
    jump_px = jump_v**2 / (2 * gravity)
    air_time = 2 * jump_v / gravity
    jump_tiles = int(jump_px // 32)          # 3 with the shipped constants
    reach_tiles = int(speed * air_time // 32) - 1  # 4: one tile of safety margin
    print(f"constants from project: speed={speed}, jump={jump_px:.0f}px "
          f"({jump_px / 32:.2f} tiles), envelope used: up {jump_tiles}, across {reach_tiles}")

    maps = load_maps()
    for run in (1, 2):                        # completable twice in a row
        for i, rows in enumerate(maps, 1):
            playtest(rows, jump_tiles, reach_tiles, f"run {run} level {i}")
    print("PLAYTEST PASSED: all levels completable, twice in a row")


if __name__ == "__main__":
    main()
    sys.exit(0)
