"""Background watchdog: relaunches the Unreal editor (remaster view) after it CRASHES while Skyrim is being played.
    pythonw tools/editor_watchdog.py           run the loop (single instance)
    python  tools/editor_watchdog.py --start   start it detached + hidden (WMI Win32_Process.Create), survives the shell
    python  tools/editor_watchdog.py --stop    stop it
    python  tools/editor_watchdog.py --once [--act]   one check, print the decision (acts only with --act)
    python  tools/editor_watchdog.py --test    crash-detection self test on tonight's logs (launches nothing)
Pause: create area2/no_watchdog.txt. Log: area2/editor_watchdog.log.
Relaunch only when ALL hold: Skyrim runs and is in the world, no UnrealEditor.exe (nor UnrealEditor-Cmd / a C++ build)
for >= 30 s, the last editor session ended in a real crash (Critical error / RequestExit(1 / non-ensure crash report),
and fewer than 3 relaunches in the last 30 minutes. A clean exit (QUIT_EDITOR, window closed) or a killed editor
(log just stops: an agent/play.py is restarting it) is left alone. Never kills anything.
Nothing here opens a console window: processes are listed with Toolhelp32, children get CREATE_NO_WINDOW."""
import ctypes, ctypes.wintypes as wt, glob, json, os, re, struct, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import play                                         # module level is constants only (no side effects on import)

AREA = os.path.join(ROOT, "area2")
LOG = os.path.join(AREA, "editor_watchdog.log")
STATE = os.path.join(AREA, "editor_watchdog_state.json")
PAUSE = os.path.join(AREA, "no_watchdog.txt")
CRASHES = os.path.join(play.PROJ, "Saved", "Crashes")
MUTEX = "Local\\SkyBridgeEditorWatchdog"
HIDDEN = 0x08000000
DETACH = play.DETACH
POLL, GRACE = 5, 30
MAX_RELAUNCH, WINDOW = 3, 1800
MIN_FREE_GB = 6
BUILD_EXES = {"unrealbuildtool.exe", "msbuild.exe", "cl.exe", "link.exe", "unrealeditor-cmd.exe", "build.bat"}
PYDIR = os.path.dirname(sys.executable)
PYTHON = os.path.join(PYDIR, "python.exe") if os.path.exists(os.path.join(PYDIR, "python.exe")) else sys.executable
PYTHONW = os.path.join(PYDIR, "pythonw.exe") if os.path.exists(os.path.join(PYDIR, "pythonw.exe")) else sys.executable
k32, user32 = ctypes.windll.kernel32, ctypes.windll.user32
k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
k32.CreateMutexW.restype = ctypes.c_void_p
k32.OpenMutexW.restype = ctypes.c_void_p
k32.OpenFileMappingW.restype = ctypes.c_void_p
k32.MapViewOfFile.restype = ctypes.c_void_p
k32.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
k32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
k32.CloseHandle.argtypes = [ctypes.c_void_p]


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    if sys.stdout:                                  # None under pythonw
        print(line, flush=True)
    try:
        if os.path.exists(LOG) and os.path.getsize(LOG) > 1 << 20:
            os.replace(LOG, LOG + ".1")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


class PE32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD), ("szExeFile", ctypes.c_wchar * 260)]


def processes():
    """{exe name lower: [pids]} without spawning tasklist."""
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    out = {}
    if not snap or snap == ctypes.c_void_p(-1).value:
        return out
    e = PE32(); e.dwSize = ctypes.sizeof(PE32)
    ok = k32.Process32FirstW(ctypes.c_void_p(snap), ctypes.byref(e))
    while ok:
        out.setdefault(e.szExeFile.lower(), []).append(e.th32ProcessID)
        ok = k32.Process32NextW(ctypes.c_void_p(snap), ctypes.byref(e))
    k32.CloseHandle(snap)
    return out


def skyrim_in_world():
    """play.skyrim_in_world without leaking the mapping handle (this runs every 5 s for hours)."""
    h = k32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_actors_v1")
    if not h:
        return False
    try:
        p = k32.MapViewOfFile(h, 4, 0, 0, 32)
        if not p:
            return False
        n = struct.unpack("<8I", ctypes.string_at(p, 32))[4]
        k32.UnmapViewOfFile(p)
        return n > 0
    finally:
        k32.CloseHandle(h)


