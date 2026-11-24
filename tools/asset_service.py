"""On-demand asset service. The Unreal editor (live_bridge.py) appends model asset names to area2/requests.txt when it needs a
model it does not have. This service converts them (game archives/loose files -> OBJ -> textures -> FBX) and lists the finished
names in area2/ready.txt, which the editor then imports. Run:  python tools\\asset_service.py   (leave it running)"""
import glob, json, os, subprocess, sys, time

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
AREA = os.path.join(ROOT, "area2")
T = os.path.join(ROOT, "tools")
PY = sys.executable
REQ, READY, FAILED = (os.path.join(AREA, n) for n in ("requests.txt", "ready.txt", "failed.txt"))


def nif_from_asset(name):
    """asset name 'architecture_whiterun_wrx_y' -> candidate nif paths ('architecture/whiterun/wrx_y.nif' ...): try every split."""
    parts = name.split("_")
    cands = []
    # the folder structure is unknown from underscores; recover it from the request log written by the editor when available
    return cands


def main():
    os.makedirs(AREA, exist_ok=True)
    for p in (REQ, READY, FAILED):
        if not os.path.exists(p): open(p, "w").close()
    done = set(open(READY).read().split()) | set(open(FAILED).read().split())
    print("asset service running; watching", REQ)
    while True:
        want = [n for n in dict.fromkeys(open(REQ).read().split()) if n not in done]
        if want:
            print("converting %d models: %s" % (len(want), ", ".join(want[:6]) + ("..." if len(want) > 6 else "")))
            # models.json maps asset name -> nif path (written by the editor script alongside requests)
            mp = os.path.join(AREA, "models.json")
            mapping = json.load(open(mp)) if os.path.exists(mp) else {}
            if any(n not in mapping for n in want):               # models.json is rewritten each editor session: recover the path from the name
                sys.path.insert(0, T)
                import mesh_index
                idx = mesh_index.load()
                for n in want:
                    if n not in mapping and n in idx:
                        mapping[n] = idx[n]
            refs = [{"nif": mapping[n], "pos": [0, 0, 0], "rot": [0, 0, 0], "scale": 1.0} for n in want if n in mapping]
            area_json = os.path.join(AREA, "request_batch.json")
            json.dump(refs, open(area_json, "w"))
            subprocess.run([PY, "-W", "ignore", "-I", os.path.join(T, "build_area.py"), DATA, area_json, AREA], capture_output=True)
            subprocess.run([PY, "-W", "ignore", "-I", os.path.join(T, "textures.py"), DATA, AREA], capture_output=True)
            subprocess.run([PY, "-W", "ignore", "-I", os.path.join(T, "textures_pbr.py"), DATA, AREA], capture_output=True)
            subprocess.run([r"D:\blender.exe", "-b", "-P", os.path.join(T, "blender_export.py"), "--", os.path.join(AREA, "obj"), os.path.join(AREA, "export")], capture_output=True)
            for n in want:
                done.add(n)
                ok = os.path.exists(os.path.join(AREA, "export", n + ".fbx"))
                with open(READY if ok else FAILED, "a") as f: f.write(n + "\n")
                print(("ready: " if ok else "FAILED: ") + n)
        time.sleep(3)


if __name__ == "__main__":
    main()
