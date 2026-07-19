# Diffusion and Flow Matching for Robotics

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Award status is asserted only where a fetched page confirms it.
> **Scope caveat:** diffusion-based robot policies begin in 2023; entries before that are labelled generic-ML precursors or left explicitly empty. See Coverage notes.

## What this is

Diffusion and flow matching are generative-modeling techniques, originally developed for image/data synthesis, that were repurposed starting in 2023 to represent robot action distributions directly: instead of regressing a single action, a policy learns to denoise (diffusion) or integrate a learned velocity field (flow matching) from noise into a coherent action sequence. This handles multimodal action distributions (many valid ways to complete a task) better than simple regression, and today underpins several of the field's leading generalist robot policies — including the flow-matching action experts in Physical Intelligence's π0/π0.5 and Hugging Face's SmolVLA, both directly relevant to this repo's LeRobot/SmolVLA reference backend. This file traces the lineage from the generic diffusion/flow-matching math through its robotics adoption and into 2025–2026 frontier work.

## Classic papers (2014–2024, one per year — see scope caveat)

### 2014
*No qualifying paper — diffusion/flow-matching methods (generic or robotic) do not yet exist in the literature.* (see Coverage notes)

### 2015
**[Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585)** — ICML 2015 · `precursor (generic ML, not robotics)` · `award: not verified`
- *Contribution:* Introduces the diffusion probabilistic model framework: destroy structure in a data distribution via a slow forward diffusion process, then learn a reverse Markov chain to restore it, yielding a flexible yet tractable generative model.
- *Results:* Demonstrates tractable learning, sampling, and inference on toy and image datasets (e.g., swirl, MNIST-scale data), establishing the mathematical foundation later used by DDPM and all downstream diffusion models — no robotic application.

### 2016
*No qualifying paper found — no diffusion/flow-matching robotics or notable generic-ML-foundations paper for this year.* (see Coverage notes)

### 2017
*No qualifying paper found.* (see Coverage notes)

### 2018
*No qualifying paper found.* (see Coverage notes)

### 2019
*No qualifying paper found.* (see Coverage notes)

### 2020
**[Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239)** — NeurIPS 2020 · `precursor (generic ML, not robotics)` · `award: not verified`
- *Contribution:* Simplifies the diffusion framework into DDPM, connecting it to denoising score matching with Langevin dynamics and introducing the training/sampling recipe (noise-prediction network, weighted variational bound) that essentially every later diffusion model — including robotic ones — builds on.
- *Results:* Achieves an Inception score of 9.46 and a then-state-of-the-art FID of 3.17 on unconditional CIFAR-10, with 256×256 LSUN sample quality comparable to ProgressiveGAN — image synthesis only, no robotic application.

### 2021
*No qualifying paper found — no diffusion/flow-matching robotics or notable generic-ML-foundations paper for this year.* (see Coverage notes)

### 2022
**[Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747)** — arXiv 2022 (later ICLR 2023) · `precursor (generic ML, not robotics)` · `award: not verified`
- *Contribution:* Introduces Flow Matching (FM), a simulation-free way to train Continuous Normalizing Flows by regressing vector fields of fixed conditional probability paths; this family subsumes diffusion paths and also supports Optimal-Transport paths, giving the objective that π0/π0.5, SmolVLA, RDT2 and most 2025–2026 robot "flow policies" now use for their action experts.
- *Results:* Shows Optimal-Transport conditional paths yield more efficient probability paths than diffusion paths, giving faster training, faster sampling, and better generalization on standard image-generation benchmarks — no robotic application.

