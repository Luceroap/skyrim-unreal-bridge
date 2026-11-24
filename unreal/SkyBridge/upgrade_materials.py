# Rebuild every M_<texture> material as PBR (normal + roughness/metallic/AO when companion maps exist) and enable Nanite on meshes.
import unreal, glob, os

SRC = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
alpha = os.path.join(SRC, "tex", "alpha_masked.txt")
MASKED = set(open(alpha).read().split()) if os.path.exists(alpha) else set()
_fol = os.path.join(SRC, "tex", "foliage_textures.txt")
FOLIAGE = set(open(_fol).read().split()) if os.path.exists(_fol) else set()


def task(f):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = "/Game/Area2Tex"; t.automated = True; t.replace_existing = True; t.save = True
    return t


# 1. import companion maps
tasks = [task(f) for f in glob.glob(os.path.join(SRC, "tex", "*_n.png")) + glob.glob(os.path.join(SRC, "tex", "*_rmaos.png"))
         if not eal.does_asset_exist("/Game/Area2Tex/" + os.path.splitext(os.path.basename(f))[0])]
if tasks: at.import_asset_tasks(tasks)
for f in glob.glob(os.path.join(SRC, "tex", "*_n.png")):
    t = unreal.load_asset("/Game/Area2Tex/" + os.path.splitext(os.path.basename(f))[0])
    if t:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        t.set_editor_property("srgb", False); eal.save_loaded_asset(t)
for f in glob.glob(os.path.join(SRC, "tex", "*_rmaos.png")):
    t = unreal.load_asset("/Game/Area2Tex/" + os.path.splitext(os.path.basename(f))[0])
    if t:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
        t.set_editor_property("srgb", False); eal.save_loaded_asset(t)

# 2. rebuild materials
n_norm = n_orm = 0
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    key = os.path.splitext(os.path.basename(f))[0]
    if key.endswith("_n") or key.endswith("_rmaos") or key == "terrain_detail":
        continue
    m = unreal.load_asset("/Game/Area2Tex/M_" + key)
    base = unreal.load_asset("/Game/Area2Tex/" + key)
    if not isinstance(m, unreal.Material) or not base:
        continue
    mel.delete_all_material_expressions(m)
    m.set_editor_property("two_sided", True)
    d = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)
    d.set_editor_property("texture", base)
    mel.connect_material_property(d, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    if key.lower() in MASKED:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mel.connect_material_property(d, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    if key.lower() in FOLIAGE:   # light shines through leaves: two-sided foliage shading with a boosted subsurface colour
        try:
            m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
            sc = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, -420)
            sc2 = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -650, -480)
            sc2.set_editor_property("constant", unreal.LinearColor(1.6, 1.7, 0.9, 1.0))
            mel.connect_material_expressions(d, "RGB", sc, "A"); mel.connect_material_expressions(sc2, "", sc, "B")
            mel.connect_material_property(sc, "", unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        except Exception as e:
            unreal.log_warning("foliage shading failed: %s" % e)
    nt = unreal.load_asset("/Game/Area2Tex/" + key + "_n")
    if nt:
        n = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 100)
        n.set_editor_property("texture", nt)
        n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL); n_norm += 1
    rt = unreal.load_asset("/Game/Area2Tex/" + key + "_rmaos")
    if rt:
        r = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 400)
        r.set_editor_property("texture", rt)
        r.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        mel.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        mel.connect_material_property(r, "G", unreal.MaterialProperty.MP_METALLIC)
        mel.connect_material_property(r, "B", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION); n_orm += 1
    else:
        c = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 400)
        c.set_editor_property("r", 0.85)
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
unreal.log("PBR materials rebuilt: %d with normal maps, %d with rmaos" % (n_norm, n_orm))

# 3. Nanite on meshes
nan = 0
for p in glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2\*.uasset"):
    mesh = unreal.load_asset("/Game/Area2/" + os.path.splitext(os.path.basename(p))[0])
    if isinstance(mesh, unreal.StaticMesh):
        s = mesh.get_editor_property("nanite_settings")
        if not s.enabled:
            s.enabled = True
            mesh.set_editor_property("nanite_settings", s); eal.save_loaded_asset(mesh); nan += 1
unreal.log("NANITE enabled on %d meshes" % nan)

# 4. (re)assign materials on ALL meshes by slot name (fixes meshes whose texture was missing when they were first imported)
mats = {}
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    key = os.path.splitext(os.path.basename(f))[0]
    if key.endswith("_n") or key.endswith("_rmaos") or key.startswith("terrain"):
        continue
    mm = unreal.load_asset("/Game/Area2Tex/M_" + key)
    if mm: mats[key.lower()] = mm
fixed = 0
for p in glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2\*.uasset"):
    n = os.path.splitext(os.path.basename(p))[0]
    mesh = unreal.load_asset("/Game/Area2/" + n)
    if not isinstance(mesh, unreal.StaticMesh) or n == "terrain":
        continue
    changed = False
    for i, sm in enumerate(mesh.static_materials):
        slot = str(sm.material_slot_name).lower()
        for key, mm in mats.items():
            if slot.endswith("_" + key + "_dds") and sm.material_interface != mm:
                mesh.set_material(i, mm); changed = True; fixed += 1; break
    if changed: eal.save_loaded_asset(mesh)
unreal.log("REASSIGNED %d material slots" % fixed)

