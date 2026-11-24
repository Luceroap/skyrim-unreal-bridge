"""Helpers used by live_bridge.py to import one converted model (FBX) with its materials, inside the editor."""
import os, glob, shutil
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary


def _lines(name):
    p = os.path.join(AREA, "tex", name)
    return set(open(p).read().split()) if os.path.exists(p) else set()


def _task(f, dest):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    return t


def _texture(key):
    path = "/Game/Area2Tex/" + key
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    png = os.path.join(AREA, "tex", key + ".png")
    if not os.path.exists(png):
        return None
    at.import_asset_tasks([_task(png, "/Game/Area2Tex")])
    t = unreal.load_asset(path)
    if t and key.endswith("_n"):
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); t.set_editor_property("srgb", False); eal.save_loaded_asset(t)
    elif t and key.endswith("_rmaos"):
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); t.set_editor_property("srgb", False); eal.save_loaded_asset(t)
    return t


def material_for(key):
    try:
        import remaster_materials
        mi = remaster_materials.instance_for(key)
        if mi:
            return mi
    except Exception as e:
        unreal.log_warning("[SkyBridgeLive] master material instance for %s failed: %s" % (key, e))
    return legacy_material_for(key)


def legacy_material_for(key):
    path = "/Game/Area2Tex/M_" + key
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    base = _texture(key)
    if not base:
        return None
    masked, foliage = _lines("alpha_masked.txt"), _lines("foliage_textures.txt")
    m = at.create_asset("M_" + key, "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)
    d = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)
    d.set_editor_property("texture", base)
    mel.connect_material_property(d, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    if key.lower() in masked:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mel.connect_material_property(d, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    if key.lower() in foliage:
        try:
            m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
            mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, -420)
            c = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -650, -480)
            c.set_editor_property("constant", unreal.LinearColor(1.6, 1.7, 0.9, 1.0))
            mel.connect_material_expressions(d, "RGB", mul, "A"); mel.connect_material_expressions(c, "", mul, "B")
            mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
        except Exception:
            pass
    nt = _texture(key + "_n")
    if nt:
        n = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 100)
        n.set_editor_property("texture", nt); n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    rt = _texture(key + "_rmaos")
    if rt:
        r = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 400)
        r.set_editor_property("texture", rt); r.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        mel.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        mel.connect_material_property(r, "G", unreal.MaterialProperty.MP_METALLIC)
        mel.connect_material_property(r, "B", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    else:
        c = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 400)
        c.set_editor_property("r", 0.85); mel.connect_material_property(c, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def hidden_material():
    path = "/Game/Area2Tex/M_Hidden"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    m = at.create_asset("M_Hidden", "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    z = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 0)
    z.set_editor_property("r", 0.0); mel.connect_material_property(z, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def import_model(name):
    """Import area2/export/<name>.fbx as /Game/Area2/<name> and give each slot its textured material."""
    if not eal.does_asset_exist("/Game/Area2/" + name):
        at.import_asset_tasks([_task(os.path.join(AREA, "export", name + ".fbx"), "/Game/Area2")])
    mesh = unreal.load_asset("/Game/Area2/" + name)
    if not isinstance(mesh, unreal.StaticMesh):
        return
    for i, sm in enumerate(mesh.static_materials):
        m = slot_material(str(sm.material_slot_name))
        if m: mesh.set_material(i, m)
    eal.save_loaded_asset(mesh)


def slot_material(slot):
    """Material for an imported FBX slot name ('..._<texture key>_dds[_ncl_...]'), or None when its texture is missing."""
    slot = slot.lower()
    if slot in ("null", "none"):
        return hidden_material()
    base = slot.split("_ncl_")[0]
    if not base.endswith("_dds"):
        return None
    if base.startswith("textures_effects_"):
        return hidden_material()        # effect cards (heat haze, glow, vapor): Skyrim's effect shader, not a colour map
    for cand in glob.glob(os.path.join(AREA, "tex", "*.png")):
        k = os.path.splitext(os.path.basename(cand))[0]
        if k.endswith(("_n", "_rmaos")): continue
        kn = k.replace(" ", "_")
        if base.endswith("_" + kn.lower() + "_dds"):
            if kn != k:                 # unreal renames 'old wood 24.png' to old_wood_24 on import
                for suf in ("", "_n", "_s", "_rmaos"):
                    src, dst = (os.path.join(AREA, "tex", x + suf + ".png") for x in (k, kn))
                    if os.path.exists(src) and not os.path.exists(dst):
                        shutil.copyfile(src, dst)
            return material_for(kn)
    if base.endswith("_n_dds"):
        return hidden_material()        # only a normal map: an effect card, the raw import renders rainbow
    return None
