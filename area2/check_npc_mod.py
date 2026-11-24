import sys
nl = sys.modules["npc_live"]
print("live module: _ref_scales", hasattr(nl, "_ref_scales"), "_walk_pose", hasattr(nl, "_walk_pose"),
      "actors", len(nl._state["actors"]), "walk loops", {k: round(w["loop"]["dur"], 2) for k, w in nl._state.get("walk", {}).items() if w.get("loop")})
