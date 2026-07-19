---
name: diagnosing-qualitatively
description: Watch the policy act — rollouts, dataset replays, and the eval's rendered videos — to see how it fails, not just that it fails. Use when the metric regressed or is flat and no one can say why; the finding, not a metric change, is the round's output.
metadata:
  lifecycle: validated
  safety: reversible
---

# Diagnose qualitatively

## When to use

The metric regressed, or it is flat and you cannot say why. Numbers say *that*
it failed; video says *how*.

## Prerequisites

A checkpoint to roll out, and/or the `<eval_dir>/videos/` of the round being
diagnosed.

## Do

```bash
uv run lerobot-rollout --policy.path=<checkpoint> ...   # watch the policy act
uv run lerobot-replay --dataset.repo_id=<user/dataset> --dataset.episode=<i>
```

Also read the eval's rendered videos under `<eval_dir>/videos/`. As a worker,
return the *finding* (what the failures look like, where they cluster) in your
[worker result] — that is what the controller needs for the next Decide step.

## Mutates

Nothing.

## Validation

The finding names concrete episodes/timestamps another worker could re-open —
not an impression.

## Rollback

None — reversible.

## Watch out

**"Every failure burns the full step budget" is TAUTOLOGICAL, not evidence.** The env
terminates on success, so *by construction* every failure runs to `max_steps` and every success
is shorter. An observed diagnosis built its whole "the policy freezes after the first sub-goal"
story on this, and video motion-energy traces then REFUTED it: the arm was still moving at
t=518. Measure a quiet-tail / motion-energy fraction if you want to claim a freeze. Likewise,
LIBERO's reward is the success bit itself (`sum_rewards == max_rewards` in {0,1}) — it carries
zero partial credit and can never tell you which sub-goal was reached.

**Hold the scene constant before blaming task structure.** Two LIBERO-10 tasks can share a
scene, object set and grasp count and differ only in which objects the instruction NAMES —
scoring 0/10 and 6/10. That is a language-grounding failure, and no amount of horizon, memory
or extra training on the same demos addresses it.

This skill changes nothing, so it produces `delta = 0` by construction. Log it
as `NO PROGRESS` on the metric but record the *finding* in `Changed:` — that
finding is the round's actual output.

## Evidence

- Origin: OPTIONS.md O6 (seed option); not yet exercised in a logged round.
- Round 3 (libero_smolvla_001, 2026-07-11): validated — 13 failure + 1 success videos frame-analyzed; found the systematic single-miss-then-open-loop-place mode (no retry) that redirected the loop from more-training to inference-time chunking; delta 0 by construction.
