"""Full-resolution LAND terrain with blended landscape layers (tools/land_terrain.py -> area2/landterrain/), live in the editor.

  spawn(live, max_new=None)  import (if needed) + place every tile of tiles.json whose FBX exists, nearest first;
                             returns the number still pending (max_new limits the imports per call)
  tick(live)                 incremental spawn (one tile per call) + hides the tiles inside interior cells
  update(live, cam, dt)      add-on hook (area2/addons.txt): tick, then swap(on=True) once every tile is placed
  reimport_weights()         re-import the weight maps in place after tools/land_terrain.py rewrote them
  swap(live, on=True)        on: new terrain at its real height, old baked terrain (/Game/Area2/terrain) hidden, Skyrim's LOD
                             terrain replaced by the trimmed copy (landlod, no triangles over the full-resolution cells).
                             off: back to the old terrain; the new tiles sit SINK units lower so the old one wins where both
                             exist and the new one only shows where the old had no cells (water cells) - no z-fighting.
  clear(live)                destroy the new actors and undo the swap

Assets: /Game/LandTerrain/M_LandTerrain (+ MI_LT_<x>_<y>), Mesh/LT_<x>_<y>, Tex/<layer key>[_n], Weights/LTW_<x>_<y>_<i>.
Material: up to 16 layers per tile (4 RGBA weight textures), height-aware blend (layer height = colour alpha), only layers
with weight are sampled (dynamic branch), normal maps, VCLR tint, MPC_Weather wetness/puddles/snow like M_SkyMaster."""
import json, math, os, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
OUT = os.path.join(AREA, "landterrain")
DEST = "/Game/LandTerrain"
FOLDER = "SkyBridge/LandTerrain"
U = 1.4287
SINK = 10.0                         # Skyrim units below the old terrain while it is still shown
NL = 16
MAT_VERSION = 3
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
E = unreal
MP = unreal.MaterialProperty
STATE = {"actors": {}, "swapped": False, "hidden_old": [], "lod": None, "interior": None, "meta": None}


def log(msg):
    unreal.log("[LandTerrain] " + msg)


def _task(path, dest, name=None, options=None):
    t = unreal.AssetImportTask()
    t.filename = path; t.destination_path = dest; t.automated = True; t.replace_existing = False; t.save = True
    if name: t.destination_name = name
    if options: t.options = options
    return t


