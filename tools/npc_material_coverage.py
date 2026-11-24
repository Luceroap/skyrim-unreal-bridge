"""Offline coverage check for NPC / gear / creature materials (no Skyrim, no Unreal).

Reads what the converter built (area2/npc/obj/npc_<id>.mtl, area2/npc/skin/gear_*.json and skeleton_*.json, area2/npc/export)
and checks it against unreal/SkyBridge/npc_material_types.py, which remaster_materials uses to pick each slot's material:
  gear      every worn texture gets a real material kind (not the cloth fallback); armor that relies on the spec-mask split
            (metal plates vs leather straps) has its _s map; diffuse/normal PNGs exist; gear the stream reported is in the mesh
  creatures every creature texture folder is mapped; every creature skeleton has a built mesh; meshes are imported (FBX)
  profiles  every kind has a profile and every detail texture the profiles use exists (tools/*_detail.py)
Writes area2/npc/material_coverage.json.

  python tools/npc_material_coverage.py            report
  python tools/npc_material_coverage.py --strict   exit 1 when anything is uncovered
  python tools/npc_material_coverage.py --test     classifier self-test only
"""
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
NPC = os.path.join(AREA, "npc")
sys.path.insert(0, os.path.join(ROOT, "unreal", "SkyBridge"))
import npc_material_types as nmt  # noqa: E402

CASES = [
    (r"textures\actors\character\eyes\eyebrown.dds", "eye"),
    (r"textures\actors\character\eyes\eyebrownbloodshot.dds", "eye"),
    (r"textures\actors\character\anukethreplacers\eyes\aela.dds", "eye"),
    ("eyes_aela", "eye"),
    (r"textures\actors\character\anukethreplacers\brows\aela.dds", "hair"),
    (r"textures\actors\character\malebrows\malebrow_1.dds", "hair"),
    (r"textures\actors\character\hair\hairbraids.dds", "hair"),
    (r"textures\actors\character\beards\beardshort04.dds", "hair"),
    (r"textures\actors\character\mouth\mouthhuman.dds", "mouth"),
    (r"textures\actors\character\facegendata\facetint\skyrim.esm\00013b97.dds", "skin"),
    (r"textures\actors\character\female\femalebody_1.dds", "skin"),
    (r"textures\actors\character\male\malehead.dds", "skin"),
    (r"textures\actors\character\malechild\upperbodymale.dds", "skin"),
    (r"textures\actors\character\male\facedetails\faceleftsidegash1.dds", "skin"),
    (r"textures\actors\character\khajiitmale\bodymale.dds", "skin_beast"),
    ("textures_actors_character_female_femalehands_1_dds", "skin"),
    ("00013b97", "skin"),
    (r"textures\armor\hide\m\cuirasslight.dds", "leather_armor"),
    (r"textures\armor\studded\studdedarmor_male_body_d.dds", "leather_armor"),
    (r"textures\armor\stormcloaks\stormcloakshelm.dds", "leather_armor"),
    (r"textures\armor\iron\m\cuirassplate.dds", "metal_armor"),
    (r"textures\armor\steel\m\steelhelmetlite.dds", "metal_armor"),
    (r"textures\armor\draugr\femaledraugrarmor.dds", "metal_armor"),
    (r"textures\armor\amuletsandrings\mara\maraamulet.dds", "jewelry"),
    (r"textures\furshells\hide\m\cuirasslight_shell.dds", "fur"),
    (r"textures\clothes\monk\robes.dds", "cloth"),
    (r"textures\clothes\monk\boots.dds", "leather"),
    (r"textures\clothes\farmclothes03\glovesm_d.dds", "leather"),
    (r"textures\clothes\barkeeper\f\barkeepfemaleshoes.dds", "leather"),
    (r"textures\clothes\beggarclothes\hatm_d.dds", "cloth"),
    (r"textures\actors\highlandcow\highlandcow.dds", "creature_fur"),
    (r"textures\actors\highlandcow\highlandcow_shell.dds", "creature_fur"),
    (r"textures\actors\dragon\dragon.dds", "creature_scale"),
    (r"textures\actors\skeleton\skeleton.dds", "bone"),
    (r"textures\actors\canine\wolf.dds", "creature_fur"),
    (r"textures\actors\dlc01\chaurusflyer\chaurusflyer.dds", "chitin"),
    (r"textures\actors\dwarvenspider\dwarvenspider.dds", "creature_metal"),
    ("cuirassplate", "metal_armor"),
    ("bootslight", "leather"),
]


