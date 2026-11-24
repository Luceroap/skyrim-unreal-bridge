"""Start a clean photo session:  python tools/shot_session.py [--max]
Frees the machine (stops the local-model queue and its llama-server, which hold ~27 GB), refuses to start if free virtual memory is still
too low, launches Skyrim + the Unreal view with play.py, and (with --max) switches the editor to showcase quality afterwards.
Back to everyday settings: python tools/max_quality.py --off   (or just restart the editor: the settings are session-only).
Photos: tools/showcase_shot.py.  Night: write 'hour 22' into Data/SKSE/Plugins/SkyrimUnrealBridge.sky and wait ~25 s for the torches."""
import ctypes, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_FREE_VIRTUAL_GB = 30.0


class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in
               ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]


def free_commit_gb():
    m = MEM(); m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 2 ** 30                    # free commit (RAM + pagefile), the number that froze the PC


def say(s):
    print("[%3ds] %s" % (time.time() - t0, s), flush=True)


def kill_cmd(pattern):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine -match '%s' -and $_.ProcessId -ne %d } | % ProcessId" % (pattern, os.getpid())],
                         capture_output=True, text=True).stdout
    for pid in out.split():
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)


t0 = time.time()
kill_cmd("run_local_queue|Local_Queue")
subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"], capture_output=True)
subprocess.run(["taskkill", "/F", "/IM", "codex.exe", "/FI", "WINDOWTITLE eq nothing"], capture_output=True)
time.sleep(4)
free = free_commit_gb()
say("free commit memory: %.0f GB" % free)
if free < MIN_FREE_VIRTUAL_GB:
    sys.exit("only %.0f GB free (need %.0f). Close big programs (browser tabs, Cursor, Ollama) and try again." % (free, MIN_FREE_VIRTUAL_GB))
subprocess.run([sys.executable, os.path.join(ROOT, "play.py")], cwd=ROOT)
if "--max" in sys.argv:
    time.sleep(15)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "max_quality.py")], cwd=ROOT)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "set_cvar.py"), "r.ScreenPercentage 100"], cwd=ROOT)
    say("showcase quality is on")
