# Reinforcement Learning for Robotics

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Award status is asserted only where a fetched page confirms it.

## What this is

Reinforcement learning (RL) for robotics trains a control policy against a reward signal obtained through trial-and-error interaction with an environment (simulated or real), rather than purely by imitating labeled demonstrations. It is the main lever for discovering behavior that goes *beyond* what any demonstration set contains — contact-rich dexterity, recovery from failure, and skills that are hard to teleoperate — at the cost of being higher-variance and more sample-hungry than supervised approaches. The field spans model-based methods that fit local dynamics models (guided policy search, optimal control), model-free policy-gradient/Q-learning methods trained at scale in simulation or the real world, and, more recently, RL used to fine-tune large pretrained vision-language-action (VLA) policies.

**Relationship to the skills library:** for VLA-specific RL fine-tuning recipes the loop actually executes, `skills/iterated/reinforcing-with-rl/SKILL.md` is the source of truth; this file is background reading.

## Classic papers (2014–2024, one per year)

### 2014
**[Learning Neural Network Policies with Guided Policy Search under Unknown Dynamics](https://neurips.cc/virtual/2014/poster/4462)** — NeurIPS 2014 · `award: not verified`
- *Contribution:* Introduces guided policy search with iteratively-refitted time-varying linear dynamics models to train general neural-network control policies without requiring a known global dynamics model.
- *Results:* Demonstrated on simulated robotic manipulation with contact discontinuities and underactuation, showing the method trains neural-network policies in regimes where prior purely model-free approaches struggle (no single headline number stated in the abstract).

### 2015
**[Learning Contact-Rich Manipulation Skills with Guided Policy Search](https://arxiv.org/abs/1501.05611)** — ICRA 2015 · `award: not verified`
- *Contribution:* Extends guided policy search to real-robot contact-rich manipulation, fitting iteratively-refitted time-varying linear models into trajectories that are then unified into one generalizing policy.
- *Results:* Learned "fast, fluent behaviors after only minutes of interaction time" on real-robot assembly tasks (toy-airplane assembly, tight-fitting lego stacking, ring-on-peg placement, shoe-tree insertion, bottle-cap screwing) with no pre-programmed dynamics model.

### 2016
**[Optimal Control with Learned Local Models: Application to Dexterous Manipulation](https://www.ieee-ras.org/about-ras/latest-news/icra-2016-award-recipients-announced)** — ICRA 2016 · `award: IEEE ICRA Best Paper Award on Robot Manipulation and Locomotion`
- *Contribution:* Model-based RL / adaptive optimal control that learns dexterous manipulation on a 24-DoF pneumatically-actuated Adroit hand by iteratively refitting time-varying linear models, controlling directly at the pneumatic-valve level with no prior actuation model.
- *Results:* Sample-efficient learning (~60 trials) of contact-rich, under-actuated tasks (e.g. clockwise object rotation) over a 100-dimensional state space and 40-dimensional valve-command control space.

### 2017
**[Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World](https://arxiv.org/abs/1703.06907)** — IROS 2017 · `award: not verified`
- *Contribution:* Introduces domain randomization — randomizing simulator textures, lighting, and camera parameters — to train object-localization/control networks purely in simulation that transfer to the real world.
- *Results:* Achieved real-world object-localization accuracy to roughly 1.5cm and demonstrated grasping in cluttered scenes using only simulated RGB images, which the authors describe as the first such zero-shot sim-to-real transfer for robotic control.

### 2018
**[QT-Opt: Scalable Deep Reinforcement Learning for Vision-Based Robotic Manipulation](https://arxiv.org/abs/1806.10293)** — CoRL 2018 · `award: CoRL 2018 Best Systems Paper Award (one of two co-winners)`
- *Contribution:* A scalable, self-supervised deep RL framework (QT-Opt) that trains a large closed-loop Q-function for vision-based robotic grasping from real-world trial and error.
- *Results:* Trained on over 580,000 real-world grasp attempts with a 1.2M-parameter Q-function, reaching 96% grasp success on unseen objects while learning regrasping, object probing, and non-prehensile behaviors from RGB input alone.

### 2019
**[Dexterous Manipulation with Deep Reinforcement Learning: Efficient, General, and Low-Cost](https://arxiv.org/abs/1810.06045)** — ICRA · `award: not verified`
- *Contribution:* Shows model-free deep RL can learn contact-rich, multi-fingered dexterous-hand manipulation directly through real-world interaction, with no simulation or task-specific models.
- *Results:* Learned diverse manipulation behaviors from scratch in about 4–7 hours per task on two low-cost hardware hand platforms, with a small number of human demonstrations cutting this to 2–3 hours.

### 2020
**[Learning Agile Robotic Locomotion Skills by Imitating Animals](https://arxiv.org/abs/2004.00784)** — RSS 2020 · `award: RSS 2020 Best Paper Award`
- *Contribution:* An imitation-driven RL pipeline that trains legged robots to reproduce diverse agile motions by tracking reference motion data captured from real animals, with domain-adaptation techniques for sim-to-real transfer.
- *Results:* Deployed on an 18-DoF quadruped robot, synthesizing controllers for a range of agile behaviors — varied locomotion gaits, dynamic hops, and turns — from real-animal reference clips alone.

### 2021
**[A System for General In-Hand Object Re-Orientation](https://arxiv.org/abs/2111.03043)** — CoRL 2021 · `award: CoRL 2021 Best Paper Award`
- *Contribution:* A simple model-free RL framework for general in-hand object reorientation, working with the hand facing both upward and downward, distilled to use only observations available in the real world.
- *Results:* Reoriented over 2,000 geometrically different simulated objects with strong zero-shot transfer to new objects, and demonstrated real-world operation via observation distillation.

### 2022
**[Training Robots to Evaluate Robots: Example-Based Interactive Reward Functions for Policy Learning](https://arxiv.org/abs/2212.08961)** — CoRL 2022 · `award: CoRL 2022 Best Paper Award`
- *Contribution:* Trains robots to perform interactive evaluation behaviors — "interactive reward functions" (IRFs) — from only examples of successful outcomes, and uses these learned evaluators as reward signals for RL policy training, avoiding hand-engineered rewards.
- *Results:* Across door locking and weighted block stacking (simulation) and screw tightening (real robot), IRF-trained policies achieved large performance gains, outperforming baselines that had access to either demonstrations or carefully engineered rewards (exact success-rate figures not stated in the fetched abstract).

### 2023
**[Demonstrating A Walk in the Park: Learning to Walk in 20 Minutes With Model-Free Reinforcement Learning](https://arxiv.org/abs/2208.07860)** — RSS 2023 (confirmed accepted paper, [program listing](https://roboticsconference.org/2023/program/papers/)) · `award: not verified`
- *Contribution:* Combines recent sample-efficient off-policy RL with careful real-world controller and reward tuning so a legged robot can learn to walk entirely from scratch with no simulation pretraining.
- *Results:* Learned a consistent walking gait across multiple challenging indoor and outdoor terrains within about 20 minutes of real-world training time.

### 2024
**[PoliFormer: Scaling On-Policy RL with Transformers Results in Masterful Navigators](https://arxiv.org/abs/2406.20083)** — CoRL 2024 · `award: CoRL 2024 Outstanding Paper Award`
- *Contribution:* Scales on-policy RL (PPO-style) training of an RGB-only navigation policy — a foundational vision-transformer encoder plus a causal transformer decoder for long-horizon memory — trained purely in simulation via massively parallelized rollouts.
- *Results:* Reached an 85.5% success rate on the CHORES-S object-goal-navigation benchmark, a 28.5-percentage-point absolute improvement over prior work, and generalized zero-shot to the real world across two robot embodiments (LoCoBot, Stretch RE-1) with no real-world adaptation.

## 2025 (3 papers)

**[Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning](https://arxiv.org/abs/2410.21845)** (HIL-SERL) — Science Robotics 2025 ([DOI](https://doi.org/10.1126/scirobotics.ads5033)) · `award: not verified` · `lab: UC Berkeley`
- *Contribution:* A human-in-the-loop, vision-based RL system combining demonstrations, live human corrective interventions, and an efficient off-policy RL algorithm to train precise, dexterous real-world manipulation policies.
- *Results:* Reached near-perfect success rates within 1–2.5 hours of real-world training — roughly 2x the success rate and 1.8x faster execution than imitation-learning and prior RL baselines — across dynamic manipulation, precision-assembly, and dual-arm tasks.

**[Learning Humanoid Standing-up Control across Diverse Postures](https://arxiv.org/abs/2502.08378)** (HoST) — RSS 2025, Best Systems Paper Finalist · `award: RSS 2025 Best Systems Paper Award — finalist, not confirmed winner` · `lab: Shanghai AI Lab / SJTU (InternRobotics)`
- *Contribution:* A multi-critic, curriculum-based RL framework (HoST) that trains a humanoid to stand up from diverse fallen postures across varied simulated terrains, with constraints built in for safe real-world deployment.
- *Results:* Reached 99.5% simulated success on ground terrain (vs. 0% for a single-critic ablation baseline) and 100% real-world success (20/20 episodes) across four lab terrain types on a Unitree G1, plus robust standing-up on outdoor grass, wood, and stone surfaces and under a 12kg payload.

**[ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills](https://arxiv.org/abs/2502.01143)** — RSS 2025 ([project page](https://agile.human2humanoid.com/)) · `award: not verified` · `lab: Carnegie Mellon University / NVIDIA`
- *Contribution:* A two-stage sim-to-real framework that pretrains humanoid whole-body motion-tracking policies in simulation from retargeted human motion, then learns a real-world "delta action" model that corrects sim-to-real dynamics mismatch and refines the policy against this corrected simulator.
- *Results:* Enabled agile Unitree G1 skills — forward jumps up to 1.5m, side jumps up to 1.3m, kicks, and dance moves — while reducing tracking error compared to system-identification, domain-randomization, and delta-dynamics-learning baselines across three sim-to-real transfer settings.

## 2026 (5 papers)

**[Beyond Action Residuals: Real-World Robot Policy Steering via Bottleneck Latent Reinforcement Learning](https://arxiv.org/abs/2605.19919)** — arXiv, May 2026 · `award: not verified` · `lab: Tsinghua University (IIIS)`, co-authors from HKU, Shanghai Qi Zhi Institute, SJTU, and CASIA
- *Contribution:* Z-Perturbation RL (ZPRL) steers a frozen, pretrained flow-matching policy through RL-optimized perturbations of a compact variational-information-bottleneck latent, instead of perturbing the raw action space.
- *Results:* Improved average real-world success rate by 33.7% over imitation-learning base policies across four real-world manipulation tasks (plus eight simulation tasks), with better sample efficiency than baselines that perturb actions directly.

**[Failure-Aware RL: Reliable Offline-to-Online Reinforcement Learning with Self-Recovery for Real-World Manipulation](https://arxiv.org/abs/2601.07821)** — arXiv, Jan 2026 · `award: not verified` · `lab: Tsinghua University (IIIS)`, co-authors from Shanghai Qi Zhi Institute, SJTU, NTU, A*STAR I2R, and University of Maryland
- *Contribution:* FARL combines offline-to-online RL with a world-model-based safety critic and an offline-trained recovery policy to reduce human interventions caused by unsafe real-world exploration, evaluated on a new FailureBench benchmark.
- *Results:* Reduced intervention-requiring failures by 73.1% while improving average task performance by 11.3% during real-world RL post-training, relative to baselines without failure-aware recovery.

**[ViVa: A Video-Generative Value Model for Robot Reinforcement Learning](https://arxiv.org/abs/2604.08168)** — arXiv, Apr 2026 · `award: not verified` · `lab: GigaAI`, co-authors from Tsinghua University and Sichuan University
- *Contribution:* Repurposes a pretrained video generator's spatiotemporal priors into a value model that jointly predicts future proprioception and a scalar state value, used to guide/re-rank a VLA policy (RECAP) for robot RL.
- *Results:* On a real-world box-assembly task, RECAP+ViVa reached 73% success at 14 tasks/hour, versus 42% for π0.5, 53% for Gigabrain-0, and 58% for a VLM-based reranker baseline.

**[EXPO-FT: Sample-Efficient Reinforcement Learning Finetuning for Vision-Language-Action Models](https://arxiv.org/abs/2605.25477)** — arXiv, May 2026 · `award: not verified` · `lab: Stanford University`
- *Contribution:* A sample-efficient RL finetuning method for pretrained VLA policies (π0.5) that combines human-in-the-loop interventions with temporally-extended action handling for stable online RL finetuning.
- *Results:* Reached perfect 30/30 success across all evaluated real-robot tasks (egg flip, flower insert, pool shot, cube pick, string-light routing, candy scoop) after an average of just 19.1 minutes of online robot data, beating HG-DAgger (20.5/30), supervised finetuning (18.8/30), DSRL (19/30), and HIL-SERL (5.5/30) baselines.

**[FlowDPG: Deterministic Policy Gradient on Flow Matching Policies for Real-World Manipulation](https://arxiv.org/abs/2606.22303)** — arXiv, June 2026 · `award: not verified` · `lab: Carnegie Mellon University`, co-authors from University of Pennsylvania and Skild AI
- *Contribution:* A DDPG-style policy-gradient method for flow-matching policies that distills a learned critic's gradient directly into the policy's velocity field, avoiding the prohibitive backpropagation-through-time needed to differentiate through the multi-step ODE sampler.
- *Results:* Reached a 92% end-to-end success rate on a real-world, long-horizon, dual-arm AirPods assembly task, outperforming other recent RL approaches for flow/diffusion policies (value-conditioning, auxiliary-module adaptation, adjoint-based critic-gradient methods).

## Coverage notes

- **2014:** No RL-focused best-paper winner was found at ICRA, IROS, or RSS for 2014. Per the directly-fetched RSS Foundation award page, RSS's Outstanding Paper Award was first given in 2015 (no 2014 winner exists), and CoRL did not yet exist (est. 2017). The entry used instead — Levine & Abbeel, NeurIPS 2014 — is the foundational guided-policy-search paper that the confirmed 2015 ICRA and 2016 ICRA-award-winning entries directly build on, so it was picked as most representative despite not being from one of the four preferred venues.
- **2015, 2017, 2019, 2023:** highly-cited, representative papers from ICRA/IROS/RSS, but no best-paper award could be confirmed for these specific papers within the research budget; each is marked `award: not verified` rather than asserted. Directly fetching `roboticsfoundation.org/awards/best-paper-award/` (2014–2024) confirmed none of RSS's Outstanding-Paper-Award winners in that window is an RL paper, so several RSS-associated picks above are not RSS-award winners, just RSS-accepted RL papers.
- **RSS 2020 best paper:** the official RSS Foundation and `roboticsconference.org/2020/program/awards/` pages only show 2020 nominees / list the year as "TBA"; the award itself is confirmed instead via the authors' own project page (`xbpeng.github.io`), which explicitly states "Robotics: Science and Systems (RSS 2020) Best Paper Award."
- **HoST (2025):** listed by its own GitHub repo as an "RSS 2025 Best Systems Paper Finalist" — finalist status, not a confirmed win; recorded conservatively.
- **2026 venue reality:** see the index's [Known limitations](../knowledge_index.md#known-limitations) for full ICRA/RSS/IROS/CoRL 2026 status. Consequently all 5 "2026" entries above are arXiv preprints (Jan–Jun 2026), not conference-awarded papers; every `award:` field for 2026 is `not verified` by construction.
- **2026 tool budget:** this session's shared `WebSearch` quota (pooled across nine parallel sibling researchers writing other category files) was exhausted partway through this category's research. All research for the 2025/2026 sections and several classic-paper verifications after that point used `WebFetch` against arXiv abstract pages, the `ar5iv` HTML mirror, `export.arxiv.org`'s API, and the Semantic Scholar API instead — all still live-fetched, none from prior knowledge.
- **2026 lab clustering:** 3 of 5 2026 picks are Tsinghua University (IIIS)-affiliated. This reflects which real-world-RL papers had affiliations confirmable via a directly-fetched page within the tool budget (`ar5iv` mirrors show author affiliations more reliably than arXiv abstract pages, which frequently omit them) — not a claim that Tsinghua dominates 2026 robot RL. Candidate papers from NVIDIA (CHORD, arXiv 2607.00033) and DeepMind were found but dropped because no fetched page confirmed their institutional affiliation, per the anti-fabrication rule.
- **Excluded as not RL-core:** ASPIRE (arXiv 2607.00272, code-as-policy + evolutionary search, no RL) and RoboTTT (arXiv 2607.15275, test-time-training/supervised, no RL) were investigated as NVIDIA/Stanford 2026 candidates but excluded once their fetched abstracts confirmed they do not use reinforcement learning as a core method.

## Sources

- https://roboticsfoundation.org/awards/best-paper-award/
- https://roboticsfoundation.org/awards/best-systems-paper-award/
- https://2018.corl.org/
- https://2021.corl.org/program/awards_2021
- https://2024.corl.org/program/awards
- https://2025.corl.org/program/awards
- https://roboticsconference.org/2020/program/awards/index.html
- https://roboticsconference.org/2023/program/papers/
- https://www.ieee-ras.org/about-ras/latest-news/icra-2016-award-recipients-announced
- https://xbpeng.github.io/projects/Robotic_Imitation/index.html
- https://neurips.cc/virtual/2014/poster/4462
- https://docslib.org/doc/8696854/optimal-control-with-learned-local-models-application-to-dexterous-manipulation
- https://www.roboti.us/lab/papers/KumarICRA16.pdf
- https://arxiv.org/abs/1501.05611
- https://arxiv.org/abs/1703.06907
- https://arxiv.org/abs/1806.10293
- https://arxiv.org/abs/1810.06045
- https://arxiv.org/abs/2004.00784
- https://arxiv.org/abs/2111.03043
- https://arxiv.org/abs/2212.08961
- https://arxiv.org/abs/2208.07860
- https://arxiv.org/abs/2406.20083
- https://arxiv.org/abs/2410.21845
- https://arxiv.org/abs/2502.08378
- https://ar5iv.labs.arxiv.org/html/2502.08378
- https://agile.human2humanoid.com/
- https://arxiv.org/abs/2502.01143
- https://ar5iv.labs.arxiv.org/html/2605.19919
- https://ar5iv.labs.arxiv.org/html/2601.07821
- https://ar5iv.labs.arxiv.org/html/2604.08168
- https://ar5iv.labs.arxiv.org/html/2605.25477
- https://ar5iv.labs.arxiv.org/html/2606.22303
- https://arxiv.org/abs/2605.19919
- https://arxiv.org/abs/2601.07821
- https://arxiv.org/abs/2604.08168
- https://arxiv.org/abs/2605.25477
- https://arxiv.org/abs/2606.22303
- https://arxiv.org/abs/2607.00033 (CHORD — investigated, excluded: affiliation unconfirmed)
- https://arxiv.org/abs/2607.00272 (ASPIRE — investigated, excluded: not RL-core)
- https://arxiv.org/abs/2607.15275 (RoboTTT — investigated, excluded: not RL-core)
- https://arxiv.org/abs/2606.31958 (Semantic RL, UC Berkeley — investigated, excluded: no quantified results found)
- https://api.semanticscholar.org/graph/v1/paper/arXiv:1810.06045 (venue confirmation)
- http://export.arxiv.org/api/query (used repeatedly for author/title discovery: Levine & Abbeel 2014, Kumar/Todorov/Levine 2016 PDF link, Chelsea Finn 2026 listing, Linxi Fan 2026 listing, Sergey Levine 2026 listing, Deepak Pathak 2026 listing)
