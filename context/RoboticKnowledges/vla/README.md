# Vision-Language-Action Models (VLA)

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Award status is asserted only where a fetched page confirms it.
> **Scope caveat:** the VLA paradigm begins ~2022 (RT-1) and is named by RT-2 (2023); earlier entries are labelled precursors or left explicitly empty. See Coverage notes.

## What this is

Vision-Language-Action (VLA) models are robot control policies that take a natural-language instruction plus visual observation(s) as input and directly output low-level robot actions (joint commands, end-effector deltas, or discretized/continuous action tokens), typically by fine-tuning or co-training a pretrained vision-language backbone on robot trajectory data. The name was coined by RT-2 (Google DeepMind, 2023), which represented robot actions as tokens output by a large VLM; RT-1 (Google, 2022) is the Transformer-based, large-scale real-world robot policy widely credited with starting the modeling lineage that RT-2 subsequently named. Before RT-1, the closest antecedents are two separate threads that VLA later fused: end-to-end visuomotor policy learning (raw pixels to torques/grasps, 2015–2018) and language-conditioned imitation learning (natural-language instructions to continuous control, 2019–2021). As of 2026, VLA is the dominant generalist-policy paradigm, spanning academic labs (Stanford, UC Berkeley, CMU, MIT, Tsinghua), industry labs (Google DeepMind, NVIDIA, Alibaba), and VLA-focused startups (Physical Intelligence).

**Relationship to the skills library:** for VLA-specific RL fine-tuning recipes the loop actually executes, `skills/iterated/reinforcing-with-rl/SKILL.md` is the source of truth; this file is background reading.

## Classic papers (2014–2024, one per year — see scope caveat)

### 2014
_No qualifying paper for this slot._ The nearest 2014 candidate, Levine & Abbeel's "Learning Neural Network Policies with Guided Policy Search under Unknown Dynamics" (NeurIPS 2014), could not be confirmed to use raw visual input (fetch of the NeurIPS proceedings page failed; the only available summary describes state-space manipulation policies, not a vision-to-action pipeline), so it does not clearly meet even the visuomotor-precursor bar for this category. Left empty rather than force-fit — see Coverage notes.

