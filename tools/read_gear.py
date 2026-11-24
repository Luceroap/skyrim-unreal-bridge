"""Print the plugin's worn-gear stream (armor addon models per actor)."""
import ctypes, ctypes.wintypes as wt, struct
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_gear_v1")
if not h:
    raise SystemExit("gear mapping not found (plugin not loaded or an old plugin version)")
p = k.MapViewOfFile(h, 4, 0, 0, 0)
magic, ver, seq, tick, nA = struct.unpack("<5I", ctypes.string_at(p, 20))
print("magic %08x version %d seq %d tick %d actors %d" % (magic, ver, seq, tick, nA))
MAXG, PLEN = 24, 112
SZ = 32 + MAXG * PLEN + 2 * PLEN + 24 * 200
for i in range(min(nA, 12)):
    b = ctypes.string_at(p + 32 + i * SZ, SZ)
    id_, base, n, fl, face, wfl = struct.unpack_from("<6I", b, 0)
    paths = [b[32 + j * PLEN:32 + (j + 1) * PLEN].split(b"\0")[0].decode("latin1") for j in range(n)]
    print("actor %08x base %08x flags %d gear %d: %s" % (id_, base, fl, n, paths[:4]))

    wp = [b[32 + MAXG * PLEN + h * PLEN:32 + MAXG * PLEN + (h + 1) * PLEN].split(b'\0')[0].decode('latin1') for h in range(2)]
    print('   face %08x weaponFlags %d weapons %s' % (face, wfl, wp))

