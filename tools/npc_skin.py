"""Skinned NIF + skeleton extractor for NPC rendering in Unreal.
  python -I npc_skin.py skeleton <skeleton.nif> <out.json>       rest pose of every NiNode (parent, world T/R/S)
  python -I npc_skin.py mesh <body.nif> <out.json>               skinned BSTriShapes: verts, uvs, tris, 4 weights/bone names per vertex, texture
Rotation matrices are the NIF's own (row-major 3x3, world = parent * local), positions in Skyrim units."""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nif2obj import R, parse, avobject, mat_mul, xform

CREATURE = "--creature" in sys.argv   # creature mode (see meshes())
SKEL = {}   # bone name -> skeleton rest world position (filled from the skeleton json before meshes() runs)
IDENT = ([1, 0, 0, 0, 1, 0, 0, 0, 1], (0.0, 0.0, 0.0), 1.0)


def name_of(strings, i):
    return strings[i] if 0 <= i < len(strings) else None


def skeleton(path):
    data, blocks, strings, bsver = parse(open(path, "rb").read())
    out = []

    def visit(idx, parent, parent_bone):
        typ, pos, size = blocks[idx]
        if not (typ.endswith("Node") or typ in ("NiNode", "BSFadeNode")):
            return
        r = R(data, pos)
        name, t, rot, s = avobject(r)
        m = mat_mul(parent, t, rot, s)
        nm = name_of(strings, name) or "node%d" % idx
        out.append(dict(name=nm, parent=parent_bone, pos=list(m[1]), rot=list(m[0]), scale=m[2]))
        me = len(out) - 1
        n = r.u32()
        for c in [r.i32() for _ in range(n)]:
            if c >= 0:
                visit(c, m, me)

    visit(0, IDENT, -1)
    return out


def tex_of(data, blocks, shader_ref):
    if shader_ref < 0:
        return None
    typ, pos, _ = blocks[shader_ref]
    if "Lighting" not in typ:
        return None
    r = R(data, pos)
    r.u32()
    r.i32(); k = r.u32(); [r.i32() for _ in range(k)]; r.i32()
    r.u32(); r.u32(); r.f(4)
    ts = r.i32()
    if ts < 0:
        return None
    rr = R(data, blocks[ts][1]); cnt = rr.u32()
    return rr.lstr() if cnt else None


