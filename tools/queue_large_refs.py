"""Queue the models of a worldspace's large references (walls, towers, castles) with the asset service ahead of time.
Usage: python -I queue_large_refs.py [worldspace edid, default whiterunworld]"""
import json, os, struct, sys, zlib

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
AREA = os.path.join(ROOT, "area2")
ESM = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\Skyrim.esm"
WS = (sys.argv[1] if len(sys.argv) > 1 else "whiterunworld").lower()
data = open(ESM, "rb").read()
large, base_of, model_of = set(), {}, {}
state = {"world": None}


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


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
                edid = next((sd.split(b"\0")[0].decode().lower() for st, sd in fields if st == b"EDID"), "")
                if edid == WS:
                    for st, sd in fields:
                        if st == b"RNAM":
                            n, = struct.unpack_from("<I", sd, 4)
                            large.update(struct.unpack_from("<I", sd, 8 + i * 8)[0] for i in range(n))
            elif t == b"REFR":
                for st, sd in fields:
                    if st == b"NAME": base_of[fid], = struct.unpack("<I", sd[:4])
            else:
                for st, sd in fields:
                    if st == b"MODL": model_of[fid] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
        p += 24 + sz


walk(0, len(data))
models = sorted({model_of[base_of[r]] for r in large if r in base_of and base_of[r] in model_of})
models = [m if m.endswith(".nif") else m + ".nif" for m in models if " " not in m]
mp = os.path.join(AREA, "models.json")
mapping = json.load(open(mp)) if os.path.exists(mp) else {}
have = set(open(os.path.join(AREA, "ready.txt")).read().split()) | set(open(os.path.join(AREA, "failed.txt")).read().split())
new = []
for m in models:
    name = m[:-4].replace("/", "_")
    mapping[name] = m
    if name not in have: new.append(name)
json.dump(mapping, open(mp, "w"))
with open(os.path.join(AREA, "requests.txt"), "a") as f:
    f.write("".join(n + "\n" for n in new))
print("%d large refs, %d models, %d newly queued" % (len(large), len(models), len(new)))
for n in new: print("  " + n)
