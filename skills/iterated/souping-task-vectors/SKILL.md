---
name: souping-task-vectors
description: Interpolates a regressed-but-informative fine-tune back toward the champion (W = champ + alpha*(finetune - champ)) to keep its task gains while canceling its forgetting. Use when a training round REGRESSED overall but its per-task profile shows real gains buried under forgetting on other tasks.
metadata:
  lifecycle: candidate
  safety: reversible
---

# Soup the champion with a regressed fine-tune's task vector

## Prerequisites
Champion and fine-tune checkpoints with IDENTICAL state-dict keys/shapes (same architecture/config); per-task eval evidence showing the fine-tune gained somewhere.

## Do
`scripts/build_soup.py --base <champion pretrained_model> --other <finetune pretrained_model> --alpha 0.35 --out <new dir>` (float32 blend, cast back to stored dtype; copy config/processor files from base). Start at alpha ~0.35; the alpha-curve is nonlinear (forgetting cancels faster than gains shrink).

## Mutates
Nothing — writes a NEW checkpoint dir; both sources untouched.

## Validation
Key sets identical; spot-check max|soup - blend| < 1e-6; policy loads from the new dir; then measure through the objective's own gate.

## Rollback
Delete the soup dir; champion was never touched.

## Watch out
- Linear reasoning says a net-negative vector can't help at any alpha — the whole bet is the NONLINEARITY (forgetting cancels super-linearly). Measure, don't assume.
- Alpha too high re-imports the forgetting; too low dilutes the gains. One eval per alpha point — budget accordingly.

- VECTOR DIVERSITY IS THE INGREDIENT: a vector trained on the same data family as the champion's own ancestry (plain stage2 from a stage2-descended champion) measured DILUTIVE (-6.0 at alpha 0.5) — it re-walks known ground and drags the soup back toward the old optimum. Generate vectors from data the champion has NOT already absorbed (e.g. targeted boosts), and keep them redundant with the champion's own training ancestry at your peril.

## Evidence
- round 2, run _70_002 (2026-07-15): champ 55.0 + 0.35*(46.0-regression vector) -> 63.0 (+8.0, PROGRESS, promoted champion). Forgetting largely canceled (9/10->7/10 worst case) while weak/mid gains held or grew (4/10->8/10 on moka pots; 7/10->10/10).
- round 3, run _70_002 (2026-07-16): champ63 + 0.5*(plain-stage2 10k vector) -> 57.0 (-6.0, NO PROGRESS). Same-data vector = dilutive; see Watch out.
- round 4, run _70_002 (2026-07-16): recipe repeat (fresh boost{0,4,6,7} 25k vector from champ63, alpha 0.35) -> 53.0 (-10.0, REGRESSION). The mechanism is NOT reliably repeatable; the original +8.0 carried an informational McNemar p~0.25. Treat single-soup wins as provisional until re-measured.
