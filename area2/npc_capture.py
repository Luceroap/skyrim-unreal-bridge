"""Close-up renders of NPCs without touching the user's camera. area2/npc_step.txt: 'setup' | 'grab <prefix>' | 'done'."""
import sys, math
step = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\npc_step.txt").read().split()
world = unreal.EditorLevelLibrary.get_editor_world()
out = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
nl = sys.modules["npc_live"]
if step[0] == "setup":
    caps = []
    names = step[1].split(",") if len(step) > 1 else None
    ents = sorted([e for e in nl._state["actors"].values() if e["comp"].get_num_bones() > 100
                   and (not names or any(n in e["actor"].get_actor_label() for n in names))], key=lambda e: e.get("dist", 0))[:3]
    for e in ents:
        a = e["actor"]
        comp = e["comp"]
        head = comp.get_socket_location("NPC-Head-_Head_")
        spine = comp.get_socket_location("NPC-Spine2-_Spn2_")
        vcam = unreal.UnrealEditorSubsystem().get_level_viewport_camera_info()[0]
        fwd = vcam - head
        fwd.z = 0
        n = math.hypot(fwd.x, fwd.y) or 1.0
        fwd = unreal.Vector(fwd.x / n, fwd.y / n, 0)
        dist = float(step[2]) if len(step) > 2 else 170.0
        tgt = (head + spine) * 0.5 if dist < 120 else spine + unreal.Vector(0, 0, -25)
        cam = tgt + fwd * dist + unreal.Vector(0, 0, 10)
        d = tgt - cam
        rot = unreal.Rotator(pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)), roll=0)
        rt = unreal.RenderingLibrary.create_render_target2d(world, 768, 1024, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
        cc = cap.capture_component2d
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", 45.0)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cc.set_editor_property("capture_every_frame", True)
        caps.append((cap, rt, a.get_actor_label()))
    live._npc_caps = caps
    print("setup", [c[2] for c in caps])
elif step[0] == "grab":
    for i, (cap, rt, name) in enumerate(live._npc_caps):
        unreal.RenderingLibrary.export_render_target(world, rt, out, "%s_%d.png" % (step[1], i))
    print("grab", [c[2] for c in live._npc_caps])
else:
    for cap, rt, name in live._npc_caps:
        cap.destroy_actor()
    live._npc_caps = []
    print("done")
