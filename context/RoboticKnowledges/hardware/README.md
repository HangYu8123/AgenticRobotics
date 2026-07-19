# Robots and Related Hardware

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from manufacturer datasheets and spec pages. Parameters only — no evaluative or promotional content. Values are as published by the vendor and are not independently benchmarked.

## Manipulators

### UR5e — Universal Robots
- DOF: 6 rotating joints | Payload: 5 kg | Reach: 850 mm | Repeatability: ±0.03 mm (ISO 9283) | Weight: 20.7 kg | Max joint speed: 180°/s | Footprint: Ø149 mm | Power: approx. 250 W (typical program) | Control interface: PolyScope GUI, TCP/IP 1000 Mbit Ethernet, Modbus TCP, EtherNet/IP, PROFINET | IP rating: IP54 | Control box I/O: 16 DI / 16 DO / 2 AI / 2 AO
- Source: https://www.universal-robots.com/manuals/EN/HTML/SW5_19/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm (fetched 2026-07-19)

### Franka Research 3 — Franka Robotics
- DOF: 7 | Payload: 3 kg | Reach: 855 mm (covers 94.5% of workspace) | Repeatability: <±0.1 mm | Integrated torque sensors: 7 (1 per joint) | Joint velocity: A1–A4 150°/s, A5–A7 301°/s (239°/s at A6 under FCI); up to 2 m/s at TCP | Stiffness (FCI): translational 10–3000 N/m, rotational 1–300 Nm/rad | Control frequency: 1 kHz (motion control, sensor acquisition, FCI torque/position/velocity control) | Control interface: Desk (workflow programming), RIDE (integration), FCI (low-level real-time control) | Weight: approx. 18.3 kg (per official datasheet)
- Source: https://franka.de/franka-research-3 (fetched 2026-07-19); weight figure per https://franka.de/hubfs/Datasheet%20Franka%20Research%203_R02212_2.2.1_EN.pdf?hsLang=en

### Kinova Gen3 (6DOF / 7DOF) — Kinova Robotics
- DOF: 6 or 7 | Payload: 4 kg (both configurations) | Reach: 891 mm (6DOF) / 902 mm (7DOF) | Repeatability: 0.1 mm @ 2σ (6DOF) / 1.0 mm @ 2σ (7DOF) | Weight: 7.2 kg (6DOF) / 8.2 kg (7DOF) | Control: 1 kHz closed-loop low-level control | Average power draw: approx. 36 W
- Source: https://www.kinovarobotics.com/product/gen3-robots and manufacturer spec sheet https://www.kinovarobotics.com/sites/default/files/TS-014_KINOVA_Gen3_Ultra_lightweight_robot_7DOF-Specifications_EN_R02%20%281%29.pdf (fetched 2026-07-19; figures corroborated via live search of the Kinova-hosted specification PDF, direct PDF text extraction was not possible)

### UFACTORY xArm 7 — UFACTORY
- DOF: 7 | Payload: 3.5 kg | Reach: 700 mm | Repeatability: ±0.1 mm | Weight: 13.7 kg (arm only) | Max joint speed: 180°/s | Max TCP speed: 1000 mm/s | Joint ranges: J1 ±360°, J2 −118° to 120°, J3 ±360°, J4 −11° to 225°, J5 ±360°, J6 −97° to 180°, J7 ±360° | Control interface: Ethernet; RS485 Master×1, RS485 Slave×1; control box I/O 16×DI/16×DO/2×AI/2×AO | Power: AC box 100–240 VAC in / 24 VDC 20.8 A out; DC box 48–72 VDC in/out 20 A; typical consumption 200 W (500 W recommended supply)
- Source: https://www.ufactory.us/product/ufactory-xarm-7 (fetched 2026-07-19)

### KUKA LBR iiwa 7 R800 / 14 R820 — KUKA
- DOF: 7 axes (both variants) | Payload: 7 kg (7 R800) / 14 kg (14 R820) | Reach: 800 mm (7 R800) / 820 mm (14 R820) | Protection class: IP54 | Controller: KUKA Sunrise Cabinet | Media flange: DIN ISO 9409-1-50-7-M6 | Torque sensors in all 7 axes; torque accuracy ±2% of max torque | Mounting: ceiling, floor, wall
- Source: https://www.kuka.com/en-us/products/robotics-systems/industrial-robots/lbr-iiwa (fetched 2026-07-19); repeatability (±0.1 mm) and weight (24 kg, aluminum construction) figures per manufacturer literature located via live search, not independently re-parsed from PDF

