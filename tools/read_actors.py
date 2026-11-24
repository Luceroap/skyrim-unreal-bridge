"""Print a summary of the plugin's actor pose stream."""
import ctypes, ctypes.wintypes as wt, struct
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_actors_v1")
if not h:
    raise SystemExit("actors mapping not found (plugin not loaded or an old plugin version)")
p = k.MapViewOfFile(h, 4, 0, 0, 0)
MAXB, NAMELEN, MAXA, MAXBONES = 512, 40, 96, 320
magic, ver, seq, tick, nA, nN, _, _ = struct.unpack("<8I", ctypes.string_at(p, 32))
print("magic %08x version %d seq %d tick %d actors %d bone names %d" % (magic, ver, seq, tick, nA, nN))
names = [ctypes.string_at(p + 32 + i * NAMELEN, NAMELEN).split(b"\0")[0].decode("latin1") for i in range(nN)]
APOSE = 4 * 4 + 12 + 4 + 4 + 96 + 48 + MAXBONES * 32
off = 32 + MAXB * NAMELEN
for i in range(min(nA, 8)):
    b = ctypes.string_at(p + off + i * APOSE, APOSE)
    id_, base, fl, nb = struct.unpack_from("<4I", b, 0)
    pos = struct.unpack_from("<3f", b, 16)
    skel = b[36 + 4 + 4 - 4 + 4:][:0]  # placeholder (offsets below)
    yaw, scale = struct.unpack_from("<2f", b, 28)
    skel = b[36:36 + 96].split(b"\0")[0].decode("latin1")
    nm = b[132:132 + 48].split(b"\0")[0].decode("latin1")
    print("actor %08x base %08x flags %d bones %d pos %.0f,%.0f,%.0f yaw %.2f '%s' skel=%s" % (id_, base, fl, nb, *pos, yaw, nm, skel))
    if i == 0 and nb:
        for j in range(min(nb, 4)):
            nn, par, x, y, z, qx, qy, qz, qw = struct.unpack_from("<Hh3f4f", b, 180 + j * 32)
            print("   bone %-22s parent %3d pos %.1f,%.1f,%.1f quat %.2f,%.2f,%.2f,%.2f" % (names[nn], par, x, y, z, qx, qy, qz, qw))
