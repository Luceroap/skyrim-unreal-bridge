## Purpose
Analyzes terrain mesh data from Skyrim's BSA archive by extracting a specific BTR file, processing vertex and texture information, and printing key metrics to the console for debugging or validation purposes.

## How it is run
Executed directly via `python probe_btr.py` in the command line. The `git grep` command confirms no other files in the project call this script.

## Inputs
- BSA archive path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\Skyrim - Meshes1.bsa`
- Target BTR file path within BSA: `meshes\terrain\tamriel\tamriel.4.4.-4.btr`

## Outputs
- Console output of mesh name, vertex count, and texture name (if present).
- Min/max X/Y coordinates of vertex positions.
- Sample vertex coordinates (indices 0, 1/3, 1/2, and last vertex).

## Key functions
Bsa - BSA archive reader  
read - Extracts file from BSA  
extract - Processes NIF/BTR mesh data  

## Depends on
- `tools/bsa` module (for BSA handling)  
- `nif2obj` module (for mesh data processing)  

## Gotchas
- Hardcoded D: drive path for Skyrim installation (non-portable).  
- Assumes specific BSA filename (`Skyrim - Meshes1.bsa`) and terrain file path.  
- Temporary file (`probe.btr`) is written to system temp directory without explicit cleanup.  
- Relies on exact terrain filename (`tamriel.4.4.-4.btr`) existing in BSA.  
- Output depends on `nif2obj`'s parsing behavior for BTR format.  

Source: read, not executed.
