"""Runs inside a headless UnrealEditor (started by tools/offline_preview.py, no Skyrim): builds a small studio scene, spawns the
requested NPC meshes with the materials saved in /Game/Npc and writes PNGs of them. Settings arrive in env vars:
SB_KEYS (comma list of NPC keys, default: first saved ones), SB_OUT (folder), SB_DIST (camera distance cm), SB_SIZE (px)."""
import os, math, glob
import unreal

OUT = os.environ.get("SB_OUT", r"C:\Users\Aidan\SkyrimUnrealBridge\screenshots\offline")
DIST = float(os.environ.get("SB_DIST", "230"))
SIZE = int(os.environ.get("SB_SIZE", "1280"))
os.makedirs(OUT, exist_ok=True)
log = lambda m: unreal.log("[OfflinePreview] " + m)

keys = [k for k in os.environ.get("SB_KEYS", "").split(",") if k]
if not keys:
    keys = sorted(os.path.basename(f)[4:12] for f in glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Npc\npc_*.uasset"))[:3]
keys = list(dict.fromkeys(keys))
log("keys %s" % keys)

unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
world = unreal.EditorLevelLibrary.get_editor_world()
spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
V, R = unreal.Vector, unreal.Rotator

sun = spawn(unreal.DirectionalLight, V(0, 0, 500), R(-35, 40, 0))
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property("intensity", 9.0)
sky = spawn(unreal.SkyLight, V(0, 0, 300), R(0, 0, 0))
sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property("intensity", 1.2)
sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property("real_time_capture", True)
spawn(unreal.SkyAtmosphere, V(0, 0, 0), R(0, 0, 0))
floor = spawn(unreal.StaticMeshActor, V(0, 0, 0), R(0, 0, 0))
floor.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane.Plane"))
floor.set_actor_scale3d(V(40, 40, 1))

rt = unreal.RenderingLibrary.create_render_target2d(world, SIZE * 16 // 9, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1))
cap = spawn(unreal.SceneCapture2D, V(0, 0, 0), R(0, 0, 0))
cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
cc.set_editor_property("texture_target", rt)
cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
cc.set_editor_property("fov_angle", 40.0)
cc.set_editor_property("capture_every_frame", False)

jobs = []                                     # (actor, name) camera shots for every NPC, taken one per few frames once shaders are ready
actors = []
for key in keys:
    mesh = unreal.load_asset("/Game/Npc/npc_" + key)
    if not isinstance(mesh, unreal.SkeletalMesh):
        log("no mesh for %s" % key); continue
    a = spawn(unreal.SkeletalMeshActor, V(0, 0, 0), R(0, 0, 0))
    a.skeletal_mesh_component.set_skeletal_mesh_asset(mesh)
    a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
    b = mesh.get_bounds(); top = b.origin.z + b.box_extent.z
    actors.append(a)
    jobs.append((a, key, "full", DIST, top * 0.55)); jobs.append((a, key, "torso", DIST * 0.45, top * 0.62))

import time


def luma():
    tot = 0.0; n = 0
    for gx in range(8):
        for gy in range(5):
            c = unreal.RenderingLibrary.read_render_target_pixel(world, rt, int((gx + 0.5) * rt.size_x / 8), int((gy + 0.5) * rt.size_y / 5))
            tot += (c.r + c.g + c.b) / 3.0; n += 1
    return tot / n


S = dict(job=0, wait=0, t0=time.time(), jt=None)


def _tick():
    if time.time() - S["t0"] < 30:                     # let the editor finish starting
        return
    if S["job"] >= len(jobs):
        log("done"); unreal.unregister_slate_post_tick_callback(H[0])
        unreal.SystemLibrary.execute_console_command(world, "QUIT_EDITOR"); return
    a, key, name, dist, z = jobs[S["job"]]
    S["wait"] += 1
    if S["wait"] == 1:
        S["jt"] = time.time()
        for o in actors:
            o.set_is_temporarily_hidden_in_editor(o is not a); o.set_actor_hidden_in_game(o is not a)
        cap.set_actor_location_and_rotation(V(-dist, 0, z), R(-2, 0, 0), False, False)
    elif S["wait"] % 20 == 0:                          # every 20 frames: capture; accept when the picture is lit (shaders are ready)
        cc.capture_scene()
        l = luma()
        if l > 0.03 or time.time() - S["jt"] > 400:
            unreal.RenderingLibrary.export_render_target(world, rt, OUT, "npc_%s_%s.png" % (key, name))
            log("wrote %s %s (luma %.3f, %.0f s)" % (key, name, l, time.time() - S["jt"])); S["job"] += 1; S["wait"] = 0


def tick(dt):
    try:
        _tick()
    except Exception:
        import traceback; log("TICK ERROR " + traceback.format_exc().replace(chr(10), " | ")); S["job"] = 10 ** 6


H = [unreal.register_slate_post_tick_callback(tick)]
log("scene ready, waiting for shaders")