def self_test():
    bad = []
    for name, want in CASES:
        got, rule = nmt.classify(name)
        if got != want:
            bad.append("%s -> %s (%s), expected %s" % (name, got, rule, want))
    missing = sorted({k for _, k in CASES} - set(nmt.PROFILES))
    if missing:
        bad.append("kinds without a profile: %s" % missing)
    for k, p in nmt.PROFILES.items():
        if set(p) != set(nmt._BASE):
            bad.append("profile %s has unknown/missing fields: %s" % (k, set(p) ^ set(nmt._BASE)))
        for d in (p["detail"], p["detail2"]):
            if d and d not in nmt.DETAIL_TEXTURES:
                bad.append("profile %s uses detail '%s' not in DETAIL_TEXTURES" % (k, d))
        if p["shading"] == "skin" and not p["sss_profile"]:
            bad.append("profile %s: skin shading without sss_profile" % k)
    for c, k in nmt.CREATURES.items():
        if k not in nmt.PROFILES:
            bad.append("creature %s -> unknown kind %s" % (c, k))
    print("self-test: %d cases, %s" % (len(CASES), "OK" if not bad else "%d FAILED" % len(bad)))
    for b in bad:
        print("  FAIL " + b)
    return not bad


def read_mtls():
    """{npc id: [(slot, skyrim path)]}"""
    out = {}
    for f in sorted(glob.glob(os.path.join(NPC, "obj", "npc_*.mtl"))):
        if not re.fullmatch(r"npc_[0-9a-f]{8}\.mtl", os.path.basename(f)):
            continue
        rows, slot = [], None
        for line in open(f, encoding="latin1"):
            line = line.strip()
            if line.startswith("newmtl "):
                slot = line[7:]
            elif line.startswith("# skyrim diffuse: ") and slot:
                rows.append((slot, line[18:].strip()))
        out[os.path.basename(f)[4:-4]] = rows
    return out


def read_gear():
    """{npc id: set(skyrim texture paths the gear stream reported)}"""
    out = defaultdict(set)
    for f in glob.glob(os.path.join(NPC, "skin", "gear_*.json")):
        fid = os.path.basename(f).split("_")[1]
        try:
            for shape in json.load(open(f)):
                if shape.get("texture"):
                    out[fid].add(shape["texture"])
        except (OSError, ValueError):
            pass
    return out


GEAR_KINDS = ("cloth", "fur", "leather", "leather_armor", "metal_armor", "jewelry")


def gear_key(path):
    """Gear-stream paths sometimes lack the 'textures\\' prefix and differ in case from the .mtl ones."""
    p = path.lower().replace("/", "\\")
    return p[9:] if p.startswith("textures\\") else p


def png_stem(slot, path, alias):
    s = alias.get(slot.lower())
    if s:
        return s
    stem = re.split(r"[\\/]", path)[-1].lower()
    return stem[:-4] if stem.endswith(".dds") else stem


def has_png(stem, suffix=""):
    return any(os.path.exists(os.path.join(d, stem + suffix + ".png")) for d in (os.path.join(NPC, "tex"), os.path.join(AREA, "tex")))


