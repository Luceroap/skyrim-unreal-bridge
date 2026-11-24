"""Wait for the offline import to finish, close every project process, then shut the PC down (2-minute warning; cancel with:  shutdown /a).
Started detached, so it keeps working if the chat/Cursor windows are closed. Log: area2/shutdown_after_import.log
    python tools/shutdown_after_import.py [--no-shutdown] [--max-hours 4]"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "area2", "shutdown_after_import.log")
IMPORT_LOG = os.path.join(ROOT, "area2", "offline_import.log")
max_h = float(sys.argv[sys.argv.index("--max-hours") + 1]) if "--max-hours" in sys.argv else 4.0


def say(msg):
    with open(LOG, "a") as f:
        f.write("%s  %s\n" % (time.strftime("%H:%M:%S"), msg))


def import_running():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'offline_import' -or $_.Name -eq 'UnrealEditor-Cmd.exe' } | % ProcessId"],
                         capture_output=True, text=True).stdout.split()
    return bool(out)


def last_line():
    try:
        return open(IMPORT_LOG).read().strip().splitlines()[-1]
    except Exception:
        return "(no import log)"


import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)         # ES_CONTINUOUS | ES_SYSTEM_REQUIRED: no idle sleep while this script runs
say("waiting for the offline import to finish (gives up after %.1f h)" % max_h)
t0 = time.time(); seen = False
while time.time() - t0 < max_h * 3600:
    if import_running():
        seen = True
    elif seen or time.time() - t0 > 120:            # it ran and ended (or never started within 2 min)
        break
    time.sleep(20)
say("import ended: " + last_line())
for exe in ("UnrealEditor-Cmd.exe", "UnrealEditor.exe", "SkyrimSE.exe", "blender.exe"):
    subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
subprocess.run(["powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_Process | ? { $_.Name -match 'python' -and $_.CommandLine -match 'asset_service|npc_autobuild|remaster_watch|editor_watchdog' } | % { Stop-Process -Id $_.ProcessId -Force }"],
               capture_output=True)
say("project processes closed")
if "--no-shutdown" in sys.argv:
    say("--no-shutdown given: leaving the PC on"); sys.exit()
say("shutting down in 120 s (cancel with: shutdown /a)")
subprocess.run(["shutdown", "/s", "/t", "120", "/c", "Skyrim/Unreal asset import finished: shutting down. Cancel with: shutdown /a"])