def focus_skyrim():
    want = set(processes().get("skyrimse.exe", []))
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        p = wt.DWORD(); user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value in want and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    if found:
        user32.keybd_event(0x12, 0, 0, 0)
        user32.ShowWindow(found[0], 9); user32.SetForegroundWindow(found[0])
        user32.keybd_event(0x12, 0, 2, 0)


# ---------------------------------------------------------------- crash detection

def last_session_log():
    """Newest editor log. While no editor runs this is the session that ended last (UE renames it to *-backup-* only
    when the next editor starts, keeping the mtime)."""
    logs = glob.glob(os.path.join(play.LOGS, "SkyBridge*.log"))
    return max(logs, key=os.path.getmtime) if logs else None


def crash_reports(near, slack=120):
    """Non-ensure crash folders written within `slack` s of `near`: [(folder, CrashType, ErrorMessage)]."""
    out = []
    for d in glob.glob(os.path.join(CRASHES, "*")):
        if not os.path.isdir(d) or abs(os.path.getmtime(d) - near) > slack:
            continue
        ctx = os.path.join(d, "CrashContext.runtime-xml")
        try:
            xml = open(ctx, encoding="utf-8", errors="replace").read(200000)
        except OSError:
            continue
        kind = (re.search(r"<CrashType>([^<]*)<", xml) or [None, "?"])[1]
        if kind == "Ensure" or "<IsEnsure>true<" in xml:
            continue
        msg = (re.search(r"<ErrorMessage>([^<]*)", xml) or [None, ""])[1].strip()
        out.append((os.path.basename(d), kind, msg[:300]))
    return out


def classify(path):
    """('crash'|'clean'|'killed'|'empty', reason line) for an editor log of a session that has ENDED."""
    if not path or not os.path.exists(path):
        return "empty", "no editor log"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - 400000))
        tail = f.read().decode("utf-8", "replace")
    lines = tail.splitlines()
    for i, l in enumerate(lines):
        if "=== Critical error: ===" in l:
            reason = next((x for x in lines[i + 1:i + 6] if x.split("Error:", 1)[-1].strip()), l)
            return "crash", reason.strip()
    m = re.search(r"^.*RequestExit(WithStatus)?\(1\b.*$", tail, re.M)
    if m:
        return "crash", m.group(0).strip()
    reports = crash_reports(os.path.getmtime(path))
    if reports:
        return "crash", "crash report %s: %s %s" % reports[-1]
    quit_ = [l for l in lines if "QUIT_EDITOR" in l]
    if quit_:
        return "clean", quit_[-1].strip()
    if any("Log file closed" in l for l in lines[-5:]):
        return "clean", "editor closed normally (no crash markers)"
    return "killed", "log stops without crash markers or shutdown (killed by a tool/agent): " + (lines[-1].strip()[:200] if lines else "")


# ---------------------------------------------------------------- state / decision

def load_state():
    try:
        return json.load(open(STATE))
    except (OSError, ValueError):
        return {"relaunches": []}


def save_state(st):
    try:
        json.dump(st, open(STATE, "w"))
    except OSError:
        pass


