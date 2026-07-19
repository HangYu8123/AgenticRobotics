---
name: rebalancing-stage-2
description: Clones every multi-stage demo from its first "place" event onward, so the post-place state gets extra sampling weight. Use when the policy reliably completes sub-goal 1 and then fails to start sub-goal 2 — the classic long-horizon sequencing failure.
metadata:
  lifecycle: validated
  safety: reversible
---

# Rebalance the training data toward stage 2

## Prerequisites
A diagnosed SEQUENCING failure: the policy completes the first sub-goal, then dithers or never
re-targets. Confirm it first with `diagnosing-qualitatively` — and rule out the impostors:
wrong-object selection (a grounding failure) and a frozen/stalled arm (measure motion energy;
"failures run the full step budget" is TAUTOLOGICAL, not evidence).

## Do
1. **Find each demo's first place event** from the gripper channel, not from vision.
   In LIBERO, `action[6]` is the gripper (exactly +-1; verify the sign convention by correlating
   the command against the finger width `state[6]-state[7]`, lagged a few frames). The first place
   = the end of the first sustained CLOSED run, provided (a) the gripper actually opens later,
   (b) enough tail remains, and (c) it is not a re-grasp — reject if the next grasp begins soon
   after AND the end-effector barely moved (measured separation: re-grasps travel <0.15 m,
   genuine place->transit travels >=0.2 m).
2. **Emit a clone episode per demo that STARTS at that index** and runs to the end. Append the
   clones after the originals; rewrite `index`/`frame_index`/`timestamp`/`episode_index`.
3. Train from the champion on original + clones (fresh optimizer, `--policy.path`).

## Mutates
Writes a NEW dataset directory. The source dataset and the champion are untouched.

## Validation
**Prove the frame remap before you spend a GPU-hour on it.** Load the new dataset with
`LeRobotDataset` and assert: clone frame 0 is pixel-IDENTICAL to source frame `place_index`,
and pixel-UNEQUAL to source frame 0. Also check the episode count, `len(dataset)`, and that the
task string survives on the clones.

## Watch out
- **Check whether the dataset even has videos.** `HuggingFaceVLA/libero` stores images as HF
  `Image` structs embedded in the parquet rows (`dtype: "image"`, no `videos/` dir), so a clone is
  a literal ROW COPY — no re-encoding. If your dataset IS video-backed, a mid-episode clone needs
  frame-range remapping and is far more expensive. Check `meta/info.json` first.
- `meta/stats.json` is loaded VERBATIM (`dataset_metadata.py:184`), not recomputed from the
  episode subset — byte-copy it so a resumed champion sees an identical normalizer.
- Demos that never release (the arm ends still gripping) have NO place event. Skip them; do not
  fabricate a boundary. 41 of 379 libero_10 demos are like this (the "book into the caddy" task).
- The reweighting is only ~2x, not 10x: post-place frames were ALREADY ~47% of the data. It still
  worked, but calibrate your expectations.
- Judge it ANNEALED (see `continuing-training`): this run read 45.0 mid-training and 55.0 annealed.

## Rollback
Delete the augmented dataset dir; retrain from the champion.
- Whole-episode targeted oversampling of weak tasks from a CONVERGED checkpoint is a measured dead end at 2.4x: run smolvla_libero10_70_002 round 1 (2026-07-15) trained 25k fresh-optimizer steps on 4-task 2.4x clones from a 55.0 champion -> 46.0 (-9.0, REGRESSION beyond min_delta 8.0): strong-task catastrophic forgetting (9/10 -> 2/10) with NO weak-task gain (freeze mode persisted, one weak task fell 4->1). Dose matters; prefer gentler reweighting or intermediate-checkpoint early stops.

## Evidence
- round 4 (smolvla_libero10_80_001): the diagnosis was that 38/51 failures (75%) placed object 1
  and never completed object 2. Built a 717-episode augmented set (379 originals + 338 stage-2
  clones; post-place frames 47.5% -> 64.4% of draws), trained 25k steps from the 49.0 champion,
  **expert-only so the DATA was the only variable**. Scored **55.0 (+6.0) — PROGRESS**, and the new
  champion. It beat round 3's VLM unfreeze (pooled 48.0) while training FEWER parameters: the DATA
  fix beat the CAPACITY fix. The candidate is also far more self-consistent than the champion it
  replaced (4/100 vs 25/100 episodes flipping between identical re-runs).
  HONEST CAVEAT: a paired McNemar at n=200 puts p=0.27, so the +5.5pp pooled gain is NOT
  statistically significant; the promotion follows the objective's operator-set min_delta of 5.0.
- round 1, run _70_002 (2026-07-15): 2.4x whole-episode weak-task variant, delta -9.0, verdict REGRESSION (see Watch out).
