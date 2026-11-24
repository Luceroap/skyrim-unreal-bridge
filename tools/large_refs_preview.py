"""Export a worldspace's large references (city walls, towers, castle) from Skyrim.esm for a preview spawn in Unreal, until the
updated plugin streams them live. Output: area2/large_preview.json [{id, model, pos, rot(3x3 row-major), scale}]
Usage: python -I large_refs_preview.py [worldspace edid]"""
import json, math, os, struct, sys, zlib

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
ESM = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\Skyrim.esm"
WS = (sys.argv[1] if len(sys.argv) > 1 else "whiterunworld").lower()
data = open(ESM, "rb").read()
large, refs, model_of = set(), {}, {}


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def rot_from_angles(rx, ry, rz):
    """Same as RotFromAngles in plugin/src/main.cpp."""
    ax, ay, az = -rx, -ry, -rz
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    X = [1, 0, 0, 0, cx, -sx, 0, sx, cx]; Y = [cy, 0, sy, 0, 1, 0, -sy, 0, cy]; Z = [cz, -sz, 0, sz, cz, 0, 0, 0, 1]
    mul = lambda A, B: [sum(A[i * 3 + k] * B[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
    return mul(mul(X, Y), Z)


def walk(s, e):
    p = s
    while p < e:
        t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
        if t == b"GRUP":
            walk(p + 24, p + sz); p += sz; continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        if t in (b"WRLD", b"REFR", b"STAT", b"MSTT", b"ACTI", b"DOOR"):
            body = data[p + 24:p + 24 + sz]
            if flags & 0x40000: body = zlib.decompress(body[4:])
            fields = list(subs(body))
            if t == b"WRLD":
                if next((sd.split(b"\0")[0].decode().lower() for st, sd in fields if st == b"EDID"), "") == WS:
                    for st, sd in fields:
                        if st == b"RNAM":
                            n, = struct.unpack_from("<I", sd, 4)
                            large.update(struct.unpack_from("<I", sd, 8 + i * 8)[0] for i in range(n))
            elif t == b"REFR" and not flags & 0x820:                     # skip deleted / initially disabled
                r = {"scale": 1.0}
                for st, sd in fields:
                    if st == b"NAME": r["base"], = struct.unpack("<I", sd[:4])
                    elif st == b"DATA" and len(sd) >= 24: r["data"] = struct.unpack("<6f", sd[:24])
                    elif st == b"XSCL": r["scale"], = struct.unpack("<f", sd[:4])
                refs[fid] = r
            else:
                for st, sd in fields:
                    if st == b"MODL": model_of[fid] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
        p += 24 + sz


walk(0, len(data))
out = []
for fid in sorted(large):
    r = refs.get(fid)
    if not r or "data" not in r or r.get("base") not in model_of: continue
    m = model_of[r["base"]]
    if "marker" in m or m.startswith("effects/") or " " in m: continue
    d = r["data"]
    out.append({"id": fid, "model": m[:-4].replace("/", "_") if m.endswith(".nif") else m,
                "pos": d[:3], "rot": rot_from_angles(*d[3:]), "scale": r["scale"]})
json.dump(out, open(os.path.join(ROOT, "area2", "large_preview.json"), "w"))
print("%d large refs exported" % len(out))
