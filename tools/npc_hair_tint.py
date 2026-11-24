"""Hair colours of the converted NPCs. Skyrim draws hair/brow textures in grey and multiplies them by the NPC's hair colour,
which the FaceGen head NIF stores as the 'Hair Tint Color' of BSLightingShaderProperty shader type 6 (HairTint).
Writes area2/npc/hair_tint.json: {face form id (8 hex): {texture path (lower case): [r, g, b]}}.
  python npc_hair_tint.py [--dump <face.nif>]"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nif2obj import R, parse, avobject

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
NPC = os.path.join(ROOT, "area2", "npc")
HAIR_TINT = 6


def shader_info(data, blocks, ref):
    """(shader type, texture-set diffuse path, hair tint or None) of a BSLightingShaderProperty (Skyrim SE layout)."""
    if ref < 0 or "Lighting" not in blocks[ref][0]:
        return None
    r = R(data, blocks[ref][1])
    stype = r.u32()
    r.i32(); k = r.u32(); [r.i32() for _ in range(k)]; r.i32()        # name, extra data, controller
    r.u32(); r.u32(); r.f(4)                                          # flags 1/2, uv offset + scale
    ts = r.i32()
    r.f(3); r.f(1); r.u32()                                           # emissive colour, multiple, clamp mode
    r.f(1); r.f(1); r.f(1)                                            # alpha, refraction, glossiness
    r.f(3); r.f(1); r.f(1); r.f(1)                                    # specular colour, strength, lighting effects 1/2
    tint = list(r.f(3)) if stype == HAIR_TINT else None
    tex = None
    if ts >= 0:
        rr = R(data, blocks[ts][1])
        if rr.u32():
            tex = rr.lstr()
    return stype, tex, tint


def tints(path):
    data, blocks, strings, bsver = parse(open(path, "rb").read())
    out = {}
    for typ, pos, size in blocks:
        if typ not in ("BSTriShape", "BSDynamicTriShape"):
            continue
        r = R(data, pos)
        avobject(r)
        r.f(4); r.i32(); shader = r.i32()
        info = shader_info(data, blocks, shader)
        if info and info[2] and info[1]:
            t = info[1].strip().lower().replace("/", "\\")
            i = t.find("textures\\")
            out[t[i:] if i > 0 else t] = [round(max(0.0, min(1.0, c)), 4) for c in info[2]]
    return out


if __name__ == "__main__":
    if "--dump" in sys.argv:
        print(json.dumps(tints(sys.argv[sys.argv.index("--dump") + 1]), indent=1))
        sys.exit()
    res = {}
    for f in glob.glob(os.path.join(NPC, "nif", "actors", "character", "facegendata", "facegeom", "*", "*.nif")):
        try:
            t = tints(f)
        except Exception as e:
            print("FAILED", f, e)
            continue
        if t:
            res[os.path.basename(f)[:-4].lower().zfill(8)] = t
    json.dump(res, open(os.path.join(NPC, "hair_tint.json"), "w"), indent=1, sort_keys=True)
    print(len(res), "faces with hair tint")
