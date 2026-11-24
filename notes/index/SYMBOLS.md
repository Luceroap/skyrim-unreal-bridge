# Python symbols (exact, from ast)
format: `line  name(args)  - first docstring line`

## area2/apply_dt.py  (13 lines)

## area2/cap.py  (26 lines)
> python area2/cap.py <names,comma> <dist> <prefix> -> area2/<prefix>_all.png
- 8  `step(s)`

## area2/cap_root.py  (36 lines)

## area2/cap_walkers.py  (46 lines)
> Close-up of up to 3 WALKING NPCs (side view), grabbed twice 0.5 s apart -> area2/walkers_<k>_<i>.png + walkers_report.txt.
- 28  `_cb(dt)`

## area2/check_npc_mod.py  (5 lines)

## area2/fix_audit.py  (22 lines)

## area2/fix_audit2.py  (19 lines)

## area2/fix_detail.py  (5 lines)

## area2/fix_dup.py  (23 lines)

## area2/fix_interior.py  (9 lines)

## area2/fix_interior2.py  (9 lines)

## area2/fix_night.py  (25 lines)

## area2/fix_npc_mats.py  (28 lines)

## area2/fix_prefetch.py  (11 lines)

## area2/fix_trees.py  (8 lines)

## area2/fix_water_nanite.py  (27 lines)
- 5  `water_slots(comp, model)`

## area2/fix_wet.py  (5 lines)

## area2/gpu_prof.py  (3 lines)

## area2/hot_atmos.py  (21 lines)
> Hot-patch the running live_bridge with the current atmosphere.py / live_bridge.py (no editor restart).

## area2/hot_memgov.py  (11 lines)

## area2/list_windows.py  (21 lines)
> Visible top-level windows: title, process, pid.
- 6  `cb(h, _)`

## area2/memgov_dry.py  (12 lines)

## area2/memrep.py  (8 lines)

## area2/night_test.py  (13 lines)

## area2/npc_capture.py  (46 lines)
> Close-up renders of NPCs without touching the user's camera. area2/npc_step.txt: 'setup' | 'grab <prefix>' | 'done'.

