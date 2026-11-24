"""Which streamed actors are moving, and how far are their limb bones from the skeleton's rest pose? (rest pose = T/A pose of skeleton.nif)
Run while Skyrim is in the world: python tools/walk_check.py"""
import ctypes, ctypes.wintypes as wt, json, math, os, struct, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "unreal", "SkyBridge"))
import types
sys.modules.setdefault("unreal", types.ModuleType("unreal"))              # npc_live imports unreal at the top; only its stream/matrix helpers are used here
import npc_live as nl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rest = {s: {b["name"]: (b["rot"], b["pos"]) for b in json.load(open(os.path.join(ROOT, "area2", "npc", "skin", "skeleton_%s.json" % s)))} for s in ("male", "female")}


def snap():
    return {a["id"]: a for a in (nl.read_actors() or [])}


def limb_angles(a):
    sex = "female" if a["flags"] & 4 else "male"
    root = a["bones"].get("NPC")
    if not root:
        return None
    Rr = nl.quat_to_mat(*root[1]); RrT = nl.tr(Rr)
    out = {}
    for raw in ("NPC L UpperArm [LUar]", "NPC R UpperArm [RUar]", "NPC L Forearm [LLar]", "NPC L Thigh [LThg]", "NPC R Thigh [RThg]", "NPC L Calf [LClf]"):
        if raw in a["bones"] and raw in rest[sex]:
            Ri = nl.quat_to_mat(*a["bones"][raw][1])
            rel = nl.mul(nl.mul(RrT, Ri), nl.tr(rest[sex][raw][0]))
            out[raw.split(" [")[0][4:]] = round(math.degrees(math.acos(max(-1, min(1, (rel[0] + rel[4] + rel[8] - 1) / 2)))), 1)
    return out


def camera():
    k = ctypes.windll.kernel32
    k.OpenFileMappingW.restype = ctypes.c_void_p; k.MapViewOfFile.restype = ctypes.c_void_p
    k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
    p = k.MapViewOfFile(k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1"), 4, 0, 0, 0)
    f = struct.unpack("<3f9f", ctypes.string_at(p + 40, 48))
    return f[0:3], (f[4], f[7], f[10])          # camPos, forward = column 1 of the camera rotation (Skyrim axes)



