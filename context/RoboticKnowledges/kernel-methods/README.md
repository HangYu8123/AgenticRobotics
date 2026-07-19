# Kernel Methods for Robotics

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Award status is asserted only where a fetched page confirms it.
> **Scope caveat:** kernel/GP methods are rarely flagship-conference best papers — they land in journals (IJRR, T-RO, T-CST) or general-ML/control venues (ICML, NeurIPS, ECC, CDC) instead of winning ICRA/IROS/RSS/CoRL best-paper awards. The best-paper preference used by other categories in this knowledge base is **deliberately dropped** for this file; entries below are the most representative *accepted* paper per year regardless of award status. See Coverage notes.
> † marks entries where only title/venue/authors/DOI could be verified (abstract text was blocked by a paywall or JS-only renderer); the contribution/results text for those is a conservative paraphrase of the verified title, not a quote from verified abstract content.

## What this is

Kernel methods place a positive-definite kernel function — an implicit inner product in a (possibly infinite-dimensional) reproducing kernel Hilbert space (RKHS) — at the center of learning, letting linear algorithms fit nonlinear functions without an explicit feature map. In robotics the dominant instance is the Gaussian process (GP): a distribution over functions defined by a kernel (covariance function) that gives GP regression and classification calibrated, closed-form predictive uncertainty, which is why GPs are used for data-efficient dynamics/inverse-dynamics models, model-based control (GP-MPC), and Bayesian optimization for tuning controllers and policies from few real-world trials. Related kernel machinery in robotics includes kernelized movement primitives (trajectory representations via the kernel trick instead of fixed basis functions), the GP latent variable model (GP-LVM) for low-dimensional motion manifolds, sparse/inducing-point GP approximations for scaling beyond the cubic cost of exact GP inference, and kernel two-sample tests (MMD) for distribution comparison. Kernel/GP methods remain preferred over deep networks specifically in the low-data, safety-critical, and uncertainty-quantification regime — e.g. safe learning-based control with high-probability guarantees — where a deep net's point predictions and poorly calibrated uncertainty are a liability.

## Classic papers (2014–2024, one per year)

