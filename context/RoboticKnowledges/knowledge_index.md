# Robotic Knowledge Base — Index

Compiled **2026-07-19** from live web sources.

## What this is

A reference library of robotics background knowledge for the operators and agents working on this repo: ROS, hardware, the major robot-learning paradigms (RL, imitation learning, diffusion/flow matching, VLA), classical control and planning, kernel methods, mechanical engineering, and agentic AI.

**Scope note — this is *not* a pack runtime dependency.** The rest of `context/` (`_lib/`, `philosophy/`, `agents/`, `repo_info/`, `skills/`) is a vendored mirror of the HarnessFlow pack files that `robot_agentic_training_flow.md` reads at runtime. `RoboticKnowledges/` is different: it is **background reading for humans and for research subagents**, and nothing in the control loop reads it. It is deliberately outside the flow's runtime contract, so adding or reorganizing files here cannot break a run.

**Relationship to the skills library.** The root `skills/` tree is the flow's *operational* memory — procedures the loop actually executes, promoted on measured evidence. This knowledge base is *declarative* background. Where the two overlap, **the skill wins**: in particular `skills/iterated/reinforcing-with-rl/SKILL.md` is the source of truth for VLA-RL fine-tuning recipes, and the `reinforcement-learning/` and `vla/` files here cross-reference it rather than forking a second paper table.

## How to read the entries

Each paper is described in three parts, as requested: **title**, **key contribution** (one sentence), **key results** (one sentence).

```
**[Exact Title](url)** — Venue Year · `award: <exact award name>` | `award: not verified`
- *Contribution:* one sentence.
- *Results:*      one sentence.
```

## Sourcing and verification policy

Every category file was written by a subagent operating under a live-web-only contract. The rules, and what the markers mean:

| Marker / rule | Meaning |
|---|---|
| Every entry carries a URL | The writer fetched that page in-session. Nothing was written from model memory. |
| `award: <exact name>` | A **fetched page states this award**. Awards are never inferred from a paper's reputation. |
| `award: not verified` | No fetched page confirmed an award. This is the honest default, **not** a claim that the paper lost. |
| `lab: <affiliation>` | Affiliation shown on a fetched page. `lab: not verified` where it could not be confirmed. |
| `precursor (…)` | The paper predates the named subfield and is included as lineage, **not** as an instance of it. |
| *No qualifying paper — …* | An intentionally empty year slot. **Leaving a slot empty was explicitly preferred over force-fitting a paper.** |

Every file ends with a **Coverage notes** section recording where the requested structure could not be met, and a **Sources** section listing the URLs fetched.

## Index

| # | Category | Path | Contents |
|---|---|---|---|
| 1 | ROS 1 and ROS 2 | [`ros/`](ros/README.md) | One-sentence intro each; 16 known issues/challenges and 9 common mistakes across both; 9 ROS 1→2 migration pitfalls |
| 2 | Robots and hardware | [`hardware/`](hardware/README.md) | 25 platforms across manipulators (7), humanoid/legged (7), mobile bases (1), grippers (3), sensors (5), compute (2) — vendor parameters only |
| 3 | Reinforcement learning | [`reinforcement-learning/`](reinforcement-learning/README.md) | 19 papers: 11 classic year-slots (all filled), 3×2025, 5×2026; 6 verified awards |
| 4 | Imitation learning | [`imitation-learning/`](imitation-learning/README.md) | 19 papers: 11 classic (all filled), 3×2025, 5×2026; 4 verified awards |
| 5 | Diffusion and flow matching | [`diffusion-and-flow-matching/`](diffusion-and-flow-matching/README.md) | 13 papers: 2 genuine classic-era + 3 labelled precursors + **6 deliberately empty pre-2023 years**, 3×2025, 5×2026 |
| 6 | VLA | [`vla/`](vla/README.md) | 18 papers: 3 genuine classic-era VLA + 7 labelled precursors + 1 empty year, 3×2025, 5×2026 |
| 7 | Classic control and planning | [`classic-control-and-planning/`](classic-control-and-planning/README.md) | 19 papers: 11 classic (all filled), 3×2025, 5×2026; 8 verified awards — the best-covered category |
| 8 | Kernel methods | [`kernel-methods/`](kernel-methods/README.md) | 14 papers: 11 classic, 3×2025, **0 of 5 2026 big-lab slots fillable**; best-paper preference dropped by design |
| 9 | Mechanical engineering | [`mechanical-engineering/`](mechanical-engineering/README.md) | Brief practical reference: actuation, transmission, materials/stiffness, kinematics, statics/dynamics, tolerancing, bearings/IP, safety standards |
| 10 | Agentic AI | [`agentic-ai/`](agentic-ai/README.md) | 13 papers (2026); 4 agent-skills repos with fetched star counts; 8 OpenAI and 7 Anthropic system cards + 5 engineering posts |

