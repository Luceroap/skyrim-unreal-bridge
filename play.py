"""One-click launcher: Skyrim + the Unreal remaster view, in the right order, with the right focus.
    python play.py               start everything (re-uses whatever is already running)
    python play.py --stop        close the editor and Skyrim cleanly
Order: clean up stale helpers -> start Skyrim (autoloads your latest save) AND the Unreal editor at the same time ->
wait until both are live -> set clear morning (unless --keep-weather) -> put Unreal over Skyrim -> give Skyrim the keyboard focus."""
import ctypes, ctypes.wintypes as wt, glob, os, re, struct, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
UE = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
PROJ = os.path.join(ROOT, "unreal", "SkyBridge")
LOGS = os.path.join(PROJ, "Saved", "Logs")
PLUGINS = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\SKSE\Plugins"
PY = sys.executable
DETACH = 0x00000008 | 0x00000200 | 0x01000000        # DETACHED_PROCESS | NEW_PROCESS_GROUP | BREAKAWAY_FROM_JOB: survives this window closing
t0 = time.time()


def say(msg):
    print("[%3ds] %s" % (time.time() - t0, msg), flush=True)


def running(exe):
    return exe.lower() in subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe], capture_output=True, text=True).stdout.lower()


def kill(*names):
    for n in names:
        subprocess.run(["taskkill", "/F", "/IM", n], capture_output=True)


def kill_watchers():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'remaster_watch' -and $_.Name -match 'python' } | % ProcessId"],
                         capture_output=True, text=True).stdout
    for pid in out.split():
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)


def start_services():
    """Background converters: models (asset_service) and Tamriel terrain chunks (tamriel_terrain --serve)."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.Name -match 'python' } | % CommandLine"],
                         capture_output=True, text=True, creationflags=0x08000000).stdout
    for script, args in (("asset_service.py", []), ("tamriel_terrain.py", ["--serve"])):
        if script not in out:
            subprocess.Popen([PY, "-I", os.path.join(ROOT, "tools", script)] + args, cwd=ROOT, creationflags=DETACH | 0x08000000)
            say("started background converter " + script)


def free_gb():
    class MS(ctypes.Structure):
        _fields_ = [("l", wt.DWORD), ("load", wt.DWORD), ("tp", ctypes.c_uint64), ("ap", ctypes.c_uint64), ("tpf", ctypes.c_uint64),
                    ("apf", ctypes.c_uint64), ("tv", ctypes.c_uint64), ("av", ctypes.c_uint64), ("ae", ctypes.c_uint64)]
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ap / 2**30


def skyrim_in_world():
    k = ctypes.windll.kernel32
    k.OpenFileMappingW.restype = ctypes.c_void_p; k.MapViewOfFile.restype = ctypes.c_void_p
    k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
    h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_actors_v1")
    if not h:
        return False
    p = k.MapViewOfFile(h, 4, 0, 0, 0)
    return struct.unpack("<8I", ctypes.string_at(p, 32))[4] > 0


def editor_live(since):
    logs = [f for f in glob.glob(os.path.join(LOGS, "SkyBridge*.log")) if os.path.getmtime(f) > since]
    if not logs:
        return False
    tail = open(max(logs, key=os.path.getmtime), encoding="utf-8", errors="replace").read()[-30000:]
    return bool(re.search(r"\[SkyBridgeLive\] alive: [1-9]\d* actors", tail))


def focus_skyrim():
    u = ctypes.windll.user32
    pid_out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq SkyrimSE.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    m = re.search(r'"SkyrimSE.exe","(\d+)"', pid_out)
    if not m:
        return
    want = int(m.group(1)); found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        p = wt.DWORD(); u.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == want and u.IsWindowVisible(hwnd) and u.GetWindowTextLengthW(hwnd) > 0:
            found.append(hwnd)
        return True
    u.EnumWindows(cb, 0)
    if found:
        u.keybd_event(0x12, 0, 0, 0)                      # a tap of Alt lets this process take the foreground
        u.ShowWindow(found[0], 9); u.SetForegroundWindow(found[0])
        u.keybd_event(0x12, 0, 2, 0)


def stop():
    say("closing the editor, then Skyrim")
    kill_watchers(); kill("UnrealEditor.exe"); time.sleep(3); kill("SkyrimSE.exe"); say("done")


def main():
    if "--stop" in sys.argv:
        stop(); return
    say("Skyrim + Unreal launcher")
    gb = free_gb()
    if gb < 8:
        say("WARNING: only %.1f GB of memory free. Close other programs (browsers, games) first or the game will stutter." % gb)
    kill_watchers()
    start_services()
    editors = subprocess.run(["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe", "/NH"], capture_output=True, text=True).stdout.lower().count("unrealeditor.exe")
    if editors > 1:                                         # a stray duplicate eats ~10 GB: keep none, start one clean below
        say("closing %d duplicate editors" % editors); kill("UnrealEditor.exe"); time.sleep(3)
    sky_new = not running("SkyrimSE.exe")
    if sky_new:
        say("starting Skyrim (it loads your latest save by itself)")
        subprocess.Popen([PY, os.path.join(ROOT, "start_bridge.py"), "--no-overlay", "--skyrim-only"], cwd=ROOT, creationflags=DETACH)
    else:
        say("Skyrim is already running")
    started = time.time()
    if not running("UnrealEditor.exe"):
        say("starting the Unreal editor at the same time (about 2-3 minutes)")
        subprocess.Popen([UE, os.path.join(PROJ, "SkyBridge.uproject"), "-windowed", "-ResX=1600", "-ResY=900",
                          "-ExecCmds=r.Streaming.PoolSize 3000"], cwd=PROJ, creationflags=DETACH)
    else:
        started = 0
        say("the Unreal editor is already running")
    sky_ok = ed_ok = False
    while time.time() - t0 < 600 and not (sky_ok and ed_ok):
        time.sleep(4)
        if not sky_ok and skyrim_in_world():
            sky_ok = True; say("Skyrim is in the world")
            if "--no-autobuild" not in sys.argv:                  # builds characters/creatures (dragons, wolves, ...) as they appear near you
                out = subprocess.run(["powershell", "-NoProfile", "-Command",
                                      "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'npc_autobuild' } | % ProcessId"], capture_output=True, text=True).stdout.strip()
                if not out:
                    subprocess.Popen([PY, "-I", os.path.join(ROOT, "tools", "npc_autobuild.py")], cwd=ROOT, creationflags=DETACH | 0x08000000)
                    say("background builder for new characters/creatures started")
            if "--keep-weather" not in sys.argv:
                with open(os.path.join(PLUGINS, "SkyrimUnrealBridge.sky"), "w") as f:
                    f.write("hour 8\nweather SkyrimClearTU\n")
        if not ed_ok and editor_live(started):
            ed_ok = True; say("the Unreal editor is live")
    if not (sky_ok and ed_ok):
        say("timed out waiting (Skyrim in world: %s, editor live: %s); see README" % (sky_ok, ed_ok)); return
    time.sleep(20)                                          # let the first characters/assets finish importing
    say("putting Unreal over Skyrim")
    subprocess.run([PY, os.path.join(ROOT, "start_bridge.py"), "--remaster"], cwd=ROOT, creationflags=0x08000000)
    time.sleep(2)
    focus_skyrim()
    say("READY. Skyrim has the keyboard focus: just play. (python play.py --stop closes everything)")
    time.sleep(6)


if __name__ == "__main__":
    main()
