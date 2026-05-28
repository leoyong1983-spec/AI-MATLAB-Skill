#!/usr/bin/env python3
"""Probe local MATLAB availability without modifying user files."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
from pathlib import Path


def windows_install_roots() -> list[str]:
    roots: list[str] = []
    for base in (Path("C:/Program Files/MATLAB"), Path("D:/Program Files/MATLAB")):
        if base.exists():
            roots.extend(str(child) for child in sorted(base.iterdir()) if child.is_dir())
    return roots


def mac_install_roots() -> list[str]:
    base = Path("/Applications")
    if not base.exists():
        return []
    return [str(child) for child in sorted(base.glob("MATLAB_*.app"))]


def linux_install_roots() -> list[str]:
    roots: list[str] = []
    for base in (Path("/usr/local/MATLAB"), Path("/opt/MATLAB")):
        if base.exists():
            roots.extend(str(child) for child in sorted(base.iterdir()) if child.is_dir())
    return roots


def common_install_roots() -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return windows_install_roots()
    if system == "darwin":
        return mac_install_roots()
    return linux_install_roots()


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe MATLAB availability.")
    parser.add_argument("--check-engine", action="store_true", help="Check whether matlab.engine imports.")
    parser.add_argument(
        "--start-engine",
        action="store_true",
        help="Actually start MATLAB through Python Engine. This can take time and may require a license.",
    )
    args = parser.parse_args()

    matlab_on_path = shutil.which("matlab")
    env_roots = {
        key: os.environ.get(key)
        for key in ("MATLAB_ROOT", "MW_MATLAB_ROOT", "MATLAB_HOME")
        if os.environ.get(key)
    }

    data: dict = {
        "platform": platform.platform(),
        "matlab_on_path": matlab_on_path,
        "env_roots": env_roots,
        "common_install_roots": common_install_roots(),
    }

    if args.check_engine or args.start_engine:
        data["python_engine"] = check_engine(args.start_engine)

    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
