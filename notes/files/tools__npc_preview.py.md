## Purpose
Renders a quick preview PNG of a character FBX model using Blender's Workbench renderer. Computes bounding box to position camera and applies textures from specified directories.

## How it is run
Command: `D:\blender.exe -b -P npc_preview.py -- in.fbx out.png`. No other project files call this script; it is referenced only in COORDINATION.md as part of the preview workflow.

## Inputs
- `src`: Input FBX file path (e.g., `in.fbx`)
- `out`: Output PNG file path (e.g., `out.png`)

## Outputs
- PNG file at specified `out` path (e.g., `out.png`)
- Prints bounding box coordinates and render status to console

## Key functions
- Calculate mesh bounding box dimensions
- Apply textures matching material slot patterns
- Position camera using bounding box center
- Configure sun light and studio shading
- Render to PNG using Blender Workbench

## Depends on
- Blender installation (with Python API)
- Texture directories: `area2/tex` and `area2/npc/tex`
- FBX files with textures matching `_dds` naming pattern

## Gotchas
- Hard-coded absolute paths (C:\Users\Aidan\SkyrimUnrealBridge\area2\tex)
- Texture filenames must follow `_stem_dds` naming pattern
- Material names must strip `.001` suffixes (e.g., `Mat.001` → `Mat`)
- Uses Blender Workbench engine (not Cycles)
- Camera position scales with model size (0, -size*2.2, size*0.1)

Source: read, not executed.
