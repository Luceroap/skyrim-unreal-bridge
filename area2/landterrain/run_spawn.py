import sys, importlib
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import land_terrain_live as L
importlib.reload(L)
print("pending", L.spawn(live, max_new=4))
for n, a in L.STATE["actors"].items():
    m = a.static_mesh_component.static_mesh
    print(n, m.get_editor_property("nanite_settings").enabled, m.get_num_uv_channels(0), m.get_num_vertices(0),
          a.get_actor_bounds(False))