def meshes(path):
    data, blocks, strings, bsver = parse(open(path, "rb").read())
    shapes = []
    for idx, (typ, pos, size) in enumerate(blocks):
        if typ not in ("BSTriShape", "BSDynamicTriShape"):
            continue
        r = R(data, pos)
        name, t, rot, s = avobject(r)
        r.f(4); skin = r.i32(); shader = r.i32(); alpha = r.i32()
        if skin < 0:
            continue
        dyn = None
        if typ == "BSDynamicTriShape":        # FaceGen heads: the real (morphed) positions are the shape's own Vector4 array
            sdesc = r.u64()
            sntri = r.u16(); snvert = r.u16(); sdsize = r.u32()
            r.p += sdsize
            r.u32()                           # particle data size (0)
            dynsize = r.u32()
            if dynsize == snvert * 16:
                dyn = [struct.unpack_from("<3f", data, r.p + i * 16) for i in range(snvert)]
        # skin instance -> bone node names; the skinned vertex data itself lives in the NiSkinPartition block (shape data size is 0)
        sk = R(data, blocks[skin][1])
        data_ref = sk.i32(); part_ref = sk.i32(); sk.i32()            # skin data, skin partition, skeleton root
        # NiSkinData's overall skin transform maps skeleton space -> shape space; vertices are stored in shape space, so apply its inverse
        d0 = R(data, blocks[data_ref][1])
        d0.f(9); d0.f(3); d0.f()
        nbd = d0.u32(); hasw = d0.u8()
        # shape space -> skeleton space is a translation: for each bone, skeleton rest position minus the bone's bind position
        # in shape space (-R^T t / s from its per-bone skin transform). Bones that agree give the offset.
        offs_ = []
        bindd = {}                                                    # bone name -> [bone frame rotation (row-major) in shape space, bind position]
        sk0 = R(data, blocks[skin][1]); sk0.i32(); sk0.i32(); sk0.i32(); nbs = sk0.u32()
        brefs = [sk0.i32() for _ in range(nbs)]
        for bi_ in range(nbd):
            rot_ = d0.f(9); t_ = d0.f(3); s_ = d0.f(); d0.f(3); d0.f(); nv_ = d0.u16()
            if hasw: d0.p += nv_ * 6
            bname = name_of(strings, avobject(R(data, blocks[brefs[bi_]][1]))[0]) if bi_ < len(brefs) and brefs[bi_] >= 0 else None
            bind = [-(rot_[0 + j] * t_[0] + rot_[3 + j] * t_[1] + rot_[6 + j] * t_[2]) / s_ for j in range(3)]
            if bname:
                bindd[bname] = [[rot_[0], rot_[3], rot_[6], rot_[1], rot_[4], rot_[7], rot_[2], rot_[5], rot_[8]], bind]    # R_s^T, -R_s^T t / s
            if bname in SKEL:
                offs_.append([SKEL[bname][j] - bind[j] for j in range(3)])
        offs_.sort(key=lambda o: o[2])
        off = offs_[len(offs_) // 2] if offs_ else [0.0, 0.0, 0.0]          # median
        if CREATURE:
            off = [0.0, 0.0, 0.0]         # creatures: the mesh stays in shape space; the rest pose of the skeleton becomes the bones' BIND pose (written by npc_build_creature)
        def to_skeleton(v):
            return (v[0] + off[0], v[1] + off[1], v[2] + off[2])
        if part_ref < 0 or blocks[part_ref][0] != "NiSkinPartition":
            print("  skip %s: no NiSkinPartition" % name_of(strings, name)); continue
        pr = R(data, blocks[part_ref][1])
        npart = pr.u32(); dsize = pr.u32(); vsize = pr.u32(); desc = pr.u64()
        stride = vsize
        nvert = dsize // vsize
        offs = lambda nib: ((desc >> (4 * nib)) & 0xF) * 4
        voff, uvoff, nooff, skoff = offs(1), offs(2), offs(4), offs(7)
        has_uv, has_n, has_skin = bool(desc & (1 << 45)), bool(desc & (1 << 47)), bool(desc & (1 << 50))
        if not has_skin:
            print("  skip %s: no skin attributes" % name_of(strings, name)); continue
        nb = sk.u32()
        bones = []
        for _ in range(nb):
            bref = sk.i32()
            bn = None
            if bref >= 0:
                bn = name_of(strings, avobject(R(data, blocks[bref][1]))[0])
            bones.append(bn)
        verts, uvs, normals, w, bi = [], [], [], [], []
        vbase = pr.p
        for i in range(nvert):
            base = vbase + i * stride
            verts.append(to_skeleton(dyn[i] if dyn and i < len(dyn) else struct.unpack_from("<3f", data, base + voff)))
            uvs.append((lambda u, v: (u, 1.0 - v))(*struct.unpack_from("<2e", data, base + uvoff)) if has_uv else (0.0, 0.0))
            if has_n:
                nx, ny, nz = struct.unpack_from("<3B", data, base + nooff)
                normals.append((nx / 127.5 - 1.0, ny / 127.5 - 1.0, nz / 127.5 - 1.0))
            w.append(struct.unpack_from("<4e", data, base + skoff))
            bi.append(struct.unpack_from("<4B", data, base + skoff + 8))
        pr.p = vbase + nvert * stride
        tris = []
        for _ in range(npart):                                         # each partition ends with a plain triangle list (global vertex ids)
            nv, nt, pnb, nstrips, nw = pr.u16(), pr.u16(), pr.u16(), pr.u16(), pr.u16()
            pr.p += pnb * 2
            if pr.u8(): pr.p += nv * 2                                   # vertex map
            if pr.u8(): pr.p += nv * nw * 4                              # vertex weights
            pr.p += nstrips * 2                                          # strip lengths
            if pr.u8():                                                  # faces (strips or triangles)
                pr.p += (nt * 3 if not nstrips else 0) * 2
            if pr.u8(): pr.p += nv * nw                                  # bone indices
            pr.u8(); pr.u8(); pr.u64()                                   # lod level, global VB, vertex desc
            tris += [struct.unpack_from("<3H", data, pr.p + i * 6) for i in range(nt)]
            pr.p += nt * 6
        shapes.append(dict(name=name_of(strings, name) or "shape%d" % idx, verts=verts, uvs=uvs, normals=normals,
                           tris=tris, weights=w, bone_idx=bi, bones=bones, texture=tex_of(data, blocks, shader), bind=bindd))
        print("  %s: %d verts %d tris %d bones texture=%s" % (shapes[-1]["name"], nvert, len(tris), nb, shapes[-1]["texture"]))
    return shapes


if __name__ == "__main__":
    mode, src, dst = sys.argv[1:4]
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    if mode != "skeleton":
        sk_path = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(os.path.abspath(dst)), "skeleton_male.json")
        SKEL.update({b["name"]: b["pos"] for b in json.load(open(sk_path))})
    res = skeleton(src) if mode == "skeleton" else meshes(src)
    json.dump(res, open(dst, "w"))
    print("wrote", dst, len(res), "entries")
