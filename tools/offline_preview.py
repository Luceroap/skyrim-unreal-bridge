"""Render NPC close-ups with NO Skyrim and no editor window, so changes to NPC materials can be checked unattended.
    python tools/offline_preview.py [KEY ...] [--dist 230] [--size 1080]      KEY = NPC id like 00013b99 (default: first 3 saved NPCs)
Output: screenshots/offline/npc_<key>_full.png and _torso.png.  Needs Skyrim and UnrealEditor closed.  Log: area2/offline_preview.log"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
PROJ = os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject")
SCRIPT = os.path.join(ROOT, "unreal", "SkyBridge", "offline_preview.py")
LOG = os.path.join(ROOT, "area2", "offline_preview.log")


def running(exe):
    return exe.lower() in subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe], capture_output=True, text=True).stdout.lower()


def main():
    args = sys.argv[1:]
    env = dict(os.environ)
    keys = [a for a in args if not a.startswith("--") and (len(args) < 2 or args[args.index(a) - 1] not in ("--dist", "--size"))]
    if keys: env["SB_KEYS"] = ",".join(keys)
    for flag, var in (("--dist", "SB_DIST"), ("--size", "SB_SIZE")):
        if flag in args: env[var] = args[args.index(flag) + 1]
    if running("UnrealEditor.exe") or running("SkyrimSE.exe"):
        sys.exit("close Skyrim and the editor first (python play.py --stop)")
    t0 = time.time()
    cmd = [EXE, PROJ, "-ExecutePythonScript=" + SCRIPT, "-nosplash", "-stdout", "-FullStdOutLogOutput"]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1500, creationflags=0x08000000)
    out = [l for l in (p.stdout or "").splitlines() if "OfflinePreview" in l or "Error" in l and "Python" in l]
    print("\n".join(out[-12:]) or "no preview output; see " + LOG)
    print("took %.0f s; images in screenshots/offline/" % (time.time() - t0))


if __name__ == "__main__":
    main()