> **On the "verified awards" counts above:** these are not defined identically across rows and are not comparable. Reinforcement learning counts **outright wins only**; imitation learning and classic control & planning count **wins and finalists together**. Each figure matches its own file's self-report — read the per-entry `award:` markers for the actual status of any given paper.

## Known limitations

These are aggregated from the per-file Coverage notes. Read them before trusting a slot.

**Structural gaps that are real, not oversights:**

- **Diffusion/flow matching has no pre-2023 robotics history.** Diffusion Policy (RSS 2023) is the founding robotics application; the generic method (Sohl-Dickstein 2015, DDPM 2020, Flow Matching 2022) is included as labelled precursors and **six year slots are deliberately empty**.
- **VLA has no pre-2022 history.** RT-1 (2022) starts the paradigm and RT-2 (2023) names it; 2015–2021 hold labelled visuomotor/language-conditioned precursors, 2014 is empty.
- **Kernel methods carry no best-paper awards.** This work lands in IJRR / T-RO / ICML / CDC, not as ICRA/IROS/RSS/CoRL best papers, so the "prefer best paper" preference was dropped for that category outright rather than fabricated. Its **2026 big-lab slots could not be filled at all** — genuine 2026 kernel/GP-robotics papers exist but from other institutions, and are listed transparently instead of counted.
- **"10 papers, 2014–2024, one per year" is internally inconsistent** — that range spans 11 years. All six paper categories resolve it the same way: **11 year slots**, one per year.

**Venue reality as of 2026-07-19 (verified):**

| Venue | Status | Consequence |
|---|---|---|
| ICRA 2026 | Held — Vienna, Jun 1–5 2026 | Award **finalists** posted; winners not yet announced |
| RSS 2026 | Held — Sydney, Jul 13–17 2026 (6 days ago) | Awards not yet published |
| IROS 2026 | **Not yet held** — Pittsburgh, Sep 27–Oct 1 2026 | No 2026 IROS papers or awards exist |
| CoRL 2026 | **Not yet held** — Austin, Nov 9–12 2026 | No 2026 CoRL papers or awards exist |

So every 2026 entry is an arXiv preprint or an ICRA/RSS 2026 accepted paper, and **no 2026 entry anywhere in this knowledge base carries a confirmed award** — only finalist status, where verified.

**Collection-time limitations:**

- The shared `WebSearch` budget (200 calls) was exhausted partway through by the ten parallel writers. Later verification used direct `WebFetch` against arXiv, DBLP, Crossref, OpenReview, conference sites, and vendor pages. No writer substituted prior knowledge when search ran out; each affected file discloses this.
- Some primary sources block automated fetching: `docs.ros.org` and `ros.org/reps` (anti-bot), `iso.org` and several vendor PDFs (403 / binary). Where a claim rests on a search snippet of the same URL rather than a full page fetch, the file says so.
- Award coverage is uneven because there is **no single canonical 2014–2026 best-paper list** for ICRA, IROS, or CoRL — only RSS has one (`roboticsfoundation.org/awards/best-paper-award/`, 2009–2025). ICRA/IROS awards live on per-category IEEE RAS subpages that are partly JS-rendered; CoRL awards live on per-year sites. Absence of an award marker is therefore weak evidence.

## Maintenance

This file and its ten category files are a **dated snapshot**, not a living feed. The fastest-staling content is: `agentic-ai/` (star counts, system-card versions — days to weeks), the 2026 sections everywhere (IROS and CoRL 2026 will add papers and awards in Sep and Nov 2026), and the pending ICRA/RSS 2026 award announcements. Re-run a category's research to refresh it; keep the Coverage notes honest about what was re-verified and what was carried forward.
