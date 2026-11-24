# Git History Digest

This commit adjusted `tools/run_local_queue.py` to log the actual model name for remote workers, addressing configuration issues in the task queue system.

This commit expanded `tools/make_local_queue.py` with support for new mini task types (classes, modules, C++ functions, etc.) and refined `tools/run_local_queue.py` to handle the new task classification system.

This commit updated `tools/run_local_queue.py` to correctly manage staging/ outputs without stray file artifacts, improving file organization.

This commit added the 'ast' import in `tools/make_local_queue.py` to fix a bug where mini tasks were silently skipped during processing.

This commit introduced `Codex_Homelab.bat` for homelab server tasks, extended `tools/make_local_queue.py` to support per-function tasks, and made minor adjustments in `tools/run_local_queue.py`.

This commit added second worker support to `tools/run_local_queue.py`, including task claims and per-worker progress tracking for the OpenAI-compatible server backend.

This commit expanded `tools/make_local_queue.py` for work orders (scripts, docstrings) with safety checks, while updating `tools/run_local_queue.py` to prevent live edits from reverting.

This commit created `tools/apply_docstrings.py` and `tools/export_data.py` for docstring generation and CSV exports, while updating `staging/README.md` with new instructions.

This commit added `AGENT_BRIEFING.md`, `build_briefing.py`, `healthcheck.py`, and `make_project_index.py` to enhance agent communication and project structure, while modifying local queue components.

This commit introduced `Local_Queue.bat` and `Photo_Shoot.bat` for queue management, with `tools/photo_keys.py` added for photo-related configurations and further local queue enhancements.

This commit adjusted `unreal/SkyBridge/fire_fx.py` to create fuller orange flames with better size and less blown-out appearance.

This commit set a 45 FPS cap in `tools/perf_profile.py` to ensure Skyrim maintains GPU performance during Unreal rendering.

This commit fixed syntax in `unreal/SkyBridge/night_sky.py` including literal newlines and adjusted aurora strength to 0.25.

This commit added performance features through `tools/perf_profile.py` and `tools/sky_extras.py`, while significantly expanding `unreal/SkyBridge/night_sky.py` for enhanced aurora and mountain mist effects.

This commit created `tools/shot_session.py` for photo sessions with memory guards and updated `tools/max_quality.py` for profile settings.

This commit introduced `tools/set_cvar.py` and `tools/showcase_shot.py` for camera and settings, and extended `unreal/SkyBridge/fire_fx.py` for procedural fire effects.

This commit added `Local_Queue.bat` for local queue management and significantly expanded `tools/make_local_queue.py` and `tools/run_local_queue.py` for handling doc/analysis tasks.

This commit introduced `Codex_Local.bat` and `GRUNT_TASKS_FOR_LOCAL_MODEL.md` to enable driving Codex with a local Ollama model.

This commit added `Codex.bat` to launch the Codex CLI within the project's workspace-write sandbox with permission prompts.

This commit moved debug scripts to `tools/debug/`, updated `.gitignore`, and added `tools/mesh_index.py` and `tools/nif2obj.py` for model conversion fixes.

This commit updated `AGENTS.md` to correctly direct Codex/ChatGPT to `HANDOFF_FOR_CHATGPT.md` and project rules.

This commit made a minor update to `AGENTS.md` to align with previous pointer to `HANDOFF_FOR_CHATGPT.md`.

This commit created `HANDOFF_FOR_CHATGPT.md` as a brief optimization guide for ChatGPT/Codex, adhering to English and ASCII conventions.

This commit enhanced `unreal/SkyBridge/offline_import.py` to include full character and creature imports for live editor compatibility.

This commit added `tools/shutdown_after_import.py` to automate shutdown after offline model imports, ensuring clean termination.

This commit captured Cursor agents' work in progress, including updates to `COORDINATION.md`, `README.md`, and numerous `area2` probe scripts.

This commit introduced `Import_Assets_Offline.bat` for offline asset import, with expanded `tools/offline_import.py` and `unreal/SkyBridge/offline_import.py` for bulk model processing.

This commit added `play.py` to initiate the background character/creature builder when Skyrim is active.

This commit created `tools/editor_watchdog.py` to automatically relaunch the Unreal editor after crashes during Skyrim sessions.

This commit added version control guidelines to `README.md` and detailed git rules in `COORDINATION.md`.

This commit updated `.gitignore` and added numerous `area2` probe scripts while ignoring binary asset types and lock files in execution hooks.

This commit modified `unreal/SkyBridge/live_bridge.py` to implement lazy loading of dungeon interiors and model prefetching.

This commit enhanced `tools/distant_world.py` to dump dungeon cells with DLC form-id remapping and lazy index for model lists.

This commit added `area2/addons.txt` support via tools and updated `COORDINATION.md` with `live_bridge.py` hooks.

This commit added exec hook serialization with lock and parallel agent registration to `COORDINATION.md`.

This commit captured the project state prior to implementing parallel agents, including updates to `COORDINATION.md` and various scripts.

# Top 5 Most Changed Files
1. unreal/SkyBridge/live_bridge.py
2. tools/make_local_queue.py
3. tools/run_local_queue.py
4. COORDINATION.md
5. tools/max_quality.py
