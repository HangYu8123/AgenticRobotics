# ROS 1 and ROS 2

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL.

## ROS 1 — in one sentence

ROS 1 is a robotics middleware framework that coordinates nodes through a required central hub process (`roscore`/master) using custom TCP/UDP-based communication protocols (TCPROS/UDPROS). Source: https://www.robosmiths.com/blog/ros2-vs-ros1-2025

## ROS 2 — in one sentence

ROS 2 is a set of open-source software libraries and tools for building robot applications, built on a DDS (Data Distribution Service) middleware layer that enables decentralized, distributed node discovery and communication without a central coordinator. Source: https://design.ros2.org/articles/qos.html (DDS/QoS architecture); definition text via search of docs.ros.org and https://www.robosmiths.com/blog/ros2-vs-ros1-2025

## ROS 1 — known issues and challenges

- **`roscore` single point of failure (SPOF)** — All ROS 1 service discovery and parameter lookups depend on one master process; if it dies or crashes, "none of the working compute nodes can accomplish service discovery," parameter lookups begin failing immediately, and no new topic or service connections can be established. If the master restarts, it has typically lost all rosgraph data because that state is memory-only, so recovery generally requires rebooting all computers or restarting the ROS software. Source: https://medium.com/roshub/introducing-vapor-a-high-availability-ros-1-x-master-19d66506cb7a
- **Already-established topic connections survive master loss, but nothing new can start** — once a topic connection is set up peer-to-peer via the master, it can keep flowing without the master, but new topics/services cannot be created while `roscore` is down. Source: https://www.theconstruct.ai/ros2-in-5-mins-003-where-is-roscore-in-ros2/ (via search)
- **ROS 1 (Noetic) is end-of-life** — the ROS PMC formally voted to set the Noetic EOL date to May 31, 2025 (aligned with Ubuntu Focal's end of standard support); no new `ros/rosdistro` PRs are accepted post-EOL and there is no opportunity to fix regressions in binary packages. Source: https://discourse.openrobotics.org/t/ros-noetic-end-of-life-may-31-2025/43160
- **All ROS 1 distributions are now EOL** — endoflife.date lists every ROS 1 distro (Kinetic, Lunar, Melodic, Noetic) as end-of-life, with Noetic's EOL recorded as May 1, 2025 and the site directing users to ROS 2. Source: https://endoflife.date/ros
- **rosdep dependency resolution reports incompletely** — rosdep only surfaces the *last* resolution error per package, so when multiple packages in a build lack OS-specific definitions, users only learn about them one at a time instead of all at once (observed building `ros2_ouster`, where a `pcl_conversions` resolution failure was silently hidden behind a `libpcl-all` error). Source: https://github.com/ros-infrastructure/rosdep/issues/747
- **rosdep silently fails to resolve Python dependencies on old `pip`** — modern `pip show` returns exit code 1 when a package is absent, but older `pip` versions always return 0, so rosdep's "is it installed" check falsely reports Python dependencies as satisfied. Source: https://github.com/ros-infrastructure/rosdep/issues/410 (via search)

## ROS 1 — common mistakes

- **TF "lookup would require extrapolation" errors** — requesting a transform at a timestamp not yet available (or in the future) throws an extrapolation exception; a common trigger is querying during buffer startup/race conditions before a complete set of transforms exists at a common time. Source: https://answers.ros.org/question/204353/tf2-cannot-lookup-transform-lookup-would-require-extrapolation/ (via search)
- **Mixing simulated and wall-clock time across nodes** — the most common cause of extrapolation/timing errors is that some nodes use simulated time (`use_sim_time`) while others don't, or sensor timestamps run slightly ahead of the tf broadcaster, producing clock skew between nodes. Source: https://answers.ros.org/question/204353/tf2-cannot-lookup-transform-lookup-would-require-extrapolation/ (via search)
- **TF extrapolation-into-the-future errors reported against `navigation` stack** — a recurring open issue in `ros-planning/navigation` where costmap/localization lookups throw "Lookup would require extrapolation into the future," typically tied to timing/clock issues rather than a single root cause. Source: https://github.com/ros-planning/navigation/issues/836 (via search)
- **Relying on `roscore` for high-availability deployments without a mitigation plan** — because there is no built-in leader election or master replication, deployments in safety-critical contexts (drones, AMRs, assembly-line control) can be "disastrous if stopped mid-process" when the master fails, unless a third-party HA layer (e.g., DMTCP checkpointing, or a replicated master) is added. Source: https://medium.com/roshub/introducing-vapor-a-high-availability-ros-1-x-master-19d66506cb7a

## ROS 2 — known issues and challenges

- **QoS incompatibility silently prevents pub/sub connections** — publishers and subscribers only match if their QoS settings (reliability, durability, history/depth) are compatible; even when reliability matches, an incompatible durability setting alone will still prevent the connection, with no error surfaced to the user by default. Source: https://design.ros2.org/articles/qos.html
- **Default QoS settings don't work with sensor topics, with no error or data** — subscribing to sensor-style topics (e.g., LiDAR `/scan`) using default QoS parameters can yield "no data, no error" because sensor publishers commonly use `best_effort` reliability with a small queue depth, which is incompatible with the reliable default; the correct QoS profile is not surfaced in standard tutorials. Source: https://github.com/ros2/ros2_documentation/issues/569
- **DDS discovery race can silently drop recorded data in `ros2 bag record`** — a DDS participant-discovery race means the recorder can discover a DataReader before the matching DataWriter, causing it to fall back to default QoS instead of the publisher's actual QoS; when the mismatch involves durability (e.g., publisher `TRANSIENT_LOCAL` vs. recorder defaulting to `VOLATILE`), previously published messages are silently dropped rather than producing a loud error, and observed roughly 3–4 times per 10 recording sessions on the reporting hardware. Source: https://github.com/ros2/rosbag2/issues/967
- **Nodes cannot discover each other with only the loopback interface up** — DDS/RTPS discovery depends on multicast, and multicast is not available over loopback-only configurations, so demo nodes (e.g., talker/listener) fail to connect on isolated systems or minimal ARM boards with no active physical network interface. Source: https://github.com/ros2/rmw_fastrtps/issues/228
- **Docker's default bridge network blocks multicast, breaking discovery** — Docker's default bridge network does not forward multicast traffic between containers, so nodes in separate containers never see each other's discovery announcements; symptoms include empty topic lists and silent discovery failure with no error message. Source: https://markaicode.com/fix-ros2-docker-discovery-issues/
- **Multicast storms with multiple robots on shared networks** — with FastDDS defaults and many topics/nodes across multiple robots on one network, discovery multicast traffic can overwhelm the network (one user reported the network "grinds to a halt, 90% of the time," with messages arriving 10–15 seconds late and even crashing a router); eProsima's suggested mitigations are configuring static "Initial Peers" or switching to a Discovery Server. Source: https://github.com/eProsima/Fast-DDS/discussions/4948
- **Single-threaded executor causes priority inversion and unpredictable latency** — the default single-threaded executor processes all callbacks sequentially, so any blocking callback stalls unrelated pending callbacks, and higher-priority callbacks can be blocked behind lower-priority ones; under load this has been measured with miss rates rising to 74.8% and maximum lateness over two orders of magnitude larger than a multi-threaded configuration in one study. Source: https://arxiv.org/pdf/2601.10722
- **Multi-threaded executor introduces its own priority-inversion and non-determinism risk** — distributing callbacks across threads adds shared-resource contention and potential priority inversion when a high-priority callback waits on a lock held by a low-priority one, and (as of ROS 2 Jazzy per the survey) execution order is no longer predictable, complicating real-time analysis; callback groups must be stored for the lifetime of the node or the executor cannot trigger their callbacks. Source: https://arxiv.org/pdf/2601.10722
- **`ros1_bridge` delivers messages in latency-spiking batches, not a steady stream** — bridging ~100 Hz ROS 1 data through `ros1_bridge` was observed to arrive in bursts of ~10 messages followed by ~20-second gaps even at moderate (~30%) CPU load, raising open questions about how many simultaneously bridged topics the bridge can sustain. Source: https://github.com/ros2/ros1_bridge/issues/206
- **ABI compatibility is a hard constraint on compiled ROS 2 interfaces** — for compiled/linked languages (C/C++), public API/ABI changes (e.g., adding data members, changing function signatures, adding virtual functions, reordering members) are breaking and are restricted to major version bumps; ABI compatibility is "best effort" and applies only to the public-facing API. Source: https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0009.rst (REP 9)

## ROS 2 — common mistakes

- **TF2 extrapolation exceptions from requesting `now()` instead of the latest transform** — requesting a transform at the current wall-clock time (`now()`) often extrapolates into the future because of publisher latency; using `Time(0)` (latest available) or a bounded `timeout` on `lookup_transform` are the effective fixes, while simply enlarging the transform buffer does not help since the buffer holds history, not future data. Source: https://deadends.dev/ros2/tf2-extrapolation-into-future/
- **Inconsistent `use_sim_time` across nodes causes TF timing errors** — if some nodes use simulated time and others use wall-clock time, transform timestamps go out of sync between nodes; the fix is ensuring every node consistently sets `use_sim_time:=true` (or false). Source: https://deadends.dev/ros2/tf2-extrapolation-into-future/
- **Parameter type mismatches with default-typed `declare_parameter`** — because parameter type is inferred from the default value passed to `declare_parameter`, e.g. passing a boolean where an integer was intended is a common mistake, and by default ROS 2 rejects attempts to change a declared parameter's type at runtime; multi-type parameters require explicitly setting `dynamic_typing=True` on the `ParameterDescriptor`. Source: search results citing docs.ros.org / roboticsbackend.com parameter documentation (direct WebFetch of docs.ros.org blocked — see Coverage notes)
- **Forgetting `data_files` in `setup.py` for ROS 2 Python packages** — a common oversight when writing `ament_python` packages is omitting the `data_files` section needed to install package resource/index files, which then prevents `ros2 pkg list`/`ros2 run` from finding the package because it never registers in the ament resource index. Source: https://roboticsknowledgebase.com/wiki/common-platforms/ros/ros2-custom-package/ (via search)
- **Assuming Docker's default network works like bare-metal for discovery** — developers moving a working native ROS 2 setup into Docker frequently hit silent discovery failure because they don't realize the default bridge network drops multicast; the practical mistake is not explicitly choosing `--network host` or configuring unicast/Discovery Server settings for isolated networks. Source: https://markaicode.com/fix-ros2-docker-discovery-issues/

## ROS 1 → ROS 2 migration pitfalls

- **Build system: catkin's "devel space" has no colcon/ament equivalent** — colcon does not support the ROS 1 devel-space concept; `ament_cmake`/`ament_python` packages must declare an explicit install step to work at all, and iterative in-place editing requires remembering to pass `--symlink-install`. Source: https://design.ros2.org/articles/build_tool.html
- **Package not visible to `ros2 run`/`ros2 pkg list` after build** — ROS 2 locates packages via an ament resource index (a marker file under `install/share/ament_index/resource_index/packages/`); if a package fails to register there (e.g., missing Python `data_files`, or a build step misconfiguration), tools silently can't find it even though the build "succeeded." Source: https://roboticsknowledgebase.com/wiki/common-platforms/ros/ros2-custom-package/ (via search)
- **Command-line and environment-variable renames** — `catkin_make`/`catkin build` become `colcon build`; ROS 1's devel-space environment variable model is replaced by `AMENT_PREFIX_PATH`, and CMake-specific variables must now be derived from the generic ament variable. Source: https://design.ros2.org/articles/build_tool.html
- **Launch files: XML → Python, and path resolution breaks** — ROS 1's XML launch files (`<param>`, `<node type=...>`, `$(arg ...)`, `$(find pkg)`) become Python-based launch descriptions in ROS 2 using dictionaries for parameters, `executable=` instead of `type=`, and substitution objects (`FindPackageShare`, `PathJoinSubstitution`) instead of `$(find)`; conditionals move from `if`/`unless` XML attributes to `IfCondition`/`UnlessCondition` objects, and loops move from recursive XML tricks to a dedicated `ForLoop` action. Source: https://github.com/MetroRobots/rosetta_launch
- **`ros1_bridge` only supports message types compiled into it** — the bridge is a compiled C++ program limited to the message/service types available at its own build time; prebuilt binaries cover `ros2/common_interfaces` and `tf2_msgs`, but any custom message type requires rebuilding the bridge from source. Source: search results citing https://github.com/ros2/ros1_bridge (README/issue discussion; direct WebFetch of the README blocked — see Coverage notes)
- **`ros1_bridge` does not map ROS 1's raw `tf/tfMessage`** — only `tf2_msgs` is mapped across the bridge, not the legacy `tf/tfMessage` type, and the dynamic bridge removes `/tf` bridging entirely once the triggering application ends, which can break subsequent runs relying on lookup. Source: search results citing https://answers.ros.org/question/349088/ros1-tf-incompatible-with-ros2-through-ros1-bridge/ (direct WebFetch blocked — see Coverage notes)
- **`ros1_bridge` is not usable at all on Ubuntu 24.04** — Ubuntu 24.04 LTS does not support ROS 1, so `ros1_bridge` (which needs a functioning ROS 1 install on one side) cannot be deployed there, forcing bridge-based migrations onto older host OS versions or containers. Source: search results citing https://github.com/ros2/ros1_bridge (direct WebFetch of the README blocked — see Coverage notes)
- **Architecture shift trades one failure mode for another** — migrating from ROS 1's single-master model (SPOF, but simple and multicast-free) to ROS 2's DDS-based peer discovery (no SPOF, but multicast/QoS/network-dependent) means teams inherit an entirely new class of problems — discovery over Docker/VPN/Wi-Fi, QoS mismatches, and multicast storms — that did not exist under `roscore`. Source: synthesized from https://medium.com/roshub/introducing-vapor-a-high-availability-ros-1-x-master-19d66506cb7a, https://markaicode.com/fix-ros2-docker-discovery-issues/, and https://github.com/eProsima/Fast-DDS/discussions/4948
- **EOL is forcing migration timelines, not just recommending them** — with Noetic EOL as of May 31, 2025, upstream package maintenance has stopped; organizations are advised that continuing to run it can violate compliance/security requirements (e.g., EU Cyber Resilience Act pressure), with Canonical's ROS ESM offered as a paid bridge (patches through 2030) rather than a permanent alternative to migrating. Source: https://ubuntu.com/blog/ros-noetic-is-eol-take-action-to-maintain-fleet-security

## Coverage notes

- **`docs.ros.org` and `ros.org` were largely unreachable via direct `WebFetch`** — nearly every attempt to fetch official ROS 2 documentation pages directly (Releases matrix, TF2 debugging tutorial, Executors concept page, REP index) returned an "Anubis" anti-bot access-denial page instead of content, across multiple mirrors (`docs.ros.org`, the `uni-freiburg.de` mirror, and `ros.org/reps`). Where this happened, the corresponding facts below are sourced from `WebSearch` result snippets (which quote the live page text and provide the source URL) rather than a full `WebFetch` read, and are marked "(via search)" or "direct WebFetch blocked" inline above.
- **Distro support matrix was cross-checked from two working sources instead of the blocked official Releases page**: `https://repo.test.ros2.org/en/jazzy/Releases.html` (a docs.ros.org mirror that did load) and `https://github.com/ros2/ros2/releases` (release-tag dates). As of the fetch, currently active distros were Kilted Kaiju (EOL ~Dec 2026), Jazzy Jalisco (EOL May 2029, LTS), Humble Hawksbill (EOL May 2027), and the newly released Lyrical Luth (first patch release June 23, 2026); Iron Irwini had already reached EOL (Dec 4, 2024).
- **REP 9 (ABI compatibility) content came from the `ros-infrastructure/rep` GitHub raw source** (`raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0009.rst`) since `ros.org/reps/rep-0009.html` itself was blocked.
- Could not verify: exact current numeric ROS 2 QoS-mismatch or discovery-latency figures beyond the specific cases quoted above (e.g., no general benchmark of multicast storm thresholds was found); no official ROS 2 real-time roadmap document was reachable (docs.ros.org blocked), so real-time findings rely on the arXiv survey only.
- 27 distinct URLs were fetched or searched live for this file (21 successful direct `WebFetch` reads; the remainder via `WebSearch` snippets after direct fetch was blocked by anti-bot protection). No claim in this file is from prior/training knowledge.

## Sources

- https://discourse.openrobotics.org/t/ros-noetic-end-of-life-may-31-2025/43160
- https://endoflife.date/ros
- https://ubuntu.com/blog/ros-noetic-is-eol-take-action-to-maintain-fleet-security
- https://repo.test.ros2.org/en/jazzy/Releases.html
- https://github.com/ros2/ros2/releases
- https://design.ros2.org/articles/qos.html
- https://github.com/ros2/ros2_documentation/issues/569
- https://answers.ros.org/question/392676/ros2-galactic-nav2-scan-offering-incompatible-qos/ (via search)
- https://github.com/ros2/rosbag2/issues/967
- https://medium.com/@ultroninverse/mastering-ros-2-qos-profiles-a-practical-field-guide-on-reliability-latency-scalability-b3562eb70a26 (via search)
- https://github.com/ros2/rmw_fastrtps/issues/228
- https://markaicode.com/fix-ros2-docker-discovery-issues/
- https://github.com/eProsima/Fast-DDS/discussions/4948
- https://arxiv.org/pdf/2601.10722
- https://design.ros2.org/articles/build_tool.html
- https://roboticsknowledgebase.com/wiki/common-platforms/ros/ros2-custom-package/ (via search)
- https://docs.ros.org/en/eloquent/Contributing/Migration-Guide.html (via search)
- https://answers.ros.org/question/204353/tf2-cannot-lookup-transform-lookup-would-require-extrapolation/ (via search)
- https://github.com/ros-planning/navigation/issues/836 (via search)
- https://deadends.dev/ros2/tf2-extrapolation-into-future/
- https://foxglove.dev/blog/how-to-use-ros2-parameters
- https://github.com/ros-infrastructure/rosdep/issues/747
- https://github.com/ros-infrastructure/rosdep/issues/410 (via search)
- https://medium.com/roshub/introducing-vapor-a-high-availability-ros-1-x-master-19d66506cb7a
- https://www.theconstruct.ai/ros2-in-5-mins-003-where-is-roscore-in-ros2/ (via search)
- https://github.com/ros2/ros1_bridge/issues/206
- https://github.com/ros2/ros1_bridge (via search)
- https://answers.ros.org/question/349088/ros1-tf-incompatible-with-ros2-through-ros1-bridge/ (via search)
- https://github.com/MetroRobots/rosetta_launch
- https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0009.rst
- https://www.robosmiths.com/blog/ros2-vs-ros1-2025