### 2023
**[Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/abs/2303.04137)** — RSS 2023 ([proceedings PDF](https://roboticsproceedings.org/rss19/p026.pdf)) · `genuine robotics application` · `award: not verified`
- *Contribution:* Represents a robot's visuomotor policy as a conditional denoising diffusion process over action sequences — the foundational paper applying diffusion models directly to robot control, handling multimodal, high-dimensional action distributions that regression-based policies struggle with.
- *Results:* Consistently outperforms prior state-of-the-art robot learning methods with an average 46.9% improvement across 12 tasks spanning 4 manipulation benchmarks.

### 2024
**[π₀: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/abs/2410.24164)** — arXiv 2024 (Physical Intelligence; later RSS 2025) · `genuine robotics application` · `award: not verified`
- *Contribution:* Builds a flow-matching action expert on top of a pretrained vision-language model to inherit internet-scale semantic knowledge, trained across single-arm, dual-arm, and mobile manipulator data — the direct architectural ancestor of π0.5 and an influence on SmolVLA's action expert, both used in this repo's reference stack.
- *Results:* Demonstrates zero-shot execution and fine-tuned performance on complex, long-horizon dexterous tasks (e.g., laundry folding, table bussing, box assembly) lasting from 100 seconds to several minutes, run at up to 50 Hz control frequency; the abstract does not report a single headline benchmark number.

## 2025 (3 papers)

**[RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation](https://arxiv.org/abs/2410.07864)** — ICLR 2025 (Tsinghua University) · `genuine robotics application` · `award: not verified`
- *Contribution:* Scales a diffusion-based Transformer to 1.2B parameters — the largest diffusion foundation model for robotic manipulation at the time — with a "Physically Interpretable Unified Action Space" that unifies action representations across heterogeneous robot embodiments.
- *Results:* Pretrained on the largest multi-robot dataset assembled to date and fine-tuned on 6,000+ bimanual episodes, RDT-1B learns new skills from just 1–5 demonstrations and shows zero-shot generalization to unseen objects, scenes, and language instructions.

**[π₀.₅: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/abs/2504.16054)** — arXiv 2025 (Physical Intelligence) · `genuine robotics application` · `award: not verified`
- *Contribution:* Extends π0's flow-matching action expert with co-training on heterogeneous data sources (multi-robot data, high-level semantic prediction, web data) to push generalization beyond the training environments.
- *Results:* Shows for the first time that an end-to-end learned robotic system can perform long-horizon, dexterous mobile-manipulation skills — such as cleaning an entire kitchen or bedroom — in homes never seen during training.

**[SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics](https://arxiv.org/abs/2506.01844)** — arXiv 2025 (Hugging Face, Sorbonne University, et al.) · `genuine robotics application` · `award: not verified`
- *Contribution:* Pairs a compact SmolVLM-2 vision-language backbone (with layer skipping) with a flow-matching Transformer action expert using interleaved attention, aiming for an affordable, community-trainable VLA rather than a compute-maximal one — this is the action-expert architecture used by this repo's SmolVLA/LeRobot reference backend.
- *Results:* Pretrained on fewer than 30,000 episodes (roughly an order of magnitude less data than comparable VLAs) drawn entirely from public Hugging Face Hub datasets, SmolVLA matches or exceeds larger VLAs on benchmarks while cutting task completion time by roughly 30% via asynchronous inference.

## 2026 (5 papers)

**[RDT2: Exploring the Scaling Limit of UMI Data Towards Zero-Shot Cross-Embodiment Generalization](https://arxiv.org/abs/2602.03310)** — arXiv 2026 · `lab: Tsinghua University` (confirmed via [HuggingFace model card](https://huggingface.co/robotics-diffusion-transformer/RDT2-FM), GitHub org `thu-ml/RDT2`) · `genuine robotics application` · `award: not verified`
- *Contribution:* Successor to RDT-1B; pairs a 7B vision-language backbone (RDT2-VQ) with a flow-matching action expert (RDT2-FM) trained on UMI-format handheld-gripper data to reach zero-shot deployment on robot embodiments never seen during training.
- *Results:* Trained on 10,000+ hours across 100+ scenes of UMI manipulation data, RDT2 achieves zero-shot cross-embodiment generalization to novel bimanual platforms (e.g., UR5e, Franka FR3) after calibration, on open-vocabulary tasks.

**[GRITS: A Spillage-Aware Guided Diffusion Policy for Robot Food Scooping Tasks](https://arxiv.org/abs/2510.00573)** — ICRA 2026 · `lab: NVIDIA (co-author Yu-Wei Chao), National Yang Ming Chiao Tung University, XYZ Robotics` (confirmed via [arXiv HTML](https://arxiv.org/html/2510.00573v2)) · `genuine robotics application` · `award: ICRA 2026 Best Paper Award on Robot Learning — Finalist` (verified via [official ICRA 2026 awards page](https://2026.ieee-icra.org/awards/))
- *Contribution:* Adds a simulation-trained spillage predictor as a differentiable test-time guidance signal to a diffusion policy for robotic food scooping, steering sampling toward safer trajectories without retraining or collecting real spillage data.
- *Results:* Achieves an 82% task success rate with a 4% spillage rate — over 40% lower spillage than standard diffusion-policy baselines — trained on 6 food categories and evaluated generalizing to 10 unseen categories.

**[Flow Policy Gradients for Robot Control](https://arxiv.org/abs/2602.02481)** — arXiv 2026 · `lab: UC Berkeley, Stanford University, Carnegie Mellon University` (with Amazon FAR; confirmed via [arXiv HTML](https://arxiv.org/html/2602.02481)) · `genuine robotics application` · `award: not verified`
- *Contribution:* Makes flow-matching policy gradients practical for training and reinforcement-learning fine-tuning of expressive flow-based robot policies, rather than restricting flow matching to imitation learning alone.
- *Results:* Demonstrates robust sim-to-real transfer on two humanoid robots and improved performance over baselines across legged locomotion, humanoid motion tracking, and manipulation tasks.

**[Qwen-RobotWorld Technical Report: Unifying Embodied World Modeling through Language-Conditioned Video Generation](https://arxiv.org/abs/2606.17030)** — arXiv 2026 · `lab: Alibaba Tongyi Lab` (author Jingren Zhou; Alibaba Tongyi Lab affiliation corroborated via web search of the "Qwen-Robot Suite," not directly stated on the arXiv abstract page — see Coverage notes) · `genuine robotics-adjacent application (video world model, not an action policy)` · `award: not verified`
- *Contribution:* Uses a 60-layer double-stream diffusion Transformer to build a language-conditioned video world model that predicts physically grounded future visual trajectories, with natural language as a unified interface across manipulation, autonomous driving, indoor navigation, and human-to-robot skill transfer.
- *Results:* Ranks 1st overall on EWMBench and DreamGen Bench, trained on an 8.6M video-text corpus containing 200M+ frames.

**[FP3: A 3D Foundation Policy for Robotic Manipulation](https://arxiv.org/abs/2503.08950)** — ICRA 2026 · `lab: Shanghai AI Laboratory, Shanghai Qi Zhi Institute` (confirmed via [arXiv HTML](https://arxiv.org/html/2503.08950v1); **not** one of the requested big labs — included transparently, see Coverage notes) · `genuine robotics application` · `award: ICRA 2026 Best Paper Award on Robot Learning — Finalist` (verified via [official ICRA 2026 awards page](https://2026.ieee-icra.org/awards/))
- *Contribution:* First large-scale 3D foundation policy for manipulation: a diffusion-transformer pretrained directly on point-cloud observations (rather than 2D images) across 60k trajectories, aiming for more geometry-grounded generalization.
- *Results:* With only 80 task-specific demonstrations, FP3 exceeds 90% success in novel environments with unseen objects, substantially outperforming prior robot foundation models.

## Coverage notes

- **Classic-series gaps (2014, 2016–2019, 2021):** searched specifically; no defensible diffusion/flow-matching paper (generic-ML or robotic) was found for these years. Per the anti-fabrication instructions, these are left as explicit empty markers rather than force-fitting unrelated robotics papers.
- **Precursor years (2015, 2020, 2022):** used the generic-ML foundations as instructed (Sohl-Dickstein et al. 2015 for diffusion; Ho et al. DDPM 2020; Lipman et al. flow matching 2022), each explicitly labelled `precursor (generic ML, not robotics)`. None have a robotics application; all are cited for their role as the mathematical basis of every robotics entry from 2023 onward.
- **2023/2024 anchors:** Diffusion Policy (RSS 2023) is confirmed as the first genuine diffusion robot-policy paper. π0 (Oct 2024, later RSS 2025) is the 2024 slot — its own arXiv abstract reports no single headline benchmark number, so the results line above is a faithful qualitative paraphrase, not an invented statistic.
- **2025 selection:** three papers were chosen for direct relevance to this repo's SmolVLA/LeRobot backend (SmolVLA, π0.5) plus one additional major diffusion foundation model (RDT-1B) for method diversity. A fourth strong 2025 candidate, NVIDIA's GR00T N1 (arXiv:2503.14734, diffusion-transformer action head), was found and verified but excluded only because the quota is 3 — it may be worth a future revision if diversity of labs is prioritized over repo-relevance.
- **2026 "big lab" verification:** GRITS, RDT2, "Flow Policy Gradients for Robot Control," and Qwen-RobotWorld are traceable to labs on the requested list (NVIDIA/NYCU, Tsinghua, UC Berkeley+Stanford+CMU, Alibaba Tongyi Lab) via fetched pages, with one caveat: Qwen-RobotWorld's Alibaba affiliation was corroborated through a secondary web-search description of the "Qwen-Robot Suite," not a directly fetched affiliation line on the arXiv page itself — flagged rather than silently asserted. The fifth 2026 slot, FP3, is a verified ICRA 2026 Best Paper Award finalist but its confirmed institutional affiliation (Shanghai AI Laboratory / Shanghai Qi Zhi Institute) is **not** on the requested big-lab list; Tsinghua appears only as a funding-program acknowledgment, not an author affiliation, so it is not claimed as a Tsinghua paper. Despite a further search for a strictly-matching fifth big-lab paper (Google, DeepMind, Stanford-only, MIT-only, CMU-only candidates were checked), none could be independently verified within the session's search budget — FP3 is included as the most defensible remaining ICRA 2026 finalist rather than force-fitting an unverified lab claim.
- **ICRA 2026 award status:** confirmed via the official awards page that "award finalists posted, winners pending" (per task brief) is accurate — GRITS and FP3 are both **finalists**, not confirmed winners, for the Best Paper Award on Robot Learning; an initial web-search summary incorrectly reported GRITS as a winner and was corrected against the primary source.
- **Session constraint:** this session's WebSearch budget (200 calls, shared across the parallel research workflow) was exhausted partway through 2026 research; all further verification after that point used WebFetch only (arXiv abstract/HTML pages, HuggingFace model cards, DuckDuckGo HTML search, official award pages).

## Sources

- https://arxiv.org/abs/1503.03585 (Sohl-Dickstein et al. 2015)
- https://arxiv.org/abs/2006.11239 (Ho, Jain, Abbeel — DDPM 2020)
- https://arxiv.org/abs/2210.02747 (Lipman et al. — Flow Matching 2022)
- https://arxiv.org/abs/2303.04137 and https://roboticsproceedings.org/rss19/p026.pdf (Diffusion Policy, RSS 2023)
- https://arxiv.org/abs/2410.24164 (π0, 2024)
- https://arxiv.org/abs/2410.07864 (RDT-1B, ICLR 2025)
- https://arxiv.org/abs/2504.16054 (π0.5, 2025)
- https://arxiv.org/abs/2506.01844 (SmolVLA, 2025)
- https://arxiv.org/abs/2503.14734 (GR00T N1, 2025 — evaluated, not used in final 3)
- https://arxiv.org/abs/2602.03310 and https://huggingface.co/robotics-diffusion-transformer/RDT2-FM (RDT2, 2026)
- https://arxiv.org/abs/2510.00573 and https://arxiv.org/html/2510.00573v2 (GRITS, ICRA 2026)
- https://arxiv.org/abs/2602.02481 and https://arxiv.org/html/2602.02481 (Flow Policy Gradients for Robot Control, 2026)
- https://arxiv.org/abs/2606.17030 (Qwen-RobotWorld, 2026)
- https://arxiv.org/abs/2503.08950 and https://arxiv.org/html/2503.08950v1 (FP3, ICRA 2026)
- https://2026.ieee-icra.org/awards/ (ICRA 2026 Best Paper Award finalists, official)
- https://roboticsfoundation.org/awards/best-paper-award/ (RSS award ground truth — no 2026 entries yet, confirmed)
- https://github.com/mbreuss/diffusion-literature-for-robotics (cross-check list — confirmed no 2025/2026 entries present, not usable for those years)
