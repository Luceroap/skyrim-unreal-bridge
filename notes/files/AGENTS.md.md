## Purpose
AGENTS.md is a reference document for project agents, outlining the critical sequence of reading materials and hard rules to maintain project consistency and collaboration workflows.

## How it is run
Not executable; referenced by other files as a required read. The file `GRUNT_TASKS_FOR_LOCAL_MODEL.md` lists it as a required dependency (line 17), and `tools/make_local_queue.py` references it in its required file list (line 338).

## Inputs
The content of AGENTS.md itself, containing required reading order and hard rules.

## Outputs
None (documentation-only; no files/folders/memory modifications).

## Key functions
Required reading order
ASCII-only file naming
Local Git workflow
Single editor runtime
No software installation

## Depends on
HANDOFF_FOR_CHATGPT.md
README.md
COORDINATION.md
HANDOFF_FOR_CURSOR.md

## Gotchas
Only one UnrealEditor.exe may run at a time
Git is local only (no remote pushes)
File names must use ASCII only
Do not install or download software
Commit only changed files with clear messages

Source: read, not executed.
