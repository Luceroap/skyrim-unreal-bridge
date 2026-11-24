## Purpose
Handles lighting quality tiers (low to cinematic) and time-of-day/weather visual effects for the live bridge. Reads quality settings from `area2/quality.txt` and applies them via Unreal engine settings. Updates atmospheric effects like fog, haze, and god rays based on environmental conditions.

## How it is run
Command line: `python start_bridge.py --quality <tier>` writes `area2/quality.txt` and triggers settings. Called from `live_bridge.py`'s `update_sky`, `apply_lights`, and `build_environment` functions.

## Inputs
`area2/quality.txt` (quality tier), sun elevation (deg), hour (0-24), weather parameters (fog, rain, snow, storm), `interior` flag (bool), GPU data via `detect_gpu()`.

## Outputs
Modifies Unreal engine settings via console commands (e.g., `sg.ShadowQuality`, `r.VolumetricFog`) and component properties. Adjusts visual output: time-of-day lighting, weather effects, torch flicker. Writes to `area2/quality.txt`.

## Key functions
`detect_gpu` - Gets GPU name and VRAM  
`auto_tier` - Determines quality tier from GPU  
`apply_quality` - Sets Unreal engine settings  
`look` - Adjusts lighting based on time/weather  
`flicker` - Animates fire light intensity  
`sweep_captures` - Removes stray scene captures  

## Depends on
`live_bridge.py` (provides `live` object with `sun`, `moon`, `pp`, `light_actors`), `unreal` module, `area2/quality.txt`, `start_bridge.py`.

## Gotchas
- Cinematic quality tier is opt-in only (never picked by auto).
- `sweep_captures` removes stray SceneCapture2D actors every 30s (costing ~50ms GPU each).
- Torch flicker uses cached shadow pages, avoiding recalculation during animation.
- `apply_quality` resets `live._sky_key` and `live._look` to force re-application of visual settings.
- Indoor (`interior=True`) scenes use smoky, darker visuals with different fog parameters.

Source: read, not executed.
