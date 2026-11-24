import sys, importlib
nl = sys.modules["npc_live"]
old = nl._state
importlib.reload(nl)
nl._state = old                      # keep spawned NPCs, meshes, rest poses
print("npc_live reloaded, state kept:", len(old["actors"]), "actors; has _walk_record:", hasattr(nl, "_walk_record"))
