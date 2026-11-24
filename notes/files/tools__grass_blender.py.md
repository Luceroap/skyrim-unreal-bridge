## Purpose
Converts Skyrim grass OBJ models to FBX format for Unreal Engine, applying scaling (Skyrim units to meters) and material adjustments for proper rendering. Generates preview images showing grass placement on terrain from .npz data.

## How it is run
Command line: `blender -b --factory-startup -P grass_blender.py -- export <obj_dir> <fbx_dir>` or `blender -b --factory-startup -P grass_blender.py -- preview <preview_dir> <obj_dir> <out.png>`. Called by `tools/grass_placement.py` (lines 25, 520, 563).

## Inputs
- For export: `obj_dir` (directory containing Skyrim grass `.obj` files), `fbx_dir` (output directory for FBX files).
- For preview: `preview_dir` (directory containing `terrain.npz` and `instances.npz`), `obj_dir` (same as export input), `out.png` (base output filename).

## Outputs
- For export: `.fbx` files in `fbx_dir` (one per `.obj` file, scaled by 0.014287).
- For preview: Two PNG files at `<out>.png` (ground view) and `<out>_high.png` (overhead view).

## Key functions
import_obj: Imports a single OBJ file into Blender and returns the active mesh.
export: Converts all OBJ files from input directory to FBX with scaling and material adjustments.
grass_material: Modifies grass material nodes for alpha cut-out and thin blade lighting.
rotations: Computes Euler rotations for grass instances from normal vectors and yaw.
instancer: Creates geometry node system to place models at instance points.
preview: Renders ground and overhead preview images from terrain/instance data.

## Depends on
None (only uses standard libraries, Blender bpy module, and numpy).

## Gotchas
- Fixed scale factor (0.014287) for export; requires code change to modify.
- Preview mode requires pre-generated `terrain.npz` and `instances.npz` files.
- Missing OBJ files during preview skip with error message ("ERROR no obj for").
- Material adjustments require specific node setup in source materials.
- Renders two images per preview command (ground and overhead views).

Source: read, not executed.
