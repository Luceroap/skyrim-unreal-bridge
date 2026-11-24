src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
setattr(type(live), "load_interiors", ns["Live"].__dict__["load_interiors"])
for k in ("interiors", "interior_of"):
    live.__dict__.pop(k, None)
live.prefetch_cities()
print("interior cells", len(live.interiors), "refs", len(live.interior_of), "prefetch todo", len(live.prefetch_todo))
