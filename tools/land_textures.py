"""Baked high-resolution landscape textures + full-resolution LAND terrain over the water cells.

Skyrim blends its ground per cell quadrant: a base texture (BTXT) plus alpha layers (ATXT + VTXT, 17x17 opacities per
quadrant), each an LTEX -> TXST (TX00 colour, TX01 normal with the specular mask in alpha), multiplied by the vertex
colours (VCLR). This tool resolves all of that over the user's full load order (Skyrim.esm, DLCs, Skyrim.ccc, then the
active plugins.txt entries, masters first: USSEP, Landscape and Water Fixes, Majestic Mountains ... win as in game),
extracts the layer textures (loose Data files win over BSAs; plugin BSAs override vanilla ones in load order) and bakes
per cell:
  area2/landtex/tex/LX_<gx>_<gy>.png     colour (layers height-blended, x VCLR), sRGB
  area2/landtex/tex/LX_<gx>_<gy>_n.png   tangent-space normal (DirectX, like Skyrim/UE)
  area2/landtex/tex/LX_<gx>_<gy>_s.png   specular mask (M_SkyMaster 'Spec': roughness 0.9 -> 0.3)
  area2/landtex/preview/LX_<gx>_<gy>.jpg 512 px colour thumbnail (Blender preview)
  area2/landtex/layers/<key>.png, <key>_n.png   the LTEX textures themselves (DDS -> PNG, colour A = height)
Height blending: layer weights are interpolated per pixel and the layer with the higher texture height wins inside a
transition band (BLEND_DEPTH), so grass/dirt/rock edges follow stones and clumps instead of a linear cross-fade.

Cells: the old baked terrain's cells (area2/terrain_obj/terrain.obj, Whiterun) at 4096 px, plus every water cell of
area2/water_wide.csv within --water-radius (and a --ring of neighbour cells) so cell water meets real banks instead
of the coarse LOD terrain (the "slab at the cell edge" issue); 2048 px within --near, 1024 px beyond.
Meshes (33x33 vertices per cell = Skyrim's own grid, absolute Skyrim units, UV0 0..1 per cell, one material per cell):
  area2/landtex/tiles/LX_<tx>_<ty>.npz -> Blender -> area2/landtex/fbx/LX_<tx>_<ty>.fbx (tiles of 4x4 cells)
  area2/landtex/lod/lodterrain_trim.obj/.fbx  Skyrim's LOD terrain without the triangles the new cells cover
  area2/landtex/cells.json, tiles.json        manifest for the Unreal import (unreal/SkyBridge/terrain_textures_import.py)

Usage: python tools/land_textures.py [--water-radius 64000] [--near 24000] [--ring 1] [--force] [--only 5,-1;6,-1]
                                     [--no-bake] [--no-fbx] [--no-lod] [--core-px 4096]
"""
import glob, io, json, math, mmap, os, struct, subprocess, sys, time, zlib

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "landtex")
GAME = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition"
DATA = os.path.join(GAME, "Data")
BLENDER = r"D:\blender.exe"
CENTER = (23000.0, -6000.0)            # Whiterun (Skyrim units), same as lod_terrain.py / distant_world.py
TAMRIEL = ("skyrim.esm", 0x3C)
DEFAULT_TEX = "landscape\\dirt02.dds"  # quadrants without a BTXT: the game's default ground
TEX_UNITS = 512.0                      # one landscape texture repeat = 512 units = 8 per cell
LAYER_MAX = 2048                       # extracted LTEX PNGs are capped at this size
BLEND_DEPTH = 0.3                      # height-blend band (weight units); 0 = Skyrim's linear blend
TILE = 4                               # cells per FBX tile side
Image.MAX_IMAGE_PIXELS = None


