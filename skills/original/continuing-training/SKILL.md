---
name: continuing-training
description: Start a fresh robot-policy training run or resume an existing one into the run's persistent train_dir with lerobot-train. Use when the metric is improving, when a fresh run is needed (round 1 or a deliberate restart), whenever a round's action set includes more training steps, or when changing hyperparameters (policy type, batch size, LR, steps).
metadata:
  lifecycle: validated
  safety: mutating
---

# Continue or extend training

## When to use

The metric is improving, or a fresh run is needed. This is the default "exploit"
skill after a PROGRESS verdict.

This skill also covers **hyperparameter changes** (formerly the separate
`tuning-hyperparameters` skill): re-run with a different `--policy.type`,
`--batch_size`, learning rate, or `--steps`. Read the LeRobot repo's
`AGENT_GUIDE.md` §6 (which policy) and §7 (steps↔epochs, batch/LR-schedule
guidance) — the repo's own priors — before guessing. A `--policy.type` switch
means abandoning the current run: a *fresh* invocation into a new
`<train_dir>` lineage, directed explicitly by the [round brief].

## Prerequisites

A [round brief] with an explicit fresh / resume / branch-from-champion
directive; a dataset repo id (fresh) or an existing
`<train_dir>/checkpoints/last` (resume).

## Do

The loop carries one persistent variable, `<train_dir>` — the directory holding
the run's accumulating checkpoints. Step 1a creates it at round 0; every later
round resumes **into the same one**. The controller's [round brief] tells you
which mode this round uses — **fresh or resume is never your call as a worker**.

```bash
# Fresh run. Only at round 0 (Step 1a), or when deliberately abandoning the run
# (e.g. switching --policy.type). Sets <train_dir>
# for later rounds. output_dir must not already exist.
uv run lerobot-train \
  --dataset.repo_id=<user/dataset> \
  --policy.type=<act|diffusion|smolvla|pi0|...> \
  --output_dir=<train_dir> \
  --job_name=<name> --steps=<N> --batch_size=<B> \
  --policy.device=cuda --save_freq=<N/4>

# Continue. The normal path on rounds 1+.
# --steps MUST exceed the checkpoint's total or this trains nothing.
uv run lerobot-train \
  --config_path=<train_dir>/checkpoints/last/pretrained_model/train_config.json \
  --resume=true \
  --steps=<strictly greater than before>
```

Before **every** resume, write
`[run_dir]/round_<n>/evidence/resume_preflight.json` and do not launch training
until it passes. Run the check with the same interpreter and LeRobot checkout as
the train command:

1. Load the saved `train_config.json` through
   `TrainPipelineConfig.from_pretrained(config_path, cli_args=<the exact resume
   overrides>)`; never hand-merge JSON. Record the config sha256 and exact
   overrides.
2. Read the resolved step checkpoint's
   `training_state/training_step.json`, `scheduler_state.json`, and optimizer
   parameter-group state. Print and record: optimizer type/base LR, scheduler
   type, configured and effective warmup/decay horizon, current step, requested
   final step, loaded LR, and expected first post-resume LR.
3. Compute the expectation with the installed scheduler's own implementation.
   For `cosine_decay_with_warmup`, use its `actual_warmup_steps` /
   `actual_decay_steps` scaling and exact lambda at the saved/next step. A
   different scheduler requires a type-specific calculator; abort rather than
   guess.
4. Assert that optimizer/scheduler types resolve, requested steps are greater
   than current step, the intended horizon is beyond the current step when
   continued learning is expected, and the expected LR is not unintentionally
   the decay floor. Bind the evidence digest to the attempt's wait generation,
   execution lease, command digest, and `TRAIN_COMPLETE` transition.

Make the first LR-bearing runtime log early (`--log_freq<=100` unless the
round brief requires a stricter value). Read that log entry's actual step and
recompute the expected LR at **that step** with the preflight's effective
scheduler; never compare a step-100 observation with a saved/next-step
prediction. Compare numerically using a documented tolerance (default
`max(1e-12, 1e-3 * abs(expected_lr_at_logged_step))`). On a missing step, a
mismatch, a non-finite LR, or an unexpected floor value, terminate the
attempt's recorded process group, write the non-zero result envelope, leave
`TRAIN_COMPLETE` unset, and fix the effective top-level config before retrying.

## Mutates

`<train_dir>/checkpoints/` — new step dirs appear and the `last` symlink moves
on every save.

## Validation

A step checkpoint dir beyond the previous highest exists and `last` points at
it; the training log shows steps actually ran (a resume with non-greater
`--steps` exits 0 having trained nothing). On every resume, the durable
`resume_preflight.json` passes and the first runtime `lr:` matches its numeric
expectation. A single unchanging floor value (~2.5e-6) means the scheduler
clamp trap (Watch out) is burning the segment.

## Rollback

`skills/iterated/reverting-to-champion/SKILL.md` — repoint `last` at the champion
recorded in the run's durable `score_state` (mirrored in the derived
`[run_dir]/CHAMPION` pointer).

## Watch out