### SO-101 — TheRobotStudio / Hugging Face LeRobot
- DOF: 6 (5 arm joints + 1 gripper) | Actuators (follower arm): 6× Feetech STS3215 smart servos, per-joint gear ratios 1/345, 1/191, 1/191, 1/147, 1/147, 1/147 (base/shoulder-pan, shoulder-lift, elbow-flex, wrist-flex, wrist-roll, gripper); leader arm uses differently-geared motors on the same joints | Stall torque: 16.5 kg·cm at 7.4 V (base kit) or up to 30 kg·cm at 12 V (Pro kit) | Control interface: USB-C serial via motor-bus controller board; software integration via Hugging Face LeRobot (`lerobot-calibrate`, `lerobot-setup-motors`) | Payload, reach, weight: not specified on official assembly documentation
- Source: https://huggingface.co/docs/lerobot/so101 and https://github.com/TheRobotStudio/SO-ARM100 (fetched 2026-07-19)

### ALOHA ViperX-300 6DOF — Trossen Robotics (Interbotix X-Series)
- DOF: 6 | Reach: 750 mm | Total span: 1500 mm | Repeatability: 1 mm | Accuracy: 5–8 mm | Working payload: 750 g (rated within max reach; ≤50% arm extension recommended at rated payload) | Actuators: 9 total servos — 7× Dynamixel XM540-W270 (primary), 2× XM430-W350 (wrist/gripper), 1 Mbps bus | Gripper range: 42–116 mm | Waist rotation: ±180°
- Source: https://docs.trossenrobotics.com/interbotix_xsarms_docs/specifications/avx300s.html (fetched 2026-07-19)

## Humanoid and legged platforms

### Unitree G1 — Unitree Robotics
- Height: 1320 mm standing / 690 mm folded | Weight: approx. 35 kg (with battery) | DOF: 23 (standard) up to 43 (EDU, with optional 3-finger Dex3-1 hands) | Per-leg DOF: 6 | Per-arm DOF: 5 | Waist DOF: 1 (2 additional optional) | Joint ranges: waist Z ±155° (EDU adds X/Y ±30°), knee 0–165°, hip pitch ±154°/roll −30° to +170°/yaw ±158°, wrist pitch/yaw ±92.5° | Max knee torque: 90 N·m (standard) / 120 N·m (EDU) | Arm payload: approx. 2 kg (standard) / 3 kg (EDU) | Battery: 13-string Li-ion, 9000 mAh | Runtime: approx. 2 h | Sensing: depth camera + 3D LiDAR | Compute: 8-core CPU | Connectivity: Wi-Fi 6, Bluetooth 5.2
- Source: https://www.unitree.com/g1/ (fetched 2026-07-19)

### Unitree H1 — Unitree Robotics
- Height: approx. 180 cm | Weight: approx. 47 kg | Per-leg DOF: 5 (hip×3, knee×1, ankle×1) | Per-arm DOF: 4 (expandable) | Arm segment length: 338 mm ×2 | Leg segments: 400 mm ×2 (thigh + calf) | Joint torque: knee approx. 360 N·m, hip approx. 220 N·m, ankle approx. 59 N·m, arm joints approx. 75 N·m | Peak torque density: 189 N·m/kg | Max speed: 3.3 m/s (manufacturer-stated record); potential mobility >5 m/s | Battery: 15 Ah (0.864 kWh), max voltage 67.2 V | Sensing: 3D LiDAR + depth camera (360° depth perception) | Compute: Intel Core i5 (standard) / i7 (development)
- Source: https://www.unitree.com/h1/ (fetched 2026-07-19)

