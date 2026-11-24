"""Import every converted-but-not-imported model into Unreal WITHOUT the game running and without opening an editor window.
    python tools/offline_import.py                     everything left (can take a few hours: run it before bed)
    python tools/offline_import.py --limit 200         at most 200 models this run
    python tools/offline_import.py --minutes 60        stop after about an hour
Needs: Skyrim and the Unreal editor closed (--even-if-skyrim to skip that check), >= 8 GB free RAM. Resumable. Log: area2/offline_import.log"""
import ctypes, os, subprocess, subprocess as sp, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
PROJ = os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject")
SCRIPT = os.path.join(ROOT, "unreal", "SkyBridge", "offline_import.py")


def running(exe):
    return exe.lower() in sp.run(["tasklist", "/FI", "IMAGENAME eq " + exe], capture_output=True, text=True).stdout.lower()


def free_gb():
    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_uint32), ("load", ctypes.c_uint32), ("tp", ctypes.c_uint64), ("ap", ctypes.c_uint64), ("a", ctypes.c_uint64 * 5)]
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ap / 2**30


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else "0"


if running("UnrealEditor.exe") or running("UnrealEditor-Cmd.exe"):
    sys.exit("Close the Unreal editor first (python play.py --stop).")
if running("SkyrimSE.exe") and "--even-if-skyrim" not in sys.argv:
    sys.exit("Close Skyrim first so the import has the whole machine (or use --even-if-skyrim).")
if free_gb() < 8:
    sys.exit("Only %.1f GB of memory free; close other programs first." % free_gb())
env = dict(os.environ, OFFLINE_LIMIT=arg("--limit"), OFFLINE_MINUTES=arg("--minutes"))
log = os.path.join(ROOT, "offline_import_stdout.log")
print("importing in the background (no window); progress: area2\\offline_import.log", flush=True)
t0 = time.time()
with open(log, "w") as f:
    rc = subprocess.run([CMD, PROJ, "-run=pythonscript", "-script=" + SCRIPT, "-unattended", "-nullrhi", "-nosplash", "-stdout", "-FullStdOutLogOutput"],
                        stdout=f, stderr=subprocess.STDOUT, env=env, creationflags=0x08000000).returncode
print("done in %.0f s (exit code %d). Last lines of area2\\offline_import.log:" % (time.time() - t0, rc))
try:
    print("".join(open(os.path.join(ROOT, "area2", "offline_import.log")).readlines()[-4:]))
except Exception:
    pass
