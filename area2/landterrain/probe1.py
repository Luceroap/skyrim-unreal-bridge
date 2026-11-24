import unreal
print("CustomOutput", hasattr(unreal, "CustomOutput"))
o = unreal.CustomOutput()
print([p for p in dir(o) if not p.startswith("_")][:20])
print("ensure", hasattr(unreal.SkyBridgeViewLibrary, "ensure_mesh_renderable"))
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if str(a.get_folder_path()) == "SkyBridge/Terrain" and isinstance(a, unreal.StaticMeshActor):
        m = a.static_mesh_component.static_mesh
        o, e = a.get_actor_bounds(False)
        print(a.get_name(), a.get_actor_label(), m.get_path_name() if m else None, a.get_actor_location(), a.get_actor_rotation(), o, e,
              a.static_mesh_component.is_visible(), m.get_editor_property("nanite_settings").enabled if m else None)
print("cam", unreal.EditorLevelLibrary.get_level_viewport_camera_info())
print("live", type(live).__name__, getattr(live, "_interior", None))
