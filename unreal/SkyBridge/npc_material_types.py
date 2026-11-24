"""NPC / gear / creature material kinds and their M_SkyMaster settings. Pure Python (no `unreal`), so tools can check coverage
offline (tools/npc_material_coverage.py); remaster_materials applies the profiles.

classify(name) takes a Skyrim texture path ('textures\\armor\\hide\\m\\cuirasslight.dds'), a flattened material slot name
('textures_armor_hide_m_cuirasslight_dds') or a bare texture key ('cuirasslight', alias keys like 'f_cuirasslight') and returns
(kind, rule). rule == FALLBACK means nothing matched and the default cloth look was used: the coverage tool lists those.
Bare keys are resolved to their Skyrim path first (key_index: area2/npc/obj/*.mtl + area2/npc/tex_alias.json)."""
import json
import os
import re
import time

FALLBACK = "fallback"

# Detail textures (area2/tex/<stem>.png + <stem>_n.png): tools/fabric_detail.py, leather_detail.py, metal_detail.py, skin_detail.py
DETAIL_TEXTURES = ("fabric", "leatherdetail", "metaldetail", "skindetail")

# Per kind, every M_SkyMaster parameter an NPC instance sets:
#   detail / tiling / strength   close-range detail texture (None = off), DetailTiling, DetailStrength
#   detail2 / tiling2 / split    second detail where Skyrim's spec mask > split (metal plates, studs, buckles on leather armor);
#                                only used when the instance has a spec map (SpecMaskedDetail switch)
#   rough (matte, gloss)         roughness at spec mask 0 / 1; flat = roughness when there is no spec map (DefaultRoughness)
#   detail_rough                 roughness added where the detail texture is dark (grooves, pores, scratches)
#   metal                        metallic x spec mask (no spec map: x 0.5); specular = UE Specular (0.5 = 4 % F0)
#   shading                      None (default lit) | 'cloth' (sheen, fuzz = SubsurfaceTint x base, amount ClothFuzz) |
#                                'skin' (subsurface profile `sss_profile`) | 'foliage' (two-sided transmission, hair cards)
#   sss_tint                     SubsurfaceTint (cloth fuzz colour / transmission colour multiplier of base colour)
#   wet / puddles / snow         WetResponse (damp darkening + gloss), Puddles (mirror puddles on flat tops: never on bodies),
#                                SnowCover (weather snow on up-facing parts: shoulders, hoods, dragons' backs)
#   base_tint                    BaseTint multiplier (eyes and mouths have no occlusion mesh and read too bright)
#   opaque                       force opaque (eyes: the alpha of Skyrim eye textures is an env-map mask, not coverage)
_BASE = dict(detail=None, tiling=8.0, strength=0.0, detail2=None, tiling2=6.0, split=0.5, rough=(0.9, 0.3), flat=0.8,
             detail_rough=0.0, metal=0.0, specular=0.5, shading=None, fuzz=0.0, sss_tint=None, sss_profile=None,
             wet=1.0, puddles=0.0, snow=0.3, base_tint=1.0, opaque=False)


def _p(**kw):
    d = dict(_BASE)
    d.update(kw)
    return d


