import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if e.get("plan"))
print(len(e["plan"]), "bones in plan;", sum(1 for p in e["plan"] if p[4]), "minor")
print(sorted(p[0] for p in e["plan"]))
