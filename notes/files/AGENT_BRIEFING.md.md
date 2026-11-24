## Purpose
The AGENT_BRIEFING.md file serves as the primary reference guide for the Skyrim SE to Unreal Engine 5.8 bridge project, detailing critical hard rules, project structure, run instructions, hard-won lessons, and current quality state. It prevents costly errors by documenting specific constraints and solutions unique to this live bridge implementation.

## How it is run
This is a documentation file, not executed directly. It is read by developers and referenced by the script `tools/make_local_queue.py` (verified via `git grep` output showing two explicit references).

## Inputs
None (this is a reference document, not an executable program).

## Outputs
None (this is a read-only documentation file; it does not produce files, folders, or shared memory data).

## Key functions
- Hard rules
- Project layout
- Run instructions
- Hard-won lessons
- Quality state
- State of quality (2026-10-29)

## Depends on
Referenced by tools/make_local_queue.py (as shown in `git grep` output; no code dependencies).

## Gotchas
- Never minimize/hide Skyrim (Community Shaders crashes).
- One UnrealEditor.exe at a time (memory commit exhaustion risk).
- Git: local only; commit only your own files.
- Backup game files before editing.
- Use English ASCII names for files.

Source: read, not executed.
