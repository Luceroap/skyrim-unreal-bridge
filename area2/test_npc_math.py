"""Offline check: new folded pose math in npc_live == the original per-bone matrix math (area2/_pose_old.txt)."""
import math, random, sys, types

class V:
    def __init__(s, x=0, y=0, z=0): s.x, s.y, s.z = x, y, z
class Q:
    def __init__(s, x=0, y=0, z=0, w=1): s.x, s.y, s.z, s.w = x, y, z, w
class T:
    def __init__(s): s.translation = V(); s.rotation = Q()
class Comp:
    def __init__(s): s.out = {}
    def set_bone_transform_by_name(s, n, tf, space):
        t, r = tf.translation, tf.rotation
        s.out[n] = ((t.x, t.y, t.z), (r.x, r.y, r.z, r.w))
class Actor:
    def set_actor_location_and_rotation(s, *a): pass
stub = types.SimpleNamespace(Transform=T, Vector=V, Quat=Q, BoneSpaces=types.SimpleNamespace(COMPONENT_SPACE=0), log=print)
sys.modules["unreal"] = stub
src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\npc_live.py", encoding="utf-8").read()
ns = {"__name__": "npc_test"}
exec(src, ns)
exec(open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\_pose_old.txt", encoding="utf-8").read(), ns)

def rq():
    q = [random.gauss(0, 1) for _ in range(4)]; n = math.sqrt(sum(c * c for c in q)); return tuple(c / n for c in q)
random.seed(3)
names = ["NPC", "NPC Pelvis [Pelv]", "NPC L Thigh [LThg]", "NPC R Hand [RHnd]", "NPC Head [Head]", "NPC L Finger00 [LF00]"]
rest = {n: (ns["quat_to_mat"](*rq()), [random.uniform(-50, 50) for _ in range(3)]) for n in names}
ns["_state"]["rest"]["male"] = rest
ue = {ns["ue_bone"](n): (ns["quat_to_mat"](*rq()), tuple(random.uniform(-80, 80) for _ in range(3))) for n in names}
def entry():
    e = dict(actor=Actor(), comp=Comp(), ready=True, names=set(ue), rest0=ue,
             rest0q={k: (ns["mat_to_quat"](R), t) for k, (R, t) in ue.items()})
    return e
lb = types.SimpleNamespace(ue_rotation=lambda R: None)
worst = 0.0
for trial in range(20):
    bones = {n: (tuple(random.uniform(-1e4, 1e4) for _ in range(3)), rq()) for n in names}
    a = dict(bones=bones, flags=0)
    e1 = entry(); ns["_pose"](e1, a, "male", lb)
    e2 = entry(); root = bones["NPC"]
    ns["_apply_pose"](e2, (bones, root[1], root[0]), "male", False)
    for n, (p1, q1) in e1["comp"].out.items():
        p2, q2 = e2["comp"].out[n]
        dq = abs(abs(sum(x * y for x, y in zip(q1, q2))) - 1.0)
        worst = max(worst, max(abs(x - y) for x, y in zip(p1, p2)), dq)
print("bones compared per trial:", len(e1["comp"].out), "worst difference:", worst)
# _is_bind: quaternion angle == old matrix angle
names_l = list(ns["LIMBS"])
rest_l = {n: (ns["quat_to_mat"](*rq()), [0, 0, 0]) for n in names_l}
worst_a = 0.0
for trial in range(200):
    root = rq(); b = {n: ((0, 0, 0), rq()) for n in names_l}
    RrT = ns["tr"](ns["quat_to_mat"](*root))
    for n in names_l:
        rel = ns["mul"](ns["mul"](RrT, ns["quat_to_mat"](*b[n][1])), ns["tr"](rest_l[n][0]))
        a_old = math.degrees(math.acos(max(-1.0, min(1.0, (rel[0] + rel[4] + rel[8] - 1.0) / 2.0))))
        w = ns["qmul"](ns["qmul"](ns["qconj"](root), b[n][1]), ns["qconj"](ns["mat_to_quat"](rest_l[n][0])))[3]
        worst_a = max(worst_a, abs(a_old - math.degrees(2 * math.acos(min(1.0, abs(w))))))
print("bind-check angle worst difference (deg):", worst_a)
import time
e2 = entry(); bones = {n: (tuple(random.uniform(-1e4, 1e4) for _ in range(3)), rq()) for n in names}
t0 = time.perf_counter()
for _ in range(2000): ns["_apply_pose"](e2, (bones, bones["NPC"][1], bones["NPC"][0]), "male", False)
t_new = (time.perf_counter() - t0) / 2000 / len(names)
e1 = entry(); t0 = time.perf_counter()
for _ in range(2000): ns["_pose"](e1, dict(bones=bones, flags=0), "male", lb)
t_old = (time.perf_counter() - t0) / 2000 / len(names)
print("per bone: old %.1f us, new %.1f us" % (t_old * 1e6, t_new * 1e6))