### Unitree Go2 — Unitree Robotics
- DOF: 12 (3 per leg) | Dimensions: 70×31×40 cm standing, 76×31×20 cm crouching | Weight: approx. 15 kg (with battery) | Max speed: Air 2.5 m/s (5 m/s peak) / Pro 3.5 m/s (5 m/s peak) / Edu 3.7 m/s (5 m/s peak) | Payload: Air approx. 7 kg (max 10 kg), Pro approx. 8 kg (max 10 kg), Edu approx. 8 kg (max 12 kg) | Battery: 8000 mAh (236.8 Wh) standard, 15000 mAh (432 Wh) optional; runtime 1–4 h depending on variant | Max climb angle: 30° (Air) / 40° (Pro, Edu) | Sensing: 3D wide-angle LiDAR, HD wide-angle camera; Edu adds foot-end force sensors | Compute: 8-core CPU (Pro/Edu); Edu supports optional NVIDIA Jetson Orin modules up to 100 TOPS
- Source: https://www.docs.quadruped.de/projects/go2/html/Overview_1.html and https://shop.unitree.com/products/unitree-go2 (fetched 2026-07-19)

### Boston Dynamics Spot — Boston Dynamics
- Dimensions: length 1100 mm, width 500 mm, height (sitting) 191 mm, default walking height 610 mm (min 520 mm, max 700 mm) | Weight: 33.8 kg (net, with battery) | Max payload: 14 kg | Payload mounting area: 850×240×270 mm | Max speed: 1.6 m/s | Max slope: ±30° | Max step height: 300 mm | Battery: 564–605 Wh (source pages vary), average runtime 90 min, standby 180 min, recharge 60–120 min | IP rating: IP54 | Operating temperature: −20°C to 55°C | Terrain sensing: 360° horizontal coverage, 4 m range, >2 lux lighting requirement | Connectivity: Wi-Fi 2.4/5 GHz b/g/n, Ethernet; payload connectors 2× DB25, unregulated DC 35–58.8 V at 150 W per port
- Source: https://bostondynamics.com/products/spot/ and https://support.bostondynamics.com/s/article/Spot-Specifications-49916 (fetched 2026-07-19)

### Atlas (Electric) — Boston Dynamics
- Height: 1.9 m | Weight: 90 kg | DOF: 56 | Reach: 2.3 m | Weight capacity: 50 kg instant / 30 kg sustained | Battery life: approx. 4 h (self-swappable) | IP rating: IP67 | Operating temperature: −20°C to 40°C | Sensing: tactile sensing, 360° camera coverage
- Source: https://bostondynamics.com/products/atlas/ (fetched 2026-07-19)

### Digit — Agility Robotics
- Payload: 35 lb (approx. 15.9 kg) | Battery life: approx. 4 h | Design: human-centric bipedal form factor, reverse-jointed legs, interchangeable end effectors | Height, weight, DOF, max speed: not specified on the fetched public product page (full specification sheet is gated behind an "Access Spec Sheet" request form)
- Source: https://agilityrobotics.com/robots (fetched 2026-07-19)

### Booster T1 — Booster Robotics
- Height: approx. 1.2 m | Weight: approx. 30 kg | Dimensions: 118×47×23 cm | Leg length: 57 cm | Arm length: 45 cm | DOF: 23 standard (6 per leg ×2, 4 per arm ×2, 1 waist, 2 head) / 31 with grippers / 41 with dexterous hands | Peak joint torque: 130 N·m | Joint ranges: waist ±58°, hip pitch ±118° / roll −21° to 88° / yaw ±58°, knee 0–123°, ankle pitch −50° to 20° / roll ±25° | Speed: 0.97 m/s | Battery: 10.5 Ah; walking endurance approx. 2 h, standing endurance approx. 4 h | Compute: NVIDIA AGX Orin (200 TOPS) + Intel i7-1370P CPU | Sensing: depth camera, 9-axis IMU, 6-mic circular array + speaker | Connectivity: Wi-Fi 6, Bluetooth 5.2, USB, Ethernet
- Source: https://www.booster.tech/booster-t1/ (fetched 2026-07-19)

## Mobile bases

### Tracer 2.0 — AgileX Robotics
- Drive type: two-wheel differential AGV | Max speed: 2 m/s | Payload: 150 kg | Runtime: 6 h | Motors: 400 W | Battery: 30 Ah | IP rating: IP22 | Operating temperature: −10°C to 40°C | Obstacle capability: 10 mm step, 25 mm gap | Interface: CAN bus, open-source SDK | Note: dimensions and total vehicle weight not specified on the fetched product page
- Source: https://global.agilex.ai/products/tracer (fetched 2026-07-19)

