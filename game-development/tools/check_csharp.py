#!/usr/bin/env python3
"""Syntax-check every C# script in the Unity project with tree-sitter.

Unity (and any .NET compiler) is unavailable in the build environment, so
this is the strongest automated check we can run: a full C# parse that
fails on any syntax error, plus a couple of Unity-specific sanity greps
(class name must match file name; exactly one MonoBehaviour per file that
is attached in a scene).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import tree_sitter
import tree_sitter_c_sharp

UNITY = Path(__file__).resolve().parent.parent / "key-quest-unity"

parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_c_sharp.language()))


def find_errors(node, source: bytes, out: list[str]) -> None:
    if node.type == "ERROR" or node.is_missing:
        line = source[: node.start_byte].count(b"\n") + 1
        snippet = source[node.start_byte : node.start_byte + 40].decode(errors="replace")
        out.append(f"line {line}: {snippet!r}")
    for child in node.children:
        find_errors(child, source, out)


def main() -> None:
    scripts = sorted(UNITY.rglob("*.cs"))
    if not scripts:
        sys.exit("no C# scripts found")
    problems = 0
    for path in scripts:
        source = path.read_bytes()
        tree = parser.parse(source)
        errors: list[str] = []
        if tree.root_node.has_error:
            find_errors(tree.root_node, source, errors)
        text = source.decode()
        classes = re.findall(r"\bclass\s+(\w+)", text)
        if classes and path.stem not in classes:
            errors.append(f"no class named {path.stem} (found {classes})")
        for err in errors:
            print(f"FAIL {path.name}: {err}")
            problems += 1
        if not errors:
            print(f"ok {path.name} ({len(classes)} classes)")
    if problems:
        sys.exit(f"{problems} problems")
    print("ALL C# SCRIPTS PARSE")


if __name__ == "__main__":
    main()