PROFILES = {
    # worn gear
    "cloth": _p(detail="fabric", tiling=14.0, strength=0.7, rough=(0.95, 0.7), flat=0.88, detail_rough=0.12, specular=0.35,
                shading="cloth", fuzz=0.45, sss_tint=(0.9, 0.9, 0.9), wet=1.0, snow=0.35),
    "fur": _p(detail="fabric", tiling=6.0, strength=0.45, rough=(0.98, 0.8), flat=0.92, detail_rough=0.1, specular=0.3,
              shading="cloth", fuzz=0.85, sss_tint=(1.0, 1.0, 1.0), wet=1.0, snow=0.5),
    "leather": _p(detail="leatherdetail", tiling=10.0, strength=0.75, rough=(0.85, 0.45), flat=0.65, detail_rough=0.25,
                  specular=0.45, wet=0.7, snow=0.3),
    "leather_armor": _p(detail="leatherdetail", tiling=10.0, strength=0.75, detail2="metaldetail", tiling2=6.0, split=0.6,
                        rough=(0.85, 0.35), flat=0.62, detail_rough=0.25, metal=0.6, specular=0.5, wet=0.7, snow=0.3),
    "metal_armor": _p(detail="leatherdetail", tiling=10.0, strength=0.6, detail2="metaldetail", tiling2=6.0, split=0.4,
                      rough=(0.8, 0.25), flat=0.45, detail_rough=0.2, metal=0.85, specular=0.5, wet=0.4, snow=0.25),
    "jewelry": _p(detail="metaldetail", tiling=3.0, strength=0.3, rough=(0.5, 0.15), flat=0.25, detail_rough=0.1, metal=1.0,
                  wet=0.2, snow=0.0),
    # bodies
    "skin": _p(detail="skindetail", tiling=18.0, strength=0.4, rough=(0.62, 0.38), flat=0.5, detail_rough=0.2, specular=0.35,
               shading="skin", sss_profile="SP_SkySkin", wet=0.35, snow=0.0),
    "skin_beast": _p(detail="skindetail", tiling=14.0, strength=0.3, rough=(0.7, 0.42), flat=0.58, detail_rough=0.15,
                     specular=0.35, shading="skin", sss_profile="SP_SkySkinBeast", wet=0.4, snow=0.1),
    "eye": _p(rough=(0.06, 0.04), flat=0.05, specular=0.5, base_tint=0.9, wet=0.0, snow=0.0, opaque=True),
    "mouth": _p(rough=(0.4, 0.15), flat=0.3, specular=0.45, base_tint=0.75, wet=0.0, snow=0.0, opaque=True),
    "hair": _p(rough=(0.6, 0.4), flat=0.5, specular=0.35, shading="foliage", sss_tint=(1.0, 0.78, 0.6), wet=0.3, snow=0.0),
    # creatures
    "creature_fur": _p(detail="fabric", tiling=4.0, strength=0.3, rough=(0.97, 0.75), flat=0.9, detail_rough=0.1, specular=0.3,
                       shading="cloth", fuzz=0.7, sss_tint=(1.0, 1.0, 1.0), wet=0.8, snow=0.5),
    "creature_hide": _p(detail="leatherdetail", tiling=6.0, strength=0.5, rough=(0.85, 0.5), flat=0.7, detail_rough=0.2,
                        specular=0.4, wet=0.6, snow=0.3),
    "creature_skin": _p(detail="skindetail", tiling=10.0, strength=0.35, rough=(0.7, 0.4), flat=0.55, detail_rough=0.15,
                        specular=0.35, shading="skin", sss_profile="SP_SkySkin", wet=0.35, snow=0.1),
    "creature_scale": _p(detail="leatherdetail", tiling=16.0, strength=0.5, rough=(0.75, 0.3), flat=0.55, detail_rough=0.2,
                         specular=0.45, wet=0.6, snow=0.4),
    "chitin": _p(detail="leatherdetail", tiling=6.0, strength=0.25, rough=(0.55, 0.2), flat=0.4, detail_rough=0.1,
                 specular=0.5, wet=0.5, snow=0.2),
    "bone": _p(detail="skindetail", tiling=8.0, strength=0.4, rough=(0.85, 0.6), flat=0.75, detail_rough=0.2, specular=0.4,
               wet=0.5, snow=0.3),
    "creature_metal": _p(detail="metaldetail", tiling=4.0, strength=0.5, rough=(0.7, 0.3), flat=0.5, detail_rough=0.2,
                         metal=0.9, wet=0.4, snow=0.25),
}

