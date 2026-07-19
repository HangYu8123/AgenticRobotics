# Skills Library — `robot_agentic_training_flow`

**This is a menu, not a fence.** Every skill below is something someone tried in a
previous round. You are free — encouraged — to do something nobody has listed.
When you do, create it as a new skill here (see *Creating a new skill*). That is
how this library grows.

> **Do not confuse this library with any orchestration pack's skills.** This
> directory (`skills/` at the repo root, sibling of `robot_agentic_training_flow.md`)
> is the flow's [skills library]. If an orchestration pack is installed under
> `.github/`, its own `skills/` directory is different tooling (code review,
> PR breakdown, …), not part of this library.

Skills follow the [Agent Skills](https://agentskills.io) open standard: one
directory per skill, `SKILL.md` with `name` (must equal the directory name) and
`description` frontmatter, body under 500 lines, bundled resources one level deep.
They are plain markdown — usable by any agent on any platform.

## How to use this library

The controller re-reads this index at the start of every round (flow Step 3b) and
picks based on last round's verdict:

| Last verdict | Reach for |
|---|---|
| PROGRESS | Exploit: `continuing-training` (more steps, or re-parameterized — policy type/batch/LR) |
| NO PROGRESS (below `stagnation_rounds`) | `tuning-action-horizon` (cheapest first — config-only), `continuing-training` (re-parameterized), `curating-dataset` |
| NO PROGRESS (at `stagnation_rounds`) | **Switch strategy class** — `diagnosing-qualitatively`, `collecting-data`, `researching-online`. An action-selection interrupt, never a termination condition (flow Invariant 2) |
| REGRESSION | `diagnosing-qualitatively` first, to confirm it is real (a [delta] beyond the [noise band], not eval noise); then `reverting-to-champion` — branch the next training round from the champion in the run's durable `score_state` (mirrored in the derived `[run_dir]/CHAMPION` pointer) instead of continuing to exploit a damaged `last` |
| ERROR | Fix the measurement. Do not touch the policy. |

A round may use **more than one** skill (the [action set]) — these reach-fors are
per-need, not mutually exclusive. Bundling advances faster but the round's single
[delta] then covers the whole set, so you lose the ability to say which skill
earned it; isolate one skill in its own round when the goal is to learn what works.

## Skills

Workers execute a skill by reading its `SKILL.md` and following it with the
values from the controller's [round brief]. All commands run against the external
LeRobot repo, prefixed `uv run`.

The skill directories are grouped on disk into two subfolders (this index and
`LIBRARY.lock` stay at the `skills/` root):

- **`original/`** — the seed skills the library shipped with (`Origin` ids `O1`–`O11`)
  plus the vendored `skill-creator` (fetched from `anthropics/skills`).
- **`iterated/`** — skills authored during loop rounds or offline maintenance
  (`Origin` is a round number or an `offline <date>`).

The `Origin` column is the source of truth for which bucket a skill belongs to; the
subfolder just mirrors it. New skills created during a round go in `iterated/`.

| Skill | Purpose | Origin | Lifecycle |
|---|---|---|---|
| [`continuing-training`](original/continuing-training/SKILL.md) | Start or resume the training run into the persistent [train_dir] | O1 | validated |
| [`measuring-the-gate`](original/measuring-the-gate/SKILL.md) | Run the objective's eval command verbatim — the mandatory feedback signal | O3 | validated |
| [`collecting-data`](original/collecting-data/SKILL.md) | Record additional episodes on the robot | O4 | candidate |
| [`curating-dataset`](original/curating-dataset/SKILL.md) | Inspect, clean, or augment the dataset (incl. filtering to the suite the objective measures) | O5 | validated |
| [`diagnosing-qualitatively`](original/diagnosing-qualitatively/SKILL.md) | Watch rollouts, replays, and eval videos to see *how* it fails | O6 | validated |
| [`annotating-data`](original/annotating-data/SKILL.md) | Annotate or re-label episodes (label mutation is irreversible — snapshot first) | O7; restored offline 2026-07-15 | candidate |
| [`researching-online`](original/researching-online/SKILL.md) | Search papers, docs, and issues to escape a plateau | O8 | candidate |
| [`writing-new-scripts`](original/writing-new-scripts/SKILL.md) | Write a behavior this repo doesn't have yet | O9 | candidate |
| [`checking-hardware`](original/checking-hardware/SKILL.md) | Calibrate and check cameras/ports — the robot, not the model | O10 | candidate |
| [`scoring-with-reward-model`](original/scoring-with-reward-model/SKILL.md) | Score a real robot with a reward model when there is no gym env | O11 | candidate |
| [`reverting-to-champion`](iterated/reverting-to-champion/SKILL.md) | Branch training back from the champion checkpoint after a confirmed regression | offline 2026-07-10 | candidate |
| [`skill-creator`](original/skill-creator/SKILL.md) | Create and improve skills themselves (vendored, Apache-2.0) | anthropics/skills | validated |
| [`preparing-runtime`](iterated/preparing-runtime/SKILL.md) | Run setup/download/preprocess operations noninteractively with resume, bounded output, growth checks, and durable exit evidence | offline 2026-07-13 | candidate |
| [`installing-libero-headless`](iterated/installing-libero-headless/SKILL.md) | Install LeRobot's LIBERO sim env (hf-libero) into the repo venv on a headless box | round 0 | candidate |
| [`detaching-gpu-jobs`](iterated/detaching-gpu-jobs/SKILL.md) | Dispatch multi-hour GPU jobs detached so harness task reaping cannot kill them, with exit sentinel + artifact watch + scheduled fallback wake | round 0; re-registered offline 2026-07-15 | candidate |
| [`tuning-action-horizon`](iterated/tuning-action-horizon/SKILL.md) | Shrink a VLA checkpoint's inference action horizon (n_action_steps) for closed-loop control without retraining | round 2 | validated |
| [`rebalancing-stage-2`](iterated/rebalancing-stage-2/SKILL.md) | Clone each multi-stage demo from its first place event so the post-place state gets 2x sampling weight — for sequencing failures | round 4 | validated |
| [`unfreezing-the-vlm`](iterated/unfreezing-the-vlm/SKILL.md) | Make the frozen VLM backbone trainable — MEASURED NEGATIVE on a sequencing failure (pooled -1.0); do not re-buy | round 3 | deprecated |
| [`rebasing-on-a-stronger-checkpoint`](iterated/rebasing-on-a-stronger-checkpoint/SKILL.md) | Measure a published checkpoint of the same policy class under the objective's own gate; adopt it as the lineage base only if it beats the champion | round 1 | candidate |
| [`correcting-subtask-stalls`](iterated/correcting-subtask-stalls/SKILL.md) | Test-time levers (chunk-staleness, subtask replan/backtrack triggers) for diagnosed sequencing stalls in long-horizon evals — measured failure: place object 1, never start object 2 | offline 2026-07-15 (verified external research) | candidate |
| [`evicting-hf-dataset-caches`](iterated/evicting-hf-dataset-caches/SKILL.md) | Free disk by deleting lsof-verified-unheld regenerable HF datasets builder caches before a training launch | round 1 (run _70_002) | candidate |
| [`souping-task-vectors`](iterated/souping-task-vectors/SKILL.md) | Interpolate a regressed fine-tune's task vector into the champion (keep gains, cancel forgetting) | round 2 (run _70_002) | candidate |

`Origin` is the option id each skill carried in the retired `OPTIONS.md` registry;
for a vendored skill, its upstream source; for a skill added outside a round, when
it was added — kept so old ledgers stay readable.

`Lifecycle` is `candidate | validated | deprecated`: **candidate** = documented but
not yet evidenced in a logged round of this loop; **validated** = its procedure
survived contact with a real round (`measuring-the-gate` is validated by
construction — every round's Measure step exercises it; `skill-creator` is
upstream-tested vendored tooling, so its lifecycle lives in this row only and its
vendored body is never edited); **deprecated** = kept for the record — do not
reach for it. Prefer a `validated` skill when several fit; a `candidate` costs
the same to run but its `Evidence` is thinner. Transitions happen at flow
Step 3h, driven by measured evidence, never by claim.

## Evidence tiers (how strong is "validated"?)

`Lifecycle` says whether a skill is live; **`evidence_tier`** says how far its
effect has been *replicated*. A single good round is weak evidence — bundled
actions can't attribute a delta to one skill, and one seed/task/embodiment can't
rule out luck. Record a skill's tier under `metadata.evidence_tier` on this
ladder, promoting only on measured, isolated replication:

| Tier | Earned when |
|---|---|
| `candidate` | Documented; no isolated logged round yet. |
| `reproduced` | Its effect held in **≥2 isolated rounds** (the skill alone in its `[action set]`), same task/seed/embodiment. |
| `cross-seed` | `reproduced`, and the effect held across **≥2 distinct seed sets**. |
| `cross-task` | `cross-seed`, and it held on **≥2 distinct tasks**. |
| `cross-embodiment` | `cross-task`, and it held on **≥2 distinct robots/embodiments**. |

**Selection rule:** a skill influences **unattended** action selection (flow
Step 3d, when no operator is watching) only once it is at least `reproduced`.
Below that it stays an **exploration candidate** — usable, but only in an
isolated round whose whole purpose is to gather its evidence.

**Evidence record (per skill, kept in its `## Evidence` section):** exact
upstream URL **and commit** (for anything vendored/adapted); LeRobot / model /
dataset compatibility; required permissions and mutation scope; **positive and
negative** trials; tasks, seeds, hardware, effect size, uncertainty, and cost;
whether the skill ran **isolated or bundled**; and the reviewer identity +
approval status. Unknown fields are written `unknown`, never guessed.

## Creating a new skill

If the right move this round isn't listed above — a different framework, a
simulator, a data source, a tool, an idea from a paper — do it. Then register the
**reusable** behaviors here as `lifecycle: candidate`. A failed one-off experiment
belongs in the ledger's [round entry], not here — *unless* it yields a safe
reusable diagnostic procedure (register that as a `candidate`) or a trap worth
pinning to an existing skill's `Watch out`. An unregistered reusable lesson is one
the next round has to pay for again.

**Round-time minimal form** (mandatory path during a loop round — cheap by design):

1. Create `skills/iterated/<gerund-name>/SKILL.md` with this shape (~20 lines; conventions
   from `original/skill-creator/SKILL.md` — third-person description stating what it does
   *and* when to use it, name equal to the directory name):

   ```md
   ---
   name: <gerund-name>
   description: <what it does. Use when <the condition under which a future round should pick this>.>
   metadata:
     lifecycle: candidate       # candidate | validated | deprecated
     evidence_tier: candidate   # candidate | reproduced | cross-seed | cross-task | cross-embodiment
     safety: reversible         # reversible | mutating | irreversible
   ---

   # <Short imperative title>

   ## Prerequisites
   <state/artifacts that must exist before running — one line>

   ## Do
   <the command(s), or a description if it wasn't a command>

   ## Mutates
   <the mutable resources this touches — checkpoints, dataset, configs, hardware — or "nothing">

   ## Validation
   <how to confirm it actually took effect>

   ## Rollback
   <how to undo it, or "none — reversible" / "none known — treat as irreversible">

   ## Watch out
   <the trap you hit, or would have hit — known failure contexts>

   ## Evidence
   <!-- Upstream: <url>@<commit> (or "none — original"). Compatibility: LeRobot <ver> / <model> / <dataset>.
        Permissions/mutation scope: <what it may touch>. Reviewer: <who> (<approved|unreviewed>). -->
   - <round #, isolated|bundled, seeds, task, hardware, metric delta ± uncertainty, cost, verdict —
     append a line every time the skill is used; record negative trials too>
   ```

   Promote `metadata.evidence_tier` only on replicated evidence per *Evidence
   tiers* above; below `reproduced`, the skill stays an exploration candidate for
   unattended selection.

   (`lifecycle`/`safety` live under `metadata:` — the Agent Skills frontmatter
   allowlist has no top-level slots for them, and `skill-creator`'s
   `quick_validate.py` rejects them there while ignoring keys nested under
   `metadata`.)

2. Add one row to the *Skills* table above (Origin: "round <n>", Lifecycle:
   `candidate`).

3. **Registration is a library transaction.** This library is shared live
   between concurrent loop instances. All writes here (skill dirs and this
   index) go through the flow's Step 3(h) protocol: the controller holds an
   exclusive `flock` on the stable `skills/LIBRARY.lock`, re-reads this index
   under the lock, checks for an existing skill covering the same behavior
   under any name (fold evidence into it when in doubt — see *Curating* below),
   and atomically replaces the index (temp file → rename). Never write the
   index without the lock.

Do **not** run skill-creator's test/eval/human-review loop during a round — see
the vendoring note at the top of `original/skill-creator/SKILL.md`. That full loop
(test prompts, baselines, benchmark viewer, description optimization) is for
**offline, operator-attended** hardening of a skill that has proven itself.

## Curating the library

The library grows every run; keep it usable.

- **Promote on evidence.** A skill whose documented procedure survives contact
  with a real round moves `candidate → validated` (`metadata.lifecycle` in its
  frontmatter + this index's Lifecycle column); append the round's outcome to
  its `Evidence` either way.
- **Never delete a failed skill — deprecate it.** Set `metadata.lifecycle:
  deprecated` in its frontmatter and this index, add `**Deprecated:** <one-line reason>` at the
  top of its body, and leave it in place. Deleting it invites a future round to
  rediscover the same dead end.
- **Merge near-duplicates** into the earlier skill, folding the new `Evidence:`
  line in and deprecating the later directory.
- **Keep entries short.** If a skill needs more than the template, put the detail
  in `references/` inside the skill (one level deep) or under the run dir, and
  link to it from the SKILL.md.
