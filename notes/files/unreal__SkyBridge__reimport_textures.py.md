## Purpose
Re-imports textures modified by upscale_textures.py while preserving asset configurations. Ensures upscaling changes are reflected in Unreal Engine without disrupting material settings.

## How it is run
Command: `UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=unreal/SkyBridge/reimport_textures.py`. Called by `tools/upscale_textures.py` (line 6) and `unreal/SkyBridge/remaster_materials.py` (line 842).

## Inputs
- `area2/tex/upscaled.txt` (list of textures to process)
- `area2/tex/upscaled_imported.txt` (list of already processed textures)

## Outputs
- Appends processed texture keys to `area2/tex/upscaled_imported.txt`
- Updates Unreal Engine assets via import (no new files created)

## Key functions
- Check asset existence (`eal.does_asset_exist`)
- Configure import tasks (`AssetImportTask`)
- Append keys to stamp file
- Execute asset imports (`at.import_asset_tasks`)
- Log completion (`unreal.log`)

## Depends on
`tools/upscale_textures.py` (command-line invocation), `unreal/SkyBridge/remaster_materials.py` (dynamic execution via `exec`)

## Gotchas
- Must run with Unreal Editor closed (explicitly stated)
- Skips textures already listed in `upscaled_imported.txt`
- Uses `replace_existing=True` but `replace_existing_settings=False`
- Requires `upscaled.txt` to exist (else skips processing)
- Fails if texture `.png` files are missing

Source: read, not executed.
