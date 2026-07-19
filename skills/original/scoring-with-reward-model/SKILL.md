---
name: scoring-with-reward-model
description: Score recorded real-robot episodes with a reward model (robometer, topreward, sarm, or a trained reward_classifier) and emit the objective's metric as eval_info.json. Use when the objective targets real hardware, where there is no gym env, no env.step() reward, and therefore no lerobot-eval.
metadata:
  lifecycle: candidate
  safety: reversible
---

# Score a real robot with a reward model

## When to use

The objective targets **real hardware**, where there is no gym env, no
`env.step()` reward, and therefore no `lerobot-eval`.

## Prerequisites

Recorded episodes to score; a reward model chosen from
`src/lerobot/rewards/`; a wrapper script (via `writing-new-scripts`).

## Do

Use the LeRobot repo's `src/lerobot/rewards/` — `robometer`, `topreward`,
`sarm`, or a trained `reward_classifier`, selected via
`lerobot.rewards.factory.get_reward_model_class(name)` — to score recorded
episodes and emit the metric. Wrap it in a script (`writing-new-scripts`) whose
only contract is: **write `{eval_dir}/eval_info.json` containing the
objective's `metric_path`.**

## Mutates

Nothing — writes only `{eval_dir}/eval_info.json`.

## Validation

Spot-check the model's scores against the episodes' videos before trusting a
metric expressed in its units.

## Rollback

None — reversible.

## Watch out

A reward model is itself a model. It can be wrong, and a policy can learn to
satisfy it without doing the task. Spot-check its scores against the eval
videos before trusting a target expressed in its units.

## Evidence

- Origin: OPTIONS.md O11 (seed option); the intended answer to "the gate is env
  reward, but my robot is real" — not yet exercised in a logged round.
