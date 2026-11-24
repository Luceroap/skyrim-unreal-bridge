"""Builds the work queue for the local model: notes/queue.json  (python tools/make_local_queue.py).
Every task is READ-ONLY analysis/documentation: its only output is one markdown file under notes/. Re-run any time; finished tasks stay finished
(notes/progress.json is keyed by task id). Order: project-wide analyses first, one-file-at-a-time documentation next, the open-questions summary last."""
import ast, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
tasks = []


def add(tid, title, prompt, out, min_bytes=500, must=None, inputs=None, verify=False, check=None):
    """inputs: file paths (glob ok) or 'cmd:<shell command>'; the runner pastes their real contents into the prompt (the model cannot browse)."""
    tasks.append(dict(id=tid, title=title, prompt=prompt, out=out, min_bytes=min_bytes, must=must or [], inputs=inputs or [], verify=verify, check=check))


GREP = 'cmd:git grep -n -I -E "%s" -- %s'
INPUTS = {
 "inventory": ["cmd:git ls-files"],
 "shared_memory_spec": ["shared/BridgeShared.h", GREP % ("SkyrimUnrealBridge_", "*.py *.cpp")],
 "todos": [GREP % ("TODO|FIXME|HACK|XXX|known issue|not implemented|workaround", "*.py *.cpp *.h *.md *.bat")],
 "decisions_digest": ["COORDINATION.md"],
 "readme_digest": ["README.md", "HANDOFF_FOR_CURSOR.md"],
 "control_files": [GREP % ("debug_flags|addons.txt|no_autostart|prefetch_on|shot_request|exec_request|os.environ|argparse|sys.argv", "*.py *.cpp")],
 "launchers": ["Play.bat", "Stop.bat", "Import_Assets_Offline.bat", "Codex_Local.bat", "play.py"],
 "failed_models": ["area2/failed.txt", "cmd:dir /b area2\\failed*"],
 "log_digest": ["cmd:dir /b logs", "logs/*.log"],
 "import_graph": [GREP % ("^(import|from) ", "*.py")],
 "tuning_constants": [GREP % ("^[A-Z][A-Z_0-9]+ *= *[-0-9.(]", "*.py")],
 "hardcoded_paths": [GREP % ("[A-E]:[/\\\\]", "*.py *.cpp *.h *.bat")],
 "commands_catalog": [GREP % ("subprocess[.]|os[.]system|Start-Process", "*.py *.bat")],
 "glossary": ["README.md", "COORDINATION.md"],
 "manual_test_checklist": ["README.md", "HANDOFF_FOR_CURSOR.md"],
 "git_history_digest": ["cmd:git log --stat --format=%h%x20%ad%x20%s --date=short"],
 "naming_conventions": [GREP % ("def .*(name|key|mangle|safe)", "tools/*.py unreal/SkyBridge/*.py")],
 "pipeline_map": ["README.md", "COORDINATION.md"],
 "known_issues": ["README.md", "COORDINATION.md", "HANDOFF_FOR_CURSOR.md"],
 "memory_code_map": [GREP % ("memory_governor|collect_garbage|prefetch|mip|budget|MAX_|spawn_actor|import_asset", "unreal/SkyBridge/*.py")],
 "live_bridge_layers": ["unreal/SkyBridge/live_bridge.py"],
 "plugin_function_index": ["plugin/src/main.cpp"],
 "npc_live_map": ["unreal/SkyBridge/npc_live.py"],
 "unreal_scripts_index": ["cmd:git ls-files unreal"],
}


