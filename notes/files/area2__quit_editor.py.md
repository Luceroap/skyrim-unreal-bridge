## Purpose
Saves unsaved Unreal editor packages before terminating the editor. Triggers editor shutdown with a confirmation message.

## How it is run
Command line: `python area2/quit_editor.py`. No other project files call this script (verified via `git grep` with no results).

## Inputs
None; executes as a standalone script without command-line arguments.

## Outputs
Console output: `quit requested`. Editor saves unsaved packages and terminates.

## Key functions
save_dirty_packages
quit_editor

## Depends on
None (relies on Unreal engine's Python API modules: `unreal.EditorLoadingAndSavingUtils`, `unreal.SystemLibrary`).

## Gotchas
- Does not wait for user confirmation before exiting after printing "quit requested".

Source: read, not executed.
