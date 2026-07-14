#!/usr/bin/env python3
"""Convert normalized word/segment JSON into readable SRT captions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BREAK_RE = re.compile(r"[.!?。！？…][\"'”’）)]*$")
CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]")
NO_SPACE_BEFORE_RE = re.compile(r"^[,.;:!?，。；：！？、…%％）】》”’]")
NO_SPACE_AFTER_RE = re.compile(r"[（【《“‘]$")
CJK_CONTINUATION_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff，。；：！？、…（【《“‘）】》”’]$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Normalized transcript JSON")
    parser.add_argument("output", type=Path, help="Destination .srt file")
    parser.add_argument("--max-words", type=int, default=5)
    parser.add_argument("--max-chars", type=int, default=32)
    parser.add_argument("--max-duration", type=float, default=3.5)
    parser.add_argument("--pause", type=float, default=0.15)
    return parser.parse_args()


def flatten_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        for key in ("words", "transcript", "segments"):
            if isinstance(data.get(key), list):
                entries = data[key]
                break
        else:
            raise ValueError("JSON must contain a words, transcript, or segments list")
    else:
        raise ValueError("Transcript JSON must be a list or object")

    flattened: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if isinstance(entry.get("words"), list):
            flattened.extend(x for x in entry["words"] if isinstance(x, dict))
        else:
            flattened.append(entry)
    return flattened


def normalize(data: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in flatten_entries(data):
        text = str(entry.get("text", entry.get("word", ""))).strip()
        if not text:
            continue
        try:
            start = float(entry["start"])
            end = float(entry["end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid timestamp entry: {entry!r}") from exc
        if start < 0 or end <= start:
            raise ValueError(f"Invalid timestamp range: {entry!r}")
        normalized.append({"text": text, "start": start, "end": end})
    normalized.sort(key=lambda x: (x["start"], x["end"]))
    if not normalized:
        raise ValueError("Transcript contains no usable timed text")
    return normalized


def smart_join(parts: list[str]) -> str:
    result = ""
    for part in parts:
        if not result:
            result = part
        elif NO_SPACE_BEFORE_RE.search(part) or NO_SPACE_AFTER_RE.search(result):
            result += part
        elif CJK_CONTINUATION_RE.search(result) and CJK_RE.search(part[0]):
            result += part
        else:
            result += " " + part
    return result


def group_entries(entries: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal current
        if current:
            groups.append({
                "start": current[0]["start"],
                "end": current[-1]["end"],
                "text": smart_join([item["text"] for item in current]),
            })
            current = []

    for entry in entries:
        if current:
            candidate = smart_join([item["text"] for item in current] + [entry["text"]])
            gap = entry["start"] - current[-1]["end"]
            duration = entry["end"] - current[0]["start"]
            must_break = (
                gap >= args.pause
                or len(current) >= args.max_words
                or len(candidate) > args.max_chars
                or duration > args.max_duration
            )
            if must_break:
                flush()
        current.append(entry)
        if BREAK_RE.search(entry["text"]):
            flush()
    flush()
    return groups


def srt_time(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main() -> int:
    args = parse_args()
    if args.max_words < 1 or args.max_chars < 1 or args.max_duration <= 0 or args.pause < 0:
        raise SystemExit("Grouping limits must be positive (pause may be zero)")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    groups = group_entries(normalize(data), args)
    blocks = []
    for index, group in enumerate(groups, 1):
        blocks.append(
            f"{index}\n{srt_time(group['start'])} --> {srt_time(group['end'])}\n{group['text']}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"Wrote {len(groups)} captions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
