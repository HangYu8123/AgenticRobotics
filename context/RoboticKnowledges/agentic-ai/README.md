# Agentic AI

> Part of the AgenticRobotics robotic knowledge base (`context/RoboticKnowledges/`). Reference material for operators and agents; **not** a runtime dependency of `robot_agentic_training_flow.md`.
> Compiled 2026-07-19 from live web sources. Every entry cites a fetched URL. Star counts and report dates are as fetched on 2026-07-19 and go stale quickly.

## What this is

A snapshot of the live agentic-AI research and tooling landscape as of 2026-07-19: recent papers on LLM agent architectures, tool use, multi-agent orchestration, memory, evaluation, and safety; the GitHub ecosystem around the open Agent Skills format (directly relevant since this repo's `skills/*/SKILL.md` follow that format); and the newest OpenAI and Anthropic technical/system reports. This repo (`AgenticRobotics`) is itself an agentic system — an LLM controller delegating to subagents with a growing skill library — so this category is directly load-bearing context, not incidental background.

## Newest papers (2025–2026)

### Prismata: Confining Cross-Site Prompt Injection in Web Agents
**[Prismata: Confining Cross-Site Prompt Injection in Web Agents](https://arxiv.org/abs/2607.08147)** — arXiv:2607.08147, July 2026
- *Contribution:* Introduces a defense that enforces contextual least privilege for autonomous web agents by labeling page content by trustworthiness and restricting agent capabilities accordingly.
- *Results:* Substantially reduces attack success across published web-agent exploits, including adaptive variants, while preserving functionality for legitimate browsing tasks.

### Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering
**[Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering](https://arxiv.org/abs/2606.17799)** — arXiv:2606.17799, June 2026
- *Contribution:* Argues current coding benchmarks evaluate agentic software-engineering systems as monolithic models rather than decomposing scaffold, tools, and base model.
- *Results:* Identifies three failure modes — model/system conflation, single-reference-solution penalties, and missing component-level metrics — that make iterative improvement hard to diagnose from end-to-end scores alone.

### From Chatbot to Digital Colleague: The Paradigm Shift Toward Persistent Autonomous AI
**[From Chatbot to Digital Colleague: The Paradigm Shift Toward Persistent Autonomous AI](https://arxiv.org/abs/2606.14502)** — arXiv:2606.14502, June 2026
- *Contribution:* Frames the shift from conversational LLMs to persistent, tool-augmented autonomous systems along cognitive-processing and task-execution dimensions, proposing a "Workspace + Skill" paradigm for experience retention.
- *Results:* Argues evaluation should move from static benchmarks toward sandboxed, auditable, self-evolving AI ecosystems, though this section is conceptual/positional rather than empirical.

### Agent Planning Benchmark: A Diagnostic Framework for Planning Capabilities in LLM Agents
**[Agent Planning Benchmark: A Diagnostic Framework for Planning Capabilities in LLM Agents](https://arxiv.org/abs/2606.04874)** — arXiv:2606.04874, June 2026
- *Contribution:* Introduces APB, a planning-specific diagnostic benchmark with 4,209 multimodal cases across 22 domains that isolates planning from execution.
- *Results:* Testing 12 multimodal models found systematic weaknesses in long-horizon planning, tool-noise robustness, calibrated refusal, and inference-time refinement; APB-guided fine-tuning improved plan correctness and downstream execution.

### Domain-Conditioned Safety in Frontier Computer-Using Agents
**[Domain-Conditioned Safety in Frontier Computer-Using Agents: A 793-Episode Browser Benchmark, a Coding-Domain Cross-Reference, and a Reproducibility Audit of Recent Red-Teaming](https://arxiv.org/abs/2606.05233)** — arXiv:2606.05233, June 2026
- *Contribution:* Releases a reproducible 793-episode browser benchmark to re-test whether previously reported prompt-injection attack rates against computer-using agents still hold on current frontier models.
- *Results:* Hand-crafted browser attacks against Claude Sonnet 4.6 and GPT-5.4 yielded 0 successful multi-step attacks (≤2.6% upper bound), yet the same models remained vulnerable to skill-injection attacks in a coding domain — safety hardening is domain-specific, not comprehensive.

### Reinforcement Learning for LLM-based Multi-Agent Systems through Orchestration Traces
**[Reinforcement Learning for LLM-based Multi-Agent Systems through Orchestration Traces](https://arxiv.org/abs/2605.02801)** — arXiv:2605.02801, May 2026
- *Contribution:* Proposes "orchestration traces" — temporal interaction graphs of multi-agent coordination events — as a unifying framework for studying RL training of LLM-based multi-agent systems.
- *Results:* Surveys eight reward families, eight credit-bearing units, and five orchestration sub-decisions, and reports a gap between publicly reported industry deployment practices and open academic RL evaluation regimes.

### The Blind Spot of Agent Safety
**[The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents](https://arxiv.org/abs/2604.10577)** — arXiv:2604.10577, April 2026
- *Contribution:* Introduces OS-BLIND, a 300-task benchmark evaluating computer-use agents on harmless-sounding instructions whose execution context or outcome is harmful.
- *Results:* Most evaluated agents exceed 90% attack success rate under this framing (Claude 4.5 Sonnet at 73.0%), rising to 92.7% in multi-agent deployments where task decomposition obscures harmful intent from safety checks.

### ClawsBench: Evaluating Capability and Safety of LLM Productivity Agents in Simulated Workspaces
**[ClawsBench: Evaluating Capability and Safety of LLM Productivity Agents in Simulated Workspaces](https://arxiv.org/abs/2604.05172)** — arXiv:2604.05172, April 2026
- *Contribution:* Introduces a benchmark with five high-fidelity mock productivity services and 44 structured tasks to evaluate agents on realistic, stateful, multi-service workflows without touching live services.
- *Results:* With full scaffolding, agents reach 39–64% task success but exhibit 7–33% unsafe-action rates, with consistent capability tiers but divergent safety profiles across models.

### AgentDropoutV2: Optimizing Information Flow in Multi-Agent Systems via Test-Time Rectify-or-Reject Pruning
**[AgentDropoutV2: Optimizing Information Flow in Multi-Agent Systems via Test-Time Rectify-or-Reject Pruning](https://arxiv.org/abs/2602.23258)** — arXiv:2602.23258, February 2026
- *Contribution:* Proposes a test-time framework that intercepts multi-agent outputs and applies retrieval-augmented correction guided by historical failure patterns to prune bad information flow.
- *Results:* Improves average accuracy by 6.39 points on math benchmarks and 2.28 points on code benchmarks across both fixed and dynamic multi-agent frameworks.

### AdaptOrch: Task-Adaptive Multi-Agent Orchestration in the Era of LLM Performance Convergence
**[AdaptOrch: Task-Adaptive Multi-Agent Orchestration in the Era of LLM Performance Convergence](https://arxiv.org/abs/2602.16873)** — arXiv:2602.16873, February 2026
- *Contribution:* Treats orchestration topology itself (parallel, sequential, hierarchical, hybrid) as the optimization target once underlying LLM performance converges across providers.
- *Results:* Reports 12–23% improvement over static single-topology baselines using identical underlying models, across coding, reasoning, and retrieval tasks.

### Toward Efficient Agents: Memory, Tool learning, and Planning
**[Toward Efficient Agents: Memory, Tool learning, and Planning](https://arxiv.org/abs/2601.14192)** — arXiv:2601.14192, January 2026
- *Contribution:* Surveys efficiency techniques across agent memory, tool learning, and planning, aimed at bounding latency, token cost, and step count.
- *Results:* Identifies shared principles — context compression/management, RL rewards that minimize tool calls, controlled search — and proposes Pareto-frontier evaluation of effectiveness vs. cost.

### VIGIL: Defending LLM Agents Against Tool Stream Injection via Verify-Before-Commit
**[VIGIL: Defending LLM Agents Against Tool Stream Injection via Verify-Before-Commit](https://arxiv.org/abs/2601.05755)** — arXiv:2601.05755, January 2026
- *Contribution:* Introduces a "verify-before-commit" protocol that defends agents against indirect prompt injection carried in tool-call results, without collapsing reasoning flexibility.
- *Results:* Reduces attack success rate by over 22 points versus existing dynamic defenses and more than doubles task utility under attack relative to static baselines.

### AI Agent Systems: Architectures, Applications, and Evaluation
**[AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/abs/2601.01743)** — arXiv:2601.01743, January 2026
- *Contribution:* Presents a unified taxonomy of agent architectures spanning deliberation/reasoning, planning/control, and tool interaction.
- *Results:* Survey-level: highlights latency-vs-accuracy and autonomy-vs-controllability trade-offs, and flags non-determinism, long-horizon credit assignment, and hidden operational cost as open evaluation challenges.

## Agent-skills GitHub repositories

| Repo | URL | Stars (fetched 2026-07-19) | Notes |
|---|---|---|---|
| `anthropics/skills` | https://github.com/anthropics/skills | 163k | Official Anthropic Agent Skills repo; this repo vendors `skill-creator` from it. Skills spanning creative, technical, and enterprise workflows. |
| `ComposioHQ/awesome-claude-skills` | https://github.com/ComposioHQ/awesome-claude-skills | 68.1k | Curated collection of 1000+ production-ready Claude Skills and plugins across Claude.ai, Claude Code, Cursor, Gemini CLI. Scout's snippet claimed 60k — the fetched figure (68.1k) supersedes it. |
| `VoltAgent/awesome-agent-skills` | https://github.com/VoltAgent/awesome-agent-skills | 28.4k | Curated collection of 1000+ agent skills from official teams (Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma) and the community; compatible with Claude Code, Codex, Gemini CLI, Cursor. |
| `benjaminasterA/antigravity-awesome-skills` | https://github.com/benjaminasterA/antigravity-awesome-skills | 60 | Collection of 889+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity. The scout's snippet claimed 22,034 stars — **not confirmed**; the actual top-ranked repo of this name has only 60 stars. Treat the 22,034 figure as false/unverifiable. |

**agentskills.io** (https://agentskills.io) — the open Agent Skills format specification site. Confirms the format ("a folder with a `SKILL.md` file, discovered via progressive disclosure") was originated by Anthropic and released as an open standard, now adopted by 40+ agent products (Cursor, Gemini CLI, GitHub Copilot, VS Code, OpenAI Codex, Goose, OpenHands, and others per its client showcase). Open-source discussion at `github.com/agentskills/agentskills` (linked from the site; not independently star-verified here).

## OpenAI technical and system reports (newest first)

Source: https://deploymentsafety.openai.com/ (fetched 2026-07-19). Five reports newer than the scout's April-2026 cutoff were found.

| Title | Date | URL |
|---|---|---|
| GPT-5.6 System Card | Jul 09, 2026 | https://deploymentsafety.openai.com/gpt-5-6 |
| GPT-Live System Card | Jul 08, 2026 | https://deploymentsafety.openai.com/gpt-live |
| GPT-5.6 Preview System Card | Jun 26, 2026 | https://deploymentsafety.openai.com/gpt-5-6-preview |
| GPT-Rosalind-5.5 System Card | Jun 03, 2026 | https://deploymentsafety.openai.com/gpt-rosalind-5-5 |
| GPT-5.5 Instant System Card | May 05, 2026 | https://deploymentsafety.openai.com/gpt-5-5-instant |
| GPT-5.5 System Card | Apr 23, 2026 | https://deploymentsafety.openai.com/gpt-5-5 |
| ChatGPT Images 2.0 System Card | Apr 21, 2026 | https://deploymentsafety.openai.com/chatgpt-images-2-0 |
| GPT-5.4 Thinking System Card | Mar 05, 2026 | https://deploymentsafety.openai.com/gpt-5-4-thinking |

GPT-5.6 is described on its card as a three-model family (Sol flagship, Terra lower-cost, Luna — third tier unconfirmed at fetch time). GPT-Rosalind-5.5 is described as a frontier reasoning model. GPT-5.3-Codex (Feb 5 2026), which the scout reported, was not re-confirmed by this fetch (page did not surface it in the visible listing) — treat it as scout-reported/unverified by this pass.

## Anthropic / Claude technical and system reports (newest first)

Source: https://www.anthropic.com/system-cards (fetched 2026-07-19). Both entries the scout flagged as unconfirmed — "Mythos Preview" and a Fable/Mythos card — **are confirmed**: both appear on the primary anthropic.com system-cards listing with live URLs.

| Title | Date | URL |
|---|---|---|
| Claude Sonnet 5 | announced Jun 30, 2026 (page: June 2026) | https://www.anthropic.com/claude-sonnet-5-system-card (PDF: https://www-cdn.anthropic.com/9e6a1044980d8c4ed85669faf9c2a8342e2e9f1e/Claude%20Sonnet%205%20System%20Card.pdf) |
| Claude Fable 5 and Mythos 5 | June 2026 | https://anthropic.com/claude-fable-5-mythos-5-system-card |
| Claude Opus 4.8 | May 2026 | https://anthropic.com/claude-opus-4-8-system-card |
| Claude Opus 4.7 | April 2026 | https://anthropic.com/claude-opus-4-7-system-card |
| Claude Mythos Preview | April 2026 | https://www.anthropic.com/claude-mythos-preview-system-card |
| Claude Sonnet 4.6 | February 2026 | http://anthropic.com/claude-sonnet-4-6-system-card |
| Claude Opus 4.6 | February 2026 | https://anthropic.com/claude-opus-4-6-system-card |

Related, confirmed from https://www.anthropic.com/news: **"Redeploying Fable 5"** (Jun 30, 2026, `/news/redeploying-fable-5`) — Fable 5 returns globally July 1 after a jailbreak-severity-framework proposal with Amazon, Microsoft, Google, and other Glasswing partners; and **"More details on Fable 5's cyber safeguards and our jailbreak framework"** (Jul 2, 2026, `/news/fable-safeguards-jailbreak-framework`).

### Agent-relevant engineering / research posts (anthropic.com/engineering, fetched 2026-07-19)

| Title | Date | URL |
|---|---|---|
| Code execution with MCP: Building more efficient agents | Nov 04, 2025 | https://www.anthropic.com/engineering/code-execution-with-mcp |
| Equipping agents for the real world with Agent Skills | Oct 16, 2025 | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| Effective context engineering for AI agents | Sep 29, 2025 | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| Desktop Extensions: One-click MCP server installation for Claude Desktop | Jun 26, 2025 | https://www.anthropic.com/engineering/desktop-extensions |
| How we built our multi-agent research system | Jun 13, 2025 | https://www.anthropic.com/engineering/multi-agent-research-system |

All five predate 2026; no newer agent-relevant engineering/research posts were found on the fetched `/engineering` listing as of 2026-07-19.

## Coverage notes

- **Papers:** 13 papers, all arXiv, dated January–July 2026 (none from 2025 made the newest-first cut given strong 2026 availability). Threads covered: architectures/planning (APB, AI Agent Systems survey), tool use (VIGIL), multi-agent orchestration (RL-orchestration-traces, AdaptOrch, AgentDropoutV2), memory (Toward Efficient Agents), evaluation benchmarks (APB, ClawsBench, Position paper), self-improvement framing (From Chatbot to Digital Colleague), computer-use agents and safety/prompt injection (Prismata, Domain-Conditioned Safety, Blind Spot of Agent Safety). No dedicated "agent reliability/failure modes" paper distinct from the safety/eval papers above was fetched and verified within the session's search budget — treat that thread as thinly covered.
- **GitHub star counts:** all four table entries were fetched directly on 2026-07-19. The scout's unverified `ComposioHQ/awesome-claude-skills` figure (60k) was superseded by the fetched 68.1k. The scout's unverified `antigravity-awesome-skills` figure (22,034 stars) is **contradicted** by direct fetch — the actual top repo of that name has 60 stars; report the 22,034 figure as false.
- **OpenAI hub:** re-checking `deploymentsafety.openai.com` surfaced five reports newer than the scout's April-2026 ceiling, up to GPT-5.6 (Jul 09, 2026) and GPT-Live (Jul 08, 2026).
- **Anthropic hub:** both previously-unconfirmed Mythos-related entries are now confirmed directly from `anthropic.com/system-cards` with live URLs — no entries dropped.
- **Session constraint:** the shared `WebSearch` budget (200 calls) was exhausted partway through this task by concurrent sibling subagents; all research after that point used `WebFetch` only, against URLs already discovered or directly guessed (arXiv abstract pages, known GitHub repo paths, known Anthropic/OpenAI page paths). No prior-knowledge claims were substituted for unavailable searches — where a lead couldn't be fetched, it was omitted rather than guessed.

## Sources

- https://arxiv.org/abs/2607.08147
- https://arxiv.org/abs/2606.17799
- https://arxiv.org/abs/2606.14502
- https://arxiv.org/abs/2606.04874
- https://arxiv.org/abs/2606.05233
- https://arxiv.org/abs/2605.02801
- https://arxiv.org/abs/2604.10577
- https://arxiv.org/abs/2604.05172
- https://arxiv.org/abs/2602.23258
- https://arxiv.org/abs/2602.16873
- https://arxiv.org/abs/2601.14192
- https://arxiv.org/abs/2601.05755
- https://arxiv.org/abs/2601.01743
- https://github.com/anthropics/skills
- https://github.com/ComposioHQ/awesome-claude-skills
- https://github.com/VoltAgent/awesome-agent-skills
- https://github.com/benjaminasterA/antigravity-awesome-skills
- https://agentskills.io
- https://deploymentsafety.openai.com/
- https://www.anthropic.com/system-cards
- https://www.anthropic.com/news
- https://www.anthropic.com/news/claude-sonnet-5
- https://www.anthropic.com/engineering
