eal = unreal.EditorAssetLibrary
print("MPC_RainOcc exists", eal.does_asset_exist("/Game/Area2Tex/MPC_RainOcc"))
print("live.rain_occ", getattr(live, "rain_occ", "missing"))
print("patched methods", hasattr(type(live), "rain_occ_spawn"))
print("other agent state", "_rain_occ" in live.__dict__)
labels = [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.SceneCapture2D)]
print("captures", labels)
m = unreal.load_asset("/Game/Area2Tex/M_RainDrops")
print("vector params", [str(n) for n in unreal.MaterialEditingLibrary.get_vector_parameter_names(m)])
descs = [e.get_editor_property("description") for e in unreal.MaterialEditingLibrary.get_material_expressions(m) if isinstance(e, unreal.MaterialExpressionCustom)] if hasattr(unreal.MaterialEditingLibrary, "get_material_expressions") else "n/a"
print("custom nodes", descs)
