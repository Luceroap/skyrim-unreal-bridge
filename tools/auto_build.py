"""Rebuild the Unreal scene from everything the plugin has recorded so far (incremental: only new models are converted).
    python C:\\Users\\Aidan\\SkyrimUnrealBridge\\tools\\auto_build.py [--no-restart-ue]
Steps: merge live dump + game files -> convert new models/textures -> Blender export (new only) -> Unreal import (new only)
-> write placements.csv -> restart Unreal (it is closed during the import and reopened afterwards)."""
import glob, json, os, subprocess, sys, time

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
SKSE_DIR = os.path.expandvars(r"%USERPROFILE%\OneDrive\Documents\My Games\Skyrim Special Edition\SKSE")
UE_CMD = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
UPROJECT = os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject")
PY = sys.executable
T = os.path.join(ROOT, "tools")


def run(cmd, **kw):
    print(">", " ".join(str(c) for c in cmd)[:150])
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    tail = (r.stdout or "").strip().splitlines()[-3:]
    for l in tail: print("   ", l[:160])
    return r


def running(exe):
    return exe.lower() in subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe], capture_output=True, text=True).stdout.lower()


def main():
    restart_ue = "--no-restart-ue" not in sys.argv
    refs, centers = os.path.join(SKSE_DIR, "SkyrimUnrealBridge_refs_all.tsv"), os.path.join(SKSE_DIR, "SkyrimUnrealBridge_centers.txt")
    area_all = os.path.join(ROOT, "whiterun", "area_all.json")
    run([PY, "-I", os.path.join(T, "merge_area.py"), area_all, refs, centers, os.path.join(ROOT, "whiterun", "area_esm.json")])
    run([PY, "-I", os.path.join(T, "build_area.py"), DATA, area_all, os.path.join(ROOT, "area2")])
    run([PY, "-I", os.path.join(T, "textures.py"), DATA, os.path.join(ROOT, "area2")])
    run([PY, "-W", "ignore", "-I", os.path.join(T, "textures_pbr.py"), DATA, os.path.join(ROOT, "area2")])
    # alpha-masked texture list (near-binary alpha with 1-80% transparent pixels = foliage / cut-outs)
    from PIL import Image
    masked = []
    for f in glob.glob(os.path.join(ROOT, "area2", "tex", "*.png")):
        n = os.path.splitext(os.path.basename(f))[0]
        if n.endswith(("_n", "_rmaos")) or n.startswith("terrain_tile") or n == "terrain_detail":
            continue
        im = Image.open(f)
        if im.mode != "RGBA": continue
        a = list(im.getchannel("A").resize((128, 128)).getdata()); cnt = len(a)
        lo = sum(1 for v in a if v < 128) / cnt; binary = sum(1 for v in a if v < 25 or v > 230) / cnt
        if 0.003 < lo < 0.995 and binary > 0.6: masked.append(n.lower())
    open(os.path.join(ROOT, "area2", "tex", "alpha_masked.txt"), "w").write("\n".join(masked))
    print("alpha-masked textures:", len(masked))
    # terrain + alpha list are produced once and reused
    obj_dir = os.path.join(ROOT, "area2", "obj")
    if not os.path.exists(os.path.join(obj_dir, "terrain.obj")):
        run([PY, "-I", os.path.join(T, "esm_land.py"), os.path.join(DATA, "Skyrim.esm"), os.path.join(obj_dir, "terrain.obj"), "whiterunworld", "23000", "-6000", "14000"])
    run([r"D:\blender.exe", "-b", "-P", os.path.join(T, "blender_export.py"), "--", obj_dir, os.path.join(ROOT, "area2", "export")])

    ue_was_running = running("UnrealEditor.exe")
    if ue_was_running:
        subprocess.run(["taskkill", "/F", "/IM", "UnrealEditor.exe"], capture_output=True); time.sleep(3)
    r = run([UE_CMD, UPROJECT, "-run=pythonscript", "-script=" + os.path.join(ROOT, "unreal", "SkyBridge", "import_area2.py"),
             "-unattended", "-nullrhi", "-stdout", "-FullStdOutLogOutput"])
    for l in (r.stdout or "").splitlines():
        if "LogPython: IMPORTED" in l or "LogPython: TEXTURED" in l or "Traceback" in l: print("   ", l[l.find("LogPython"):][:120])
    r2 = run([UE_CMD, UPROJECT, "-run=pythonscript", "-script=" + os.path.join(ROOT, "unreal", "SkyBridge", "upgrade_materials.py"),
              "-unattended", "-nullrhi", "-stdout", "-FullStdOutLogOutput"])
    for l in (r2.stdout or "").splitlines():
        if "LogPython: PBR" in l or "LogPython: NANITE" in l or "Traceback" in l: print("   ", l[l.find("LogPython"):][:120])
    csv = os.path.join(ROOT, "area2", "placements.csv")
    rows = [l for l in open(csv).read().split() if not l.startswith("terrain,")] + ["terrain,0,0,0,0,0,0,1"]
    open(csv, "w").write("\n".join(rows) + "\n")
    print("placements:", len(rows) - 1)
    if restart_ue and ue_was_running:
        subprocess.Popen([r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe", UPROJECT, "-game", "-windowed", "-ResX=1280", "-ResY=720"])
        print("Unreal restarted; run start_bridge.py --overlay-only once it is up.")


if __name__ == "__main__":
    main()

