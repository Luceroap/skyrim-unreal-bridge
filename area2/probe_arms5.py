import sys, time
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
print([m for m in dir(c) if any(k in m.lower() for k in ("refresh", "update", "tick", "dirty", "pose", "lod"))])
print("tick enabled", c.is_component_tick_enabled(), "pred lod", c.get_editor_property("forced_lod_model") if hasattr(c, "get_editor_property") else None)
