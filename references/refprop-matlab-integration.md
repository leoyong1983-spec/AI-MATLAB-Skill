# REFPROP MATLAB Integration

Source reviewed: `储氢容器充放气过程计算软件 源代码V1.0.docx`.

This note records how the reviewed MATLAB App Designer source controls local NIST REFPROP for hydrogen charging/discharging calculations. It is a design interpretation of the source, not a copy of the bundled `refpropm.m` implementation.

## Observed Business-Level Calls

The application does not call REFPROP DLL functions directly in the charging/discharging equations. It calls a MATLAB wrapper named `refpropm`, and that wrapper owns the DLL loading, fluid setup, flash calculation, and property mapping.

The charging model uses hydrogen properties from these calls:

```matlab
U = refpropm('U','T',T,'P',P,'hydrogen');
D = refpropm('D','T',T,'P',P,'hydrogen');
T = refpropm('T','D',D,'U',U,'hydrogen');
P = refpropm('P','D',D,'U',U,'hydrogen');
```

The discharging model uses the same REFPROP pattern. The difference is in the mass and energy balance, not in the property-call route.

Important unit conventions from the wrapper comments:

- `T`: temperature in K.
- `P`: pressure in kPa.
- `D`: density in kg/m^3.
- `U`: internal energy in J/kg.
- `H`: enthalpy in J/kg.
- `S`: entropy in J/(kg K).

When the tank model needs pressure work in Pa-based SI units, it multiplies REFPROP pressure by `1000`.

## Wrapper Control Flow

The reviewed source embeds a classic MATLAB `refpropm` wrapper. Its control flow is:

1. Accept a property request and two state variables:
   `refpropm(prop_req, spec1, value1, spec2, value2, fluidName)`.
2. Select the REFPROP installation root:
   - Windows default: `C:\Program Files\REFPROP\`
   - Windows fallback: `C:\Program Files (x86)\REFPROP\`
   - Unix-like default: `/usr/local/REFPROP/`
3. Select the REFPROP DLL:
   - 32-bit style default: `REFPROP.dll`
   - 64-bit MATLAB on Windows: `REFPRP64.dll`
4. Load the DLL once through MATLAB:
   `loadlibrary(fullDllPath, prototype, 'alias', 'refprop')`.
5. Cache loaded state in MATLAB app data under `RefpropLoadedState`.
6. If the requested fluid changes, call REFPROP setup again:
   - pure or component-list fluids: `SETUPdll`
   - predefined `.mix` mixtures: `SETMIXdll`
7. Choose a REFPROP flash function from the provided state-variable pair.
8. Return the requested output property or properties to the business calculation.

## Flash Function Mapping

The wrapper chooses REFPROP DLL flash functions according to the two independent state variables:

| Inputs | REFPROP call used by wrapper | Typical purpose |
| --- | --- | --- |
| `T`, `P` | `TPFLSHdll` or `TPRHOdll` | Compute density and thermodynamic state from temperature/pressure. |
| `D`, `U` | `DEFLSHdll` | Recover temperature and pressure from density/internal energy. |
| `P`, `D` | `PDFLSHdll` | Recover complete state from pressure/density. |
| `P`, `H` | `PHFLSHdll` or `PHFL1dll` | Enthalpy-pressure flash. |
| `T`, `D` | `TDFLSHdll` | Temperature-density flash. |
| `T`, `Q` | `TQFLSHdll` | Saturation state from temperature/quality. |
| `P`, `Q` | `PQFLSHdll` | Saturation state from pressure/quality. |

After a flash call, the wrapper uses functions such as `THERMdll`, `HEATdll`, and `TRNPRPdll` when requested properties require additional thermodynamic, heating-value, or transport calculations.

## Local Installation Check

On the reviewed machine, REFPROP is installed at:

```text
C:\Program Files (x86)\REFPROP
```

Key files observed:

- `REFPRP64.DLL`
- `refprop.dll`
- `fluids\HYDROGEN.FLD`
- `fluids\hmx.bnc`
- `mixtures\`

This is consistent with the reviewed wrapper's fallback search path.

## Minimal MATLAB Smoke Test

When `refpropm.m`, `rp_proto.m`, and `rp_proto64.m` are available on the MATLAB path, use a small hydrogen property call before trusting a larger tank calculation:

```matlab
which refpropm
u = refpropm('U','T',300,'P',1000,'hydrogen');
d = refpropm('D','T',300,'P',1000,'hydrogen');
t = refpropm('T','D',d,'U',u,'hydrogen');
p = refpropm('P','D',d,'U',u,'hydrogen');
disp([u d t p])
```

Acceptance criteria:

- `which refpropm` resolves to the intended wrapper file.
- The first call loads the REFPROP DLL without `loadlibrary` or missing-file errors.
- `u`, `d`, `t`, and `p` are finite numeric values.
- Recovered `t` is close to `300 K`, and recovered `p` is close to `1000 kPa`.

## Common Failure Points

- REFPROP is installed, but `refpropm.m` and its prototype files are not on the MATLAB path.
- 64-bit MATLAB tries to load a 32-bit DLL, or a 32-bit MATLAB tries to load a 64-bit DLL.
- The wrapper hard-codes `C:\Program Files\REFPROP\`, while the actual installation is under `C:\Program Files (x86)\REFPROP\`.
- `HYDROGEN.FLD` or `hmx.bnc` is missing from the `fluids` directory.
- Pressure units are mixed up: this wrapper expects `P` in kPa, while tank-energy equations may need Pa and therefore multiply by `1000`.
- `RefpropLoadedState` caches the active fluid; if debugging fluid changes, clear MATLAB app data or restart MATLAB before retesting.

## Recommended Agent Handling

For future REFPROP tasks, report capability in layers:

1. REFPROP files: DLL, `fluids`, and target fluid file exist.
2. MATLAB wrapper: `which refpropm` resolves, and prototype files are available.
3. MATLAB-DLL loading: first `refpropm` call succeeds.
4. Property smoke test: hydrogen `T/P -> U/D -> T/P` round trip passes.
5. Business model: charging/discharging loop uses REFPROP values in the intended units.

## GitHub Case-Study Lessons

Public GitHub examples show three practical REFPROP routes for MATLAB:

1. Legacy `refpropm` wrappers, common in older engineering scripts and in the reviewed local hydrogen tank source.
2. MathWorks `getFluidProperty`, a newer MATLAB-native facade that can call REFPROP or CoolProp after a one-time REFPROP MEX setup.
3. MATLAB calling NIST `ctREFPROP` through MATLAB's Python bridge, which is separate from Python controlling MATLAB through MATLAB Engine.

For inherited source, preserve the existing route first so numeric results stay reproducible. For new reusable examples, prefer a facade layer around property calls so the business model does not depend directly on one wrapper's argument quirks. See `references/refprop-github-case-studies.md` for the repository review and route-selection details.
