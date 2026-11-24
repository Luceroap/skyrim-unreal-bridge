"""Find placed references (REFR) in Skyrim.esm whose base STAT uses one of the given NIFs.
Usage: python -I esm_refs.py <Skyrim.esm> <out.json> <nif1> <nif2> ...  (nif = lowercase path tail, e.g. wrhouse02.nif)
Output: [{"nif":..., "pos":[x,y,z], "rot":[rx,ry,rz], "scale":s, "cell_group":...}]"""
import struct, sys, zlib, json

path, out = sys.argv[1], sys.argv[2]
wanted = [w.lower() for w in sys.argv[3:]]
data = open(path, "rb").read()
stat_nif = {}   # formid -> nif tail
refs = []       # (base formid, pos, rot, scale)


def sub_records(buf):
    p = 0
    ext = None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None:
            sz = ext; ext = None
        yield t, buf[p:p + sz]
        p += sz


def walk(start, end):
    p = start
    while p < end:
        t = data[p:p + 4]
        sz, = struct.unpack_from("<I", data, p + 4)
        if t == b"GRUP":
            walk(p + 24, p + sz)
            p += sz
            continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        body = data[p + 24:p + 24 + sz]
        if t in (b"STAT", b"REFR"):
            if flags & 0x40000:  # compressed
                body = zlib.decompress(body[4:])
            if t == b"STAT":
                for st, sd in sub_records(body):
                    if st == b"MODL":
                        n = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
                        for w in wanted:
                            if n.endswith(w):
                                stat_nif[fid] = w
            else:
                base = pos = scale = None
                for st, sd in sub_records(body):
                    if st == b"NAME": base, = struct.unpack("<I", sd[:4])
                    elif st == b"DATA" and len(sd) >= 24: pos = struct.unpack("<6f", sd[:24])
                    elif st == b"XSCL": scale, = struct.unpack("<f", sd[:4])
                if base is not None and pos:
                    refs.append((base, pos, scale or 1.0, flags))
        p += 24 + sz


walk(0, len(data))
res = []
for base, pos, scale, flags in refs:
    if base in stat_nif and not (flags & 0x20):  # skip deleted
        res.append({"nif": stat_nif[base], "pos": pos[:3], "rot": pos[3:], "scale": scale})
json.dump(res, open(out, "w"))
print(len(stat_nif), "STATs matched,", len(res), "placed refs")