def decide(absent_since, st, now=None):
    """(action, message): action 'relaunch' or None."""
    now = now or time.time()
    if os.path.exists(PAUSE):
        return None, "paused (area2/no_watchdog.txt exists)"
    procs = processes()
    eds = procs.get("unrealeditor.exe", [])
    if len(eds) >= 2:
        return None, "WARNING %d editors running (pids %s); not touching them (play.py handles duplicates)" % (len(eds), eds)
    if eds:
        return None, "editor running (pid %d), nothing to do" % eds[0]
    if "skyrimse.exe" not in procs:
        return None, "no editor, no Skyrim: nothing to do"
    builds = sorted(BUILD_EXES & set(procs))
    if builds:
        return None, "no editor but %s running (build / headless editor): waiting" % ", ".join(builds)
    if not skyrim_in_world():
        return None, "no editor; Skyrim is not in the world yet: waiting"
    gone = now - absent_since
    if gone < GRACE:
        return None, "no editor for %.0f s (< %d s grace): waiting" % (gone, GRACE)
    path = last_session_log()
    kind, reason = classify(path)
    what = "last session %s: %s (%s)" % (os.path.basename(path or "-"), kind, reason)
    if kind != "crash":
        return None, "no editor for %.0f s, but not relaunching: %s" % (gone, what)
    recent = [t for t in st.get("relaunches", []) if now - t < WINDOW]
    if len(recent) >= MAX_RELAUNCH:
        return "giveup", "%d relaunches in the last %d min; giving up. %s" % (len(recent), WINDOW // 60, what)
    gb = play.free_gb()
    if gb < MIN_FREE_GB:
        return None, "would relaunch but only %.1f GB RAM free (< %d): waiting. %s" % (gb, MIN_FREE_GB, what)
    return "relaunch", "editor crashed and has been gone %.0f s: %s" % (gone, what)


def relaunch(st):
    st.setdefault("relaunches", []).append(time.time()); save_state(st)
    if processes().get("unrealeditor.exe"):
        log("relaunch aborted: an editor appeared meanwhile"); return False
    started = time.time()
    cmd = [play.UE, os.path.join(play.PROJ, "SkyBridge.uproject"), "-windowed", "-ResX=1600", "-ResY=900",
           "-ExecCmds=r.Streaming.PoolSize 3000"]
    try:
        p = subprocess.Popen(cmd, cwd=play.PROJ, creationflags=DETACH)
    except OSError:
        p = subprocess.Popen(cmd, cwd=play.PROJ, creationflags=DETACH & ~0x01000000)   # no BREAKAWAY_FROM_JOB if the job forbids it
    log("relaunched the editor (pid %d); waiting for '[SkyBridgeLive] alive'" % p.pid)
    while time.time() - started < 600:
        time.sleep(4)
        if play.editor_live(started):
            break
        if p.poll() is not None and not processes().get("unrealeditor.exe"):
            log("editor exited during startup (code %s)" % p.returncode); return False
    else:
        log("editor did not report alive within 10 min; leaving it running"); return False
    log("editor is live after %.0f s; remaster view in 20 s" % (time.time() - started))
    time.sleep(20)
    try:
        r = subprocess.run([PYTHON, os.path.join(ROOT, "start_bridge.py"), "--remaster"], cwd=ROOT, creationflags=HIDDEN,
                           capture_output=True, text=True, timeout=240)
        log("start_bridge --remaster (exit %d): %s" % (r.returncode, " | ".join((r.stdout + r.stderr).strip().splitlines()[-3:])))
    except subprocess.TimeoutExpired:
        log("start_bridge --remaster timed out")
    time.sleep(2)
    focus_skyrim()
    log("Skyrim focused; relaunch done")
    return True


# ---------------------------------------------------------------- process control

def watchdog_pids():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ? { $_.CommandLine -match 'editor_watchdog' -and "
                          "$_.CommandLine -notmatch '--(start|stop|once|test)' } | % ProcessId"],
                         capture_output=True, text=True, creationflags=HIDDEN).stdout
    return [int(x) for x in out.split() if int(x) != os.getpid()]


def is_running():
    h = k32.OpenMutexW(0x00100000, False, MUTEX)                                # SYNCHRONIZE
    if h:
        k32.CloseHandle(h)
    return bool(h)


def start():
    if is_running():
        print("watchdog already running (pids %s)" % watchdog_pids()); return
    cmd = '"%s" "%s"' % (PYTHONW, os.path.abspath(__file__))
    ps = ("$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0}; "
          "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='%s'; CurrentDirectory='%s'; "
          "ProcessStartupInformation=$si}; \"$($r.ReturnValue) $($r.ProcessId)\"" % (cmd.replace("'", "''"), ROOT))
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, creationflags=HIDDEN)
    print("WMI create:", (out.stdout + out.stderr).strip())
    time.sleep(3)
    print("running:", is_running(), "pids:", watchdog_pids())


def stop():
    pids = watchdog_pids()
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, creationflags=HIDDEN)
    if pids:
        log("stopped by --stop (pids %s)" % pids)
    print("stopped %s" % (pids or "nothing (not running)"))


