## Purpose
Finds and converts specific landscape texture files (dirt, grass, Whiterun) from Skyrim's BSA archives to RGB format for the Skyrim-Unreal bridge project. Processes DX10 textures to standard DDS format.

## How it is run
Command: `python tools/find_tex.py <directory> <output_file>`. No other project files call it (git grep shows no callers).

## Inputs
- `d`: Directory path containing Skyrim BSA files (e.g., `Skyrim - Textures*.bsa`)
- `out`: Output file path for saved RGB image

## Outputs
- Converted RGB image saved to `out`
- Prints filtered texture filenames
- Prints `PICKED` followed by chosen texture path (e.g., `textures\\landscape\\dirt02.dds`)

## Key functions
Bsa parsing - Extracts files from BSA archives  
Filename filtering - Targets landscape/dirt/grass textures  
DX10 header adjustment - Modifies texture format code  
Image conversion - Converts DDS to RGB  
Output saving - Saves processed image

## Depends on
- `bsa.py` (Bsa class)
- `PIL.Image` (Python Imaging Library)

## Gotchas
- Only processes DX10 textures (fails on non-DX10)
- Requires BSA filenames to match `Skyrim - Textures*.bsa` pattern
- Hardcoded keywords (`dirt`, `grass`, `whiterun`) in filename checks
- Uses specific texture names (`dirt02.dds`, `fielddirtgrass01.dds`) if present
- Stops after first match in hardcoded `pick` list

Source: read, not executed.