def main():
    ok = self_test()
    if "--test" in sys.argv:
        sys.exit(0 if ok else 1)
    alias = {}
    try:
        alias = {k.lower(): v for k, v in json.load(open(os.path.join(NPC, "tex_alias.json"))).items()}
    except (OSError, ValueError):
        pass
    mtls, gear = read_mtls(), read_gear()
    rep = dict(kinds=Counter(), fallback=[], unmapped_armor=[], unmapped_creatures=[], missing_diffuse=[], missing_normal=[],
               armor_without_spec=[], gear_not_in_mesh=[], creatures={}, creature_skeletons_unbuilt=[], meshes_not_exported=[],
               missing_detail=[], naked_humanoids=[])
    seen = {}
    creature_meshes = defaultdict(list)
    for fid, rows in mtls.items():
        kinds_here = set()
        for slot, path in rows:
            kind, rule = nmt.classify(path, AREA)
            kinds_here.add(kind)
            key = path.lower()
            if key in seen:
                continue
            seen[key] = (kind, rule)
            rep["kinds"][kind] += 1
            if rule == nmt.FALLBACK:
                rep["fallback"].append(path)
            elif rule.startswith("armor?:"):
                rep["unmapped_armor"].append(path)
            elif rule.startswith("creature?:"):
                rep["unmapped_creatures"].append(path)
            stem = png_stem(slot, path, alias)
            if not has_png(stem):
                rep["missing_diffuse"].append("%s (%s)" % (stem, path))
            elif kind in GEAR_KINDS and not has_png(stem, "_n") and not stem.endswith("_shell"):
                rep["missing_normal"].append(stem)
            if kind in ("leather_armor", "metal_armor") and not has_png(stem, "_s") and not has_png(stem, "_rmaos"):
                rep["armor_without_spec"].append(stem)
        cre = sorted({r.split(":", 1)[1] for k, r in (nmt.classify(p, AREA) for _, p in rows) if r.startswith("creature")})
        if cre:
            for c in cre:
                creature_meshes[c].append(fid)
        elif not kinds_here & set(GEAR_KINDS):
            rep["naked_humanoids"].append(fid)
        if not os.path.exists(os.path.join(NPC, "export", "npc_%s.fbx" % fid)):
            rep["meshes_not_exported"].append(fid)
        built = {gear_key(p) for _, p in rows}
        for g in sorted(gear.get(fid, ())):
            if gear_key(g) not in built:
                rep["gear_not_in_mesh"].append("%s: %s" % (fid, g))
    for sk in sorted(glob.glob(os.path.join(NPC, "skin", "skeleton_actors_*.json"))):
        race = os.path.basename(sk)[len("skeleton_actors_"):].split("_")[0]
        meshes = [f for c, fs in creature_meshes.items() for f in fs if c == race or c.startswith(race) or race.startswith(c)]
        if race == "cow":
            meshes += creature_meshes.get("highlandcow", [])
        if not meshes:
            rep["creature_skeletons_unbuilt"].append(race)
    for c, fids in sorted(creature_meshes.items()):
        rep["creatures"][c] = dict(kind=nmt.CREATURES.get(c, "UNMAPPED"), meshes=fids,
                                   exported=[f for f in fids if os.path.exists(os.path.join(NPC, "export", "npc_%s.fbx" % f))])
    for d in sorted({p[x] for p in nmt.PROFILES.values() for x in ("detail", "detail2") if p[x]}):
        for suf in ("", "_n"):
            if not os.path.exists(os.path.join(AREA, "tex", d + suf + ".png")):
                rep["missing_detail"].append(d + suf)
    rep["missing_normal"] = sorted(set(rep["missing_normal"]))
    rep["armor_without_spec"] = sorted(set(rep["armor_without_spec"]))

    print("\n%d meshes, %d distinct textures" % (len(mtls), len(seen)))
    print("kinds: " + ", ".join("%s %d" % kv for kv in rep["kinds"].most_common()))
    print("\nCREATURES (%d built, %d known creature folders)" % (len(rep["creatures"]), len(nmt.CREATURES)))
    for c, v in rep["creatures"].items():
        print("  %-14s %-15s meshes %s, exported %s" % (c, v["kind"], ",".join(v["meshes"]), ",".join(v["exported"]) or "NONE"))
    sections = [("fallback (no rule, got default cloth)", "fallback"), ("unmapped armor folders", "unmapped_armor"),
                ("unmapped creature folders", "unmapped_creatures"), ("creature skeletons with no built mesh", "creature_skeletons_unbuilt"),
                ("meshes with no FBX in npc/export", "meshes_not_exported"), ("missing diffuse PNG", "missing_diffuse"),
                ("missing detail textures (run tools/*_detail.py)", "missing_detail"),
                ("armor without _s (no metal/leather split, single layer)", "armor_without_spec"),
                ("gear reported by the stream but not in the mesh", "gear_not_in_mesh"),
                ("humanoids with no clothing/armor slot", "naked_humanoids"), ("gear textures without _n", "missing_normal")]
    problems = 0
    for title, k in sections:
        items = rep[k]
        print("\n%s: %d" % (title, len(items)))
        for it in items[:25]:
            print("  " + it)
        if len(items) > 25:
            print("  ... %d more" % (len(items) - 25))
        if k in ("fallback", "unmapped_armor", "unmapped_creatures", "missing_diffuse", "missing_detail", "creature_skeletons_unbuilt"):
            problems += len(items)
    rep["kinds"] = dict(rep["kinds"])
    out = os.path.join(NPC, "material_coverage.json")
    json.dump(rep, open(out, "w"), indent=1)
    print("\nwrote %s; %d coverage problems%s" % (out, problems, "" if ok else ", SELF-TEST FAILED"))
    if "--strict" in sys.argv and (problems or not ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
