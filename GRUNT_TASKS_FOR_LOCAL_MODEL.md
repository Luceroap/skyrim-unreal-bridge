# Grunt work for the local model (qwen3:30b-a3b via Ollama)

Start it with `Codex_Local.bat` (free, no login). Close Skyrim and the Unreal editor first (the model needs ~18 GB). It edits only inside this folder and asks before running other commands.
It is much weaker than ChatGPT/Claude: in a test it summarised `Play.bat` too shallowly. So: ONE small task per session, read every change (`git diff`) before keeping it, and `git checkout -- <file>` to undo a bad edit.

## Good jobs (low risk, repetitive)
1. Docstrings/comments: "Add a one-line docstring to every function in tools/<file>.py that lacks one. Do not change any code."
2. README sections: "Using only HANDOFF_FOR_CURSOR.md and COORDINATION.md, add a 'Daily use' section to README.md listing the launcher files and what each does."
3. Log summaries: "Read area2/offline_import.log and logs/*.log and list every line containing FAILED, with the model name, as a table in a new file notes/failed_models.md."
4. Table/list conversion: "Convert the table in COORDINATION.md under 'Ownership' into a CSV file notes/ownership.csv."
5. Cleanup lists: "List files in tools/ that no other file imports or mentions; write the list to notes/unused_tools.md. Do NOT delete anything."
6. Commit messages: "Look at `git diff --stat` and write a one-paragraph commit message into notes/commit_message.txt."

## Do NOT give it
The plugin C++ (`plugin/`, `shared/BridgeShared.h`), the pose math in `unreal/SkyBridge/npc_live.py`, the memory-growth hunt, Windows/security settings, anything that deletes files, anything involving accounts or downloads.

## Rules it must follow (already in AGENTS.md)
English, ASCII file names; local git only (never push); commit only files it changed; one Unreal editor at a time.