def loop():
    h = k32.CreateMutexW(None, False, MUTEX)
    if ctypes.GetLastError() == 183:                                            # ERROR_ALREADY_EXISTS
        log("another watchdog is already running; exiting"); return
    log("watchdog started (pid %d, poll %d s, grace %d s, max %d relaunches / %d min)" % (os.getpid(), POLL, GRACE, MAX_RELAUNCH, WINDOW // 60))
    st = load_state()
    path = last_session_log()
    absent_since = min(time.time(), os.path.getmtime(path)) if path else time.time()
    last_msg, last_beat = None, 0
    while True:
        try:
            if processes().get("unrealeditor.exe"):
                absent_since = None
            elif absent_since is None:
                absent_since = time.time()
            action, msg = decide(absent_since or time.time(), st)
            key = re.sub(r"\d+(\.\d+)? s\b|pid \d+|pids \[[^\]]*\]|[\d.]+ GB", "", msg)
            if key != last_msg or time.time() - last_beat > 600:
                log(("" if key != last_msg else "heartbeat: ") + msg)
                last_msg, last_beat = key, time.time()
            if action == "giveup":
                log("stopping the watchdog (start it again with --start after fixing the crash)"); break
            if action == "relaunch":
                log("RELAUNCH: " + msg)
                relaunch(st)
                absent_since, last_msg = None, None
        except Exception as e:                                                  # keep watching whatever happens
            log("error: %r" % (e,))
        time.sleep(POLL)
    k32.CloseHandle(h)


# ---------------------------------------------------------------- tests

def self_test():
    """Crash detection against tonight's real logs; launches nothing."""
    L = play.LOGS
    cases = [("SkyBridge-backup-2026.10.28-06.38.11.log", "crash"),     # 23:38 access violation in python311.dll
             ("SkyBridge-backup-2026.10.28-06.32.21.log", "clean"),     # 23:32 stale QUIT_EDITOR
             ("SkyBridge-backup-2026.10.28-06.28.40.log", "clean"),     # 23:28 QUIT_EDITOR
             ("SkyBridge-backup-2026.10.28-05.36.34.log", "killed"),    # 22:36 killed + restarted by an agent
             ("SkyBridge_2.log", "killed")]                             # 22:42 duplicate editor killed
    ok = True
    for name, want in cases:
        p = os.path.join(L, name)
        if not os.path.exists(p):
            print("SKIP %s (missing)" % name); continue
        kind, reason = classify(p)
        good = kind == want; ok &= good
        print("%s %-45s -> %-6s (want %s): %s" % ("PASS" if good else "FAIL", name, kind, want, reason[:160]))
    t = os.path.getmtime(os.path.join(L, "SkyBridge-backup-2026.10.28-06.38.11.log"))
    rep = crash_reports(t)
    good = any("ACCESS_VIOLATION" in r[2] for r in rep); ok &= good
    print("%s crash folder for 23:38: %s" % ("PASS" if good else "FAIL", rep))
    cur = os.path.join(L, "SkyBridge.log")
    rep = crash_reports(os.path.getmtime(cur), slack=3600)
    ens = [r for r in rep if "8E3612884B4DAB2A597616AB813DA1B7" in r[0]]
    good = not ens; ok &= good
    print("%s 23:40:59 ensure folder (running editor) ignored: %s" % ("PASS" if good else "FAIL", not ens))
    st = {"relaunches": [time.time() - 60, time.time() - 600, time.time() - 1200]}
    recent = [x for x in st["relaunches"] if time.time() - x < WINDOW]
    good = len(recent) >= MAX_RELAUNCH; ok &= good
    print("%s back-off: 3 relaunches in 30 min blocks further ones" % ("PASS" if good else "FAIL"))
    print("ALL PASS" if ok else "SOME FAILED")
    return ok


def main():
    a = sys.argv[1:]
    if "--start" in a:
        start()
    elif "--stop" in a:
        stop()
    elif "--test" in a:
        sys.exit(0 if self_test() else 1)
    elif "--once" in a:
        eds = processes().get("unrealeditor.exe")
        path = last_session_log()
        absent = time.time() if eds else (os.path.getmtime(path) if path else time.time())
        st = load_state()
        action, msg = decide(absent, st)
        print("decision:", action or "none", "-", msg)
        if not eds and path:
            print("last session log %s: %s" % (os.path.basename(path), classify(path)))
        if action == "relaunch" and "--act" in a:
            log("RELAUNCH (--once --act): " + msg); relaunch(st)
    else:
        loop()


if __name__ == "__main__":
    main()
