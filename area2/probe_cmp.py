import sys, math
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Carlotta" in e["actor"].get_actor_label())
c = e["comp"]
cap = {}
orig = unreal.SkyBridgeViewLibrary.apply_pose


class Fake:
    @staticmethod
    def apply_pose(comp, names, tfs):
        cap["n"], cap["t"] = names, tfs
        return len(names)


real = unreal.SkyBridgeViewLibrary
unreal.SkyBridgeViewLibrary = Fake
try:
    s = e["shown"]
    nl._orig_apply(e, s["pose"], s["sex"], False)
finally:
    unreal.SkyBridgeViewLibrary = real
cs = {}
for i in range(c.get_num_bones()):
    n = str(c.get_bone_name(i))
    p = str(c.get_parent_bone(n))
    l = c.get_ref_pose_transform(i)
    cs[n] = l if p not in cs else unreal.MathLibrary.compose_transforms(l, cs[p])
print("bones sent", len(cap.get("n", [])))
for n, t in list(zip(cap["n"], cap["t"]))[:12] + [(n, t) for n, t in zip(cap["n"], cap["t"]) if "Hand" in n or "Head" in n][:4]:
    r = cs[n]
    q1, q0 = t.rotation, r.rotation
    dot = abs(q1.x * q0.x + q1.y * q0.y + q1.z * q0.z + q1.w * q0.w)
    print("%-26s dpos %.1f  drot %.1f deg  scale %s  |q| %.3f" % (n, (t.translation - r.translation).length(), math.degrees(2 * math.acos(min(1, dot))),
          (round(t.scale3d.x, 1), round(t.scale3d.y, 1), round(t.scale3d.z, 1)), math.sqrt(q1.x**2 + q1.y**2 + q1.z**2 + q1.w**2)))
