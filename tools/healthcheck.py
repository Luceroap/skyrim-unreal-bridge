"""One-screen state check for agents:  python tools/healthcheck.py
processes, memory (free commit is the number that matters), GPU, disk, shared-memory streams, editor heartbeat, Ollama, last crashes."""
import ctypes, ctypes.wintypes as wt, glob, os, re, struct, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, "unreal", "SkyBridge", "Saved", "Logs")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout.strip()


class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in
               ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]


m = MEM(); m.dwLength = ctypes.sizeof(MEM)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
g = 2 ** 30
free_commit = m.ullAvailPageFile / g
print("MEMORY  free RAM %.1f / %.1f GB   free commit %.1f / %.1f GB  %s" % (m.ullAvailPhys / g, m.ullTotalPhys / g, free_commit, m.ullTotalPageFile / g,
      "<-- DANGER (<10)" if free_commit < 10 else ("low (<25)" if free_commit < 25 else "ok")))
for d in ("C:\\", "D:\\"):
    try:
        import shutil
        u = shutil.disk_usage(d); print("DISK    %s free %.0f GB of %.0f" % (d, u.free / g, u.total / g))
    except Exception:
        pass
print("GPU     " + (sh("nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader") or "n/a"))
for name in ("SkyrimSE.exe", "UnrealEditor.exe", "llama-server.exe", "ollama.exe", "CrashReportClientEditor.exe"):
    out = sh('tasklist /FI "IMAGENAME eq %s" /FO CSV /NH' % name)
    rows = [l for l in out.splitlines() if name.lower() in l.lower()]
    mem = ", ".join(l.split('","')[-1].strip('"') for l in rows)
    print("PROC    %-28s %s%s" % (name, "running x%d (%s)" % (len(rows), mem) if rows else "not running", "   <-- one editor only!" if name == "UnrealEditor.exe" and len(rows) > 1 else ""))
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p; k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
for n in ("v1", "world_v1", "actors_v1", "gear_v1"):
    h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_" + n)
    if not h:
        print("STREAM  %-10s missing (Skyrim/plugin not running)" % n); continue
    p = k.MapViewOfFile(h, 4, 0, 0, 0)
    hd = struct.unpack("<8I", ctypes.string_at(p, 32))
    note = {"v1": "camera packet; hd[3]>0 = in a world", "world_v1": "refs=%d models=%d" % (hd[4], hd[5]), "actors_v1": "actors=%d (in world if >0)" % hd[4], "gear_v1": "actors=%d" % hd[4]}[n]
    print("STREAM  %-10s ok  %s" % (n, note))
logs = sorted(glob.glob(os.path.join(LOGS, "SkyBridge*.log")), key=os.path.getmtime)
if logs:
    tail = open(logs[-1], encoding="utf-8", errors="replace").read()[-40000:]
    beats = re.findall(r"\[SkyBridgeLive\] alive: (\d+) actors, (\d+) queued, (\d+) lights", tail)
    age = time.time() - os.path.getmtime(logs[-1])
    print("EDITOR  heartbeat: %s (log updated %.0f s ago)" % (("%s actors, %s queued, %s lights" % beats[-1]) if beats else "none yet", age))
    bad = re.findall(r"(Assertion failed[^\n]{0,80}|Fatal error[^\n]{0,80}|Unhandled Exception[^\n]{0,60})", tail)
    if bad:
        print("EDITOR  last error: " + bad[-1])
sk = glob.glob(os.path.expandvars(r"%USERPROFILE%\OneDrive\Documents\My Games\Skyrim Special Edition\SKSE\crash-*.log"))
if sk:
    last = max(sk, key=os.path.getmtime); print("SKYRIM  last crash log: %s (%s)" % (os.path.basename(last), time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(last)))))
print("OLLAMA  " + (sh('"%s" list' % os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")).replace("\n", " | ")[:160] or "not answering"))
print("QUEUE   " + sh('python "%s" --status' % os.path.join(ROOT, "tools", "run_local_queue.py")))
