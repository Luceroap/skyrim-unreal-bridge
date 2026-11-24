src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
for name in ("city_world", "city_keep", "load_interiors", "interior_key", "prefetch_cities", "prefetch_step", "request",
             "import_ready", "spawn_some", "city_some", "apply_world", "set_interior", "update_sky"):
    setattr(type(live), name, ns["Live"].__dict__[name])
live.prefetch_cities()
print("interiors", len(live.interiors), "prefetch todo", len(live.prefetch_todo), "interior now", getattr(live, "_interior", None))
