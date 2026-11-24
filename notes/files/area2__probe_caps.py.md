## Purpose
This script probes and logs settings for SceneCapture2D components, directional light (sun), skylight, and volumetric cloud components in the current Unreal Editor level. It outputs configuration values related to cloud shadow rendering, ambient occlusion, and console variables affecting volumetric cloud visuals.

## How it is run
Executed directly from Unreal Editor's Python console or via command line (`python area2/probe_caps.py`), as no other files call it (confirmed via `git grep` returning no results).

## Inputs
Current level actors (SceneCapture2D components), Unreal Editor scene state, and console variables.

## Outputs
Console output showing property values (e.g., `SceneCapture2D /Game/LevelFolder/SceneCapture2D capture_every_frame True`, `cloud_shadow_extent 0.5`, `r.VolumetricCloud.ShadowMap.MaxResolution 256`).

## Key functions
get_all_level_actors
get_editor_property
get_component_by_class
get_console_variable_float_value
get_path_name

## Depends on
`unreal` module (Unreal Engine API), `live` namespace (e.g., `live.sun`, `live.skylight`).

## Gotchas
- Requires `live` namespace to be preinitialized (crashes if missing).
- Relies on specific Unreal Engine component names (e.g., `VolumetricCloudComponent`).
- Output format not documented; assumes consistent property names.
- Console variable values (`r.VolumetricCloud.*`) require engine restart to take effect.

Source: read, not executed.
