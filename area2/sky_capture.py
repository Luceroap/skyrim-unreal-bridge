step = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\sky_step.txt").read().split()
world = unreal.EditorLevelLibrary.get_editor_world()
out = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
if step[0] == "setup":
    live._night_saved = live.night_mid
    live.night_mid = None                       # update_sky leaves the dome alone during the test
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1024, 576, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, live.sky_dome.get_actor_location() + V(0, 0, 3000),
                                                          unreal.Rotator(pitch=40, yaw=float(step[1]) if len(step) > 1 else 0.0))
    cc = cap.capture_component2d
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("capture_every_frame", True)
    live._sky_cap = (cap, rt)
    print("setup")
elif step[0] == "set":
    m = live._night_saved
    m.set_scalar_parameter_value("Night", float(step[1])); m.set_scalar_parameter_value("Aurora", float(step[2]))
    m.set_scalar_parameter_value("Intensity", float(step[3]))
    print("set", step)
elif step[0] == "grab":
    cap, rt = live._sky_cap
    unreal.RenderingLibrary.export_render_target(world, rt, out, step[1] + ".png")
    print("grab", step[1])
else:
    cap, rt = live._sky_cap
    cap.destroy_actor()
    live.night_mid = live._night_saved
    live.night_mid.set_scalar_parameter_value("Intensity", 6.0)
    live._sky_key = None
    print("done")
