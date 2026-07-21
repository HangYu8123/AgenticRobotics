# Dissemination Outline — AgenticRobotics

> **Tech-report phase 2, last mile** (ResearchStudio-**Reel**). Concrete, render-ready
> outlines for the four Reel deliverables — poster, bilingual blog, video, interactive reel —
> each mapped to the skill that produces it and grounded in `paper_spec.md` (the shared
> `paper2assets` substrate) and `tech_report.md`. **All numbers are derived from those two
> files** — edit the report/spec first, then re-derive here, so nothing drifts.
>
> These are *outlines*, not rendered artifacts: the Reel renderers are infra-blocked in this
> environment (no compiled paper PDF; `pymupdf`/`libreoffice` absent). Once a PDF and the
> native tools are provisioned, `paper2assets` extracts the bundle and each renderer below
> consumes it — see `README.md` in this folder for the exact commands.

---

## 0. Shared inputs (paper2assets bundle)
- **paper_spec.md** — the 9 sections + audio scripts (already authored here).
- **Figures to produce** (this project has no paper figures yet — author these as the reusable `assets/figures/*`):
  - `fig_architecture` — the controller/worker diagram (from `tech_report.md` §2.1).
  - `fig_round_loop` — Steps 0–4 pipeline with the (a)–(j) round sub-steps.
  - `fig_scoring` — the promotion decision tree (band → 1.5× margin → confirmation → paired test).
  - `fig_results` — a two-bar chart per run: baseline → final (53→85, 46→88), band whiskers ±12.1 / ±11.8.
  - `fig_durability` — the 6-phase commit sequence + recovery.
- **QR / links** — repo URL, ResearchStudio methodology cite.

---

## 1. Poster (`paper2poster` → `poster.{html,pdf,png,pptx}`)

Landscape (NeurIPS/CVPR preset). Column flow left→right, one idea per block:

| Block | Content (from spec/report) | Figure |
|---|---|---|
| Title bar | Full title + one-line deck ("Close the outer loop, not the inner one") | — |
| Problem | Outer-loop bottleneck; SOTA-discovery gap | — |
| Approach | Controller/worker split; backend-agnostic contract | `fig_architecture` |
| Round loop | Steps 0–4 + (a)–(j) | `fig_round_loop` |
| Measured, never asserted | Band + 1.5× margin + confirmation + paired McNemar/bootstrap | `fig_scoring` |
| Crash-safe | 10 invariants (highlight 6,7,8,9,10); 6-phase commit; replay checker | `fig_durability` |
| Skills library | 26 skills, evidence ladder, `flock`-shared, negatives kept | — |
| Results | 53→85, 46→88; the 30-min zero-training win; horizon-saturation ablation | `fig_results` |
| Takeaway + QR | One-sentence takeaway; repo/methodology QR | — |
- **Narration pills:** reuse each section's `Audio script` from `paper_spec.md` (paper2poster's Listen/Full-Listen feature).

---

## 2. Bilingual blog (`paper2blog` → `blog_en.docx` + `blog_zh.docx`)

Both share identical facts, figures, and numbers; differ only in language/voice (EN = neutral
research blog; ZH = restrained WeChat register). Recommended DOCX structure (per the
paper2blog output contract):

1. **Title + deck.** EN: *"Automating the outer loop of robot learning: an LLM controller that trains, measures, and improves policies on its own."* ZH: *「让机器人策略自己进化：一个只做决策的大模型控制器」*
2. **Lead (2–3 paragraphs).** The manual outer loop; the "controller not doer" idea; the 30-minute zero-training result as the hook.
3. **Overview figure.** `fig_architecture`.
4. **Paper / code links.**
5. **Sections:**
   - *Why the outer loop is the bottleneck* (Intro).
   - *How one round works* (`fig_round_loop`).
   - *Measured, never asserted* — the statistics, in plain terms (`fig_scoring`).
   - *Crash-safe by construction* — why long unattended runs survive kills (`fig_durability`).
   - *A library that gets smarter every run* — evidence ladder + kept negatives.
   - *Results* (`fig_results`) — with the honest provenance caveat (§4 of the report).
6. **Result table** (same numbers both languages):

   | Run | Baseline | Final | Decisive lever |
   |---|---|---|---|
   | `smolvla_libero_70_001` | 53.0 | 85.0 | action-horizon (30-min, zero-train) |
   | `libero_smolvla_001` | 46.0 | 88.0 | action-horizon 50→10 |
7. **Closing.** The four extension directions (`idea_cards.md`) + the "reconcile docs/schema" honesty note.

- **Filenames stay ASCII** (`blog_en.docx` / `blog_zh.docx`); the Chinese title lives *inside* the `_zh` doc.

---

## 3. Video (`paper2video` → `video.mp4` + `video.pptx`)

~3–4 min narrated walkthrough; one slide per spec section, speaker notes = the `Audio script`
fields. Storyboard:

1. **Hook (0:00–0:20):** "This robot policy improved itself from 46 to 88 percent — and its biggest win retrained nothing." → `fig_results`.
2. **Problem (0:20–0:50):** outer loop vs inner loop → `fig_architecture` build-on.
3. **The loop (0:50–1:40):** Steps 0–4, (a)–(j) → animate `fig_round_loop`.
4. **Measured, never asserted (1:40–2:20):** the promotion decision tree → `fig_scoring`.
5. **Crash-safe (2:20–2:50):** kill-and-recover → `fig_durability`.
6. **Results + ablation (2:50–3:30):** 53→85, 46→88; horizon saturation; noise honesty.
7. **Takeaway + next (3:30–end):** four extension directions; call to the repo.
- Default visual style `spotlight_laser`; produce `video_no_subtitles.mp4` for the reel.

---

## 4. Interactive reel (`paper2reel` → `reel.html`)
- Poster-first interactive viewer; hover highlights each section; double-click opens a
  synchronized modal (video segment + slide thumbnails + captions + bilingual blog text).
- Consumes the completed poster + video + blog bundle above; serve locally via the skill's
  `serve_reel.py` (needs HTTP Range for video seeking).

---

## Content guardrails (carried from the report's honesty pass)
- **Never invent numbers or competitors.** Every figure/number traces to `paper_spec.md` → `tech_report.md` → in-repo Evidence records.
- **Keep the provenance caveat visible** wherever 85/88 appear (reported results, not re-run here).
- **State the skill count as 26** (6 validated / 18 candidate / 1 deprecated), not the stale README "24."
- **Mark the idea cards as candidate directions**, not audited novelty, in any public-facing copy.
