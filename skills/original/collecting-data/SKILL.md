---
name: collecting-data
description: Record additional teleoperated episodes into the training dataset with lerobot-record. Use when the policy underfits the task, fails on states absent from the data, or the dataset is small — a strategy-class switch away from tuning.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Collect more data

## When to use

The policy underfits the task, fails on states absent from the data, or the
dataset is small (the LeRobot repo's `AGENT_GUIDE.md` §5.5: start small, then
extend).

## Prerequisites

The robot and teleoperator reachable (`--robot.port`/`--robot.id`); the
existing dataset's repo id (and its root, if non-default) for `--resume=true`.

## Do

```bash
uv run lerobot-record \
  --robot.type=so101_follower --robot.port=<PORT> --robot.id=<ID> \
  --dataset.repo_id=<user/dataset> --dataset.num_episodes=<K> --resume=true
```

## Mutates

The training dataset — appends K episodes.

## Validation

The dataset's `meta/info.json` episode count increased by exactly K.

## Rollback

Delete the newly-recorded episode indices with `lerobot-edit-dataset
--operation.type=delete_episodes` (see `curating-dataset`) — and re-baseline
either way, since the dataset changed.

## Watch out

When resuming a recording, `--dataset.num_episodes` is the number of
**additional** episodes, not the new total. `--dataset.root` is optional (it
defaults to `$HF_LEROBOT_HOME/<repo_id>`) but must be passed if the original
recording used a non-default root. Data collected under different lighting or
camera placement is a distribution shift, not extra data.

## Evidence

- Origin: OPTIONS.md O4 (seed option); not yet exercised in a logged round.
