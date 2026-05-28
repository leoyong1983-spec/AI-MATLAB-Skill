# Environment Check

## Date

2026-05-28

## Repository

AI-MATLAB-Skill

## Capability Summary

| Level | Capability | Status | Evidence |
| --- | --- | --- | --- |
| Level 0 | Package self-check | PASS | `python scripts/verify_skill_package.py` returned `status: ok` with no warnings. |
| Level 1 | MATLAB batch execution | PASS | `matlab.exe -batch` and `scripts/run_matlab_batch.ps1 -SmokeTest` returned exit code 0. |
| Level 2 | Python Engine for MATLAB | PASS | Project `.venv` imports `matlab.engine` and `start_matlab()` returns R2025b. |

## MATLAB

- Detected root: `D:\Program Files\MATLAB\MatlabR2025b`
- MATLAB executable: `D:\Program Files\MATLAB\MatlabR2025b\bin\matlab.exe`
- PATH contains MATLAB: No
- Direct batch smoke test: Pass
- Project batch smoke test: Pass
- Version output: `25.2.0.2998904 (R2025b)`

## Python

- Project Python executable: `D:\SKILL\AI-MATLAB-Skill\.venv\Scripts\python.exe`
- Python version: `3.11.15`
- 64-bit: True
- Virtual environment: `.venv`

## MATLAB Engine for Python

- Install source: `D:\Program Files\MATLAB\MatlabR2025b\extern\engines\python`
- Installed package: `matlabengine`
- Installed version: `25.2`
- `import matlab.engine`: Pass
- `start_matlab`: Pass
- MATLAB version from engine: `25.2.0.2998904 (R2025b)`

## Commands

```powershell
python scripts/verify_skill_package.py
python scripts/probe_matlab.py --check-engine
.\.venv\Scripts\python.exe scripts/probe_matlab.py --start-engine --smoke-test
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -SmokeTest -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_matlab_batch.ps1 -SmokeTest
& "D:\Program Files\MATLAB\MatlabR2025b\bin\matlab.exe" -batch "disp(matlabroot); disp(version)"
.\.venv\Scripts\python.exe -c "import matlab.engine; eng = matlab.engine.start_matlab(); print(eng.version()); eng.quit()"
```

## Notes

- `MATLAB not in PATH` is an information/warning condition, not a hard failure, because the scripts resolve the absolute MATLAB executable path.
- Python Engine support is tied to the active Python environment. It is available in the repository-local `.venv`; other Python environments may still report `ModuleNotFoundError`.
- `scripts/run_matlab_batch.ps1` uses direct PowerShell argument passing for `-batch` commands so compound MATLAB statements such as `disp(matlabroot); disp(version)` are preserved.