### 2015
**[End-to-End Training of Deep Visuomotor Policies](https://arxiv.org/abs/1504.00702)** — arXiv preprint 2015 (JMLR 2016) · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Levine, Finn, Darrell, and Abbeel train a deep CNN policy (92,000 parameters) end-to-end from raw camera images directly to motor torques via a partially-observed guided policy search method, testing whether joint perception+control training beats training the two separately.
- *Results:* The policy is evaluated on real-world contact-rich manipulation tasks requiring close vision-control coordination, such as screwing a cap onto a bottle, with simulated comparisons against prior policy-search methods reported in the paper.

### 2016
**[Learning Hand-Eye Coordination for Robotic Grasping with Deep Learning and Large-Scale Data Collection](https://arxiv.org/abs/1603.02199)** — arXiv preprint 2016 · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Levine, Pastor, Krizhevsky, and Quillen train a large CNN to predict grasp success probability from monocular images alone (no camera calibration or robot pose needed), then use it to servo the gripper in closed loop.
- *Results:* The model is trained on over 800,000 grasp attempts collected over two months using 6–14 real robotic manipulators in parallel, and the paper reports effective real-time control that grasps novel objects and corrects mistakes via continuous servoing.

### 2017
**[Deep Visual Foresight for Planning Robot Motion](https://arxiv.org/abs/1610.00696)** — ICRA 2017 · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Finn and Levine combine deep action-conditioned video-prediction models with model-predictive control, trained entirely from unlabeled video with no calibrated camera or instrumented setup required.
- *Results:* A real robot performs nonprehensile pushing manipulation on novel objects unseen during training, demonstrating that learned video-prediction models can directly drive physical robot control.

### 2018
**[Task-Embedded Control Networks for Few-Shot Imitation Learning](https://arxiv.org/abs/1810.03237)** — arXiv preprint 2018 · `precursor (not VLA)` · `award: not verified`
- *Contribution:* James, Bloesch, and Davison use metric learning to build a task embedding from one or more visual demonstrations, letting a single network condition on that embedding to imitate new tasks without per-task retraining.
- *Results:* The method outperforms a state-of-the-art few-shot imitation baseline in simulated visually-guided manipulation and, combined with domain randomization, transfers sim-trained policies to real-world manipulation from a single real demonstration.

### 2019
**[Learning Latent Plans from Play](https://arxiv.org/abs/1903.01973)** — CoRL 2019 · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Lynch, Khansari, Xiao, Kumar, Tompson, Levine, and Sermanet propose Play-LMP, which self-supervises on unlabeled teleoperated "play" data to organize behavior into a reusable latent-plan space conditioned on goal images (not natural language).
- *Results:* Play-LMP substantially outperforms individual expert-trained policies on 18 user-specified visual manipulation tasks (85.5% vs. 70.3% average success reported on the project page) and shows more robustness to perturbations, including retrying until success.

### 2020
**[Language Conditioned Imitation Learning over Unstructured Data](https://arxiv.org/abs/2005.07648)** — arXiv preprint 2020 (RSS 2021) · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Lynch and Sermanet train a single end-to-end network that jointly learns visual perception, language understanding, and continuous control to follow free-form natural-language instructions, using a pretrained language model and requiring language annotation on less than 1% of the underlying play data.
- *Results:* The paper reports that incorporating a large pretrained language encoder makes the resulting policy robust to instruction synonyms/rephrasings without needing additional demonstrations for each phrasing.

### 2021
**[CLIPort: What and Where Pathways for Robotic Manipulation](https://arxiv.org/abs/2109.12098)** — CoRL 2021 · `precursor (not VLA)` · `award: not verified`
- *Contribution:* Shridhar, Manuelli, and Fox combine CLIP's semantic ("what") understanding with TransporterNets' spatial ("where") precision into a two-stream, language-conditioned imitation-learning agent for tabletop manipulation.
- *Results:* The paper reports that CLIPort solves a range of language-specified tabletop tasks — from packing unseen objects to folding cloths — without explicit object-pose estimation, instance segmentation, or symbolic state.

### 2022
**[RT-1: Robotics Transformer for Real-World Control at Scale](https://arxiv.org/abs/2212.06817)** — arXiv preprint / RSS 2022 · `VLA-paradigm origin (predates the "VLA" term, coined by RT-2 in 2023)` · `award: not verified`
- *Contribution:* Brohan et al. (Robotics at Google / Everyday Robots) build a Transformer policy over a FiLM-conditioned EfficientNet and TokenLearner, trained with imitation learning on natural-language task instructions plus images to output robot actions, and study generalization as a function of data size, model size, and data diversity.
- *Results:* RT-1 executes over 700 training instructions at a 97% success rate and generalizes to new tasks, distractors, and backgrounds 25%, 36%, and 18% better respectively than the strongest baseline reported in the paper.

### 2023
**[RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/abs/2307.15818)** — arXiv preprint 2023 · `VLA (term coined here)` · `award: not verified`
- *Contribution:* Brohan et al. (Google DeepMind) co-fine-tune a large vision-language model on both robot trajectory data and internet-scale vision-language tasks (e.g. VQA), representing robot actions as output text tokens so the same model does perception, reasoning, and control — the paper that names the "vision-language-action model" (VLA) class.
- *Results:* The paper reports that RT-2 inherits web-scale semantic and reasoning knowledge into robotic control, generalizing to novel objects and instructions not seen in the robot's own training data (e.g. recognizing a toy dinosaur or that an apple is a "healthy snack") without task-specific robot training for those concepts.

### 2024
**[OpenVLA: An Open-Source Vision-Language-Action Model](https://arxiv.org/abs/2406.09246)** — arXiv preprint 2024 / CoRL 2024 · `VLA` · `award: not verified`
- *Contribution:* Kim, Pertsch, Karamcheti, et al. release a 7B-parameter open-source VLA built on Llama 2 with a DINOv2+SigLIP fused visual encoder, trained on nearly one million real-world robot demonstrations from the Open X-Embodiment dataset, and release full checkpoints and fine-tuning code (including LoRA/quantized fine-tuning for consumer GPUs).
- *Results:* The paper reports OpenVLA outperforming the much larger closed RT-2-X (55B) by 16.5 absolute points in task success rate across 29 tasks despite using 7x fewer parameters, and improving over Diffusion Policy by 20.4 points in multi-task settings.

_(Octo, "An Open-Source Generalist Robot Policy," arXiv:2405.12213, RSS 2024, was also verified as a genuine 2024 VLA-adjacent generalist policy but was not selected for this slot — see Coverage notes.)_

## 2025 (3 papers)

**[π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/abs/2504.16054)** — arXiv preprint, submitted Apr 22, 2025 · `VLA` · `award: not verified` · `lab: Physical Intelligence`
- *Contribution:* Black, Brown, Darpinian, Dhabalia, Driess, et al. extend π0 with co-training on heterogeneous data (multi-robot demonstrations, high-level semantic prediction, and web data) to target open-world generalization for long-horizon, dexterous mobile-manipulation tasks.
- *Results:* The paper reports π0.5 performing long-horizon tasks such as cleaning entirely new, previously unseen kitchens and bedrooms, which it frames as the first demonstration of this degree of end-to-end learned generalization to new homes.

**[GR00T N1: An Open Foundation Model for Generalist Humanoid Robots](https://arxiv.org/abs/2503.14734)** — arXiv preprint, submitted Mar 18, 2025 · `VLA` · `award: not verified` · `lab: NVIDIA`
- *Contribution:* NVIDIA presents GR00T N1, a dual-system VLA with a vision-language module for scene/instruction understanding and a diffusion-transformer module for real-time motor control, trained on a heterogeneous mix of real-robot trajectories, human videos, and synthetic data.
- *Results:* The paper reports GR00T N1 outperforming imitation-learning baselines on simulation benchmarks across multiple robot embodiments and achieving strong data efficiency on a real Fourier GR-1 humanoid for language-conditioned bimanual manipulation.

**[SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics](https://arxiv.org/abs/2506.01844)** — arXiv preprint, submitted Jun 2, 2025 · `VLA` · `award: not verified` · `lab: Hugging Face / LeRobot`
- *Contribution:* Shukor, Aubakirova, Capuano, et al. build a compact, community-trained VLA designed to be trainable on a single GPU and deployable on consumer-grade hardware or CPUs, releasing all code, pretrained weights, and training data.
- *Results:* The paper reports SmolVLA achieving performance comparable to VLA models roughly 10x larger despite its much smaller size and compute footprint.

## 2026 (5 papers)

**[π0.7: a Steerable Model with Emergent Capabilities](https://www.pi.website/blog/pi07)** — Physical Intelligence blog post, published Apr 16, 2026 · `blog post, not a peer-reviewed paper` · `award: not verified` · `lab: Physical Intelligence`
- *Contribution:* Physical Intelligence describes π0.7 as trained with "diverse context" prompting (language, metadata, and visual subgoals) that specifies not just what to do but how, enabling compositional recombination of learned skills and cross-embodiment transfer with minimal robot-specific data.
- *Results:* The post reports π0.7 matching specialist RL-trained models (π*0.6) on laundry folding, espresso making, and box building, and matching expert human teleoperation on zero-shot laundry folding on an unseen UR5e embodiment, with normalized throughput of 0.9–2.0x versus specialists.

**[Precise Manipulation with Efficient Online RL](https://www.pi.website/research/rlt)** — Physical Intelligence research post, published Mar 19, 2026 · `blog post, not a peer-reviewed paper` · `award: not verified` · `lab: Physical Intelligence`
- *Contribution:* Xu, Springenberg, Equi, Amin, Esmail, Levine, and Ke introduce an "RL token" (RLT) — a compact output interface between a VLA and a lightweight online RL policy — that adapts precise manipulation behaviors from minutes to hours of real-world data without fine-tuning the full VLA.
- *Results:* The post reports RLT speeding up the most precise stages of four manipulation tasks (screwdriver, zip-tie fastening, ethernet insertion, power-cord insertion) by up to 3x, with gains from as little as 15 minutes of real-world data, and on ethernet insertion, half of final policy trials beating the fastest human teleoperated demonstration (median 66 vs. 146 timesteps).

**[VLAs with Long and Short-Term Memory](https://www.pi.website/research/memory)** — Physical Intelligence research post, published Mar 3, 2026 · `blog post, not a peer-reviewed paper` · `award: not verified` · `lab: Physical Intelligence`
- *Contribution:* Physical Intelligence introduces Multi-Scale Embodied Memory (MEM), giving a VLA short-term memory over raw observations (via an interleaved spatial/temporal-attention video encoder) and long-term memory as natural-language task-progress descriptions the model actively updates.
- *Results:* The post reports the memory-augmented π0.6-MEM handling tasks requiring up to ten-plus minutes of memory (e.g. a "swap 3 mugs" task and multi-step kitchen tasks) and substantially outperforming variants without memory or with naive memory.

**[Qwen-VLA: Unifying Vision-Language-Action Modeling across Tasks, Environments, and Robot Embodiments](https://arxiv.org/abs/2605.30280)** — arXiv preprint, submitted May 28, 2026 · `VLA` · `award: not verified` · `lab: Alibaba (Qwen team)`
- *Contribution:* Wang, Bai, et al. build a single unified VLA on the Qwen foundation-model stack that folds manipulation, navigation, and trajectory prediction into one action-and-trajectory prediction framework with embodiment-aware prompt conditioning for cross-embodiment transfer.
- *Results:* The paper reports 97.9% on LIBERO, 73.7% on Simpler-WidowX, 86.1%/87.2% on RoboTwin-Easy/Hard, 69.0% OSR on R2R navigation, 59.6% SR on RxR, 76.9% average OOD success on real-world ALOHA, and 26.6% zero-shot success on the DOMINO dynamic-manipulation benchmark.

**[Isaac GR00T N1.7](https://github.com/NVIDIA/Isaac-GR00T)** — NVIDIA model/software release, GA tagged Apr 18, 2026 · `software release, not a peer-reviewed paper` · `award: not verified` · `lab: NVIDIA`
- *Contribution:* NVIDIA ships GR00T N1.7 as the current generally-available release of its open Isaac GR00T humanoid foundation-model line (following N1.5 and N1.6), continuing the dual-system VLA design introduced in the GR00T N1 paper (arXiv:2503.14734, listed under 2025 above).
- *Results:* The repository's citation still points to the original March-2025 GR00T N1 arXiv preprint; no separate 2026 technical report or new quantitative benchmark numbers for N1.7 were found in the repository README.

## Coverage notes

- **2014 left empty by design.** The only 2014 candidate found (Levine & Abbeel, "Learning Neural Network Policies with Guided Policy Search under Unknown Dynamics," NeurIPS 2014) could not be fetched directly (NeurIPS proceedings page returned a connection error); the WebSearch summary available describes state-based simulated manipulation, not a confirmed vision-to-action pipeline. Per the anti-fabrication rule, an unverifiable/likely-non-visual paper was excluded rather than force-fit. The confirmed vision-from-pixels lineage begins in 2015 with arXiv:1504.00702.
- **2015–2018 lineage:** end-to-end visuomotor policy learning (pixels/monocular images → torques or grasp actions), no language conditioning yet.
- **2019–2021 lineage:** shifts to goal/language-conditioned imitation learning (Play-LMP → language-conditioned imitation → CLIPort), the direct precursor thread RT-1/RT-2 build on.
- **2021 alternative considered:** BC-Z (Jang et al., CoRL 2021) was verified as real but its arXiv posting (2202.02005) is dated Feb 2022, so it was not used for the 2021 slot to avoid a same-year clash under the "one per year" rule; CLIPort's Sept 2021 arXiv date fit cleanly.
- **2022 (RT-1) labelled distinctly** from "precursor (not VLA)" per the task brief's own framing that RT-1 "starts" the paradigm even though the term "VLA" didn't exist until RT-2 (2023) — see the `VLA-paradigm origin` label.
- **2024 alternative considered:** Octo (arXiv:2405.12213, RSS 2024) was verified as a real, contemporaneous 2024 generalist-policy paper; OpenVLA was selected instead because its title and framing explicitly claim the "vision-language-action model" category, matching this file's scope more directly. Octo is noted rather than dropped.
- **2026 slate is 3 blog posts + 2 papers/releases**, matching what was actually available from the labs when fetched: Physical Intelligence currently publishes primarily via its research blog rather than arXiv, so all three PI entries are labelled `blog post, not a peer-reviewed paper` per instruction. Qwen-VLA (Alibaba) is a genuine arXiv preprint. Isaac GR00T N1.7 is a software/model release (GitHub-tagged GA, Apr 18 2026) rather than a new paper; its citation still resolves to the 2025 GR00T N1 arXiv preprint.
- **2026 candidates verified but excluded from the 5-slot "big lab" quota:** (1) "Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines" (arXiv:2604.23001, submitted Apr 24 2026, accepted at TMLR) is a real, peer-reviewed survey, but author affiliation could not be verified as one of the named big labs, so it is cited here as background rather than counted. (2) "Simple-to-Complex Structured Demonstrations for Vision-Language-Action Learning" (arXiv:2607.04591, submitted Jul 6 2026) is real but authored at Hiroshima University, not a big lab on the required list, so it was excluded from the quota.
- **Award claims:** no fetched source for any entry in this file stated a best-paper or other award; every entry is marked `award: not verified` rather than guessed.
- **Lab-affiliation claims (2026 entries):** all `lab:` values above were read directly from the fetched page/paper (blog byline, arXiv author affiliation, or repository owner), not inferred.

## Sources

- https://arxiv.org/abs/1504.00702 — End-to-End Training of Deep Visuomotor Policies
- https://arxiv.org/abs/1603.02199 — Learning Hand-Eye Coordination for Robotic Grasping
- https://arxiv.org/abs/1610.00696 — Deep Visual Foresight for Planning Robot Motion
- https://arxiv.org/abs/1810.03237 — Task-Embedded Control Networks for Few-Shot Imitation Learning
- https://arxiv.org/abs/1903.01973 — Learning Latent Plans from Play
- https://arxiv.org/abs/2005.07648 — Language Conditioned Imitation Learning over Unstructured Data
- https://arxiv.org/abs/2109.12098 — CLIPort: What and Where Pathways for Robotic Manipulation
- https://arxiv.org/abs/2212.06817 — RT-1: Robotics Transformer for Real-World Control at Scale
- https://arxiv.org/abs/2307.15818 — RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control
- https://arxiv.org/abs/2406.09246 — OpenVLA: An Open-Source Vision-Language-Action Model
- https://arxiv.org/abs/2504.16054 — π0.5: a Vision-Language-Action Model with Open-World Generalization
- https://arxiv.org/abs/2503.14734 — GR00T N1: An Open Foundation Model for Generalist Humanoid Robots
- https://arxiv.org/abs/2506.01844 — SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics
- https://arxiv.org/abs/2604.23001 — Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines (background only, not counted in quota)
- https://arxiv.org/abs/2605.30280 — Qwen-VLA: Unifying Vision-Language-Action Modeling across Tasks, Environments, and Robot Embodiments
- https://arxiv.org/html/2607.04591 — Simple-to-Complex Structured Demonstrations for VLA (verified, excluded — non-big-lab affiliation)
- https://www.pi.website/blog — Physical Intelligence blog index (used to confirm post titles/dates/URLs)
- https://www.pi.website/blog/pi07 — π0.7: a Steerable Model with Emergent Capabilities
- https://www.pi.website/research/rlt — Precise Manipulation with Efficient Online RL
- https://www.pi.website/research/memory — VLAs with Long and Short-Term Memory
- https://developer.nvidia.com/isaac/gr00t — Isaac GR00T product page
- https://github.com/NVIDIA/Isaac-GR00T — Isaac GR00T N1.7 repository/release notes
- (attempted, failed to load) https://proceedings.neurips.cc/paper_files/paper/2014/hash/c7c9344b5a3c0533e29fa69ce807cf08-Abstract.html — 2014 GPS paper, used only to explain the empty 2014 slot
