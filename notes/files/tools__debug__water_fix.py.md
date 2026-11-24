## Purpose
Fixes compilation issues in the SkyWater material by removing duplicate SingleLayerWaterMaterialOutput nodes and properly connecting scattering and absorption coefficients. Ensures the material compiles correctly after repeated rebuilds.

## How it is run
Run directly in the Unreal Editor's Python environment (e.g., via the Editor's script console). Called by `remaster_materials.water_material()` with `rebuild=True` parameter, as documented in COORDINATION.md.

## Inputs
- Material asset path: `/Game/Area2Tex/M_SkyWater`
- Color constants: Scattering (0.05, 0.09, 0.075) and Absorption (1.2, 0.35, 0.25)

## Outputs
- Modified material asset at `/Game/Area2Tex/M_SkyWater` (saved via `save_loaded_asset`)
- Console logs: "connect results" dictionary and "SLW nodes now: 1"

## Key functions
`delete_material_expression` - Removes existing SLW nodes  
`create_material_expression` - Creates new SLW and constant nodes  
`connect_material_expressions` - Links scattering/absorption coefficients  
`recompile_material` - Compiles the updated material  
`save_loaded_asset` - Persists changes to disk  

## Depends on
- Unreal Engine's `unreal` module
- `MaterialEditingLibrary` API
- `remaster_materials.water_material()` (called with `rebuild=True`)

## Gotchas
- Remaster script leaves old SLW nodes after `delete_all_material_expressions()`
- Requires explicit deletion of SLW nodes before rebuild
- Duplicate nodes prevent material compilation ("No inputs to Single Layer Water Material")
- Must connect specific pins: "ScatteringCoefficients" and "AbsorptionCoefficients"
- Material path is hardcoded (`/Game/Area2Tex/M_SkyWater`)

Source: read, not executed.
