"""Minimal Skyrim SE NIF (20.2.0.7, BS stream 100) geometry extractor -> Wavefront OBJ (+ MTL with diffuse texture names).
Handles NiNode hierarchy transforms and BSTriShape (and subclasses). Skinned/animated data is ignored.
Usage: python -I nif2obj.py in.nif out.obj
"""
import struct, sys, os, io


class R:
    def __init__(self, b, p=0): self.b, self.p = b, p
    def u8(self): v = self.b[self.p]; self.p += 1; return v
    def u16(self): v, = struct.unpack_from("<H", self.b, self.p); self.p += 2; return v
    def u32(self): v, = struct.unpack_from("<I", self.b, self.p); self.p += 4; return v
    def i32(self): v, = struct.unpack_from("<i", self.b, self.p); self.p += 4; return v
    def u64(self): v, = struct.unpack_from("<Q", self.b, self.p); self.p += 8; return v
    def f(self, n=1):
        v = struct.unpack_from("<%df" % n, self.b, self.p); self.p += 4 * n
        return v[0] if n == 1 else v
    def sstr(self): n = self.u8(); s = self.b[self.p:self.p + n]; self.p += n; return s
    def lstr(self): n = self.u32(); s = self.b[self.p:self.p + n]; self.p += n; return s.decode("latin1")


def half(h):
    return struct.unpack("<e", struct.pack("<H", h))[0]


def parse(data):
    r = R(data)
    nl = data.index(b"\n")
    r.p = nl + 1
    ver = r.u32(); r.u8(); user = r.u32(); nblocks = r.u32(); bsver = r.u32()
    assert ver == 0x14020007 and bsver >= 83, (hex(ver), bsver)
    r.sstr(); r.sstr(); r.sstr()  # author, process script, export script
    ntypes = r.u16()
    types = [r.lstr() for _ in range(ntypes)]
    tidx = [r.u16() for _ in range(nblocks)]
    sizes = [r.u32() for _ in range(nblocks)]
    nstr = r.u32(); r.u32()
    strings = [r.lstr() for _ in range(nstr)]
    ngroups = r.u32(); [r.u32() for _ in range(ngroups)]
    blocks, pos = [], r.p
    for i in range(nblocks):
        blocks.append((types[tidx[i]], pos, sizes[i])); pos += sizes[i]
    return data, blocks, strings, bsver


def avobject(r):
    name = r.i32(); n = r.u32(); [r.i32() for _ in range(n)]; r.i32()  # NiObjectNET
    r.u32()  # flags
    t = r.f(3); rot = r.f(9); s = r.f(); r.i32()  # collision
    return name, t, rot, s


