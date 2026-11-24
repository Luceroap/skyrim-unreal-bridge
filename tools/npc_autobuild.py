"""Background builder: every 15 s, build the character/creature FBXs for any new actor near the player (npc_batch.py --autobuild).
Started by play.py once Skyrim is in the world; stops by itself when Skyrim is closed. Log: area2/npc/autobuild.log"""
import os, subprocess, sys, time

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
LOG = os.path.join(ROOT, "area2", "npc", "autobuild.log")


def skyrim_running():
    return "skyrimse.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq SkyrimSE.exe"], capture_output=True, text=True).stdout.lower()


os.makedirs(os.path.dirname(LOG), exist_ok=True)
while skyrim_running():
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "npc_batch.py"), "3", "--autobuild"], capture_output=True, text=True, cwd=ROOT,
                       creationflags=0x08000000)
    out = r.stdout.strip()
    if "building" in out:
        with open(LOG, "a") as f:
            f.write("%s\n%s\n" % (time.strftime("%H:%M:%S"), out))
    time.sleep(15)
