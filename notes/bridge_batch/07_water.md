# Water lifecycle and flow application

Local-model review lead; NOT independently verified or applied.

## Finding
Duplicated water actors

## Evidence
- unreal/SkyBridge/live_bridge.py:237 - log("cell water: %d strips" % len(xs))

## Suggested fix
Remove the 'quads' branch (lines 215-238) and use only the 'water_wide.csv' branch (lines 239-249) for water actor creation.

## Validation needed
Check that the 'quads' branch (lines 215-238) is redundant with the 'water_wide.csv' branch (lines 239-249) by verifying that the 'quads' file is not used in the game's water system and that the 'water_wide.csv' file contains all necessary water data.
