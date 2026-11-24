## Purpose
Diagnoses material properties for the SkyWater material in Unreal Engine, printing shading model, blend mode, and texture connections. Focuses on identifying SingleLayerWater nodes and input node connections for normal and base color properties.

## How it is run
Executed via Unreal Engine's Python console. No other files in the project call this script (confirmed by empty `git grep` results for "water_diag.py").

## Inputs
Hardcoded material asset path `/Game/Area2Tex/M_SkyWater`. Requires Unreal Engine context with the asset present.

## Outputs
Console output with:
- Shading model and blend mode
- Expression count and type distribution (e.g., `{'SingleLayerWater': 1}`)
- SingleLayerWater node names
- Normal and base color input node connections

## Key functions
unreal.load_asset
mel.get_material_expressions
m.get_editor_property
mel.get_material_property_input_node

## Depends on
unreal (Unreal Engine API)
MaterialEditingLibrary
collections.Counter

## Gotchas
Hardcoded material path `/Game/Area2Tex/M_SkyWater` may break if asset is renamed/moved.

Source: read, not executed.