def mat_mul(parent, t, rot, s):
    """parent: (R(9), t(3), s). returns composed (R, t, s)."""
    pr, pt, ps = parent
    R9 = [sum(pr[i * 3 + k] * rot[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
    tt = tuple(ps * sum(pr[i * 3 + k] * t[k] for k in range(3)) + pt[i] for i in range(3))
    return (R9, tt, ps * s)


def xform(m, v):
    r, t, s = m
    return tuple(s * sum(r[i * 3 + k] * v[k] for k in range(3)) + t[i] for i in range(3))


def _skinned_as_static(path):
    """Fallback for models whose shapes are all skinned (the normal reader skips those). Uses npc_skin's skinned reader with creature mode
    (vertices stay in shape space, no skeleton needed) and returns the same (name, verts, uvs, tris, texture) tuples."""
    try:
        import io, contextlib, npc_skin
        npc_skin.CREATURE = False                       # shape space -> the model's own node space: offset from the bones' bind vs rest positions
        npc_skin.SKEL.clear()
        npc_skin.SKEL.update({b["name"]: b["pos"] for b in npc_skin.skeleton(path)})
        with contextlib.redirect_stdout(io.StringIO()):
            sk = npc_skin.meshes(path)
        return [(s["name"], [tuple(v) for v in s["verts"]], [tuple(u) for u in s["uvs"]], [tuple(t) for t in s["tris"]], s["texture"]) for s in sk if s["tris"]]
    except Exception:
        return []


def extract(path):
    data, blocks, strings, bsver = parse(open(path, "rb").read())
    shapes = []  # (name, verts, uvs, tris, texture)

    def tex_of(shader_ref):
        if shader_ref < 0: return None
        typ, pos, size = blocks[shader_ref]
        if "ShaderProperty" not in typ or "Lighting" not in typ: return None
        r = R(data, pos)
        r.u32()  # Skyrim shader type (precedes NiObjectNET in BSLightingShaderProperty)
        n = r.i32(); k = r.u32(); [r.i32() for _ in range(k)]; r.i32()
        r.u32(); r.u32(); r.f(4)
        ts = r.i32()
        if ts < 0: return None
        t2, p2, _ = blocks[ts]
        rr = R(data, p2); cnt = rr.u32()
        return rr.lstr() if cnt else None

    def visit(idx, parent):
        typ, pos, size = blocks[idx]
        r = R(data, pos)
        if typ in ("NiNode", "BSFadeNode", "BSLeafAnimNode", "BSMultiBoundNode", "BSOrderedNode", "BSValueNode", "BSBlastNode", "BSDamageStage", "BSMasterParticleSystem") or typ.endswith("Node"):
            name, t, rot, s = avobject(r)
            # Skyrim replaces the root node's own transform with the object's placement, so the root's local transform
            # in the NIF (rotated by 90/180 deg in ~19 of our models: benches, bridge, signs...) must be ignored.
            m = parent if idx == 0 else mat_mul(parent, t, rot, s)
            n = r.u32()
            for c in [r.i32() for _ in range(n)]:
                if c >= 0: visit(c, m)
        elif typ == "NiTriShape":
            # Older-format geometry (many LE-converted / mod meshes): NiTriShape + NiTriShapeData blocks.
            name, t, rot, s = avobject(r)
            m = mat_mul(parent, t, rot, s)
            dref = r.i32(); skin = r.i32()
            nmat = r.u32(); [r.i32() for _ in range(nmat)]; [r.i32() for _ in range(nmat)]; r.i32(); r.u8()
            shader = r.i32(); alpha = r.i32()
            if dref < 0 or skin >= 0:
                return
            d = R(data, blocks[dref][1])
            d.i32(); nv = d.u16(); d.u8(); d.u8(); hasv = d.u8()
            if not hasv or nv == 0:
                return
            pts = [d.f(3) for _ in range(nv)]
            dflags = d.u16()
            d.u32()                                      # material CRC (present for Bethesda streams)
            if d.u8():                                   # has normals
                d.p += nv * 12
                if dflags & 0x1000: d.p += nv * 24      # tangents + bitangents
            d.p += 16                                    # bounding centre + radius
            if d.u8(): d.p += nv * 16                    # vertex colours
            uv = [d.f(2) for _ in range(nv)] if (dflags & 1) else [(0.0, 0.0)] * nv
            d.u16(); d.i32()                             # consistency flags, additional data
            ntri = d.u16(); d.u32()
            tris = []
            if d.u8():
                tris = [struct.unpack_from("<3H", data, d.p + i * 6) for i in range(ntri)]
            nm = strings[name] if 0 <= name < len(strings) else "shape%d" % idx
            shapes.append((nm, [xform(m, p_) for p_ in pts], [(u, 1.0 - v) for u, v in uv], tris, tex_of(shader)))
        elif "TriShape" in typ and "Dynamic" not in typ:
            name, t, rot, s = avobject(r)
            m = mat_mul(parent, t, rot, s)
            r.f(4); skin = r.i32(); shader = r.i32(); alpha = r.i32()
            desc = r.u64()
            # num triangles: u32 on newer versions; detect by consistency
            save = r.p
            stride = (desc & 0xF) * 4
            ok = False
            for tri_u32 in (False, True):
                r.p = save
                ntri = r.u32() if tri_u32 else r.u16()
                nvert = r.u16(); dsize = r.u32()
                if dsize == nvert * stride + ntri * 6:
                    ok = True; break
            if not ok or dsize == 0 or skin >= 0:
                return
            voff = ((desc >> 4) & 0xF) * 4
            uvoff = ((desc >> 8) & 0xF) * 4
            has_uv = bool(desc & (1 << 45))
            verts, uvs = [], []
            for i in range(nvert):
                base = r.p + i * stride
                x, y, z = struct.unpack_from("<3f", data, base + voff)
                verts.append(xform(m, (x, y, z)))
                if has_uv:
                    u, v = struct.unpack_from("<2e", data, base + uvoff)
                    uvs.append((u, 1.0 - v))
                else:
                    uvs.append((0.0, 0.0))
            r.p += nvert * stride
            tris = [struct.unpack_from("<3H", data, r.p + i * 6) for i in range(ntri)]
            nm = strings[name] if 0 <= name < len(strings) else "shape%d" % idx
            shapes.append((nm, verts, uvs, tris, tex_of(shader)))

    # roots: block 0 normally
    ident = ([1, 0, 0, 0, 1, 0, 0, 0, 1], (0.0, 0.0, 0.0), 1.0)
    visit(0, ident)
    if not shapes:                         # banners, flags, hanging animals, low-poly books: every shape is skinned -> show them in their bind pose
        shapes = _skinned_as_static(path)
    return shapes


def write_obj(shapes, obj_path, mtl_name=None):
    base = os.path.splitext(os.path.basename(obj_path))[0]
    mtl_path = os.path.splitext(obj_path)[0] + ".mtl"
    off = 1
    mats = {}
    with open(obj_path, "w") as f, open(mtl_path, "w") as m:
        f.write("mtllib %s.mtl\n" % base)
        for name, verts, uvs, tris, tex in shapes:
            mat = (tex or "none").replace("\\", "_").replace("/", "_").replace(".", "_")
            if mat not in mats:
                mats[mat] = 1
                m.write("newmtl %s\nKd 0.8 0.8 0.8\n" % mat)
                if tex: m.write("# skyrim diffuse: %s\n" % tex)
            f.write("o %s\nusemtl %s\n" % (name or "shape", mat))
            for v in verts: f.write("v %.4f %.4f %.4f\n" % v)
            for u in uvs: f.write("vt %.5f %.5f\n" % u)
            for a, b, c in tris:
                f.write("f %d/%d %d/%d %d/%d\n" % (a + off, a + off, b + off, b + off, c + off, c + off))
            off += len(verts)


if __name__ == "__main__":
    shapes = extract(sys.argv[1])
    write_obj(shapes, sys.argv[2])
    print(sys.argv[1], "->", len(shapes), "shapes,", sum(len(s[1]) for s in shapes), "verts,", sum(len(s[3]) for s in shapes), "tris")
