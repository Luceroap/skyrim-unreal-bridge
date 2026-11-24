## Purpose
Provides a comprehensive one-screen health check for the SkyrimUnrealBridge agent, monitoring critical system resources, process status, shared memory streams, editor heartbeat, and external services. It enables quick validation of bridge stability before and after risky operations by aggregating real-time diagnostic data.

## How it is run
Command line: `python tools/healthcheck.py`  
Other files: Referenced in `AGENT_BRIEFING.md` (line 36) as part of the documentation for agent state checks.

## Inputs
- System memory (via Windows API)
- Disk space (C: and D: drives only)
- GPU metrics (via `nvidia-smi`)
- Running processes (SkyrimSE.exe, UnrealEditor.exe, etc.)
- Shared memory streams (`Local\\SkyrimUnrealBridge_*`)
- Logs in `unreal/SkyBridge/Saved/Logs/`
- SKSE crash logs (`%USERPROFILE%\OneDrive\Documents\My Games\Skyrim Special Edition\SKSE\crash-*.log`)
- Ollama executable location (`%LOCALAPPDATA%\Programs\Ollama\ollama.exe`)

## Outputs
Prints console diagnostics including:
- Memory usage (free RAM/free commit with status warnings)
- Disk space (C:/D: drives)
- GPU utilization
- Process status with memory details
- Shared memory stream status
- Editor heartbeat from latest log
- Last Skyrim crash log
- Ollama service status
- Local queue status (`run_local_queue.py --status`)

## Key functions
sh: Executable command wrapper using subprocess

## Depends on
- `tools/run_local_queue.py` (for queue status)
- Shared memory streams (created by Skyrim plugin/Unreal bridge)
- Ollama installation at `%LOCALAPPDATA%\Programs\Ollama\ollama.exe` (optional)
- `unreal/SkyBridge/Saved/Logs/` log directory structure

## Gotchas
- Free commit memory under 10 GB is marked "DANGER"
- Only C: and D: drives are checked for disk space
- Multiple UnrealEditor.exe instances trigger "one editor only!" warning
- Ollama status shows "not answering" if executable missing
- Shared memory streams require Skyrim plugin actively running

Source: read, not executed.
