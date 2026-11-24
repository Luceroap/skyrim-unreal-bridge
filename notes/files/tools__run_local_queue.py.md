## Purpose
Processes tasks from `notes/queue.json` sequentially using a local Ollama model. Ensures safety by restricting model writes to `notes/` and restoring external file changes via Git after each task.

## How it is run
Command line: `python tools/run_local_queue.py [--limit N] [--only ID] [--status]`. Called by `Local_Queue.bat` (line 8), `tools/build_briefing.py` (line 4), and `tools/healthcheck.py` (line 60).

## Inputs
`notes/queue.json` (tasks), `notes/progress.json` (current progress), `notes/STOP` (halt trigger).

## Outputs
`notes/*.md`, `notes/files/*.md` (task outputs), `notes/progress.json` (progress tracking), `logs/local_queue.log` (execution logs).

## Key functions
log - Writes timestamped messages to log file  
codex_exe - Finds Codex executable path  
git - Runs Git commands safely  
claim - Reserves tasks to avoid duplicates  
material - Gathers input materials for model  
run_task - Executes a single task with safety checks  
wait_for_ollama - Ensures Ollama is ready before processing  

## Depends on
`tools/build_briefing.py` (called every 8 tasks or for `Z_` tasks), Ollama service.

## Gotchas
- Files changed outside `notes/` that were unmodified before the task are restored via `git checkout`; already modified files are left alone and reported.  
- Ollama must be running (local or specified via `--base-url`) to avoid startup failure.  
- Input material exceeding 55,000 characters per task is truncated.  
- `notes/STOP` file halts processing after the current task completes.  
- Model-generated file names not in Git repository trigger "invents files" error.  
Source: read, not executed.
