import sys, math
nl = sys.modules["npc_live"]
world = unreal.EditorLevelLibrary.get_editor_world()
step = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\npc_step.txt").read().split()
if step[0] == "setup":
    caps = []
    ents = [e for e in nl._state["actors"].values() if any(n in e["actor"].get_actor_label() for n in step[1].split(","))][:3]
    for e in ents:
        a = e["actor"]
        p = a.get_actor_location()
        b = e["comp"].bounds if hasattr(e["comp"], "bounds") else None
        tgt = p + unreal.Vector(0, 0, 100)
        cam = tgt + unreal.Vector(float(step[2]), 0, 30)
        d = tgt - cam
        rot = unreal.Rotator(pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)), roll=0)
        rt = unreal.RenderingLibrary.create_render_target2d(world, 768, 1024, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
        cc = cap.capture_component2d
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", 50.0)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cc.set_editor_property("capture_every_frame", True)
        caps.append((cap, rt, a.get_actor_label()))
        c = e["comp"]
        print(a.get_actor_label(), "loc", p, "head", c.get_socket_location("NPC-Head-_Head_"), "visible", c.is_visible(), "hidden", a.is_hidden_ed())
    live._npc_caps = caps
elif step[0] == "grab":
    for i, (cap, rt, name) in enumerate(live._npc_caps):
        unreal.RenderingLibrary.export_render_target(world, rt, r"C:\Users\Aidan\SkyrimUnrealBridge\area2", "%s_%d.png" % (step[1], i))
    print("grab")
else:
    for cap, rt, name in live._npc_caps:
        cap.destroy_actor()
    live._npc_caps = []
    print("done")
