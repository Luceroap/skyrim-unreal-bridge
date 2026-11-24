## Purpose
Builds a work queue for documentation tasks targeting the project codebase. The queue is stored in `notes/queue.json` and generates markdown files for analysis, review, and synthesis. Tasks are read-only and organized by project scope (e.g., project-wide analysis, per-file documentation).

## How it is run
Command: `python tools/make_local_queue.py`  
Called by: `Local_Queue.bat` (line 7) and `tools/run_local_queue.py` (line 289).

## Inputs
- Project source files (via `git grep`, `git ls-files`, and glob patterns)
- Existing documentation (`README.md`, `COORDINATION.md`, `HANDOFF_FOR_CURSOR.md`)
- Git repository state (for version history and file patterns)

## Outputs
- `notes/queue.json`: Primary output containing all tasks.  
- Generated markdown files under `notes/files/`, `notes/review/`, and `notes/` (e.g., `inventory.md`, `review/live_bridge.md`).  
- Scripts under `staging/scripts/` (e.g., `log_summary.py`).

## Key functions
- `add`: Adds a task with metadata to the queue.
- `prio`: Sorts tasks by priority (key files first).

## Depends on
- Standard library (`ast`, `glob`, `json`, `os`, `re`).
- Git commands (`git grep`, `git ls-files`).
- Project structure (folder hierarchy, `*.py`, `*.cpp`, `*.h` files).

## Gotchas
- Must run in project root (changes directory via `os.chdir(ROOT)`).
- Relies on Git repository presence (fails if not under Git).
- Generates output only in `notes/` and `staging/` (never modifies source code).
- `queue.json` must be processed before documentation tasks begin.
- Skips hidden directories (`.git`, `build`, `deps`, `logs`) automatically.

Source: read, not executed.
