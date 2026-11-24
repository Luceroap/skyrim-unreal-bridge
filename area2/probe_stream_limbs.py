"""Outside Unreal: sample the actor stream for a few seconds and show, per NPC, whether limbs move and whether npc_live._is_bind flags it.
python area2/probe_stream_limbs.py [seconds]"""
import math, sys, time, types
sys.modules["unreal"] = types.SimpleNamespace(log=print)
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live as nl

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
LA = "NPC L UpperArm [LUar]"; LH = "NPC L Hand [LHnd]"; LC = "NPC L Calf [LClf]"
hist = {}
t0 = time.time(); seqs = set()
while time.time() - t0 < dur:
    acts = nl.read_actors()
    if acts:
        seqs.add(nl._state.get("seq"))
        for a in acts:
            b = a["bones"]
            if "NPC" not in b:
                continue
            rest = nl.rest_pose(nl.skel_key(a))
            rq = b["NPC"][1]
            rel = {k: nl.qmul(nl.qconj(rq), b[k][1]) for k in (LA, LH, LC) if k in b}
            hand = None
            if LH in b:
                hand = nl.qrot(nl.qconj(rq), [b[LH][0][i] - b["NPC"][0][i] for i in range(3)])
            hist.setdefault((a["id"], a["name"]), []).append((nl._is_bind(b, rest, rq), rel, hand, a["pos"]))
    time.sleep(0.05)
print("seq values seen:", len(seqs))
import ctypes, struct
h = nl.k32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1")
pp = nl.k32.MapViewOfFile(h, 4, 0, 0, 0)
v = struct.unpack("<4I21f", ctypes.string_at(pp, 100))
cam, rot = v[10:13], v[13:22]
fwd = (rot[1], rot[4], rot[7])
def view_angle(p):
    d = [p[i] - cam[i] for i in range(3)]; n = math.sqrt(sum(c * c for c in d)) or 1
    return math.degrees(math.acos(max(-1, min(1, sum(d[i] * fwd[i] for i in range(3)) / n))))
for (aid, nm), h in hist.items():
    binds = sum(1 for x in h if x[0])
    def ang(q1, q2):
        w = abs(sum(q1[i] * q2[i] for i in range(4)))
        return math.degrees(2 * math.acos(min(1.0, w)))
    arm = max((ang(h[0][1][LA], x[1][LA]) for x in h if LA in x[1] and LA in h[0][1]), default=-1)
    calf = max((ang(h[0][1][LC], x[1][LC]) for x in h if LC in x[1] and LC in h[0][1]), default=-1)
    hd = h[-1][2]
    mv = math.dist(h[0][3], h[-1][3])
    print("%08x %-22s n%3d bind %3d  armChange %5.1f  calfChange %5.1f  moved %6.1f  dist %5.0f viewAngle %5.1f" % (
        aid, nm[:22], len(h), binds, arm, calf, mv, math.dist(h[-1][3], cam), view_angle(h[-1][3])))
