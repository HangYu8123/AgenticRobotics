---
name: unfreezing-the-vlm
description: Makes a VLA's frozen vision-language backbone trainable (train_expert_only=false) instead of training only the action expert. Use ONLY when the diagnosed failure is genuinely a perception/grounding deficit — it did NOT help a sequencing failure, and it is not a general-purpose "add capacity" lever.
metadata:
  lifecycle: deprecated
  safety: reversible
---

# Unfreeze the VLM (measured: did NOT help)

**Deprecated:** measured on LIBERO-10 and it bought nothing (pooled delta -1.0). Kept so no
future round re-buys it. Reach for it only with direct evidence of a grounding/perception failure.

## Prerequisites
A VLA whose backbone is frozen. In SmolVLA, `train_expert_only=True` sets `requires_grad=False`
on EVERY VLM parameter and pins it to `.eval()` (`smolvlm_with_expert.py:155-158`) — only the
action expert trains.

## Do
You must start a **fresh optimizer** — `--resume` restores an optimizer state_dict built for the
old (expert-only) trainable set and will mismatch (`common/train_utils.py:201`). So:
`--policy.path=<champion> --policy.train_expert_only=false --output_dir=<NEW dir>`, and **lower
the LR** (2e-5, not the expert's 1e-4).

**LR FLAG TRAP:** on a FRESH run, `--optimizer.lr` and `--scheduler.peak_lr` are **silently
discarded** — `train.py:251` rebuilds both sections from the policy preset when
`use_policy_training_preset=True` (default) and not resuming. Use `--policy.optimizer_lr`,
`--policy.scheduler_warmup_steps`, `--policy.scheduler_decay_steps`. (This is the INVERSE of the
resume-time trap, where `--scheduler.num_decay_steps` is the one that works.) Verify the live
value in the log's config dump.

## Validation
The trainable-param count must jump (SmolVLA: 100M -> 316M with the vision tower still frozen;
450M total). If it does not, the flag did not take and you are about to burn hours on a no-op.

## Mutates
A new training lineage. The champion is untouched.

## Evidence
- round 3 (smolvla_libero10_80_001): trainable 100M -> 316M, 20k steps @ lr 2e-5 from a 49.0
  champion, annealed. Scored **52.0**, confirmation on the SAME checkpoint scored **44.0**,
  **pooled (n=200) = 48.0 vs the champion's 49.0 => delta -1.0. NO PROGRESS.** Training loss DID
  fall below the champion's (0.327 vs 0.34) — it fits the demos better without succeeding more.
  The round's premise (a language-grounding bottleneck) had already been REFUTED by video analysis
  before it finished: 0/51 failures were wrong-object selection. **Capacity was not the constraint.**
