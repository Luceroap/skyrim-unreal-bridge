## Purpose
COORDINATION.md documents the two-agent coordination (Claude Code and Cursor) for the Skyrim-to-Unreal bridge project. It defines file ownership, task responsibilities, communication protocols, and request tracking to prevent conflicts during concurrent editing. This is necessary because the project has no git repository in the initial development phase.

## How it is run
This is a documentation file, not executable code. It is read-only and referenced directly by agents working on the project. It is not run as a program, but is consulted for coordination guidance. The project uses it as a primary reference for determining who owns which files before making changes.

## Inputs
No inputs are taken by this documentation file. It is a reference document read for coordination guidance.

## Outputs
This documentation file produces no outputs itself. It references several project outputs created by other files:
- `area2/spaced_names_ok.txt` (for handling model names with spaces)
- `area2/npc/tex_alias.json` (for resolving texture name collisions)
- `area2/interiors_*.json` (for city and dungeon interiors)
- Various other outputs documented under specific Requests in the file

## Key functions
Owner - define who owns which files
Task split - divide responsibilities between agents
Protocol - establish communication rules
Requests - log changes to files owned by others
Ownership - clarify responsibility boundaries

## Depends on
This file depends on:
- README.md (project overview and setup)
- HANDOFF_FOR_CURSOR.md (project overview for Cursor)
- The actual project structure and current file ownership
- The current state of the project reflected in the Requests section

## Gotchas
- Only edit files you own (use Requests section to document changes to others' files)
- Never kill Skyrim/Unreal processes the other agent may be using without noting it here (Skyrim restarts reload the plugin)
- Plugin DLL installs: only Claude Code builds and copies the plugin (Cursor asks under Requests)
- Models with spaces in their names (e.g., "dining set") need special handling (spaces replaced with underscores)
- Editor crashes (notably at 23:38:11 with EXCEPTION_ACCESS_VIOLATION) can occur during concurrent edits

Source: read, not executed.