## area2/npc_live_before_cursor.py  (481 lines)
> NPCs in the live Unreal scene: imports area2/npc/export/npc_<baseId>.fbx (tools/npc_build.py) as skeletal meshes and poses them from
- 33  `log(msg)`
- 38  `quat_to_mat(x, y, z, w)`
- 44  `mat_to_quat(m)`
- 57  `mul(a, b)`
- 61  `tr(a)`
- 65  `mv(a, v)`
- 69  `conj_flip(a)`
- 74  `qmul(a, b)`
- 80  `qconj(a)`
- 84  `qflip(a)`
- 88  `qrot(q, v)`
- 94  `qnlerp(a, b, t)`
- 103  `stream_seq()`
- 112  `read_actors(cam=None, radius=None)`  - All actors; with cam/radius only actors within radius get their bones parsed (parsing ~30 x 134 bones costs ~3
- 146  `rest_pose(sex)`
- 159  `_png_for_slot(slot)`
- 171  `_material_for_slot(slot)`
- 202  `mesh_for(base)`
- 237  `_spawn(a_info, mesh, lb)`
- 253  `_ensure_rest(entry)`  - Read the reference pose of EVERY bone once, before any bone is moved (a child's component-space transform chan
- 273  `_plan(entry, sex)`  - Per-bone constants of the pose math (module docstring), folded so a bone costs two quaternion products + two v
- 293  `ue_bone(name)`  - Unreal's FBX import renames bones: spaces -> '-', '[' and ']' -> '_'  ('NPC Root [Root]' -> 'NPC-Root-_Root_')
- 301  `_is_bind(bones, rest, RrT)`  - True when every limb bone sits at the SAME angle from its rest pose (a pure root rotation): the skeleton is un
- 311  `_pose(entry, a_info, sex, lb)`
- 377  `read_gear()`  - Worn gear stream (~1 Hz): actor ref id -> dict(wfl, weapons=[right, left]).
- 401  `_weapon(entry, a, gear, live, lb)`  - Right-hand weapon as a rigid mesh on the streamed WEAPON node, only while the weapon is drawn.
- 434  `tick(live)`

## area2/npc_live_before_cursor_frozen.py  (646 lines)
> NPCs in the live Unreal scene: imports area2/npc/export/npc_<baseId>.fbx (tools/npc_build.py) as skeletal meshes and poses them from
- 35  `log(msg)`
- 40  `quat_to_mat(x, y, z, w)`
- 46  `mat_to_quat(m)`
- 59  `mul(a, b)`
- 63  `tr(a)`
- 67  `mv(a, v)`
- 71  `conj_flip(a)`
- 76  `qmul(a, b)`
- 82  `qconj(a)`
- 86  `qflip(a)`
- 90  `qrot(q, v)`
- 96  `qnlerp(a, b, t)`
- 105  `stream_seq()`
- 117  `parse_bones(a)`  - Bones of an actor returned by read_actors(lazy=True) (parsing every actor's ~134 bones costs ~3 ms per frame).
- 127  `read_actors(cam=None, radius=None, lazy=False)`  - All actors; with cam/radius only actors within radius get their bones parsed; lazy: none (call parse_bones).
- 166  `skel_key(a)`  - 'male'/'female' for the human skeletons; otherwise a file-name key from the race skeleton nif path (creatures:
- 174  `rest_pose(sex)`
- 187  `_png_for_slot(slot)`
- 203  `_alias(slot)`
- 215  `_material_for_slot(slot)`
- 237  `_material_for_stem(slot, d, stem)`
- 265  `mesh_for(base)`
- 300  `_spawn(a_info, mesh, lb)`
- 316  `_ensure_rest(entry)`  - Read the reference pose of EVERY bone once, before any bone is moved (a child's component-space transform chan
- 336  `_plan(entry, sex)`  - Per-bone constants of the pose math (module docstring), folded so a bone costs two quaternion products + two v
- 356  `ue_bone(name)`  - Unreal's FBX import renames bones: spaces -> '-', '[' and ']' -> '_'  ('NPC Root [Root]' -> 'NPC-Root-_Root_')
- 364  `_is_bind(bones, rest, rq)`  - True when every limb bone sits at the SAME angle from its rest pose (a pure root rotation): the skeleton is un
- 379  `_ingest(entry, a_info, now)`  - New stream sample for this actor: pick the pose to show and append (t, root, pose) to its short history.
- 419  `_apply_pose(entry, pose, sex, far)`
- 454  `_smooth(entry, now, dist, lb)`  - Every editor frame: place the actor between its last two stream samples (shown ~one stream interval late, so m
- 495  `_pose_gap(dist)`  - Seconds between limb updates: every stream sample near, fewer far away.
- 504  `read_gear()`  - Worn gear stream (~1 Hz): actor ref id -> dict(wfl, weapons=[right, left]).
- 528  `_weapon(entry, a, gear, live, lb)`  - Right-hand weapon as a rigid mesh on the streamed WEAPON node, only while the weapon is drawn.
- 561  `tick(live)`  - Every editor frame: smooth each NPC between stream samples. When the stream has a new frame (seq changed, ~30 
- 582  `_has_fbx(base)`  - os.path.exists per actor per frame was ~10% of the NPC time; new FBXs (npc_batch) are picked up within 10 s.
- 592  `_read_and_spawn(live, lb, now)`

## area2/patch_rain_occ.py  (18 lines)

## area2/preview_sky.py  (6 lines)
> area2/preview.txt: '<hour> <weather name>' previews that time/weather in the editor; 'off' returns to Skyrim's.

## area2/probe.py  (54 lines)

## area2/probe_arms.py  (30 lines)
- 5  `ang(a, b)`

## area2/probe_arms2.py  (14 lines)

## area2/probe_arms3.py  (15 lines)

## area2/probe_arms4.py  (15 lines)

## area2/probe_arms5.py  (7 lines)

## area2/probe_arms6.py  (15 lines)

## area2/probe_bake.py  (23 lines)

## area2/probe_bounds.py  (13 lines)

## area2/probe_btr.py  (16 lines)

## area2/probe_caps.py  (20 lines)

## area2/probe_cmp.py  (36 lines)
- 9  `class Fake`
- 11  `apply_pose(comp, names, tfs)`

## area2/probe_dup.py  (16 lines)
- 4  `key(a)`

## area2/probe_fog.py  (12 lines)

## area2/probe_gpu.py  (11 lines)

## area2/probe_ground.py  (20 lines)

## area2/probe_hist.py  (21 lines)
- 6  `ing(entry, a, now, _o=orig)`

## area2/probe_light_props.py  (21 lines)
- 2  `props(obj, words)`

## area2/probe_limbs_live.py  (23 lines)
- 5  `ang(c, W, a, b)`

## area2/probe_lod.py  (11 lines)

## area2/probe_np.py  (7 lines)

## area2/probe_npc.py  (25 lines)

## area2/probe_npc2.py  (20 lines)

## area2/probe_npc3.py  (20 lines)

## area2/probe_npc_mats.py  (18 lines)

## area2/probe_perf.py  (17 lines)

## area2/probe_pf.py  (2 lines)

## area2/probe_plan.py  (6 lines)

## area2/probe_player.py  (27 lines)
> Run with normal python: Skyrim fps, game-time rate vs real time, player speed (slow-motion check).
- 9  `rd()`

## area2/probe_pose_cost.py  (15 lines)

## area2/probe_pose_rate.py  (25 lines)
- 4  `_cb(dt)`

## area2/probe_rain_mine.py  (12 lines)

## area2/probe_refresh.py  (36 lines)
- 10  `chk(tag)`

## area2/probe_refresh2.py  (11 lines)

## area2/probe_render2.py  (20 lines)

## area2/probe_render_pose.py  (15 lines)

## area2/probe_rot.py  (16 lines)

## area2/probe_scale.py  (9 lines)

## area2/probe_sky.py  (4 lines)

## area2/probe_smooth.py  (26 lines)
- 6  `traced(live, _o=orig)`

## area2/probe_sp.py  (4 lines)

## area2/probe_state.py  (19 lines)
> Is Skyrim in the world? Reads the bridge packet (run with normal python).

## area2/probe_stream_limbs.py  (49 lines)
> Outside Unreal: sample the actor stream for a few seconds and show, per NPC, whether limbs move and whether npc_live._is_bind flags it.
- 35  `view_angle(p)`
- 40  `ang(q1, q2)`

## area2/probe_tex.py  (12 lines)

## area2/probe_vis.py  (10 lines)

## area2/probe_water_nanite.py  (14 lines)

## area2/prof_apply.py  (10 lines)

## area2/prof_npc.py  (17 lines)
- 5  `timed(live, _o=orig)`

## area2/prof_npc2.py  (14 lines)
- 6  `timed(live, _o=orig, _pr=pr)`

## area2/quit_editor.py  (4 lines)

## area2/reload_npc_keep.py  (7 lines)

## area2/sbperf_cprof.py  (28 lines)
> cProfile live.tick_body for N frames, then write the top functions to area2/sbperf_cprof.txt and restore.
- 6  `body(dt)`

## area2/sbperf_csv.py  (4 lines)

## area2/sbperf_long.py  (40 lines)
> 30 s window: cProfile the whole tick_body, list frames whose body took > 40 ms, write area2/sbperf_long.txt.
- 7  `body(dt)`

## area2/sbperf_read.py  (16 lines)

## area2/sbperf_start.py  (48 lines)
> Stability session profiler: wraps the main per-tick functions of `live` (instance attributes, no file edits) and
- 9  `wrap(obj, name, key)`
- 11  `w(*a, **k)`
- 22  `body(dt)`
- 38  `restore()`

## area2/sky_capture.py  (32 lines)

## area2/swap_npc.py  (12 lines)

## area2/swap_reset.py  (8 lines)

## area2/tam_test1.py  (18 lines)

## area2/test_interior.py  (10 lines)

## area2/test_npc_frozen.py  (30 lines)
> Offline: an animated walker records a gait cycle; a frozen walker (same pose every sample, root moving) and a bind walker play it.
- 7  `qax(ax, deg)`
- 11  `bones_at(phase, x, bind=False)`
- 25  `shown(e)`

## area2/test_npc_math.py  (70 lines)
> Offline check: new folded pose math in npc_live == the original per-bone matrix math (area2/_pose_old.txt).
- 4  `class V`
- 5  `__init__(s, x=0, y=0, z=0)`
- 6  `class Q`
- 7  `__init__(s, x=0, y=0, z=0, w=1)`
- 8  `class T`
- 9  `__init__(s)`
- 10  `class Comp`
- 11  `__init__(s)`
- 12  `set_bone_transform_by_name(s, n, tf, space)`
- 15  `class Actor`
- 16  `set_actor_location_and_rotation(s, *a)`
- 24  `rq()`
- 31  `entry()`

## area2/test_refpose.py  (26 lines)
- 7  `_skip(entry, *a, **k)`

## area2/test_spaced_names.py  (73 lines)
> Offline test (no editor): space-named models get whitespace-free asset names and are held back until the converter
- 45  `ref(model, nif, typ='STAT')`

## area2/undo_rain_mine.py  (10 lines)

## demo.py  (62 lines)
> One-click demo: asset converter + Skyrim (if not running) + Unreal editor with the live script.
- 10  `procs()`
- 17  `running(text, p)`
- 36  `editor_log(since)`  - The editor writes SkyBridge_2.log etc. when SkyBridge.log is held by another process: use the newest one.

## play.py  (158 lines)
> One-click launcher: Skyrim + the Unreal remaster view, in the right order, with the right focus.
- 18  `say(msg)`
- 22  `running(exe)`
- 26  `kill(*names)`
- 31  `kill_watchers()`
- 39  `start_services()`  - Background converters: models (asset_service) and Tamriel terrain chunks (tamriel_terrain --serve).
- 50  `free_gb()`
- 51  `class MS`
- 58  `skyrim_in_world()`
- 69  `editor_live(since)`
- 77  `focus_skyrim()`
- 86  `cb(hwnd, _)`
- 98  `stop()`
- 103  `main()`

## remaster_watch.py  (298 lines)
> Runs alongside the remaster view (started by `start_bridge.py --remaster`).
- 44  `class Packet`
- 45  `__init__(self)`
- 48  `read(self)`
- 69  `class WNDCLASSW`
- 75  `class BLENDFUNCTION`
- 83  `class Sprite`  - Click-through, never-activated, always-on-top window showing an RGBA image (per-pixel alpha).
- 86  `__init__(self, x, y, w, h)`
- 97  `update(self, img)`
- 115  `show(self, on)`
- 123  `font(size)`
- 132  `class Hud`
- 133  `__init__(self, rect)`
- 155  `draw_compass(self, heading)`
- 182  `draw_bars(self, v, flags)`
- 209  `draw_prompt(self, text)`  - Skyrim's activation prompt: the target's name, and under it the key in a box plus the verb.
- 243  `frame(self, v, visible)`
- 257  `pump()`
- 263  `main()`

## start_bridge.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/asset_service.py  (59 lines)
> On-demand asset service. The Unreal editor (live_bridge.py) appends model asset names to area2/requests.txt when it needs a
- 14  `nif_from_asset(name)`  - asset name 'architecture_whiterun_wrx_y' -> candidate nif paths ('architecture/whiterun/wrx_y.nif' ...): try e
- 22  `main()`

## tools/auto_build.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/blender_export.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/blender_preview.py  (24 lines)
> D:\blender.exe -b -P blender_preview.py -- <model.glb> <out.png>

## tools/bsa.py  (71 lines)
> Minimal Skyrim SE (BSA v105) reader. Usage: python -I bsa.py <archive> list <substring> | extract <outdir> <substring>
- 6  `class Bsa`
- 7  `__init__(self, path)`
- 44  `read(self, path)`

## tools/build_area.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/capture_window.py  (19 lines)
> Capture a window's contents even when it is covered (PrintWindow). Usage: python capture_window.py <exe> <out.png>

## tools/check_rotation.py  (55 lines)
> Compare the REFR rotation angles with the actual world rotation matrix of the loaded 3D (from the plugin dump).
- 16  `ypred_cw(z)`
- 18  `ypred_ccw(z)`
- 20  `err(a, b)`
- 35  `Rx(a)`
- 36  `Ry(a)`
- 37  `Rz(a)`
- 38  `mul(a, b)`

## tools/check_tex_keys.py  (34 lines)
> Report mesh materials whose texture key is ambiguous (suffix match picked by ue_assets.import_model) and diffuse

## tools/compare_refs.py  (67 lines)
> Compare runtime-truth references (SkyrimUnrealBridge_refs.tsv from the plugin) with area/placements.csv.
- 9  `asset(model)`

## tools/debug/npc_api.py  (6 lines)

## tools/debug/npc_creature_diag.py  (10 lines)

## tools/debug/npc_creature_test.py  (17 lines)

## tools/debug/npc_diag.py  (18 lines)

## tools/debug/npc_diag2.py  (21 lines)

## tools/debug/npc_diag3.py  (21 lines)

## tools/debug/npc_dump_rest.py  (11 lines)

## tools/debug/npc_names.py  (9 lines)

## tools/debug/npc_probe.py  (26 lines)

## tools/debug/npc_reload.py  (9 lines)

## tools/debug/npc_try.py  (15 lines)

## tools/debug/npc_view.py  (20 lines)

## tools/debug/npc_view2.py  (16 lines)

## tools/debug/npc_view3.py  (18 lines)

## tools/debug/npc_view_cow.py  (16 lines)

## tools/debug/walk_check.py  (61 lines)
> Which streamed actors are moving, and how far are their limb bones from the skeleton's rest pose? (rest pose = T/A pose of skeleton.nif)
- 13  `snap()`
- 17  `limb_angles(a)`
- 32  `camera()`

## tools/debug/walk_check_lib.py  (42 lines)
> Which streamed actors are moving, and how far are their limb bones from the skeleton's rest pose? (rest pose = T/A pose of skeleton.nif)
- 13  `snap()`
- 17  `limb_angles(a)`
- 32  `camera()`

## tools/debug/walk_watch.py  (26 lines)
> Sample the actor stream for ~40 s and report characters that move: are their limbs animated or at bind pose?

## tools/debug/water_diag.py  (13 lines)

## tools/debug/water_fix.py  (24 lines)

## tools/debug/water_recompile.py  (5 lines)

## tools/debug/water_view.py  (27 lines)

## tools/derive_spec.py  (33 lines)
> Specular masks for textures whose normal map has no specular alpha (textures_pbr.py left <key>_s.png.none).

## tools/detail_noise.py  (44 lines)
> Write area2/tex/detailgrain_n.png + detailgrain.png: seamless fine surface grain for M_SkyMaster's close-range detail.
- 15  `spectral_noise(rng, lo, hi, slope)`  - Periodic band-limited noise via FFT: frequencies lo..hi (cycles per tile), amplitude ~ f^-slope. Wraps exactly
- 25  `main()`

## tools/distant_world.py  (449 lines)
> Distant world layer: every mountain, cliff, big rock and tree that Skyrim places around the play area, read from the
- 35  `subs(buf)`
- 45  `rot_from_angles(rx, ry, rz)`  - Same as RotFromAngles in plugin/src/main.cpp (and tools/large_refs_preview.py).
- 54  `read_plugin(path, model_of, refs, worlds)`
- 58  `walk(s, e, world)`
- 92  `land_heights(sd)`  - LAND VHGT -> 33x33 absolute heights (rows = +y, columns = +x, 128 units apart).
- 106  `read_water(path, cells, worlds, radius=170000.0, land=None)`  - Exterior cells of WORLD whose CELL DATA has the 'has water' flag (0x2) and an explicit XCLW height ->
- 113  `walk(s, e, world)`
- 149  `classify(m)`
- 165  `remapper(name, data)`  - Plugin-local form id -> runtime form id (official masters, same as tools/tamriel_world.py Remap). The high byt
- 175  `scan_refs(plugins=PLUGINS, interiors_only=False, templates=None)`  - All placed references of the plugins (later plugins override) with their worldspace and cell, base models/type
- 188  `walk(s, e, world, cell)`
- 239  `ref_items(refs, model_of, typ, keep)`
- 255  `dump_world(ws)`  - Every placed reference with a model in worldspace `ws` (all base types) -> area2/world_<ws>.json, for comparin
- 264  `dump_interiors(prefix)`  - Interior cells whose editor id starts with `prefix` (e.g. 'Whiterun': Dragonsreach, Jorrvaskr, Breezehome, the
- 287  `drawn(it)`  - Same rules as Live.city_keep in live_bridge.py: the references the interior layer actually places.
- 297  `dump_dungeons(refs_per_file=30000)`  - Every interior cell of the official masters (Skyrim, Update, Dawnguard, HearthFires, Dragonborn; runtime form 
- 330  `flush()`
- 372  `main()`

## tools/editor_watchdog.py  (383 lines)
> Background watchdog: relaunches the Unreal editor (remaster view) after it CRASHES while Skyrim is being played.
- 45  `log(msg)`
- 58  `class PE32`
- 64  `processes()`  - {exe name lower: [pids]} without spawning tasklist.
- 79  `skyrim_in_world()`  - play.skyrim_in_world without leaking the mapping handle (this runs every 5 s for hours).
- 95  `focus_skyrim()`
- 100  `cb(hwnd, _)`
- 114  `last_session_log()`  - Newest editor log. While no editor runs this is the session that ended last (UE renames it to *-backup-* only
- 121  `crash_reports(near, slack=120)`  - Non-ensure crash folders written within `slack` s of `near`: [(folder, CrashType, ErrorMessage)].
- 140  `classify(path)`  - ('crash'|'clean'|'killed'|'empty', reason line) for an editor log of a session that has ENDED.
- 169  `load_state()`
- 176  `save_state(st)`
- 183  `decide(absent_since, st, now=None)`  - (action, message): action 'relaunch' or None.
- 218  `relaunch(st)`
- 254  `watchdog_pids()`
- 262  `is_running()`
- 269  `start()`
- 282  `stop()`
- 291  `loop()`
- 325  `self_test()`  - Crash detection against tonight's real logs; launches nothing.
- 358  `main()`

## tools/esm_area.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/esm_land.py  (95 lines)
> Extract terrain (LAND heightmaps) near a point for one worldspace -> OBJ.
- 13  `subs(buf)`
- 23  `walk(s, e)`

## tools/esm_land_tex.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/esm_persistence.py  (69 lines)
> Count placed refs in a worldspace by persistence (persistent vs temporary cell children) for models matching a filter.
- 13  `subs(buf)`
- 23  `walk(s, e)`

## tools/esm_refs.py  (65 lines)
> Find placed references (REFR) in Skyrim.esm whose base STAT uses one of the given NIFs.
- 13  `sub_records(buf)`
- 26  `walk(start, end)`

## tools/esm_water.py  (54 lines)
> Water heights per exterior cell (CELL XCLW) near a point -> water.csv (gx,gy,height). Child worldspaces fall back to the parent.
- 12  `subs(buf)`
- 22  `walk(s, e)`

## tools/fill_textures.py  (68 lines)
> Fill in diffuse maps the converter missed: every area2/tex/<key>_n.png without <key>.png gets its colour map from the
- 15  `decode(raw)`
- 24  `main()`

## tools/find_decals.py  (40 lines)
> List diffuse textures that Skyrim draws as decals (BSLightingShaderProperty flags1 bit 26 Decal / 27 Dynamic Decal).

## tools/find_lod.py  (25 lines)
> Where are Skyrim's terrain LOD meshes (.btr) and textures? Usage: python tools/find_lod.py

## tools/find_overrides.py  (75 lines)
> Which active plugins override given Skyrim.esm references, and how (deleted / persistent / disabled / moved).
- 14  `subs(buf)`
- 24  `scan(name)`
- 32  `walk(s, e, grp)`

## tools/find_tex.py  (23 lines)

## tools/gpu_profile.py  (35 lines)
> Capture one GPU frame in the live editor (ProfileGPU) and print the expensive passes per GPU queue.
- 11  `main()`

## tools/grass_blender.py  (189 lines)
> Blender side of tools/grass_placement.py.
- 15  `import_obj(path)`
- 28  `export(obj_dir, fbx_dir)`
- 47  `grass_material(mat, thr=0.5)`  - Texture colour x instance shade, alpha cut-out, light transmission for the thin blades.
- 71  `rotations(n, yaw)`  - XYZ Euler of Align(+Z -> n) @ Rz(yaw), vectorized.
- 88  `instancer(name, model, data)`  - Point cloud object whose geometry nodes put `model` on every point (rot/scl/shade attributes).
- 122  `preview(pdir, obj_dir, out_png)`
- 151  `ground(x, y)`

## tools/grass_placement.py  (632 lines)
> Grass placement for the Unreal remaster (Skyrim's own grass is off in the remaster profile).
- 52  `arg(name, default, n=1, cast=float)`
- 60  `min_grass_size()`  - iMinGrassSize from the grass mods' ini files in Data (Skyrim's default is 20).
- 72  `load_order()`
- 88  `class Db`
- 89  `__init__(self)`
- 97  `_body(data, p, sz, flags)`
- 102  `land_heights(sd)`
- 109  `read_plugin(path, db, worlds, center, radius, full)`  - full: also walk WRLD/CELL/LAND (masters); otherwise only the top-level LTEX/GRAS groups (mods).
- 118  `G(fid)`
- 122  `near(c)`
- 127  `record(t, p, sz, flags, fid)`
- 187  `walk(s, e, depth)`
- 215  `bilinear(g, u, v)`  - g[row=v, col=u], u/v arrays of fractional grid coordinates.
- 223  `tex_weights(base, layers, fx, fy)`  - {ltex: weight array} at cell vertex coordinates fx, fy (0..32): per quadrant the base texture, then every ATXT
- 247  `surface(h, fx, fy)`  - Height and face normal on the terrain triangles (diagonal (x, y)-(x+1, y+1), as terrain.obj / land_terrain).
- 260  `water_ok(g, z, wh)`
- 270  `grass_lists(db)`  - ltex -> GRAS keys that exist (first iMaxGrassTypesPerTexure entries, like the game).
- 275  `scatter_cell(key, land, wh, db, lists, spacing, seed, stats)`  - -> {gras key: structured array of instances (DT)} for one cell.
- 330  `asset_name(nif)`
- 334  `write_bin(path, parts)`  - parts: [((gx, gy), array)] -> SKGR file (instances sorted by cell).
- 348  `read_bin(path)`  - -> {(gx, gy): structured array}. Reference reader for the format (grass_layer.py has a numpy-free one).
- 362  `place(world, db, center, radius, spacing, seed)`
- 409  `archives()`
- 423  `data_file(rel, arcs)`
- 434  `dds_to_png(raw, png)`
- 446  `alpha_threshold(path)`  - NiAlphaProperty test threshold (0-255) of the first alpha property in the nif, or None.
- 462  `convert_models(world)`
- 525  `preview(world, db, spot, radius=1400.0)`  - Blender render of the grass around spot (Skyrim units): terrain of the cells around it + instances.
- 569  `best_spot(world, info, center)`  - Densest cell near the centre -> its densest 1024-unit tile centre (a grassy patch for the preview).
- 591  `main()`

## tools/grass_world.py  (425 lines)
> Grass layer: Skyrim's landscape grass (GRAS records) scattered the way the game does it, from the plugins' data, because
- 41  `arg(name, default, n=1, cast=float)`
- 49  `subs(buf)`
- 59  `land_heights(sd)`
- 72  `load_order()`  - Skyrim.esm, Update.esm, the DLCs, Creation Club (Skyrim.ccc), then the active plugins of plugins.txt, in order
- 88  `plugin_bytes(path, full)`  - The whole file, or (full=False) only its TES4 header plus the top-level LTEX/GRAS groups (cheap for big mods).
- 110  `read_plugin(path, db, center, radius, full=True)`  - Records of one plugin into db. Form ids become (defining plugin, low 24 bits) through the plugin's master list
- 124  `G(fid)`
- 130  `in_range(c)`
- 133  `walk(s, e, world)`
- 199  `bilinear(g, u, v)`  - g[row=v][col=u], u, v fractional grid coordinates.
- 207  `height(h, fx, fy)`  - Terrain height on the same triangles as the terrain meshes (esm_land_tex: diagonal from (x, y) to (x+1, y+1)).
- 215  `tex_weights(base, layers, fx, fy)`  - Blended landscape textures at cell vertex coordinates (fx, fy) in 0..32 -> [(ltex form id or 0, weight)].
- 229  `water_ok(g, z, wh)`  - GRAS 'units from water' rule. wh = cell water height or None (no water in the cell).
- 246  `scatter_cell(gx, gy, land, water, db, model_idx, spacing, seed, stats)`
- 297  `mesh_sources(nifs)`  - nif -> 'loose' / 'bsa:<archive>' / None, mod BSAs before vanilla (build_area.open_archives order).
- 325  `queue(models)`  - Append unconverted models to area2/requests.txt with their nif paths merged into area2/models.json (the same f
- 348  `main()`

## tools/land_terrain.py  (502 lines)
> Full-resolution Tamriel terrain with per-layer landscape textures (replaces the baked-tile terrain + covers water cells).
- 41  `blender_main(paths)`
- 78  `blender_obj(obj_dir, out_dir)`  - OBJ -> FBX with the converter's conventions (used for the trimmed LOD terrain).
- 114  `arg(name, default, conv=float)`
- 118  `subs(buf)`
- 128  `read_plugin(path, want, worlds, ltex, txst, land, wlist, prio)`  - LTEX/TXST everywhere; LAND of cells of the worldspaces in wlist (first wins: Whiterun's city worldspace has it
- 134  `walk(s, e, world)`
- 173  `parse_land(body)`
- 201  `cell_normals(h, vnml)`  - Normals from the heights; VNML is used when it agrees (its byte encoding varies between tools).
- 214  `cell_weights(rec)`  - ltex fid (0 = default dirt) -> 33x33 weight (sum 1 per vertex; quadrant seams averaged).
- 231  `class TexSource`
- 232  `__init__(self)`
- 246  `raw(self, rel)`
- 259  `decode(raw)`
- 268  `tex_key(rel)`
- 274  `convert_layer(src, key, diff, norm)`  - <key>.png (RGB + height in A) and <key>_n.png; returns True when the colour map exists.
- 318  `selected_cells(center, radius, wradius, ring)`
- 346  `main()`
- 364  `paths_of(fid)`
- 471  `trim_lod(covered)`  - Copy of area2/lod_obj/lodterrain.obj without triangles whose centre lies in a covered cell (lod_terrain.py

## tools/land_textures.py  (671 lines)
> Baked high-resolution landscape textures + full-resolution LAND terrain over the water cells.
- 49  `arg(name, default, conv=str)`
- 53  `subs(buf)`
- 63  `zstr(b)`
- 68  `load_order()`
- 82  `is_master(n)`
- 91  `class Plugin`
- 92  `__init__(self, name)`
- 100  `close(self)`
- 103  `fid(self, f)`
- 107  `body(self, p)`
- 112  `top_groups(self)`
- 121  `records(self, s, e)`
- 131  `parse_land(body, pl)`
- 156  `read_load_order(order, want)`  - -> ltex {fid: txst fid}, txst {fid: (diffuse, normal)}, land {(gx, gy): rec}; later plugins override.
- 185  `walk_world(pl, p, e, want, land, st, inworld)`
- 209  `class FastBsa`  - BSA v105 index restricted to wanted paths (one read for the name block; tools/bsa.py reads names byte by byte)
- 211  `__init__(self, path, wanted)`
- 236  `read(self, key)`
- 248  `class TexSource`
- 249  `__init__(self, order, wanted_rel)`
- 269  `raw(self, rel)`
- 280  `decode(raw)`
- 289  `tex_key(rel)`
- 295  `height_candidates(diff)`
- 300  `class Layers`  - Layer texture cache: PNG extraction (once) + per-resolution float arrays for baking.
- 302  `__init__(self, src)`
- 306  `extract(self, key, diff, norm)`
- 358  `get(self, key, R)`  - -> (height RxR, colour RxRx3 0..1, normal RxRx3 -1..1, spec RxR 0..1), float32.
- 377  `wanted_cells(wradius, near, ring, core_px)`
- 397  `cell_weights(rec, key_of)`  - texture key -> 33x33 weight; Skyrim order per quadrant: base, then each ATXT layer alpha-composited on top.
- 414  `stitch(W, land)`  - Average weights (and vertex colours) on shared cell edges so neighbouring bakes meet without a seam.
- 438  `interp_matrix(S)`
- 448  `blend(W, layers, S, want_normal, block=512)`  - Bake one cell at S x S px (row 0 = north). Returns colour float (S,S,3) or (normal (S,S,3), spec (S,S)).
- 482  `bake_cell(c, rec, W, layers, S, force)`
- 507  `write_tiles(land)`  - One npz per TILE x TILE cells: 33x33 vertices per cell, smooth normals across cell borders.
- 509  `H(gx, gy, ix, iy)`
- 552  `trim_lod(covered)`  - lodterrain.obj without the triangles whose whole footprint lies in cells this terrain covers (an inset
- 579  `blender(*args)`
- 585  `old_thumbs()`  - 512 px thumbnails of the current Unreal terrain bake (area2/tex/terrain_tile_*.png) for the comparison preview
- 597  `main()`
- 613  `paths_of(fid)`
- 626  `key_of(fid)`

## tools/land_textures_blender.py  (241 lines)
> Blender side of tools/land_textures.py (run by it, or by hand):
- 18  `mesh_from_npz(path, with_images=None)`
- 41  `material(name, image=None, color=None)`
- 58  `export(paths)`
- 73  `lod(obj_path, out_dir)`
- 100  `lod_region(rect, sink_tex=True, trimmed=False)`  - LOD terrain triangles inside the rect (from the original or the trimmed obj), with its lodtex_* textures.
- 132  `water_region(rect)`
- 153  `old_tiles(rect)`  - The current Unreal terrain (esm_land_tex.py bake): one 33x33 grid per cell with area2/tex/terrain_tile_* textu
- 186  `ground_z(x, y)`
- 197  `preview(out, view, variant)`

## tools/large_refs_preview.py  (74 lines)
> Export a worldspace's large references (city walls, towers, castle) from Skyrim.esm for a preview spawn in Unreal, until the
- 13  `subs(buf)`
- 23  `rot_from_angles(rx, ry, rz)`  - Same as RotFromAngles in plugin/src/main.cpp.
- 32  `walk(s, e)`

## tools/lod_horizon_preview.py  (261 lines)
> Offline check of the horizon layer: Blender render from Whiterun toward the horizon with the terrain LOD
- 25  `free_commit_gb()`
- 26  `class MS`
- 34  `in_wedge(x, y, yaw, half, rmin=0.0)`
- 43  `box_in_wedge(lo, hi, yaw, half)`
- 47  `ground_z()`  - Highest detailed-terrain vertex within 4000 units of the centre (Whiterun's hill top).
- 58  `small_tex(src, dst, size)`
- 69  `prepare(view, args, man, trees, gz)`
- 114  `run_outside()`
- 144  `tex_material(bpy, name, path, masked)`
- 166  `run_inside(job_path)`
- 177  `imp(path, col)`

## tools/lod_objects.py  (425 lines)
> Horizon object LOD from Skyrim's own LOD data (DynDOLOD/xLODGen loose output in Data\ wins over the BSAs):
- 40  `arc(name)`
- 51  `read_data(rel, bsas)`  - Loose file first (DynDOLOD/xLODGen output), then the archives.
- 63  `list_lod(sub, ext)`  - Lower-case file names under meshes\terrain\tamriel\<sub> from loose files + vanilla archives.
- 77  `near_cells()`
- 88  `distant_refs()`
- 94  `dds_to_png(raw, png, texmax, alpha)`
- 107  `tex_key(path)`
- 112  `make_texture(rel, key, texmax, masked_names)`  - rel = textures\...\x.dds. Returns {masked} or None when no colour map was found.
- 138  `pieces(verts, tris)`  - Split triangles into connected pieces (shared vertex indices). Returns lists of triangle indices.
- 142  `find(a)`
- 156  `choose_blocks(l4, l8, radius)`
- 165  `dist(lvl, x, y)`
- 170  `visit(lvl, x, y)`
- 187  `class DistantSurface`  - Surface samples (vertices, triangle centroids, edge midpoints) of every model the distant layer draws, from th
- 193  `__init__(self, refs)`
- 219  `enc(k)`
- 223  `occupied(self, x0, y0, x1, y1)`
- 240  `inside(self, occ, verts)`
- 246  `convert_objects(args, near, refs, masked_names)`
- 325  `convert_trees(args, near, refs)`
- 370  `write_card()`  - Two crossed quads, CARD units wide/high, bottom centre at the origin; OBJ v is flipped like nif2obj (v = 1 - v
- 384  `main()`

## tools/lod_terrain.py  (115 lines)
> Distant terrain backdrop (mountains) from Skyrim's own terrain LOD: meshes\terrain\tamriel\tamriel.<lvl>.<x>.<y>.btr
- 26  `read_tex(path)`

## tools/make_local_queue.py  (141 lines)
> Builds the work queue for the local model: notes/queue.json  (python tools/make_local_queue.py).
- 11  `add(tid, title, prompt, out, min_bytes=500, must=None, inputs=None, verify=False)`  - inputs: file paths (glob ok) or 'cmd:<shell command>'; the runner pastes their real contents into the prompt (

## tools/make_project_index.py  (175 lines)
> Exact (non-LLM) project index for the agent team -> notes/index/*.md and notes/index/symbols.json.   python tools/make_project_index.py
- 20  `files(*pats)`
- 30  `read(f)`

## tools/max_quality.py  (68 lines)
> Push the live Unreal editor to its absolute maximum quality for showcase screenshots (ray traced Lumen hit lighting, cinematic scalability,

## tools/merge_area.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/mesh_index.py  (45 lines)
> Index of every mesh in the game (BSAs + loose files): asset name -> nif path, so a model name can be turned back into its file even when
- 14  `key(rel)`
- 18  `build()`
- 36  `load()`

## tools/nif2obj.py  (207 lines)
> Minimal Skyrim SE NIF (20.2.0.7, BS stream 100) geometry extractor -> Wavefront OBJ (+ MTL with diffuse texture names).
- 8  `class R`
- 9  `__init__(self, b, p=0)`
- 10  `u8(self)`
- 11  `u16(self)`
- 12  `u32(self)`
- 13  `i32(self)`
- 14  `u64(self)`
- 15  `f(self, n=1)`
- 18  `sstr(self)`
- 19  `lstr(self)`
- 22  `half(h)`
- 26  `parse(data)`
- 46  `avobject(r)`
- 53  `mat_mul(parent, t, rot, s)`  - parent: (R(9), t(3), s). returns composed (R, t, s).
- 61  `xform(m, v)`
- 66  `_skinned_as_static(path)`  - Fallback for models whose shapes are all skinned (the normal reader skips those). Uses npc_skin's skinned read
- 81  `extract(path)`
- 85  `tex_of(shader_ref)`
- 99  `visit(idx, parent)`
- 182  `write_obj(shapes, obj_path, mtl_name=None)`

## tools/npc_autobuild.py  (22 lines)
> Background builder: every 15 s, build the character/creature FBXs for any new actor near the player (npc_batch.py --autobuild).
- 9  `skyrim_running()`

## tools/npc_batch.py  (82 lines)
> Build FBXs for every named NPC currently loaded in Skyrim (reads the actor stream) that has none yet.

## tools/npc_blender.py  (109 lines)
> Build a skinned character FBX (armature + joined body/hands/feet mesh) from npc_skin.py output.

## tools/npc_build.py  (106 lines)
> Build one named NPC (body + baked FaceGen head/hair/eyes/brows/beard) as a skinned FBX for Unreal.
- 20  `run(*a)`

## tools/npc_build_creature.py  (95 lines)
> Build one creature (wolf, dragon, draugr, cow, ...) as a skinned FBX for Unreal from its race skeleton + body-skin meshes.
- 20  `run(*a)`

## tools/npc_extract.py  (58 lines)
> Copy the character skeleton + base body NIFs (loose overrides first, then mod BSAs, then vanilla) into area2/npc/nif.

## tools/npc_hair_tint.py  (68 lines)
> Hair colours of the converted NPCs. Skyrim draws hair/brow textures in grey and multiplies them by the NPC's hair colour,
- 15  `shader_info(data, blocks, ref)`  - (shader type, texture-set diffuse path, hair tint or None) of a BSLightingShaderProperty (Skyrim SE layout).
- 36  `tints(path)`

## tools/npc_preview.py  (55 lines)
> Render a quick preview PNG of a character FBX (Blender, workbench).  D:\blender.exe -b -P npc_preview.py -- in.fbx out.png

## tools/npc_skin.py  (165 lines)
> Skinned NIF + skeleton extractor for NPC rendering in Unreal.
- 14  `name_of(strings, i)`
- 18  `skeleton(path)`
- 22  `visit(idx, parent, parent_bone)`
- 41  `tex_of(data, blocks, shader_ref)`
- 58  `meshes(path)`
- 104  `to_skeleton(v)`

## tools/npc_tex_alias.py  (103 lines)
> NPC textures whose file name is shared by different paths (e.g. anukethreplacers\Hair\Jenassa.dds, ...\Eyes\Jenassa.dds,
- 18  `norm(p)`
- 44  `read(tex)`
- 66  `convert(tex, png)`
- 85  `unique_stem(tex)`

## tools/offline_import.py  (47 lines)
> Import every converted-but-not-imported model into Unreal WITHOUT the game running and without opening an editor window.
- 14  `running(exe)`
- 18  `free_gb()`
- 19  `class MS`
- 25  `arg(name)`

## tools/perf_gpu_share.py  (73 lines)
> GPU share per process (SkyrimSE vs UnrealEditor) from the Windows GPU performance counters. Read-only, no editor access.
- 11  `names()`
- 21  `main()`

## tools/perf_profile.py  (52 lines)
> Switch the live Unreal view to a performance profile.   python tools/perf_profile.py [fast|faster|fastest|everyday]

## tools/photo_keys.py  (70 lines)
> Photo hotkeys while you fly around in Skyrim (works with Skyrim focused). Run by Photo_Shoot.bat; saves to screenshots/photos/.
- 38  `apply_sky()`
- 46  `photo(w, h)`

## tools/projected_snow.py  (50 lines)
> Which texture keys use Skyrim's special snow/mountain shading, from the models in area2/nif/*.nif:

## tools/puddle_noise.py  (44 lines)
> Write area2/tex/puddlenoise.png: seamless low-frequency fBm used by M_SkyMaster to place rain puddles in world space.
- 13  `tiling_noise(rng, cells)`  - Periodic value noise: random grid of `cells` x `cells`, smooth (cosine) interpolation, wraps at the edges.
- 25  `fbm(rng, base, octaves)`
- 33  `main()`

## tools/queue_large_refs.py  (67 lines)
> Queue the models of a worldspace's large references (walls, towers, castles) with the asset service ahead of time.
- 14  `subs(buf)`
- 24  `walk(s, e)`

## tools/read_actors.py  (30 lines)
> Print a summary of the plugin's actor pose stream.

## tools/read_bridge.py  (21 lines)
> Print live values from the SkyrimUnrealBridge shared memory (run while Skyrim is running).

## tools/read_gear.py  (24 lines)
> Print the plugin's worn-gear stream (armor addon models per actor).

## tools/read_world.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/run_local_queue.py  (253 lines)
> Feeds notes/queue.json to the local Ollama model one task at a time, unattended.
- 23  `log(msg)`
- 31  `codex_exe()`
- 38  `git(*a)`
- 42  `dirty()`
- 49  `load(p, d)`
- 56  `ok(t)`
- 77  `known_names()`  - Lower-case base names of every file git knows plus everything under area2/ and notes/ (for the invented-file c
- 90  `material(t)`
- 110  `call_model(codex, prompt)`  - One read-only model call; returns (reply_text, stdout_tail).
- 127  `run_task(codex, t)`
- 163  `free_commit_gb()`
- 165  `class MEM`
- 173  `wait_for_ollama(timeout=300)`  - The server may be mid-update or still starting: start the app if needed and wait until `ollama list` answers.
- 192  `main()`

## tools/set_cvar.py  (8 lines)
> Set console variables in the live editor:  python tools/set_cvar.py "r.ScreenPercentage 100" "sg.ShadowQuality 4"

## tools/shot_session.py  (50 lines)
> Start a clean photo session:  python tools/shot_session.py [--max]
- 12  `class MEM`
- 17  `free_commit_gb()`
- 23  `say(s)`
- 27  `kill_cmd(pattern)`

## tools/showcase_shot.py  (81 lines)
> Showcase screenshots from the live Unreal editor: pins the viewport camera around a target, forces hour + weather (+ ground wetness/snow),
- 26  `setup(x, y, z, d, az, el, hour, weather, wet, snow, fov)`
- 56  `shoot(name, x, y, z, d, az, el, hour, weather, wet=0.0, snow=0.0, fov=60.0, settle=8.0, w=3840, )`

## tools/shutdown_after_import.py  (52 lines)
> Wait for the offline import to finish, close every project process, then shut the PC down (2-minute warning; cancel with:  shutdown /a).
- 12  `say(msg)`
- 17  `import_running()`
- 24  `last_line()`

## tools/sky_extras.py  (28 lines)
> Mountain haze/cloud band, moons, planets and aurora for the live Unreal view.

## tools/skyrim_lightweight.py  (58 lines)
> Make the base Skyrim as cheap as possible while Unreal draws the picture. Run while Skyrim is CLOSED (it rewrites SkyrimPrefs.ini on exit).
- 27  `running()`
- 31  `set_keys(text, settings)`

## tools/skyrim_plugins.py  (33 lines)
> Turn off Skyrim SKSE plugins the bridge does not need (physics + visual-only), by MOVING the DLLs into Plugins\_disabled_for_bridge.

## tools/stream_coverage.py  (44 lines)
> Which models in the live world stream are missing in Unreal, and why. Usage: python tools\stream_coverage.py [filter]

## tools/tamriel_terrain.py  (439 lines)
> Terrain and water for all of Tamriel, from the official masters' LAND records (exact heights, texture layers, vertex colours).
- 44  `parse_land()`
- 48  `on(name, rm, t, flags, fid, body, world, xy)`
- 105  `load_land()`
- 111  `whiterun_cells()`  - Cells Whiterun's own hand-baked terrain covers (kept, so the Tamriel layers leave them out).
- 122  `class Heights`
- 123  `__init__(self, cells, skip)`
- 126  `has(self, gx, gy)`
- 129  `at(self, X, Y)`  - Height at global vertex (X, Y) = cell * 32 + local (0..32); clamped into existing neighbours.
- 139  `normal(self, X, Y, step)`
- 150  `class Baker`
- 151  `__init__(self, ltex)`
- 156  `image(self, path)`
- 183  `quad(self, ltex_fid, Q, px)`  - Q x Q pixels of a landscape texture tiled so one repeat covers TILE_UNITS (px pixels = one cell).
- 203  `cell(self, c, px)`  - px x px albedo of one LAND cell (image top = north), layers blended by their opacity, times vertex colour.
- 223  `class Obj`
- 224  `__init__(self, path)`
- 229  `group(self, name)`
- 232  `vert(self, x, y, z, u, v, n)`
- 237  `tri(self, a, b, c)`
- 240  `close(self)`
- 248  `emit_cells(obj, H, cells, step, uv_of, skirt_edge)`  - Grid of every cells' vertices (every `step`th LAND vertex) plus skirts on edges where skirt_edge(gx, gy, side)
- 275  `blender(obj_dir)`
- 282  `build_low(land, baker)`
- 319  `build_chunk(land, baker, cx, cy, skip=None)`  - Full-res mesh + 4096 px texture of one 4x4-cell chunk. Returns the asset name or None (no LAND there).
- 348  `build_water(land)`  - Strips of visible water for every Tamriel cell with the 'has water' flag; Whiterun's water_wide.csv cells are 
- 386  `serve()`
- 419  `main()`

## tools/tamriel_world.py  (204 lines)
> All of Tamriel for Unreal: every placed reference with a model in the Tamriel worldspace (forts, castles, farms, villages,
- 41  `keep(m, typ)`  - Same rules as Live.city_keep: loose items, effects and editor markers stay with the live stream.
- 50  `kind(m)`
- 58  `read_masters(data)`  - TES4 header MAST list of a plugin.
- 65  `class Remap`  - Plugin-local form id -> runtime form id (official masters only).
- 67  `__init__(self, name, data)`
- 71  `__call__(self, fid)`
- 76  `scan(want_world=None, on_record=None)`  - Walk every official master; on_record(plugin, remap, type, flags, fid, body, world, cell_xy) for WRLD/CELL/REF
- 88  `walk(s, e, world)`
- 119  `main()`
- 123  `on_record(name, rm, t, flags, fid, body, world, xy)`

## tools/textures.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/textures_pbr.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## tools/truth_to_area.py  (30 lines)
> Turn the runtime dump (SkyrimUnrealBridge_refs.tsv) into an area json for build_area.py.

## tools/ue_run.py  (8 lines)
> Run a Python file inside the live editor (live_bridge debug hook) and print its output.

## tools/upscale_textures.py  (76 lines)
> AI-upscale (Real-ESRGAN x2, CUDA) the low-resolution diffuse textures in area2/tex.
- 23  `upscale_rgb(model, s, rgb)`  - rgb: HxWx3 uint8 -> (sH)x(sW)x3 uint8, processed in padded tiles to keep VRAM low (Skyrim + Unreal share the G
- 41  `main()`

## tools/verify_models.py  (88 lines)
> Automatic comparison: game truth (plugin dump with bounds) vs my converted models.
- 14  `asset(m)`
- 20  `obj_bounds(path)`

## tools/verify_unreal.py  (54 lines)
> Compare Unreal's placed-object bounds (area2/ue_actors.csv, written by the game at startup) with the game's own bounds
- 18  `asset(m)`

## tools/water_flow.py  (77 lines)
> Downhill flow direction for every water strip in area2/water_quads.csv -> area2/water_flow.csv (same line order).
- 35  `gauss(sig)`
- 41  `blur(a, sig)`

## tools/water_flow_run.py  (7 lines)
> python tools/ue_run.py tools/water_flow_run.py   (needs the editor running with live_bridge; water_flow.csv from tools/water_flow.py)

## tools/weatherfx_build.py  (14 lines)

## tools/weatherfx_check.py  (16 lines)

## tools/weatherfx_splash.py  (8 lines)

## tools/weatherfx_test.py  (20 lines)

## unreal/SkyBridge/apply_textures.py  (47 lines)

## unreal/SkyBridge/atmosphere.py  (315 lines)
> Lighting quality tiers and the time-of-day / weather look, used by live_bridge.
- 42  `log(msg)`
- 46  `cmd(c)`
- 50  `setp(obj, name, value)`
- 59  `clamp(x, a=0.0, b=1.0)`
- 62  `smooth(a, b, x)`
- 66  `lerp(a, b, t)`
- 70  `detect_gpu()`  - (name, VRAM GB) of the adapter with the most dedicated memory (the discrete GPU on hybrid laptops/desktops).
- 96  `auto_tier(name, vram)`  - Conservative: Skyrim renders on the same GPU, so a card gets one tier less than it would running Unreal alone.
- 112  `wanted_tier()`
- 123  `apply_quality(live, tier=None)`
- 177  `light_quality(live, c, i)`
- 185  `look(live, elev, hour, mul, fog, rain, snow, storm, weather, interior)`  - Grading, haze, mist and god rays for the current sun elevation (deg) / weather; called only when they change.
- 268  `flicker(live, cam, now)`  - Fire lights near the camera flicker (intensity only: cached shadow pages stay valid). Cheap: a few lights, 30 
- 300  `sweep_captures(live)`  - Debug capture scripts (area2/*capture*.py) leave SceneCapture2D actors rendering the whole scene every frame

## unreal/SkyBridge/audit_slots.py  (18 lines)

## unreal/SkyBridge/fire_fx.py  (120 lines)
> Procedural fire for the live view: Skyrim streams each torch's LIGHT but not its flame, so lit lights get an animated flame here.
- 38  `_e(m, cls, x, y, **props)`
- 45  `build(rebuild=False)`
- 76  `_world()`
- 80  `clear()`
- 91  `place(live, flip=0.0, scale=1.0)`  - Spawn flames at the currently lit lights. Returns how many.

## unreal/SkyBridge/fix_slots.py  (41 lines)

## unreal/SkyBridge/grass_live.py  (235 lines)
> Grass around the camera from area2/grass (tools/grass_world.py): Skyrim's GRAS scatter on the LAND texture layers.
- 26  `_log(msg)`
- 30  `_state(live)`
- 39  `_dir(st)`
- 43  `_index(st)`
- 50  `_dataset(live, st)`  - Grass data folder for the packet's worldspace (None: no grass there), re-read every 0.5 s. A change of worldsp
- 67  `_cell(st, gx, gy)`
- 75  `_foliage(st, comp)`  - Grass cards: two-sided, alpha-masked, two-sided-foliage shading (remaster_materials.npc_hair does exactly that
- 92  `_actor(live, st, name, mesh)`
- 121  `_wanted(idx, sx, sy)`  - {(tx, ty): near?} for tiles whose centre is within RADIUS (+ half a tile) of the camera.
- 135  `_tile_items(st, idx, t)`
- 141  `update(live, cam_loc=None)`
- 153  `_update(live, st, cam_loc)`
- 218  `clear(live)`
- 230  `stats(live)`  - (instances near, far, models built, tiles) for debugging.

## unreal/SkyBridge/import_area.py  (61 lines)

## unreal/SkyBridge/import_area2.py  (71 lines)
- 10  `task(f, dest)`

## unreal/SkyBridge/import_terrain.py  (25 lines)

## unreal/SkyBridge/import_terrain2.py  (26 lines)

## unreal/SkyBridge/import_terrain3.py  (39 lines)
- 8  `task(f, dest)`

## unreal/SkyBridge/import_whiterun.py  (15 lines)

## unreal/SkyBridge/land_terrain_live.py  (428 lines)
> Full-resolution LAND terrain with blended landscape layers (tools/land_terrain.py -> area2/landterrain/), live in the editor.
- 34  `log(msg)`
- 38  `_task(path, dest, name=None, options=None)`
- 46  `_fbx_options()`
- 61  `texture(key, kind)`  - kind: color | normal | weight
- 86  `_e(m, cls, x, y, **props)`
- 93  `_custom(m, x, y, code, inputs, out_type, extra=(), desc='')`
- 107  `blend_hlsl()`  - Height-aware blend of NL layers. Only layers with weight are sampled; one (anisotropic, wrapping) sampler for 
- 151  `material(rebuild=False)`
- 232  `meta()`
- 239  `instance(name, info, parent)`
- 258  `mesh(name)`
- 276  `_camera_skyrim()`
- 284  `_alive(a)`
- 291  `_find_existing()`
- 301  `spawn(live=None, max_new=None, names=None)`  - Place the tiles (nearest to the camera first). Returns how many tiles are still waiting.
- 335  `tick(live=None)`  - Call from live_bridge.tick: one tile per call until all are placed; follows interior cells like the old terrai
- 348  `_old_terrain_actors()`  - The baked terrain (/Game/Area2/terrain) and Skyrim's LOD terrain (/Game/Area2/lodterrain) placed by live_bridg
- 361  `_lod_actor()`  - Skyrim's LOD terrain without the triangles over the full-resolution cells (tools/land_terrain.py --lod).
- 394  `swap(live=None, on=True)`  - on: new terrain replaces the old (reversible with on=False). Hides via component visibility, so live_bridge's
- 417  `clear(live=None)`

## unreal/SkyBridge/live_bridge.py  (1138 lines)
> SkyBridge Live: runs inside the Unreal editor (no compiled module, so nothing for Windows to block).
- 36  `open_map(name)`
- 43  `log(msg)`
- 47  `V(x, y, z)`
- 50  `sky_to_ue_pos(p)`
- 53  `ue_rotation(R)`  - Skyrim row-major rotation R -> UE rotator for a mesh imported through Blender/FBX: A = C * R * diag(1,-1,1).
- 62  `class Live`
- 63  `__init__(self)`
- 93  `spawn(self, cls, loc=None, rot=None)`
- 97  `setp(obj, name, value)`  - Set an editor property, plus its override_ flag for post-process settings; tolerate engine-version differences
- 106  `build_environment(self)`  - Physically based outdoor lighting (real sun/moon illuminance, atmosphere, volumetric clouds + fog, Lumen).
- 169  `spawn_static_world(self)`
- 204  `spawn_cell_water(self)`  - Skyrim's own water: one plane per exterior cell with the 'has water' flag at its XCLW height
- 263  `weather_family(w)`
- 270  `weather_setup(self)`  - Dynamic cloud material, weather parameter collection and the rain curtains (created on first use).
- 322  `set_weather_param(self, name, value)`
- 329  `set_interior(self, interior)`  - Interior cells have no sky: no sun/moon/clouds/rain, so daylight cannot leak through gaps in the walls.
- 352  `streamed_weather(self, v)`  - Packet v2: Skyrim's own weather classification (blended over its transition), sun position/colour and fog.
- 366  `update_sky(self, hour, weather, cam=None, v=None)`
- 466  `asset_name(model)`
- 471  `spaced_ok(nif)`  - False for a nif path with a space until the converter names its outputs the same way (it creates
- 482  `mesh(self, name)`
- 500  `request(self, name, model)`
- 511  `import_ready(self)`  - Import models that the asset service finished converting (names listed in area2/ready.txt).
- 535  `read_world(self)`
- 547  `apply_world(self, data, hdr)`
- 586  `taken(p)`
- 596  `apply_lights(self, data, n)`
- 625  `spawn_some(self)`
- 679  `city_world(self, ws)`  - Entering a city worldspace loads area2/world_<edid>.json (tools/distant_world.py --world <edid>): every placed
- 710  `load_interiors(self)`  - area2/interiors_<prefix>.json (tools/distant_world.py --interiors Whiterun): every reference of those cells.
- 732  `load_dungeon(self, edid)`  - Read one dungeon cell from its interiors_dungeons_<n>.json (the rest of that file is dropped again).
- 740  `interior_key(self)`  - Which known interior cell the player is in: the one most of the streamed references belong to ('int:<edid>'),
- 765  `city_keep(cls, it)`
- 773  `prefetch_cities(self)`  - Queue every model of the dumped interiors and the other cities that was never converted, so arriving there doe
- 806  `prefetch_step(self)`  - The asset service converts everything pending as one batch: feed it 40 at a time, after the previous batch is
- 832  `near(p, q, d=300.0)`
- 835  `city_some(self, budget)`
- 868  `distant_setup(self)`  - area2/distant_refs.json (tools/distant_world.py): Skyrim's placed mountains/cliffs/rocks/trees well beyond the
- 882  `water_slots(comp, model)`  - Skyrim water meshes (Whiterun canals, pools, water/water1024) use the water shader, which has no texture: the
- 907  `fix_slots(comp, mesh)`  - Slots imported before their colour map existed (white, unmasked): override on the component. Editing the mesh
- 925  `distant_some(self)`  - Check a few models per tick; build at most one instanced actor (adding thousands of instances takes a moment).
- 961  `addons_tick(self, dt)`  - Optional layer modules (grass_live, lod_objects_live, land_terrain_live, weather_fx, ...), one module name per
- 1013  `tick(self, dt)`
- 1022  `tick_body(self, dt)`
- 1130  `start()`

## unreal/SkyBridge/memory_governor.py  (186 lines)
> Keeps the editor's memory bounded while you travel (called from live_bridge.tick).
- 32  `class _MemStatus`
- 39  `memory_gb()`
- 46  `log(msg)`
- 50  `_cvars(cmds)`
- 55  `_textures(mi)`  - Texture paths a material instance uses (cached per instance path).
- 74  `_in_use()`  - (mesh paths, material paths, texture paths) referenced by any component in the level.
- 96  `sweep(live, now, level)`
- 111  `_collect(live, now, level)`
- 156  `tick(live)`

## unreal/SkyBridge/mountain_mist.py  (46 lines)
> Soft atmospheric depth for the live view: distance haze plus a low cloud band that hugs the mountainsides, so the far world can be
- 10  `_fog(live)`
- 14  `apply(live, strength=1.0, cam_z=None)`
- 36  `off(live)`

## unreal/SkyBridge/night_sky.py  (127 lines)
> Moons, planets and aurora for the night sky of the live view (tasteful: two pale moons with phases, three small steady planets).
- 40  `_e(m, cls, x, y, **props)`
- 47  `build(rebuild=False)`
- 75  `_actors()`
- 79  `remove()`
- 86  `_spawn(live, mat)`
- 114  `apply(live, night=True, aurora=True)`

## unreal/SkyBridge/npc_live.py  (795 lines)
> NPCs in the live Unreal scene: imports area2/npc/export/npc_<baseId>.fbx (tools/npc_build.py) as skeletal meshes and poses them from
- 35  `log(msg)`
- 40  `quat_to_mat(x, y, z, w)`
- 46  `mat_to_quat(m)`
- 59  `mul(a, b)`
- 63  `tr(a)`
- 67  `mv(a, v)`
- 71  `conj_flip(a)`
- 76  `qmul(a, b)`
- 82  `qconj(a)`
- 86  `qflip(a)`
- 90  `qrot(q, v)`
- 96  `qnlerp(a, b, t)`
- 105  `stream_seq()`
- 117  `parse_bones(a)`  - Bones of an actor returned by read_actors(lazy=True) (parsing every actor's ~134 bones costs ~3 ms per frame).
- 127  `read_actors(cam=None, radius=None, lazy=False)`  - All actors; with cam/radius only actors within radius get their bones parsed; lazy: none (call parse_bones).
- 166  `skel_key(a)`  - 'male'/'female' for the human skeletons; otherwise a file-name key from the race skeleton nif path (creatures:
- 174  `rest_pose(sex)`
- 187  `_png_for_slot(slot)`
- 203  `_alias(slot)`
- 215  `_hair_tint(key, slot)`  - Linear hair colour for this mesh's slot (tools/npc_hair_tint.py), via the slot's Skyrim texture path in npc_<k
- 245  `_material_for_slot(slot, key=None)`
- 282  `_material_for_stem(slot, d, stem)`
- 310  `mesh_for(base)`
- 353  `_spawn(a_info, mesh, lb)`
- 372  `_ensure_rest(entry)`  - Read the reference pose of EVERY bone once, before any bone is moved (a child's component-space transform chan
- 393  `_ref_scales(entry)`  - Reference component-space scale per bone. The FBX armature carries a x100 scale that every bone inherits; a po
- 410  `_plan(entry, sex)`  - Per-bone constants of the pose math (module docstring), folded so a bone costs two quaternion products + two v
- 430  `ue_bone(name)`  - Unreal's FBX import renames bones: spaces -> '-', '[' and ']' -> '_'  ('NPC Root [Root]' -> 'NPC-Root-_Root_')
- 438  `_is_bind(bones, rest, rq)`  - True when every limb bone sits at the SAME angle from its rest pose (a pure root rotation): the skeleton is un
- 453  `_limb_rel(bones, rq)`
- 458  `_limb_change(a, b)`  - Largest angle (deg) between two _limb_rel samples; -1 when they share fewer than 4 limbs (creatures).
- 466  `_walk_record(sex, entry, pose, now)`  - Record ~2.5 s of a walker Skyrim IS animating and cut one seamless gait cycle from it (the later sample whose 
- 489  `_walk_pose(sex, entry, now)`  - Next pose of the recorded gait cycle for this walker (own phase, played at its own speed).
- 505  `_ingest(entry, a_info, now)`  - New stream sample for this actor: pick the pose to show and append (t, root, pose) to its short history.
- 552  `_apply_pose(entry, pose, sex, far)`
- 594  `_smooth(entry, now, dist, lb)`  - Every editor frame: place the actor between its last two stream samples (shown ~one stream interval late, so m
- 635  `_pose_gap(dist)`  - Seconds between limb updates: every stream sample near, fewer far away.
- 644  `read_gear()`  - Worn gear stream (~1 Hz): actor ref id -> dict(wfl, weapons=[right, left]).
- 668  `_weapon(entry, a, gear, live, lb)`  - Right-hand weapon as a rigid mesh on the streamed WEAPON node, only while the weapon is drawn.
- 701  `tick(live)`  - Every editor frame: smooth each NPC between stream samples. When the stream has a new frame (seq changed, ~30 
- 728  `_has_fbx(base)`  - os.path.exists per actor per frame was ~10% of the NPC time; new FBXs (npc_batch) are picked up within 10 s.
- 738  `_read_and_spawn(live, lb, now)`

## unreal/SkyBridge/offline_import.py  (79 lines)
> Headless bulk import (run by tools/offline_import.py through UnrealEditor-Cmd -run=pythonscript, no window, no Skyrim needed):
- 20  `say(msg)`

## unreal/SkyBridge/probe_bounds.py  (6 lines)

## unreal/SkyBridge/reimport_textures.py  (29 lines)
> Re-import the textures that tools/upscale_textures.py replaced (names in area2/tex/upscaled.txt), keeping the assets

## unreal/SkyBridge/remaster_materials.py  (847 lines)
> One master material for every Skyrim surface, with per-texture material instances.
- 22  `log(msg)`
- 26  `_lines(name)`
- 31  `_import_tex(key, kind)`  - kind: 'color' | 'normal' | 'masks' | 'linear'
- 56  `weather_collection()`
- 71  `_e(m, cls, x, y, **props)`
- 131  `master()`  - Load M_SkyMaster, (re)building its graph in place when missing or older than the current version (instances ke
- 354  `rain_material()`  - Translucent falling-streak material for the rain curtains live_bridge keeps around the camera (strength = MPC 
- 405  `rain_streak_mesh()`  - Engine cylinder copy whose bounds cover the whole rain box: the material moves every streak (wrap + fall), so 
- 419  `rain_drops_material(rebuild=False)`  - Falling streaks for SkyBridgeViewLibrary.SpawnRainField: each instance's position wraps into a box around the 
- 512  `night_sky_material(rebuild=False)`  - Sky dome material (Is Sky, unlit): the sky atmosphere's own luminance + sun/moon discs + stars and aurora
- 555  `lod_water()`  - Import area2/export/lodwater.fbx (water layer of Skyrim's terrain LOD: rivers/lakes at their real heights).
- 572  `water_material(rebuild=False)`  - Single Layer Water (physically based absorption/scattering) with Skyrim's water normal map panned along the
- 590  `instance_for(key)`
- 620  `configure(mi, key)`  - Blend mode / shading model / decal settings from the texture lists (re-runnable on existing instances).
- 650  `npc_hair(mi)`  - Hair / brow / lash cards: two-sided cut-out with back-lit transmission (one-sided cards vanish from behind).
- 663  `hair_material()`  - M_SkyHair: NPC hair cards with UE's Hair shading model (anisotropic strand highlights + scatter), dithered cut
- 694  `hair_instance(key, tint)`  - MI_hair_<key>_<rrggbb> of M_SkyHair for texture area2/tex/<key>.png with linear tint (r, g, b).
- 713  `npc_skin(mi)`  - Body / head / hands: subsurface-profile skin (engine default Burley profile).
- 725  `lod_terrain()`  - Import area2/export/lodterrain.fbx (tools/lod_terrain.py) as /Game/Area2/lodterrain with one instance per tile
- 748  `fix_missing_slots()`  - Give mesh slots that never got an MI_ (their colour map was missing at import) one now. Headless only.
- 769  `nanite_landscape()`  - Nanite for the mountains/rocks/trees the distant-world layer instances by the thousand. Headless only: togglin
- 788  `ensure_usage(m)`  - Set usage flags up front; otherwise every instance sets them at runtime and dirties/recompiles the master.
- 801  `convert_all()`  - Point every slot of every /Game/Area2 mesh that uses an old M_<key> at MI_<key>.

## unreal/SkyBridge/tamriel_live.py  (482 lines)
> All of Tamriel in the editor (called from live_bridge's tick: tamriel_live.tick(live)).
- 30  `log(msg)`
- 34  `rot_from_angles(rx, ry, rz)`  - Same as RotFromAngles in plugin/src/main.cpp (tools/distant_world.py).
- 43  `cull_for(nif)`  - End cull distance (cm, 0 = never) by model folder.
- 57  `instanced_actor(live, mesh, label, folder)`
- 69  `import_fbx(fbx, dest)`
- 101  `far_material()`  - M_TerrainFar: atlas texture placed by world position (no UVs needed), wet darkening and snow cover from MPC_We
- 150  `far_instance(GX, GY)`
- 169  `class Tamriel`
- 170  `__init__(self, live)`
- 216  `cam(self)`
- 219  `dist2(self, key, cam)`
- 222  `finished(self)`  - Models the asset service has finished (ready or failed), re-read every few seconds.
- 237  `feed(self, cam)`  - Ask the asset service for the nearest unconverted models, at most MAX_OUTSTANDING at a time.
- 272  `build_some(self, cam)`
- 305  `hidden(self, tag)`
- 311  `update_visibility(self)`
- 328  `terrain_step(self, cam)`
- 366  `drop_old_lod(self)`
- 374  `low_slot(self, chunk, show_low)`  - Hide/show the low-res section of a chunk (material slot 'tlo_<cx>_<cy>' of its 16x16-cell group).
- 388  `chunk_step(self, cam)`
- 438  `spawn_water(self)`
- 461  `tick(self)`
- 474  `tick(live)`

## unreal/SkyBridge/ue_assets.py  (143 lines)
> Helpers used by live_bridge.py to import one converted model (FBX) with its materials, inside the editor.
- 11  `_lines(name)`
- 16  `_task(f, dest)`
- 22  `_texture(key)`
- 38  `material_for(key)`
- 49  `legacy_material_for(key)`
- 94  `hidden_material()`
- 106  `import_model(name)`  - Import area2/export/<name>.fbx as /Game/Area2/<name> and give each slot its textured material.
- 119  `slot_material(slot)`  - Material for an imported FBX slot name ('..._<texture key>_dds[_ncl_...]'), or None when its texture is missin

## unreal/SkyBridge/upgrade_materials.py
(parse error: invalid non-printable character U+FEFF (<unknown>, line 1))

## unreal/SkyBridge/water_flow_apply.py  (95 lines)
> Run inside the editor (python tools/ue_run.py unreal/SkyBridge/water_flow_apply.py).
- 14  `_n(m, cls, x, y, **props)`
- 21  `rebuild_water_material()`
- 71  `apply_flow(actor)`  - actor: the CellWater actor (one InstancedStaticMeshComponent, instances in water_quads.csv order).
- 87  `run()`  - Rebuild the material and apply the flow to the live CellWater actor (tools/water_flow_run.py calls this in the

## unreal/SkyBridge/water_setup.py  (72 lines)
- 28  `chunk(t, d)`

## unreal/SkyBridge/weather_fx.py  (461 lines)
> Weather effects that live_bridge's rain field does not cover: falling snow and rain splash rings.
- 38  `log(msg)`
- 42  `_e(m, cls, x, y, **props)`
- 49  `_custom(m, x, y, code, inputs, out, desc)`
- 58  `_material(name, rebuild)`  - -> (material, build_graph). delete_all_material_expressions leaves old nodes behind, so a rebuild deletes and
- 84  `collection()`
- 99  `snow_mesh()`  - Engine plane copy whose bounds cover the whole snow box (the material moves every flake, see rain_streak_mesh)
- 139  `snow_material(rebuild=False)`
- 229  `splash_material(rebuild=False)`
- 278  `build(rebuild=False)`
- 284  `_world()`
- 288  `_set(name, value)`
- 299  `_alive(a)`
- 306  `_find(label)`
- 313  `_spawn()`  - Lazily create assets + actors (re-uses actors left by an earlier module load in the same level).
- 350  `_show(name, on)`
- 356  `_packet(live)`
- 365  `update(live, cam_loc, dt=None, v=None)`  - Per frame (cheap): smooth Skyrim's snow/rain amounts, integrate wind drift, keep the actors around the camera.
- 422  `clear(live=None)`  - Destroy the actors and zero the parameters (assets stay).
- 442  `install_test_tick(live)`  - Drive update() from our own slate tick (until live_bridge has the hook). Camera = the level viewport camera.
- 447  `_tick(dt)`
- 457  `uninstall_test_tick()`
