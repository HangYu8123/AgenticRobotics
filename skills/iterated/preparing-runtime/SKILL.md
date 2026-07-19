---
name: preparing-runtime
description: Runs dependency installs, model or dataset downloads, cache fills, and preprocessing noninteractively with resumable state, bounded output, growth checks, and durable completion evidence. Use before any setup operation that may be slow, noisy, or restarted.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Prepare runtime state safely

## Prerequisites

A [round brief] with the operation's wait generation, execution lease, evidence
directory, absolute deadline, expected artifacts, cache/staging path, and
task-specific command.

## Do

1. Record cwd, explicit interpreter path/version, package-manager version,
   command sha256, pinned revision/version, cache/staging path, preflight free
   space, cache bytes, and expected artifact size/count. Abort before mutation
   when the declared disk margin is unavailable.
2. Make the task-specific command noninteractive and quiet. Common controls are
   `HF_HUB_DISABLE_PROGRESS_BARS=1`, `UV_NO_PROGRESS=1`, and
   `PIP_NO_INPUT=1 PIP_PROGRESS_BAR=off`; always pass `uv pip --python
   <exact-python>`. Preserve tool caches and partial transfers, pin the remote
   revision, and use that tool's resume/cache-reuse mode rather than forcing a
   fresh download.
3. Redirect the full stream to an attempt-owned durable log with a persisted
   byte cap; expose only a bounded tail to the agent. At each heartbeat record
   log bytes, artifact/cache bytes, free space, and latest mtime. If the log
   reaches its cap, either rotate it with a predeclared bounded policy or
   terminate the verified process group immediately and record `LOG_CAP` as a
   non-zero terminal outcome—never keep writing past the cap. Declare a stall
   only when both artifact/cache bytes and mtimes remain unchanged for the
   operation's stated threshold; preserve valid partial data on retry.
4. On every terminal path, atomically write the generation/lease-bound result
   envelope under `[run_dir]/round_<n>/evidence/`: operation and attempt ids,
   command/config digests, cwd/interpreter/environment, PID/PGID/start identity,
   start/end, exit code or signal, log path/digest, before/after disk and cache
   sizes, growth samples, validated artifact paths/counts/digests, and status.
   A controller derives `*_COMPLETE` only after verifying this envelope and the
   real artifacts.

## Mutates

The explicitly named environment, cache/staging directory, and output
artifacts; the durable log and result envelope under the run directory.

## Validation

Exit code is zero, the result envelope matches the wait generation, lease,
command, and process identity, expected artifacts pass their task-specific
checks, free-space margin remains positive, and bounded-output/log caps held.

## Rollback

Remove only attempt-owned incomplete outputs after verifying ownership. Keep
package-manager caches and valid resumable partial transfers unless the
task-specific skill proves they are corrupt.

## Watch out

Progress suppression alone does not bound redirected logs or cache growth.
File existence alone is not completion. Expired leases, missing PIDs, and
worker messages never substitute for a durable exit code plus artifact checks.
Keep installer-specific prompts and build workarounds in task-specific skills.

## Evidence

- Offline generalization, 2026-07-13: distilled from repeated progress-spam,
  reaped-download, wrong-interpreter, silent-stall, and cache-growth failures;
  candidate until exercised in a logged round.
