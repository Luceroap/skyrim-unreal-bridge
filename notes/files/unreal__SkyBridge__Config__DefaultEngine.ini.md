## Purpose
Configures engine defaults for the Skyrim-to-Unreal bridge, including game maps, rendering features (ray tracing, Lumen, DLSS), and editor viewport settings. Sets critical parameters like shadow quality, lighting method, and DLSS presets to enable high-fidelity visuals and performance optimizations.

## How it is run
The Unreal Engine automatically loads this file at startup. It is referenced by `play.py` (via build environment) and explicitly mentioned in `README.md`, `COORDINATION.md`, and `HANDOFF_FOR_CURSOR.md` as part of the project's configuration workflow. No command line invocation is required.

## Inputs
Engine configuration parameters (e.g., `r.RayTracing=True`, `r.NGX.DLSS.Preset=12`, `r.AllowStaticLighting=False`).

## Outputs
- Engine rendering behavior (ray tracing, Lumen, DLSS denoising, shadow quality).
- No external files or shared memory are written; all settings are read-only by the engine.

## Key functions
RayTracing
DLSS
AutoExposure
Lumen
VolumetricFog
VirtualShadows
DenoiserMode

## Depends on
None (standard Unreal Engine configuration file; no project-specific dependencies).

## Gotchas
- Hardcoded SecurityToken `3F8F9D0D44D6F376F0828681F25EFC12` in Android settings.
- `r.AllowStaticLighting=False` disables static lighting, increasing runtime calculation costs.
- DLSS presets set to high values (`r.NGX.DLSS.Preset=12`, `r.NGX.DLSSRR.Preset=5`).
- Backup file `DefaultEngine.ini.bak_prephoto` used for modifications (per `README.md`).
- `r.VolumetricFog.GridSizeZ=128` may impact performance.

Source: read, not executed.
