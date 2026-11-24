import time, sys
nl = sys.modules["npc_live"]
st = nl._state
e = next(iter(st["actors"].values()))
comp = e["comp"]
names = [n for n in e["rest0"]][:80]
tf = unreal.Transform()
t0 = time.perf_counter()
for n in names:
    tf0 = comp.get_bone_transform_by_name(n, unreal.BoneSpaces.COMPONENT_SPACE)
t_get = time.perf_counter() - t0
t0 = time.perf_counter()
for n in names:
    comp.set_bone_transform_by_name(n, tf0, unreal.BoneSpaces.COMPONENT_SPACE)
t_set = time.perf_counter() - t0
print("bones", len(e["rest0"]), "80 sets %.2f ms, 80 gets %.2f ms" % (t_set * 1000, t_get * 1000))
for i in range(min(5, len(names))):
    print(names[i])
print("in rest json?", sum(1 for n in nl.rest_pose("male")), "streamed bones per actor ~", len(nl.read_actors()[1]["bones"]))
