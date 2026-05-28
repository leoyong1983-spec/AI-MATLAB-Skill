# GitHub MATLAB Control Routes

Last researched: 2026-05-20.

Use this reference when selecting a MATLAB control route for an agent, automation script, or CI workflow.

## Preferred Official Projects

- `matlab/matlab-mcp-core-server`: Official MATLAB MCP server for AI applications and coding agents. Prefer this for Codex/Claude/Copilot-style agent control when MCP tools are available.
- `matlab/matlab-agentic-toolkit`: Official agent-oriented MATLAB toolkit. Use it as the main conceptual route for agent-ready MATLAB workflows.
- `matlab/simulink-agentic-toolkit`: Official Simulink-focused agent toolkit. Use it for model inspection, simulation, and model-based-design workflows.
- `mathworks/matlab-engine-for-python`: Official Python package source for MATLAB Engine for Python. Use it when Python must start MATLAB, call functions, and exchange variables.
- `matlab-actions/setup-matlab`: Official GitHub Action to install/configure MATLAB in CI.
- `matlab-actions/run-command`: Official GitHub Action to run MATLAB commands, scripts, functions, and statements.
- `matlab-actions/run-tests`: Official GitHub Action to run MATLAB and Simulink tests and collect artifacts.
- `mathworks/MATLAB-extension-for-vscode`: Official VS Code extension. Use it for editing/debugging support, not as the primary automation backend.
- `mathworks/matlab-proxy` and `mathworks/jupyter-matlab-proxy`: Browser and Jupyter routes. Use only when the task needs notebook or browser access.

## Community Project Worth Knowing

- `jigarbhoye04/MatlabMCP`: Community MCP server based on MATLAB Engine API. Treat it as a reference implementation, not the first production choice when the official MCP server is available.

## Decision Matrix

| Need | Use | Avoid |
| --- | --- | --- |
| AI agent controls MATLAB locally | Official MATLAB MCP server | Ad-hoc GUI automation |
| Python orchestrates MATLAB | MATLAB Engine for Python | Parsing MATLAB console text |
| CI runs MATLAB code/tests | `matlab-actions/*` | Long-lived desktop sessions |
| One deterministic local run | `matlab -batch` | Interactive GUI-only workflow |
| Simulink model work | Simulink Agentic Toolkit | Treating `.slx` files as text |
| Browser/Jupyter access | MATLAB proxy/Jupyter MATLAB proxy | Using proxy as a batch runner |

## Practical Notes

- On Windows, old COM/ActiveX routes such as `Matlab.Application` exist but should be a fallback only. They are platform-specific and less aligned with current MathWorks agent tooling.
- If MATLAB is not on `PATH`, search standard install roots first, then ask the user for the MATLAB executable path.
- For private CI or licensed products, GitHub Actions may need a MathWorks license token such as `MLM_LICENSE_TOKEN`.
- Always separate "MATLAB was executed" from "a route appears installable". Agent reports must not imply execution when only repository research or dry-run checks were done.
