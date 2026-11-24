# Local tasks in OpenCode

Read AGENT_BRIEFING.md for current project state. Older README and handoff status can be stale. Follow AGENTS.md for project rules.

You are running Qwen3 30B locally through Ollama. The model has 32768 context tokens and text input only. Work on one focused task at a time. Use tools to read real files before making claims. Keep reads small, use targeted searches, and do not scan generated asset directories recursively. Do not launch parallel agents.

You may edit project source for requested coding tasks. Preserve other workers' changes. Do not edit game files, change security settings, install software, download models, enter passwords, or push Git. Shell commands require approval except routine Git inspection. Read-only review commands must not edit files.

Keep Skyrim and Unreal closed while doing local-model work on this PC. The model shares GPU and system memory with the games. The task launcher refuses to start while either game process is present. Existing queue workers are separate; do not start another queue worker for the same job.

## How to use
1. Open C:\Users\Aidan\SkyrimUnrealBridge in OpenCode.
2. Start a NEW session and select Qwen3 30B Local Tasks - 32K under Aidan Local Qwen3 30B if the current session retained another model.
3. Ask for one task, or use /bridge-status, /bridge-review tools/some_file.py, or /bridge-fix followed by a specific bug.
4. For the terminal interface, double-click OpenCode_Local.bat. It locates the installed desktop CLI. Ollama must be running.
5. If settings do not refresh, use the installed CLI reload command or reopen OpenCode. No account or API key is needed for this provider.

The qwen3:30b-opencode alias reuses existing model weights and a separate tool-calling template; it does not download another model. Existing Qwen aliases and queue configuration are unchanged. This file is guidance, not an operating-system sandbox.

## Verified setup
On 2026-10-29, OpenCode 2.2.2 completed a real read-tool task using aidan-local/qwen3:30b-opencode. It read CMakeLists.txt and correctly reported SkyrimUnrealBridge and CMake 3.21. This verifies the local provider and file tools, not the correctness of future code changes. The model may show verbose reasoning before tools. Give it one small task at a time.

## Improved task behavior
New project chats use the bridge agent (12 steps maximum per request). The bridge-reviewer agent and /bridge-status, /bridge-review, and /bridge-check commands cannot edit files or run arbitrary shell commands (only Git status, diff, and log are allowed). /bridge-fix uses the coding agent. Start with /bridge-check. New chats in other folders use local-helper, which knows the bridge absolute path and must not fabricate missing files.

The task launcher opens the real project and starts with a briefing read. Existing chats keep their selected agent: start a new chat or explicitly select bridge. The provider requests reasoning_effort none and the model has a concise system instruction; this reduces unnecessary output but is not a guarantee against errors. The original upstream template is restored.

## Verification of improved helpers
- Read both the real briefing and memory governor through OpenCode (21 seconds).
- Fixed an isolated example through read, edit, and read-back tools (41 seconds); independent checks passed for None, empty list, and two-item list.
- From an unrelated empty folder, found and read the real briefing by absolute path (12 seconds).
- Test records: logs/local_model_smoke/results.json and workspace_recovery.json.

Limitation: the model still emits verbose reasoning in some OpenCode replies despite the no-thinking request. Step limits bound tool cycles; they do not guarantee correctness or eliminate reasoning. Successful small tests do not establish reliability on large remaster tasks.

## Automatic review batch
Run_Local_Tasks.bat starts or resumes 12 focused source-review tasks. Stop_Local_Tasks.bat requests a stop after the current response. It does not stop interactive OpenCode or the older queue workers. Reports are under notes/bridge_batch; progress is notes/bridge_batch_progress.json. Run Run_Local_Tasks.bat --status to inspect progress without loading the model.

This batch supplies numbered code excerpts directly to the local model. The model receives no command or file-edit tools. Reports are unverified leads and suggested fixes, not completed project features. The runner checks memory and refuses to start while Skyrim or Unreal is running. The homelab model and server-management setup are unchanged.

Batch reports use constrained JSON output, then become Markdown. Evidence quotes must occur in the provided source excerpts; a unique exact quote can correct an inaccurate model-supplied line number. This checks citations, not whether the proposed bug is real. Failed reports remain marked failed and are retried on the next Run_Local_Tasks invocation.

## Homelab 600-task queue
Run_Homelab_Tasks.bat starts or resumes 600 focused tasks: a correctness review and regression-test design for each of 300 actual project functions. It calls the existing qwen3:14b-gpu model at http://<homelab-tailscale-ip>:11434 over Tailscale, one request at a time. The PC supplies source excerpts and saves results; inference runs on the server. The PC and its network connection must stay on for this dispatcher.

Stop_Homelab_Tasks.bat requests a stop after the current response. Run_Homelab_Tasks.bat --status shows progress. Results are notes/homelab_batch, progress is notes/homelab_batch_progress.json, and the manifest is notes/homelab_batch_tasks.json. Reports are unverified leads and test designs, not applied code fixes or executed tests. Three consecutive connection or runner failures stop the runner; rejected report content is recorded and the remaining jobs continue. Local-model and homelab queues have separate locks, progress, and stop files.
