import sys, math
nl = sys.modules["npc_live"]


def ang(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in v)) or 1
    return round(math.degrees(math.acos(max(-1, min(1, -v[2] / n)))), 1)


for e in nl._state["actors"].values():
    lab = e["actor"].get_actor_label()
    s = e.get("shown")
    if not s:
        continue
    bones, rq, rp = s["pose"]
    rest = nl.rest_pose(s["sex"])
    out = [lab[:22]]
    for side in "LR":
        ua, fa, hd = "NPC %s UpperArm [%sUar]" % (side, side), "NPC %s Forearm [%sLar]" % (side, side), "NPC %s Hand [%sHnd]" % (side, side)
        if ua in bones and fa in bones:
            sk = ang(bones[ua][0], bones[fa][0])
            r0 = ang(rest[ua][1], rest[fa][1]) if ua in rest else None
            c = e["comp"]
            u = c.get_socket_location(nl.ue_bone(ua)); f = c.get_socket_location(nl.ue_bone(fa))
            ue = ang((u.x, u.y, u.z), (f.x, f.y, f.z))
            out.append("%s: skyrim %s  unreal %s  rest %s" % (side, sk, ue, r0))
    out.append("bind=%s" % nl._is_bind(bones, rest, rq))
    print("  ".join(map(str, out)))
