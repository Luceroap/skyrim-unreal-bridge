import importlib, sys
old = sys.modules["npc_live"]
st, gear = old._state, old._gear
nl = importlib.reload(old)
for e in st["actors"].values():
    if e.get("ready") and "rest0q" not in e:
        e["rest0q"] = {k: (nl.mat_to_quat(R), t) for k, (R, t) in e["rest0"].items()}
st.setdefault("seq", None)
nl._state.clear(); nl._state.update(st)
nl._gear.clear(); nl._gear.update(gear)
print("npc_live swapped; npcs kept:", len(nl._state["actors"]))
