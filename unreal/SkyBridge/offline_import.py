"""Headless bulk import (run by tools/offline_import.py through UnrealEditor-Cmd -run=pythonscript, no window, no Skyrim needed):
imports every converted model in area2/ready.txt that is not yet in /Game/Area2 (FBX + its textures + material instances), saving each one,
so the live editor only LOADS them instead of importing hundreds while you play. Resumable: it skips what already exists.
Env: OFFLINE_LIMIT (max models this run, 0 = all), OFFLINE_MINUTES (time budget, 0 = unlimited)."""
import os, sys, time
import unreal

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
AREA = os.path.join(ROOT, "area2")
sys.path.insert(0, os.path.join(ROOT, "unreal", "SkyBridge"))
import ue_assets

eal = unreal.EditorAssetLibrary
LOG = os.path.join(AREA, "offline_import.log")
limit = int(os.environ.get("OFFLINE_LIMIT", "0") or 0)
budget = float(os.environ.get("OFFLINE_MINUTES", "0") or 0) * 60
t0 = time.time()


def say(msg):
    line = "[%5.0fs] %s" % (time.time() - t0, msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


names = list(dict.fromkeys(open(os.path.join(AREA, "ready.txt")).read().split()))
todo = [n for n in names if " " not in n and os.path.exists(os.path.join(AREA, "export", n + ".fbx")) and not eal.does_asset_exist("/Game/Area2/" + n)]
say("ready models %d, not imported yet %d%s" % (len(names), len(todo), (", this run limited to %d" % limit) if limit else ""))
done = failed = 0
for i, n in enumerate(todo):
    if (limit and done >= limit) or (budget and time.time() - t0 > budget):
        say("stopping: %s" % ("limit reached" if limit and done >= limit else "time budget used"))
        break
    try:
        ue_assets.import_model(n)
        done += 1
    except Exception as e:
        failed += 1
        say("FAILED %s: %s" % (n, e))
    if done % 25 == 0 and done:
        unreal.SystemLibrary.collect_garbage()
        say("%d imported (%d failed), %d left" % (done, failed, len(todo) - i - 1))
unreal.SystemLibrary.collect_garbage()
say("models finished: %d imported, %d failed, %d still to import" % (done, failed, len(todo) - done - failed))

# characters + creatures (area2/npc/export/npc_<baseId>.fbx -> /Game/Npc/npc_<baseId>, materials assigned, SAVED): the live editor then loads them
# instead of importing ~100 FBXs at the start of every session.
if os.environ.get("OFFLINE_NPCS", "1") != "0":
    import glob, npc_live
    fbxs = sorted(glob.glob(os.path.join(AREA, "npc", "export", "npc_*.fbx")))
    n_ok = n_fail = n_have = 0
    for f in fbxs:
        key = os.path.basename(f)[4:-4]
        if len(key) != 8:                                   # npc_male.fbx / npc_female.fbx test files
            continue
        if eal.does_asset_exist("/Game/Npc/npc_" + key):
            n_have += 1
            continue
        if budget and time.time() - t0 > budget:
            say("stopping before characters: time budget used"); break
        try:
            mesh = npc_live.mesh_for(int(key, 16))
            if mesh is None:
                raise RuntimeError("import returned nothing")
            eal.save_loaded_asset(mesh)
            sk = mesh.get_editor_property("skeleton")
            if sk:
                eal.save_loaded_asset(sk)
            n_ok += 1
        except Exception as e:
            n_fail += 1
            say("FAILED npc %s: %s" % (key, e))
        if n_ok % 10 == 0 and n_ok:
            unreal.SystemLibrary.collect_garbage()
            say("%d characters imported" % n_ok)
    say("characters finished: %d imported, %d failed, %d were already there" % (n_ok, n_fail, n_have))
say("finished")
