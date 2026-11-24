## Purpose
Runs a local Ollama-powered model (qwen3:30b-a3b-64k) to edit files within the SkyrimUnrealBridge project. Enforces strict workspace-write safety mode, avoiding external modifications, and requires no ChatGPT login.

## How it is run
Command line: `Codex_Local.bat [extra_args]`  
Other files that call it: `Codex_Homelab.bat` (line 4) and `GRUNT_TASKS_FOR_LOCAL_MODEL.md` (line 3), with `tools/make_local_queue.py` listing it as a launcher.

## Inputs
Command-line arguments via `%*` (e.g., `-m qwen3:30b-a3b-128k`).

## Outputs
Edited files within `C:\Users\Aidan\SkyrimUnrealBridge` (no external writes), triggered via `workspace-write` flag.

## Key functions
Find codex.exe via PowerShell  
Run with Ollama provider  
Set workspace-write restriction  
Use qwen3:30b-a3b-64k model  
Forward command-line arguments

## Depends on
`codex.exe` (installed via ChatGPT desktop app)  
`Codex_Homelab.bat` (references via line 4)  
`tools/make_local_queue.py` (lists as launcher)

## Gotchas
- Requires closing Skyrim and Unreal Editor first (18 GB RAM needed)  
- Fails if `codex.exe` is missing (ChatGPT desktop app must be run once)  
- Only edits files within `C:\Users\Aidan\SkyrimUnrealBridge`  
- Model version fixed to `qwen3:30b-a3b-64k`  
- `workspace-write` mode prevents external file edits

Source: read, not executed.
