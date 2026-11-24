## Purpose
This script retrieves and prints the scalar parameter names of a material in the Unreal Engine's remastered material system. It supports debugging or verifying material parameter configurations during the Skyrim-Unreal bridge development process.

## How it is run
Executed directly via Python command line (e.g., `python area2/fix_detail.py`), as confirmed by `git grep` returning no caller files.

## Inputs
None (no command-line arguments); relies on Unreal editor context with active remastered materials.

## Outputs
Console output listing scalar parameter names (e.g., `params: [param1, param2]`).

## Key functions
get_scalar_parameter_names (Unreal API)
print
importlib.reload

## Depends on
remaster_materials.py
Unreal Engine Python API

## Gotchas
- No other project files reference or call this script, requiring manual execution.
- Requires Unreal editor to be open with relevant material context loaded.

Source: read, not executed.
