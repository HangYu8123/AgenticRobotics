---
name: tuning-action-horizon
description: Shrinks a VLA checkpoint's inference action horizon (n_action_steps) for closed-loop control without retraining. Use when a chunked-action policy (chunk_size much greater than 1) underperforms in eval and a training round is expensive.
metadata:
  lifecycle: validated
  safety: reversible
---

# Shrink the inference action horizon

## Prerequisites
A chunked-action checkpoint whose *executed* horizon is smaller than its *predicted* chunk (room to shrink), and the objective's eval_command. Action chunking is a VLA-general design — ACT, Diffusion Policy, SmolVLA, pi0, and OpenVLA-OFT all predict a chunk and execute a prefix of it — so this lever exists on any of them under whatever name that backend gives the two numbers.

## Do
Backend-independent contract: the policy predicts `chunk_size` actions and executes the first `n_action_steps` of them before re-observing. Shrinking the executed prefix trades inference cost for closed-loop responsiveness, **without touching weights**. So: record the current value (find where the inference-time config actually lives — it is usually a single copy), lower it (e.g. 50→10, never above `chunk_size`), then re-run the objective's eval_command verbatim.

### Reference backend (LeRobot / SmolVLA)
Edit `<checkpoint>/pretrained_model/config.json`, field `n_action_steps`.

## Mutates
One inference-time config field — weights untouched. On the reference backend: `pretrained_model/config.json`'s `n_action_steps`.

## Validation
eval_info.json regenerates; the dumped eval config shows the new horizon.

## Rollback
Restore the previous value. Keep the backup **outside** the checkpoint dir (e.g. the round evidence dir).

## Watch out
Horizon-10 eval makes ~5x more policy calls (round-2 eval 22→30 min). **The edit does NOT ride along into a resume — it is silently REVERTED.** `pretrained_model/config.json` is read by *eval*; `pretrained_model/train_config.json` is read by `--resume=true`, and it still carries the ORIGINAL `n_action_steps`. LeRobot rebuilds the policy from train_config (`configs/train.py` resume branch -> `policies/factory.py`: the train_config-derived config wins over the saved config.json), and `save_checkpoint` then stamps that value into every NEW checkpoint's config.json. So a resume after this edit trains and saves at the OLD horizon, and the next eval silently loses the lever. **Every resume must re-assert it: `--policy.n_action_steps=<value>`** (verified to stick). With a fixed-seed deterministic eval, this cheap config probe is the right first lever, because only a >noise-band jump can score PROGRESS.

## Evidence
- **Round 2 (smolvla_libero10_80_002, 2026-07-14) — NEGATIVE RESULT, going below 10 HURTS.** Same weights
  (075000, libero_10-specialized), config-only 10 -> 5: **48.0 -> 43.0 pc_success (-5.0, n=100, fixed seed)** ->
  REGRESSION; reverted to 10. **7 of 10 tasks got worse.** So the lever is the 50->10 cut, not "smaller is better":
  it saturates at 10 and reverses below it. Plausible mechanism (SmolVLA has `n_obs_steps=1`, i.e. no memory of what
  it already did): re-deciding every 5 steps invites dithering between sub-goals instead of committing to one —
  worst on multi-stage tasks. Corollary: this lever cannot fix a **semantic** failure (grasping an object that
  appears in no instruction, or failing to re-target after finishing sub-task 1); it only fixes **staleness**
  (open-loop drift with no retry). Diagnose which one you have BEFORE spending an eval on it.
  Cost note: horizon 5 eval took 76 min vs 57 min at horizon 10 on libero_10.

- round 2 (smolvla_libero10_80_001), controlled A/B on libero_10 — IDENTICAL weights (ckpt
  070000), identical seed, identical 100 episodes, only the horizon changed:
  **n_action_steps=10 -> 44.0; n_action_steps=5 -> 33.0 (-11 pp).** Shorter is WORSE here.
  (Paired McNemar p=0.108, so not formally significant — but there is no hint of a gain, and
  39/100 episodes flipped outcome between the two arms, which is itself the finding: this eval
  is NOISY at n=100.) **The knob is closed at 10 for this policy/suite — do not re-buy this eval.**
  The +21 pp that 50->10 bought on libero_object was a one-time win, and it is already spent.
- Round 2 (smolvla_libero_70_001): pc_success 64.0→85.0 on identical seeds (delta +32 vs champion 53.0, band ±12.1), decisive win — cleared the run's 70% exit target in one 30-min round.
- Round 4 (libero_smolvla_001, 2026-07-11): independent replication, 50->10 on the
  80k SmolVLA checkpoint: 52.0 -> 88.0 (n=100 fixed seeds; +42.0 vs champion 46.0,
  band +-11.8; every libero_object task >=7/10) — eliminated the diagnosed
  single-miss-no-retry mode; produced that run's champion. Merged in from the
  duplicate `tuning-inference-chunking` (registered the same day, later deleted
  after its evidence was merged here).
  Extra practice folded in: keep the config backup OUTSIDE the checkpoint dir
  (e.g. round evidence dir); values below 10 are separate experiments — smaller
  is not monotonically better.
