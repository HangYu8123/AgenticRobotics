"""Load and validate an objective spec against objective.schema.json.

Mirrors the prose contract documented in robot_agentic_training_flow.md Step 0
and the [command preflight] rules documented in objective.example.yaml. Pure and
deterministic — reads the objective, never writes it.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

_ALLOWED_PLACEHOLDERS = {"checkpoint", "eval_dir"}
_PLACEHOLDER_RE = re.compile(r"\{([^}]*)\}")
_REDIRECT_RE = re.compile(r"(?:>>?|<)\s*(\S+)")
_DEFAULT_EXECUTABLES = ("uv", "python")

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_PATH = _REPO_ROOT / "objective.schema.json"


def objective_digest(text: str) -> str:
    """The Step 0 integrity digest: sha256 of the raw objective bytes."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_objective(path: str | Path) -> dict[str, Any]:
    """Parse the YAML objective. Raises ValueError on a non-mapping document."""

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("objective must be a YAML mapping")
    return data


def _load_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _join_continuations(command: str) -> list[str]:
    """Join backslash line-continuations, then split into logical command lines."""

    joined = re.sub(r"\\\n", " ", command)
    return [line.strip() for line in joined.splitlines() if line.strip()]


def command_preflight(command: str, *, run_dir: str, allowed_executables: list[str]) -> list[str]:
    """Return a list of [command preflight] violations (empty means it passes).

    Enforces the rules documented in objective.example.yaml: only the two known
    placeholders; first token of every logical command must be uv/python or an
    allowed executable; no `;`, backticks, `$(...)`, or background `&`; no
    redirection outside the run dir.
    """

    violations: list[str] = []

    for name in _PLACEHOLDER_RE.findall(command):
        if name not in _ALLOWED_PLACEHOLDERS:
            violations.append(f"unknown placeholder {{{name}}} (only {{checkpoint}}/{{eval_dir}})")

    for token in (";", "`", "$(", "&", "|"):
        if token in command:
            violations.append(f"forbidden shell metacharacter {token!r}")

    allowed = set(_DEFAULT_EXECUTABLES) | set(allowed_executables)
    for line in _join_continuations(command):
        first = line.split()[0] if line.split() else ""
        if first not in allowed:
            violations.append(
                f"command must start with one of {sorted(allowed)}, got {first!r}"
            )
        for target in _REDIRECT_RE.findall(line):
            if not _redirect_within_run_dir(target, run_dir):
                violations.append(f"redirection target {target!r} is outside the run dir")

    return violations


def _redirect_within_run_dir(target: str, run_dir: str) -> bool:
    """True only when a redirection target is a path inside the run/eval dir.

    Guards against traversal (`{eval_dir}/../../etc/passwd`) and sibling-prefix
    bypasses (`out_secret` against run_dir `out`) that a bare startswith misses.
    """

    if ".." in target.split("/"):
        return False
    if target.startswith("{eval_dir}/") or target == "{eval_dir}":
        return True
    if not run_dir:
        return False
    return target == run_dir or target.startswith(run_dir.rstrip("/") + "/")


def validate_objective(objective: dict[str, Any]) -> list[str]:
    """Validate an objective mapping. Returns human-readable errors ([] == valid)."""

    validator = Draft202012Validator(_load_schema())
    errors = [
        f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(objective), key=lambda e: list(e.path))
    ]

    run_dir = str(objective.get("run_dir", ""))
    allowed = objective.get("allowed_executables") or []
    if not isinstance(allowed, list):
        allowed = []

    def _preflight(label: str, command: str) -> list[str]:
        violations = command_preflight(command, run_dir=run_dir, allowed_executables=allowed)
        return [f"{label}: {v}" for v in violations]

    for field in ("eval_command", "preflight_eval_command"):
        command = objective.get(field)
        if isinstance(command, str):
            errors.extend(_preflight(field, command))

    acceptance_eval = objective.get("acceptance_eval")
    if isinstance(acceptance_eval, dict) and isinstance(acceptance_eval.get("eval_command"), str):
        errors.extend(_preflight("acceptance_eval.eval_command", acceptance_eval["eval_command"]))

    return errors
