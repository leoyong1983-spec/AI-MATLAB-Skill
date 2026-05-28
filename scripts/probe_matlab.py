#!/usr/bin/env python3
"""Probe local MATLAB availability without modifying user files."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


def windows_install_roots() -> list[str]:
    roots: list[str] = []
    for base in (Path("C:/Program Files/MATLAB"), Path("D:/Program Files/MATLAB")):
        if base.exists():
            roots.extend(str(child) for child in sorted(base.iterdir(), reverse=True) if child.is_dir())
    return roots


def mac_install_roots() -> list[str]:
    base = Path("/Applications")
    if not base.exists():
        return []
    return [str(child) for child in sorted(base.glob("MATLAB_*.app"), reverse=True)]


def linux_install_roots() -> list[str]:
    roots: list[str] = []
    for base in (Path("/usr/local/MATLAB"), Path("/opt/MATLAB")):
        if base.exists():
            roots.extend(str(child) for child in sorted(base.iterdir(), reverse=True) if child.is_dir())
    return roots


def common_install_roots() -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return windows_install_roots()
    if system == "darwin":
        return mac_install_roots()
    return linux_install_roots()


def matlab_executable_for_root(root: str) -> str | None:
    path = Path(root)
    if platform.system().lower() == "windows":
        candidate = path / "bin" / "matlab.exe"
    elif platform.system().lower() == "darwin" and path.suffix == ".app":
        candidate = path / "bin" / "matlab"
    else:
        candidate = path / "bin" / "matlab"
    return str(candidate) if candidate.exists() else None


def find_matlab_executable(roots: list[str]) -> tuple[str | None, list[str]]:
    candidates: list[str] = []
    matlab_on_path = shutil.which("matlab")
    if matlab_on_path:
        candidates.append(matlab_on_path)

    for root in roots:
        exe = matlab_executable_for_root(root)
        if exe and exe not in candidates:
            candidates.append(exe)

    return (candidates[0] if candidates else None, candidates)


def run_batch_smoke_test(matlab_executable: str, timeout_seconds: int) -> dict:
    command = [matlab_executable, "-batch", "disp(matlabroot); disp(version)"]
    result: dict = {
        "status": "FAIL",
        "command": command,
        "timeout_seconds": timeout_seconds,
    }

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        result["error"] = f"TimeoutExpired: {exc}"
        return result
    except Exception as exc:  # pragma: no cover - environment dependent
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    result.update(
        {
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "status": "PASS" if completed.returncode == 0 else "FAIL",
        }
    )
    return result


def check_engine(start_engine: bool) -> dict:
    result: dict = {"importable": False, "start_tested": False}
    try:
        import matlab.engine  # type: ignore

        result["importable"] = True
    except Exception as exc:  # pragma: no cover - environment dependent
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    if start_engine:
        result["start_tested"] = True
        try:
            eng = matlab.engine.start_matlab()  # type: ignore[name-defined]
            try:
                result["version"] = eng.version()
            finally:
                eng.quit()
        except Exception as exc:  # pragma: no cover - environment dependent
            result["start_error"] = f"{type(exc).__name__}: {exc}"
    return result


def classify_capabilities(data: dict) -> dict:
    matlab = data["matlab"]
    engine = data.get("python_engine")

    capabilities: dict = {
        "level_0_package_self_check": {
            "status": "NOT_RUN",
            "reason": "Run scripts/verify_skill_package.py to validate package files.",
        }
    }

    if not matlab["executable"]:
        capabilities["level_1_batch_execution"] = {
            "status": "FAIL",
            "reason": "No matlab executable was found on PATH or under common install roots.",
        }
    elif matlab.get("batch_smoke_test", {}).get("status") == "PASS":
        capabilities["level_1_batch_execution"] = {
            "status": "PASS",
            "reason": "matlab executable was found and batch smoke test returned exit code 0.",
        }
    elif matlab.get("batch_smoke_test", {}).get("status") == "FAIL":
        capabilities["level_1_batch_execution"] = {
            "status": "FAIL",
            "reason": "matlab executable was found, but batch smoke test failed.",
        }
    else:
        capabilities["level_1_batch_execution"] = {
            "status": "PASS",
            "reason": "matlab executable was found; run with --smoke-test to prove execution.",
        }

    if not engine:
        capabilities["level_2_python_engine"] = {
            "status": "NOT_RUN",
            "reason": "Run with --check-engine or --start-engine to evaluate matlab.engine.",
        }
    elif not engine.get("importable"):
        capabilities["level_2_python_engine"] = {
            "status": "WARN",
            "reason": "matlab.engine is not importable; only Python-to-MATLAB workflows are affected.",
        }
    elif engine.get("start_tested") and engine.get("start_error"):
        capabilities["level_2_python_engine"] = {
            "status": "FAIL",
            "reason": "matlab.engine imports, but start_matlab failed.",
        }
    elif engine.get("start_tested"):
        capabilities["level_2_python_engine"] = {
            "status": "PASS",
            "reason": "matlab.engine imports and start_matlab returned a MATLAB version.",
        }
    else:
        capabilities["level_2_python_engine"] = {
            "status": "PASS",
            "reason": "matlab.engine imports; run with --start-engine to prove startup.",
        }

    return capabilities


def overall_status(capabilities: dict) -> str:
    statuses = [item["status"] for item in capabilities.values()]
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe MATLAB availability.")
    parser.add_argument("--check-engine", action="store_true", help="Check whether matlab.engine imports.")
    parser.add_argument(
        "--start-engine",
        action="store_true",
        help="Actually start MATLAB through Python Engine. This can take time and may require a license.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Actually start MATLAB with -batch and print matlabroot/version.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Timeout for --smoke-test or --start-engine style checks.",
    )
    args = parser.parse_args()

    matlab_on_path = shutil.which("matlab")
    env_roots = {
        key: os.environ.get(key)
        for key in ("MATLAB_ROOT", "MW_MATLAB_ROOT", "MATLAB_HOME")
        if os.environ.get(key)
    }
    roots = common_install_roots()
    matlab_executable, executable_candidates = find_matlab_executable(roots)

    data: dict = {
        "platform": platform.platform(),
        "matlab": {
            "on_path": matlab_on_path,
            "path_contains_matlab": matlab_on_path is not None,
            "executable": matlab_executable,
            "executable_candidates": executable_candidates,
        },
        "env_roots": env_roots,
        "common_install_roots": roots,
    }

    # Backward-compatible top-level fields for simple consumers.
    data["matlab_on_path"] = matlab_on_path
    data["matlab_executable"] = matlab_executable

    if args.check_engine or args.start_engine:
        data["python_engine"] = check_engine(args.start_engine)

    if args.smoke_test and matlab_executable:
        data["matlab"]["batch_smoke_test"] = run_batch_smoke_test(matlab_executable, args.timeout_seconds)
    elif args.smoke_test:
        data["matlab"]["batch_smoke_test"] = {
            "status": "FAIL",
            "error": "No matlab executable found.",
        }

    data["capabilities"] = classify_capabilities(data)
    data["overall_status"] = overall_status(data["capabilities"])

    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
