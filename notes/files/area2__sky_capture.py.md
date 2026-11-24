## Purpose
Captures sky dome textures in Unreal Engine for atmospheric effects, enabling dynamic sky parameter adjustments and image exports. Handles setup, parameter updates, and cleanup to integrate with the sky rendering pipeline.

## How it is run
Command line: Processed automatically by reading `area2/sky_step.txt` entries. Called by `unreal/SkyBridge/atmosphere.py:313` during sky parameter adjustments.

## Inputs
- `area2/sky_step.txt`: Lines with format `[action] [param1] [param2] [param3]`, e.g., `setup 0.5` or `set 0.8 0.2 1.5`.

## Outputs
- PNG files written to `area2/` (e.g., `step[1].png` from `grab` action).
- Modifies Unreal Engine parameters via `live._night_saved` and `live.night_mid`.

## Key functions
setup - Initializes scene capture for sky rendering  
set - Adjusts sky parameters (Night/Aurora/Intensity)  
grab - Exports captured render target as PNG  
done - Cleans up capture and resets sky state  

## Depends on
- `unreal` (Unreal Engine Python API)  
- `live` module (for `live._night_saved`, `live.sky_dome`)  
- `atmosphere.py` (called via `git grep` result)  

## Gotchas
- 'setup' without 'done' leaves stars disabled (confirmed by `atmosphere.py` comment)  
- 'done' resets intensity to 6.0, overriding prior values  
- Hardcoded paths (`C:\Users\Aidan\...`)  
- Fixed render target size (1024×576)  
- Capture location fixed at Z=3000  

Source: read, not executed.
