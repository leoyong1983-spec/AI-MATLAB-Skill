#!/usr/bin/env python3
"""Verify this skill package without requiring MATLAB."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "references/github-control-routes.md",
    "references/agentic-toolkit-lessons.md",
    "references/capability-roadmap.md",
    "scripts/probe_matlab.py",
    "scripts/run_matlab_batch.ps1",
]

REQUIRED_SKILL_SECTIONS = [
    "## Route Selection",
    "## First Checks",
    "## Verification Ladder",
    "## Execution Rules",
    "## Safety Boundaries",
    "## Common Workflows",
    "## Chinese Agent Handoff",
]

REQUIRED_README_COMMANDS = [
    "python scripts/probe_matlab.py",
    "python scripts/probe_matlab.py --check-engine",
    "python scripts/probe_matlab.py --smoke-test",
    "powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\run_matlab_batch.ps1 -SmokeTest -DryRun",
    "python scripts/verify_skill_package.py",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")


def check_skill(errors: list[str], warnings: list[str]) -> None:
    path = ROOT / "SKILL.md"
    if not path.is_file():
        return

    text = read_text(path)
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML front matter")

    for section in REQUIRED_SKILL_SECTIONS:
        if section not in text:
            errors.append(f"SKILL.md missing section: {section}")

    if "让龙虾调用 MATLAB" not in text:
        warnings.append("SKILL.md Chinese handoff example is missing or may be corrupted")

    if re.search(r"When the user says.*\?MATLAB", text):
        warnings.append("SKILL.md may contain damaged mojibake text near the Chinese handoff section")

    if "Do not copy files from the official toolkit" not in text:
        warnings.append("SKILL.md should state the no-copy upstream boundary")


def check_readme(errors: list[str], warnings: list[str]) -> None:
    path = ROOT / "README.md"
    if not path.is_file():
        return

    text = read_text(path)
    for command in REQUIRED_README_COMMANDS:
        if command not in text:
            warnings.append(f"README.md missing quick-check command: {command}")

    if "https://github.com/matlab/matlab-agentic-toolkit" not in text:
        warnings.append("README.md missing official toolkit reference URL")


def check_internal_script_links(errors: list[str], warnings: list[str]) -> None:
    docs = [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "references/github-control-routes.md"]
    pattern = re.compile(r"(?:\.\\)?scripts[\\/][A-Za-z0-9_.-]+")

    for doc in docs:
        if not doc.is_file():
            continue
        text = read_text(doc)
        for match in sorted(set(pattern.findall(text))):
            normalized = match.replace(".\\", "").replace("\\", "/")
            if not (ROOT / normalized).is_file():
                warnings.append(f"{doc.relative_to(ROOT)} references missing script: {match}")


def check_agent_metadata(errors: list[str]) -> None:
    path = ROOT / "agents/openai.yaml"
    if not path.is_file():
        return

    text = read_text(path)
    required_fragments = [
        "display_name:",
        "short_description:",
        "default_prompt:",
        "allow_implicit_invocation:",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(f"agents/openai.yaml missing key: {fragment}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the AI MATLAB Skill package.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    check_required_files(errors)
    check_skill(errors, warnings)
    check_readme(errors, warnings)
    check_internal_script_links(errors, warnings)
    check_agent_metadata(errors)

    status = "ok"
    if errors or (args.strict and warnings):
        status = "failed"

    print(
        json.dumps(
            {
                "status": status,
                "root": str(ROOT),
                "errors": errors,
                "warnings": warnings,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
