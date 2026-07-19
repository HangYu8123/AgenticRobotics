# Mechanical Engineering Knowledge for Robotics

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Brief practical reference, not a textbook. Every section cites fetched URLs.

## Scope

Mechanical knowledge a robotics practitioner needs to spec, debug, or reason about a manipulator/mobile-robot's physical hardware: actuation, transmission, structure, kinematics, statics/dynamics, tolerancing, bearings/sealing, and the safety standards that govern human-robot proximity. Electronics, controls theory, and perception are out of scope.

## Actuation

- Torque constant (Kt) and back-EMF constant (Ke) of a DC motor are numerically equal in consistent SI units (V·s/rad = N·m/A). Source: https://zbotic.in/dc-motor-torque-vs-speed-understanding-the-characteristics-curve/
- Torque is proportional to current (τ = Kt·I). As back-EMF rises with speed, available current — and therefore torque — falls, giving an approximately linear torque–speed curve. Source: https://zbotic.in/dc-motor-torque-vs-speed-understanding-the-characteristics-curve/
- Continuous torque is a thermal rating set by I²R winding heating; short-duration peak torque (higher current) is available until winding temperature limits are exceeded. This follows from the Kt/current relationship above.
- Duty-cycle-specific manufacturer curves were not independently verified in this pass — a fetch of Maxon's technical-formulas page returned a server error (see Coverage notes). Treat specific continuous-vs-peak torque ratios as a datasheet lookup, not a fact from this document.
- Gearing multiplies torque and divides speed by the gear ratio: higher ratio → more torque/less speed (favors lifting, low-speed precision); lower ratio → more speed/less torque (favors fast motion). Source: https://ineedmicromotors.com/dc-motor-gear-ratios-impact-on-torque-and-speed-explained/
- **Quasi-direct-drive (QDD):** high-torque-density motor with a low reduction ratio, typically 2:1–15:1, versus 50:1–300:1 for classical gearmotors. Source: https://www.emergentmind.com/topics/quasi-direct-drive-qdd-actuation
- QDD trades some torque density for low reflected inertia, low friction, and backdrivability. Single-stage internal (stator-integrated) planetary gearing is mass- and efficiency-optimal only up to roughly 7:1; higher ratios need an external gearbox. Source: https://www.emergentmind.com/topics/quasi-direct-drive-qdd-actuation
- **Series elastic actuators (SEA):** a compliant spring is placed in series between the motor/gearbox and the joint output. Source: https://www.emergentmind.com/topics/backdrivable-actuators ; QDD context: https://arxiv.org/abs/2004.00467
- SEA benefits: high-fidelity force sensing from spring deflection, passive shock absorption, energy storage/return in cyclic motion, and inherently safer contact — at the cost of compromised control bandwidth relative to stiff or QDD actuation. Source: https://www.emergentmind.com/topics/backdrivable-actuators
- **Backdrivability:** the ability of external forces to move an actuator with low resistance, i.e., low mechanical impedance; central to safe/adaptive physical human-robot interaction, haptics, and exoskeletons. Source: https://www.emergentmind.com/topics/backdrivable-actuators
- **Gearbox families:**
  - Planetary: single-stage efficiency typically 96–98%, good for continuous high-speed servo duty. Source: https://zanerobotics.substack.com/p/cycloidal-harmonic-and-planetary
  - Harmonic drive: near-zero backlash by design (flexspline teeth engage the circular spline over a wide arc under load); low reflected inertia; compact. Industry standard for compact precision joints in industrial arms.
  - Cycloidal: multi-point pin/cycloidal-disc contact gives >300% more load capacity than a harmonic drive of the same volume. Source: https://zanerobotics.substack.com/p/cycloidal-harmonic-and-planetary
  - Cycloidal cost: more viscous friction/heat (notably at low-temperature startup or high speed) and more backlash/ripple than a harmonic drive — better suited to high-torque, impact-loaded joints rather than precision positioning.
  - A hobbyist 3D-printed (PLA) head-to-head test found both drive types reached ~4.8 N·m with a NEMA17 (~65% real efficiency vs. a theoretical 25× reduction). Source: https://howtomechatronics.com/how-it-works/harmonic-vs-cycloidal-drive-designing-3d-printing-testing/
  - In the same test, under a NEMA23 the cycloidal unit sustained ~21.5 N·m before deforming while the harmonic unit's flexspline failed almost immediately — illustrating that failure mode (not just backlash) differs sharply between the two topologies. Caveat: printed-plastic prototype, not representative of production metal units. Source: https://howtomechatronics.com/how-it-works/harmonic-vs-cycloidal-drive-designing-3d-printing-testing/