# textures\actors\<folder>\ -> kind (DLC folders 'dlc01'/'dlc02' are skipped to the next path part)
CREATURES = {
    "highlandcow": "creature_fur", "cow": "creature_fur", "canine": "creature_fur", "wolf": "creature_fur",
    "dog": "creature_fur", "bear": "creature_fur", "sabrecat": "creature_fur", "horse": "creature_fur",
    "deer": "creature_fur", "elk": "creature_fur", "goat": "creature_fur", "skeever": "creature_fur",
    "mammoth": "creature_fur", "troll": "creature_fur", "werewolfbeast": "creature_fur", "werewolf": "creature_fur",
    "fox": "creature_fur", "hare": "creature_fur", "chicken": "creature_fur", "deathhound": "creature_fur",
    "bristleback": "creature_fur", "boar": "creature_fur", "ambient": "creature_fur",
    "horker": "creature_hide", "draugr": "creature_hide", "netch": "creature_hide", "vampirebrute": "creature_hide",
    "giant": "creature_skin", "hagraven": "creature_skin", "falmer": "creature_skin", "riekling": "creature_skin",
    "vampirelord": "creature_skin", "lurker": "creature_skin", "seeker": "creature_skin", "atronachflame": "creature_skin",
    "wisp": "creature_skin", "witchlight": "creature_skin",
    "dragon": "creature_scale", "slaughterfish": "creature_scale", "atronachfrost": "creature_scale",
    "icewraith": "creature_scale",
    "mudcrab": "chitin", "frostbitespider": "chitin", "chaurus": "chitin", "chaurusflyer": "chitin", "ashhopper": "chitin",
    "skeleton": "bone", "dragonpriest": "bone", "spriggan": "bone", "gargoyle": "bone", "atronachstorm": "bone",
    "dwarvenspider": "creature_metal", "dwarvenspherecenturion": "creature_metal",
    "dwarvensteamcenturion": "creature_metal", "dwarvenballistacenturion": "creature_metal",
}

# textures\armor\<folder>\: mostly metal (plates, mail) vs mostly leather (studs and buckles via the spec-mask split)
METAL_ARMOR = {"iron", "steel", "steelplate", "dwarven", "orcish", "ebony", "daedric", "dragonplate", "blades", "ancientnord",
               "draugr", "silver", "stalhrim", "nordic", "nordiccarved", "dawnguard", "elven", "glass", "dragonbone",
               "steelsaxon"}
LEATHER_ARMOR = {"hide", "leather", "studded", "wolf", "stormcloaks", "imperial", "guards", "thievesguild", "darkbrotherhood",
                 "nightingale", "forsworn", "fur", "bandit", "scaled", "chitin", "dragonscale", "companions", "penitusoculatus",
                 "vampire", "bonemold", "shrouded", "linwe", "falmer", "morag", "dbarmor"}

_LEATHER_ITEM = r"boot|shoe|glove|gauntlet|belt|bracer|strap|satchel|bag"
_RULES = [  # (kind, regex on '_' + normalised name + '_'), first match wins
    ("hair", r"brow(?!n)|beard|lash|scalp|hair"),                         # not 'eyebrown' (brown eyes)
    ("eye", r"_eyes?_|_eye[a-z]"),
    ("mouth", r"mouth|teeth|tongue"),
    ("@creature", r"_actors_(?:dlc0\d_)?(?!character_)([a-z]+)_"),
    ("skin_beast", r"_actors_character_.*(?:argonian|khajiit)"),
    ("skin", r"facegendata|facetint|facedetails|_(?:fe)?male(?:body|hands|head|feet)|upperbody|headhuman|_actors_character_.*skin"),
    ("jewelry", r"amulet|circlet|necklace|jewel|_rings?(?:_|\d)"),
    ("fur", r"furshells|_shell_"),
    ("@armor", r"_armor_([a-z]+)_"),
    ("leather", r"_clothes_.*(?:%s)" % _LEATHER_ITEM),
    ("cloth", r"_clothes_"),
]
# bare keys with no known path
_KEY_RULES = [
    ("skin", r"^_[0-9a-f]{8}_$"),                                         # FaceGen face tint: <formid>.dds
    ("leather", _LEATHER_ITEM),
    ("metal_armor", r"plate|steel|iron|dwarven|ebony|daedric|chain|mail"),
    ("leather_armor", r"cuirass|helmet|helm|armor|armour"),
    ("cloth", r"robe|cloth|outfit|pant|shirt|dress|tunic|hood|hat|underwear|torso|apron|skirt"),
]


