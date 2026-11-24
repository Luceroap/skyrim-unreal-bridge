import importlib, sys
rm = importlib.reload(sys.modules["remaster_materials"])
nm = rm.night_sky_material(rebuild=True)
src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
for name in ("update_sky", "set_interior", "weather_setup", "spawn_some"):
    setattr(type(live), name, ns["Live"].__dict__[name])
old = getattr(live, "sky_dome", None)
if old:
    old.destroy_actor()
a = live.spawn(unreal.StaticMeshActor)
c = a.static_mesh_component
c.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere"))
c.set_mobility(unreal.ComponentMobility.MOVABLE)
c.set_cast_shadow(False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
c.set_editor_property("affect_distance_field_lighting", False)
a.set_actor_scale3d(V(2.0e6, 2.0e6, 2.0e6))
live.night_mid = c.create_dynamic_material_instance(0, nm)
a.set_actor_label("NightSky"); a.set_folder_path("SkyBridge/Weather")
live.sky_dome = a
live._dome_x = 1e12
live._sky_key = None
print("night sky ready", nm, live.night_mid)
