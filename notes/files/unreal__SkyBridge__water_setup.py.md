## Purpose
Generates a tileable wave normal map for water surfaces using sine wave summation, stored as a PNG file. Configures a single-layer water material in Unreal Engine with dynamic UV panning and specific shading properties.

## How it is run
Executed within Unreal Editor's Python environment via editor scripting. No other project files call it, confirmed by `git grep` returning no results.

## Inputs
Hardcoded input path: `C:\Users\Aidan\SkyrimUnrealBridge\area2\tex\water_n.png` (source for normal map generation).

## Outputs
- Generated PNG file: `water_n.png` (256x256 tileable normal map).
- Imported texture asset: `/Game/Area2Tex/water_n` (normal map texture).
- Material asset: `/Game/Area2Tex/M_Water` (single-layer water material).

## Key functions
gen_normal
import_texture
config_material
set_shading

## Depends on
None (relies solely on Unreal Engine modules and standard libraries).

## Gotchas
- Hardcoded absolute path may break if project directory changes.
- Fixed random seed (7) ensures identical normal map output on each run.
- Single-layer water shading model may log warnings if unsupported in Unreal version.
- Base color values (0.02, 0.09, 0.11) are hard-coded.
- UV panning speeds (0.012, 0.006) are fixed values.

Source: read, not executed.