### 2014
**[Bayesian Gait Optimization for Bipedal Locomotion](https://doi.org/10.1007/978-3-319-09584-4_25)** — LION (Learning and Intelligent Optimization) 2014 · `award: not verified` †
- *Contribution:* Applies Bayesian optimization with a Gaussian-process surrogate to automatically search bipedal-gait/controller parameters in place of hand-tuning.
- *Results:* The LION 2014 paper (Calandra, Gopalan, Seyfarth, Peters, Deisenroth) introduces the method on gait-parameter tuning; the group's 2016 journal extension in *Annals of Mathematics and Artificial Intelligence* ([DOI](https://doi.org/10.1007/s10472-015-9463-9)) later validated the same approach on a real dynamic bipedal walker, finding good gaits in few trials.

### 2015
**[Safe and Robust Learning Control with Gaussian Processes](https://doi.org/10.1109/ECC.2015.7330913)** — ECC 2015 · `award: not verified` †
- *Contribution:* Combines a Gaussian-process model of system/model uncertainty with robust-control-style analysis to give high-probability safety guarantees for controllers that are improved from data (Berkenkamp & Schoellig).
- *Results:* Establishes the safe-learning-control template later built on directly by Koller et al.'s learning-based MPC line of work (see 2018 entry); full experimental detail was not retrievable from accessible metadata (IEEE Xplore abstract not text-accessible during compilation).

### 2016
**[Automatic LQR Tuning Based on Gaussian Process Global Optimization](https://arxiv.org/abs/1605.01950)** — ICRA 2016 · `award: not verified`
- *Contribution:* Marco, Hennig, Bohg, Schaal, and Trimpe use Entropy Search — a Bayesian-optimization algorithm that models the cost as a GP and maximizes information gain per trial — to automatically retune LQR gains from experimental data.
- *Results:* On a 7-DoF robot arm balancing an inverted pole (2D and 4D gain-tuning scenarios), the method reaches improved controllers using fewer real experimental evaluations than compared alternatives.

### 2017
**[Virtual vs. Real: Trading Off Simulations and Physical Experiments in Reinforcement Learning with Bayesian Optimization](https://arxiv.org/abs/1703.01250)** — ICRA 2017 · `award: not verified`
- *Contribution:* Marco, Berkenkamp, Hennig, Schoellig, Krause, Schaal, and Trimpe extend Entropy Search to multiple information sources, giving a principled way to combine cheap/inaccurate simulation data with expensive/accurate physical trials.
- *Results:* On a cart-pole system, the multi-fidelity approach finds good control policies using fewer physical experiments than standard single-source Bayesian optimization run on the real system alone.

### 2018
**[Learning-Based Model Predictive Control for Safe Exploration](https://doi.org/10.1109/CDC.2018.8619572)** — CDC 2018 · `award: not verified`
- *Contribution:* Koller, Berkenkamp, Turchetta, and Krause build GP-based, input-dependent confidence intervals over predicted trajectories and combine them with terminal-set constraints in an MPC loop, giving provable high-probability safety during learning-based exploration.
- *Results:* Demonstrated on safely learning pendulum dynamics and on a constrained cart-pole reinforcement-learning task, keeping trajectories within safety constraints throughout learning (extended version: [arXiv:1906.12189](https://arxiv.org/abs/1906.12189); original arXiv preprint [1803.08287](https://arxiv.org/abs/1803.08287)).

### 2019
**[Kernelized Movement Primitives](https://doi.org/10.1177/0278364919846363)** — IJRR 2019 · `award: not verified`
- *Contribution:* Huang, Rozo, Silvério, and Caldwell reformulate movement primitives using the kernel trick instead of fixed basis functions, letting the robot adapt learned motor skills and satisfy additional task constraints while handling high-dimensional inputs with fewer open parameters.
- *Results:* Demonstrated on trajectory-modulation and adaptation examples with extrapolation beyond the demonstrated data, establishing KMP as a standard reference point for kernel-based learning-from-demonstration in robotics.

### 2020
**[Sample-Efficient Robot Motion Learning using Gaussian Process Latent Variable Models](https://doi.org/10.1109/ICRA40945.2020.9196658)** — ICRA 2020 · `award: not verified`
- *Contribution:* Delgado-Guerrero, Colomé, and Torras adapt the GP-LVM to build a low-dimensional latent space over movement-primitive parameters, then use that latent model together with observed rewards to build a surrogate reward model for policy search.
- *Results:* The GP-LVM latent space can be flexibly resized without losing much information, improving the sample efficiency of policy-search refinement of kinesthetically-taught robot motions relative to optimizing directly in the original parameter space.

### 2021
**[Learning Terrain Dynamics: A Gaussian Process Modeling and Optimal Control Adaptation Framework Applied to Robotic Jumping](https://doi.org/10.1109/TCST.2020.3009636)** — IEEE Transactions on Control Systems Technology, 29(4), 2021 · `award: not verified` †
- *Contribution:* Chang, Hubicki, Aguilar, Goldman, Ames, and Vela fit a Gaussian-process model of terrain-contact dynamics and couple it with an optimal-control adaptation framework so a legged/jumping robot can adjust online to varying terrain.
- *Results:* The framework is applied to and validated on a robotic jumping platform, as named in the title; granular numeric results were not retrievable from accessible metadata (Crossref/IEEE abstract text not accessible during compilation).

### 2022
**[Model Predictive Control with Gaussian Processes for Flexible Multi-Modal Physical Human Robot Interaction](https://arxiv.org/abs/2110.12433)** — ICRA 2022 · `award: not verified`
- *Contribution:* Haninger, Hegeler, and Peternel build a GP-based MPC that reasons over multiple interaction modes (e.g. contact vs. free motion) so a robot's impedance/trajectory can adapt to a human partner's belief/intent during physical interaction.
- *Results:* The controller optimizes robot trajectory and impedance conditioned on a belief over human intent across interaction modes, improving flexibility of physical human-robot interaction relative to single-mode GP-MPC baselines.

### 2023
**[Gaussian-Process-Based Control of Underactuated Balance Robots With Guaranteed Performance](https://doi.org/10.1109/TRO.2022.3203625)** — IEEE Transactions on Robotics, 39(1), 2023 · `award: not verified` †
- *Contribution:* Chen, Yi, and Song design a GP-based feedback control scheme for underactuated balance robots that comes with theoretical (guaranteed) tracking/stability performance rather than only empirical tuning.
- *Results:* The approach targets underactuated balance-robot control with formal performance guarantees, as named in the title; detailed quantitative results were not retrievable from accessible metadata (IEEE abstract text not accessible during compilation) — the paper has accumulated 30 citations per its Crossref record.

### 2024
**[Active Preference-Based Gaussian Process Regression for Reward Learning and Optimization](https://doi.org/10.1177/02783649231208729)** — IJRR 43(5):665–684, 2024 (Stanford University; first available online 2023) · `award: not verified`
- *Contribution:* Bıyık, Huynh, Kochenderfer, and Sadigh use GP regression over human pairwise-comparison feedback (rather than demonstrations or hand-specified reward models) plus active querying to efficiently learn expressive robot reward functions.
- *Results:* Across simulations and user studies, the active preference-based GP approach outperforms existing baselines at learning expressive reward functions and at optimizing trajectories in a data-efficient way, i.e. with fewer human queries.

## 2025 (3 papers)

**[Active Training Data Selection for Gaussian Process-based Robot Dynamics Learning and Control](https://doi.org/10.1109/IROS60139.2025.11246109)** — IROS 2025 · `award: not verified` †
- *Contribution:* Han, Huang, and Yi propose an active (informative) data-selection strategy for choosing which training points to collect when fitting GP dynamics models used in robot control, instead of passive/random data collection.
- *Results:* The paper targets improved GP dynamics-model quality and downstream control performance for a fixed data-collection budget, per its IROS 2025 proceedings listing; specific numeric comparisons were not retrievable from accessible metadata during compilation.

**[The Unreasonable Effectiveness of Discrete-Time Gaussian Process Mixtures for Robot Policy Learning](https://arxiv.org/abs/2505.03296)** — arXiv preprint, submitted to IEEE Transactions on Robotics (University of Freiburg), May 2025 · `award: not verified`
- *Contribution:* von Hartz, Röfer, Boedecker, and Valada introduce MiDiGap, a mixture-of-discrete-time-Gaussian-Processes representation for imitation-learned manipulation policies, trainable from as few as five camera-only demonstrations in under a minute of CPU time.
- *Results:* Reports a 76-percentage-point higher success rate and 67% lower trajectory cost on constrained manipulation tasks, a 48-point success-rate gain with 20x better sample efficiency on multimodal tasks, and more than doubled success rates under cross-embodiment transfer, plus inference-time obstacle-avoidance steering.

**[Robot Impedance Iterative Learning With Sparse Online Gaussian Process](https://doi.org/10.1109/JAS.2025.125195)** — IEEE/CAA Journal of Automatica Sinica, 12(11):2218–2227, 2025 · `award: not verified` †
- *Contribution:* Pan, Shi, Li, Xu, and Ahn propose an iterative-learning control scheme for robot impedance/interaction tasks that incorporates a sparse online GP to keep the GP model computationally tractable while adapting impedance parameters online.
- *Results:* The sparse-online-GP formulation is presented as improving learning-convergence speed and generalization for robot impedance/interaction control relative to standard (non-sparse) online-GP variants; detailed quantitative comparisons were not retrievable from accessible metadata during compilation.

## 2026 (0 of 5 big-lab slots filled)

**No entries could be verified against the "big lab" requirement (Stanford, UC Berkeley, CMU, MIT, Tsinghua, Alibaba, NVIDIA, Google, DeepMind) — 0 of 5 slots filled.** Per the anti-fabrication rules, this is reported explicitly rather than padded.

What was checked: DBLP author-level searches for known kernel/GP-in-robotics researchers plausibly at these labs (Byron Boots, Dorsa Sadigh, Marco Pavone, Chelsea Finn, Anca Dragan) turned up no 2025/2026 kernel-methods publications for them; DBLP keyword searches combining lab names with "Gaussian process"/"kernel"/"robot"/2026 returned no matches; the Semantic Scholar and arXiv APIs rate-limited (HTTP 429/503) partway through the session, and the WebSearch tool budget was exhausted mid-task, both cutting off further discovery avenues. Genuine 2026 kernel/GP-robotics papers *do* exist but from labs outside the required list — found via DBLP and cited here for transparency only, **not counted toward the 5 required slots**:
- Haque, Sukkar, Sujipto, Le Gentil, Carmichael, Vidal-Calleja, "Towards Robot Skill Learning and Adaptation with Gaussian Processes," [arXiv:2603.01480](https://arxiv.org/abs/2603.01480) — University of Technology Sydney.
- Salunkhe & Kontoudis, "Federated Gaussian Process Learning via Pseudo-Representations for Large-Scale Multi-Robot Systems," [arXiv:2602.12243](https://arxiv.org/abs/2602.12243).
- Evangelisti, Della Santina, Hirche, "Exponentially Stable Projector-Based Control of Lagrangian Systems With Gaussian Processes," IEEE Trans. Automatic Control 71(7):4435–4449, 2026, [DOI](https://doi.org/10.1109/TAC.2026.3662545) — TU Munich (arXiv preprint 2024: [2406.03224](https://arxiv.org/abs/2406.03224)).
- Lederer, Umlauft, Hirche, "Episodic Gaussian Process-Based Learning Control with Vanishing Tracking Errors," IEEE Trans. Automatic Control 71(2):962–977, 2026 — TU Munich (arXiv preprint 2023: [2307.04415](https://arxiv.org/abs/2307.04415)).

Per the index's [Known limitations](../knowledge_index.md#known-limitations) (2026 venue status), 2026 coverage for this category is necessarily limited to arXiv preprints and journal-ahead-of-print items, which is what the search surfaced (none from the required labs).

## Coverage notes

- **Deviation from best-paper preference (deliberate, category-specific):** kernel/GP methods in robotics have continuous but thin yearly output and are essentially never ICRA/IROS/RSS/CoRL best-paper winners — this work lands in journals (IJRR, T-RO, T-CST) or general-ML/control venues (ICML, NeurIPS, ECC, CDC) instead. Accordingly the "prefer best paper from ICRA/IROS/RSS/CoRL" rule used elsewhere in this knowledge base is dropped for this file; the most-cited/representative *accepted* paper per year was selected instead, with IJRR/T-RO/T-CST/ICRA/CDC/ECC all treated as acceptable venues.
- **Spelling note:** the original request spelled this category "kernal methods"; the folder and this file use the correct spelling, `kernel-methods`.
- **Research-process note:** early in this task the WebSearch tool's session budget was exhausted (this file was one of ten parallel category files being researched in the same session), so roughly two-thirds of verification for this file was done via WebFetch against DBLP, Crossref (`api.crossref.org`), arXiv abstract pages, and direct DOI resolution rather than further WebSearch queries. The Semantic Scholar Graph API and the arXiv Atom API both intermittently returned HTTP 429/503 during this session; where they did respond they are cited below and used.
- **† entries:** for the entries marked † in the sections above (2014, 2015, 2021, 2023, and two of the three 2025 entries), only title/authors/venue/year/DOI could be verified — the abstract text itself was blocked by a paywall or a JavaScript-rendered page (IEEE Xplore, ResearchGate, Springer authwall all returned 403/empty content to WebFetch). Their contribution/results text is a conservative paraphrase of the verified title and any partial metadata found, not a quote from verified abstract content, and contains no invented statistics.
- **Award and lab-affiliation claims:** no fetched source for any entry in this file stated a best-paper/award designation, so every entry carries `award: not verified`; no 2026 entry carries a `lab:` tag because no 2026 entry from the required lab list could be verified (see 2026 section above for what was checked and why).

## Sources

- https://doi.org/10.1007/978-3-319-09584-4_25 (Calandra et al., LION 2014, via Crossref + DBLP)
- https://link.springer.com/article/10.1007/s10472-015-9463-9 (Calandra et al., AMAI 2016 journal extension)
- https://doi.org/10.1109/ECC.2015.7330913 (Berkenkamp & Schoellig, ECC 2015, via Crossref + DBLP)
- https://robotics.caltech.edu/wiki/images/2/22/SafeRobustLearningControlwithGPs.pdf (Berkenkamp & Schoellig PDF, fetched but not text-extractable)
- https://arxiv.org/abs/1605.01950 (Marco et al., ICRA 2016)
- https://doi.org/10.1109/ICRA.2016.7487144 (Marco et al., ICRA 2016 DOI, via DBLP)
- https://arxiv.org/abs/1703.01250 (Marco et al., ICRA 2017)
- https://doi.org/10.1109/ICRA.2017.7989186 (Marco et al., ICRA 2017 DOI, via DBLP)
- https://arxiv.org/abs/1803.08287 and https://arxiv.org/abs/1906.12189 (Koller et al., CDC 2018 / extended version)
- https://doi.org/10.1109/CDC.2018.8619572 (Koller et al., CDC 2018 DOI, via DBLP)
- https://doi.org/10.1177/0278364919846363 (Huang, Rozo, Silvério, Caldwell, KMP, IJRR 2019, via Crossref)
- https://doi.org/10.1109/ICRA40945.2020.9196658 (Delgado-Guerrero et al., ICRA 2020, via DBLP + Crossref)
- https://scispace.com/papers/sample-efficient-robot-motion-learning-using-gaussian-12dirxmiyc (GP-LVM ICRA 2020 summary)
- https://doi.org/10.1109/TCST.2020.3009636 (Chang et al., T-CST 2021, via DBLP + Crossref)
- https://arxiv.org/abs/2110.12433 (Haninger, Hegeler, Peternel, ICRA 2022)
- https://doi.org/10.1109/TRO.2022.3203625 (Chen, Yi, Song, T-RO 2023, via DBLP + Crossref)
- https://doi.org/10.1177/02783649231208729 (Bıyık, Huynh, Kochenderfer, Sadigh, IJRR 2024, via DBLP + Crossref)
- https://doi.org/10.1109/IROS60139.2025.11246109 (Han, Huang, Yi, IROS 2025, via DBLP)
- https://arxiv.org/abs/2505.03296 (von Hartz et al., MiDiGap, 2025)
- https://doi.org/10.1109/JAS.2025.125195 (Pan, Shi, Li, Xu, Ahn, JAS 2025, via DBLP)
- https://arxiv.org/abs/2603.01480 (Haque et al., 2026, UTS — not a required-lab match)
- https://arxiv.org/abs/2602.12243 (Salunkhe & Kontoudis, 2026 — not a required-lab match)
- https://doi.org/10.1109/TAC.2026.3662545 and https://arxiv.org/abs/2406.03224 (Evangelisti, Della Santina, Hirche, TAC 2026 — TU Munich, not a required-lab match)
- https://arxiv.org/abs/2307.04415 (Lederer, Umlauft, Hirche, TAC 2026 — TU Munich, not a required-lab match)
- https://dblp.org (multiple author/keyword searches used throughout for venue/year/DOI verification)
- https://api.crossref.org (multiple DOI lookups used for abstract/metadata verification)
