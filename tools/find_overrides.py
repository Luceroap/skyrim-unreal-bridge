"""Which active plugins override given Skyrim.esm references, and how (deleted / persistent / disabled / moved).
Usage: python -I find_overrides.py <ids.json: {"0001abcd": "model", ...}>"""
import collections, json, os, struct, sys, zlib

DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
PLUGINS = os.path.join(os.environ["LOCALAPPDATA"], "Skyrim Special Edition", "plugins.txt")
want = {int(k, 16): v for k, v in json.load(open(sys.argv[1])).items()}
GROUP_KIND = {8: "persistent", 9: "temporary", 10: "distant"}

order = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
order += [l[1:].strip() for l in open(PLUGINS, encoding="utf-8", errors="replace") if l.startswith("*")]


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def scan(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path): return None
    data = open(path, "rb").read()
    hsz, = struct.unpack_from("<I", data, 4)
    masters = [sd.split(b"\0")[0].decode("cp1252").lower() for st, sd in subs(data[24:24 + hsz]) if st == b"MAST"]
    hits = []

    def walk(s, e, grp):
        p = s
        while p < e:
            t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
            if t == b"GRUP":
                gtype, = struct.unpack_from("<I", data, p + 12)
                walk(p + 24, p + sz, GROUP_KIND.get(gtype, grp)); p += sz; continue
            flags, fid = struct.unpack_from("<II", data, p + 8)
            if t == b"REFR":
                mi = fid >> 24
                if mi < len(masters) and masters[mi] == "skyrim.esm" and (fid & 0xFFFFFF) in want:
                    body = data[p + 24:p + 24 + sz]
                    pos = None; parent = None
                    if not flags & 0x20:
                        if flags & 0x40000: body = zlib.decompress(body[4:])
                        for st, sd in subs(body):
                            if st == b"DATA" and len(sd) >= 12: pos = struct.unpack("<3f", sd[:12])
                            if st == b"XESP": parent = struct.unpack("<II", sd[:8])
                    hits.append((fid & 0xFFFFFF, flags, grp, pos, parent))
            p += 24 + sz
    walk(24 + hsz, len(data), None)
    return hits


summary = collections.Counter()
last = {}
for name in order:
    hits = scan(name)
    if not hits or name == "Skyrim.esm": continue
    kinds = collections.Counter()
    for fid, flags, grp, pos, parent in hits:
        k = []
        if flags & 0x20: k.append("deleted")
        if flags & 0x800: k.append("initially-disabled")
        k.append(grp or "?")
        if parent: k.append("enable-parent")
        kinds[" ".join(k)] += 1
        last[fid] = (name, " ".join(k))
    print("%-60s %s" % (name, dict(kinds)))
print("\nwinning override per ref:")
win = collections.Counter((n, k) for n, k in last.values())
for (n, k), c in win.most_common(): print("  %3d  %s  [%s]" % (c, n, k))
print("refs with no override:", len(set(want) - set(last)))
