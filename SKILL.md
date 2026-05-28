---
name: ai-matlab-skill
description: Control MATLAB from AI agents such as Codex, Claude, custom assistants, "Lobster", or "Hermes". Use when the user asks an agent to run MATLAB code, inspect or execute .m files, call MATLAB from Python, use MATLAB MCP, run MATLAB tests, automate Simulink, verify toolbox availability, or make MATLAB interaction easier for Chinese-language agent conversations.
---

# AI MATLAB Skill

Use this skill to control MATLAB in an auditable, agent-friendly way. Prefer official MathWorks routes first, then fall back to scriptable local routes.

This project learns from MathWorks' official MATLAB Agentic Toolkit at the design level:

- keep agent instructions separate from executable MATLAB routes;
- verify the local MATLAB environment before claiming execution;
- make tests, static checks, and toolbox discovery first-class actions;
- require a short evidence trail for every meaningful run;
- keep human approval in the loop for destructive or broad file operations.

Do not copy files from the official toolkit into this project. Treat the official toolkit as a reference for architecture and workflow quality, then express local guidance in this project's own compact style.

## Route Selection

Choose the narrowest route that satisfies the request:

1. Use the official MATLAB MCP server when the user wants an AI agent to operate MATLAB interactively. Prefer MCP tools for short code evaluation, file execution, MATLAB tests, code analysis, and toolbox discovery when those tools are available.
2. Use MATLAB Engine for Python when a Python workflow must call MATLAB functions, exchange variables, or coordinate MATLAB with Python-side data processing.
3. Use `matlab -batch` when the task is a deterministic local script, test, export, or CI-style run.
4. Use `matlab-actions/*` when the task belongs in GitHub Actions or repository CI.
5. Use Simulink Agentic Toolkit only for Simulink/model-based-design work.
6. Use browser/Jupyter proxy only when the user explicitly needs a browser or notebook session.
7. Use manual user instructions only when automation is blocked by missing software, missing licenses, or missing permissions.

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

## Verification Ladder

For non-trivial work, climb only as high as the task requires:

1. Discover: confirm MATLAB executable, version if available, license state if execution is attempted, and relevant toolbox availability.
2. Analyze: run MATLAB Code Analyzer or the closest available static check for changed `.m` files.
3. Execute: run the smallest deterministic command, file, function, or test set that proves the behavior.
4. Validate: compare generated numeric output, figures, tables, logs, or test results against the user's requested acceptance criteria.
5. Record: report the route, command/tool call, working directory, MATLAB release if known, exit status, warnings, generated files, and any unverified assumptions.

Do not claim that MATLAB executed when only a dry run, repository inspection, or environment probe was performed.

## Execution Rules

- Prefer non-interactive execution for repeatability: MCP tool call, Engine call, or `matlab -batch`.
- Keep user project files in their existing project structure. Put temporary MATLAB scripts, logs, figures, or exported tables in an existing scratch/work/output area when one exists.
- Never run destructive MATLAB commands such as `delete`, `rmdir`, broad `movefile`, `copyfile` overwrite, or shell `system` calls unless the user explicitly asked for that operation and the target path is clear.
- Do not fake MATLAB results. If a run cannot be performed, provide the exact blocker and the command you attempted.
- Capture evidence for engineering tasks: command, code entry point, MATLAB release if known, toolbox assumptions, key numeric output, warnings, and generated file paths.
- Keep repository edits small and explain why each generated file belongs in its directory.
- Prefer project-native tests and fixtures over one-off console experiments once the work touches reusable MATLAB code.
- If a task changes multiple MATLAB files, run a focused test first, then a broader test only if the project already has one.

## Safety Boundaries

- Treat `.slx`, `.mlx`, app files, binary data, generated reports, and model artifacts as structured or binary assets. Do not edit them as plain text unless the format is explicitly text-based.
- Ask for explicit confirmation before overwriting model files, exported reports, tuned parameters, or user data.
- Avoid hidden global state. Set working directories, random seeds, and output paths explicitly when they affect reproducibility.
- When using external references or official MathWorks projects, summarize the idea and adapt it. Do not vendor upstream files unless the user explicitly asks for dependency installation.

## Common Workflows

### Run A MATLAB Command

Use MCP `evaluate_matlab_code` when available. Otherwise use batch mode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -Command "disp(version)"
```

For a project smoke test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -SmokeTest
```

### Run A MATLAB File

Prefer a file entry point with no GUI requirements:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -File "D:\path\to\script.m" -WorkDir "D:\path\to\project"
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
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -Command "results = runtests; assertSuccess(results);"
```

For GitHub Actions, use `matlab-actions/setup-matlab` plus `matlab-actions/run-tests` or `matlab-actions/run-command`.

### Check MATLAB Code

When MCP code analysis is available, use it for changed `.m` files. Otherwise run a batch command that invokes `checkcode` or the project's existing lint/static-analysis entry point.

Example fallback:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -Command "issues = checkcode('myfile.m'); disp(issues)"
```

### Discover Toolboxes

When MCP toolbox discovery is available, use it. Otherwise run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -Command "disp(version); v = ver; disp({v.Name}')"
```

### Work With Simulink

Use Simulink Agentic Toolkit guidance for model inspection, simulation, and generated artifacts. Keep model edits small, save copies when experimenting, and report changed model files explicitly.

### Package Or Handoff

For handoff to another agent or developer, include:

1. selected route and reason,
2. environment probe result,
3. exact command/tool calls already run,
4. generated files and where they were placed,
5. tests/checks that passed or could not be run,
6. blockers, assumptions, and next safe action.

## Chinese Agent Handoff

When the user says "让龙虾调用 MATLAB", "让爱马仕跑一下 MATLAB", or similar, interpret that as an agent-control request. Respond with:

1. selected control route,
2. whether local MATLAB is available,
3. exact command/tool call to run,
4. expected evidence files or console output,
5. any blocker that prevents actual execution.

Keep the handoff concise and executable so another agent can continue without rediscovering the control path.