## End-effectors and grippers

### 2F-85 / 2F-140 — Robotiq
- Stroke: 85 mm (2F-85) / 140 mm (2F-140) | Grasp force: 20–235 N (2F-85) / 10–125 N (2F-140) | Finger speed: 20–150 mm/s (2F-85) / 30–250 mm/s (2F-140) | Weight: 925 g (2F-85) / 1025 g (2F-140) | Position repeatability: 0.05 mm (2F-85) / 0.08 mm (2F-140) | Position resolution: 0.4 mm (2F-85) / 0.6 mm (2F-140) | Force repeatability: ±10% | Max payload: 5 kg (both, grasp-type dependent) | Height: 162.8 mm (2F-85) / 232.8 mm (2F-140) | Supply voltage: 24 V DC ±10% (max 28 V) | IP rating: not specified in the fetched instruction manual
- Source: https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_TM_InstructionManual_HTML5_20190503.zip/2F-85_2F-140_TM_InstructionManual_HTML5/Content/6.%20Specifications.htm (fetched 2026-07-19)

### Allegro Hand V4 / V5 — Wonik Robotics
- DOF: V4 16 (4 per finger, 4 fingers incl. thumb) | V5 9-DOF structure with 360° pressure-sensitive tactile sensing; V5 Plus 16-DOF with tactile sensing; V5 Sense 16 pressure-sensing channels (DOF confirmed directly on manufacturer site) | V4 weight: approx. 1.1–1.2 kg | V4 max joint torque: 0.70 N·m | V4 speed: 0.11 s/60° | V4 power: 12–24 VDC, approx. 100–120 W | V4 control: CAN bus, 333 Hz | V5 weight: 1050 g | V5 power: 24 V / 5 A / 120 W | V5 control frequency: 500 Hz via CAN
- Source: http://allegrohand.com/ (fetched 2026-07-19, DOF variants confirmed); V4 weight/torque/power figures per manufacturer datasheet https://www.wonikrobotics.com/upload/board/Allegro%20Hand%20V4_Rev.6,250306_6fac1.pdf (located via live search; direct PDF text extraction was not possible)

### RH56 series dexterous hand — Inspire Robots
- RH56H1: DOF 6, joints 11, weight 470±10 g, static load capacity 8 kg, thumb max force ≥15 N, four-finger force ≥10 N, operating voltage 24–48 V | RH56E2: DOF 6, joints 12, weight 790±10 g, thumb fingertip force 30 N, finger fingertip force 28 N, max fingertip pressure 8 kg
- Source: https://en.inspire-robots.com/product-category/the-dexterous-hands and manufacturer manual https://en.inspire-robots.com/wp-content/uploads/2024/02/INSPIRE-ROBOTS-THE-DEXTEROUS-HAND-RH56-SERIES-USER-MANUAL.pdf (located via live search; numeric fields per that manual, direct PDF text extraction was not possible)

## Sensors

### RealSense D435i — Intel
- Depth technology: stereoscopic, global shutter | Depth resolution: up to 1280×720 | Depth frame rate: up to 90 fps | Depth FOV: 87°×58° (±3°) | Ideal range: 0.3–3 m | Min depth distance: approx. 0.28 m (min-Z ~0.105 m) | Depth accuracy: <2% at 2 m | RGB resolution: 1920×1080 (2 MP), rolling shutter | RGB frame rate: 30 fps | RGB FOV: 69°×42° | IMU: BMI055, 6-DoF (accelerometer + gyroscope) | Dimensions: 90×25×25 mm | Interface: USB-C 3.1 Gen 1 | Mounting: 1× 1/4-20 UNC, 2× M3 | Components: RealSense Module D430 + RGB camera + Vision Processor D4
- Source: https://www.intelrealsense.com/depth-camera-d435i/ (fetched 2026-07-19)

