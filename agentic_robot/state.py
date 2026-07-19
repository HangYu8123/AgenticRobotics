"""Typed, versioned view over decoded durable round-state snapshots.

The on-disk record (ROUND_IN_PROGRESS.md) is markdown-encoded and is deliberately
NOT parsed here — see recovery/round_state.schema.json. This module works with the
already-decoded logical mapping: it pins the current schema version and provides a
single, honest migration seam (not a framework — there is only version 1 today).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CURRENT_SCHEMA_VERSION = 1

# Optional JSONL export of decoded snapshots, if a run chooses to produce one for
# offline replay checking. The flow itself does not require it.
SNAPSHOTS_FILENAME = "state_snapshots.jsonl"


def migrate(state: dict[str, Any]) -> dict[str, Any]:
    """Upgrade a decoded snapshot to CURRENT_SCHEMA_VERSION.

    Identity for the only version that exists (1). New versions register their
    step here; an unknown version raises rather than guessing.
    """

    version = state.get("schema_version")
    if version == CURRENT_SCHEMA_VERSION:
        return state
    raise ValueError(
        f"unsupported schema_version {version!r}; no migration registered "
        f"(current={CURRENT_SCHEMA_VERSION})"
    )


def load_snapshots(run_dir: str | Path) -> list[dict[str, Any]]:
    """Load decoded state snapshots from <run_dir>/state_snapshots.jsonl.

    Returns [] when the file is absent (the flow stores ROUND_IN_PROGRESS.md, not
    this JSONL — callers should say so). Each non-blank line is one snapshot.
    """

    path = Path(run_dir) / SNAPSHOTS_FILENAME
    if not path.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            snapshot = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON snapshot: {exc}") from None
        snapshots.append(migrate(snapshot))
    return snapshots
