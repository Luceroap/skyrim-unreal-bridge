## Purpose
The script retrieves scalar parameter names from the master material in Unreal Engine for debugging or analysis purposes.

## How it is run
Run directly via Python command (e.g., `python area2/fix_wet.py`). No other files in the project call this file, as confirmed by `git grep` with no results.

## Inputs
The master material object loaded from `remaster_materials` module.

## Outputs
Prints the list of scalar parameter names to the console (e.g., `master ['Param1', 'Param2']`).

## Key functions
master
get_scalar_parameter_names

## Depends on
area2/remaster_materials.py

## Gotchas
none noticed
Source: read, not executed.