Every simultaneous hyperparameter change bundled into a round costs
attribution — the round's [delta] then reflects the whole [action set], not
one knob. When the round's purpose is to learn *which* change helped, change
one thing; whatever you bundle, name it in the ledger so a later round reads
the [delta] correctly.

**Do NOT judge a re-warmed fine-tune by a mid-training checkpoint.** A champion that finished
its cosine schedule sits at an ANNEALED minimum (e.g. lr 2.5e-06). Any new run that warm-starts
from it and re-warms the LR (a fresh optimizer, or a reopened decay horizon) is knocked out of
that minimum and is TRANSIENTLY WORSE while its LR is high — it has to re-converge. Measured:
two independent arms warm-started from a 49.0 champion scored 47.0 (at 5k/20k steps, lr 1.3e-05)
and 45.0 (at 10k/25k steps, lr ~2e-05) — both BELOW the champion, both still mid-anneal. Judging
either as a failure and killing it would have been wrong. Compare only ANNEALED-to-ANNEALED, i.e.
the end-of-schedule checkpoint. (Early reads are still worth taking — just read them as
"is it diverging?", never as "is it better?".)

- **A resume reverts inference-only config edits.** `train_config.json` — not `pretrained_model/config.json` — is the source of truth on resume. Any `n_action_steps` change made by `tuning-action-horizon` is discarded and the OLD value is stamped into every new checkpoint. Re-assert it on the resume command line (`--policy.n_action_steps=<value>`) and assert it in `resume_preflight.json`.

Re-running the *fresh* command each round throws away every prior checkpoint
while still looking like a well-logged "continue training" round. On rounds 1+
use the resume command unless the [round brief] explicitly directs a restart —
and if it does, say so in `Changed:`. Resuming without raising `--steps` past
the checkpoint's total trains **nothing** and exits 0, which looks exactly like
a no-progress round. `lerobot-train` won't overwrite an existing `output_dir`
unless `--resume=true`.

lerobot's `cosine_decay_with_warmup` scheduler **auto-scales** warmup and decay
to the run's `--steps` whenever `steps < scheduler_decay_steps`
(`src/lerobot/optim/schedulers.py` `build()`): a short run ends with `lr:` at
the ~2.5e-6 floor even though the config says a much larger decay horizon. That
end-of-log LR is *stale*, not the resume-D2 bug — on resume with a larger
`--steps` the lambda rebuilds and LR jumps back up (each extension replays a
fresh partial cosine). The real health check is the `lr:` value a few hundred
steps *after* the resume, not the last line of the previous segment.

The same scheduler **clamps** at its horizon: once the checkpoint's step count
has reached `num_decay_steps`, any further resume runs the WHOLE extension at
the `decay_lr` floor (`step = min(current_step, actual_decay_steps)`) — it
trains almost nothing while logging normally. Re-opening it on resume requires
overriding the **top-level** scheduler field: `--scheduler.num_decay_steps=<larger>`.
`--policy.scheduler_decay_steps` is a NO-OP on resume — `TrainPipelineConfig.validate()`
(`src/lerobot/configs/train.py:249-253`) rebuilds the scheduler from the policy
preset only when `not resume`, so the saved top-level `scheduler` section wins
(confirmed round 2, libero_smolvla_001: policy field showed 80000 while the
live scheduler kept 40000 and LR sat at the floor). Pass both flags to keep the
saved config sections consistent. Guard every extension resume with an LR check
a few hundred steps in; kill and fix rather than burn a floored segment.

## Evidence
- Round 1 (smolvla_libero10_80_002, 2026-07-14): resume 60k->75k, batch 8->32, schedule re-opened via top-level
  `--scheduler.num_decay_steps=75000`, horizon re-asserted via `--policy.n_action_steps=10`. 14h17m at 3.43 s/step.
  35.0 -> 48.0 (+13.0). The resume preflight caught BOTH traps before launch; the early-LR gate then confirmed
  lr=1.2e-05 at step 60000 against a predicted 1.181e-05 (the 2.5e-6 floor would have meant a wasted 14h).

- Origin: OPTIONS.md O1 (seed option); not yet exercised in a logged round.
- Round 0 (libero_smolvla_001, 2026-07-10): fresh mode validated — 2000/2000
  steps, exactly one checkpoint (`save_freq == steps`), `last` symlink correct;
  auto-scaling-scheduler trap observed and documented above.
- Rounds 0-1 (smolvla_libero_70_001, 2026-07-11): fresh 4k preflight + resume
  4k→40k behaved as documented (greater --steps trained; config carried; last
  advanced; LR decayed 1e-4→2.5e-6 across the 40k cosine). Resume 40k→60k hit
  the **clamp trap** above: `--policy.scheduler_decay_steps=60000` was a no-op,
  the saved scheduler kept `num_decay_steps=40000`, and the entire 20k extension
  ran at the 2.5e-6 floor (a single `lr:` value in the whole segment log; loss
  flat ~0.39) — its eval delta 53.0→64.0 stayed inside the noise band. Use
  `--scheduler.num_decay_steps=<larger>` as documented in Watch out.
