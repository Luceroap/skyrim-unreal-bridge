# Local models and task queues

Two free local models are available for grunt work. Use them for small, repetitive jobs so paid models stay on the hard problems. Their output is unverified: review every change with `git diff` before keeping it.

## The two machines

| | Warforge (this PC) | Homelab server (sunsetservers) |
|---|---|---|
| Model | `qwen3:30b-a3b` (aliases `-32k`, `-64k`, `-128k`, `qwen3:30b-opencode` share the same weights) | `qwen3:14b-gpu` |
| Endpoint | `http://127.0.0.1:11434` | `http://<homelab-tailscale-ip>:11434` (OpenAI-compatible API at `/v1`) |
| Hardware | RTX 5080 16 GB, model partly in system RAM | GTX 1070 8 GB, about 80 percent on GPU |
| Speed | Faster and smarter | About 7-9 tokens per second |
| Context | Up to 32k (or the 64k/128k alias) | 4096 tokens total (prompt plus answer) |
| Concurrency | One task at a time | One request at a time; extra requests wait in line |
| Availability | Only while Skyrim and Unreal are closed (they share the GPU and RAM) | Always on, reachable over Tailscale only, no API key |

## Which one to use

- Homelab server: one function or one short file section per request. Good for correctness reviews of a single function, regression-test designs, docstrings, renames, short summaries. Keep each prompt under about 2500 tokens so the answer fits in the 4096 limit. Add `/no_think` to prompts that do not need reasoning.
- Warforge model: tasks that need several files or longer context, such as a README section built from two docs, or a log summary across files. Still one focused task per session.
- Neither: the plugin C++ (`plugin/`, `shared/BridgeShared.h`), pose math in `unreal/SkyBridge/npc_live.py`, the memory-growth hunt, anything that deletes files, security settings, accounts or downloads. See GRUNT_TASKS_FOR_LOCAL_MODEL.md for the full good/bad list.

## Launchers (double-click, in this folder)

Homelab server:
- `Run_Homelab_Tasks.bat` starts or resumes the 600-task queue (a correctness review and a regression-test design for each of 300 project functions). The PC sends source excerpts; the server runs the model. The PC must stay on. `Run_Homelab_Tasks.bat --status` shows progress without sending work.
- `Stop_Homelab_Tasks.bat` stops after the current response.
- `Homelab_Worker.bat` keeps a worker on the general task queue (kinds H,K,M,X,N,T,Y,U) and retries every 10 minutes. Create `notes\STOP_HOMELAB` to stop it.
- `Codex_Homelab.bat` opens Codex on the server model for one small interactive task.

Warforge:
- `Codex_Local.bat` or `OpenCode_Local.bat` for interactive tasks (see OPENCODE_LOCAL.md).
- `Run_Local_Tasks.bat` runs the 12-task source review batch; `Stop_Local_Tasks.bat` stops it.

The two queues use separate locks, progress files and stop files, so they can run at the same time.

## Where results go

- Homelab queue: reports in `notes/homelab_batch/`, progress in `notes/homelab_batch_progress.json`, task list in `notes/homelab_batch_tasks.json`.
- Local batch: reports in `notes/bridge_batch/`, progress in `notes/bridge_batch_progress.json`.
- Reports are leads and test designs, not applied fixes or executed tests. A report marked `needs_review` still needs a human or a stronger model to confirm it.

## Known limits and problems

- `Evidence quote has no unique match` failures mean the model quoted code that is not in the excerpt. These are rejected on purpose; the queue moves on.
- Three timeouts in a row stop the homelab queue. Before 2026-10-29 this happened after about 55 jobs because the server's prompt cache filled its memory; that was fixed on the server. If it happens again, tell the user. Do not try to change server settings from this PC.
- `notes`, `tools`, `area2` and other folders here are junctions to `D:\Aidan_Moved\SkyrimUnrealBridge`. Use the paths as they appear in this folder.
- Python for the launchers: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`.
