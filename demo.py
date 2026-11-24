"""One-click demo: asset converter + Skyrim (if not running) + Unreal editor with the live script."""
import subprocess, sys, os, re, time

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
UE = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
PROJ = os.path.join(ROOT, "unreal", "SkyBridge")
DETACH = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW


def procs():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ForEach-Object { $_.Name + '|' + $_.CommandLine }"],
                         capture_output=True, text=True).stdout
    return out


def running(text, p):
    return text.lower().count(text.lower() and p.lower()) > 0


p = procs()
if "asset_service" not in p:
    print("starting asset converter")
    subprocess.Popen([sys.executable, "-I", os.path.join(ROOT, "tools", "asset_service.py")],
                     creationflags=DETACH, cwd=ROOT)
if "tamriel_terrain" not in p:
    print("starting Tamriel terrain service")
    subprocess.Popen([sys.executable, "-I", os.path.join(ROOT, "tools", "tamriel_terrain.py"), "--serve"],
                     creationflags=DETACH, cwd=ROOT)
if "skyrimse.exe|" not in p.lower():
    print("starting Skyrim with the bridge (takes a minute)")
    subprocess.run([sys.executable, os.path.join(ROOT, "start_bridge.py"), "--no-overlay", "--skyrim-only"], cwd=ROOT)
LOGS = os.path.join(PROJ, "Saved", "Logs")


def editor_log(since):
    """The editor writes SkyBridge_2.log etc. when SkyBridge.log is held by another process: use the newest one."""
    logs = [os.path.join(LOGS, f) for f in os.listdir(LOGS) if f.startswith("SkyBridge") and f.endswith(".log")]
    logs = [f for f in logs if os.path.getmtime(f) > since]
    return max(logs, key=os.path.getmtime) if logs else None


if "unrealeditor.exe|" in p.lower():
    print("Unreal is already running.")
else:
    print("starting Unreal (1-2 minutes to appear)")
    t0 = time.time()
    subprocess.Popen([UE, os.path.join(PROJ, "SkyBridge.uproject"),
                      "-windowed", "-ResX=1600", "-ResY=900"], creationflags=DETACH, cwd=PROJ)
    while time.time() - t0 < 300:                                   # wait until the live bridge has spawned the world
        time.sleep(5)
        log = editor_log(t0)
        if log:
            tail = open(log, encoding="utf-8", errors="replace").read()[-20000:]
            if re.search(r"\[SkyBridgeLive\] alive: [1-9]\d* actors", tail):
                break
    time.sleep(10)
if "--no-remaster" not in sys.argv:
    print("switching to the remaster view (Unreal's viewport over Skyrim)")
    subprocess.run([sys.executable, os.path.join(ROOT, "start_bridge.py"), "--remaster"], cwd=ROOT)
print("Done. Play Skyrim; you see Unreal's render. Undo with: python start_bridge.py --remaster-off")
