#!/usr/bin/env python3
"""Verify a captioned render and its optional normalized transcript."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


MUSIC_RE = re.compile(r"^[♪♫♬♩�]+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--duration-seconds", type=float, default=1.0)
    parser.add_argument("--duration-ratio", type=float, default=0.03)
    return parser.parse_args()


def probe(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Missing media file: {path}")
    command = [
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed for {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def duration(info: dict[str, Any]) -> float:
    candidates = [info.get("format", {}).get("duration")]
    candidates.extend(stream.get("duration") for stream in info.get("streams", []))
    values = []
    for candidate in candidates:
        try:
            values.append(float(candidate))
        except (TypeError, ValueError):
            pass
    if not values or max(values) <= 0:
        raise ValueError("Media has no positive duration")
    return max(values)


def video_stream(info: dict[str, Any]) -> dict[str, Any] | None:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)


def has_audio(info: dict[str, Any]) -> bool:
    return any(s.get("codec_type") == "audio" for s in info.get("streams", []))


def transcript_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = next(
            (data[key] for key in ("words", "transcript", "segments") if isinstance(data.get(key), list)),
            [],
        )
    else:
        entries = []
    flattened: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if isinstance(entry.get("words"), list):
            flattened.extend(x for x in entry["words"] if isinstance(x, dict))
        else:
            flattened.append(entry)
    return flattened


def verify_transcript(path: Path, output_duration: float, errors: list[str], notes: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing transcript: {path}")
        return
    try:
        entries = transcript_entries(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read transcript JSON: {exc}")
        return
    if not entries:
        errors.append("Transcript has no timed entries")
        return

    invalid = 0
    noise = 0
    previous_start = -1.0
    last_end = 0.0
    for entry in entries:
        text = str(entry.get("text", entry.get("word", ""))).strip()
        if MUSIC_RE.fullmatch(text):
            noise += 1
        try:
            start = float(entry["start"])
            end = float(entry["end"])
        except (KeyError, TypeError, ValueError):
            invalid += 1
            continue
        if not text or start < 0 or end <= start or start + 0.08 < previous_start:
            invalid += 1
        previous_start = max(previous_start, start)
        last_end = max(last_end, end)

    if invalid:
        errors.append(f"Transcript contains {invalid} invalid or unsorted entries")
    noise_ratio = noise / len(entries)
    if noise_ratio > 0.20:
        errors.append(f"Transcript music/replacement token ratio is {noise_ratio:.1%} (>20%)")
    if last_end > output_duration + 0.5:
        errors.append(
            f"Transcript ends at {last_end:.3f}s, after output duration {output_duration:.3f}s"
        )
    notes.append(f"Transcript entries: {len(entries)}; noise tokens: {noise} ({noise_ratio:.1%})")


def main() -> int:
    args = parse_args()
    if not shutil.which("ffprobe"):
        raise SystemExit("ffprobe is required but was not found on PATH")

    errors: list[str] = []
    notes: list[str] = []
    try:
        source = probe(args.source)
        output = probe(args.output)
        source_duration = duration(source)
        output_duration = duration(output)
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    source_video = video_stream(source)
    output_video = video_stream(output)
    if source_video is None:
        errors.append("Source has no video stream")
    if output_video is None:
        errors.append("Output has no video stream")
    if has_audio(source) and not has_audio(output):
        errors.append("Source has audio but output has no audio stream")

    tolerance = max(args.duration_seconds, source_duration * args.duration_ratio)
    drift = abs(output_duration - source_duration)
    if drift > tolerance:
        errors.append(
            f"Duration drift is {drift:.3f}s; allowed tolerance is {tolerance:.3f}s"
        )

    if output_video:
        width = int(output_video.get("width", 0) or 0)
        height = int(output_video.get("height", 0) or 0)
        if width <= 0 or height <= 0:
            errors.append("Output video has invalid dimensions")
        if args.width is not None and width != args.width:
            errors.append(f"Output width is {width}, expected {args.width}")
        if args.height is not None and height != args.height:
            errors.append(f"Output height is {height}, expected {args.height}")
        notes.append(f"Output dimensions: {width}x{height}")

    if args.output.stat().st_size < 10_000:
        errors.append("Output file is unexpectedly small (<10 KB)")

    notes.append(
        f"Duration: source {source_duration:.3f}s; output {output_duration:.3f}s; drift {drift:.3f}s"
    )
    if args.transcript:
        verify_transcript(args.transcript, output_duration, errors, notes)

    report = {"ok": not errors, "errors": errors, "notes": notes}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

