## Purpose
This script inspects DDS texture files within Skyrim's BSA archive, extracting header metadata and image properties. It serves as a diagnostic tool for validating texture format configurations during the Skyrim-to-Unreal bridge development.

## How it is run
Executed directly via `python probe_lod.py`. No other project files call this script, confirmed by `git grep` (no matching lines found).

## Inputs
- Skyrim BSA archive: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\Skyrim - Textures7.bsa`
- Hardcoded texture paths: `textures\terrain\tamriel\tamriel.4.4.-4.dds` and `textures\terrain\tamriel\tamriel.4.-16.-4_n.dds`

## Outputs
Console output showing:
- Texture file paths
- Byte data (offsets 84-88 in DDS header)
- Unpacked 32-bit integer values (from DDS header at offset 12)
- Image dimensions (e.g., `(1024, 1024)`)
- Color mode (e.g., `RGB`)

## Key functions
Bsa.read
Image.open
struct.unpack_from

## Depends on
tools/bsa.py

## Gotchas
- Hardcoded Skyrim installation path (D:\SteamLibrary...)
- Hardcoded BSA filename (Skyrim - Textures7.bsa)
- Hardcoded texture paths (tamriel.4.4.-4.dds)
- Requires exact BSA structure to avoid read errors
- Relies on Python's backslash escaping for Windows paths

Source: read, not executed.
