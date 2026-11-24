## Purpose
Identifies which active plugins override specific Skyrim.esm references (e.g., deleted, persistent, disabled) by analyzing plugin files. Determines override types and wins for referenced IDs.

## How it is run
Command: `python -I find_overrides.py ids.json`  
Called by `HANDOFF_FOR_CURSOR.md` in diagnostics section.

## Inputs
- JSON file (`ids.json`) with hex ID to model name mappings (e.g., `{"0001abcd": "model"}`).

## Outputs
- Per-plugin override summaries (e.g., `Dawnguard.esm: {'deleted persistent': 2, ...}`)  
- "winning override per ref" table showing top plugin/override status  
- Count of referenced IDs with no override

## Key functions
subs - Parses file chunks into headers/data  
scan - Analyzes plugin files for override references  
walk - Processes GRUP hierarchy entries

## Depends on
- `DATA` path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`  
- `PLUGINS` path: `%LOCALAPPDATA%\Skyrim Special Edition\plugins.txt`  
- Imports: `collections`, `json`, `os`, `struct`, `sys`, `zlib`

## Gotchas
- Hardcoded Windows path (D:\SteamLibrary)  
- Skips `Skyrim.esm` during scanning  
- Relies on `plugins.txt` location in `LOCALAPPDATA`  
- Uses fixed GRUP type codes (8=persistent, 9=temporary, 10=distant)  
- Requires exact plugin name casing in `plugins.txt`

Source: read, not executed.