def _fbx_options():
    ui = unreal.FbxImportUI()
    for k, v in (("import_mesh", True), ("import_as_skeletal", False), ("import_materials", False), ("import_textures", False),
                 ("import_animations", False), ("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)):
        try: ui.set_editor_property(k, v)
        except Exception as e: log("fbx option %s: %s" % (k, e))
    sd = ui.static_mesh_import_data
    for k, v in (("combine_meshes", True), ("generate_lightmap_u_vs", False), ("auto_generate_collision", False),
                 ("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE),
                 ("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS), ("build_nanite", False)):
        try: sd.set_editor_property(k, v)
        except Exception as e: log("fbx option %s: %s" % (k, e))
    return ui


def texture(key, kind, reimport=False):
    """kind: color | normal | weight. Weight maps keep layer 3 in alpha; tools/land_terrain.py writes alpha >= 1 because
    Unreal's PNG import overwrites the RGB (layers 0-2) of alpha-0 pixels."""
    sub = "Weights" if kind == "weight" else "Tex"
    path = "%s/%s/%s" % (DEST, sub, key)
    if reimport or not eal.does_asset_exist(path):
        png = os.path.join(OUT, "tex", key + ".png")
        if not os.path.exists(png):
            return None
        t = _task(png, DEST + "/" + sub)
        t.replace_existing = reimport
        at.import_asset_tasks([t])
        t = unreal.load_asset(path)
        if t is None:
            return None
        if kind == "normal":
            t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            t.set_editor_property("srgb", False)
        elif kind == "weight":
            t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
            t.set_editor_property("srgb", False)
            t.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            t.set_editor_property("never_stream", True)
        eal.save_loaded_asset(t)
        return t
    return unreal.load_asset(path)


def _e(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def _custom(m, x, y, code, inputs, out_type, extra=(), desc=""):
    c = _e(m, E.MaterialExpressionCustom, x, y, code=code, output_type=out_type, description=desc)
    ins = []
    for n in inputs:
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    c.set_editor_property("inputs", ins)
    outs = []
    for n, t in extra:
        co = E.CustomOutput(); co.set_editor_property("output_name", n); co.set_editor_property("output_type", t); outs.append(co)
    if outs:
        c.set_editor_property("additional_outputs", outs)
    return c


def blend_hlsl():
    """Height-aware blend of NL layers. Only layers with weight are sampled; one (anisotropic, wrapping) sampler for all."""
    s = ["float4 wv[4];",
         "wv[0] = WA.SampleLevel(L0Sampler, WUV, 0); wv[1] = WB.SampleLevel(L0Sampler, WUV, 0);",
         "wv[2] = WC.SampleLevel(L0Sampler, WUV, 0); wv[3] = WD.SampleLevel(L0Sampler, WUV, 0);",
         "float2 dx = ddx(UV), dy = ddy(UV);",
         "float mx = -10.0;"]
    for i in range(NL):
        s.append("float w%d = wv[%d][%d]; float4 c%d = 0; float b%d = -10.0;" % (i, i // 4, i % 4, i, i))
        s.append("if (w%d > 0.004) { c%d = L%d.SampleGrad(L0Sampler, UV, dx, dy); b%d = w%d + c%d.a * Contrast; mx = max(mx, b%d); }"
                 % (i, i, i, i, i, i, i))
    s.append("float fs = 1e-5; float3 col = 0; float h = 0; float2 nxy = 0;")
    for i in range(NL):
        s.append("float f%d = max(b%d - mx + Soft, 0.0);" % (i, i))
        s.append("if (f%d > 0.0) { fs += f%d; col += f%d * c%d.rgb; h += f%d * c%d.a; "
                 "nxy += f%d * (N%d.SampleGrad(L0Sampler, UV, dx, dy).xy * 2.0 - 1.0); }" % ((i,) * 8))
    s += ["col /= fs; h /= fs; nxy /= fs;",
          "col = pow(max(col, 1e-5), 2.2);",          # Custom-node samples of these sRGB layers arrive undecoded (5x too bright)
          "NormalTS = float3(nxy * NormalStrength, sqrt(saturate(1.0 - dot(nxy, nxy))));",
          "Height = h;",
          "return col;"]
    return "\n".join(s)


WEATHER_HLSL = """
float3 c = Col * lerp(float3(1, 1, 1), pow(max(VC, 1e-4), 2.2) * VCGain, VCAmount);
float fade = saturate(1.0 - (Depth - 6000.0) / 10000.0);
float up = saturate(Up);
float damp = Wet * up * fade;
float n = Noise.x * 0.8 + Noise.y * 0.2;
float flat = saturate((up - 0.9) * 10.0);
float p = saturate(((n * 0.6 + (1.0 - H) * 0.4) - (1.0 - 0.6 * Wet)) * 10.0) * flat * fade;
c *= lerp(1.0, 0.6, damp) * lerp(1.0, 0.7, p);
float r = lerp(lerp(Rough0, 0.35, damp), 0.03, p);
float3 nn = normalize(lerp(Nrm, float3(0, 0, 1), p));
float s = Snow * saturate((up - 0.55) * 4.0) * saturate(1.4 - H * 0.8);
c = lerp(c, float3(0.85, 0.87, 0.9), s);
r = lerp(r, 0.65, s);
nn = normalize(lerp(nn, float3(0, 0, 1), s * 0.7));
Rough = r;
NormalOut = nn;
return c;
"""


def material(rebuild=False):
    path = DEST + "/M_LandTerrain"
    if eal.does_asset_exist(path) and not rebuild:
        m = unreal.load_asset(path)
        if "LTVersion%d" % MAT_VERSION in [str(n) for n in mel.get_scalar_parameter_names(m)]:
            return m
        rebuild = True
    if eal.does_asset_exist(path):
        m = unreal.load_asset(path)
        for ex in list(mel.get_material_expressions(m)):
            mel.delete_material_expression(m, ex)
    else:
        m = at.create_asset("M_LandTerrain", DEST, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", False)
    deftex = unreal.load_asset("/Engine/EngineResources/DefaultTexture")
    flat = unreal.load_asset("/Engine/EngineMaterials/FlatNormal")
    black = unreal.load_asset("/Engine/EngineResources/Black") or deftex
    names = ["UV", "WUV", "WA", "WB", "WC", "WD", "Contrast", "Soft", "NormalStrength"] + \
            ["L%d" % i for i in range(NL)] + ["N%d" % i for i in range(NL)]
    bl = _custom(m, -900, 0, blend_hlsl(), names, E.CustomMaterialOutputType.CMOT_FLOAT3,
                 (("NormalTS", E.CustomMaterialOutputType.CMOT_FLOAT3), ("Height", E.CustomMaterialOutputType.CMOT_FLOAT1)),
                 "LandBlend")
    tile = _e(m, E.MaterialExpressionScalarParameter, -1500, -500, parameter_name="LayerTiling", default_value=1.0)
    uv = _e(m, E.MaterialExpressionMultiply, -1300, -500)
    mel.connect_material_expressions(_e(m, E.MaterialExpressionTextureCoordinate, -1500, -600, coordinate_index=0), "", uv, "A")
    mel.connect_material_expressions(tile, "", uv, "B")
    mel.connect_material_expressions(uv, "", bl, "UV")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionTextureCoordinate, -1500, -400, coordinate_index=1), "", bl, "WUV")
    for i, n in enumerate(("WA", "WB", "WC", "WD")):
        p = _e(m, E.MaterialExpressionTextureObjectParameter, -1500, -300 + i * 80, parameter_name=n, texture=black)
        mel.connect_material_expressions(p, "", bl, n)
    for n, d, y in (("Contrast", 0.6, 40), ("Soft", 0.25, 120), ("NormalStrength", 1.0, 200)):
        mel.connect_material_expressions(_e(m, E.MaterialExpressionScalarParameter, -1500, y, parameter_name=n, default_value=d), "", bl, n)
    for i in range(NL):
        p = _e(m, E.MaterialExpressionTextureObjectParameter, -1800, -900 + i * 90, parameter_name="L%d" % i, texture=deftex)
        mel.connect_material_expressions(p, "", bl, "L%d" % i)
        p = _e(m, E.MaterialExpressionTextureObjectParameter, -2100, -900 + i * 90, parameter_name="N%d" % i, texture=flat,
               sampler_type=E.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        mel.connect_material_expressions(p, "", bl, "N%d" % i)
    # weather (MPC_Weather from remaster_materials / live_bridge)
    mpc = unreal.load_asset("/Game/Area2Tex/MPC_Weather")
    wx = _custom(m, -400, 0, WEATHER_HLSL, ["Col", "Nrm", "H", "Up", "Wet", "Snow", "Noise", "Depth", "VC", "VCAmount", "VCGain", "Rough0"],
                 E.CustomMaterialOutputType.CMOT_FLOAT3,
                 (("Rough", E.CustomMaterialOutputType.CMOT_FLOAT1), ("NormalOut", E.CustomMaterialOutputType.CMOT_FLOAT3)), "LandWeather")
    mel.connect_material_expressions(bl, "", wx, "Col")
    mel.connect_material_expressions(bl, "NormalTS", wx, "Nrm")
    mel.connect_material_expressions(bl, "Height", wx, "H")
    vn = _e(m, E.MaterialExpressionVertexNormalWS, -700, 300)
    up = _e(m, E.MaterialExpressionComponentMask, -600, 300, r=False, g=False, b=True, a=False)
    mel.connect_material_expressions(vn, "", up, ""); mel.connect_material_expressions(up, "", wx, "Up")
    for n, y in (("Wetness", 400), ("Snow", 480)):
        if mpc:
            p = _e(m, E.MaterialExpressionCollectionParameter, -700, y, collection=mpc, parameter_name=n)
        else:
            p = _e(m, E.MaterialExpressionConstant, -700, y, r=0.0)
        mel.connect_material_expressions(p, "", wx, "Wet" if n == "Wetness" else "Snow")
    wp = _e(m, E.MaterialExpressionWorldPosition, -1000, 560)
    wxy = _e(m, E.MaterialExpressionComponentMask, -900, 560, r=True, g=True, b=False, a=False)
    mel.connect_material_expressions(wp, "", wxy, "")
    puv = _e(m, E.MaterialExpressionDivide, -800, 560, const_b=700.0)
    mel.connect_material_expressions(wxy, "", puv, "A")
    noise = _e(m, E.MaterialExpressionTextureSample, -700, 560, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    pt = unreal.load_asset("/Game/Area2Tex/puddlenoise")
    noise.set_editor_property("texture", pt or deftex)
    mel.connect_material_expressions(puv, "", noise, "UVs")
    mel.connect_material_expressions(noise, "RGB", wx, "Noise")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionPixelDepth, -700, 700), "", wx, "Depth")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionVertexColor, -700, 780), "", wx, "VC")   # VertexColor's RGB output is unnamed
    for n, d, y in (("VCAmount", 1.0, 860), ("VCGain", 1.0, 920), ("Roughness", 0.85, 980)):
        mel.connect_material_expressions(_e(m, E.MaterialExpressionScalarParameter, -700, y, parameter_name=n, default_value=d), "",
                                         wx, "Rough0" if n == "Roughness" else n)
    _e(m, E.MaterialExpressionScalarParameter, -700, 1100, parameter_name="LTVersion%d" % MAT_VERSION, default_value=0.0)
    mel.connect_material_property(wx, "", MP.MP_BASE_COLOR)
    mel.connect_material_property(wx, "Rough", MP.MP_ROUGHNESS)
    mel.connect_material_property(wx, "NormalOut", MP.MP_NORMAL)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    log("built M_LandTerrain")
    return m


def meta():
    p = os.path.join(OUT, "tiles.json")
    if STATE["meta"] is None or STATE.get("meta_mtime") != os.path.getmtime(p):
        STATE["meta"] = json.load(open(p)); STATE["meta_mtime"] = os.path.getmtime(p)
    return STATE["meta"]


def reimport_weights():
    """Re-import every weight map in place (same assets, so the MI_LT_* instances keep their references)."""
    n = 0
    for name, info in meta().items():
        tx, ty = name.split("_")[1:3]
        for i in range((len(info["layers"]) + 3) // 4):
            if texture("LTW_%s_%s_%d" % (tx, ty, i), "weight", reimport=True):
                n += 1
    log("re-imported %d weight maps" % n)
    return n


def instance(name, info, parent):
    path = "%s/MI_%s" % (DEST, name)
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    mi = at.create_asset("MI_" + name, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    tx, ty = name.split("_")[1:3]
    for i in range((len(info["layers"]) + 3) // 4):
        w = texture("LTW_%s_%s_%d" % (tx, ty, i), "weight")
        if w: mel.set_material_instance_texture_parameter_value(mi, "W" + "ABCD"[i], w)
    for i, key in enumerate(info["layers"][:NL]):
        c = texture(key, "color")
        if c: mel.set_material_instance_texture_parameter_value(mi, "L%d" % i, c)
        n = texture(key + "_n", "normal")
        if n: mel.set_material_instance_texture_parameter_value(mi, "N%d" % i, n)
    eal.save_loaded_asset(mi)
    return mi


def mesh(name):
    path = "%s/Mesh/%s" % (DEST, name)
    if not eal.does_asset_exist(path):
        fbx = os.path.join(OUT, "fbx", name + ".fbx")
        if not os.path.exists(fbx):
            return None
        at.import_asset_tasks([_task(fbx, DEST + "/Mesh", name, _fbx_options())])
    m = unreal.load_asset(path)
    if not isinstance(m, unreal.StaticMesh):
        return None
    try:
        if not unreal.SkyBridgeViewLibrary.ensure_mesh_renderable(m):
            return None
    except Exception as e:
        log("ensure_mesh_renderable %s: %s" % (name, e))
    return m


def _camera_skyrim():
    try:
        loc, _rot = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
        return loc.y / U, loc.x / U
    except Exception:
        return 23000.0, -6000.0


def _alive(a):
    try:
        return a is not None and a.get_world() is not None
    except Exception:
        return False


def _find_existing():
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if str(a.get_folder_path()) == FOLDER:
            lab = a.get_actor_label()
            if lab.startswith("LandTerrain_"):
                STATE["actors"][lab[len("LandTerrain_"):]] = a
            elif lab == "LandTerrainLOD":
                STATE["lod"] = a


def spawn(live=None, max_new=None, names=None):
    """Place the tiles (nearest to the camera first). Returns how many tiles are still waiting."""
    if not STATE["actors"]:
        _find_existing()
    info = meta()
    parent = material()
    cx, cy = _camera_skyrim()
    todo = [n for n in info if (names is None or n in names) and not _alive(STATE["actors"].get(n))
            and os.path.exists(os.path.join(OUT, "fbx", n + ".fbx"))]
    todo.sort(key=lambda n: math.hypot(info[n]["origin"][0] + 8192 - cx, info[n]["origin"][1] + 8192 - cy))
    made = 0
    for n in todo:
        if max_new is not None and made >= max_new:
            break
        m = mesh(n)
        if m is None:
            log("no mesh for %s" % n); continue
        mi = instance(n, info[n], parent)
        z = 0.0 if STATE["swapped"] else -SINK * U
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, z), unreal.Rotator(yaw=90))
        c = a.static_mesh_component
        c.set_static_mesh(m)
        c.set_material(0, mi)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_actor_label("LandTerrain_" + n); a.set_folder_path(FOLDER)
        if STATE["interior"]:
            a.set_is_temporarily_hidden_in_editor(True)
        STATE["actors"][n] = a
        made += 1
    left = len(todo) - made
    log("spawned %d tiles, %d pending, swapped=%s" % (made, left, STATE["swapped"]))
    return left


def tick(live=None):
    """Call from live_bridge.tick: one tile per call until all are placed; follows interior cells like the old terrain."""
    interior = bool(getattr(live, "_interior", False)) if live is not None else False
    if interior != STATE["interior"]:
        STATE["interior"] = interior
        for a in list(STATE["actors"].values()) + [STATE["lod"]]:
            if _alive(a): a.set_is_temporarily_hidden_in_editor(interior)
    if STATE.get("done") and time.time() - STATE.get("checked", 0) < 30:
        return
    STATE["checked"] = time.time()
    STATE["done"] = spawn(live, max_new=1) == 0


def update(live=None, cam=None, dt=None):
    """Add-on hook (area2/addons.txt): place the tiles one per tick, then show them instead of the old baked terrain."""
    tick(live)
    if STATE.get("done") and not STATE["swapped"]:
        swap(live, True)


def _old_terrain_actors():
    """The baked terrain (/Game/Area2/terrain) and Skyrim's LOD terrain (/Game/Area2/lodterrain) placed by live_bridge."""
    old, lod = [], []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor) or str(a.get_folder_path()) != "SkyBridge/Terrain":
            continue
        m = a.static_mesh_component.static_mesh
        name = m.get_name() if m else ""
        if name == "terrain": old.append(a)
        elif name == "lodterrain": lod.append(a)
    return old, lod


def _lod_actor():
    """Skyrim's LOD terrain without the triangles over the full-resolution cells (tools/land_terrain.py --lod)."""
    if _alive(STATE["lod"]):
        return STATE["lod"]
    path = DEST + "/Mesh/landlod"
    fbx = os.path.join(OUT, "lod", "landlod.fbx")
    if not eal.does_asset_exist(path):
        if not os.path.exists(fbx):
            return None
        opts = _fbx_options()
        opts.set_editor_property("import_materials", False)
        at.import_asset_tasks([_task(fbx, DEST + "/Mesh", "landlod", opts)])
    m = unreal.load_asset(path)
    if not isinstance(m, unreal.StaticMesh):
        return None
    try:
        unreal.SkyBridgeViewLibrary.ensure_mesh_renderable(m)
    except Exception:
        pass
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(yaw=90))
    c = a.static_mesh_component
    c.set_static_mesh(m)
    for i, sm in enumerate(m.static_materials):                    # same per-tile instances as the original lodterrain
        key = str(sm.material_slot_name)
        mi = "/Game/Area2Tex/MI_" + key
        if eal.does_asset_exist(mi):
            c.set_material(i, unreal.load_asset(mi))
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_label("LandTerrainLOD"); a.set_folder_path(FOLDER)
    STATE["lod"] = a
    return a


def swap(live=None, on=True):
    """on: new terrain replaces the old (reversible with on=False). Hides via component visibility, so live_bridge's
    interior hiding (temporarily-hidden flag) does not undo it."""
    if not STATE["actors"]:
        _find_existing()
    old, lod = _old_terrain_actors()
    tamriel = bool(getattr(live, "_tamriel_on", False))         # tamriel_live already replaced Skyrim's LOD terrain
    new_lod = _lod_actor() if on and not tamriel else STATE["lod"]
    for a in old:
        a.static_mesh_component.set_visibility(not on)
    for a in lod:
        a.static_mesh_component.set_visibility(not (on and new_lod is not None))
    if _alive(new_lod):
        new_lod.static_mesh_component.set_visibility(on)
    z = 0.0 if on else -SINK * U
    for a in STATE["actors"].values():
        if _alive(a):
            a.set_actor_location(unreal.Vector(0, 0, z), False, False)
    STATE["swapped"] = on
    msg = "swap %s: old terrain %d, lod %d (replacement %s), new tiles %d" % (on, len(old), len(lod), bool(new_lod), len(STATE["actors"]))
    log(msg)
    return msg


def clear(live=None):
    swap(live, False)
    if not STATE["actors"]:
        _find_existing()
    n = 0
    for a in list(STATE["actors"].values()) + [STATE["lod"]]:
        if _alive(a):
            unreal.EditorLevelLibrary.destroy_actor(a); n += 1
    STATE["actors"].clear(); STATE["lod"] = None; STATE["done"] = False
    log("cleared %d actors" % n)
    return n
