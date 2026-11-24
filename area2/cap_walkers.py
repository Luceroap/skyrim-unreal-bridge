"""Close-up of up to 3 WALKING NPCs (side view), grabbed twice 0.5 s apart -> area2/walkers_<k>_<i>.png + walkers_report.txt."""
import sys, math, time
nl = sys.modules["npc_live"]
world = unreal.EditorLevelLibrary.get_editor_world()
OUT = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
ents = sorted([e for e in nl._state["actors"].values() if e["comp"].get_num_bones() > 100 and e.get("speed", 0) > 25],
              key=lambda e: e.get("dist", 0))[:3]
caps = []
for e in ents:
    comp = e["comp"]
    head = comp.get_socket_location("NPC-Head-_Head_"); face = comp.get_socket_location("NPCEyeBone")
    spine = comp.get_socket_location("NPC-Spine2-_Spn2_")
    f = face - head; n = math.hypot(f.x, f.y) or 1.0
    side = unreal.Vector(-f.y / n, f.x / n, 0)                      # look from the side: legs/arms swing visible
    tgt = spine + unreal.Vector(0, 0, -30)
    cam = tgt + side * 300 + unreal.Vector(0, 0, 10)
    d = tgt - cam
    rot = unreal.Rotator(pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)), roll=0)
    rt = unreal.RenderingLibrary.create_render_target2d(world, 640, 900, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cc = cap.capture_component2d
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("fov_angle", 45.0)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("capture_every_frame", True)
    cap.attach_to_actor(e["actor"], "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    caps.append((cap, rt, e))
st = dict(t0=time.time(), k=0, lines=[])
def _cb(dt):
    el = time.time() - st["t0"]
    if st["k"] < 2 and el > 1.0 + 0.5 * st["k"]:
        for i, (cap, rt, e) in enumerate(caps):
            unreal.RenderingLibrary.export_render_target(world, rt, OUT, "walkers_%d_%d.png" % (st["k"], i))
            c = e["comp"]; W = c.get_world_transform()
            h = W.inverse_transform_location(c.get_socket_location("NPC-L-Hand-_LHnd_"))
            ft = W.inverse_transform_location(c.get_socket_location("NPC-L-Foot-_Lft_"))
            st["lines"].append("grab %d %-26s frozen %s walkloop %s  Lhand %.0f,%.0f,%.0f  Lfoot %.0f,%.0f,%.0f" % (
                st["k"], e["actor"].get_actor_label()[:26], e.get("frozen"), e.get("wph") is not None, h.x, h.y, h.z, ft.x, ft.y, ft.z))
        st["k"] += 1
    if st["k"] >= 2:
        unreal.unregister_slate_post_tick_callback(st["h"])
        for cap, rt, e in caps:
            cap.destroy_actor()
        open(OUT + r"\walkers_report.txt", "w").write("\n".join(st["lines"]) + "\n")
st["h"] = unreal.register_slate_post_tick_callback(_cb)
print("walkers:", [e["actor"].get_actor_label() for c, r, e in caps])
