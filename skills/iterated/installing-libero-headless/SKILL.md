---
name: installing-libero-headless
description: Installs LeRobot's LIBERO sim env (hf-libero) into the repo venv on a headless Linux box. Use when env.type=libero is needed and `import libero` fails.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Install LIBERO headless into the repo venv

## Prerequisites
Repo venv exists at `.venv`; the objective requires `env.type=libero`. Read and
apply `skills/iterated/preparing-runtime/SKILL.md` as the generic setup envelope; the
commands and workarounds below remain LIBERO-specific.

## Do
```bash
# egl-probe wheel build fails under cmake>=4 -> pin policy first, then hf-libero
CMAKE_POLICY_VERSION_MINIMUM=3.5 PYTHONPATH= uv pip install --python .venv/bin/python egl_probe==1.0.2 hf-egl-probe==1.0.2
PYTHONPATH= uv pip install --python .venv/bin/python 'hf-libero>=0.1.4,<0.2.0'
echo n | .venv/bin/python -c "import libero.libero"   # drains interactive first-import prompt (EOFErrors headless)
# smoke test: MUJOCO_GL=egl, build one LiberoEnv(task='libero_object', task_ids=[0]).create_envs(1),
# reset+step, confirm info has is_success (assets auto-download ~600 files to ~/.cache/libero)
```

## Mutates
Repo venv site-packages; `~/.libero/config.yaml`; `~/.cache/libero`.

## Validation
Import + env step succeed with `is_success` in info; later `overall.pc_success` parseable from a real `lerobot-eval`.

## Rollback
`uv pip uninstall hf-libero robosuite robomimic egl-probe hf-egl-probe` (all under `--python .venv/bin/python`).

## Watch out
Always pass `--python <venv-python>` to `uv pip` (uv otherwise may target a different env). `MUJOCO_GL=osmesa` is the fallback if EGL device init fails.

## Evidence
- round 0: enabled preflight eval, `pc_success 2.0`, baseline `53.0` — worked.
