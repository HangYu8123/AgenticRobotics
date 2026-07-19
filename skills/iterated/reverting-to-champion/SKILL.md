---
name: reverting-to-champion
description: Restore the training lineage to the champion checkpoint recorded in the run's durable score_state (mirrored in the derived CHAMPION pointer file) by repointing the checkpoints/last symlink, so the next round branches from the best measured policy instead of a damaged last. Use after a confirmed REGRESSION verdict (beyond the noise band), or whenever last is suspected damaged.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Revert training to the champion checkpoint

## When to use

A confirmed REGRESSION verdict (a [delta] beyond the [noise band]), or `last`
is suspected damaged — never on a within-noise dip.

## Prerequisites

The [round brief] carries the champion (checkpoint path, metric, round) from the
run's **canonical** durable `score_state` / applied [score snapshot] in
`[run_dir]/ROUND_IN_PROGRESS.md` — that is the authority. `[run_dir]/CHAMPION`
is its derived 3-line mirror (regenerated on every promotion and at recovery);
use it only to cross-check, and if it is missing or disagrees, report that back —
the controller regenerates it from durable state (flow recovery rule). The
champion path must name a step checkpoint dir still on disk;
`<train_dir>/checkpoints/last` is a symlink.

## Do

```bash
# 1. Take the champion from the [round brief] (canonical, from score_state).
#    Cross-check against the derived pointer file when present
#    (line 1 = path, line 2 = metric, line 3 = round); on mismatch, stop and
#    report — do not guess which is right.
head -n3 <run_dir>/CHAMPION

# 2. Confirm the layout before touching it: `last` must be a symlink, and the
#    champion step dir must exist and contain pretrained_model/.
ls -l <train_dir>/checkpoints/

# 3. Quarantine every step dir NEWER than the champion — they are the damaged
#    lineage, and lerobot's save_checkpoint re-creates step dirs with
#    exist_ok=True, silently overwriting them when training passes those steps
#    again.
mkdir -p <train_dir>/checkpoints_quarantine/round_<n>
mv <train_dir>/checkpoints/<each step dir newer than champion> \
   <train_dir>/checkpoints_quarantine/round_<n>/

# 4. Repoint `last` exactly the way lerobot's update_last_checkpoint() builds
#    it — a RELATIVE symlink to the step dir name.
ln -sfn <champion_step_name> <train_dir>/checkpoints/last

# 5. Validate the revert: run the objective's eval_command verbatim against
#    {checkpoint} into a fresh eval dir. The metric must match the champion's
#    recorded metric (score_state metric_best) within the [noise band] — only
#    then is the revert trusted and the next round allowed to resume training
#    from it.
```

## Mutates

`<train_dir>/checkpoints/` only (the `last` symlink target; quarantined step
dirs). Never writes `[run_dir]/CHAMPION` or `score_state` itself — only the
controller's promotion/recovery regeneration (flow Step 3g) does that.

## Validation

Step 5 above: a fresh eval of the repointed checkpoint reproduces the champion's
recorded metric within the [noise band]. Report the eval's exit status and the
eval_info.json path back; the controller parses the number itself (Invariant 3).

## Rollback

The quarantine dir is the rollback: move the step dirs back into
`<train_dir>/checkpoints/` and repoint `last` at the newest one.

## Watch out

- lerobot resume reads the step counter, optimizer, and scheduler state from
  *inside* the step dir (`training_state/`), so repointing `last` rewinds all of
  them together — but the next resume's `--steps` must exceed the **champion's**
  step count, not the damaged lineage's higher one, or it trains nothing and
  exits 0 (`skills/original/continuing-training/SKILL.md`).
- Resume needs
  `--config_path=<train_dir>/checkpoints/last/pretrained_model/train_config.json`
  — the file, not the directory.
- `train_config.json` does not carry the W&B run id; re-pass it on resume or the
  logging forks into a new run.

## Evidence

- Created offline (2026-07-10 design revision) from lerobot source:
  `train_utils.update_last_checkpoint()` builds `last` as a relative symlink and
  `load_training_state()` reads the step from inside the target dir, so the
  repoint is library-consistent. Not yet exercised in a logged round.
