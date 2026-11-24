## Purpose
Generates a quick preview PNG of a 3D model from a GLB file using Blender's headless mode. Renders the model with a standardized camera angle and simple lighting for consistent visual representation.

## How it is run
Command line: `blender.exe -b -P blender_preview.py -- <model.glb> <out.png>`
The only referenced caller in the project is `README.md` (line 58), which mentions it as part of the build process for `whiterun/preview_banneredmare.png`.

## Inputs
- `src`: Input GLB file path (e.g., `whiterun/model.glb`)
- `out`: Output PNG file path (e.g., `whiterun/preview_banneredmare.png`)

## Outputs
- PNG file at specified `out` path (e.g., `whiterun/preview_banneredmare.png`)
- Console output: `PREVIEW <out> [<x>, <y>, <z>]` showing output path and model bounding box dimensions (rounded to 1 decimal)

## Key functions
- `read_factory_settings` (resets Blender scene)
- `import_scene.gltf` (loads GLB model)
- `bounding_box_calculation` (computes model extents)
- `camera_setup` (positions camera relative to model)
- `render_configuration` (sets viewport lighting/resolution)
- `render_to_file` (outputs PNG)

## Depends on
- Blender 2.80+ (via `bpy` module)
- GLB model files with mesh geometry

## Gotchas
- Output resolution fixed at 900x600 pixels
- Requires Blender to be installed at default path `D:\blender.exe`
- Fails if input model contains no mesh objects
- Uses simple 'BLENDER_WORKBENCH' rendering (not high-fidelity)
- Bounding box dimensions printed to console

Source: read, not executed.
