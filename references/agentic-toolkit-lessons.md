# Lessons Adapted From MathWorks MATLAB Agentic Toolkit

Last reviewed: 2026-05-28.

This note records the design lessons adopted from the public MathWorks MATLAB Agentic Toolkit without copying its files or implementation. The goal is to improve this project through interpretation, simplification, and local workflow design.

## What Is Worth Learning

### 1. Separate Capabilities From Agent Instructions

The official toolkit separates agent-facing skills, MCP server configuration, and supporting templates. This project keeps the same separation concept but implements it in a smaller form:

- `SKILL.md` defines behavior and safety rules;
- `scripts/` contains local probes and repeatable execution helpers;
- `references/` explains route tradeoffs and future expansion;
- `agents/` holds agent metadata.

### 2. Make Environment Verification Explicit

A MATLAB agent must not imply that MATLAB ran unless it actually did. This project strengthens that rule with a verification ladder:

1. discover MATLAB and relevant toolboxes;
2. analyze changed MATLAB files;
3. execute the smallest meaningful command, file, or test;
4. validate outputs against requested criteria;
5. record command, route, output, and blockers.

### 3. Treat Tests And Code Analysis As Core Workflows

The official toolkit exposes test and code-analysis oriented routes. This project adapts that idea by requiring agents to prefer MCP test/static-check tools when available and fall back to `matlab -batch` with `runtests` or `checkcode` when MCP is unavailable.

### 4. Keep Destructive Actions Human-Gated

Model files, exported reports, tuned parameters, and user data should not be overwritten casually. This project makes destructive or broad file operations explicit approval points, especially for `.slx`, `.mlx`, app artifacts, generated reports, and data files.

### 5. Support Multiple Agent Hosts Without Bloated Local State

The official toolkit supports multiple agent ecosystems. This repository keeps only lightweight metadata and route notes by default. More host-specific adapters should be added only when they are tested locally or needed by a user workflow.

## Original Improvements In This Project

- A compact route-selection policy that works even when no MCP tool is installed.
- A strict evidence standard for Chinese-language agent handoff.
- A local probe-first workflow that distinguishes dry runs, installability checks, and actual MATLAB execution.
- Directory-light structure suitable for a standalone Codex skill instead of a large multi-skill catalog.
- Explicit "do not copy upstream files" guidance to preserve a clean original project boundary.

## What Not To Import Blindly

- Do not mirror the full official skill catalog unless this repository grows into a maintained multi-domain catalog.
- Do not vendor the MCP server; install or reference the official server as an external dependency.
- Do not create placeholder skills for domains that have not been tested in local MATLAB.
- Do not claim support for a host agent until the adapter has a known install path and verification command.