### ZED 2i — Stereolabs
- Resolution: up to 4416×1242 @ 15 fps or 1920×1080 @ 60 fps | Depth range: up to 20 m | Field of view: 110° horizontal / 70° vertical / 120° diagonal | IMU: 9-DOF (accelerometer, gyroscope, magnetometer) with integrated barometer | Sensor: rolling shutter | IP rating: IP66 | Lens options: 2 mm (wide FOV) or 4 mm (extended range/quality)
- Source: https://www.stereolabs.com/store/products/zed-2i, corroborated via manufacturer-hosted datasheet https://www.mouser.com/datasheet/2/1520/StereoLabs_ZED_2i_Datasheet-3401402.pdf (fetched 2026-07-19; direct PDF text extraction was not possible)

### Mid-360 — Livox
- Field of view: 360° horizontal, −7° to 52° vertical | Detection range: 40 m @ 10% reflectivity, 70 m @ 80% reflectivity (100 klx) | Point rate: 200,000 points/s (first return), 10 Hz frame rate | Range precision: ≤2 cm @ 10 m, ≤3 cm @ 0.2 m | Angular precision: <0.15° | Dimensions: 65×65×60 mm | Weight: 265 g | Power: 6.5 W average, 9–27 V DC supply | Interface: 100BASE-TX Ethernet, IEEE 1588-2008 (PTPv2) and GPS sync | IP rating: IP67 | Operating temperature: −4°F to 131°F | Blind zone: 0.1 m | Built-in IMU: yes
- Source: https://www.livoxtech.com/mid-360/specs (fetched 2026-07-19)

### GelSight Mini — GelSight
- Camera: 8 MP, image output 2448×3264 | Sensing area: 21×25 mm | Effective spatial resolution: 240×320 px (approx. 85 µm/pixel) | Gel thickness: 4.25 mm ±0.20 mm | Operating temperature: 0–25°C
- Source: manufacturer-hosted datasheet https://www.gelsight.com/wp-content/uploads/2022/09/GelSight_Datasheet_GSMini_9.20.22b.pdf (located via live search; direct PDF text extraction was not possible; product page https://www.gelsight.com/gelsightmini/ fetched 2026-07-19 did not expose the numeric table in fetchable text)

### Axia80 — ATI Industrial Automation (Novanta)
- Sensing range: Fx/Fy ±500 N, Fz ±900 N, Tx/Ty/Tz ±20 Nm | Resolution: Fx/Fy/Fz 0.025 N, Tx/Ty/Tz 0.00125 Nm | Sample/data rate: 8 kHz | Latency: <1 ms | Accuracy: 2% of full scale | Dimensions: 80 mm diameter × 25.4 mm height | Weight: 0.3 kg | IP rating: IP64 | Interface: EtherCAT, 6-pin M8 (ZC22) connector | Resonant frequency: 2200 Hz (Fx/Fy/Tz), 2600 Hz (Fz/Tx/Ty) | Overload capacity: 5.0–12.5× rated, axis-dependent
- Source: https://ati.novanta.com/product/axia80-force-torque-sensor-kit/ (fetched 2026-07-19)

## Onboard compute

### Jetson AGX Orin — NVIDIA
- AI performance: up to 275 TOPS (sparse INT8) | GPU: 2048-core NVIDIA Ampere architecture, 64 Tensor Cores, 1.3 GHz | CPU: 12-core Arm Cortex-A78AE v8.2 64-bit, 3 MB L2 + 6 MB L3 cache, 2.2 GHz max | Memory: 64 GB 256-bit LPDDR5, 204.8 GB/s bandwidth | Power: 15–60 W configurable (MAXN mode up to 60 W)
- Source: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ (fetched 2026-07-19)

### Jetson Orin NX — NVIDIA
- AI performance: up to 157 TOPS (sparse INT8) | GPU: 1792-core NVIDIA Ampere architecture, 56 Tensor Cores, 1.2 GHz | CPU: 8-core Arm Cortex-A78AE v8.2 64-bit, 2 MB L2 + 4 MB L3 cache, 2.0 GHz max | Memory: 16 GB or 8 GB 128-bit LPDDR5, 102.4 GB/s bandwidth | Power: 10–40 W configurable
- Source: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ (fetched 2026-07-19)

## Coverage notes