- **Backlash and backdrivability trade off against stiffness and precision:** near-zero-backlash transmissions (harmonic drives, preloaded ball screws) typically also reduce backdrivability; low-ratio QDD trades peak torque density for backdrivability and low reflected inertia (see QDD above).

## Transmission and gearing

- **Ball screws:** rolling ball contact instead of sliding threads gives markedly lower driving torque than an equivalent sliding (Acme-type) screw for the same load. Source: https://tech.thk.com/en/products/pdf/en_b15_006.pdf (THK)
- Consequence: less friction heat and a higher achievable feed rate than a sliding screw, for a given motor size. Source: https://tech.thk.com/en/products/pdf/en_b15_006.pdf (THK)
- **Preload:** applying preload removes axial clearance (backlash) in a ball screw or linear guide and increases rigidity, at the cost of some added friction/torque. Source: https://www.linearmotiontips.com/a-users-guide-to-preload/
- Common preload methods: oversized balls in the nut, an adjustable-diameter nut, or tensioning two single nuts against each other (double-nut) with a spacer or spring. Source: https://www.linearmotiontips.com/a-users-guide-to-preload/
- **Linear guides (LM rails):** under combined preload and working load, THK reports over 90% of the original preload remains after 2,000 km of travel, and preload does not meaningfully increase rolling resistance. Source: https://tech.thk.com/en/products/pdf/en_b01_008.pdf (THK)
- **Belts/tendons:** used for remote actuation (moving the motor mass off the distal link) with low backlash and light weight, at the cost of finite compliance/stretch versus a rigid screw or gear train. Source: https://source-robotics.com/blogs/blog/belts-vs-planetary-vs-harmonic-vs-cycloidal-there-are-too-many-what-to-choose

## Structure, materials, and stiffness

