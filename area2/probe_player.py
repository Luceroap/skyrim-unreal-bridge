"""Run with normal python: Skyrim fps, game-time rate vs real time, player speed (slow-motion check)."""
import ctypes, struct, time, math
k32 = ctypes.windll.kernel32
k32.OpenFileMappingW.restype = ctypes.c_void_p
k32.MapViewOfFile.restype = ctypes.c_void_p
k32.MapViewOfFile.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_size_t]
p = k32.MapViewOfFile(k32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1"), 4, 0, 0, 0)

def rd():
    b = ctypes.string_at(p, 64)
    frame, = struct.unpack_from("<I", b, 12)
    pos = struct.unpack_from("<3f", b, 16)
    hb = ctypes.string_at(p + 92, 8)
    hour, days = struct.unpack("<2f", hb)
    return time.time(), frame, pos, hour, days

samples = []
for _ in range(60):
    samples.append(rd()); time.sleep(0.1)
t0, f0, p0, h0, d0 = samples[0]; t1, f1, p1, h1, d1 = samples[-1]
dt = t1 - t0
game_s = ((d1 - d0) * 24 + 0) * 3600 if abs(d1 - d0) > 1e-6 else (h1 - h0) * 3600
print("real %.1f s | skyrim frames %d -> %.1f fps | game time %.1f s -> timescale %.1f (normal 20)" % (dt, f1 - f0, (f1 - f0) / dt, game_s, game_s / dt))
speeds = [math.dist(a[2][:2], b[2][:2]) / (b[0] - a[0]) for a, b in zip(samples, samples[1:])]
print("player speed units/s: max %.0f, median %.0f  (Skyrim: walk ~80, run ~250-300, sprint ~400; over-encumbered walk ~40-80)" %
      (max(speeds), sorted(speeds)[len(speeds) // 2]))
