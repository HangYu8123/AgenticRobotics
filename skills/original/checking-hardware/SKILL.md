---
name: checking-hardware
description: Calibrate the robot and check cameras and ports — the hardware, not the model. Use when a real-robot policy degraded with no software change, or eval results are erratic between identical rounds.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Check the hardware, not the model

## When to use

A real-robot policy degraded with no software change, or eval results are
erratic between identical rounds.

## Prerequisites

Physical access to the robot/cameras/ports, and a symptom that points at
hardware. Save a copy of the current calibration file before recalibrating.

## Do

```bash
uv run lerobot-calibrate --robot.type=<T> --robot.port=<PORT> --robot.id=<ID>
uv run lerobot-find-cameras
uv run lerobot-find-port
```

## Mutates

The robot's calibration files (`lerobot-calibrate`); the finder commands mutate
nothing.

## Validation

Re-read the calibration and run a short reference move (or a small eval) to
confirm the recalibration took.

## Rollback

Restore the saved pre-calibration file.

## Watch out

A camera that moved silently invalidates every earlier metric in this run. Say
so in the ledger; do not compare across the change.

## Evidence

- Origin: OPTIONS.md O10 (seed option); not yet exercised in a logged round.
