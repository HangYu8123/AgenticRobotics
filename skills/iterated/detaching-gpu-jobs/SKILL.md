---
name: detaching-gpu-jobs
description: Dispatch multi-hour GPU training/eval commands detached from harness task management so they survive task reaping, with an exit sentinel, an artifact watch, and a scheduled fallback wake for low-latency completion detection. Use when a command is expected to outlive a harness-tracked shell task (reaping observed at ~18-25 min) or when a prior long job died with its session.
metadata:
  lifecycle: candidate
  safety: reversible
---

# Detach long GPU jobs

> Re-registered offline 2026-07-15: the original round-0 registration (untracked)
> was deleted from the working tree the same day; this body was re-authored from
> the `context/` index snapshot, the pre-deletion scripts_overview row, and
> update_logs ID 3, plus the corrected completion-detection guidance from
> past_Q&A 2. Its pre-deletion Evidence lines are summarized, not reproduced.

## Prerequisites

An [execution lease] and [wait generation] already allocated for this dispatch
(flow Step 3(e)/(f)); the command text, a log path, and a sentinel path under
the run dir.

## Do

```bash
setsid bash -c '<env vars> <command> > <log> 2>&1; echo $? > <sentinel>.exit' &
```

Immediately record generation-owned identity into the durable record/lease per
the flow: pid, `ps`-read pgid, `/proc/<pid>/stat` starttime, sha256 of the
command text, log and sentinel paths, owning [wait generation].

Then arm BOTH wakes before any yield (`stay_active.md` Rule 2):

- **Event trigger:** a Monitor watch on the awaited artifact + the exit
  sentinel + `kill -0 $PID` liveness (60–120 s cadence). Never rely on a
  harness task-completion notification — attached background tasks get reaped,
  so for a detached job that notification will never come.
- **Time fallback:** a scheduled wake (cron/scheduled-wakeup mechanism), never
  a background `sleep` (also reaped). Scheduled prompts fire only between
  turns, and recurring ticks can land late (up to half the interval when
  sub-hourly): keep bounded heartbeat ticks running for the WHOLE wait
  (Rule 3), densify to 2–5 min as the ETA approaches, and keep controller
  turns short near the ETA. Do not place the first tick at the ETA — duration
  estimates in this domain miss by more than 2x (see `measuring-the-gate`,
  66-min estimate → 134-min reality).

## Mutates

Nothing beyond the launched command's own effects — the wrapper adds only the
log file and exit sentinel.

## Validation

`kill -0 $PID` succeeds while running; on completion the sentinel exists and
holds the exit code; artifact identity and completeness verify per the flow
before the wait is claimed.

## Rollback

Identity-verified `kill -- -PGID` from the controller — verify pid, pgid,
starttime, and command sha256 against the recorded identity first; never a
bare `kill $PID` (it orphans the process group).

## Watch out

- The [command preflight] validates the objective's **raw command text**; this
  wrapper is dispatch-side process placement and must embed that text
  verbatim, never edit it (the flow: process placement and harness mechanics
  never alter the objective's measurement semantics).
- Normalize logs with `tr '\r' '\n'` before line-based monitoring (tqdm
  rewrites lines with `\r`), and note step counts ≥1000 print abbreviated
  (e.g. "5K") — both defeat naive grep watchers.

## Evidence

- Exec ID 2/3 (LIBERO runs, 2026-07-11): attached shell tasks were reaped at
  ~18–25 min, killing training; detached dispatch survived ~10 h and ~5.5 h
  segments (summarized from the pre-deletion row; original per-round lines
  lost with the deleted file).
- 2026-07-15: deleted from the working tree undocumented (untracked — body
  unrecoverable from git); re-authored offline per the note above.
