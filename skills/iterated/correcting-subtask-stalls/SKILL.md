---
name: correcting-subtask-stalls
description: Test-time interventions for the measured long-horizon sequencing failure — the policy completes subtask 1, then dithers and never starts subtask 2. Use when qualitative diagnosis shows completed-first-stage stalls dominating eval failures and the training-side lever (stage-2 rebalance) has been exploited.
metadata:
  lifecycle: candidate   # candidate | validated | deprecated
  safety: reversible     # inference/config-side only; champion weights and datasets untouched
---

# Correct sequencing stalls at inference time

## Prerequisites
A champion checkpoint with a diagnosed sequencing-stall failure mode (e.g. run smolvla_libero10_80_001 round 4: 38/51 failures place object 1 and never advance to object 2; 0/51 wrong-object). `writing-new-scripts` for anything beyond a config edit.

## Do
Pick ONE per round (isolate for attribution), cheapest first:
1. **Chunk-staleness reduction.** A chunked policy replans only every n_action_steps; a stale open-loop chunk can carry the arm past the "object 1 placed" boundary with no reaction. Probe alternative `n_action_steps` values via `tuning-action-horizon` (config-only), or add a per-step chunk-correction module per "Leave No Observation Behind" / A2C2 (arXiv:2509.23224 — plug-in, no retraining of the base policy).
2. **Subtask-boundary replan/backtrack trigger.** CycleVLA (arXiv:2601.02295): detect stalled progress at a subtask transition (VLM failure predictor, or a cheap heuristic — gripper idle + no EE displacement for N steps after a place event) and force a re-plan/backtrack. Implement as an eval-time wrapper via `writing-new-scripts`.
3. **Modality-rebalance retraining** (training-class, last resort). ReViP (arXiv:2601.16667): "false completion" from state-dominant bias — progress-aware visual cues rebalance vision vs proprioception coupling. Requires retraining; reported gains on LIBERO suites with a π0 backbone.

## Mutates
Nothing by itself; option 1 edits a checkpoint COPY's config.json (back it up first), options 2–3 create new scripts/checkpoints.

## Validation
Scored only by the objective's eval_command through the flow's Measure step; qualitative cross-check = the stalled-episode count in eval videos falls.

## Rollback
Restore config.json from backup / discard wrapper scripts; the champion lineage is never touched.

## Watch out
- LOCAL EVIDENCE FIRST: n_action_steps 10→5 measured REGRESSION (−5.0) on this lineage (run _80_002 round 2), while lerobot issue #2354 reports 0.43→0.51 on libero_10 from an eval-config change on the base SmolVLA checkpoint. Horizon effects are checkpoint-dependent — measure, never assume.
- The objective's eval_command is immutable (Invariant 1): an inference-time wrapper produces a SCORED metric only if the operator amends the objective; until then use it as unscored diagnosis/evidence.

## Evidence
- (registered 2026-07-15 from external research with citations fetched and title/claim-verified the same day: arXiv:2509.23224, arXiv:2601.02295, arXiv:2601.16667, huggingface/lerobot#2354. No logged round has exercised it yet.)
