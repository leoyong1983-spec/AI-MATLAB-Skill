---
name: ai-matlab-skill
description: Control MATLAB from AI agents such as Codex, Claude, custom assistants, "Lobster", or "Hermes". Use when the user asks an agent to run MATLAB code, inspect or execute .m files, call MATLAB from Python, use MATLAB MCP, run MATLAB tests, automate Simulink, verify toolbox availability, or make MATLAB interaction easier for Chinese-language agent conversations.
---

# AI MATLAB Skill

Use this skill to control MATLAB in an auditable, agent-friendly way. Prefer official MathWorks routes first, then fall back to scriptable local routes.

## Route Selection

Choose the narrowest route that satisfies the request:

1. Use the official MATLAB MCP server when the user wants an AI agent to operate MATLAB interactively.
2. Use MATLAB Engine for Python when a Python workflow must call MATLAB functions and exchange variables.
3. Use `matlab -batch` when the task is a deterministic script, test, export, or CI-style run.
4. Use `matlab-actions/*` when the task is GitHub Actions or repository CI.
5. Use Simulink Agentic Toolkit only for Simulink/model-based-design work.
6. Use browser/Jupyter proxy only when the user explicitly needs a browser or notebook session.

Read `references/github-control-routes.md` when you need repository names, install routes, or tradeoffs.

## First Checks

Before claiming MATLAB can be controlled:

1. Check whether MATLAB exists locally:

```powershell
python scripts/probe_matlab.py
```

2. If Python Engine is needed, check importability:

```powershell
python scripts/probe_matlab.py --check-engine
```

3. If the task requires execution, record the route used, MATLAB path/version if available, working directory, command, and output/error log.

If MATLAB is not installed, not on `PATH`, or license checkout fails, say that directly. Do not substitute GNU Octave unless the user explicitly authorizes it.

## Execution Rules

- Prefer non-interactive execution for repeatability: MCP tool call, Engine call, or `matlab -batch`.
- Keep user project files in their existing project structure. Put temporary MATLAB scripts, logs, figures, or exported tables in an existing scratch/work/output area when one exists.
- Never run destructive MATLAB commands such as `delete`, `rmdir`, broad `movefile`, `copyfile` overwrite, or shell `system` calls unless the user explicitly asked for that operation and the target path is clear.
- Do not fake MATLAB results. If a run cannot be performed, provide the exact blocker and the command you attempted.
- Capture evidence for engineering tasks: command, code entry point, MATLAB release if known, toolbox assumptions, key numeric output, warnings, and generated file paths.

## Common Workflows

### Run A MATLAB Command

Use MCP `evaluate_matlab_code` when available. Otherwise use batch mode:

```powershell
.\scripts\run_matlab_batch.ps1 -Command "disp(version)"
```

### Run A MATLAB File

Prefer a file entry point with no GUI requirements:

```powershell
.\scripts\run_matlab_batch.ps1 -File "D:\path\to\script.m" -WorkDir "D:\path\to\project"
```

### Call MATLAB From Python

Use MATLAB Engine when the task needs Python orchestration or data exchange:

```python
import matlab.engine

eng = matlab.engine.start_matlab()
try:
    result = eng.sqrt(4.0)
finally:
    eng.quit()
```

For an already-open MATLAB session, prefer a shared engine only when the workflow intentionally needs it:

```matlab
matlab.engine.shareEngine
```

Then connect from Python with `matlab.engine.connect_matlab()`.

### Run Tests

For local tests, use MCP test tools if available or batch mode:

```powershell
.\scripts\run_matlab_batch.ps1 -Command "results = runtests; assertSuccess(results);"
```

For GitHub Actions, use `matlab-actions/setup-matlab` plus `matlab-actions/run-tests` or `matlab-actions/run-command`.

### Work With Simulink

Use Simulink Agentic Toolkit guidance for model inspection, simulation, and generated artifacts. Keep model edits small, save copies when experimenting, and report changed model files explicitly.

## Chinese Agent Handoff

When the user says "让龙虾调用 MATLAB", "让爱马仕跑一下 MATLAB", or similar, interpret that as an agent-control request. Respond with:

1. selected control route,
2. whether local MATLAB is available,
3. exact command/tool call to run,
4. expected evidence files or console output,
5. any blocker that prevents actual execution.

Keep the handoff concise and executable so another agent can continue without rediscovering the control path.
