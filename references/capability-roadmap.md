# Capability Roadmap

This roadmap turns the official toolkit's broad architecture into a smaller, original path for this repository.

## Current Baseline

- One Codex skill: `SKILL.md`.
- Local MATLAB discovery: `scripts/probe_matlab.py`.
- Local batch runner: `scripts/run_matlab_batch.ps1`.
- Route reference: `references/github-control-routes.md`.
- Agent metadata: `agents/openai.yaml`.

## Priority 1: Verification And Packaging

Goal: make the skill self-checking before adding more capabilities.

- Validate required files and directories.
- Detect broken internal links and missing scripts.
- Detect mojibake or damaged handoff text.
- Confirm that quick-check commands are documented.
- Keep a small `verify_skill_package.py` script as the package smoke test.

## Priority 2: MATLAB MCP Integration Notes

Goal: document how this skill should behave when official MCP tools are available.

- Add a reference note for expected MCP tool coverage: evaluate code, run file, run tests, analyze code, and detect toolboxes.
- Keep the note conceptual; do not copy upstream server configuration.
- Add a quick verification checklist for "MCP connected" versus "MATLAB actually executed".

## Priority 3: CI Examples

Goal: provide original, minimal CI examples for users who want GitHub Actions.

- Add a small workflow example that runs MATLAB tests with MathWorks Actions.
- Clearly mark license-token assumptions.
- Keep CI examples separate from local execution scripts.

## Priority 4: Domain Modules

Goal: split into additional skills only when there is repeated real use.

Candidate modules:

- `matlab-testing`: unit tests, fixtures, coverage, result export.
- `matlab-code-review`: Code Analyzer, API compatibility, vectorization review.
- `simulink-handoff`: model inspection, simulation evidence, artifact safety.
- `matlab-data-analysis`: table/timetable workflows and plot/export hygiene.

Do not create these modules as empty folders. Add them only after at least one real workflow proves the procedure.

## Priority 5: Chinese Agent Operations

Goal: make Chinese-language agent handoffs precise and executable.

- Keep route, availability, command, evidence, and blocker fields in every handoff.
- Prefer short bilingual labels only when they reduce ambiguity.
- Avoid translating official command names or repository identifiers.
