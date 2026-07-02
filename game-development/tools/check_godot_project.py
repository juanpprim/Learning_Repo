#!/usr/bin/env python3
"""Static validator for the Key Quest Godot project.

Godot itself is not available in every environment, so this checks what can
be checked without the engine:

  * every .gd script parses (gdparse from gdtoolkit)
  * every .tscn: load_steps matches resource count, every ext_resource path
    exists on disk, every ExtResource()/SubResource() reference is defined,
    every node's parent exists, script/scene ext_resources resolve
  * project.godot: main scene and autoload paths exist

Exit code 0 = all good.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent / "key-quest-godot"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    fail.count += 1


fail.count = 0


def res_path(res: str) -> Path:
    return PROJECT / res.removeprefix("res://")


def check_scripts() -> None:
    scripts = sorted(PROJECT.rglob("*.gd"))
    result = subprocess.run(["gdparse", *map(str, scripts)], capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"gdparse: {result.stdout} {result.stderr}")
    else:
        print(f"ok: {len(scripts)} scripts parse")


def check_scene(path: Path) -> None:
    text = path.read_text()
    header = re.match(r'\[gd_scene load_steps=(\d+) format=3\]', text)
    if not header:
        fail(f"{path.name}: bad gd_scene header")
        return
    ext = re.findall(r'\[ext_resource type="(\w+)" path="([^"]+)" id="([^"]+)"\]', text)
    sub = re.findall(r'\[sub_resource type="(\w+)" id="([^"]+)"\]', text)
    if int(header.group(1)) != len(ext) + len(sub) + 1:
        fail(f"{path.name}: load_steps={header.group(1)} but "
             f"{len(ext)} ext + {len(sub)} sub resources")
    for _type, res, _id in ext:
        if not res_path(res).exists():
            fail(f"{path.name}: missing resource {res}")
    ext_ids = {e[2] for e in ext}
    sub_ids = {s[1] for s in sub}
    for ref in re.findall(r'ExtResource\("([^"]+)"\)', text):
        if ref not in ext_ids:
            fail(f"{path.name}: undefined ExtResource({ref})")
    for ref in re.findall(r'SubResource\("([^"]+)"\)', text):
        if ref not in sub_ids:
            fail(f"{path.name}: undefined SubResource({ref})")
    nodes = re.findall(r'\[node name="([^"]+)"(?: type="(\w+)")?'
                       r'(?: parent="([^"]*)")?', text)
    paths = set()
    for name, _type, parent in nodes:
        if parent is None or parent == "":
            if paths:
                fail(f"{path.name}: multiple root nodes?")
            paths.add(".")
            root = name
        else:
            if parent not in paths:
                fail(f"{path.name}: node {name} has unknown parent {parent}")
            paths.add(name if parent == "." else f"{parent}/{name}")
    print(f"ok: {path.name} ({len(nodes)} nodes, {len(ext)} ext, {len(sub)} sub)")


def check_project_file() -> None:
    text = (PROJECT / "project.godot").read_text()
    for res in re.findall(r'"(res://[^"]+)"', text) + re.findall(r'="\*?(res://[^"]+)"', text):
        if not res_path(res).exists():
            fail(f"project.godot: missing {res}")
    print("ok: project.godot resource paths resolve")


def main() -> None:
    check_scripts()
    for scene in sorted(PROJECT.rglob("*.tscn")):
        check_scene(scene)
    check_project_file()
    if fail.count:
        sys.exit(f"{fail.count} problems")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