def arg(name, default, conv=str):
    return conv(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def zstr(b):
    return b.split(b"\0")[0].decode("cp1252", "replace").lower().replace("/", "\\").lstrip("\\")


# ------------------------------------------------------------------------------------------------------------ load order
def load_order():
    names = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
    ccc = os.path.join(GAME, "Skyrim.ccc")
    if os.path.exists(ccc):
        names += [l.strip() for l in open(ccc, encoding="utf-8", errors="replace") if l.strip()]
    pt = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Skyrim Special Edition", "plugins.txt")
    if os.path.exists(pt):
        names += [l.strip()[1:] for l in open(pt, encoding="utf-8", errors="replace") if l.strip().startswith("*")]
    seen, out = set(), []
    for n in names:
        if n.lower() in seen or not os.path.exists(os.path.join(DATA, n)):
            continue
        seen.add(n.lower()); out.append(n)

    def is_master(n):
        if n.lower().endswith((".esm", ".esl")):
            return True
        with open(os.path.join(DATA, n), "rb") as f:
            h = f.read(24)
        return h[:4] == b"TES4" and bool(struct.unpack_from("<I", h, 8)[0] & 1)
    return [n for n in out if is_master(n)] + [n for n in out if not is_master(n)]


class Plugin:
    def __init__(self, name):
        self.name = name.lower()
        self.f = open(os.path.join(DATA, name), "rb")
        self.mm = mmap.mmap(self.f.fileno(), 0, access=mmap.ACCESS_READ)
        sz, = struct.unpack_from("<I", self.mm, 4)
        self.masters = [zstr(sd) for st, sd in subs(self.mm[24:24 + sz]) if st == b"MAST"]
        self.top = 24 + sz

    def close(self):
        self.mm.close(); self.f.close()

    def fid(self, f):
        i = f >> 24
        return (self.masters[i] if i < len(self.masters) else self.name, f & 0xFFFFFF)

    def body(self, p):
        sz, flags = struct.unpack_from("<II", self.mm, p + 4)
        b = self.mm[p + 24:p + 24 + sz]
        return zlib.decompress(b[4:]) if flags & 0x40000 else b

    def top_groups(self):
        p, n = self.top, len(self.mm)
        while p + 24 <= n:
            t = self.mm[p:p + 4]; sz, = struct.unpack_from("<I", self.mm, p + 4)
            if t == b"GRUP":
                yield self.mm[p + 8:p + 12], p, p + sz; p += sz
            else:
                p += 24 + sz

    def records(self, s, e):
        p = s + 24
        while p < e:
            t = self.mm[p:p + 4]; sz, = struct.unpack_from("<I", self.mm, p + 4)
            if t == b"GRUP":
                p += sz; continue
            yield t, p, struct.unpack_from("<I", self.mm, p + 12)[0]
            p += 24 + sz


def parse_land(body, pl):
    h = col = None
    base, layers, cur = {}, [], None
    for st, sd in subs(body):
        if st == b"VHGT" and len(sd) >= 1093:
            off, = struct.unpack_from("<f", sd, 0)
            d = np.frombuffer(sd, dtype=np.int8, count=1089, offset=4).astype(np.float64).reshape(33, 33)
            col0 = np.cumsum(d[:, 0]) + off                    # column 0 accumulates up the rows, then each row along x
            h = np.cumsum(np.concatenate([col0[:, None], d[:, 1:]], axis=1), axis=1) * 8.0
        elif st == b"VCLR" and len(sd) >= 3267:
            col = np.frombuffer(sd, dtype=np.uint8, count=3267).reshape(33, 33, 3).copy()
        elif st == b"BTXT":
            f, q = struct.unpack("<IB", sd[:5]); base[q] = pl.fid(f) if f else None
        elif st == b"ATXT":
            f, q, _u, lay = struct.unpack("<IBBh", sd[:8])
            cur = {"ltex": pl.fid(f) if f else None, "q": q, "layer": lay, "op": np.zeros((17, 17))}; layers.append(cur)
        elif st == b"VTXT" and cur is not None:
            for i in range(len(sd) // 8):
                pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                if pos < 289: cur["op"][pos // 17, pos % 17] = op
    if h is None:
        return None
    return {"h": h, "col": col, "base": base, "layers": layers, "plugin": pl.name}


def read_load_order(order, want):
    """-> ltex {fid: txst fid}, txst {fid: (diffuse, normal)}, land {(gx, gy): rec}; later plugins override."""
    ltex, txst, land = {}, {}, {}
    t0 = time.time()
    for n in order:
        try:
            pl = Plugin(n)
        except Exception as e:
            print("skip plugin", n, e); continue
        try:
            for label, s, e in pl.top_groups():
                if label == b"LTEX":
                    for _t, p, f in pl.records(s, e):
                        for st, sd in subs(pl.body(p)):
                            if st == b"TNAM": ltex[pl.fid(f)] = pl.fid(struct.unpack("<I", sd[:4])[0])
                elif label == b"TXST":
                    for _t, p, f in pl.records(s, e):
                        r = {st: zstr(sd) for st, sd in subs(pl.body(p)) if st in (b"TX00", b"TX01")}
                        if r.get(b"TX00"): txst[pl.fid(f)] = (r[b"TX00"], r.get(b"TX01"))
                elif label == b"WRLD":
                    walk_world(pl, s + 24, e, want, land, {"cell": None}, False)
        except Exception as ex:
            print("plugin %s: read error %s" % (n, ex))
        pl.close()
    print("load order: %d plugins in %.0f s; LTEX %d, TXST %d, LAND cells %d/%d"
          % (len(order), time.time() - t0, len(ltex), len(txst), len(land), len(want)))
    return ltex, txst, land


def walk_world(pl, p, e, want, land, st, inworld):
    mm = pl.mm
    while p < e:
        t = mm[p:p + 4]; sz, = struct.unpack_from("<I", mm, p + 4)
        if t == b"GRUP":
            label, gt = struct.unpack_from("<Ii", mm, p + 8)
            if gt == 1:
                if pl.fid(label) == TAMRIEL:
                    walk_world(pl, p + 24, p + sz, want, land, st, True)
            elif inworld and (gt in (4, 5, 9) or (gt == 6 and st["cell"] in want)):
                walk_world(pl, p + 24, p + sz, want, land, st, True)
            p += sz; continue
        if inworld:
            if t == b"CELL":
                st["cell"] = None
                for s, sd in subs(pl.body(p)):
                    if s == b"XCLC": st["cell"] = struct.unpack("<ii", sd[:8]); break
            elif t == b"LAND" and st["cell"] in want:
                rec = parse_land(pl.body(p), pl)
                if rec: land[st["cell"]] = rec
        p += 24 + sz


# -------------------------------------------------------------------------------------------------------------- textures
class FastBsa:
    """BSA v105 index restricted to wanted paths (one read for the name block; tools/bsa.py reads names byte by byte)."""
    def __init__(self, path, wanted):
        self.path = path
        f = open(path, "rb")
        magic, ver, off, flags, nfold, nfile, _tfold, tfn = struct.unpack("<4sIIIIIII", f.read(32))
        if magic != b"BSA\0" or ver != 105:
            f.close(); raise ValueError("not a v105 BSA")
        self.comp_default, self.embed = bool(flags & 0x4), bool(flags & 0x100)
        f.seek(off)
        folders = [struct.unpack("<QIIQ", f.read(24)) for _ in range(nfold)]
        recs = []
        for _h, count, _p, _o in folders:
            nlen = f.read(1)[0]
            folder = f.read(nlen).rstrip(b"\0").decode("cp1252", "replace").lower()
            data = f.read(16 * count)
            recs.append((folder, [struct.unpack_from("<QII", data, i * 16)[1:] for i in range(count)]))
        names = f.read(tfn).split(b"\0")
        f.close()
        self.files, i = {}, 0
        for folder, rr in recs:
            for size, offset in rr:
                key = folder + "\\" + names[i].decode("cp1252", "replace").lower()
                if key in wanted:
                    self.files[key] = (size & 0x3FFFFFFF, offset, self.comp_default ^ bool(size & 0x40000000))
                i += 1

    def read(self, key):
        import lz4.frame
        size, offset, comp = self.files[key]
        with open(self.path, "rb") as f:
            f.seek(offset)
            if self.embed:
                n = f.read(1)[0]; f.read(n); size -= n + 1
            if comp:
                f.read(4); return lz4.frame.decompress(f.read(size - 4))
            return f.read(size)


class TexSource:
    def __init__(self, order, wanted_rel):
        wanted = {"textures\\" + r for r in wanted_rel}
        names = sorted(glob.glob(os.path.join(DATA, "*.bsa")))
        lower = {os.path.basename(p).lower(): p for p in names}
        chain = [p for p in names if os.path.basename(p).lower().startswith("skyrim - ")]
        for n in order:                                     # plugin archives in load order (later wins)
            stem = os.path.splitext(n)[0].lower()
            for b in sorted(lower):
                if b == stem + ".bsa" or (b.startswith(stem + " - ") and b.endswith(".bsa")):
                    if lower[b] not in chain: chain.append(lower[b])
        self.archives = []
        for p in chain:
            try:
                a = FastBsa(p, wanted)
                if a.files: self.archives.append(a)
            except Exception:
                pass
        print("texture archives with landscape textures: %d (%s)" % (len(self.archives),
              ", ".join(os.path.basename(a.path) for a in self.archives[-6:])))

    def raw(self, rel):
        key = ("textures\\" + rel).lower()
        loose = os.path.join(DATA, key)
        if os.path.exists(loose):
            return open(loose, "rb").read(), "loose"
        for a in reversed(self.archives):
            if key in a.files:
                return a.read(key), os.path.basename(a.path)
        return None, None

    @staticmethod
    def decode(raw):
        if raw[84:88] == b"DX10":
            f = struct.unpack_from("<I", raw, 128)[0]
            if f in (72, 75, 78, 99):                       # *_SRGB -> UNORM twin (Pillow decodes those)
                raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
        im = Image.open(io.BytesIO(raw)); im.load()
        return im


def tex_key(rel):
    stem = os.path.splitext(rel)[0]
    stem = stem[len("landscape\\"):] if stem.startswith("landscape\\") else stem
    return "".join(c if c.isalnum() else "_" for c in stem)


def height_candidates(diff):
    stem = os.path.splitext(diff)[0]
    return [stem + "_p.dds", "landscape\\parallax\\" + os.path.basename(diff)]


class Layers:
    """Layer texture cache: PNG extraction (once) + per-resolution float arrays for baking."""
    def __init__(self, src):
        self.src, self.meta, self.cache = src, {}, {}
        os.makedirs(os.path.join(OUT, "layers"), exist_ok=True)

    def extract(self, key, diff, norm):
        if key in self.meta:
            return self.meta[key]["ok"]
        cpath = os.path.join(OUT, "layers", key + ".png")
        npath = os.path.join(OUT, "layers", key + "_n.png")
        info = {"diffuse": diff, "normal": norm, "ok": False}
        self.meta[key] = info
        raw, where = self.src.raw(diff)
        if raw is None:
            print("  missing colour map", diff); return False
        info["from"] = where
        if not os.path.exists(cpath):
            im = self.src.decode(raw).convert("RGBA")
            if max(im.size) > LAYER_MAX: im = im.resize((LAYER_MAX, LAYER_MAX), Image.LANCZOS)
            height = im.getchannel("A") if np.asarray(im.getchannel("A"), np.float32).std() / 255.0 > 0.04 else None
            for hc in ([] if height is not None else height_candidates(diff)):
                hr, _w = self.src.raw(hc)
                if hr:
                    try:
                        him = self.src.decode(hr).convert("RGBA").resize(im.size, Image.BILINEAR)
                        ch = him.getchannel("A") if np.asarray(him.getchannel("A"), np.float32).std() > 10 else him.convert("L")
                        if np.asarray(ch, np.float32).std() > 10: height = ch; info["height"] = hc; break
                    except Exception as e:
                        print("  height map decode failed", hc, e)
            if height is None:                              # luminance, stretched to 0..1
                l = np.asarray(im.convert("L"), np.float32)
                lo, hi = np.percentile(l, 2), np.percentile(l, 98)
                height = Image.fromarray(np.clip((l - lo) / max(hi - lo, 1.0) * 255.0, 0, 255).astype(np.uint8))
                info["height"] = "luminance"
            im.putalpha(height)
            im.save(cpath, compress_level=3)
        if not os.path.exists(npath):
            nr, _w = self.src.raw(norm) if norm else (None, None)
            if nr is None:
                nr, _w = self.src.raw(os.path.splitext(diff)[0] + "_n.dds")
            if nr is not None:
                try:
                    im = self.src.decode(nr)
                    has_a = im.mode in ("RGBA", "LA")
                    im = im.convert("RGBA")
                    if max(im.size) > LAYER_MAX: im = im.resize((LAYER_MAX, LAYER_MAX), Image.LANCZOS)
                    a = np.asarray(im, np.uint8).copy()
                    if a[..., 2].mean() < 20:               # BC5 (two channels): rebuild z
                        xy = a[..., :2].astype(np.float32) / 127.5 - 1.0
                        a[..., 2] = np.clip((np.sqrt(np.clip(1 - (xy ** 2).sum(-1), 0, 1)) * 0.5 + 0.5) * 255, 0, 255)
                    if not has_a: a[..., 3] = 0             # no specular mask: matte
                    Image.fromarray(a, "RGBA").save(npath, compress_level=3)
                except Exception as e:
                    print("  normal decode failed", norm, e)
        info["ok"] = True
        return True

    def get(self, key, R):
        """-> (height RxR, colour RxRx3 0..1, normal RxRx3 -1..1, spec RxR 0..1), float32."""
        ck = (key, R)
        if ck not in self.cache:
            if len(self.cache) > 24: self.cache.clear()
            c = Image.open(os.path.join(OUT, "layers", key + ".png")).convert("RGBA").resize((R, R), Image.LANCZOS)
            c = np.asarray(c, np.float32) / 255.0
            npath = os.path.join(OUT, "layers", key + "_n.png")
            if os.path.exists(npath):
                n = np.asarray(Image.open(npath).convert("RGBA").resize((R, R), Image.LANCZOS), np.float32) / 255.0
                nv, sp = n[..., :3] * 2.0 - 1.0, n[..., 3]
            else:
                nv, sp = np.zeros((R, R, 3), np.float32), np.zeros((R, R), np.float32)
                nv[..., 2] = 1.0
            self.cache[ck] = (c[..., 3].copy(), np.ascontiguousarray(c[..., :3]), nv, sp)
        return self.cache[ck]


# ----------------------------------------------------------------------------------------------------------------- cells
def wanted_cells(wradius, near, ring, core_px):
    core = set()
    tpath = os.path.join(AREA, "terrain_obj", "terrain.obj")
    for line in open(tpath):
        if line.startswith("o terrain_tile_"):
            gx, gy = line.split()[1][len("terrain_tile_"):].split("_")
            core.add((int(gx), int(gy)))
    px = {c: core_px for c in core}
    for line in open(os.path.join(AREA, "water_wide.csv")).read().split():
        gx, gy, _h = line.split(",")
        gx, gy = int(gx), int(gy)
        for dx in range(-ring, ring + 1):
            for dy in range(-ring, ring + 1):
                c = (gx + dx, gy + dy)
                d = math.hypot((c[0] + .5) * 4096 - CENTER[0], (c[1] + .5) * 4096 - CENTER[1])
                if d <= wradius and c not in px:
                    px[c] = 2048 if d <= near else 1024
    return px, core


def cell_weights(rec, key_of):
    """texture key -> 33x33 weight; Skyrim order per quadrant: base, then each ATXT layer alpha-composited on top."""
    acc, cnt = {}, np.zeros((33, 33))
    for q in range(4):
        ws = {key_of(rec["base"].get(q)): np.ones((17, 17))}
        for l in sorted((l for l in rec["layers"] if l["q"] == q), key=lambda l: l["layer"]):
            a = np.clip(l["op"], 0.0, 1.0)
            k = key_of(l["ltex"])
            for kk in ws: ws[kk] = ws[kk] * (1.0 - a)
            ws[k] = ws.get(k, 0.0) + a
        oy, ox = (q // 2) * 16, (q % 2) * 16
        for k, w in ws.items():
            acc.setdefault(k, np.zeros((33, 33)))[oy:oy + 17, ox:ox + 17] += w
        cnt[oy:oy + 17, ox:ox + 17] += 1
    return {k: v / cnt for k, v in acc.items()}


def stitch(W, land):
    """Average weights (and vertex colours) on shared cell edges so neighbouring bakes meet without a seam."""
    for (gx, gy) in W:
        for (nx, ny), a_sl, b_sl in (((gx + 1, gy), (slice(None), 32), (slice(None), 0)),
                                     ((gx, gy + 1), (32, slice(None)), (0, slice(None)))):
            if (nx, ny) not in W:
                continue
            A, B = W[(gx, gy)], W[(nx, ny)]
            for k in set(A) | set(B):
                A.setdefault(k, np.zeros((33, 33))); B.setdefault(k, np.zeros((33, 33)))
                m = (A[k][a_sl] + B[k][b_sl]) * 0.5
                A[k][a_sl] = m; B[k][b_sl] = m
            ca, cb = land[(gx, gy)]["col"], land[(nx, ny)]["col"]
            if ca is not None and cb is not None:
                m = ((ca[a_sl].astype(np.int32) + cb[b_sl]) // 2).astype(np.uint8)
                ca[a_sl] = m; cb[b_sl] = m
    for w in W.values():
        tot = sum(w.values())
        tot[tot <= 1e-9] = 1.0
        for k in list(w):
            w[k] = w[k] / tot
            if w[k].max() < 1e-3: del w[k]


def interp_matrix(S):
    u = (np.arange(S) + 0.5) / S * 32.0
    i0 = np.clip(np.floor(u).astype(int), 0, 31)
    f = (u - i0).astype(np.float32)
    A = np.zeros((S, 33), np.float32)
    A[np.arange(S), i0] = 1.0 - f
    A[np.arange(S), i0 + 1] += f
    return A


def blend(W, layers, S, want_normal, block=512):
    """Bake one cell at S x S px (row 0 = north). Returns colour float (S,S,3) or (normal (S,S,3), spec (S,S))."""
    keys = sorted(W, key=lambda k: -W[k].sum())
    R = int(round(S * TEX_UNITS / 4096.0))
    idx = np.arange(S) % R
    Ax = interp_matrix(S)
    Ay = Ax[::-1]                                         # image row 0 = north edge = vertex row 32
    out = np.zeros((S, S, 3), np.float32)
    spec = np.zeros((S, S), np.float32) if want_normal else None
    for r0 in range(0, S, block):
        rows = slice(r0, min(S, r0 + block))
        ri = idx[rows]
        ts = []
        for k in keys:
            w = Ay[rows] @ W[k].astype(np.float32) @ Ax.T
            h = layers.get(k, R)[0][ri][:, idx]
            ts.append(np.where(w > 1e-3, w + BLEND_DEPTH * h, -1e9).astype(np.float32))
        m = np.max(ts, axis=0) - BLEND_DEPTH
        cs = [np.maximum(t - m, 0.0) for t in ts]
        tot = np.maximum(sum(cs), 1e-6)
        for k, c in zip(keys, cs):
            c = c / tot
            _h, col, nv, sp = layers.get(k, R)
            src = (nv if want_normal else col)[ri][:, idx]
            out[rows] += c[..., None] * src
            if want_normal:
                spec[rows] += c * sp[ri][:, idx]
        del ts, cs
    if want_normal:
        out /= np.maximum(np.linalg.norm(out, axis=2, keepdims=True), 1e-6)
        return out, spec
    return out


def bake_cell(c, rec, W, layers, S, force):
    name = "LX_%d_%d" % c
    tdir = os.path.join(OUT, "tex")
    cpath, npath, spath = (os.path.join(tdir, name + s + ".png") for s in ("", "_n", "_s"))
    ppath = os.path.join(OUT, "preview", name + ".jpg")
    if not force and all(os.path.exists(p) for p in (cpath, npath, spath, ppath)):
        return False
    col = blend(W, layers, S, False)
    if rec["col"] is not None:                              # Skyrim multiplies the ground by the vertex colours
        Ax = interp_matrix(S); Ay = Ax[::-1]
        for ch in range(3):
            col[..., ch] *= (Ay @ (rec["col"][..., ch].astype(np.float32) / 255.0) @ Ax.T)
    im = Image.fromarray(np.clip(col * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
    del col
    im.save(cpath, compress_level=3)
    im.resize((512, 512), Image.LANCZOS).save(ppath, quality=90)
    del im
    NS = S // 2
    nv, sp = blend(W, layers, NS, True)
    Image.fromarray(np.clip((nv * 0.5 + 0.5) * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB").save(npath, compress_level=3)
    Image.fromarray(np.clip(sp * 255.0 + 0.5, 0, 255).astype(np.uint8), "L").resize((S // 4, S // 4), Image.LANCZOS).save(spath)
    return True


# ------------------------------------------------------------------------------------------------------------------ mesh
def write_tiles(land):
    """One npz per TILE x TILE cells: 33x33 vertices per cell, smooth normals across cell borders."""
    def H(gx, gy, ix, iy):
        while ix < 0 and (gx - 1, gy) in land: gx -= 1; ix += 32
        while ix > 32 and (gx + 1, gy) in land: gx += 1; ix -= 32
        while iy < 0 and (gx, gy - 1) in land: gy -= 1; iy += 32
        while iy > 32 and (gx, gy + 1) in land: gy += 1; iy -= 32
        return land[(gx, gy)]["h"][min(max(iy, 0), 32), min(max(ix, 0), 32)]

    tiles = {}
    for c in land:
        tiles.setdefault((c[0] // TILE, c[1] // TILE), []).append(c)
    tdir = os.path.join(OUT, "tiles")
    os.makedirs(tdir, exist_ok=True)
    meta = {}
    yy, xx = np.meshgrid(np.arange(32), np.arange(32), indexing="ij")
    base = (yy * 33 + xx).ravel()
    quad = np.stack([base, base + 1, base + 34, base, base + 34, base + 33], 1).reshape(-1, 3)
    for (tx, ty), cells in sorted(tiles.items()):
        cells = sorted(cells)
        pos, nrm, uv, tris, mat = [], [], [], [], []
        for mi, (gx, gy) in enumerate(cells):
            h = land[(gx, gy)]["h"]
            pad = np.array([[H(gx, gy, ix, iy) for ix in range(-1, 34)] for iy in range(-1, 34)])
            dx = (pad[1:-1, 2:] - pad[1:-1, :-2]) / 256.0
            dy = (pad[2:, 1:-1] - pad[:-2, 1:-1]) / 256.0
            n = np.dstack([-dx, -dy, np.ones_like(dx)])
            n /= np.linalg.norm(n, axis=2, keepdims=True)
            vy, vx = np.mgrid[0:33, 0:33]
            o = len(pos) and sum(len(p) for p in pos)
            pos.append(np.stack([gx * 4096 + vx.ravel() * 128.0, gy * 4096 + vy.ravel() * 128.0, h.ravel()], 1))
            nrm.append(n.reshape(-1, 3))
            uv.append(np.stack([vx.ravel() / 32.0, vy.ravel() / 32.0], 1))
            tris.append(quad + o)
            mat.append(np.full(len(quad), mi, np.int32))
        name = "LX_%d_%d" % (tx, ty)
        np.savez(os.path.join(tdir, name + ".npz"), pos=np.concatenate(pos), nrm=np.concatenate(nrm).astype(np.float32),
                 uv=np.concatenate(uv).astype(np.float32), tris=np.concatenate(tris).astype(np.int32),
                 mat=np.concatenate(mat), names=np.array(["LX_%d_%d" % c for c in cells]))
        meta[name] = {"cells": [list(c) for c in cells], "materials": ["LX_%d_%d" % c for c in cells]}
    json.dump(meta, open(os.path.join(OUT, "tiles.json"), "w"), indent=1)
    print("mesh tiles: %d" % len(meta))
    return [os.path.join(tdir, n + ".npz") for n in meta]


def trim_lod(covered):
    """lodterrain.obj without the triangles whose whole footprint lies in cells this terrain covers (an inset
    centroid + vertex test, so triangles straddling the edge stay: no holes; the LOD sits 60 units lower anyway)."""
    src = os.path.join(AREA, "lod_obj", "lodterrain.obj")
    ld = os.path.join(OUT, "lod")
    os.makedirs(ld, exist_ok=True)
    verts, kept, dropped = [], 0, 0
    cov = lambda x, y: (math.floor(x / 4096), math.floor(y / 4096)) in covered
    with open(os.path.join(ld, "lodterrain_trim.obj"), "w") as obj:
        obj.write("mtllib lodterrain_trim.mtl\n")
        for line in open(src):
            if line.startswith("v "):
                v = line.split(); verts.append((float(v[1]), float(v[2]))); obj.write(line)
            elif line.startswith("f "):
                ids = [int(t.split("/")[0]) - 1 for t in line.split()[1:4]]
                mx = sum(verts[i][0] for i in ids) / 3.0; my = sum(verts[i][1] for i in ids) / 3.0
                pts = [(mx, my)] + [(mx + (verts[i][0] - mx) * 0.95, my + (verts[i][1] - my) * 0.95) for i in ids]
                if all(cov(x, y) for x, y in pts):
                    dropped += 1; continue
                kept += 1; obj.write(line)
            elif not line.startswith("mtllib"):
                obj.write(line)
    mt = os.path.join(AREA, "lod_obj", "lodterrain.mtl")
    open(os.path.join(ld, "lodterrain_trim.mtl"), "w").write(open(mt).read())
    print("lodterrain_trim.obj: kept %d, dropped %d LOD triangles under full-resolution cells" % (kept, dropped))


def blender(*args):
    script = os.path.join(ROOT, "tools", "land_textures_blender.py")
    return subprocess.run([BLENDER, "-b", "--factory-startup", "-P", script, "--"] + list(args), check=False)


# ------------------------------------------------------------------------------------------------------------------ main
def old_thumbs():
    """512 px thumbnails of the current Unreal terrain bake (area2/tex/terrain_tile_*.png) for the comparison preview."""
    d = os.path.join(OUT, "preview_old")
    os.makedirs(d, exist_ok=True)
    for p in sorted(glob.glob(os.path.join(AREA, "tex", "terrain_tile_*.png"))):
        dst = os.path.join(d, os.path.splitext(os.path.basename(p))[0] + ".jpg")
        if not os.path.exists(dst):
            with Image.open(p) as im:
                im.draft("RGB", (512, 512))
                im.convert("RGB").resize((512, 512), Image.LANCZOS).save(dst, quality=90)


def main():
    if "--old-thumbs" in sys.argv:
        return old_thumbs()
    wradius = arg("--water-radius", 64000.0, float)
    near = arg("--near", 24000.0, float)
    ring = arg("--ring", 1, int)
    core_px = arg("--core-px", 4096, int)
    force = "--force" in sys.argv
    only = {tuple(map(int, s.split(","))) for s in arg("--only", "", str).split(";") if s}
    px, core = wanted_cells(wradius, near, ring, core_px)
    print("cells wanted: %d (core %d at %d px, water+ring %d)" % (len(px), len(core), core_px, len(px) - len(core)))
    for d in ("tex", "preview", "tiles", "fbx", "lod"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    order = load_order()
    ltex, txst, land = read_load_order(order, set(px))

    def paths_of(fid):
        t = txst.get(ltex.get(fid)) if fid else None
        return t if t else (DEFAULT_TEX, None)

    needed = set()
    for rec in land.values():
        for fid in list(rec["base"].values()) + [l["ltex"] for l in rec["layers"]] + [None]:
            d, n = paths_of(fid)
            needed.update([d, n or os.path.splitext(d)[0] + "_n.dds", os.path.splitext(d)[0] + "_n.dds"] + height_candidates(d))
    src = TexSource(order, {p for p in needed if p})
    layers = Layers(src)
    key_ok = {}

    def key_of(fid):
        d, n = paths_of(fid)
        k = tex_key(d)
        if k not in key_ok:
            key_ok[k] = layers.extract(k, d, n)
        if not key_ok[k]:
            k = tex_key(DEFAULT_TEX)
            if k not in key_ok: key_ok[k] = layers.extract(k, DEFAULT_TEX, None)
        return k

    W = {c: cell_weights(rec, key_of) for c, rec in land.items()}
    stitch(W, land)
    print("layer textures: %d (%d missing) -> area2/landtex/layers" % (len(key_ok), sum(1 for v in key_ok.values() if not v)))

    cells_meta = {}
    if "--no-bake" not in sys.argv:
        t0, n = time.time(), 0
        for c in sorted(land, key=lambda c: (px[c] != core_px, math.hypot(c[0] * 4096 - CENTER[0], c[1] * 4096 - CENTER[1]))):
            if only and c not in only:
                continue
            if bake_cell(c, land[c], W[c], layers, px[c], force):
                n += 1
                if n % 10 == 0:
                    print("  baked %d cells (%.0f s)" % (n, time.time() - t0)); sys.stdout.flush()
        print("baked %d cells in %.0f s" % (n, time.time() - t0))
    for c, rec in land.items():
        cells_meta["LX_%d_%d" % c] = {"cell": list(c), "px": px[c], "core": c in core, "plugin": rec["plugin"],
                                      "layers": {k: round(float(w.mean()), 3) for k, w in sorted(W[c].items(), key=lambda kv: -kv[1].sum())},
                                      "zmin": float(rec["h"].min()), "zmax": float(rec["h"].max())}
    json.dump(cells_meta, open(os.path.join(OUT, "cells.json"), "w"), indent=1)
    json.dump(layers.meta, open(os.path.join(OUT, "layers.json"), "w"), indent=1)
    missing = sorted(set(px) - set(land))
    print("cells with LAND %d; wanted cells without LAND (ocean / outside the map) %d" % (len(land), len(missing)))
    npz = write_tiles(land)
    if "--no-lod" not in sys.argv:
        trim_lod(set(land))
    if "--no-fbx" not in sys.argv:
        for i in range(0, len(npz), 30):
            blender("export", *npz[i:i + 30])
        if "--no-lod" not in sys.argv:
            blender("lod", os.path.join(OUT, "lod", "lodterrain_trim.obj"), os.path.join(OUT, "fbx"))


if __name__ == "__main__":
    main()
