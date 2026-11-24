## Purpose
Defines safe, low-risk maintenance tasks for the local model (Qwen3:30b-a3b via Ollama). Ensures operations avoid destructive changes, require explicit review, and limit work to repetitive, verifiable edits.

## How it is run
Command: `Codex_Local.bat` (requires closing Skyrim/Unreal editor first). Triggered by `tools/make_local_queue.py` (line 338, `git grep` result).

## Inputs
COORDINATION.md, README.md, HANDOFF_FOR_CURSOR.md, PLAY.BAT, logs/*.log, area2/offline_import.log, and referenced files as specified in tasks.

## Outputs
notes/failed_models.md (log summaries), notes/ownership.csv (converted table), notes/unused_tools.md (unused file list), notes/commit_message.txt (commit summaries).

## Key functions
Add docstrings to functions
Add Daily use section to README
Summarize logs with FAILED entries
Convert ownership table to CSV
List unused tools files
Generate commit messages from diff

## Depends on
tools/make_local_queue.py

## Gotchas
- Must close Skyrim and Unreal editor before execution
- Requires ~18 GB RAM allocation
- One task per session only
- Always verify changes via `git diff` before committing
- Never deletes files; lists unused files only

Source: read, not executed.
