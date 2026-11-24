## Purpose
Starts the Codex command-line agent with strict workspace-write safety (modifies only files within the project directory) and requires user confirmation before executing actions.

## How it is run
Command line: `Codex.bat [-m gpt-6-astra ...]`. Called by `tools/make_local_queue.py` (line 60).

## Inputs
Command-line arguments passed to Codex (e.g., `-m gpt-6-astra`), handled via `%*`.

## Outputs
Edits files within `C:\Users\Aidan\SkyrimUnrealBridge` (workspace directory). No explicit outputs beyond file modifications.

## Key functions
- Starts Codex.exe via PowerShell to find latest binary
- Enforces workspace-write mode for file edits
- Requires 'on-request' user confirmation
- Passes all extra command-line arguments
- Validates Codex installation path

## Depends on
ChatGPT desktop app (codex.exe installed), `C:\Users\Aidan\SkyrimUnrealBridge` directory structure.

## Gotchas
- Hardcoded project path `C:\Users\Aidan\SkyrimUnrealBridge` (fails if moved)
- Requires ChatGPT desktop app installed first
- Fails if `codex.exe` not found in `LOCALAPPDATA\OpenAI\Codex\bin\`
- No error handling for invalid arguments
- Relies on PowerShell `Get-ChildItem` for binary detection

Source: read, not executed.
