import sys, math
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
W = c.get_world_transform()
CS = unreal.BoneSpaces.COMPONENT_SPACE
print("actor", e["actor"].get_actor_location(), "bounds", c.bounds.box_extent if hasattr(c, "bounds") else None)
bad = []
for i in range(c.get_num_bones()):
    n = c.get_bone_name(i)
    s = W.inverse_transform_location(c.get_socket_location(n))
    g = c.get_bone_transform_by_name(n, CS)
    d = math.dist((s.x, s.y, s.z), (g.translation.x, g.translation.y, g.translation.z))
    sc = g.scale3d
    if d > 1 or abs(sc.x - 1) > 0.05 or not (-300 < s.z < 300) or i < 4:
        bad.append((i, str(n), round(d, 1), (round(s.x, 1), round(s.y, 1), round(s.z, 1)), (round(sc.x, 2), round(sc.y, 2), round(sc.z, 2))))
print(len(bad), "odd bones")
for b in bad[:40]:
    print(b)
