## Purpose
Runs the local model queue for the Skyrim-Unreal bridge project. Requires Skyrim and Unreal to be closed. Displays progress and totals, with resumable execution and halting via the `notes\STOP` file.

## How it is run
Command line: `Local_Queue.bat --limit 5` or similar arguments. No other project files call it (confirmed via `git grep` with no results outside `Local_Queue.bat`).

## Inputs
Command-line arguments passed through to `run_local_queue.py`, e.g., `--limit 5`, `--status`, or `--retry-failed`.

## Outputs
Reads/writes `notes\STOP` to halt processing after current task. Displays progress totals to console. Creates no additional output files.

## Key functions
Change directory to project root  
Run make_local_queue.py  
Run run_local_queue.py with args  
Pause for user input  

## Depends on
tools\make_local_queue.py  
tools\run_local_queue.py  

## Gotchas
- Must close Skyrim and Unreal before execution.  
- Resumable by running again to continue.  
- Creating `notes\STOP` halts after current task.  
- Hardcoded absolute path `C:\Users\Aidan\SkyrimUnrealBridge` will fail if project moves.  
- Requires `tools\` directory containing both Python scripts.  
Source: read, not executed.
