## Purpose
Adjusts the Unreal Editor's viewport screen percentage by reading a value from 'sp.txt' in the area2 directory. This script dynamically sets a console variable for the editor's display scaling.

## How it is run
Command line: `python area2/probe_sp.py`. No other project files call this script, as confirmed by `git grep` showing no references.

## Inputs
`area2/sp.txt` (contains the target screen percentage value as a string).

## Outputs
Modifies Unreal Engine's console variable `r.Editor.Viewport.ScreenPercentage` and prints the current value to stdout. No files or shared memory are written by the script.

## Key functions
execute_console_command
get_console_variable_float_value

## Depends on
`unreal` module (Unreal Engine Python API)

## Gotchas
sp.txt must exist; missing file causes a runtime error.

Source: read, not executed.
