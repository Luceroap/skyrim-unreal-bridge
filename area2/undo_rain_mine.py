w = unreal.EditorLevelLibrary.get_editor_world()
mpc = unreal.load_asset("/Game/Area2Tex/MPC_RainOcc")
unreal.MaterialLibrary.set_vector_parameter_value(w, mpc, "Occ", unreal.LinearColor(0, 0, 0, 0))
a = getattr(live, "rain_occ", None)
if a is not None:
    a.destroy_actor()
live.rain_occ = None
labels = [x.get_actor_label() for x in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(x, unreal.SceneCapture2D)]
print("captures left", labels)
