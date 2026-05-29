#!/usr/bin/env python3
"""Probe local REFPROP files used by MATLAB refpropm-style wrappers."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path


def common_refprop_roots() -> list[Path]:
    system = platform.system().lower()
    if system == "windows":
        return [
            Path("C:/Program Files/REFPROP"),
            Path("C:/Program Files (x86)/REFPROP"),
            Path("D:/Program Files/REFPROP"),
            Path("D:/REFPROP"),
        ]
    return [
        Path("/usr/local/REFPROP"),
        Path("/opt/REFPROP"),
    ]


def find_refprop_roots(extra_roots: list[str]) -> list[Path]:
    candidates = common_refprop_roots() + [Path(root) for root in extra_roots]
    seen: set[str] = set()
    roots: list[Path] = []
    for root in candidates:
        key = str(root).lower()
        if key in seen:
            continue
        seen.add(key)
        if root.exists() and root.is_dir():
            roots.append(root)
    return roots


def fluid_filename(name: str) -> str:
    upper = name.upper()
    if upper.endswith((".FLD", ".PPF")):
        return upper
    return f"{upper}.FLD"


def inspect_root(root: Path, fluid: str) -> dict:
    dll_candidates = [
        root / "REFPRP64.DLL",
        root / "REFPRP64.dll",
        root / "REFPROP.dll",
        root / "refprop.dll",
    ]
    dlls: list[str] = []
    seen_dlls: set[str] = set()
    for path in dll_candidates:
        if not path.is_file():
            continue
        key = str(path).lower()
        if key in seen_dlls:
            continue
        seen_dlls.add(key)
        dlls.append(str(path))
    fluids_dir = root / "fluids"
    fluid_file = fluids_dir / fluid_filename(fluid)
    hmx_file = fluids_dir / "hmx.bnc"

    return {
        "root": str(root),
        "dlls": dlls,
        "fluids_dir": str(fluids_dir) if fluids_dir.is_dir() else None,
        "fluid_file": str(fluid_file) if fluid_file.is_file() else None,
        "hmx_file": str(hmx_file) if hmx_file.is_file() else None,
        "mixtures_dir": str(root / "mixtures") if (root / "mixtures").is_dir() else None,
    }


def classify(results: list[dict]) -> dict:
    for item in results:
        if item["dlls"] and item["fluids_dir"] and item["fluid_file"] and item["hmx_file"]:
            return {
                "status": "PASS",
                "reason": "REFPROP DLL, fluids directory, target fluid file, and hmx.bnc were found.",
                "selected_root": item["root"],
            }
    if results:
        return {
            "status": "WARN",
            "reason": "A REFPROP directory was found, but at least one required file is missing.",
            "selected_root": results[0]["root"],
        }
    return {
        "status": "FAIL",
        "reason": "No REFPROP installation directory was found in common locations.",
        "selected_root": None,
    }


def matlab_path(path: str | None) -> str:
    if not path:
        return "<REFPROP root>"
    return path.replace("\\", "/")


def refpropm_smoke_test_template(fluid: str) -> list[str]:
    return [
        "which refpropm",
        f"u = refpropm('U','T',300,'P',1000,'{fluid.lower()}');",
        f"d = refpropm('D','T',300,'P',1000,'{fluid.lower()}');",
        f"t = refpropm('T','D',d,'U',u,'{fluid.lower()}');",
        f"p = refpropm('P','D',d,'U',u,'{fluid.lower()}');",
        "disp([u d t p])",
    ]


def get_fluid_property_smoke_test_template(fluid: str, root: str | None) -> list[str]:
    return [
        "which getFluidProperty",
        f"libLoc = '{matlab_path(root)}';",
        f"[h, s, d] = getFluidProperty(libLoc, 'H,S,D', 'T', 300, 'P', 1000, '{fluid.title()}', 1, 1, 'MKS');",
        "disp([h s d])",
    ]


def ctrefprop_smoke_test_template(root: str | None) -> list[str]:
    return [
        "pyversion",
        f"RP = py.ctREFPROP.ctREFPROP.REFPROPFunctionLibrary('{matlab_path(root)}');",
        "disp(RP.RPVersion())",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe local REFPROP files for MATLAB integration.")
    parser.add_argument("--fluid", default="HYDROGEN", help="Fluid file base name, default: HYDROGEN.")
    parser.add_argument("--root", action="append", default=[], help="Additional REFPROP root to inspect.")
    args = parser.parse_args()

    roots = find_refprop_roots(args.root)
    results = [inspect_root(root, args.fluid) for root in roots]
    summary = classify(results)
    selected_root = summary.get("selected_root")

    print(
        json.dumps(
            {
                "platform": platform.platform(),
                "fluid": args.fluid,
                "summary": summary,
                "roots": results,
                "matlab_smoke_test_template": refpropm_smoke_test_template(args.fluid),
                "matlab_smoke_test_templates": {
                    "legacy_refpropm": refpropm_smoke_test_template(args.fluid),
                    "mathworks_getFluidProperty": get_fluid_property_smoke_test_template(args.fluid, selected_root),
                    "matlab_python_ctREFPROP": ctrefprop_smoke_test_template(selected_root),
                },
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if summary["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
