# Entry points

## launchers (.bat/.ps1): first comment lines
- **Codex.bat**: rem Starts the Codex command-line agent in this project. Safe defaults: it may edit files inside this folder only (workspace-write) rem and asks before running anything else (on-request). Extra arguments are passed through, e.g.  Codex.bat -m gpt-6-astra rem Uses the codex.exe that the ChatGPT/Codex desktop app installed (already logged in with your ChatGPT account).
- **Codex_Local.bat**: rem Codex agent driven by YOUR LOCAL model (Ollama, qwen3:30b-a3b, 64k context): free, no ChatGPT login or usage limit needed. rem Same safe defaults as Codex.bat: may edit files inside this project only (workspace-write), asks before anything else. rem Close Skyrim and the Unreal editor first: the model needs ~18 GB of GPU/system memory.  Extra args pass through, e.g. -m qwen3:30b-a3b-1
- **Import_Assets_Offline.bat**: (no comment)
- **Launch_Demo.bat**: (no comment)
- **Local_Queue.bat**: rem Runs the whole grunt-work queue on your LOCAL model (free). Close Skyrim and Unreal first. Resumable: run it again to continue. rem Shows what is being worked on and the totals as it goes. Create the file notes\STOP to halt after the current task. rem Args pass through, e.g.  Local_Queue.bat --limit 5   or   --status   or   --retry-failed
- **Photo_Shoot.bat**: rem Photo shoot: stops the local model, starts Skyrim + Unreal at showcase quality, then listens for photo hotkeys (F8 4K, F9 8K, F5 time, F rem Fly with the Skyrim console: ~ then tfc.  Photos land in screenshots\photos.
- **Play.bat**: (no comment)
- **Stop.bat**: (no comment)
- **rebuild_all.ps1**: (no comment)
- **start_bridge.ps1**: # Starts Skyrim (via SKSE, auto-loads your newest save), waits for live data, then opens the Unreal window. # Run from PowerShell: C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.ps1 # (If your execution policy blocks scripts, that is your setting to change; or paste the steps below by hand.)

## python scripts with `if __name__ == '__main__'` (first docstring line)
- play.py: One-click launcher: Skyrim + the Unreal remaster view, in the right order, with the right focus.
- remaster_watch.py: Runs alongside the remaster view (started by `start_bridge.py --remaster`).
- start_bridge.py: 
- tools/asset_service.py: On-demand asset service. The Unreal editor (live_bridge.py) appends model asset names to area2/requests.txt when it needs a
- tools/auto_build.py: 
- tools/bsa.py: Minimal Skyrim SE (BSA v105) reader. Usage: python -I bsa.py <archive> list <substring> | extract <outdir> <substring>
- tools/detail_noise.py: Write area2/tex/detailgrain_n.png + detailgrain.png: seamless fine surface grain for M_SkyMaster's close-range detail.
- tools/distant_world.py: Distant world layer: every mountain, cliff, big rock and tree that Skyrim places around the play area, read from the
- tools/editor_watchdog.py: Background watchdog: relaunches the Unreal editor (remaster view) after it CRASHES while Skyrim is being played.
- tools/fill_textures.py: Fill in diffuse maps the converter missed: every area2/tex/<key>_n.png without <key>.png gets its colour map from the
- tools/gpu_profile.py: Capture one GPU frame in the live editor (ProfileGPU) and print the expensive passes per GPU queue.
- tools/grass_placement.py: Grass placement for the Unreal remaster (Skyrim's own grass is off in the remaster profile).
- tools/grass_world.py: Grass layer: Skyrim's landscape grass (GRAS records) scattered the way the game does it, from the plugins' data, because
- tools/land_terrain.py: Full-resolution Tamriel terrain with per-layer landscape textures (replaces the baked-tile terrain + covers water cells).
- tools/land_textures.py: Baked high-resolution landscape textures + full-resolution LAND terrain over the water cells.
- tools/lod_horizon_preview.py: Offline check of the horizon layer: Blender render from Whiterun toward the horizon with the terrain LOD
- tools/lod_objects.py: Horizon object LOD from Skyrim's own LOD data (DynDOLOD/xLODGen loose output in Data\ wins over the BSAs):
- tools/make_local_queue.py: Builds the work queue for the local model: notes/queue.json  (python tools/make_local_queue.py).
- tools/make_project_index.py: Exact (non-LLM) project index for the agent team -> notes/index/*.md and notes/index/symbols.json.   python tools/make_project_index.py
- tools/max_quality.py: Push the live Unreal editor to its absolute maximum quality for showcase screenshots (ray traced Lumen hit lighting, cinematic scalability,
- tools/mesh_index.py: Index of every mesh in the game (BSAs + loose files): asset name -> nif path, so a model name can be turned back into its file even when
- tools/nif2obj.py: Minimal Skyrim SE NIF (20.2.0.7, BS stream 100) geometry extractor -> Wavefront OBJ (+ MTL with diffuse texture names).
- tools/npc_hair_tint.py: Hair colours of the converted NPCs. Skyrim draws hair/brow textures in grey and multiplies them by the NPC's hair colour,
- tools/npc_skin.py: Skinned NIF + skeleton extractor for NPC rendering in Unreal.
- tools/perf_gpu_share.py: GPU share per process (SkyrimSE vs UnrealEditor) from the Windows GPU performance counters. Read-only, no editor access.
- tools/perf_profile.py: Switch the live Unreal view to a performance profile.   python tools/perf_profile.py [fast|faster|fastest|everyday]
- tools/puddle_noise.py: Write area2/tex/puddlenoise.png: seamless low-frequency fBm used by M_SkyMaster to place rain puddles in world space.
- tools/run_local_queue.py: Feeds notes/queue.json to the local Ollama model one task at a time, unattended.
- tools/showcase_shot.py: Showcase screenshots from the live Unreal editor: pins the viewport camera around a target, forces hour + weather (+ ground wetness/snow),
- tools/tamriel_terrain.py: Terrain and water for all of Tamriel, from the official masters' LAND records (exact heights, texture layers, vertex colours).
- tools/tamriel_world.py: All of Tamriel for Unreal: every placed reference with a model in the Tamriel worldspace (forts, castles, farms, villages,
- tools/upscale_textures.py: AI-upscale (Real-ESRGAN x2, CUDA) the low-resolution diffuse textures in area2/tex.
- unreal/SkyBridge/remaster_materials.py: One master material for every Skyrim surface, with per-texture material instances.
