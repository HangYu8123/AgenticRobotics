# Security Policy

## Supported versions

This project is pre-1.0 and evolves on the `main` branch. Security fixes land on
`main`; there is no separate maintenance branch yet.

| Version | Supported |
|---|---|
| `main` (latest) | ✅ |
| tagged pre-releases | ⚠️ best-effort |

## Reporting a vulnerability

**Do not open a public issue for a vulnerability.** Instead, use GitHub's private
[**Report a vulnerability**](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
flow (Security tab → *Report a vulnerability*) so the report stays private until a
fix is available. Include reproduction steps and the affected file/commit.

We aim to acknowledge a report within a few business days.

## Threat model notes specific to this project

- **Objective specs and eval commands are operator-authored input.** The loop runs
  `eval_command` verbatim; the documented **command preflight** (see
  `objective.example.yaml` and `agentic_robot/objective.py`) rejects shell
  metacharacters, unknown placeholders, disallowed executables, and redirection
  outside the run dir. Treat any relaxation of that preflight as security-sensitive.
- **Fetched/model content is data, not instructions** (philosophy §8). Skills that
  pull external content must never feed it into a shell, `eval`, or a file path
  unvalidated.
- **The objective sha256 is an audit record, not a boundary.** Real immutability of
  the objective must be enforced at the harness level (e.g. a Claude Code
  `settings.json` permission rule denying writes to the objective path).
