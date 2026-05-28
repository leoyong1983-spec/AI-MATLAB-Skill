# AI MATLAB Skill

This repository contains a compact Codex skill for controlling MATLAB from AI agent workflows. It focuses on auditable execution, route selection, local environment checks, and concise handoff evidence.

The project is inspired by the public architecture of MathWorks' MATLAB Agentic Toolkit, but it does not vendor or copy upstream implementation files. The local design intentionally stays smaller: one practical skill, a few probe scripts, and reference notes that help an agent choose the right MATLAB control path.

## What This Project Provides

- A Codex skill entry point: `SKILL.md`.
- Local MATLAB discovery: `scripts/probe_matlab.py`.
- Deterministic MATLAB batch execution: `scripts/run_matlab_batch.ps1`.
- Agent-facing metadata: `agents/openai.yaml`.
- Reference notes for MATLAB MCP, Python Engine, CI, Simulink, and proxy routes.

## Route Priority

Use the narrowest route that proves the requested result:

1. MATLAB MCP tools for interactive agent control, file execution, tests, static checks, and toolbox discovery.
2. MATLAB Engine for Python when Python must orchestrate MATLAB and exchange variables.
3. `matlab -batch` for deterministic local scripts, exports, and repeatable checks.
4. `matlab-actions/*` for GitHub Actions.
5. Simulink Agentic Toolkit for model-based-design tasks.
6. Browser or Jupyter proxy only when an interactive web/notebook session is required.

## Quick Checks

```powershell
python scripts/probe_matlab.py
python scripts/probe_matlab.py --check-engine
python scripts/probe_matlab.py --smoke-test
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -SmokeTest -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -SmokeTest
python scripts/verify_skill_package.py
```

## Evidence Standard

For any meaningful MATLAB run, report:

- selected route and reason;
- MATLAB executable/version if known;
- working directory;
- exact command or tool call;
- exit status, warnings, and key output;
- generated files;
- unverified assumptions or blockers.

## Capability Levels

- Level 0: package self-check. Requires Python only.
- Level 1: MATLAB batch execution. Requires a discoverable `matlab.exe`; PATH is helpful but not required.
- Level 2: Python Engine for MATLAB. Requires `matlab.engine` installed for the active Python environment.

## Local Python Engine Setup

For MATLAB R2025b, use Python 3.9 through 3.12, 64-bit. Prefer a repository-local virtual environment so agent runtimes and system Python installations remain untouched:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install "D:\Program Files\MATLAB\MatlabR2025b\extern\engines\python"
.\.venv\Scripts\python.exe -c "import matlab.engine; eng = matlab.engine.start_matlab(); print(eng.version()); eng.quit()"
.\.venv\Scripts\python.exe scripts/probe_matlab.py --check-engine
```

Install from the local MATLAB `extern\engines\python` directory when matching a specific MATLAB release. Avoid relying on the latest PyPI package unless it is known to match the local MATLAB release.

## Upstream References

- MathWorks MATLAB Agentic Toolkit: https://github.com/matlab/matlab-agentic-toolkit
- MATLAB MCP Core Server: https://github.com/matlab/matlab-mcp-core-server
- MATLAB Engine for Python: https://github.com/mathworks/matlab-engine-for-python
- MATLAB Actions: https://github.com/matlab-actions