# ---------------------------------------------------------------- project-wide analyses
F = [
 ("inventory", "Inventory of every top-level file and folder",
  "List every file in the project root and every top-level folder (tools, unreal/SkyBridge, plugin, shared, area2 (only the .py/.txt/.csv/.json files, not the thousands of generated files), logs, screenshots, notes). One line each: name - what it is for, judging by its name and first lines. Group by folder. If you cannot tell, write 'unclear'.", "inventory.md"),
 ("shared_memory_spec", "Shared-memory specification from BridgeShared.h",
  "Read shared/BridgeShared.h. Produce a table for EVERY shared mapping (name, struct, who writes it, who reads it, update rate) and then, for every struct, a table of fields (name, type, size in bytes, meaning from the comments). Compute byte offsets assuming #pragma pack(4) and mark every offset you computed with '(computed - verify)'. Also find, with grep, which Python files read each mapping.", "shared_memory_spec.md"),
 ("todos", "Every TODO / FIXME / HACK / known-issue comment",
  "Search all .py, .cpp, .h, .md and .bat files outside the folders area2/export, area2/obj, area2/tex, area2/nif, unreal/SkyBridge/Content, build, deps for: TODO, FIXME, HACK, XXX, 'known issue', 'not implemented', 'unresolved', 'workaround'. Write a table: file:line | text | category (bug / missing feature / workaround / performance / docs).", "todos.md"),
 ("decisions_digest", "Digest of COORDINATION.md",
  "Read COORDINATION.md fully (in chunks if needed). Write: (1) who owns which files, (2) a chronological list of every decision/request/fix with its time and author, one line each, (3) requests that were never answered or whose outcome is not stated.", "decisions_digest.md"),
 ("readme_digest", "README digest and contradictions",
  "Read README.md section by section. Write one line per section. Then list every statement in README.md that contradicts COORDINATION.md or HANDOFF_FOR_CURSOR.md or the code (e.g. wrong file names, old launch commands, things described as missing that now exist). Quote both sides.", "readme_digest.md"),
 ("control_files", "Every control file, flag and switch",
  "Find every way the project is controlled by a small file or flag: files under area2/ such as debug_flags.txt, addons.txt, no_autostart.txt, prefetch_on.txt, shot_request.txt, exec_request.py, the .sky command file in the Skyrim plugins folder, environment variables (os.environ), command line flags (argparse / sys.argv). Table: name | where it is checked (file:line) | accepted values | effect.", "control_files.md"),
 ("launchers", "Catalog of launchers and entry points",
  "List every .bat, .ps1 and every Python file that has a main entry (if __name__ == '__main__'). For each: how it is started, what it starts, what it needs to be closed or open first, what it writes. Put the daily-use ones (Play.bat, Stop.bat, Import_Assets_Offline.bat, Codex.bat, Codex_Local.bat, play.py) first.", "launchers.md"),
 ("failed_models", "Failed model conversions",
  "Read area2/failed.txt and any area2/failed.txt.bak* and logs/*.log. Categorise each failed model name (banner, flag, animal, book, weapon, other) and note which backup file it came from. If failed.txt is empty, say so and list the backups instead.", "failed_models.md", ),
 ("log_digest", "Digest of all logs",
  "Read every file in logs/ and area2/offline_import.log and area2/asset_service.log if present (read only the last 300 lines of very large files). Summarise: what ran, how long it took, every error or warning (group identical ones with a count), and anything that looks like a crash.", "log_digest.md"),
 ("import_graph", "Python import graph",
  "For every .py file in tools/, unreal/SkyBridge/, area2/ and the project root, list which OTHER project modules it imports (ignore the standard library and unreal/bpy). Write an adjacency list, then a list of project .py files that no other file imports and no .bat/.md mentions (candidate unused scripts - do NOT delete anything).", "import_graph.md"),
 ("tuning_constants", "Catalog of tuning constants",
  "Search the Python and C++ sources for numeric tuning constants in ALL_CAPS or module-level assignments that control behaviour (radius, counts, rates, budgets, memory limits, thresholds, scale factors like 1.4287). Table: name | value | file:line | what it controls (from nearby comments).", "tuning_constants.md"),
 ("hardcoded_paths", "Hard-coded absolute paths",
  "Search all source files for absolute paths (C:\\, D:\\, E:\\). Table: path | file:line | purpose. Then group into: game install, Unreal install, project, user profile, other. This is for making the project relocatable later.", "hardcoded_paths.md"),
 ("commands_catalog", "Commands the project launches",
  "Search for subprocess.run / subprocess.Popen / os.system / Start-Process / Invoke-CimMethod and write a table of every external command the project runs: file:line | executable | main arguments | purpose.", "commands_catalog.md"),
 ("glossary", "Glossary of project terms",
  "Write a glossary of at least 40 terms used in this project (examples: seqlock, WRef, remaster view, prefetch, bind pose, FaceGen, bone-name mangling, offline import, shared mapping, add-on layer, memory governor, HISM, Nanite, Lumen). One to two sentences each, based ONLY on how the files in this folder use the term. Mark any you are guessing with '(guess)'.", "glossary.md"),
 ("manual_test_checklist", "Manual test checklist",
  "From README.md, COORDINATION.md and HANDOFF_FOR_CURSOR.md write a checklist of at least 30 things a human should check in a fresh session after pressing Play.bat (world loads, camera follows, water flows, NPCs posed, creatures, weapons, HUD, menus, weather, memory under 20 GB, no duplicate editors...). Each item: what to do | what you should see | which file implements it.", "manual_test_checklist.md"),
 ("git_history_digest", "Git history digest",
  "Run `git log --stat --format=%h%x20%ad%x20%s --date=short` (read only) and write one short paragraph per commit: what changed and why, naming the files. Then list the five files changed most often.", "git_history_digest.md"),
 ("naming_conventions", "Asset and naming conventions",
  "Read tools/nif2obj.py, tools/build_area.py, tools/blender_export.py, tools/npc_build.py, tools/npc_build_creature.py, unreal/SkyBridge/ue_assets.py and unreal/SkyBridge/npc_live.py. Explain every naming rule: asset names from model paths, texture keys, material slot names, FBX names, Unreal bone-name mangling, folder names under /Game. Give one worked example for each rule.", "naming_conventions.md"),
 ("pipeline_map", "End-to-end pipeline map",
  "Describe each pipeline end to end, stage by stage, with the exact file and function for each stage: (1) static world model conversion nif -> obj -> fbx -> Unreal, (2) textures dds -> png -> material instance, (3) NPC and creature building, (4) live streaming (plugin -> shared memory -> live_bridge/npc_live), (5) terrain and water, (6) launch and shutdown. Use arrows and one line per stage.", "pipeline_map.md"),
 ("known_issues", "Known issues compiled from the docs",
  "Collect every problem, limitation or unresolved item stated in README.md, COORDINATION.md and HANDOFF_FOR_CURSOR.md. Table: issue | where stated | status (open / fixed / unclear) | suggested owner (plugin / Unreal python / converter / launcher).", "known_issues.md"),
 ("memory_code_map", "Where memory is managed in the code",
  "Search for everything that manages or limits memory: memory_governor, memory_status.json, texture pool, mip bias, garbage collection, 'unloaded unused packages', collect_garbage, prefetch, budgets, MAX_* counts. Write: file:line | what it does | what triggers it | what it limits. End with a section 'Things that create actors or import assets without any cap' listing loops that spawn or import in unreal/SkyBridge/*.py.", "memory_code_map.md"),
 ("live_bridge_layers", "Layers and hooks inside live_bridge.py",
  "Read unreal/SkyBridge/live_bridge.py in chunks of about 250 lines. List every layer/feature it runs per tick or on events (camera, sky, lights, world stream, distant world, terrain, water, rain, clouds, interiors, prefetch, NPC hook, add-on hook, exec hook, screenshot hook...). Table: name | function (file:line) | how often it runs | what flag or file turns it off. Also list every add-on module loaded from area2/addons.txt.", "live_bridge_layers.md"),
 ("plugin_function_index", "Function index of the SKSE plugin",
  "Read plugin/src/main.cpp in chunks of about 250 lines. List every function with line numbers and one line each (what it does, which thread runs it). Then list every shared-memory block it creates and every file it reads or writes.", "plugin_function_index.md"),
 ("npc_live_map", "Map of npc_live.py",
  "Read unreal/SkyBridge/npc_live.py in chunks. List every function with line numbers, what it does, and which one calls which (a call tree starting at tick()). List every module-level constant and every key stored in _state.", "npc_live_map.md"),
 ("unreal_scripts_index", "Index of the Unreal-side Python scripts",
  "List every .py in unreal/SkyBridge/ and unreal/SkyBridge/Content/Python/. For each: one-line purpose, whether it runs inside the live editor, in a headless commandlet (UnrealEditor-Cmd), or standalone, and the first line of its docstring.", "unreal_scripts_index.md"),
]
for item in F:
    tid, title, prompt, out = item[:4]
    add("F_" + tid, title, prompt + " Use ONLY the pasted material below; do not mention files that are not in it. Output file will be notes/%s." % out, "notes/" + out, 150 if tid == "failed_models" else 600, inputs=INPUTS.get(tid, []), verify=True)

