"""Minimal Skyrim SE (BSA v105) reader. Usage: python -I bsa.py <archive> list <substring> | extract <outdir> <substring>"""
import struct, sys, os
import lz4.frame


class Bsa:
    def __init__(self, path):
        self.f = open(path, "rb")
        h = self.f.read(36)
        magic, ver, off, flags, nfold, nfile, tfn, tfl, ftype = struct.unpack("<4sIIIIIIIH", h[:34])
        assert magic == b"BSA\0" and ver == 105, (magic, ver)
        self.flags = flags
        self.compressed_default = bool(flags & 0x4)
        self.embed_names = bool(flags & 0x100)
        folders = []
        self.f.seek(36)
        for _ in range(nfold):
            _hash, count, _pad, foff = struct.unpack("<QIIQ", self.f.read(24))
            folders.append((count, foff))
        self.files = {}  # lowercase path -> (size, offset, compressed)
        for count, _ in folders:
            nlen = self.f.read(1)[0]
            folder = self.f.read(nlen).rstrip(b"\0").decode("cp1252")
            recs = [struct.unpack("<QII", self.f.read(16)) for _ in range(count)]
            self.files[folder.lower()] = recs  # temporarily
        # file name block follows all folder blocks
        names = []
        total = sum(len(v) for v in self.files.values())
        buf = b""
        while len(names) < total:
            c = self.f.read(1)
            if c == b"\0":
                names.append(buf.decode("cp1252")); buf = b""
            else:
                buf += c
        out, i = {}, 0
        for folder, recs in self.files.items():
            for _h, size, offset in recs:
                comp = self.compressed_default ^ bool(size & 0x40000000)
                out[(folder + "\\" + names[i]).lower()] = (size & 0x3FFFFFFF, offset, comp)
                i += 1
        self.files = out

    def read(self, path):
        size, offset, comp = self.files[path.lower()]
        self.f.seek(offset)
        if self.embed_names:
            n = self.f.read(1)[0]; self.f.read(n)
            size -= n + 1
        if comp:
            (orig,) = struct.unpack("<I", self.f.read(4))
            return lz4.frame.decompress(self.f.read(size - 4))
        return self.f.read(size)


if __name__ == "__main__":
    b = Bsa(sys.argv[1])
    sub = sys.argv[-1].lower()
    if sys.argv[2] == "list":
        for p in sorted(b.files):
            if sub in p:
                print(p, b.files[p][0])
    else:
        outdir = sys.argv[3]
        for p in sorted(b.files):
            if sub in p:
                dst = os.path.join(outdir, p)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(b.read(p))
                print("wrote", dst)
