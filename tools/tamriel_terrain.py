"""Terrain and water for all of Tamriel, from the official masters' LAND records (exact heights, texture layers, vertex colours).

Two layers, both in absolute Skyrim units (same convention as area2/terrain_obj/terrain.obj, exported by blender_export.py):
  tlo_<GX>_<GY>   low-res group mesh, 16x16 cells, one vertex every 512 units (every 4th LAND vertex). One material slot per
                  4x4-cell chunk ('tlo_<cx>_<cy>') so Unreal can hide the chunk under its full-res mesh. Textured with
                  tatl_<GX>_<GY>.png (128 px per cell, baked from the landscape layers) by world position (M_TerrainFar).
  tch_<cx>_<cy>   full-res chunk mesh, 4x4 cells, every LAND vertex (128 units), with a skirt along its border to hide the seam
                  to the low-res neighbours. Material slot 'tdet_<cx>_<cy>' = baked 4096 px texture (1024 px per cell).
Cells covered by Whiterun's hand-baked terrain (area2/terrain_obj/terrain.obj) are left out of both.

Water: area2/tamriel/water_quads.csv (x0, y0, length, height: 128-unit strips where LAND is below the cell's water height;
fully wet cells are one 4096-unit square: length 0), skipping cells that area2/water_wide.csv already covers (Whiterun area).

Usage:
  python tools/tamriel_terrain.py --land            parse LAND once -> area2/tamriel/land.pkl
  python tools/tamriel_terrain.py --low             all low-res groups + atlases + water, exported to area2/export
  python tools/tamriel_terrain.py --chunk cx cy     one full-res chunk
  python tools/tamriel_terrain.py --serve           background service: --land/--low if missing, then bakes the chunks the editor
                                                    lists in area2/tamriel/terrain_requests.txt (done -> terrain_ready.txt)"""
import io, glob, math, os, pickle, re, struct, subprocess, sys, time
from array import array
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tamriel_world import scan, subs, TAMRIEL, OUT, DATA
from bsa import Bsa
from PIL import Image, ImageChops, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
TEX = os.path.join(AREA, "tex")
EXPORT = os.path.join(AREA, "export")
LOW_OBJ, CHUNK_OBJ = os.path.join(OUT, "low_obj"), os.path.join(OUT, "chunk_obj")
LAND_PKL = os.path.join(OUT, "land.pkl")
REQ, READY = os.path.join(OUT, "terrain_requests.txt"), os.path.join(OUT, "terrain_ready.txt")
BLENDER = r"D:\blender.exe"
GROUP, CHUNK = 16, 4                     # cells per side
FAR_PX, NEAR_PX = 128, 1024              # baked texture pixels per cell
TILE_UNITS = 512.0                       # one repeat of a landscape texture (as in esm_land_tex.py)
SKIRT = 96.0
DEFAULT_TEX = "landscape\\dirt02.dds"
LIFT_TARGET, LIFT_MAX = 78.0, 2.0        # mean sRGB brightness dark landscape textures are lifted to (see Baker.image)