# ---------------------------------------------------------------- one file at a time
SKIP = ("\\.git\\", "\\build\\", "\\deps\\", "__pycache__", "\\notes\\", "\\unreal\\SkyBridge\\Content\\", "\\Intermediate\\", "\\Saved\\", "\\Binaries\\", "\\screenshots\\", "\\logs\\")
files = []
for pat in ("*.py", "*.bat", "*.ps1", "tools/*.py", "tools/debug/*.py", "unreal/SkyBridge/*.py", "unreal/SkyBridge/Content/Python/*.py", "area2/*.py",
            "plugin/src/*.cpp", "plugin/src/*.h", "shared/*.h", "unreal/SkyBridge/Source/SkyBridge/*.cpp", "unreal/SkyBridge/Source/SkyBridge/*.h",
            "*.md", "unreal/SkyBridge/Config/*.ini"):
    for f in glob.glob(pat):
        p = os.path.abspath(f)
        if os.path.isfile(p) and not any(s in p for s in SKIP):
            files.append(os.path.relpath(p, ROOT).replace("\\", "/"))
files = sorted(set(files))
CHUNK = 40000  # chars; bigger files become several tasks, one per slice of lines
for rel in files:
    text = open(rel, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    cuts, start, acc = [], 1, 0
    for i, ln in enumerate(lines, 1):
        acc += len(ln) + 1
        if acc >= CHUNK:
            cuts.append((start, i))
            start, acc = i + 1, 0
    if start <= len(lines) or not cuts:
        cuts.append((start, max(len(lines), 1)))
    for part, (a, b) in enumerate(cuts, 1):
        suffix = "" if len(cuts) == 1 else ".part%d" % part
        name = rel.replace("/", "__") + suffix + ".md"
        chunk = "" if len(cuts) == 1 else " The file is large, so you only see part %d of %d (lines %d-%d); document only that part and say so in Purpose." % (part, len(cuts), a, b)
        src = rel if len(cuts) == 1 else "range:%s:%d:%d" % (rel, a, b)
        add("D_" + rel.replace("/", "_") + suffix, "Document " + rel + suffix,
        "Document the file %s (read only; do not change it).%s Write notes/files/%s with EXACTLY these sections: '## Purpose' (2-3 sentences), '## How it is run' (command line, and which other files call it - find them with grep for its file name), '## Inputs', '## Outputs' (files, folders, shared memory it reads or writes), '## Key functions' (name - one line each, at most 15), '## Depends on' (other project files it imports or calls), '## Gotchas' (at most 5 bullets, ONLY things you are certain of; otherwise write 'none noticed'). End with the line 'Source: read, not executed.' If you are unsure about anything write 'unsure' instead of guessing." % (rel, chunk, name),
        "notes/files/" + name, 350, ["## Purpose", "## Outputs"],
        inputs=[src, GREP % (re.escape(os.path.basename(rel)), "*.py *.bat *.md *.cpp")])

# ---------------------------------------------------------------- review leads: problems / optimisation candidates (UNVERIFIED; a stronger model checks them)
KEY = ["unreal/SkyBridge/live_bridge.py", "unreal/SkyBridge/npc_live.py", "plugin/src/main.cpp", "shared/BridgeShared.h", "unreal/SkyBridge/remaster_materials.py",
       "unreal/SkyBridge/atmosphere.py", "unreal/SkyBridge/tamriel_live.py", "unreal/SkyBridge/land_terrain_live.py", "unreal/SkyBridge/grass_live.py",
       "unreal/SkyBridge/weather_fx.py", "unreal/SkyBridge/memory_governor.py", "unreal/SkyBridge/lod_objects_live.py", "start_bridge.py", "play.py",
       "tools/asset_service.py", "tools/offline_import.py", "tools/npc_batch.py", "tools/npc_autobuild.py", "tools/nif2obj.py", "tools/npc_skin.py",
       "tools/land_terrain.py", "tools/land_textures.py", "tools/grass_placement.py", "tools/distant_world.py", "tools/tamriel_terrain.py"]
KEY = [k for k in KEY if os.path.exists(k)]
REVIEW_PROMPT = ("Review %s (%s) for problems that hurt PERFORMANCE, MEMORY or CORRECTNESS in a live Skyrim->Unreal bridge: heavy work inside per-tick/per-frame loops, "
                 "unbounded growth (lists, dicts, caches, spawned actors or imported assets that are never freed), repeated disk or shared-memory reads, exceptions swallowed silently, "
                 "race conditions, unit or coordinate mistakes, hard-coded paths, O(n^2) loops. The material has line numbers at the start of each line; use ONLY those. "
                 "Write at most 10 findings, one per line, in this exact form: `L<line> | <category: perf|memory|bug|robustness|cleanup> | <what> | <why it matters> | <suggested fix> | <confidence: low|medium|high>`. "
                 "Quote at most one short code fragment per finding. If you find no real problem write exactly `no findings`. Begin the document with the heading `# Review leads for %s (UNVERIFIED)`. "
                 "These are leads for a stronger reviewer, so prefer fewer, concrete findings over many vague ones.")
for rel in KEY:
    klines = open(rel, encoding="utf-8", errors="replace").read().splitlines()
    cuts, start_l, acc = [], 1, 0
    for i, ln in enumerate(klines, 1):
        acc += len(ln) + 8
        if acc >= 38000:
            cuts.append((start_l, i)); start_l, acc = i + 1, 0
    if start_l <= len(klines) or not cuts:
        cuts.append((start_l, max(len(klines), 1)))
    for part, (a, b) in enumerate(cuts, 1):
        suffix = "" if len(cuts) == 1 else ".part%d" % part
        out = "notes/review/" + rel.replace("/", "__") + suffix + ".md"
        add("R_" + rel.replace("/", "_") + suffix, "Review leads: " + rel + suffix, REVIEW_PROMPT % (rel, "lines %d-%d" % (a, b), rel + suffix), out, 150,
            inputs=["numbered:%s:%d:%d" % (rel, a, b)])

# ---------------------------------------------------------------- synthesis for the paid agents (needs the assembled notes; run last)
add("Z_open_questions", "Open questions for the humans",
    "Using the pasted file map, review leads and known-issues notes: write notes/open_questions.md: (1) every place where two notes contradict each other, (2) every item marked 'unsure' or 'guess', (3) the 20 most important things a human should confirm, ranked. One line each, with the note file it came from.",
    "notes/open_questions.md", 600, inputs=["notes/FILE_MAP.md", "notes/known_issues.md", "notes/REVIEW_LEADS.md"])
add("Z_backlog", "Prioritised work backlog for the strong models",
    "Using the pasted briefing, file map, review leads and known issues, write notes/BACKLOG.md: 25 concrete work items ordered by visual or performance impact for the project (a Skyrim->Unreal bridge that should look much better and run smoother). "
    "For each item: `N. <title>` then three lines: `files:` (exact paths from the material), `do:` (what to change, concretely), `verify:` (how to prove it works, e.g. a command or a screenshot). "
    "Only use files and facts present in the material; mark anything uncertain with 'unverified'. Put the ground/road texture problem, flame placement, editor memory growth and per-tick performance items near the top.",
    "notes/BACKLOG.md", 800, inputs=["AGENT_BRIEFING.md", "notes/FILE_MAP.md", "notes/REVIEW_LEADS.md", "notes/known_issues.md"])


# ---------------------------------------------------------------- WORK ORDERS: small scripts, doc drafts, docstring suggestions -> staging/ (UNREVIEWED; nothing is wired into the project)
SCRIPT_RULES = ("Write ONE complete Python 3 script using ONLY the standard library (plus PIL only where the task says so). Reply with the Python source only: no markdown fence, no explanation. "
                "Start with a module docstring (purpose + usage examples), use argparse, put the logic in functions with a `main()` and `if __name__ == '__main__':`. "
                "It must be read-only: print results to stdout by default and accept an OPTIONAL --out FILE that writes the same text to a new file (never overwrite an existing file, never delete or move anything). The script will live in the project's tools/ folder, so project-relative defaults must be computed from os.path.dirname(os.path.dirname(os.path.abspath(__file__))). If the module docstring mentions a Windows path with backslashes, make it a raw string (r\"\"\"...) or avoid backslashes there. "
                "No network, no subprocess, no os.system, no eval/exec, no ctypes. Handle missing files and bad input with a clear message, not a traceback. Windows paths (use os.path / pathlib). "
                "Keep it under 150 lines and write plain, readable code.")
SCRIPTS = [
 ("log_summary", "Summarise the Unreal editor log SkyBridge*.log", "Usage: python log_summary.py [path]. Default: the newest unreal/SkyBridge/Saved/Logs/SkyBridge*.log relative to this script's parent-of-parent folder. Print file name and size; first and last timestamp; counts of lines containing 'Error:', 'Warning:', 'Assertion failed', 'Fatal error'; the 10 most frequent warning messages with counts (strip leading timestamps like [2026.10.29-06.31.32:768][ 16] first); the last 5 lines containing '[SkyBridgeLive] alive'; every 'Assertion failed' line in full."),
 ("crash_log_summary", "Summarise a Skyrim SKSE crash log", "Usage: python crash_log_summary.py [path]. Default: the newest crash-*.log in %USERPROFILE%\\OneDrive\\Documents\\My Games\\Skyrim Special Edition\\SKSE, else %USERPROFILE%\\Documents\\My Games\\Skyrim Special Edition\\SKSE. Print CRASH TIME, the Unhandled exception line, 'Type:' and 'HRESULT' lines, 'Throw Location' lines, the first 6 lines under 'POSSIBLE RELEVANT OBJECTS', and 'Process Uptime'."),
 ("photos_to_jpeg", "Convert PNG photos to phone-friendly JPEG", "Usage: python photos_to_jpeg.py FOLDER [--quality 95] [--max-mb 30]. For each .png in FOLDER write a .jpg at full resolution into FOLDER/jpg (create it), never overwrite. If a jpg exceeds --max-mb lower the quality by 5 until it fits (minimum 80). Use PIL (Pillow); if it is missing print a clear message. Print a table: name, png MB, jpg MB, quality used. (The --out argument is replaced by the fixed FOLDER/jpg output folder.)"),
 ("disk_report", "Disk usage by top-level folder", "Usage: python disk_report.py PATH [--depth 1] [--top 25]. Print the size in GB of each immediate subfolder of PATH (and files) sorted largest first; skip anything unreadable; follow no symlinks or junctions (print them as '(link)'). Stdlib only."),
 ("area2_inventory", "Inventory of the area2 data folder", "Usage: python area2_inventory.py [area2_path] [--out report.md]. List the files directly inside area2 with size and modified time, then for each subfolder the file count, total MB and the 5 most common extensions. Default path: the 'area2' folder next to this script's parent folder."),
 ("cvar_diff", "Compare two console-variable lists", "Usage: python cvar_diff.py A.txt B.txt [--out diff.md]. Each file has lines like `r.Lumen.Foo 1` (name then value, # comments ignored). Print three sections: changed (name, A value, B value), only in A, only in B. Names are case-insensitive."),
 ("md_link_checker", "Find broken relative links in markdown files", "Usage: python md_link_checker.py [ROOT] [--out report.md]. Scan every .md under ROOT (default: parent-of-parent folder of this script; skip folders named notes, .git, staging) and report each [text](relative/path) or ![img](path) whose target file does not exist, with file:line. Ignore http(s) and #anchor links."),
 ("todo_to_csv", "Export the TODO index to CSV", "Usage: python todo_to_csv.py [--in notes/index/TODO.md] --out todo.csv. The input has lines like `- unreal/SkyBridge/live_bridge.py:120  some TODO text`. Write CSV columns file,line,text."),
 ("symbols_to_csv", "Export the symbol index to CSV", "Usage: python symbols_to_csv.py [--in notes/index/symbols.json] --out symbols.csv. The JSON maps file -> list of [line, name, docstring]. Write CSV columns file,line,name,docstring, sorted by file then line."),
 ("hardcoded_paths", "Find hard-coded absolute Windows paths", "Usage: python hardcoded_paths.py [ROOT] --out paths.csv. Scan .py .cpp .h .bat .ps1 files under ROOT (default: parent-of-parent of this script; skip .git, build, deps, notes, area2/export, area2/obj, area2/tex) for strings like C:\\Users\\... or D:\\... and write CSV file,line,drive,path. Print a count per drive."),
 ("git_changelog", "Turn a git log text file into a markdown changelog", "Usage: python git_changelog.py LOG.txt --out CHANGELOG.md. LOG.txt was produced by `git log --format=%h%x09%ad%x09%s --date=short` (tab separated hash, date, subject). Group commits by date (newest first) as markdown bullets `- subject (hash)`."),
 ("json_check", "Validate JSON files", "Usage: python json_check.py [ROOT] [--out report.md]. Parse every .json under ROOT (default parent-of-parent of this script; skip .git, build, deps, Content, Intermediate, Saved, Binaries) and report files that fail with the line and column of the error, plus a count of OK files."),
 ("bat_inventory", "List what each .bat launcher runs", "Usage: python bat_inventory.py [ROOT] [--out report.md]. For every .bat in ROOT (default parent-of-parent of this script, not recursive) print its name, the leading `rem` comment lines and every line that starts a program (python, powershell, start, cmd, call, any .exe). Markdown output."),
 ("stale_files", "Report big files not touched for N days", "Usage: python stale_files.py PATH [--days 30] [--min-mb 50] [--top 40]. Walk PATH (do not follow links) and print files larger than --min-mb not modified for --days days: path, MB, age in days, sorted by size. Read-only."),
 ("duplicate_finder", "Find duplicate files in a folder", "Usage: python duplicate_finder.py PATH [--min-mb 1] [--out dups.md]. Group files by size first, then by SHA-256 of the first 1 MB plus size, and report groups with more than one file (paths and sizes). Read-only; never delete."),
]
for sid, title, spec in SCRIPTS:
    add("S_" + sid, "Script: " + title, SCRIPT_RULES + " TASK: " + spec + " Output file name will be staging/scripts/%s.py." % sid, "staging/scripts/%s.py" % sid, 400, check="python")

DOCS = [
 ("daily_use", "Daily-use guide for the user", "Write a plain-language 'Daily use' guide for the owner of this project (a gamer, not a programmer): how to start the Skyrim + Unreal view, stop it, take photos with the hotkeys, switch performance profiles, and what to do when something goes wrong. Use ONLY facts from the pasted briefing and entry-point list. Short sections, commands in code blocks.", ["AGENT_BRIEFING.md", "notes/index/ENTRYPOINTS.md"]),
 ("troubleshooting", "Troubleshooting FAQ", "Write a troubleshooting FAQ (at least 12 entries: symptom -> likely cause -> what to do) from section 3 'Hard-won lessons' and section 0 of the briefing. Use ONLY facts in the material; do not invent causes.", ["AGENT_BRIEFING.md"]),
 ("tools_overview", "Overview of tools/ grouped by purpose", "From the pasted entry-point list write notes grouping the scripts into purposes (converters, importers, NPC building, terrain, photo/showcase, diagnostics, local-model queue, other). One line per script: name - what it does (from its docstring line). Mark any script whose purpose you cannot tell as 'unclear'.", ["notes/index/ENTRYPOINTS.md"]),
 ("flags_reference", "Reference of controls and flags", "Rewrite the pasted controls scan as a reference document: for each control file, environment variable, command-line option, console variable and sky command, one line with its name and the files that read it. Do not guess meanings: write 'meaning: see the file' when the material does not say.", ["notes/index/CONTROLS.md"]),
 ("changelog_draft", "Changelog draft from git history", "From the pasted git log (hash date subject, newest first) write a CHANGELOG draft grouped by day with bullets, merging commits that are obviously one change. Do not invent anything not in the log.", ["cmd:git log --format=%h%x20%ad%x20%s --date=short"]),
 ("photo_guide", "Guide to the photo tools", "Write a user guide for the photo tools using the pasted docstrings and code: what each script does, example commands, where photos are saved, the hotkeys. Facts only from the material; no invented options.", ["tools/photo_keys.py", "tools/showcase_shot.py", "tools/shot_session.py", "tools/perf_profile.py"]),
]
for did, title, prompt, inputs in DOCS:
    add("W_" + did, "Doc draft: " + title, prompt + " Start with a level-1 heading. Output file will be staging/docs/%s.md." % did, "staging/docs/%s.md" % did, 500, inputs=inputs)

# docstring suggestions for functions that have none (key python files): applied later by a reviewer-run script, never by the model
try:
    SYMS = json.load(open("notes/index/symbols.json"))
except Exception:
    SYMS = {}
for rel in [k for k in KEY if k.endswith(".py")]:
    missing = [(ln, nm) for ln, nm, doc in SYMS.get(rel, []) if not doc and not nm.startswith("class ")]
    if not missing:
        continue
    klines = open(rel, encoding="utf-8", errors="replace").read().splitlines()
    cuts, start_l, acc = [], 1, 0
    for i, ln in enumerate(klines, 1):
        acc += len(ln) + 8
        if acc >= 38000:
            cuts.append((start_l, i)); start_l, acc = i + 1, 0
    if start_l <= len(klines) or not cuts:
        cuts.append((start_l, max(len(klines), 1)))
    for part, (a, b) in enumerate(cuts, 1):
        here = [(ln, nm) for ln, nm in missing if a <= ln <= b]
        if not here:
            continue
        suffix = "" if len(cuts) == 1 else ".part%d" % part
        listing = "; ".join("line %d %s" % (ln, nm.split("(")[0]) for ln, nm in here[:60])
        add("C_" + rel.replace("/", "_") + suffix, "Docstring suggestions: " + rel + suffix,
            "Below is code with line numbers. These functions have no docstring: %s. For EACH, write a one-line docstring (at most 100 characters, imperative mood, says what it does, based only on its code). "
            "Reply with one line per function in this exact form: `<line> | <function name> | <docstring text>` and nothing else. Skip a function if you cannot tell what it does." % listing,
            "staging/docstrings/" + rel.replace("/", "__") + suffix + ".txt", 60, inputs=["numbered:%s:%d:%d" % (rel, a, b)])

# ---------------------------------------------------------------- MINI TASKS for the small homelab server (4k context, ~9 tok/s): ONE function per task, one-line answer
MINI_FILES = sorted(set(KEY) | set(f for f in files if f.endswith(".py") and (f.startswith("tools/") or f.startswith("unreal/SkyBridge/"))))
mini_n = 0
for rel in MINI_FILES:
    if not rel.endswith(".py"):
        continue
    try:
        src = open(rel, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        continue
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not ast.get_docstring(n):
            a_, b_ = n.lineno, getattr(n, "end_lineno", n.lineno)
            if not (3 <= b_ - a_ + 1 <= 70) or n.name.startswith("__"):
                continue
            add("H_%s_L%d" % (rel.replace("/", "_"), a_), "Docstring: %s:%d %s" % (rel, a_, n.name),
                "/no_think\nWrite a one-line docstring (at most 100 characters, imperative mood, no quotes) for the function `%s` below, based only on its code. "
                "Reply with exactly one line in this form and nothing else: `%d | %s | <docstring text>`" % (n.name, a_, n.name),
                "staging/docstrings/%s.part%d.txt" % (rel.replace("/", "__"), a_), 10, inputs=["numbered:%s:%d:%d" % (rel, a_, b_)])
            mini_n += 1
print("mini tasks:", mini_n)

# ---------------------------------------------------------------- MINI TASKS 2 (homelab, tiny context): classes, modules, C++ functions, constants, TODO triage, doc digests, usage lines
counts2 = {}


def _mini(kind, tid, title, prompt, out, rel, a, b, mode="numbered"):
    add("%s_%s" % (kind, tid), title, prompt, out, 8, inputs=["%s:%s:%d:%d" % (mode, rel, a, b)])
    counts2[kind] = counts2.get(kind, 0) + 1


pyfiles = [f for f in MINI_FILES if f.endswith(".py")]
for rel in pyfiles:
    try:
        src = open(rel, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        continue
    lines_ = src.splitlines()
    tag = rel.replace("/", "_")
    flat = rel.replace("/", "__")
    # K: classes without a docstring
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and not ast.get_docstring(n):
            a_ = n.lineno
            _mini("K", "%s_L%d" % (tag, a_), "Class docstring: %s:%d %s" % (rel, a_, n.name),
                  "Write a one-line docstring (at most 100 characters, imperative or noun phrase, no quotes) for the class `%s` below, based only on its code. Reply with exactly one line: `%d | %s | <text>`" % (n.name, a_, n.name),
                  "staging/class_docstrings/%s.part%d.txt" % (flat, a_), rel, a_, min(getattr(n, "end_lineno", a_), a_ + 45))
    # M: module purpose line for files without a module docstring
    if not ast.get_docstring(tree) and len(lines_) > 5:
        _mini("M", tag, "Module purpose: " + rel,
              "From the first lines of this Python file (imports, constants, function names) write ONE line (at most 120 characters) saying what the file is for. Reply with exactly one line: `%s | <description>`" % rel,
              "staging/modules/%s.txt" % flat, rel, 1, min(len(lines_), 60))
    # N: tuning constants (UPPER_CASE = number / tuple / list at column 0)
    for i, l in enumerate(lines_, 1):
        m = re.match(r"^([A-Z][A-Z0-9_]{2,})\s*=\s*[-+0-9.(\[]", l)
        if m:
            _mini("N", "%s_L%d" % (tag, i), "Constant: %s:%d %s" % (rel, i, m.group(1)),
                  "Explain in at most 100 characters what the constant `%s` (line %d) controls, with its unit if the code shows one (cm, m, seconds, count, ...). If you cannot tell, write `unclear`. Reply with exactly one line: `%d | %s | <text>`" % (m.group(1), i, i, m.group(1)),
                  "staging/constants/%s.part%d.txt" % (flat, i), rel, max(1, i - 8), min(len(lines_), i + 10))
    # U: usage line for scripts
    if rel.startswith("tools/") or "/" not in rel:
        _mini("U", tag, "Usage line: " + rel,
              "From the file header below write ONE line (at most 140 characters) telling a user how to run it and what it does. Use only what the header shows; if there is no usage hint write the likely command from the docstring. Reply with exactly one line: `%s | <usage>`" % rel,
              "staging/usage/%s.txt" % flat, rel, 1, min(len(lines_), 45))

# X: C++ functions (from the exact C++ index)
try:
    cur, cpp_lines = None, {}
    for l in open("notes/index/CPP.md", encoding="utf-8"):
        h = re.match(r"## (\S+)\s", l)
        if h:
            cur = h.group(1)
            continue
        m = re.match(r"- (\d+)\s+`(\w+)\(", l)
        if m and cur:
            cpp_lines.setdefault(cur, []).append((int(m.group(1)), m.group(2)))
    for rel, fl in cpp_lines.items():
        total = len(open(rel, encoding="utf-8", errors="replace").read().splitlines())
        for ln, name in fl:
            _mini("X", "%s_L%d" % (rel.replace("/", "_"), ln), "C++ function: %s:%d %s" % (rel, ln, name),
                  "Write a one-line comment (at most 100 characters, says what the function `%s` does and on which thread/when if the code shows it) for the C++ function below. Reply with exactly one line: `%d | %s | <text>`" % (name, ln, name),
                  "staging/docstrings_cpp/%s.part%d.txt" % (rel.replace("/", "__"), ln), rel, ln, min(total, ln + 55))
except Exception as e:
    print("C++ mini tasks skipped:", e)

# T: TODO triage (from the exact TODO index)
try:
    for l in open("notes/index/TODO.md", encoding="utf-8"):
        m = re.match(r"- (.+?):(\d+)\s\s", l)
        if m and m.group(1).endswith((".py", ".cpp", ".h")) and os.path.exists(m.group(1)):
            rel, ln = m.group(1), int(m.group(2))
            total = len(open(rel, encoding="utf-8", errors="replace").read().splitlines())
            _mini("T", "%s_L%d" % (rel.replace("/", "_"), ln), "TODO triage: %s:%d" % (rel, ln),
                  "A TODO/FIXME/workaround comment is at line %d of %s (shown with context). Classify it as one of: bug | missing-feature | workaround | performance | cleanup | stale, and give one sentence (at most 120 characters) on the next step. Reply with exactly one line: `%s:%d | <category> | <next step>`" % (ln, rel, rel, ln),
                  "staging/todo_triage/%s.part%d.txt" % (rel.replace("/", "__"), ln), rel, max(1, ln - 12), min(total, ln + 12))
except Exception as e:
    print("TODO triage skipped:", e)

# Y: digests of the long markdown docs in ~2400-character slices
for rel in ["COORDINATION.md", "README.md", "HANDOFF_FOR_CURSOR.md", "HANDOFF_FOR_CHATGPT.md", "AGENTS.md", "GRUNT_TASKS_FOR_LOCAL_MODEL.md"]:
    if not os.path.exists(rel):
        continue
    ml = open(rel, encoding="utf-8", errors="replace").read().splitlines()
    start_l, acc, part = 1, 0, 0
    for i, l in enumerate(ml, 1):
        acc += len(l) + 1
        if acc >= 2400 or i == len(ml):
            part += 1
            _mini("Y", "%s_P%d" % (rel.replace("/", "_"), part), "Doc digest: %s part %d" % (rel, part),
                  "Summarize the text below (lines %d-%d of %s) in at most 3 bullet points, each starting with `- `, concrete facts only (names, decisions, numbers, file names). If it is only chat or filler reply `- (nothing substantive)`." % (start_l, i, rel),
                  "staging/md_digest/%s.part%d.txt" % (rel.replace("/", "__"), part), rel, start_l, i, mode="range")
            start_l, acc = i + 1, 0
print("mini tasks 2:", counts2)

# ---------------------------------------------------------------- ROUND 2 (30B on the PC): verify review leads, algorithm notes, data-file formats
# V: verify each review lead against the code and its callers (cuts the false positives)
try:
    lead_rx = re.compile(r"- \*\*(high|medium|low)\*\* \| (\w+) \| (.+?):(\d+) \| (.*)")
    for l in open("notes/REVIEW_LEADS.md", encoding="utf-8"):
        m = lead_rx.match(l.rstrip())
        if not m:
            continue
        conf, cat, rel, ln, text = m.groups()
        rel = re.sub(r"\.part\d+$", "", rel)
        ln = int(ln)
        if not os.path.exists(rel):
            continue
        total = len(open(rel, encoding="utf-8", errors="replace").read().splitlines())
        inputs = ["numbered:%s:%d:%d" % (rel, max(1, ln - 30), min(total, ln + 30))]
        fname = None
        if rel.endswith(".py"):
            try:
                tree = ast.parse(open(rel, encoding="utf-8", errors="replace").read())
                best = None
                for n in ast.walk(tree):
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= ln <= getattr(n, "end_lineno", n.lineno):
                        if best is None or n.lineno > best.lineno:
                            best = n
                fname = best.name if best else None
            except Exception:
                pass
        if fname:
            inputs.append('cmd:git grep -n -E "%s[(]" -- *.py' % fname)
        add("V_%s_L%d" % (rel.replace("/", "_"), ln), "Verify lead: %s:%d" % (rel, ln),
            "A small model reported this review finding for %s line %d: [%s] %s. Decide from the pasted code (with line numbers) and, if shown, the list of places that call the function, whether the finding is CORRECT. "
            "Consider how often the code really runs (look at the callers: per frame, per second, once at startup?). Reply with exactly one line: `%s:%d | YES or NO or UNSURE | <one sentence reason>`" % (rel, ln, cat, text[:300], rel, ln),
            "staging/verified/%s.L%d.txt" % (rel.replace("/", "__"), ln), 10, inputs=inputs)
except Exception as e:
    print("verify tasks skipped:", e)

# E: algorithm notes for the long/complex functions in the key python files
en = 0
for rel in [k for k in KEY if k.endswith(".py")]:
    try:
        tree = ast.parse(open(rel, encoding="utf-8", errors="replace").read())
    except Exception:
        continue
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a_, b_ = n.lineno, getattr(n, "end_lineno", n.lineno)
            if 45 <= b_ - a_ + 1 <= 230:
                add("E_%s_L%d" % (rel.replace("/", "_"), a_), "Algorithm notes: %s:%d %s" % (rel, a_, n.name),
                    "Explain the function `%s` below for a maintainer, in 5 to 10 short bullet points: its inputs, the main steps in order, side effects (files, shared memory, Unreal or Skyrim calls), units and coordinate conventions visible in the code, "
                    "and anything that must not be broken. Use only the code shown; write 'unsure' where the code does not say. Begin with the heading `# %s (%s:%d)`." % (n.name, n.name, rel, a_),
                    "staging/algorithm_notes/%s.L%d.md" % (rel.replace("/", "__"), a_), 300, inputs=["numbered:%s:%d:%d" % (rel, a_, b_)])
                en += 1

# FMT: formats of the small data/control files in area2 (first lines only)
fn_ = 0
for pat in ("area2/*.json", "area2/*.txt", "area2/*.csv", "area2/*.tsv", "area2/landterrain/*.json"):
    for f in sorted(glob.glob(pat)):
        try:
            if os.path.getsize(f) > 1500000 or os.path.getsize(f) < 20:
                continue
        except OSError:
            continue
        rel = f.replace("\\", "/")
        add("FMT_" + rel.replace("/", "_"), "Data format: " + rel,
            "Below are the first lines of the data file %s. Describe its format in at most 6 lines, each starting with `- `: what each line or field means, the separators, one short example from the sample, and how a program would parse it. Use only the sample; write 'unclear' where it does not say." % rel,
            "staging/formats/%s.txt" % rel.replace("/", "__"), 20, inputs=["range:%s:1:40" % rel])
        fn_ += 1
print("round 2 tasks: verify=%d algorithm=%d formats=%d" % (sum(1 for t in tasks if t["id"].startswith("V_")), en, fn_))

# ---------------------------------------------------------------- ROUND 3 (30B on the PC): reviews + algorithm notes for the rest of the python files, refactoring plans for the biggest functions
other_py = [f for f in files if f.endswith(".py") and f not in KEY and (f.startswith(("tools/", "unreal/SkyBridge/")) or "/" not in f)]
r3 = {"R": 0, "E": 0, "P": 0}
for rel in other_py:
    try:
        src = open(rel, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        continue
    klines = src.splitlines()
    if len(klines) < 25:
        continue
    # reviews (same format as round 1 so tools/build_briefing.py merges them)
    cuts, start_l, acc = [], 1, 0
    for i, ln in enumerate(klines, 1):
        acc += len(ln) + 8
        if acc >= 38000:
            cuts.append((start_l, i)); start_l, acc = i + 1, 0
    if start_l <= len(klines) or not cuts:
        cuts.append((start_l, max(len(klines), 1)))
    for part, (a, b) in enumerate(cuts, 1):
        suffix = "" if len(cuts) == 1 else ".part%d" % part
        add("R_" + rel.replace("/", "_") + suffix, "Review leads: " + rel + suffix, REVIEW_PROMPT % (rel, "lines %d-%d" % (a, b), rel + suffix),
            "notes/review/" + rel.replace("/", "__") + suffix + ".md", 150, inputs=["numbered:%s:%d:%d" % (rel, a, b)])
        r3["R"] += 1
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a_, b_ = n.lineno, getattr(n, "end_lineno", n.lineno)
            ln_ = b_ - a_ + 1
            if 60 <= ln_ <= 230:
                add("E_%s_L%d" % (rel.replace("/", "_"), a_), "Algorithm notes: %s:%d %s" % (rel, a_, n.name),
                    "Explain the function `%s` below for a maintainer, in 5 to 10 short bullet points: its inputs, the main steps in order, side effects (files, shared memory, Unreal or Skyrim calls), units and coordinate conventions visible in the code, "
                    "and anything that must not be broken. Use only the code shown; write 'unsure' where the code does not say. Begin with the heading `# %s (%s:%d)`." % (n.name, n.name, rel, a_),
                    "staging/algorithm_notes/%s.L%d.md" % (rel.replace("/", "__"), a_), 300, inputs=["numbered:%s:%d:%d" % (rel, a_, b_)])
                r3["E"] += 1
# P: refactoring plans for the biggest functions (all python files, key or not)
for rel in [f for f in files if f.endswith(".py") and (f in KEY or f in other_py)]:
    try:
        tree = ast.parse(open(rel, encoding="utf-8", errors="replace").read())
    except Exception:
        continue
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a_, b_ = n.lineno, getattr(n, "end_lineno", n.lineno)
            if 110 <= b_ - a_ + 1 <= 420:
                add("P_%s_L%d" % (rel.replace("/", "_"), a_), "Refactor plan: %s:%d %s" % (rel, a_, n.name),
                    "The function `%s` below is long (%d lines). Propose how a maintainer could split it into 3 to 6 smaller functions WITHOUT changing behaviour: for each new function give a name, the line range it would take over (use the line numbers shown), what it does in one sentence, and what it needs as arguments / returns. "
                    "Mention any shared state or early returns that make the split risky. This is a plan only; do not rewrite the code. Begin with the heading `# Refactor plan: %s (%s:%d)`." % (n.name, b_ - a_ + 1, n.name, rel, a_),
                    "staging/refactor_plans/%s.L%d.md" % (rel.replace("/", "__"), a_), 300, inputs=["numbered:%s:%d:%d" % (rel, a_, b_)])
                r3["P"] += 1
print("round 3 tasks:", r3)

# ---------------------------------------------------------------- ROUND 4 (homelab, tiny context, massive): per-function summaries, type-hinted signatures, edge cases
r4 = {"A": 0, "B": 0, "G": 0}
for rel in [f for f in MINI_FILES if f.endswith(".py")]:
    try:
        src = open(rel, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        continue
    tag, flat = rel.replace("/", "_"), rel.replace("/", "__")
    for n in ast.walk(tree):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a_, b_ = n.lineno, getattr(n, "end_lineno", n.lineno)
        ln_ = b_ - a_ + 1
        if not (4 <= ln_ <= 70):
            continue
        inputs = ["numbered:%s:%d:%d" % (rel, a_, b_)]
        add("A_%s_L%d" % (tag, a_), "Summary: %s:%d %s" % (rel, a_, n.name),
            "Summarize what the function `%s` below does in ONE sentence of at most 120 characters (what it takes, what it returns or changes). Use only the code. Reply with exactly one line: `%d | %s | <summary>`" % (n.name, a_, n.name),
            "staging/function_summaries/%s.part%d.txt" % (flat, a_), 8, inputs=inputs)
        r4["A"] += 1
        if 4 <= ln_ <= 45:
            add("B_%s_L%d" % (tag, a_), "Type hints: %s:%d %s" % (rel, a_, n.name),
                "Write the signature of the function `%s` below with Python type hints inferred from how it is used in its body. Use `Any` when unsure, keep default values, do not invent or drop parameters. "
                "Reply with exactly one line: `%d | %s | def %s(<typed parameters>) -> <return type>`" % (n.name, a_, n.name, n.name),
                "staging/type_hints/%s.part%d.txt" % (flat, a_), 8, inputs=inputs)
            r4["B"] += 1
        if 6 <= ln_ <= 60:
            add("G_%s_L%d" % (tag, a_), "Edge cases: %s:%d %s" % (rel, a_, n.name),
                "List up to 3 edge cases or bad inputs that could make the function `%s` below fail or misbehave (empty or missing data, wrong units, None, very large values, missing files). One sentence each, each starting with `- `. "
                "Only mention things the code shows; if it looks safe write `- (none obvious)`." % n.name,
                "staging/edge_cases/%s.part%d.txt" % (flat, a_), 8, inputs=inputs)
            r4["G"] += 1
print("round 4 tasks:", r4)

def prio(t):   # key runtime files first (docs, then reviews), then the rest, synthesis last
    tid = t["id"]
    if tid.startswith("Z_"):
        return 9
    for n, k in enumerate(KEY):
        kk = k.replace("/", "_")
        if tid in ("D_" + kk, "R_" + kk) or tid.startswith(("D_" + kk + ".part", "R_" + kk + ".part")):
            return 1 + n / 100.0
    if tid[:2] in ("S_", "W_", "C_"):
        return 2.5
    if tid[:2] in ("H_", "K_", "M_", "X_", "N_", "T_", "Y_", "U_"):
        return 2.6
    if tid[:2] in ("V_", "E_") or tid.startswith("FMT_"):
        return 2.2
    if tid[:2] == "P_":
        return 2.9
    if tid[:2] in ("A_", "B_", "G_"):
        return 2.7
    return 2 if tid.startswith("F_") else 3


tasks.sort(key=prio)

os.makedirs("notes", exist_ok=True)
json.dump(tasks, open("notes/queue.json", "w"), indent=1)
print("%d tasks (%d project-wide, %d per-file docs, 1 final) -> notes/queue.json" % (len(tasks), len(F), len(files)))
