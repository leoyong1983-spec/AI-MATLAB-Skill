# REFPROP MATLAB GitHub Case Studies

Snapshot date: 2026-05-29.

This note distills public GitHub examples of MATLAB-driven REFPROP work into local project guidance. It records patterns and risks only. Do not copy wrapper source, MEX source, prototype files, or example scripts from these repositories into this project unless the user explicitly approves dependency vendoring and license review.

## Repositories Reviewed

| Repository | Route shown | Useful lesson | Local handling |
| --- | --- | --- | --- |
| [mathworks/matlab-interface-refprop-coolprop](https://github.com/mathworks/matlab-interface-refprop-coolprop) | MATLAB `getFluidProperty` facade over REFPROP/CoolProp; REFPROP route requires a one-time MEX build through `createREFPROPmex.m`. | New MATLAB code should prefer a single property facade, explicit units, vectorized calls, optional struct output, reference-state selection, and cautious rapid mode. | Treat as the preferred modern MATLAB-native route for new REFPROP workflows when a compiler and MEX build are acceptable. |
| [usnistgov/REFPROP-wrappers](https://github.com/usnistgov/REFPROP-wrappers) | Official NIST wrapper collection. Its MATLAB README points users to the MathWorks MATLAB-native interface and describes a NIST-supported MATLAB route through Python `ctREFPROP`; legacy MATLAB wrappers remain available but are not the primary supported route. | Keep `refpropm` compatibility for inherited projects, but do not present it as the only or newest route. Separate "MATLAB calls REFPROP through Python" from "Python calls MATLAB Engine". | Use for route taxonomy and troubleshooting; do not vendor legacy wrapper files by default. |
| [engineer-scientist/organic-Rankine-cycle](https://github.com/engineer-scientist/organic-Rankine-cycle) | Engineering MATLAB scripts call `refpropm` for pure and mixed working-fluid ORC calculations. | Engineering models should make units visible in variable names, check feasibility before expensive property calls, and keep REFPROP calls close to thermodynamic state definitions. | Adopt the modeling discipline, not the cycle code. This pattern is closest to local tank/SCV calculation documents. |
| [Lvyuan13/matlab_refprop](https://github.com/Lvyuan13/matlab_refprop) | Minimal 64-bit MATLAB `refpropm` example, including mixture and vapor-quality calls. | Small examples are useful for smoke tests of mixtures, quality `Q`, and multi-output property requests, but provenance and encoding quality vary. | Use only as a conceptual example; do not copy `refpropm.m` or prototype files. |
| [VIAJYNISHAD/REFPROP](https://github.com/VIAJYNISHAD/REFPROP) | MATLAB refrigeration-cycle style REFPROP use. | Simple cycle examples can validate enthalpy-first workflows. | Optional background reference; verify code quality before relying on it. |
| [PhilippLa22/REFPROP-Matlab-Simulink](https://github.com/PhilippLa22/REFPROP-Matlab-Simulink) | MATLAB/Simulink integration tutorial. | Simulink integration is a separate route from script-only MATLAB. | Use only when a task explicitly involves Simulink. |

## Local Route Taxonomy

### Route R1: Legacy `refpropm`

Use this for inherited MATLAB source that already calls:

```matlab
value = refpropm(requestedProperty, input1, value1, input2, value2, fluid);
```

This is the route used by the reviewed hydrogen tank source and is likely the safest route for reproducing legacy engineering results. It depends on `refpropm.m`, prototype files, REFPROP DLL bitness, fluid files, and consistent units.

### Route R2: MathWorks `getFluidProperty`

Use this for new MATLAB code when the user wants a maintained MATLAB-native interface and can run the one-time MEX setup. The route centralizes calls through `getFluidProperty`, with arguments for library location, requested properties, state variables, fluid name or mixture list, composition, mass/molar basis, units, and optional reference-state handling.

This is the preferred target for future reusable examples in this repository because it avoids scattering `refpropm` calls through business code.

### Route R3: MATLAB calling NIST `ctREFPROP` through Python

Use this when a NIST-supported route is more important than MATLAB-native MEX integration, or when the workflow already relies on MATLAB's Python bridge. This is not the same as MATLAB Engine for Python:

- MATLAB Engine for Python means Python starts or controls MATLAB.
- MATLAB plus `ctREFPROP` means MATLAB calls Python, and Python loads REFPROP.

Keep these capability checks separate.

## Recommended Selection Rules

1. Reproducing an existing calculation: use the existing route first, usually `refpropm`.
2. Creating new MATLAB property code: prefer `getFluidProperty` if the MEX build and compiler are available.
3. Needing NIST-supported wrapper behavior from MATLAB: use MATLAB's Python bridge plus `ctREFPROP`.
4. Running headless acceptance checks: keep a tiny `refpropm` or `getFluidProperty` smoke test before running a full engineering model.
5. Building Simulink workflows: treat Simulink REFPROP integration as its own route and require a separate smoke test.

## Smoke Test Patterns

For `refpropm`, use a round trip that proves both forward and inverse states:

```matlab
u = refpropm('U','T',300,'P',1000,'hydrogen');
d = refpropm('D','T',300,'P',1000,'hydrogen');
t = refpropm('T','D',d,'U',u,'hydrogen');
p = refpropm('P','D',d,'U',u,'hydrogen');
disp([u d t p])
```

For `getFluidProperty`, prefer one call that requests multiple properties and records the unit system:

```matlab
libLoc = 'C:\Program Files (x86)\REFPROP';
[h, s, d] = getFluidProperty(libLoc, 'H,S,D', 'T', 300, 'P', 1000, 'Hydrogen', 1, 1, 'MKS');
disp([h s d])
```

For MATLAB plus `ctREFPROP`, prove MATLAB can select Python and instantiate the REFPROP function library before running model code:

```matlab
pyversion
RP = py.ctREFPROP.ctREFPROP.REFPROPFunctionLibrary('C:\Program Files (x86)\REFPROP');
disp(RP.RPVersion())
```

## Risks To Report

- REFPROP itself is proprietary; public repositories usually provide wrappers or examples, not the licensed REFPROP database.
- Unit conventions differ across wrappers and desired unit enums. Record pressure, temperature, enthalpy, entropy, density, and composition basis.
- Legacy `refpropm` wrappers often cache loaded DLL/fluid state. Restart MATLAB or unload the library before debugging path or fluid changes.
- `getFluidProperty` rapid mode can improve loops but should be enabled only after a non-rapid smoke test succeeds.
- MATLAB's Python bridge route depends on MATLAB's configured Python, not the repository `.venv` used by Codex or shell commands.
