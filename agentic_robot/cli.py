"""agentic-robot — deterministic control-plane CLI.

Verbs are read-only or scaffolding only. This tool does NOT run the training loop
(that is the LLM controller's job — see robot_agentic_training_flow.md and
README.md). It gives an operator deterministic checks the loop's correctness rests
on: objective validation, run status, recovery replay, and an event-ledger view.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__, ledger
from . import objective as objective_mod
from . import state as state_mod

_REPO_ROOT = Path(__file__).resolve().parents[1]
_OBJECTIVE_TEMPLATE = _REPO_ROOT / "objective.example.yaml"


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        obj = objective_mod.load_objective(args.objective)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors = objective_mod.validate_objective(obj)
    if errors:
        print(f"INVALID — {len(errors)} problem(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    digest = objective_mod.objective_digest(Path(args.objective).read_text(encoding="utf-8"))
    print(f"OK — objective is valid. sha256={digest}")
    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    dest = Path(args.objective)
    if dest.exists():
        print(f"error: {dest} already exists — refusing to overwrite", file=sys.stderr)
        return 1
    if not _OBJECTIVE_TEMPLATE.exists():
        print(f"error: template {_OBJECTIVE_TEMPLATE} not found", file=sys.stderr)
        return 2
    shutil.copyfile(_OBJECTIVE_TEMPLATE, dest)
    print(f"wrote {dest} — fill it in, then run: agentic-robot validate {dest}")
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    log = run_dir / "LOOP_LOG.md"
    if not log.exists():
        print(f"no LOOP_LOG.md under {run_dir} (has the run started?)")
        return 1
    text = log.read_text(encoding="utf-8")
    rounds = text.count("<!-- ROUND_ENTRY_BEGIN")
    print(f"run_dir: {run_dir}")
    print(f"logged rounds: {rounds}")
    cont = run_dir / "CONTINUATION.json"
    if cont.exists():
        data = json.loads(cont.read_text(encoding="utf-8"))
        print(f"status: {data.get('status', '?')}  round: {data.get('current_round', '?')}")
        if data.get("pending_action"):
            print(f"pending_action: {data['pending_action']}")
    return 0


def _cmd_replay(args: argparse.Namespace) -> int:
    try:
        from recovery.replay_checker import check_replay
    except ImportError as exc:
        print(f"error: recovery.replay_checker unavailable: {exc}", file=sys.stderr)
        return 2
    snapshots = state_mod.load_snapshots(args.run_dir)
    if not snapshots:
        print(
            f"no {state_mod.SNAPSHOTS_FILENAME} under {args.run_dir} — nothing to replay "
            "(the flow stores ROUND_IN_PROGRESS.md; export decoded snapshots to replay them)"
        )
        return 1
    try:
        check_replay(snapshots)
    except ValueError as exc:
        print(f"REPLAY VIOLATION: {exc}")
        return 1
    print(f"OK — {len(snapshots)} snapshot(s) replay consistently.")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    events = ledger.read_events(Path(args.run_dir) / ledger.EVENTS_FILENAME)
    if not events:
        print(f"no {ledger.EVENTS_FILENAME} under {args.run_dir}")
        return 1
    print(ledger.render_events_markdown(events))
    return 0


def _cmd_resume(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    cont = run_dir / "CONTINUATION.json"
    if cont.exists():
        data = json.loads(cont.read_text(encoding="utf-8"))
        print(f"run_id: {data.get('run_id', '?')}")
        print(f"status: {data.get('status', '?')}  round: {data.get('current_round', '?')}")
        print(f"pending_action: {data.get('pending_action', '(none)')}")
        if data.get("reentry_prompt"):
            print(f"reentry_prompt: {data['reentry_prompt']}")
    else:
        print(f"no CONTINUATION.json under {run_dir} — cannot describe a resume point")
    # Validate durable state if a decoded snapshot export exists.
    snapshots = state_mod.load_snapshots(run_dir)
    if snapshots:
        try:
            from recovery.replay_checker import check_replay

            check_replay(snapshots)
            print(f"recovery: {len(snapshots)} snapshot(s) are consistent — safe to resume")
        except (ImportError, ValueError) as exc:
            print(f"recovery: WARNING — {exc}")
            return 1
    return 0 if cont.exists() else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentic-robot", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate an objective spec against objective.schema.json")
    p.add_argument("objective")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("init", help="scaffold a new objective from objective.example.yaml")
    p.add_argument("objective")
    p.set_defaults(func=_cmd_init)

    p = sub.add_parser("status", help="summarize a run's LOOP_LOG.md (read-only)")
    p.add_argument("run_dir")
    p.set_defaults(func=_cmd_status)

    p = sub.add_parser("replay", help="replay-check decoded state snapshots (read-only)")
    p.add_argument("run_dir")
    p.set_defaults(func=_cmd_replay)

    p = sub.add_parser("report", help="render the JSONL event ledger as markdown to stdout")
    p.add_argument("run_dir")
    p.set_defaults(func=_cmd_report)

    p = sub.add_parser("resume", help="describe a run's deterministic resume point (read-only)")
    p.add_argument("run_dir")
    p.set_defaults(func=_cmd_resume)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
