"""Append-only JSONL event ledger with crash-safe atomic writes.

Deliberately NOT a second writer of LOOP_LOG.md: the controller renders LOOP_LOG.md
itself with a byte-exact append protocol (robot_agentic_training_flow.md), so this
module only ever writes its own `events.jsonl` and renders a human view to a
DISTINCT file or stdout — never LOOP_LOG.md.

`crash_hook` lets tests inject a crash at each write boundary
(prepare / write / fsync / rename) to prove that a target file is always either
fully old or fully new, never torn.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

# A crash hook is called with the name of the boundary about to be crossed; if it
# raises, the write is interrupted at exactly that point.
CrashHook = Callable[[str], None]

EVENTS_FILENAME = "events.jsonl"


def _crash(hook: CrashHook | None, boundary: str) -> None:
    if hook is not None:
        hook(boundary)


def _write_all(fd: int, data: bytes) -> None:
    """Write every byte, looping over short writes so the payload is never torn."""

    view = memoryview(data)
    while view:
        view = view[os.write(fd, view) :]


def _fsync_dir(path: Path) -> None:
    dir_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def atomic_write(path: str | Path, data: bytes, *, crash_hook: CrashHook | None = None) -> None:
    """Write `data` to `path` atomically: prepare -> write -> fsync -> rename.

    A crash at any boundary leaves `path` untouched (temp discarded) until the
    rename, and fully-new after it — the target is never a torn partial file.
    """

    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")

    _crash(crash_hook, "prepare")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        _write_all(fd, data)
        _crash(crash_hook, "write")
        os.fsync(fd)
        _crash(crash_hook, "fsync")
    finally:
        os.close(fd)

    os.replace(tmp, path)
    _crash(crash_hook, "rename")
    _fsync_dir(path)


def append_event(
    events_path: str | Path, event: dict[str, Any], *, crash_hook: CrashHook | None = None
) -> None:
    """Append one canonical JSON event as a single line to the JSONL ledger.

    The line is serialized then written in a single O_APPEND write (atomic on
    POSIX for a line under PIPE_BUF), followed by fsync.
    """

    events_path = Path(events_path)
    line = (json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")

    _crash(crash_hook, "prepare")
    existed = events_path.exists()
    fd = os.open(events_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        _write_all(fd, line)
        _crash(crash_hook, "write")
        os.fsync(fd)
        _crash(crash_hook, "fsync")
    finally:
        os.close(fd)
    if not existed:
        _fsync_dir(events_path)


def read_events(events_path: str | Path) -> list[dict[str, Any]]:
    """Read the JSONL event ledger. Returns [] if absent; skips blank lines."""

    events_path = Path(events_path)
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for lineno, line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{events_path}:{lineno}: invalid JSON event: {exc}") from None
    return events


def render_events_markdown(events: Iterable[dict[str, Any]]) -> str:
    """Render events as a human-readable markdown VIEW (never written to LOOP_LOG.md)."""

    lines = ["# Event ledger (human view)", ""]
    for event in events:
        kind = event.get("event", "event")
        rnd = event.get("round")
        header = f"## {kind}" + (f" — round {rnd}" if rnd is not None else "")
        lines.append(header)
        for key in sorted(k for k in event if k not in {"event", "round"}):
            lines.append(f"- {key}: {event[key]}")
        lines.append("")
    return "\n".join(lines)
