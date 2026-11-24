src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
for name in ("city_world", "city_keep", "prefetch_cities", "prefetch_step", "request", "import_ready", "spawn_some",
             "city_some", "update_sky", "set_interior", "weather_setup", "distant_some"):
    setattr(type(live), name, ns["Live"].__dict__[name])
live._prefetched = True
live.prefetch_cities()
live.prefetch_step()
print("prefetch todo", len(live.prefetch_todo), "chunk", len(getattr(live, "_pf_chunk", [])))
