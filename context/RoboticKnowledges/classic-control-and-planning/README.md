# Classic Control and Planning for Robotics

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Award status is asserted only where a fetched page confirms it.

## What this is

This page tracks classical, model-based approaches to robot control and motion planning — the non-learned foundations that model-predictive control, safety filters, and modern learned policies still build on or get benchmarked against. **Control** covers PID, LQR/LQG, model-predictive control (MPC), impedance/admittance and force control, whole-body control for legged/humanoid robots, and control barrier functions (CBFs) for safety. **Planning** covers sampling-based motion planning (RRT*, PRM, BIT*), trajectory optimization (CHOMP, TrajOpt, iLQR/DDP, sequential convex programming), search-based planning, and task-and-motion planning (TAMP). The lists below give one representative paper per year from 2014–2024, three from 2025, and five 2026 preprints/ICRA 2026 papers from major labs.

## Classic papers (2014–2024, one per year)

### 2014
**[Control-limited differential dynamic programming](https://doi.org/10.1109/ICRA.2014.6907001)** — ICRA 2014 · `award: not verified`
- *Contribution:* Generalizes Differential Dynamic Programming (DDP) to handle box inequality constraints on controls without sacrificing convergence speed, enabling real-time trajectory optimization.
- *Results:* Demonstrated fast enough for real-time control of a full humanoid robot model on contemporary hardware.

### 2015
**[Batch Informed Trees (BIT*): Sampling-based Optimal Planning via the Heuristically Guided Search of Implicit Random Geometric Graphs](https://robotic-esp.com/papers/gammell_icra15)** — ICRA 2015 · `award: not verified`
- *Contribution:* Unifies graph-based search (A*-style ordering) with sampling-based planning by treating batches of samples as an implicit random geometric graph, searched with an admissible heuristic.
- *Results:* Found better solutions faster than RRT, RRT*, Informed RRT*, and FMT* across simulated R² and R⁸ problems and a 14-DOF manipulation task on the HERB robot.

### 2016
**[Control Barrier Function Based Quadratic Programs for Safety Critical Systems](https://arxiv.org/abs/1609.06408)** — IEEE Transactions on Automatic Control, 2016 (arXiv Sept 2016) · `award: not verified`
- *Contribution:* Formalizes control barrier functions (CBFs) as a way to encode safety (forward invariance of a set) as a constraint in a real-time quadratic program alongside a performance objective.
- *Results:* Demonstrated on adaptive cruise control and lane-keeping, satisfying both safety constraints and actuator limits; this QP-based CBF formulation became the standard safety-filter pattern cited across later safety-critical control work.

### 2017
**[Asymptotically Optimal Design of Piecewise Cylindrical Robots using Motion Planning](https://roboticsproceedings.org/rss13/p20.html)** — RSS 2017 · `award: RSS 2017 Best Paper Award (per roboticsfoundation.org)`
- *Contribution:* Integrates sampling-based motion planning into a stochastic design-optimization loop to select robot kinematic parameters (piecewise-cylindrical links) that reach the most goal regions while avoiding obstacles.
- *Results:* Shown to converge asymptotically to optimal designs, applied to serial manipulators and concentric-tube medical robots navigating constrained anatomical spaces.

### 2018
**[Dynamic Locomotion in the MIT Cheetah 3 Through Convex Model-Predictive Control](https://dspace.mit.edu/bitstream/handle/1721.1/138000/convex_mpc_2fix.pdf)** — IROS 2018 · `award: not verified`
- *Contribution:* Formulates ground-reaction-force planning for a torque-controlled quadruped as a convex MPC problem over a simplified rigid-body model, keeping the full 3D dynamics while remaining solvable in real time.
- *Results:* Solved MPC problems with up to 0.5 s prediction horizons in under 1 ms at 20–30 Hz, demonstrating stand, trot, flying-trot, pronk, bound, pace, a 3-legged gait, and a full 3D gallop on hardware.

### 2019
**[Feedback MPC for Torque-Controlled Legged Robots](https://arxiv.org/abs/1905.06144)** — IROS 2019 · `award: not verified`
- *Contribution:* Uses the feedback policy produced by a DDP-based MPC solver — rather than a separately designed tracking controller — to bridge the gap between low MPC update rates and high-rate torque commands, using a relaxed barrier function for friction-cone constraints.
- *Results:* Achieved stable locomotion on the ANYmal torque-controlled quadruped in both simulation and hardware experiments.

### 2020
**[PDDLStream: Integrating Symbolic Planners and Blackbox Samplers via Optimistic Adaptive Planning](https://arxiv.org/abs/1802.08705)** — ICAPS 2020 · `award: not verified`
- *Contribution:* Extends PDDL with "streams" — declarative specifications of black-box sampling procedures — letting domain-independent symbolic planners solve task-and-motion planning (TAMP) problems with continuous, high-dimensional variables (poses, configurations, motions).
- *Results:* Solved robotic manipulation problems (pick, place, push, pour, cook) across simulated domains and real-world robot tasks, becoming a widely used TAMP baseline (code released as `pddlstream`).

### 2021
**[TARE: A Hierarchical Framework for Efficiently Exploring Complex 3D Environments](https://roboticsproceedings.org/rss17/p018.html)** — RSS 2021 · `award: RSS 2021 Best Paper Award and Best System Paper Award (per roboticsfoundation.org)`
- *Contribution:* Introduces a two-level exploration planner that maintains dense data near the robot and sparse data far away, trading detail for speed to keep kinodynamically feasible paths computable at high update rates.
- *Results:* Reported 80% more exploration efficiency (explored volume per second) than the prior state of the art while using under 50% of the computation, validated on ground and aerial robots in complex indoor/outdoor environments.

### 2022
**[Non-Gaussian Risk Bounded Trajectory Optimization for Stochastic Nonlinear Systems in Uncertain Environments](https://arxiv.org/abs/2203.03038)** — ICRA 2022 · `award: ICRA 2022 Outstanding Planning Paper (per robohub.org)`
- *Contribution:* Solves risk-bounded trajectory optimization for robots with stochastic nonlinear dynamics and arbitrarily distributed (non-Gaussian) obstacle and initial-state uncertainty, by converting chance constraints into deterministic constraints on distribution moments.
- *Results:* The authors state this is the first method to solve motion planning to this general extent (nonlinear dynamics, nonlinear constraints, arbitrary uncertainty), demonstrated on several robotics examples; the paper does not report specific numeric benchmarks.

### 2023
**[Time Optimal Ergodic Search](https://roboticsproceedings.org/rss19/p082.html)** — RSS 2023 · `award: RSS 2023 Outstanding Paper Award (Winner) (per roboticsfoundation.org)`
- *Contribution:* Formulates the search-time-vs-coverage-thoroughness tradeoff as a minimum-time problem with an ergodic-coverage constraint, solved both analytically (via Pontryagin's optimality conditions) and numerically (via direct transcription).
- *Results:* Demonstrated on simulated trajectory generation and real drone experiments in cluttered environments with obstacle avoidance, including ablations on parameter sensitivity.

### 2024
**[TinyMPC: Model-Predictive Control on Resource-Constrained Microcontrollers](https://arxiv.org/abs/2310.16985)** — ICRA 2024 · `award: ICRA 2024 Best Paper Award in Automation (per tinympc.org project page)`
- *Contribution:* An open-source convex MPC solver built for embedded microcontrollers, handling state/input bounds and second-order-cone constraints with a small memory footprint.
- *Results:* Achieved up to an 8x speed-up over the OSQP solver on randomly generated QP-based MPC benchmarks while using substantially less memory.

## 2025 (3 papers)

**[No Plan but Everything under Control: Robustly Solving Sequential Tasks with Dynamically Composed Gradient Descent](https://arxiv.org/abs/2503.01732)** — ICRA 2025 · `award: ICRA 2025 Best Paper Award on Planning and Control (Winner)` · `lab: TU Berlin (Robotics and Biology Laboratory)`
- *Contribution:* Replaces explicit sequential-task planning with a gradient-descent controller that dynamically composes and adapts a myopic potential field in response to feedback, so task structure emerges from control rather than being planned in advance.
- *Results:* Solved the classic Blocks World domain without an explicit planner and ran 100 real-world drawer-manipulation trials with robustness to disturbances that broke planning-based baselines.

**[SELP: Generating Safe and Efficient Task Plans for Robot Agents with Large Language Models](https://arxiv.org/abs/2409.19471)** — ICRA 2025 (Best Paper Award on Planning and Control finalist, per 2025.ieee-icra.org) · `award: ICRA 2025 Best Paper Award on Planning and Control finalist` · `lab: not verified`
- *Contribution:* Converts natural-language instructions into Linear Temporal Logic task plans using equivalence voting for consistent translation, constrained decoding to keep generation within the LTL grammar, and domain-specific fine-tuning.
- *Results:* Improved safety rate by 10.8% and plan efficiency by 19.8% over prior LLM planners on drone navigation, and improved safety rate by 20.4% on manipulation tasks.

**[Solving Multi-Agent Safe Optimal Control with Distributed Epigraph Form MARL](https://roboticsproceedings.org/rss21/p027.html)** — RSS 2025 (Outstanding Paper Award finalist, per roboticsfoundation.org) · `award: RSS 2025 Outstanding Paper Award finalist` · `lab: MIT (per RSS 2025 award listing)`
- *Contribution:* Reformulates constrained multi-agent optimal control using an epigraph form to stabilize training, then distributes the resulting centralized optimization into a per-agent, centralized-training/distributed-execution MARL algorithm (Def-MARL).
- *Results:* Outperformed baseline safe-MARL methods on 8 tasks across 2 simulators while maintaining safety constraints, and was validated on physical Crazyflie quadcopters completing collaborative tasks safely.

## 2026 (5 papers)

**[Whole-Body Model-Predictive Control of Legged Robots with MuJoCo](https://arxiv.org/abs/2503.04613)** — ICRA 2026, Vienna (accepted, per arXiv listing) · `award: not verified (not an ICRA 2026 Planning & Control finalist, per 2026.ieee-icra.org/awards)` · `lab: MIT Robotic Exploration Lab (per roboticexplorationlab.org) with Carnegie Mellon University (Guanya Shi, confirmed CMU Robotics Institute faculty per ri.cmu.edu) and Google DeepMind (Yuval Tassa, Tom Erez — MuJoCo maintainers, per github.com/google-deepmind/mujoco)`
- *Contribution:* Shows that a straightforward iLQR-based whole-body MPC loop, using MuJoCo for dynamics and finite-difference derivatives, is sufficient to control quadruped and humanoid robots in the real world without more specialized machinery.
- *Results:* Demonstrated real-time whole-body control transferring from simulation to physical hardware across dynamic quadruped locomotion and bipedal/humanoid tasks; the paper does not report specific timing/accuracy numbers on its arXiv abstract page.

**[The Trajectory Bundle Method: Unifying Sequential-Convex Programming and Sampling-Based Trajectory Optimization](https://arxiv.org/abs/2509.26575)** — ICRA 2026, Vienna (accepted, per arXiv listing) · `award: not verified (not an ICRA 2026 Planning & Control finalist, per 2026.ieee-icra.org/awards)` · `lab: MIT Robotic Exploration Lab (per roboticexplorationlab.org) with Google DeepMind (Yuval Tassa, Tom Erez)`
- *Contribution:* Unifies sequential convex programming and sampling-based methods (e.g., MPPI) into a single derivative-free trajectory-optimization framework that samples the dynamics, cost, and constraints and lets the solver interpolate between samples.
- *Results:* Presented as a general framework applicable to practical motion-planning and control problems; specific numeric benchmarks are not stated in the abstract.

**[Code Generation and Conic Constraints for Model-Predictive Control on Microcontrollers with Conic-TinyMPC](https://arxiv.org/abs/2403.18149)** — ICRA 2026, Vienna (accepted, per arXiv listing) · `award: not verified (not an ICRA 2026 Planning & Control finalist, per 2026.ieee-icra.org/awards)` · `lab: MIT Robotic Exploration Lab (per roboticexplorationlab.org)`
- *Contribution:* Extends the TinyMPC ADMM-based embedded solver to support second-order-cone constraints and adds code generation for Python, MATLAB, and Julia, targeting resource-constrained microcontrollers.
- *Results:* Reported a 10.6x–142.7x speedup over state-of-the-art embedded solvers on QP and second-order-cone problems and fit order-of-magnitude larger problems in memory, validated on a 27-gram Crazyflie quadrotor tracking trajectories under conic constraints.

**[Constrained Whole-Body Tracking for Humanoid Robots](https://arxiv.org/abs/2606.00374)** — arXiv preprint, submitted May 2026 · `award: not verified` · `lab: Stanford University (Marco Pavone) — Pavone's Google Scholar profile also lists an NVIDIA affiliation`
- *Contribution:* ConstrainedMimic combines operational-space control and control barrier functions to enforce arbitrary runtime constraints (collision avoidance, joint limits, center-of-mass stability) on top of a pre-trained RL whole-body tracking policy, without retraining.
- *Results:* Runs fully differentiably on CPU/GPU/TPU at 300–500 Hz, demonstrated for collision avoidance, joint-limit, and CoM-stability enforcement on a simulated Unitree G1 humanoid in motion-tracking and teleoperation experiments.

**[WarpMPC: Large-Batch MPC on GPU via ADMM](https://arxiv.org/abs/2607.11603)** — arXiv preprint, submitted July 2026 · `award: not verified` · `lab: MIT Biomimetic Robotics Lab (Sangbae Kim, Se Hwan Jeon — confirmed current MIT PhD student per biomimetics.mit.edu/people) with RWTH Aachen (Sebastian Trimpe)`
- *Contribution:* A GPU toolbox (JAX/Warp) for solving very large batches (10,000–100,000+) of identically structured MPC problems by unrolling the sparse linear factorizations that dominate ADMM solver runtime, with optimized memory layout and scheduled backsolves.
- *Results:* Achieved 8,000–250,000 SQP iterations per second on cartpole, quadrotor, and humanoid benchmarks (3x–25x over baselines), and used this throughput to synthesize a dataset and train a neural-network MPC approximation in under 4 minutes that stabilized a nano quadrotor in hardware.

## Coverage notes

- **Year-count discrepancy:** the brief asked for "10 classic papers, one per year, 2014–2024" — that range is actually 11 years. A verifiable, on-topic paper was found for all 11 years (2014–2024 inclusive), so all 11 are included rather than arbitrarily dropping one.
- **Not all classic entries are award winners.** RSS/ICRA/IROS best-paper awards in 2014–2024 rarely went to classical-control/planning papers specifically (they more often went to perception, manipulation-learning, or HRI work). Where no relevant award existed, the entry is the most-cited/most-influential classical-control-or-planning paper published that year at a top venue (verified to exist via arXiv/DOI/proceedings, not via citation-count tools), marked `award: not verified`. Confirmed award wins: 2017 (RSS Best Paper), 2021 (RSS Best Paper + Best System Paper), 2022 (ICRA Outstanding Planning Paper), 2023 (RSS Outstanding Paper), 2024 (ICRA Best Paper in Automation).
- **2020 pick (PDDLStream) is ICAPS, not ICRA/IROS/RSS/CoRL** — flagged because the brief said "preferring" those four venues; ICAPS is the top venue for the specific classical-planning subfield (TAMP/PDDL) this paper represents, and no comparable ICRA/IROS/RSS 2020 control/planning candidate was found with equal confidence in the time available.
- **2026 venue reality:** see the index's [Known limitations](../knowledge_index.md#known-limitations) for full ICRA/RSS/IROS/CoRL 2026 status. ICRA 2026 award finalists were checked directly at `2026.ieee-icra.org/awards/`; none of the three ICRA 2026 papers below are Planning & Control finalists, so they carry `award: not verified`.
- **Lab-affiliation sourcing for 2026 entries:** MIT and CMU affiliations were confirmed via each lab's own website (`roboticexplorationlab.org`, `biomimetics.mit.edu/people`, `ri.cmu.edu`) rather than the arXiv abstract pages themselves, which display no author affiliations. The Google DeepMind connection for Yuval Tassa/Tom Erez rests on their listing as MuJoCo's original authors on a repository explicitly "maintained by Google DeepMind" — this confirms the MuJoCo/DeepMind link but is not a direct current-employment statement, so it is presented with that caveat.
- **WebSearch tool budget was exhausted mid-task** (shared session-wide limit, consumed in part by parallel sibling category subagents). All verification after that point used `WebFetch` directly against arXiv's API/abstract pages, official RSS proceedings (`roboticsproceedings.org`), lab/award pages, and Google Scholar profile pages — no claim in this file is from prior model knowledge.

## Sources

- https://roboticsfoundation.org/awards/best-paper-award/ (RSS award ground truth, 2014–2025)
- https://doi.org/10.1109/ICRA.2014.6907001 / https://api.semanticscholar.org/graph/v1/paper/45fd8d3745b20349ef763c80bf01ced802eaf75a (Tassa DDP 2014)
- https://robotic-esp.com/papers/gammell_icra15 (BIT* 2015)
- https://arxiv.org/abs/1609.06408 (CBF-QP 2016)
- https://roboticsproceedings.org/rss13/p20.html (RSS 2017 winner)
- https://dspace.mit.edu/bitstream/handle/1721.1/138000/convex_mpc_2fix.pdf ; https://kyo-kutsuzawa.github.io/technical-note/carlo2018.html (Cheetah 3 MPC 2018)
- https://arxiv.org/abs/1905.06144 (Feedback MPC 2019)
- https://arxiv.org/abs/1802.08705 (PDDLStream 2020)
- https://roboticsproceedings.org/rss17/p018.html (TARE, RSS 2021)
- https://arxiv.org/abs/2203.03038 ; https://robohub.org/icra2022-awards-finalists-and-winners/ (ICRA 2022 Outstanding Planning Paper)
- https://roboticsproceedings.org/rss19/p082.html (Time Optimal Ergodic Search, RSS 2023)
- https://arxiv.org/abs/2310.16985 ; https://tinympc.org (TinyMPC, ICRA 2024 Best Paper in Automation)
- https://2025.ieee-icra.org/awards-and-finalists/ (ICRA 2025 awards)
- https://arxiv.org/abs/2503.01732 (Mengers & Brock, ICRA 2025 winner)
- https://arxiv.org/abs/2409.19471 (SELP, ICRA 2025 finalist)
- https://roboticsproceedings.org/rss21/p027.html (Def-MARL, RSS 2025 finalist)
- https://2026.ieee-icra.org/awards/ (ICRA 2026 finalists check)
- https://roboticexplorationlab.org and https://roboticexplorationlab.org/publications.html (MIT REx Lab 2026 papers)
- https://arxiv.org/abs/2503.04613, https://arxiv.org/abs/2509.26575, https://arxiv.org/abs/2403.18149 (three ICRA 2026 papers)
- https://www.ri.cmu.edu/ri-faculty/guanya-shi/ (Guanya Shi, CMU)
- https://github.com/google-deepmind/mujoco (MuJoCo / DeepMind / Tassa & Erez)
- https://scholar.google.com (Marco Pavone profile — Stanford/NVIDIA) ; https://arxiv.org/abs/2606.00374 (ConstrainedMimic)
- https://arxiv.org/abs/2607.11603 ; https://biomimetics.mit.edu/people (WarpMPC, MIT Biomimetic Robotics Lab)
