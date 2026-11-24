import math
loc, rot = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
f = rot.get_forward_vector(); r = rot.get_right_vector()
world = unreal.EditorLevelLibrary.get_editor_world()
for fwd, side in ((300, 150), (500, 300), (200, 0), (800, -300)):
    p = loc + f * fwd + r * side
    hit = unreal.SystemLibrary.line_trace_single(world, p + unreal.Vector(0, 0, 500), p - unreal.Vector(0, 0, 3000),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if not hit:
        print(fwd, side, "no hit"); continue
    t = hit.to_tuple()
    comp = next((x for x in t if isinstance(x, unreal.PrimitiveComponent)), None)
    act = comp.get_owner() if comp else None
    mats = []
    if comp and hasattr(comp, "get_num_materials"):
        for i in range(comp.get_num_materials()):
            m = comp.get_material(i); mats.append(m.get_name() if m else None)
    sm = comp.static_mesh.get_name() if comp and hasattr(comp, "static_mesh") and comp.static_mesh else "?"
    print(fwd, side, act.get_actor_label() if act else None, act.get_folder_path() if act else None, sm, mats[:6])
