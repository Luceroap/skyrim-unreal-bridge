## Purpose
Minimal reader for Skyrim Special Edition's BSA v105 archives. Handles LZ4 compression and supports list/extraction operations for NIF meshes and other resources.

## How it is run
Command line: `python -I bsa.py <archive> list <substring>` or `extract <outdir> <substring>`. Called by `tools/land_textures.py` (referenced in COORDINATION.md and land_textures.py docstring).

## Inputs
- BSA archive file path (e.g., `Skyrim - Meshes0.bsa`)
- Command (`list` or `extract`)
- Substring filter (case-insensitive)
- Output directory (for `extract` command)

## Outputs
- `list`: Prints matching file paths and sizes to console
- `extract`: Writes extracted files to `outdir` with preserved paths

## Key functions
__init__ - Parses BSA header and file index
read - Retrieves and decompresses file data
main - Processes command-line arguments

## Depends on
External modules: struct, sys, os, lz4.frame

## Gotchas
- Only supports BSA v105 (Skyrim SE); fails on older versions
- Requires lz4 module for decompression
- Path searches are case-insensitive due to lowercase storage
- Extracted files inherit original case sensitivity from source paths
- Embedded names (`embed_names` flag) require manual name skipping during decompression

Source: read, not executed.
