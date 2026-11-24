"""Offline test (no editor): space-named models get whitespace-free asset names and are held back until the converter
signals support (area2/spaced_names_ok.txt). Run: python area2/test_spaced_names.py"""
import json, os, sys, tempfile, types
from unittest import mock

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
sys.modules["unreal"] = mock.MagicMock()
sys.path.insert(0, os.path.join(ROOT, "unreal", "SkyBridge"))
src = open(os.path.join(ROOT, "unreal", "SkyBridge", "live_bridge.py"), encoding="utf-8").read()
assert src.rstrip().endswith("start()")
lb = types.ModuleType("live_bridge")
exec(compile(src.rstrip()[:-len("start()")], "live_bridge.py", "exec"), lb.__dict__)
Live = lb.Live

tmp = tempfile.mkdtemp()
lb.AREA = tmp
SP = "clutter/dining set/basictankard01.nif"

# 1. names
assert Live.asset_name(SP) == "clutter_dining_set_basictankard01"
assert Live.asset_name("architecture/whiterun/wrhouse01.nif") == "architecture_whiterun_wrhouse01"
assert Live.asset_name("already_an_asset") == "already_an_asset"

# 2. request gate
live = object.__new__(Live)
live.requested, live.model_paths = set(), {}
req = os.path.join(tmp, "requests.txt")
read = lambda: open(req).read().split() if os.path.exists(req) else []
Live._sp_t = 0.0
live.request(Live.asset_name(SP), SP)
live.request("architecture_whiterun_wrhouse01", "architecture/whiterun/wrhouse01.nif")
assert read() == ["architecture_whiterun_wrhouse01"], read()
open(os.path.join(tmp, "spaced_names_ok.txt"), "w").close()
live.request(Live.asset_name(SP), SP)                                   # flag cached for 30 s: still held back
assert len(read()) == 1
Live._sp_t = 0.0
live.request(Live.asset_name(SP), SP)
assert read() == ["architecture_whiterun_wrhouse01", "clutter_dining_set_basictankard01"], read()
assert json.load(open(os.path.join(tmp, "models.json")))["clutter_dining_set_basictankard01"] == SP
os.remove(os.path.join(tmp, "spaced_names_ok.txt"))
Live._sp_t = 0.0


# 3. prefetch: space-named nifs skipped from interiors and dungeon_models.txt until the flag exists
def ref(model, nif, typ="STAT"):
    return {"id": 1, "model": model, "nif": nif, "type": typ, "pos": [0, 0, 0], "rot": [1, 0, 0, 0, 1, 0, 0, 0, 1],
            "scale": 1.0, "disabled": False, "parent": 0}


HUT = "architecture/falmer hut/largehut.nif"
json.dump({"TestCell": {"id": 5, "ambient": None, "directional": None, "fog": None,
                        "refs": [ref("zz_test_plain", "zz/test/plain.nif"), ref(Live.asset_name(HUT), HUT),
                                 ref("old style_name", "old style/name.nif")]}},
          open(os.path.join(tmp, "interiors_test.json"), "w"))
with open(os.path.join(tmp, "dungeon_models.txt"), "w") as f:
    f.write("# count\tmodel\tnif\tconverted\n")
    f.write("9\tzz_dng_plain\tzz/dng/plain.nif\t0\n")
    f.write("8\tarchitecture_falmer_hut_wallpod\tarchitecture/falmer hut/wallpod.nif\t0\n")
live._flags = set()
live.prefetch_cities()
got = [n for n, _ in live.prefetch_todo]
assert got == ["zz_test_plain", "zz_dng_plain"], got
open(os.path.join(tmp, "spaced_names_ok.txt"), "w").close()
Live._sp_t = 0.0
live.prefetch_cities()
got = [n for n, _ in live.prefetch_todo]
assert got == ["zz_test_plain", "architecture_falmer_hut_largehut", "zz_dng_plain", "architecture_falmer_hut_wallpod"], got
assert all(" " not in n for n in got)                                   # old-style names with spaces stay filtered

# 4. the converter's whitespace split sees exactly the names written
assert all(len(n.split()) == 1 for n in read())
print("ok: spaced-name asset names, request gate and prefetch gate")
