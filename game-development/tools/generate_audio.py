#!/usr/bin/env python3
"""Generate all chiptune-style sounds for Techie Kid: Key Quest.

Produces every WAV listed in the specs (SPECS.md §2.7) and writes them into
both game projects:

    key-quest-godot/assets/audio/
    key-quest-unity/Assets/Audio/

Usage:
    python3 generate_audio.py             # write into both projects
    python3 generate_audio.py --out DIR   # write into DIR instead
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_TARGETS = [
    HERE.parent / "key-quest-godot" / "assets" / "audio",
    HERE.parent / "key-quest-unity" / "Assets" / "Resources" / "Audio",
]

SAMPLE_RATE = 44100

# Note frequencies (Hz).
C5, E5, G5, A5 = 523.25, 659.25, 783.99, 880.00
C6, E6, G6 = 1046.50, 1318.51, 1567.98


def _time(duration: float) -> np.ndarray:
    return np.arange(int(SAMPLE_RATE * duration)) / SAMPLE_RATE


def square(freq: float | np.ndarray, t: np.ndarray, duty: float = 0.5) -> np.ndarray:
    phase = np.cumsum(np.broadcast_to(freq, t.shape) / SAMPLE_RATE)
    return np.where((phase % 1.0) < duty, 1.0, -1.0)


def sine(freq: float, t: np.ndarray) -> np.ndarray:
    return np.sin(2 * np.pi * freq * t)


def decay(t: np.ndarray, rate: float) -> np.ndarray:
    return np.exp(-rate * t)


def fade_edges(samples: np.ndarray, ms: float = 4.0) -> np.ndarray:
    n = int(SAMPLE_RATE * ms / 1000)
    if n and len(samples) > 2 * n:
        ramp = np.linspace(0.0, 1.0, n)
        samples = samples.copy()
        samples[:n] *= ramp
        samples[-n:] *= ramp[::-1]
    return samples


def note(freq: float, duration: float, wave_fn=square, decay_rate: float = 6.0,
         volume: float = 1.0) -> np.ndarray:
    t = _time(duration)
    return wave_fn(freq, t) * decay(t, decay_rate) * volume


def sequence(notes: list[tuple[float, float]], **kwargs) -> np.ndarray:
    return np.concatenate([note(f, d, **kwargs) for f, d in notes])


def jump_sound() -> np.ndarray:
    """Short upward square-wave sweep, ~0.15 s."""
    t = _time(0.15)
    freq = 300 + 2000 * t          # 300 -> 600 Hz over the sweep
    return square(freq, t, duty=0.3) * decay(t, 12.0) * 0.5


def key_sound() -> np.ndarray:
    """Rising three-note arpeggio, ~0.3 s."""
    return sequence([(E5, 0.09), (G5, 0.09), (C6, 0.12)],
                    decay_rate=10.0, volume=0.45)


def door_sound() -> np.ndarray:
    """Soft chime: a major triad blooming together, ~0.6 s."""
    t = _time(0.6)
    chord = (sine(C5, t) + sine(E5, t) + sine(G5, t) + 0.5 * sine(C6, t)) / 3.5
    return chord * decay(t, 4.0) * 0.6


def win_sound() -> np.ndarray:
    """Celebration fanfare, ~1.5 s."""
    melody = sequence(
        [(C5, 0.15), (E5, 0.15), (G5, 0.15), (C6, 0.25),
         (G5, 0.12), (C6, 0.28)],
        decay_rate=5.0, volume=0.4,
    )
    tail_t = _time(0.4)
    tail = (sine(C6, tail_t) + sine(E6, tail_t) + sine(G6, tail_t)) / 3.0
    tail = tail * decay(tail_t, 5.0) * 0.5
    return np.concatenate([melody, tail])


def boop_sound() -> np.ndarray:
    """Gentle respawn boop: soft low sine, ~0.2 s. Friendly, not a fail sound."""
    t = _time(0.2)
    return sine(220, t) * decay(t, 10.0) * 0.4


SOUNDS = {
    "jump": jump_sound,
    "key": key_sound,
    "door": door_sound,
    "win": win_sound,
    "boop": boop_sound,
}


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = fade_edges(np.clip(samples, -1.0, 1.0))
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None,
                        help="write WAVs to this directory instead of both projects")
    args = parser.parse_args()

    rendered = {name: build() for name, build in SOUNDS.items()}
    targets = [args.out] if args.out else DEFAULT_TARGETS
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for name, samples in rendered.items():
            write_wav(target / f"{name}.wav", samples)
            print(f"  {name}.wav  {len(samples) / SAMPLE_RATE:.2f}s")
        print(f"wrote {len(rendered)} sounds -> {target}")


if __name__ == "__main__":
    main()
