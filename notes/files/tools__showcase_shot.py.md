## Purpose
This script captures high-resolution screenshots in the Unreal editor with a pinned camera view. It adjusts the camera position, weather, time of day, lighting, and environmental effects (wetness/snow) to produce showcase-quality images.

## How it is run
Command line: `python tools/showcase_shot.py NAME X Y Z DIST AZIMUTH_DEG ELEV_DEG HOUR WEATHER [wet=0.0] [snow=0.0] [fov=60.0] [settle=8.0]`  
or `python tools/showcase_shot.py --release` to return camera control to the game.  
Other files that call it: `tools/shot_session.py` (referenced in its comment as the photo tool source).

## Inputs
- `NAME`: Base filename for output PNG.
- `X, Y, Z`: Target position coordinates in Unreal (cm units).
- `DIST`: Camera distance from target.
- `AZIMUTH_DEG`: Camera azimuth angle (degrees).
- `ELEV_DEG`: Camera elevation angle (degrees).
- `HOUR`: Time of day (e.g., 14.5 for 2:30 PM).
- `WEATHER`: Weather type (clear/cloud/overcast/fog/rain/storm/snow).
- Optional flags: `wet`, `snow` (0.0-1.0), `fov` (degrees), `settle` (seconds).

## Outputs
- 4K PNG file saved to `screenshots/showcase/` (default) or `screenshots/<SHOWCASE_DIR>/`.
- Output path: `<project_root>/screenshots/showcase/NAME.png`.

## Key functions
- `setup`: Configures camera position and weather/lighting.
- `shoot`: Coordinates camera setup, waiting, and screenshot capture.
- `__main__`: Handles command-line arguments and execution flow.
- `ue_exec`: Executes Unreal Engine commands via bridge.

## Depends on
- `start_bridge.ue_exec` (for Unreal engine commands).
- Unreal Engine `unreal` module (via bridge).
- `play.py` must be running (uses bridge exec hook).

## Gotchas
- Requires `play.py` to be running (fails without it).
- `--release` must be used to restore camera control to the game.
- Default `wet` and `snow` values are 0.0.
- Default `settle` time is 8.0 seconds (for sky/exposure settling).
- `SHOWCASE_DIR` environment variable overrides default output folder.

Source: read, not executed.
