---
name: rebasing-on-a-stronger-checkpoint
description: Evaluates a published checkpoint of the same policy class under the objective's own gate and adopts it as the training lineage's base if it beats the champion. Use when the run's lineage was warm-started from a checkpoint that was never trained for THIS eval suite, and a purpose-trained public checkpoint of the same policy exists.
metadata:
  lifecycle: candidate
  safety: reversible
---

# Rebase the lineage on a stronger public checkpoint

## Prerequisites
A scored champion, and a public checkpoint of the **same policy class** plausibly trained for
this eval suite. Cheap only because one eval (~1 GPU-h) can be worth more than a
multi-hour training round: check this BEFORE committing GPU to exploiting the current base.

## Do
1. Diff the architecture before believing anything — two checkpoints of the "same" policy
   are often not the same model:
   `hf_hub_download(repo, 'config.json')` and compare against the champion's `config.json`
   (for SmolVLA: `num_vlm_layers` — **0 means ALL layers, not none**; `expert_width_multiplier`;
   `vlm_model_name`).
2. Download it INTO the run dir, outside the train lineage:
   `<run_dir>/candidates/<name>/pretrained_model`. Do not promote it into
   `train/checkpoints/` until it has actually won the gate.
3. Port the champion's proven inference config onto the candidate (e.g. `n_action_steps`) —
   a published checkpoint often ships an untuned default (`n_action_steps: 1`).
4. Measure it with `measuring-the-gate` — the objective's [eval_command] VERBATIM,
   `{checkpoint}` = the candidate path.
5. Only if it beats the champion by more than the [noise band] / [min_delta], make it the
   new [best checkpoint] and initialize the next training round from it.

## Mutates
Nothing in the training lineage. Writes only `<run_dir>/candidates/` and a fresh eval dir.

## Validation
The measured metric, parsed from `eval_info.json` by the controller. A third party's
number (paper, GitHub issue, model card) is **never** the metric — it is only the reason to spend the eval.

## Rollback
Delete `<run_dir>/candidates/<name>/`. The champion and `train/` are untouched by construction.

## Watch out
- **A "reproduction" number in an issue is a hypothesis, not a measurement.** Budget the eval, then decide.
- The candidate may be a bigger model than your champion (full backbone vs a truncated one):
  eval wall-clock scales with it. Re-estimate the [time budget] from the arch diff, don't reuse
  the champion's eval duration.
- Do NOT skip step 3. Measuring a public checkpoint at its shipped `n_action_steps` can
  understate it badly (this loop measured +21 pp from 50→10 on another suite).

## Evidence
- round 1 (smolvla_libero10_80_001): **REBASE REJECTED, and the skill still paid for itself.**
  A GitHub issue reported the official `HuggingFaceVLA/smolvla_libero` (full 32-layer backbone,
  LIBERO-trained) at libero_10 = 56.0 vs our 39.0 champion (16-layer truncation, libero_object
  specialist). Measured under our own verbatim gate: **35.0** (n=100, seed 100000) — the published
  number did NOT reproduce, and the candidate is WORSE than the champion. Cost 1.2 GPU-h; it
  prevented an 11-hour training round from being launched on a weaker base. Verdict NO PROGRESS,
  champion unchanged. **The lesson is the skill: measure the claim, never adopt it.**
