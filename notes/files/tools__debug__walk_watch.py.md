## Purpose
This script samples actor movement data from a live Unreal environment for approximately 40 seconds, identifying characters moving at speeds exceeding 25 units per second. It checks whether their limb animation is in bind pose (limb spread < 6 degrees) or animated.

## How it is run
Run via `python tools/debug/walk_watch.py`. No other files reference this script (git grep returned no results).

## Inputs
- Actor position and flag data via `walk_check_lib.snap()` (captured at 1-second intervals).

## Outputs
Console output listing characters that moved (e.g., `CharacterName [(speed, 'animated', spread), ...]`), truncated to 8 entries per character. Prints "nobody walked in 40 s" if no motion detected.

## Key functions
- `w.snap()`: Captures actor positions and flags
- `math.dist()`: Calculates displacement speed
- `w.limb_angles()`: Returns limb angle values

## Depends on
`tools/debug/walk_check_lib.py` (imported as `w`).

## Gotchas
- 25 units/s speed threshold for walking detection
- 6-degree limb spread threshold for bind pose
- 40-second fixed sampling duration
- Output truncated to 8 movement records per character
- Limb spread calculated as max angle minus min angle

Source: read, not executed.