# ---------------------------------------------------------------- LAND
def parse_land():
    cells, ltex, txst, water, info = {}, {}, {}, {}, {"default_water": -14000.0}
    cur = {}

    def on(name, rm, t, flags, fid, body, world, xy):
        if t == b"LTEX":
            for st, sd in subs(body):
                if st == b"TNAM": ltex[fid] = rm(struct.unpack("<I", sd[:4])[0])
        elif t == b"TXST":
            for st, sd in subs(body):
                if st == b"TX00": txst[fid] = sd.split(b"\0")[0].decode("cp1252").lower()
        elif t == b"WRLD" and fid == TAMRIEL:
            for st, sd in subs(body):
                if st == b"DNAM" and len(sd) >= 8: info["default_water"] = struct.unpack("<ff", sd[:8])[1]
        elif t == b"CELL" and world == TAMRIEL and xy is not None:
            has, h = False, None
            for st, sd in subs(body):
                if st == b"DATA": has = bool(sd[0] & 0x02)
                elif st == b"XCLW": h, = struct.unpack("<f", sd[:4])
            if has:
                water[xy] = h if h is not None and abs(h) < 1e7 else None   # None = worldspace default
            else:
                water.pop(xy, None)
        elif t == b"LAND" and world == TAMRIEL and xy is not None:
            c = {"base": {}, "layers": [], "vc": None}
            lay = None
            for st, sd in subs(body):
                if st == b"VHGT":
                    off, = struct.unpack_from("<f", sd, 0); d = struct.unpack_from("<1089b", sd, 4)
                    h, rowbase = array("f"), off
                    for y in range(33):
                        for x in range(33):
                            if x == 0: rowbase += d[y * 33]; v = rowbase
                            else: v += d[y * 33 + x]
                            h.append(v * 8.0)
                    c["h"] = h
                elif st == b"VCLR" and len(sd) >= 3267:
                    c["vc"] = bytes(sd[:3267])
                elif st == b"BTXT":
                    f, q = struct.unpack("<IB", sd[:5]); c["base"][q] = rm(f)
                elif st == b"ATXT":
                    f, q, _u, l = struct.unpack("<IBBh", sd[:8])
                    lay = [q, l, rm(f), array("f", [0.0] * 289)]; c["layers"].append(lay)
                elif st == b"VTXT" and lay is not None:
                    for i in range(len(sd) // 8):
                        pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                        if pos < 289: lay[3][pos] = op
            if "h" in c:
                c["layers"].sort(key=lambda l: (l[0], l[1]))
                cells[xy] = c

    scan(TAMRIEL, on)
    paths = {f: txst.get(t) for f, t in ltex.items()}
    land = {"cells": cells, "ltex": paths, "water": water, "default_water": info["default_water"]}
    pickle.dump(land, open(LAND_PKL, "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    xs = [k[0] for k in cells]; ys = [k[1] for k in cells]
    print("LAND: %d cells, x %d..%d, y %d..%d; %d landscape textures; %d water cells; default water %.0f" %
          (len(cells), min(xs), max(xs), min(ys), max(ys), len(paths), len(water), info["default_water"]))
    return land


def load_land():
    if not os.path.exists(LAND_PKL):
        return parse_land()
    return pickle.load(open(LAND_PKL, "rb"))


def whiterun_cells():
    """Cells Whiterun's own hand-baked terrain covers (kept, so the Tamriel layers leave them out)."""
    out = set()
    p = os.path.join(AREA, "terrain_obj", "terrain.obj")
    if os.path.exists(p):
        for line in open(p):
            m = re.match(r"o terrain_tile_(-?\d+)_(-?\d+)", line)
            if m: out.add((int(m.group(1)), int(m.group(2))))
    return out


class Heights:
    def __init__(self, cells, skip):
        self.cells, self.skip = cells, skip

    def has(self, gx, gy):
        return (gx, gy) in self.cells and (gx, gy) not in self.skip

    def at(self, X, Y):
        """Height at global vertex (X, Y) = cell * 32 + local (0..32); clamped into existing neighbours."""
        gx, lx = divmod(X, 32); gy, ly = divmod(Y, 32)
        for ox in ((0, 1) if lx == 0 else (0,)):                   # a border vertex belongs to up to four cells
            for oy in ((0, 1) if ly == 0 else (0,)):
                c = self.cells.get((gx - ox, gy - oy))
                if c is not None:
                    return c["h"][(ly + 32 * oy) * 33 + lx + 32 * ox]
        return None

    def normal(self, X, Y, step):
        h0 = self.at(X, Y)
        hl, hr, hd, hu = (self.at(X - step, Y), self.at(X + step, Y), self.at(X, Y - step), self.at(X, Y + step))
        hl = h0 if hl is None else hl; hr = h0 if hr is None else hr
        hd = h0 if hd is None else hd; hu = h0 if hu is None else hu
        nx, ny, nz = (hl - hr), (hd - hu), 4.0 * 128.0 * step / 2
        n = math.sqrt(nx * nx + ny * ny + nz * nz)
        return nx / n, ny / n, nz / n


# ---------------------------------------------------------------- textures
class Baker:
    def __init__(self, ltex):
        self.ltex = ltex
        self.archives = [Bsa(p) for p in sorted(glob.glob(os.path.join(DATA, "Skyrim - Textures*.bsa")))]
        self.src, self.quads = {}, {}

    def image(self, path):
        if path in self.src:
            return self.src[path]
        img = None
        if path:
            key = "textures\\" + path.replace("/", "\\")
            loose = os.path.join(DATA, key)
            raw = open(loose, "rb").read() if os.path.exists(loose) else \
                next((a.read(key) for a in self.archives if key in a.files), None)
            if raw:
                try:
                    if raw[84:88] == b"DX10":
                        f = struct.unpack_from("<I", raw, 128)[0]
                        if f in (72, 75, 78, 99): raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
                    img = Image.open(io.BytesIO(raw)).convert("RGB")
                except Exception as e:
                    print("texture failed", path, e)
        if img is not None:
            # The installed landscape texture mods are very dark (beach sand ~32/255): in Skyrim grass meshes cover most
            # of the ground. As physically based albedo that renders near-black, so lift dark ones toward ~78/255.
            lum = sum(ImageStat.Stat(img.resize((64, 64))).mean) / 3.0
            if 0 < lum < LIFT_TARGET:
                f = min(LIFT_MAX, LIFT_TARGET / lum)
                img = img.point(lambda v: min(255, int(v * f)))
        self.src[path] = img
        return img

    def quad(self, ltex_fid, Q, px):
        """Q x Q pixels of a landscape texture tiled so one repeat covers TILE_UNITS (px pixels = one cell)."""
        key = (ltex_fid, Q)
        if key in self.quads:
            return self.quads[key]
        img = self.image(self.ltex.get(ltex_fid)) if ltex_fid is not None else None
        if img is None:
            img = self.image(DEFAULT_TEX)
        if img is None:
            out = Image.new("RGB", (Q, Q), (90, 80, 60))
        else:
            rep = max(4, int(TILE_UNITS * px / 4096))
            t = img.resize((rep, rep), Image.LANCZOS if rep < img.size[0] else Image.BILINEAR)
            out = Image.new("RGB", (Q, Q))
            for y in range(0, Q, rep):
                for x in range(0, Q, rep):
                    out.paste(t, (x, y))
        self.quads[key] = out
        return out

    def cell(self, c, px):
        """px x px albedo of one LAND cell (image top = north), layers blended by their opacity, times vertex colour."""
        Q = px // 2
        canvas = Image.new("RGB", (px, px))
        for q in range(4):
            quad = self.quad(c["base"].get(q), Q, px).copy()
            for lq, _l, f, op in c["layers"]:
                if lq != q:
                    continue
                m = Image.new("L", (17, 17))
                m.putdata([int(max(0.0, min(1.0, op[(16 - r) * 17 + col])) * 255) for r in range(17) for col in range(17)])
                quad = Image.composite(self.quad(f, Q, px), quad, m.resize((Q, Q), Image.BILINEAR))
            canvas.paste(quad, ((q % 2) * Q, (1 - q // 2) * Q))
        if c["vc"]:
            vc = Image.frombytes("RGB", (33, 33), c["vc"]).transpose(Image.FLIP_TOP_BOTTOM).resize((px, px), Image.BILINEAR)
            canvas = ImageChops.multiply(canvas, vc)
        return canvas


# ---------------------------------------------------------------- meshes
class Obj:
    def __init__(self, path):
        self.path, self.f, self.n = path, open(path + ".tmp", "w"), 0
        self.mats = []
        self.f.write("mtllib %s.mtl\n" % os.path.basename(path)[:-4])

    def group(self, name):
        self.f.write("o %s\nusemtl %s\n" % (name, name)); self.mats.append(name)

    def vert(self, x, y, z, u, v, n):
        self.f.write("v %.1f %.1f %.1f\nvt %.5f %.5f\nvn %.4f %.4f %.4f\n" % (x, y, z, u, v, n[0], n[1], n[2]))
        self.n += 1
        return self.n

    def tri(self, a, b, c):
        self.f.write("f %d/%d/%d %d/%d/%d %d/%d/%d\n" % (a, a, a, b, b, b, c, c, c))

    def close(self):
        self.f.close()
        with open(self.path[:-4] + ".mtl", "w") as m:
            for name in self.mats:
                m.write("newmtl %s\nKd 0.8 0.8 0.8\n" % name)
        os.replace(self.path + ".tmp", self.path)


def emit_cells(obj, H, cells, step, uv_of, skirt_edge):
    """Grid of every cells' vertices (every `step`th LAND vertex) plus skirts on edges where skirt_edge(gx, gy, side)."""
    n = 32 // step + 1
    for gx, gy in cells:
        idx = {}
        for j in range(n):
            for i in range(n):
                X, Y = gx * 32 + i * step, gy * 32 + j * step
                idx[i, j] = obj.vert(X * 128.0, Y * 128.0, H.at(X, Y), *uv_of(X, Y), H.normal(X, Y, step))
        for j in range(n - 1):
            for i in range(n - 1):
                a, b, c, d = idx[i, j], idx[i + 1, j], idx[i, j + 1], idx[i + 1, j + 1]
                obj.tri(a, b, d); obj.tri(a, d, c)
        for side, (dx, dy) in (("w", (-1, 0)), ("e", (1, 0)), ("s", (0, -1)), ("n", (0, 1))):
            if not skirt_edge(gx + dx, gy + dy):
                continue
            line = [(0, k) for k in range(n)] if side == "w" else [(n - 1, k) for k in range(n)] if side == "e" else \
                   [(k, 0) for k in range(n)] if side == "s" else [(k, n - 1) for k in range(n)]
            low = []
            for i, j in line:
                X, Y = gx * 32 + i * step, gy * 32 + j * step
                low.append(obj.vert(X * 128.0, Y * 128.0, H.at(X, Y) - SKIRT, *uv_of(X, Y), H.normal(X, Y, step)))
            for k in range(n - 1):
                a, b, c, d = idx[line[k]], idx[line[k + 1]], low[k], low[k + 1]
                obj.tri(a, c, d); obj.tri(a, d, b)                        # the terrain materials are two-sided


def blender(obj_dir):
    r = subprocess.run([BLENDER, "-b", "-P", os.path.join(ROOT, "tools", "blender_export.py"), "--", obj_dir, EXPORT],
                       capture_output=True, text=True)
    if r.returncode:
        print("blender failed:", r.stderr[-2000:])


def build_low(land, baker):
    os.makedirs(LOW_OBJ, exist_ok=True)
    skip = whiterun_cells()
    H = Heights(land["cells"], skip)
    groups = {}
    for gx, gy in land["cells"]:
        if (gx, gy) not in skip:
            groups.setdefault((gx // GROUP, gy // GROUP), []).append((gx, gy))
    for (GX, GY), cells in sorted(groups.items()):
        name = "tlo_%d_%d" % (GX, GY)
        atlas = os.path.join(TEX, "tatl_%d_%d.png" % (GX, GY))
        if not os.path.exists(atlas):
            img = Image.new("RGB", (GROUP * FAR_PX, GROUP * FAR_PX), (96, 90, 74))
            for gx, gy in cells:
                img.paste(baker.cell(land["cells"][(gx, gy)], FAR_PX),
                          ((gx - GX * GROUP) * FAR_PX, (GROUP - 1 - (gy - GY * GROUP)) * FAR_PX))
            img.save(atlas, compress_level=1)
        path = os.path.join(LOW_OBJ, name + ".obj")
        if os.path.exists(path):
            continue
        obj = Obj(path)
        by_chunk = {}
        for gx, gy in cells:
            by_chunk.setdefault((gx // CHUNK, gy // CHUNK), []).append((gx, gy))
        for (cx, cy), cc in sorted(by_chunk.items()):
            obj.group("tlo_%d_%d" % (cx, cy))
            emit_cells(obj, H, sorted(cc), 4,
                       lambda X, Y: ((X - GX * GROUP * 32) / (GROUP * 32.0), (Y - GY * GROUP * 32) / (GROUP * 32.0)),
                       lambda nx, ny: not H.has(nx, ny))
        obj.close()
        print("low", name, len(cells), "cells")
    blender(LOW_OBJ)
    with open(os.path.join(OUT, "terrain_low.txt"), "w") as f:
        f.write("\n".join("tlo_%d_%d" % k for k in sorted(groups)) + "\n")
    print("low-res groups:", len(groups))


def build_chunk(land, baker, cx, cy, skip=None):
    """Full-res mesh + 4096 px texture of one 4x4-cell chunk. Returns the asset name or None (no LAND there)."""
    skip = whiterun_cells() if skip is None else skip
    H = Heights(land["cells"], skip)
    cells = [(cx * CHUNK + i, cy * CHUNK + j) for i in range(CHUNK) for j in range(CHUNK) if H.has(cx * CHUNK + i, cy * CHUNK + j)]
    if not cells:
        return None
    name, key = "tch_%d_%d" % (cx, cy), "tdet_%d_%d" % (cx, cy)
    png = os.path.join(TEX, key + ".png")
    if not os.path.exists(png):
        img = Image.new("RGB", (CHUNK * NEAR_PX, CHUNK * NEAR_PX), (96, 90, 74))
        for gx, gy in cells:
            img.paste(baker.cell(land["cells"][(gx, gy)], NEAR_PX),
                      ((gx - cx * CHUNK) * NEAR_PX, (CHUNK - 1 - (gy - cy * CHUNK)) * NEAR_PX))
        img.save(png, compress_level=1)
    os.makedirs(CHUNK_OBJ, exist_ok=True)
    path = os.path.join(CHUNK_OBJ, name + ".obj")
    if not os.path.exists(path):
        obj = Obj(path)
        obj.group(key)
        inside = set(cells)
        emit_cells(obj, H, cells, 1,
                   lambda X, Y: ((X - cx * CHUNK * 32) / (CHUNK * 32.0), (Y - cy * CHUNK * 32) / (CHUNK * 32.0)),
                   lambda nx, ny: (nx, ny) not in inside)
        obj.close()
    return name


# ---------------------------------------------------------------- water
def build_water(land):
    """Strips of visible water for every Tamriel cell with the 'has water' flag; Whiterun's water_wide.csv cells are left to
    the existing CellWater actor (it has per-strip flow)."""
    have = set()
    p = os.path.join(AREA, "water_wide.csv")
    if os.path.exists(p):
        for line in open(p).read().split():
            gx, gy, _ = line.split(","); have.add((int(gx), int(gy)))
    runs = full = 0
    with open(os.path.join(OUT, "water_quads.csv"), "w") as f:
        for (gx, gy), h in sorted(land["water"].items()):
            if (gx, gy) in have:
                continue
            h = land["default_water"] if h is None else h
            c = land["cells"].get((gx, gy))
            if c is None:
                f.write("%d,%d,0,%.1f\n" % (gx * 4096, gy * 4096, h)); full += 1; continue
            hm = c["h"]
            wet = [[min(hm[r * 33 + k], hm[r * 33 + k + 1], hm[(r + 1) * 33 + k], hm[(r + 1) * 33 + k + 1]) < h
                    for k in range(32)] for r in range(32)]
            if not any(any(r) for r in wet):
                continue
            grow = [[any(wet[rr][kk] for rr in range(max(0, r - 1), min(32, r + 2)) for kk in range(max(0, k - 1), min(32, k + 2)))
                     for k in range(32)] for r in range(32)]
            if all(all(r) for r in grow):
                f.write("%d,%d,0,%.1f\n" % (gx * 4096, gy * 4096, h)); full += 1; continue
            for r in range(32):
                k = 0
                while k < 32:
                    if not grow[r][k]:
                        k += 1; continue
                    s = k
                    while k < 32 and grow[r][k]: k += 1
                    f.write("%d,%d,%d,%.1f\n" % (gx * 4096 + s * 128, gy * 4096 + r * 128, k - s, h)); runs += 1
    print("Tamriel water: %d strips, %d full cells" % (runs, full))


# ---------------------------------------------------------------- service
def serve():
    land = load_land()
    baker = Baker(land["ltex"])
    if not os.path.exists(os.path.join(OUT, "terrain_low.txt")):
        build_low(land, baker)
    if not os.path.exists(os.path.join(OUT, "water_quads.csv")):
        build_water(land)
    for p in (REQ, READY):
        if not os.path.exists(p): open(p, "w").close()
    done = set(open(READY).read().split())
    skip = whiterun_cells()
    print("terrain service running; watching", REQ)
    while True:
        want = [n for n in dict.fromkeys(open(REQ).read().split()) if n not in done]
        if want:
            names = []
            for n in want[:6]:                                           # nearest first: the editor lists them in that order
                _, cx, cy = n.split("_")
                t = time.time()
                out = build_chunk(land, baker, int(cx), int(cy), skip)
                names.append((n, out))
                print("chunk", n, "%.1fs" % (time.time() - t), "" if out else "(no land)")
            blender(CHUNK_OBJ)
            with open(READY, "a") as f:
                for n, out in names:
                    ok = out is None or os.path.exists(os.path.join(EXPORT, n + ".fbx"))
                    f.write(("%s\n" % n) if ok else ("FAILED_%s\n" % n))
                    done.add(n)
            if len(baker.quads) > 600:
                baker.quads.clear()
        time.sleep(1.0)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--land" in sys.argv:
        parse_land(); return
    if "--low" in sys.argv:
        land = load_land(); build_low(land, Baker(land["ltex"])); build_water(land); return
    if "--water" in sys.argv:
        build_water(load_land()); return
    if "--chunk" in sys.argv:
        i = sys.argv.index("--chunk")
        land = load_land()
        print(build_chunk(land, Baker(land["ltex"]), int(sys.argv[i + 1]), int(sys.argv[i + 2])))
        blender(CHUNK_OBJ); return
    if "--serve" in sys.argv:
        serve(); return
    print(__doc__)


if __name__ == "__main__":
    main()