- **Density:** aluminum ≈ 2.7 g/cm³, structural steel ≈ 7.9 g/cm³, carbon-fiber composite (≈70% fiber / 30% epoxy) ≈ 1.55 g/cm³ — roughly half the density of aluminum and a fifth that of steel. Source: http://www.dexcraft.com/articles/carbon-fiber-composites/aluminium-vs-carbon-fiber-comparison-of-materials/
- **Stiffness (Young's modulus) at equal thickness:** aluminum ≈ 69 GPa; woven (2-direction) carbon fiber ≈ 90.5–132 GPa depending on layup; unidirectional (1-direction) carbon fiber ≈ 181 GPa. Source: http://www.dexcraft.com/articles/carbon-fiber-composites/aluminium-vs-carbon-fiber-comparison-of-materials/
- A same-thickness standard-CF part is roughly 31% stiffer, 42% lighter, and 60% stronger (by the source's tensile-strength/weight metric) than an equivalent aluminum part. Source: http://www.dexcraft.com/articles/carbon-fiber-composites/aluminium-vs-carbon-fiber-comparison-of-materials/
- Steel offers high absolute stiffness and strength but its density penalty hurts a moving robot's inertia and energy use; aluminum is the common mid-ground.
- Carbon fiber composite is used where mass at the distal end of an arm matters most, since distal mass directly drives reflected inertia and the torque required of proximal joints (see Statics and dynamics).
- **Natural frequency limits control bandwidth:** every structure has a resonant frequency; a "soft" (low-stiffness) joint or link has a low resonant frequency that can overlap the frequencies used by the servo/motion controller. Source: https://hobberdrive.com/importance-torsional-stiffness-robotic-joints/
- Operating near that resonance causes vibration that degrades motion control; increasing structural/joint torsional stiffness pushes the resonant frequency higher, permitting more aggressive controller tuning. Source: https://hobberdrive.com/importance-torsional-stiffness-robotic-joints/
- Design responses to resonance: change the excitation/control-signal frequency (software-only, simpler) or change mass/stiffness distribution (requires structural redesign, harder). This is a general vibration-analysis strategy, not tied to one numeric example.

## Kinematics and mechanism design

- **Mobility (Chebychev–Grübler–Kutzbach criterion):** for a spatial mechanism, M = 6(N − 1 − j) + Σf_i; for a planar mechanism, M = 3(N − 1 − j) + Σf_i, where N is the number of links (including the fixed link), j is the number of joints, and f_i is the degrees of freedom of joint i. Source: https://en.wikipedia.org/wiki/Chebychev%E2%80%93Gr%C3%BCbler%E2%80%93Kutzbach_criterion
- Example: a planar four-bar linkage (N=4, j=4, all 1-DOF joints) gives M = 3(4−1−4)+4 = 1, the expected single degree of freedom. Source: https://en.wikipedia.org/wiki/Chebychev%E2%80%93Gr%C3%BCbler%E2%80%93Kutzbach_criterion
- **Denavit–Hartenberg (DH) parameters:** four parameters per link fully describe serial-chain kinematics. Introduced by Denavit and Hartenberg in 1955 to standardize link-frame assignment. Source: https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters
  - link length **r/a** — length of the common normal between consecutive joint axes
  - link twist **α** — angle about the common normal from the old z-axis to the new z-axis
  - link offset **d** — offset along the previous z-axis to the common normal
  - joint angle **θ** — angle about the previous z-axis from the old x-axis to the new x-axis
- **Serial vs. parallel manipulators:** parallel architectures (e.g., delta robots, Stewart/hexapod platforms) use closed kinematic chains, giving higher stiffness — the closed loop doesn't lose rigidity as more links are added, unlike a serial chain — plus better load-to-weight ratio and higher precision. Source: https://en.wikipedia.org/wiki/Parallel_manipulator
- Cost: a comparatively small, complex-shaped workspace, harder inverse/forward kinematics, and singularities where the platform pose becomes locally uncontrollable (in extreme cases the mechanism can collapse). Source: https://en.wikipedia.org/wiki/Parallel_manipulator
- Serial manipulators give a larger, simpler workspace and simpler control at the cost of stiffness and speed.
- A Stewart platform is the canonical 6-DOF parallel mechanism, using six actuated struts; delta robots use three lightweight parallel arms for high-speed pick-and-place. Source: https://www.linearmotiontips.com/what-are-hexapod-robots-stewart-platforms/
- Payload–reach tradeoff and workspace shape are direct consequences of the chosen kinematic architecture and link-length/joint-limit choices; parallel designs concentrate stiffness near the base at the cost of reach, serial designs trade reach for base-mounted actuator mass and cumulative compliance down the chain.

## Statics and dynamics

- **Jacobian force/torque transmission:** the joint torques needed to hold a static end-effector force/torque are τ = Jᵀ(q)·F, the transpose of the manipulator Jacobian applied to the end-effector wrench. Source: https://en.wikibooks.org/wiki/Robotics_Kinematics_and_Dynamics/Serial_Manipulator_Statics
- This relation is the standard basis for torque budgeting (sizing actuators for a required end-effector force or a gravity/payload load) and derives from the principle of virtual work (end-effector virtual work equals the sum of joint virtual work). Source: https://en.wikibooks.org/wiki/Robotics_Kinematics_and_Dynamics/Serial_Manipulator_Statics
- Near kinematic singularities, bounded joint torques can map to unbounded end-effector force/torque capability — favorable for static holding at a singular pose, unfavorable for velocity control or force accuracy there. Source: https://en.wikibooks.org/wiki/Robotics_Kinematics_and_Dynamics/Serial_Manipulator_Statics
- Gravity compensation and torque budgeting follow directly from the same static relation: each joint must supply enough torque to counter the moment of every downstream link's weight (and any end-effector payload) about that joint.
- This is why proximal joints in a serial arm are sized much larger than distal ones, and why center-of-mass placement (keeping mass close to the base, or counterbalancing) reduces required actuator torque.

## Tolerancing, fits, and manufacturing

- **GD&T (Geometric Dimensioning and Tolerancing)** is a standardized symbolic language for specifying allowable geometric variation (not just linear dimensions) so that parts assemble and function correctly. Source: https://formlabs.com/blog/gdt-geometric-dimensioning-and-tolerancing/
- Two parts can each be within their individual linear tolerances and still fail to assemble; GD&T tolerance zones can also be larger (less restrictive, cheaper to manufacture) than equivalent coordinate tolerancing while still guaranteeing fit. Source: https://formlabs.com/blog/gdt-geometric-dimensioning-and-tolerancing/
- Governing standards: **ASME Y14.5** (current edition Y14.5-2018) in the US; **ISO 1101** (geometrical tolerancing of form, orientation, location, and runout) internationally. Source: https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing ; https://formlabs.com/blog/gdt-geometric-dimensioning-and-tolerancing/
- Companion ISO standards: ISO 5458 (positional tolerancing), ISO 5459 (datums and datum systems), ISO 8015 (fundamental GPS concepts). Source: https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing
- Five main geometric-tolerance categories: **form** (straightness, flatness, circularity, cylindricity), **profile** (line/surface profile), **orientation** (perpendicularity, angularity, parallelism — relative to a datum), **location** (position, concentricity, symmetry), and **runout** (circular/total runout). Source: https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing
- **Maximum material condition (MMC):** the state where a feature of size contains the most material (largest allowed pin, smallest allowed hole). Source: https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing
- Using MMC as a modifier lets a feature earn "bonus tolerance" when it is produced away from its worst-case (MMC) size, since extra clearance exists. Source: https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing
- **Fits:** ISO 286 defines a standardized system of limits and fits — e.g., a "40H11" callout specifies a 40 mm nominal hole toleranced for a loose running fit; fit class selection depends on the manufacturing process and required clearance/interference. Source: https://formlabs.com/blog/gdt-geometric-dimensioning-and-tolerancing/
- **Bolted-joint preload:** tightening torque and achieved preload are related by T = K·d·F, where T is applied torque, K is the (empirical) torque coefficient, d is the nominal bolt diameter, and F is the resulting preload force. Source: https://mechanicalc.com/reference/bolted-joint-analysis
- Typical K values: ≈0.30 for a plain/black-finish bolt, ≈0.20 zinc-plated, ≈0.18 lubricated, ≈0.12 with anti-seize; use K≈0.2 as a default when the surface condition is unknown. Friction (captured in K) is the largest source of uncertainty in torque-based preload control. Source: https://mechanicalc.com/reference/bolted-joint-analysis
- **Thread engagement:** a common rule of thumb is that a bolted/screwed joint needs at least 6–7 engaged threads (or an engagement depth at least equal to the fastener diameter) to develop the fastener's full tensile strength. Source: https://engineeringlibrary.org/reference/threaded-fastener-preload-mil-hdbk
- **Thread-locking** methods to prevent preload loss under vibration: locking adhesives (e.g., threadlocker compounds), nylon-insert lock nuts, lock washers, lock wire, and locking patches/pellets. Source: https://engineeringlibrary.org/reference/threaded-fastener-preload-mil-hdbk

## Bearings, seals, lubrication, and ingress protection

- **Bearing types:** rolling-element bearings (ball, cylindrical roller, tapered roller, needle, thrust) use rolling contact between inner/outer races and rolling elements. Source: https://engineeringhulk.com/types-of-bearing/
- Ball bearings contact races at a point — low friction at high speed but moderate load capacity; roller bearings contact along a line — much higher load capacity at somewhat higher friction. Source: https://engineeringhulk.com/types-of-bearing/
- **Grease lubrication:** grease (a thickener — commonly a lithium, sodium, barium, calcium, or strontium soap, or a non-soap inorganic thickener — combined with a base oil, mineral/ester/silicone) is used to reduce friction and prevent metal-to-metal contact and corrosion in rolling bearings. Source: https://pibsales.com/bearings/guide-to-selecting-the-right-grease-for-ball-and-roller-bearings/
- Grease selection depends on speed, load, temperature, moisture exposure, sealing, and relubrication interval; NLGI grade 2 is the most common general-purpose consistency. Source: https://pibsales.com/bearings/guide-to-selecting-the-right-grease-for-ball-and-roller-bearings/
- **Ingress protection — IEC 60529 (the IP code):** a two-digit rating; the first digit (0–6) rates protection against solid-object/dust ingress, the second (0–9K) rates protection against liquid ingress. Source: https://en.wikipedia.org/wiki/IP_code ; https://www.iec.ch/ip-ratings
- Selected solids levels: IP2X blocks objects >12.5 mm (fingers), IP4X blocks >1 mm (thin wires), IP5X is dust-protected, IP6X is dust-tight. Source: https://en.wikipedia.org/wiki/IP_code
- Selected liquids levels: IPX4 protects against splashing from any direction, IPX6 against powerful jets, IPX7 against immersion to 1 m, IPX8 against continuous immersion beyond that (depth is manufacturer-specified), IPX9K against high-pressure/high-temperature jets. Source: https://en.wikipedia.org/wiki/IP_code
- Water-ingress ratings are **not cumulative above IPX6** — an IPX7-rated device is not automatically rated for IPX5/IPX6 jet exposure unless separately tested. Source: https://en.wikipedia.org/wiki/IP_code

## Compliance and safety standards

- **ISO 10218-1:2025 — "Robotics — Safety requirements — Part 1: Industrial robots"** and **ISO 10218-2:2025 — "Robotics — Safety requirements — Part 2: Industrial robot applications and robot cells"** entered into force 1 April 2025, the first update to the core robot-safety standard series since 2011. Source: https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/ ; title/scope confirmed via ISO's own listing: https://www.iso.org/obp/ui/en/#!iso:std:73933:en
- Part 1 covers the design/manufacture/remanufacture/rebuild of the robot itself (manufacturer's responsibility); Part 2 covers the design and integration of the robot application and cell (system integrator's responsibility) — both parts must be satisfied together for a compliant collaborative application. Source: https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/
- **ISO/TS 15066:2016** ("Robots and robotic devices — Collaborative robots") previously supplemented ISO 10218 with power-and-force-limiting and collaborative-application guidance. Source: https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/
- As of the 2025 revision it **no longer exists as a standalone document** — its requirements were folded directly into ISO 10218-1:2025 / -2:2025. Source: https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/
- The four recognized collaborative operating techniques remain: power and force limiting (PFL), hand guiding, speed and separation monitoring, and safety-rated monitored stop. Source: https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/
- **Power and force limiting (PFL):** keeps any robot/human contact below biomechanical injury limits (maximum force and pressure, defined per body region) originally specified in ISO/TS 15066 and now carried in the merged ISO 10218 series. Source: https://www.automate.org/robotics/tech-papers/iso-ts-15066-explained
- **ISO 9283 — industrial robot performance testing:** defines standardized test methods for manipulating industrial robots, covering (unidirectional and multi-directional) pose accuracy, pose repeatability, distance accuracy/repeatability, pose stabilization time and overshoot, path accuracy and path repeatability, cornering deviation, and static compliance. Source: https://eureka.patsnap.com/article/iso-9283-vs-manufacturer-claims-how-to-verify-repeatability-specs
- **Repeatability** = how consistently a robot returns to the same taught pose; **accuracy** = how close the robot gets to a specified/commanded pose in space — these are distinct, and repeatability is typically much better than accuracy on an uncalibrated industrial robot. Source: https://eureka.patsnap.com/article/iso-9283-vs-manufacturer-claims-how-to-verify-repeatability-specs
- Exact formal ISO title for ISO 9283 not independently confirmed against the paywalled iso.org page — see Coverage notes.
- **Compliant mechanisms / mechanical compliance** and PFL are complementary safety strategies: compliant structures/SEAs (see Actuation) reduce peak contact force through passive energy absorption, while PFL is the standards-based limit that contact force must stay under regardless of mechanism.

## Coverage notes

- Motor thermal/duty-cycle limits are covered only qualitatively (via the Kt/current relation); a direct fetch of Maxon's technical-formulas page failed (server error) and no other manufacturer duty-cycle datasheet was fetched in this pass. Treat specific continuous/peak torque *ratios* as needing a datasheet lookup, not this document.
- The exact formal ISO title and full clause list of ISO 9283 could not be confirmed directly (iso.org and standards.iteh.ai blocked automated fetches with 403/binary-PDF responses); the scope description above is corroborated by multiple independent secondary sources but the literal title string is not independently verified here.
- Backlash/efficiency numbers for harmonic vs. cycloidal vs. planetary gearboxes mix vendor-context claims (96–98% planetary efficiency, >300% cycloidal load capacity) with one hobbyist 3D-printed test — treat the printed-prototype numbers as illustrative of failure-mode differences, not as production-hardware specs.
- Ball-screw torque-reduction and preload-percentage figures are sourced from THK's own technical PDFs via search-result synthesis; the PDFs themselves returned binary/unparseable or 403 responses on direct fetch in this pass, so the numbers should be cross-checked against the primary PDF before being treated as exact.
- ISO 10218/ISO 9283/IEC 60529 designations and IEC 60529's IP-code structure are confirmed against either iso.org's own catalog listing (via search) or Wikipedia/iec.ch (directly fetched); no standard designation in this document was cited without at least one corroborating live source.

## Sources

- https://zbotic.in/dc-motor-torque-vs-speed-understanding-the-characteristics-curve/
- https://ineedmicromotors.com/dc-motor-gear-ratios-impact-on-torque-and-speed-explained/
- https://www.emergentmind.com/topics/quasi-direct-drive-qdd-actuation
- https://www.emergentmind.com/topics/backdrivable-actuators
- https://arxiv.org/abs/2004.00467
- https://howtomechatronics.com/how-it-works/harmonic-vs-cycloidal-drive-designing-3d-printing-testing/
- https://zanerobotics.substack.com/p/cycloidal-harmonic-and-planetary
- https://source-robotics.com/blogs/blog/belts-vs-planetary-vs-harmonic-vs-cycloidal-there-are-too-many-what-to-choose
- https://tech.thk.com/en/products/pdf/en_b15_006.pdf
- https://www.linearmotiontips.com/a-users-guide-to-preload/
- https://tech.thk.com/en/products/pdf/en_b01_008.pdf
- http://www.dexcraft.com/articles/carbon-fiber-composites/aluminium-vs-carbon-fiber-comparison-of-materials/
- https://hobberdrive.com/importance-torsional-stiffness-robotic-joints/
- https://en.wikipedia.org/wiki/Chebychev%E2%80%93Gr%C3%BCbler%E2%80%93Kutzbach_criterion
- https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters
- https://en.wikipedia.org/wiki/Parallel_manipulator
- https://www.linearmotiontips.com/what-are-hexapod-robots-stewart-platforms/
- https://en.wikibooks.org/wiki/Robotics_Kinematics_and_Dynamics/Serial_Manipulator_Statics
- https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing
- https://formlabs.com/blog/gdt-geometric-dimensioning-and-tolerancing/
- https://mechanicalc.com/reference/bolted-joint-analysis
- https://engineeringlibrary.org/reference/threaded-fastener-preload-mil-hdbk
- https://engineeringhulk.com/types-of-bearing/
- https://pibsales.com/bearings/guide-to-selecting-the-right-grease-for-ball-and-roller-bearings/
- https://en.wikipedia.org/wiki/IP_code
- https://www.iec.ch/ip-ratings
- https://www.evsint.com/collaborative-robot-safety-standards-2026-iso-10218-2025-ts-15066/
- https://www.iso.org/obp/ui/en/#!iso:std:73933:en
- https://www.iso.org/standard/73934.html
- https://www.automate.org/robotics/tech-papers/iso-ts-15066-explained
- https://eureka.patsnap.com/article/iso-9283-vs-manufacturer-claims-how-to-verify-repeatability-specs
