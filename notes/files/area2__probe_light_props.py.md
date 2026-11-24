## Purpose
This script inspects and prints relevant properties of Unreal Engine's light and atmospheric components for debugging purposes. It helps developers verify available properties without manual exploration of component documentation.

## How it is run
Executed directly via Unreal Editor's Python console (no command-line arguments). The `git grep` result shows no other files reference this script, indicating it is not called automatically and must be run manually.

## Inputs
Current Unreal Engine level context via `live` (e.g., `live.fog.component`, `live.sun.light_component`). Requires a loaded level with active light/atmosphere components.

## Outputs
Console output listing:
- Component property names matching keywords (e.g., "fog", "volumetric")
- Console variable integer/float values (e.g., `r.VolumetricFog.GridPixelSize 16 0.0`)
- Overall scalability level (`overall 2`)

## Key functions
props - Filters and prints object properties matching keyword patterns

## Depends on
unreal module (Unreal Engine Python API), specific Unreal classes like `unreal.SkyAtmosphereComponent`

## Gotchas
Relies on the `live` context variable being defined in the Unreal Editor's Python environment; fails if `live` is undefined.
