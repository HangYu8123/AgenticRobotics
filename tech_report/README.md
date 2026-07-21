# AgenticRobotics — Tech Report Materials

Materials for a technical report on **AgenticRobotics**, produced by applying the
[**ResearchStudio**](https://arxiv.org/abs/2607.04438) skill methodology (Microsoft) to the
repo's own `README.md`, `robot_agentic_training_flow.md`, `objective.example.yaml`, and
`skills/` library. Two phases, matching the request:

1. **Generate ideas** — ResearchStudio-**Idea** / IdeaSpark → `idea_cards.md`
2. **Produce report materials** — the written report + ResearchStudio-**Reel** dissemination substrate

## Contents

| File | What it is | ResearchStudio skill applied |
|---|---|---|
| [`idea_cards.md`](idea_cards.md) | 1 framing card (the report's thesis) + 4 candidate extension directions, in IdeaSpark's Title·Motivation·Method·Falsification·Differentiation·Compute schema | `idea_spark` (Idea) |
| [`tech_report.md`](tech_report.md) | **The technical report** (canonical source) — Abstract, Intro, System Design, Method, Evaluation, Related Work, Limitations, Conclusion, References | systems-paper structure (Levin&Redell / SOSP hints / NeurIPS) |
| [`paper_spec.md`](paper_spec.md) | Reusable 9-section extraction + narration scripts — the substrate every renderer consumes | `paper2assets` (Reel) |
| [`dissemination_outline.md`](dissemination_outline.md) | Render-ready outlines for poster, bilingual blog, video, and interactive reel | `paper2poster` / `paper2blog` / `paper2video` / `paper2reel` (Reel) |

**Authoring order (to prevent number drift):** `tech_report.md` is canonical; `paper_spec.md`
and `dissemination_outline.md` are derived from it. Edit the report first, then re-derive.

## How these were produced (and what they are not)

These are **authored** materials, produced by applying the skills' runbooks and output
contracts — **not** the output of running the skills' Python orchestrators. That is a
deliberate, evidence-based choice: both ResearchStudio pipelines are infra-blocked in this
environment.

- **IdeaSpark** needs Python ≥3.10 (found 3.8.10), the connectors `feedparser`/`beautifulsoup4`/
  `pymupdf`/`openreview-py` (absent), and `.env` credentials (absent); its Phase 0 requires
  *real* external retrieval and halts on connector failure. So `idea_cards.md` uses IdeaSpark's
  *card schema* but not its Phase-0 grounding / Phase-3 collision audit — the cards are
  **candidate directions, not audited novelty claims**.
- **Reel** needs a compiled paper PDF (none exists), plus `pymupdf` and `libreoffice` (absent),
  to render. So `paper_spec.md` and `dissemination_outline.md` are the *inputs and plans* the
  Reel renderers consume, authored to the real output contracts.

### To render the real artifacts (once infra is provisioned)

```bash
# 0. Environment for IdeaSpark (idea grounding/audit)
conda create -n researchstudio "python>=3.10" -y && conda activate researchstudio
python -m pip install feedparser openreview-py beautifulsoup4 pymupdf
# add OpenReview + Semantic-Scholar creds to ResearchStudio-Idea/.env, then:
#   /idea-spark <one card's direction from idea_cards.md>
#   /scoop-check <that card's Title + Method>     # prior-art collision check before any novelty claim

# 1. Compile tech_report.md -> a PDF (pandoc or LaTeX), then run the Reel pipeline on it:
#   /paper2assets ./agenticrobotics.pdf           # extract the shared bundle
#   /paper2poster ./agenticrobotics/              # poster.{html,pdf,png,pptx}
#   /paper2blog   ./agenticrobotics/              # blog_en.docx + blog_zh.docx
#   /paper2video  ./agenticrobotics/              # video.mp4 (+ no-subtitles)
#   /paper2reel   ./agenticrobotics/              # reel.html
# (Reel needs pymupdf + libreoffice + ffmpeg on PATH.)
```

## Honesty flags baked into the materials

- **Skill count = 26** (11 `original` + 15 `iterated`; 6 validated / 18 candidate / 1 deprecated by frontmatter). The README's "24" and the overviews' "22" are stale; index-vs-frontmatter differ by one `validated` — flagged as a documentation-hygiene limitation.
- **Results (53→85, 46→88)** are *the project's reported results*, traceable to `skills/iterated/tuning-action-horizon/SKILL.md` Evidence records — the repo checkout ships no `LOOP_LOG.md`/`eval_info.json`. Framed as reported, not independently re-run (honoring the system's Invariant 3).
- **SOTA-discovery citations** (Papers With Code sunset, OpenScholar 78–90% hallucination, LIBERO-PRO, Dwork holdout) originate in the project README and were independently re-verified against primary sources.

## Note on git

This `tech_report/` folder is **not committed** (per the workflow's safety rules) and is **not**
currently in `.gitignore` — so a later `git add -A` would stage it. Decide whether to commit it
as project documentation or add `/tech_report/` to `.gitignore`; this pass intentionally left
that choice to you rather than presuming.