- **Dropped for lack of a verifiable manufacturer source**: Fourier GR-2 (fourierintelligence.com/fftai.com is a JS-rendered site; no fetchable spec content found), Intel RealSense D405 (intelrealsense.com and realsenseai.com both failed to resolve/404 in this session), Shadow Hand, ZED 2i exact weight/dimensions/power (not exposed in fetchable page text).
- **Thin verification, kept with caveats**: Digit (Agility Robotics gates its full spec sheet behind an access-request form — only payload and battery life were on the public page); Kinova Gen3, KUKA LBR iiwa repeatability/weight, Allegro Hand V4 numeric fields, Inspire RH56, GelSight Mini, ZED 2i (numbers traced to manufacturer-hosted PDF/store URLs located via live search, but the PDFs themselves could not be parsed as text by the fetch tool in this session — a tool limitation, not a fabricated figure).
- **PDF datasheets that failed to parse** (binary/compressed stream content returned instead of text) despite being live-fetched: Universal Robots UR5e original PDF (worked around via UR's HTML tech-spec page instead), Boston Dynamics Spot spec PDF (worked around via HTML pages), Franka Research 3 PDF, Kinova TS-014 PDF, Stereolabs ZED 2i PDF, GelSight Mini PDF.
- Not covered in this pass: mobile-manipulator bases beyond AgileX Tracer 2.0 (e.g., LeKiwi omni-wheel base — component-level info only, no consolidated dimensions/speed spec found on official channels), Shadow Dexterous Hand, Fourier/Unitree Dex hand end effectors, ZED-Mini/ZED-X variants, Velodyne/Ouster LiDAR, Intel NUC-class compute.
- 25 entries total across 6 buckets: Manipulators (7), Humanoid and legged (7), Mobile bases (1), End-effectors and grippers (3), Sensors (5), Onboard compute (2).

## Sources

- https://www.universal-robots.com/manuals/EN/HTML/SW5_19/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm
- https://franka.de/franka-research-3
- https://franka.de/hubfs/Datasheet%20Franka%20Research%203_R02212_2.2.1_EN.pdf?hsLang=en
- https://www.kinovarobotics.com/product/gen3-robots
- https://www.kinovarobotics.com/sites/default/files/TS-014_KINOVA_Gen3_Ultra_lightweight_robot_7DOF-Specifications_EN_R02%20%281%29.pdf
- https://www.ufactory.us/product/ufactory-xarm-7
- https://www.kuka.com/en-us/products/robotics-systems/industrial-robots/lbr-iiwa
- https://huggingface.co/docs/lerobot/so101
- https://github.com/TheRobotStudio/SO-ARM100
- https://docs.trossenrobotics.com/interbotix_xsarms_docs/specifications/avx300s.html
- https://www.unitree.com/g1/
- https://www.unitree.com/h1/
- https://www.docs.quadruped.de/projects/go2/html/Overview_1.html
- https://shop.unitree.com/products/unitree-go2
- https://bostondynamics.com/products/spot/
- https://support.bostondynamics.com/s/article/Spot-Specifications-49916
- https://bostondynamics.com/products/atlas/
- https://agilityrobotics.com/robots
- https://www.booster.tech/booster-t1/
- https://global.agilex.ai/products/tracer
- https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_TM_InstructionManual_HTML5_20190503.zip/2F-85_2F-140_TM_InstructionManual_HTML5/Content/6.%20Specifications.htm
- http://allegrohand.com/
- https://www.wonikrobotics.com/upload/board/Allegro%20Hand%20V4_Rev.6,250306_6fac1.pdf
- https://en.inspire-robots.com/product-category/the-dexterous-hands
- https://en.inspire-robots.com/wp-content/uploads/2024/02/INSPIRE-ROBOTS-THE-DEXTEROUS-HAND-RH56-SERIES-USER-MANUAL.pdf
- https://www.intelrealsense.com/depth-camera-d435i/
- https://www.stereolabs.com/store/products/zed-2i
- https://www.mouser.com/datasheet/2/1520/StereoLabs_ZED_2i_Datasheet-3401402.pdf
- https://www.livoxtech.com/mid-360/specs
- https://www.gelsight.com/wp-content/uploads/2022/09/GelSight_Datasheet_GSMini_9.20.22b.pdf
- https://www.gelsight.com/gelsightmini/
- https://ati.novanta.com/product/axia80-force-torque-sensor-kit/
- https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/