def normalise(name):
    s = name.lower().replace("\\", "_").replace("/", "_").replace(" ", "_").replace(".", "_")
    return "_" + s.strip("_") + "_"


def _armor_kind(folder, s):
    if folder in METAL_ARMOR:
        return "metal_armor", "armor:" + folder
    if folder in LEATHER_ARMOR:
        return ("metal_armor" if re.search(r"heavy|plate", s) and folder == "imperial" else "leather_armor"), "armor:" + folder
    if folder.startswith("amulet") or folder.startswith("ring"):
        return "jewelry", "armor:" + folder
    return ("metal_armor" if re.search(r"plate|heavy|steel|iron", s) else "leather_armor"), "armor?:" + folder


def classify_path(name):
    """(kind, rule) for a path or slot name; (None, None) when no rule matches."""
    s = normalise(name)
    for kind, rx in _RULES:
        m = re.search(rx, s)
        if not m:
            continue
        if kind == "@creature":
            c = m.group(1)
            if c in CREATURES:
                return CREATURES[c], "creature:" + c
            return "creature_hide", "creature?:" + c                       # unmapped creature: listed by the coverage tool
        if kind == "@armor":
            return _armor_kind(m.group(1), s)
        return kind, kind
    return None, None


_index = {"mt": None, "map": {}, "t": 0.0}


def key_index(area):
    """texture key -> Skyrim texture path, from every NPC/creature .mtl (+ alias keys). Re-read when any source changes
    (checked at most every 10 s: remaster_materials.configure asks once per material instance)."""
    if _index["mt"] is not None and time.time() - _index["t"] < 10.0:
        return _index["map"]
    _index["t"] = time.time()
    obj = os.path.join(area, "npc", "obj")
    alias = os.path.join(area, "npc", "tex_alias.json")
    try:
        files = [os.path.join(obj, f) for f in os.listdir(obj) if f.endswith(".mtl")]
    except OSError:
        files = []
    mt = (len(files), max([os.path.getmtime(f) for f in files] or [0]), os.path.getmtime(alias) if os.path.exists(alias) else 0)
    if _index["mt"] == mt:
        return _index["map"]
    d = {}
    for f in files:
        try:
            for line in open(f, encoding="latin1"):
                if line.startswith("# skyrim diffuse: "):
                    p = line[18:].strip()
                    stem = re.split(r"[\\/]", p)[-1].lower()
                    stem = stem[:-4] if stem.endswith(".dds") else stem
                    d.setdefault(stem, p)
        except OSError:
            pass
    if os.path.exists(alias):
        try:
            for slot, stem in json.load(open(alias)).items():
                d[stem.lower()] = slot
        except (OSError, ValueError):
            pass
    _index["mt"], _index["map"] = mt, d
    return d


def classify(name, area=None):
    """(kind, rule) for a path, slot name or bare texture key. Never None: unmatched names get ('cloth', FALLBACK)."""
    kind, rule = classify_path(name)
    if kind:
        return kind, rule
    if area and not re.search(r"[\\/]|^textures_", name.lower()):
        p = key_index(area).get(name.lower())
        if p:
            kind, rule = classify_path(p)
            if kind:
                return kind, rule
    s = normalise(name)
    for kind, rx in _KEY_RULES:
        if re.search(rx, s):
            return kind, "key:" + kind
    return "cloth", FALLBACK


def is_npc_key(key, area):
    """True for texture keys used by NPC / creature meshes (so world textures are never given an NPC profile)."""
    k = key.lower()
    return os.path.exists(os.path.join(area, "npc", "tex", k + ".png")) or k in key_index(area)
