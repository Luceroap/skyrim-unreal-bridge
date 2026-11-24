"""One master material for every Skyrim surface, with per-texture material instances.

M_SkyMaster: base colour (+ alpha mask), normal map, Skyrim's specular mask (normal-map alpha, area2/tex/<key>_s.png)
driving roughness, or Community Shaders PBR '_rmaos' maps, two-sided foliage subsurface, and a global wetness from
MPC_Weather (set by live_bridge from Skyrim's weather) that darkens and glosses upward-facing surfaces.
MI_<key> instances replace the old per-texture M_<key> materials (one shader set to compile instead of hundreds).

Batch conversion of existing meshes (editor closed, changing materials of meshes in use rebuilds their render data):
  UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=<this file>
"""
import os
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
DEST = "/Game/Area2Tex"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty


def log(msg):
    unreal.log("[SkyMaterials] " + msg)


def _lines(name):
    p = os.path.join(AREA, "tex", name)
    return set(open(p).read().split()) if os.path.exists(p) else set()


def _import_tex(key, kind):
    """kind: 'color' | 'normal' | 'masks' | 'linear'"""
    path = DEST + "/" + key
    if eal.does_asset_exist(path):
        t = unreal.load_asset(path)
    else:
        png = os.path.join(AREA, "tex", key + ".png")
        if not os.path.exists(png):
            return None
        task = unreal.AssetImportTask()
        task.filename = png; task.destination_path = DEST; task.automated = True; task.replace_existing = True; task.save = True
        at.import_asset_tasks([task])
        t = unreal.load_asset(path)
    if t is None:
        return None
    want = {"normal": (unreal.TextureCompressionSettings.TC_NORMALMAP, False),
            "masks": (unreal.TextureCompressionSettings.TC_MASKS, False),
            "linear": (unreal.TextureCompressionSettings.TC_DEFAULT, False),
            "color": (unreal.TextureCompressionSettings.TC_DEFAULT, True)}[kind]
    if t.get_editor_property("compression_settings") != want[0] or t.get_editor_property("srgb") != want[1]:
        t.set_editor_property("compression_settings", want[0]); t.set_editor_property("srgb", want[1])
        eal.save_loaded_asset(t)
    return t


def weather_collection():
    path = DEST + "/MPC_Weather"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    mpc = at.create_asset("MPC_Weather", DEST, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    params = []
    for n in ("Wetness", "Snow", "Rain"):
        p = unreal.CollectionScalarParameter()
        p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", 0.0)
        params.append(p)
    mpc.set_editor_property("scalar_parameters", params)
    eal.save_loaded_asset(mpc)
    return mpc


def _e(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


# -> float3(damp amount, puddle amount, albedo multiplier). Depth fade: full within 60 m, gone by 160 m.
# Walls = dampness of vertical faces (walls, trunks, leaves) relative to tops; undersides stay dry.
WET_HLSL = """
float fade = saturate(1.0 - (Depth - 6000.0) / 10000.0);
float w = Wet * saturate(Up * (1.0 - Walls) + Walls) * fade;
float n = Noise.x * 0.8 + Noise.y * 0.2;
float flat = saturate((Up - 0.85) * 8.0);
float p = saturate((n - (1.0 - 0.65 * Wet)) * 12.0) * flat * fade;
return float3(w, p, lerp(1.0, 0.62, w) * lerp(1.0, 0.6, p));
"""

# Z in cm (UE world). Snow fades in over 60 m above the snowline, ragged by the puddle noise, only on faces pointing up.
ALT_SNOW_HLSL = """
float n = Noise.x * 0.7 + Noise.y * 0.3;
float h = saturate((Z - Line + (n - 0.5) * 4000.0) / 6000.0);
return h * saturate((Up - 0.35) * 2.5);
"""

# Puddle normal: two panning wave layers + procedural raindrop rings (2 layers of 25 cm cells, one drop per cell with a
# random position and phase; each ring expands and fades over ~0.8 s). Pure ALU, no textures.
PUDDLE_NORMAL_HLSL = """
float2 rings = 0;
float2 uv = W / 25.0;
for (int l = 0; l < 2; l++)
{
    float2 q = uv + l * float2(0.37, 0.61);
    float2 cell = floor(q);
    float h = frac(sin(dot(cell + l * 7.0, float2(127.1, 311.7))) * 43758.5453);
    float t = frac(T * 1.25 + h);
    float2 d = frac(q) - 0.5 - (float2(frac(h * 17.0), frac(h * 31.0)) - 0.5) * 0.6;
    float r = length(d);
    float front = r - t * 0.45;
    float ring = sin(front * 70.0) * saturate(1.0 - abs(front) * 14.0) * (1.0 - t);
    rings += d / (r + 1e-4) * ring;
}
float2 waves = (R1.xy + R2.xy) * (0.1 + 0.25 * Rain);
float3 r = normalize(float3(waves + rings * Rain * Strength, 1.0));
return normalize(lerp(Nm, r, P));
"""

# Close-range grain (tools/detail_noise.py) tiled at Tiling x mesh UVs: full within 3 m of the camera, gone by 18 m.
# Whiteout blend of the detail normal onto the surface normal.
DETAIL_NORMAL_HLSL = """
float f = saturate(1.0 - (Depth - 300.0) / 1500.0) * S;
float3 d = lerp(float3(0, 0, 1), Dn, f);
return normalize(float3(Nm.xy + d.xy, Nm.z * d.z));
"""
DETAIL_COLOR_HLSL = """
float f = saturate(1.0 - (Depth - 300.0) / 1500.0) * S;
return lerp(1.0, Dc * 2.0, f);
"""


def master():
    """Load M_SkyMaster, (re)building its graph in place when missing or older than the current version (instances keep their parent)."""
    path = DEST + "/M_SkyMaster"
    if eal.does_asset_exist(path):
        m = unreal.load_asset(path)
        try:
            if "DetailStrength" in [str(n) for n in mel.get_scalar_parameter_names(m)] and                     "DetailNormalMap" in [str(n) for n in mel.get_texture_parameter_names(m)]:
                return m
        except Exception:
            return m
        mel.delete_all_material_expressions(m)
        log("upgrading M_SkyMaster graph")
    else:
        m = at.create_asset("M_SkyMaster", DEST, unreal.Material, unreal.MaterialFactoryNew())
    spec_default = next((_import_tex(f[:-4], "linear") for f in sorted(os.listdir(os.path.join(AREA, "tex"))) if f.endswith("_s.png")), None)
    rm_default = next((_import_tex(f[:-4], "masks") for f in sorted(os.listdir(os.path.join(AREA, "tex"))) if f.endswith("_rmaos.png")), None)
    mpc = weather_collection()
    m.set_editor_property("two_sided", True)
    E = unreal
    bc = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, -300, parameter_name="BaseColor",
            texture=unreal.load_asset("/Engine/EngineResources/DefaultTexture"))
    nm = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, 0, parameter_name="Normal",
            texture=unreal.load_asset("/Engine/EngineMaterials/FlatNormal"), sampler_type=E.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    # decals (moss etc.): Skyrim alpha-blends them (alpha 0.45-0.9) and fades their edges with vertex alpha, which the
    # converter drops; a plain cut-out would draw solid sheets. Keep only the dense part (moss in the cracks), dithered.
    dop = _e(m, E.MaterialExpressionCustom, -1150, -150, code="return saturate((A - 0.55) * 2.5);",
             output_type=E.CustomMaterialOutputType.CMOT_FLOAT1, description="DecalOpacity")
    ci = E.CustomInput(); ci.set_editor_property("input_name", "A"); dop.set_editor_property("inputs", [ci])
    mel.connect_material_expressions(bc, "A", dop, "A")
    dfn = unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA")
    if dfn:
        dith = _e(m, E.MaterialExpressionMaterialFunctionCall, -1000, -150)
        dith.set_material_function(dfn)
        mel.connect_material_expressions(dop, "", dith, "Alpha Threshold")
    else:
        dith = dop
    sw_op = _e(m, E.MaterialExpressionStaticSwitchParameter, -850, -150, parameter_name="IsDecal", default_value=False)
    mel.connect_material_expressions(dith, "", sw_op, "True"); mel.connect_material_expressions(bc, "A", sw_op, "False")
    mel.connect_material_property(sw_op, "", MP.MP_OPACITY_MASK)

    # roughness from Skyrim's specular mask: shiny (mask 1) -> 0.3, matte (mask 0) -> 0.9
    sp = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, 300, parameter_name="Spec", sampler_type=E.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    if spec_default: sp.set_editor_property("texture", spec_default)
    lr = _e(m, E.MaterialExpressionLinearInterpolate, -1100, 300, const_a=0.9, const_b=0.3)
    mel.connect_material_expressions(sp, "R", lr, "Alpha")
    nospec = _e(m, E.MaterialExpressionScalarParameter, -1100, 450, parameter_name="DefaultRoughness", default_value=0.8)
    sw_spec = _e(m, E.MaterialExpressionStaticSwitchParameter, -900, 350, parameter_name="HasSpec", default_value=False)
    mel.connect_material_expressions(lr, "", sw_spec, "True"); mel.connect_material_expressions(nospec, "", sw_spec, "False")

    rough_src, metal_src = sw_spec, None
    if rm_default:
        rm = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, 650, parameter_name="RMAOS",
                texture=rm_default, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_MASKS)
        sw_r = _e(m, E.MaterialExpressionStaticSwitchParameter, -700, 450, parameter_name="HasRMAOS", default_value=False)
        mel.connect_material_expressions(rm, "R", sw_r, "True"); mel.connect_material_expressions(sw_spec, "", sw_r, "False")
        zero = _e(m, E.MaterialExpressionConstant, -900, 750, r=0.0)
        one = _e(m, E.MaterialExpressionConstant, -900, 850, r=1.0)
        sw_m = _e(m, E.MaterialExpressionStaticSwitchParameter, -700, 700, parameter_name="HasRMAOS", default_value=False)
        mel.connect_material_expressions(rm, "G", sw_m, "True"); mel.connect_material_expressions(zero, "", sw_m, "False")
        sw_ao = _e(m, E.MaterialExpressionStaticSwitchParameter, -700, 900, parameter_name="HasRMAOS", default_value=False)
        mel.connect_material_expressions(rm, "B", sw_ao, "True"); mel.connect_material_expressions(one, "", sw_ao, "False")
        mel.connect_material_property(sw_m, "", MP.MP_METALLIC)
        mel.connect_material_property(sw_ao, "", MP.MP_AMBIENT_OCCLUSION)
        rough_src = sw_r

    # wetness on upward-facing surfaces (damp: darker, semi-gloss) + mirror puddles with rain ripples on flat ground,
    # both faded out with distance so far terrain does not turn into a white sky reflection
    wet = _e(m, E.MaterialExpressionCollectionParameter, -1100, -700, collection=mpc, parameter_name="Wetness")
    rainp = _e(m, E.MaterialExpressionCollectionParameter, -1100, -1000, collection=mpc, parameter_name="Rain")
    vn = _e(m, E.MaterialExpressionVertexNormalWS, -1300, -600)
    up = _e(m, E.MaterialExpressionComponentMask, -1150, -600, r=False, g=False, b=True, a=False)
    mel.connect_material_expressions(vn, "", up, "")
    upc = _e(m, E.MaterialExpressionSaturate, -1000, -600)
    mel.connect_material_expressions(up, "", upc, "")
    wpw = _e(m, E.MaterialExpressionWorldPosition, -1700, -1200)
    wxy = _e(m, E.MaterialExpressionComponentMask, -1550, -1200, r=True, g=True, b=False, a=False)
    mel.connect_material_expressions(wpw, "", wxy, "")
    pscale = _e(m, E.MaterialExpressionScalarParameter, -1550, -1300, parameter_name="PuddleScale", default_value=700.0)
    puv = _e(m, E.MaterialExpressionDivide, -1400, -1250)
    mel.connect_material_expressions(wxy, "", puv, "A"); mel.connect_material_expressions(pscale, "", puv, "B")
    ptex = _import_tex("puddlenoise", "linear")
    pn = _e(m, E.MaterialExpressionTextureSample, -1250, -1250, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    if ptex: pn.set_editor_property("texture", ptex)
    mel.connect_material_expressions(puv, "", pn, "UVs")
    depth = _e(m, E.MaterialExpressionPixelDepth, -1250, -1100)
    wc = _e(m, E.MaterialExpressionCustom, -950, -1100, code=WET_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
            description="WetPuddle")
    ins = []
    for n in ("Wet", "Up", "Noise", "Depth", "Walls"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    wc.set_editor_property("inputs", ins)
    mel.connect_material_expressions(wet, "", wc, "Wet"); mel.connect_material_expressions(up, "", wc, "Up")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionScalarParameter, -1250, -1000, parameter_name="WetWalls",
                                        default_value=0.35), "", wc, "Walls")
    mel.connect_material_expressions(pn, "RGB", wc, "Noise"); mel.connect_material_expressions(depth, "", wc, "Depth")
    wm = _e(m, E.MaterialExpressionComponentMask, -750, -1150, r=True, g=False, b=False, a=False)
    pud = _e(m, E.MaterialExpressionComponentMask, -750, -1050, r=False, g=True, b=False, a=False)
    dark = _e(m, E.MaterialExpressionComponentMask, -750, -950, r=False, g=False, b=True, a=False)
    for x in (wm, pud, dark):
        mel.connect_material_expressions(wc, "", x, "")
    rough = _e(m, E.MaterialExpressionLinearInterpolate, -550, 400, const_b=0.3)
    mel.connect_material_expressions(rough_src, "", rough, "A"); mel.connect_material_expressions(wm, "", rough, "Alpha")
    roughp = _e(m, E.MaterialExpressionLinearInterpolate, -450, 450, const_b=0.02)
    mel.connect_material_expressions(rough, "", roughp, "A"); mel.connect_material_expressions(pud, "", roughp, "Alpha")
    rough = roughp
    # close-range grain so stretched Skyrim textures do not look smeared at the player's feet
    dtile = _e(m, E.MaterialExpressionScalarParameter, -1700, 1500, parameter_name="DetailTiling", default_value=8.0)
    duv = _e(m, E.MaterialExpressionMultiply, -1550, 1450)
    mel.connect_material_expressions(_e(m, E.MaterialExpressionTextureCoordinate, -1700, 1400), "", duv, "A")
    mel.connect_material_expressions(dtile, "", duv, "B")
    dn = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, 1400, parameter_name="DetailNormalMap",
            sampler_type=E.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    dcol = _e(m, E.MaterialExpressionTextureSampleParameter2D, -1400, 1600, parameter_name="DetailColorMap",
              sampler_type=E.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    dn_t, dc_t = _import_tex("detailgrain_n", "normal"), _import_tex("detailgrain", "linear")
    if dn_t: dn.set_editor_property("texture", dn_t)
    if dc_t: dcol.set_editor_property("texture", dc_t)
    mel.connect_material_expressions(duv, "", dn, "UVs"); mel.connect_material_expressions(duv, "", dcol, "UVs")
    dstr = _e(m, E.MaterialExpressionScalarParameter, -1400, 1800, parameter_name="DetailStrength", default_value=0.6)
    dnc = _e(m, E.MaterialExpressionCustom, -1100, 1400, code=DETAIL_NORMAL_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
             description="DetailNormal")
    dcc = _e(m, E.MaterialExpressionCustom, -1100, 1600, code=DETAIL_COLOR_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT1,
             description="DetailColor")
    for node, names in ((dnc, ("Nm", "Dn", "Depth", "S")), (dcc, ("Dc", "Depth", "S"))):
        ins = []
        for n in names:
            ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
        node.set_editor_property("inputs", ins)
        mel.connect_material_expressions(depth, "", node, "Depth"); mel.connect_material_expressions(dstr, "", node, "S")
    mel.connect_material_expressions(nm, "RGB", dnc, "Nm"); mel.connect_material_expressions(dn, "RGB", dnc, "Dn")
    mel.connect_material_expressions(dcol, "R", dcc, "Dc")
    dark2 = _e(m, E.MaterialExpressionMultiply, -600, -950)
    mel.connect_material_expressions(dark, "", dark2, "A"); mel.connect_material_expressions(dcc, "", dark2, "B")

    base = _e(m, E.MaterialExpressionMultiply, -450, -300)
    mel.connect_material_expressions(bc, "RGB", base, "A"); mel.connect_material_expressions(dark2, "", base, "B")

    # puddle surface normal: flat water with two crossing ripple layers (Skyrim's water normal map) that strengthen with rain
    wn = _import_tex("skywater_n", "normal")
    rips = []
    for i, (scale, sx, sy) in enumerate(((90.0, 0.05, 0.03), (55.0, -0.04, 0.06))):
        d = _e(m, E.MaterialExpressionDivide, -1400, -1500 - i * 150, const_b=scale)
        mel.connect_material_expressions(wxy, "", d, "A")
        pan = _e(m, E.MaterialExpressionPanner, -1250, -1500 - i * 150, speed_x=sx, speed_y=sy)
        mel.connect_material_expressions(d, "", pan, "Coordinate")
        tx = _e(m, E.MaterialExpressionTextureSample, -1100, -1500 - i * 150, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if wn: tx.set_editor_property("texture", wn)
        mel.connect_material_expressions(pan, "", tx, "UVs")
        rips.append(tx)
    nc = _e(m, E.MaterialExpressionCustom, -800, -1500, code=PUDDLE_NORMAL_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
            description="PuddleNormal")
    ins = []
    for n in ("Nm", "R1", "R2", "P", "Rain", "W", "T", "Strength"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    nc.set_editor_property("inputs", ins)
    mel.connect_material_expressions(wxy, "", nc, "W")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionTime, -1000, -1650), "", nc, "T")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionScalarParameter, -1000, -1550, parameter_name="RippleStrength",
                                        default_value=0.9), "", nc, "Strength")
    mel.connect_material_expressions(dnc, "", nc, "Nm")
    mel.connect_material_expressions(rips[0], "RGB", nc, "R1"); mel.connect_material_expressions(rips[1], "RGB", nc, "R2")
    mel.connect_material_expressions(pud, "", nc, "P"); mel.connect_material_expressions(rainp, "", nc, "Rain")
    mel.connect_material_property(nc, "", MP.MP_NORMAL)

    # snow cover on near-horizontal tops
    snow = _e(m, E.MaterialExpressionCollectionParameter, -1100, -900, collection=mpc, parameter_name="Snow")
    sm1 = _e(m, E.MaterialExpressionConstantBiasScale, -1000, -800, bias=-0.6, scale=4.0)
    mel.connect_material_expressions(upc, "", sm1, "")
    sm2 = _e(m, E.MaterialExpressionSaturate, -900, -800)
    mel.connect_material_expressions(sm1, "", sm2, "")
    smask0 = _e(m, E.MaterialExpressionMultiply, -800, -850)
    mel.connect_material_expressions(snow, "", smask0, "A"); mel.connect_material_expressions(sm2, "", smask0, "B")
    # mountains/cliffs/rocks: permanent snow on upward faces above the snowline (Skyrim projects snow onto its mountains)
    alt = _e(m, E.MaterialExpressionCustom, -950, -1700, code=ALT_SNOW_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT1,
             description="AltitudeSnow")
    ins = []
    for n in ("Z", "Up", "Line", "Noise"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    alt.set_editor_property("inputs", ins)
    wz = _e(m, E.MaterialExpressionComponentMask, -1150, -1750, r=False, g=False, b=True, a=False)
    mel.connect_material_expressions(wpw, "", wz, "")
    line = _e(m, E.MaterialExpressionScalarParameter, -1150, -1650, parameter_name="SnowLine", default_value=12000.0)
    mel.connect_material_expressions(wz, "", alt, "Z"); mel.connect_material_expressions(up, "", alt, "Up")
    mel.connect_material_expressions(line, "", alt, "Line"); mel.connect_material_expressions(pn, "RGB", alt, "Noise")
    zero_s = _e(m, E.MaterialExpressionConstant, -950, -1600, r=0.0)
    sw_alt = _e(m, E.MaterialExpressionStaticSwitchParameter, -800, -1650, parameter_name="AltitudeSnow", default_value=False)
    mel.connect_material_expressions(alt, "", sw_alt, "True"); mel.connect_material_expressions(zero_s, "", sw_alt, "False")
    smask = _e(m, E.MaterialExpressionMax, -650, -850)
    mel.connect_material_expressions(smask0, "", smask, "A"); mel.connect_material_expressions(sw_alt, "", smask, "B")
    white = _e(m, E.MaterialExpressionConstant3Vector, -450, -750, constant=unreal.LinearColor(0.85, 0.87, 0.9, 1.0))
    base2 = _e(m, E.MaterialExpressionLinearInterpolate, -250, -350)
    mel.connect_material_expressions(base, "", base2, "A"); mel.connect_material_expressions(white, "", base2, "B")
    mel.connect_material_expressions(smask, "", base2, "Alpha")
    mel.connect_material_property(base2, "", MP.MP_BASE_COLOR)
    rough2 = _e(m, E.MaterialExpressionLinearInterpolate, -250, 400, const_b=0.65)
    mel.connect_material_expressions(rough, "", rough2, "A"); mel.connect_material_expressions(smask, "", rough2, "Alpha")
    mel.connect_material_property(rough2, "", MP.MP_ROUGHNESS)

    # foliage translucency colour (only used by the two-sided foliage shading model)
    tint = _e(m, E.MaterialExpressionConstant3Vector, -650, -150, constant=unreal.LinearColor(1.6, 1.7, 0.9, 1.0))
    sss = _e(m, E.MaterialExpressionMultiply, -450, -100)
    mel.connect_material_expressions(bc, "RGB", sss, "A"); mel.connect_material_expressions(tint, "", sss, "B")
    mel.connect_material_property(sss, "", MP.MP_SUBSURFACE_COLOR)

    # decals (Skyrim draws them with depth bias): move 1 cm toward the camera so they never z-fight the surface below
    cp = _e(m, E.MaterialExpressionCameraPositionWS, -1300, 1100)
    wpos = _e(m, E.MaterialExpressionWorldPosition, -1300, 1200)
    sub = _e(m, E.MaterialExpressionSubtract, -1100, 1150)
    mel.connect_material_expressions(cp, "", sub, "A"); mel.connect_material_expressions(wpos, "", sub, "B")
    nrm = _e(m, E.MaterialExpressionNormalize, -950, 1150)
    mel.connect_material_expressions(sub, "", nrm, "")
    push = _e(m, E.MaterialExpressionMultiply, -800, 1150)
    mel.connect_material_expressions(nrm, "", push, "A")
    mel.connect_material_expressions(_e(m, E.MaterialExpressionScalarParameter, -1000, 1250, parameter_name="DecalLift",
                                        default_value=1.0), "", push, "B")     # cm; ground layers need more (Nanite error)
    nothing = _e(m, E.MaterialExpressionConstant3Vector, -800, 1300, constant=unreal.LinearColor(0, 0, 0, 0))
    sw_d = _e(m, E.MaterialExpressionStaticSwitchParameter, -600, 1200, parameter_name="IsDecal", default_value=False)
    mel.connect_material_expressions(push, "", sw_d, "True"); mel.connect_material_expressions(nothing, "", sw_d, "False")
    mel.connect_material_property(sw_d, "", MP.MP_WORLD_POSITION_OFFSET)

    mel.recompile_material(m); eal.save_loaded_asset(m)
    log("built M_SkyMaster (spec default %s, rmaos default %s)" % (bool(spec_default), bool(rm_default)))
    return m


def rain_material():
    """Translucent falling-streak material for the rain curtains live_bridge keeps around the camera (strength = MPC Rain)."""
    path = DEST + "/M_RainCurtain"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    E = unreal
    mpc = weather_collection()
    m = at.create_asset("M_RainCurtain", DEST, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("two_sided", True)
    # lit by the scene (unlit emissive would be near-black under physical exposure)
    m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_VOLUMETRIC_NON_DIRECTIONAL)
    # area2/tex/rainstreaks.png: tiling thin streaks; curtain is ~25 m tall, 6 tiles -> ~0.5 m streaks falling ~9 m/s.
    # 3 tiles around a 4 m-radius curtain makes a 1-px streak ~8 mm wide: anything thinner is sub-pixel and mips away.
    uv = _e(m, E.MaterialExpressionTextureCoordinate, -1200, 0, u_tiling=3.0, v_tiling=6.0)
    pan = _e(m, E.MaterialExpressionPanner, -1000, 0, speed_x=0.0, speed_y=-2.2)
    mel.connect_material_expressions(uv, "", pan, "Coordinate")
    streaks = _import_tex("rainstreaks", "linear") or unreal.load_asset("/Engine/EngineMaterials/Good64x64TilingNoiseHighFreq")
    tx = _e(m, E.MaterialExpressionTextureSample, -800, 0, texture=streaks, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    mel.connect_material_expressions(pan, "", tx, "UVs")
    m.set_editor_property("enable_responsive_aa", True)               # keeps thin moving streaks from being smeared by TSR
    pw = _e(m, E.MaterialExpressionSaturate, -550, 0)
    mel.connect_material_expressions(tx, "R", pw, "")
    rain = _e(m, E.MaterialExpressionCollectionParameter, -800, 250, collection=mpc, parameter_name="Rain")
    op = _e(m, E.MaterialExpressionMultiply, -400, 100)
    mel.connect_material_expressions(pw, "", op, "A"); mel.connect_material_expressions(rain, "", op, "B")
    op2 = _e(m, E.MaterialExpressionMultiply, -250, 100, const_b=0.8)
    mel.connect_material_expressions(op, "", op2, "A")
    mel.connect_material_property(op2, "", MP.MP_OPACITY)
    col = _e(m, E.MaterialExpressionConstant3Vector, -400, -150, constant=unreal.LinearColor(0.8, 0.85, 0.9, 1.0))
    mel.connect_material_property(col, "", MP.MP_BASE_COLOR)
    rgh = _e(m, E.MaterialExpressionConstant, -400, -50, r=0.2)
    mel.connect_material_property(rgh, "", MP.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


RAIN_WPO = """
float3 I = Obj;
I.z -= T * (850.0 + 350.0 * R);
float3 d = I - Cam;
d.xy = (frac(d.xy / Box + 0.5) - 0.5) * Box;
d.z = (frac(d.z / Height + 0.5) - 0.5) * Height;
return Cam + d - Obj;
"""


RAIN_BOX, RAIN_HEIGHT = 1600.0, 1200.0       # cm; live_bridge spawns the streaks in the same box
RAIN_SCALE = (0.007, 0.007, 0.35)            # streak instance scale on the 1 m engine cylinder: 7 mm x 35 cm


def rain_streak_mesh():
    """Engine cylinder copy whose bounds cover the whole rain box: the material moves every streak (wrap + fall), so culling
    an instance at its spawn position would drop streaks that the shader places in view."""
    path = DEST + "/SM_RainStreak"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    m = eal.duplicate_asset("/Engine/BasicShapes/Cylinder", path)
    ext = unreal.Vector(2.0 * RAIN_BOX / RAIN_SCALE[0], 2.0 * RAIN_BOX / RAIN_SCALE[1], 2.0 * RAIN_HEIGHT / RAIN_SCALE[2])
    m.set_editor_property("positive_bounds_extension", ext)
    m.set_editor_property("negative_bounds_extension", ext)
    eal.save_loaded_asset(m)
    return m


def rain_drops_material(rebuild=False):
    """Falling streaks for SkyBridgeViewLibrary.SpawnRainField: each instance's position wraps into a box around the camera
    (world-locked, so walking through rain looks right) and falls at ~9-12 m/s; opacity = MPC Rain."""
    path = DEST + "/M_RainDrops"
    if eal.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        m = unreal.load_asset(path)
        mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset("M_RainDrops", DEST, unreal.Material, unreal.MaterialFactoryNew())
    E = unreal
    mpc = weather_collection()
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_VOLUMETRIC_NON_DIRECTIONAL)
    m.set_editor_property("enable_responsive_aa", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    cus = _e(m, E.MaterialExpressionCustom, -500, 400, code=RAIN_WPO, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
             description="RainWrap")
    ins = []
    for n in ("Obj", "Cam", "T", "R", "Box", "Height"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cus.set_editor_property("inputs", ins)
    src = {"Obj": _e(m, E.MaterialExpressionObjectPositionWS, -800, 300),
           "Cam": _e(m, E.MaterialExpressionCameraPositionWS, -800, 380),
           "T": _e(m, E.MaterialExpressionTime, -800, 460),
           "R": _e(m, E.MaterialExpressionPerInstanceRandom, -800, 540),
           "Box": _e(m, E.MaterialExpressionConstant, -800, 620, r=RAIN_BOX),
           "Height": _e(m, E.MaterialExpressionConstant, -800, 700, r=RAIN_HEIGHT)}
    for n, e in src.items():
        mel.connect_material_expressions(e, "", cus, n)
    mel.connect_material_property(cus, "", MP.MP_WORLD_POSITION_OFFSET)
    rain = _e(m, E.MaterialExpressionCollectionParameter, -800, 100, collection=mpc, parameter_name="Rain")
    depth = _e(m, E.MaterialExpressionPixelDepth, -800, 180)
    near = _e(m, E.MaterialExpressionDivide, -650, 180, const_b=250.0)            # no streaks smeared over the lens
    mel.connect_material_expressions(depth, "", near, "A")
    sat = _e(m, E.MaterialExpressionSaturate, -520, 180)
    mel.connect_material_expressions(near, "", sat, "")
    op = _e(m, E.MaterialExpressionMultiply, -400, 120)
    mel.connect_material_expressions(rain, "", op, "A"); mel.connect_material_expressions(sat, "", op, "B")
    op2 = _e(m, E.MaterialExpressionMultiply, -260, 120, const_b=0.28)
    mel.connect_material_expressions(op, "", op2, "A")
    mel.connect_material_property(op2, "", MP.MP_OPACITY)
    col = _e(m, E.MaterialExpressionConstant3Vector, -400, -150, constant=unreal.LinearColor(0.85, 0.88, 0.92, 1.0))
    mel.connect_material_property(col, "", MP.MP_BASE_COLOR)
    rgh = _e(m, E.MaterialExpressionConstant, -400, -50, r=0.1)
    mel.connect_material_property(rgh, "", MP.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


# V = camera vector (surface -> camera). Two star layers on a direction grid (one star per lit cell, random offset,
# colour and twinkle) + four drifting aurora curtains projected onto a flat sky ceiling. All emissive, additive.
NIGHT_SKY_HLSL = """
float3 d = -normalize(V);
if (d.z < -0.05) return 0;
float3 col = 0;
for (int l = 0; l < 2; l++)
{
    float s = l == 0 ? 160.0 : 380.0;
    float thr = l == 0 ? 0.982 : 0.965;
    float3 c = floor(d * s);
    float3 f = frac(d * s) - 0.5;
    float h = frac(sin(dot(c, float3(127.1, 311.7, 74.7))) * 43758.5453);
    float h2 = frac(sin(dot(c, float3(269.5, 183.3, 246.1))) * 43758.5453);
    if (h > thr)
    {
        float3 o = (float3(h2, frac(h2 * 7.13), frac(h2 * 3.71)) - 0.5) * 0.5;
        float b = saturate(1.0 - length(f - o) / 0.16);
        b = b * b * pow((h - thr) / (1.0 - thr), 2.0) * (l == 0 ? 3.0 : 1.2);
        b *= 0.75 + 0.25 * sin(T * (1.5 + h2 * 4.0) + h2 * 60.0);
        col += lerp(float3(0.7, 0.82, 1.0), float3(1.0, 0.85, 0.65), h2) * b;
    }
}
col *= saturate(d.z * 5.0 + 0.1);
if (Aurora > 0.001 && d.z > 0.02)
{
    float2 uv = d.xy / (d.z + 0.12);
    float a = 0;
    for (int i = 0; i < 4; i++)
    {
        float k = 1.0 + i * 0.37;
        float y = uv.y * 0.55 + 0.45 * sin(uv.x * 0.6 * k + T * 0.02 * k + i) - 0.6 + i * 0.3;
        float rays = pow(saturate(0.5 + 0.5 * sin(uv.x * 9.0 * k + sin(uv.x * 1.7 + T * 0.07) * 3.0 + T * 0.04)), 3.0);
        a += exp(-y * y * 7.0) * (0.35 + 0.65 * rays);
    }
    float3 ac = lerp(float3(0.08, 1.0, 0.4), float3(0.55, 0.15, 1.0), saturate(d.z * 1.6 - 0.35));
    col += ac * a * Aurora * 0.35 * saturate((d.z - 0.02) * 6.0);
}
return col * Night * Intensity;
"""


def night_sky_material(rebuild=False):
    """Sky dome material (Is Sky, unlit): the sky atmosphere's own luminance + sun/moon discs + stars and aurora
    (live_bridge drives Night/Aurora on a dynamic instance). A translucent dome gets fogged to nothing at sky distance;
    a sky material is drawn behind fog and volumetric clouds, so clouds cover the stars as they should."""
    path = DEST + "/M_NightSky"
    if eal.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        m = unreal.load_asset(path)
        mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset("M_NightSky", DEST, unreal.Material, unreal.MaterialFactoryNew())
    E = unreal
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("is_sky", True)
    cus = _e(m, E.MaterialExpressionCustom, -400, 0, code=NIGHT_SKY_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
             description="NightSky")
    ins = []
    for n in ("V", "T", "Night", "Aurora", "Intensity"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    cus.set_editor_property("inputs", ins)
    src = {"V": _e(m, E.MaterialExpressionCameraVectorWS, -800, -100),
           "T": _e(m, E.MaterialExpressionTime, -800, 0),
           "Night": _e(m, E.MaterialExpressionScalarParameter, -800, 100, parameter_name="Night", default_value=0.0),
           "Aurora": _e(m, E.MaterialExpressionScalarParameter, -800, 200, parameter_name="Aurora", default_value=0.0),
           "Intensity": _e(m, E.MaterialExpressionScalarParameter, -800, 300, parameter_name="Intensity", default_value=6.0)}
    for n, e in src.items():
        mel.connect_material_expressions(e, "", cus, n)
    total = _e(m, E.MaterialExpressionSkyAtmosphereViewLuminance, -400, -300)
    for i in (0, 1):                                                   # sun, moon
        disk = _e(m, E.MaterialExpressionSkyAtmosphereLightDiskLuminance, -400, -200 + 60 * i, light_index=i)
        add = _e(m, E.MaterialExpressionAdd, -200, -250 + 60 * i)
        mel.connect_material_expressions(total, "", add, "A"); mel.connect_material_expressions(disk, "", add, "B")
        total = add
    add = _e(m, E.MaterialExpressionAdd, -100, 0)
    mel.connect_material_expressions(total, "", add, "A"); mel.connect_material_expressions(cus, "", add, "B")
    mel.connect_material_property(add, "", MP.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def lod_water():
    """Import area2/export/lodwater.fbx (water layer of Skyrim's terrain LOD: rivers/lakes at their real heights)."""
    fbx = os.path.join(AREA, "export", "lodwater.fbx")
    if not os.path.exists(fbx):
        return
    task = unreal.AssetImportTask()
    task.filename = fbx; task.destination_path = "/Game/Area2"; task.automated = True; task.replace_existing = True; task.save = True
    at.import_asset_tasks([task])
    mesh = unreal.load_asset("/Game/Area2/lodwater")
    if not isinstance(mesh, unreal.StaticMesh):
        log("lodwater import failed"); return
    for i in range(len(mesh.static_materials)):
        mesh.set_material(i, water_material())
    eal.save_loaded_asset(mesh)
    log("lodwater imported")


def water_material(rebuild=False):
    """Single Layer Water (physically based absorption/scattering) with Skyrim's water normal map panned along the
    per-instance river flow. The graph lives in water_flow_apply.rebuild_water_material (Claude Code's file): it deletes
    every node first, so rebuilding never leaves a second SingleLayerWaterMaterialOutput behind."""
    path = DEST + "/M_SkyWater"
    if eal.does_asset_exist(path) and not rebuild:
        return unreal.load_asset(path)
    if not eal.does_asset_exist(path):
        at.create_asset("M_SkyWater", DEST, unreal.Material, unreal.MaterialFactoryNew())
    _import_tex("skywater_n", "normal")
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import water_flow_apply
    return water_flow_apply.rebuild_water_material()


def instance_for(key):
    path = DEST + "/MI_" + key
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    base = _import_tex(key, "color")
    if not base:
        return None
    parent = master()
    mi = at.create_asset("MI_" + key, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    mel.set_material_instance_texture_parameter_value(mi, "BaseColor", base)
    n = _import_tex(key + "_n", "normal")
    if n: mel.set_material_instance_texture_parameter_value(mi, "Normal", n)
    rm = _import_tex(key + "_rmaos", "masks")
    s = _import_tex(key + "_s", "linear") if not rm else None
    if rm:
        mel.set_material_instance_texture_parameter_value(mi, "RMAOS", rm)
        mel.set_material_instance_static_switch_parameter_value(mi, "HasRMAOS", True)
    elif s:
        mel.set_material_instance_texture_parameter_value(mi, "Spec", s)
        mel.set_material_instance_static_switch_parameter_value(mi, "HasSpec", True)
    configure(mi, key)
    return mi


# Ground layers the converter lists as decals: Skyrim fades them with vertex alpha (dropped by the converter), and their
# texture alpha is detail, so a cut-out punched see-through black holes into Whiterun's planters, roads and rock beds.
BLEND_LAYERS = {"wrfieldgrass01", "rocks01", "road01", "dirt02", "wrcitywalltopcap01", "woodedgetrim01"}


def npc_cloth(mi):
    """Clothes / armor / leather: woven-fabric close-range detail (tools/fabric_detail.py) instead of the generic grit,
    which looked like photocopier noise on cloth. Re-runnable."""
    fn, fc = _import_tex("fabric_n", "normal"), _import_tex("fabric", "linear")
    if fn is None or fc is None:
        return
    try:
        mel.set_material_instance_texture_parameter_value(mi, "DetailNormalMap", fn)
        mel.set_material_instance_texture_parameter_value(mi, "DetailColorMap", fc)
        mel.set_material_instance_scalar_parameter_value(mi, "DetailTiling", 14.0)
        mel.set_material_instance_scalar_parameter_value(mi, "DetailStrength", 0.7)
        mel.update_material_instance(mi)
        eal.save_loaded_asset(mi)
    except Exception as e:
        log("npc_cloth failed: %s" % e)


def configure(mi, key):
    """Blend mode / shading model / decal settings from the texture lists (re-runnable on existing instances)."""
    k = key.lower()
    npc_tex = os.path.join(AREA, "npc", "tex", k + ".png")
    if os.path.exists(npc_tex):
        # NPC armor and face textures are often stretched across a large UV island.
        # A stronger close-range detail layer restores cloth and leather relief without
        # increasing the global texture pool.
        mel.set_material_instance_scalar_parameter_value(mi, "DetailTiling", 11.0)
        mel.set_material_instance_scalar_parameter_value(mi, "DetailStrength", 0.82)
        mel.set_material_instance_scalar_parameter_value(mi, "DefaultRoughness", 0.68)
    layer = k in BLEND_LAYERS
    decal = k in _lines("decal_textures.txt") and not layer
    extra = k in _lines("alpha_masked_extra.txt")                 # tools/fill_textures.py (colour maps the converter missed)
    o = mi.get_editor_property("base_property_overrides")
    if layer:                                                      # opaque (mask ignored) but IsDecal keeps the 1 cm lift
        o.set_editor_property("override_blend_mode", False); o.set_editor_property("override_shading_model", False)
        mel.set_material_instance_static_switch_parameter_value(mi, "IsDecal", True)
        mel.set_material_instance_scalar_parameter_value(mi, "DecalLift", 8.0)
    elif k in _lines("alpha_masked.txt") or decal or extra:       # decals have soft alpha the cut-out heuristic misses
        o.set_editor_property("override_blend_mode", True); o.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    if layer:
        pass
    elif k in _lines("foliage_textures.txt") or (extra and any(s in k for s in ("branch", "addon", "leaf", "needle"))):
        try:
            o.set_editor_property("override_shading_model", True)
            o.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
        except Exception as e:
            log("shading model override: %s" % e)
    mi.set_editor_property("base_property_overrides", o)
    if decal:                                                      # only override when needed: each override is a shader permutation
        mel.set_material_instance_static_switch_parameter_value(mi, "IsDecal", True)
    if any(s in k for s in ("mountain", "cliff", "rock")) and not k.startswith("lodtex_"):
        mel.set_material_instance_static_switch_parameter_value(mi, "AltitudeSnow", True)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)


def npc_hair(mi):
    """Hair / brow / lash cards: two-sided cut-out with back-lit transmission (one-sided cards vanish from behind)."""
    o = mi.get_editor_property("base_property_overrides")
    o.set_editor_property("override_blend_mode", True); o.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    o.set_editor_property("override_two_sided", True); o.set_editor_property("two_sided", True)
    o.set_editor_property("override_opacity_mask_clip_value", True); o.set_editor_property("opacity_mask_clip_value", 0.4)
    o.set_editor_property("override_shading_model", True)
    o.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    mi.set_editor_property("base_property_overrides", o)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)


def hair_material():
    """M_SkyHair: NPC hair cards with UE's Hair shading model (anisotropic strand highlights + scatter), dithered cut-out,
    base colour = grey Skyrim hair texture x Tint (the NPC's hair colour, tools/npc_hair_tint.py). Strands run along V."""
    path = DEST + "/M_SkyHair"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    m = at.create_asset("M_SkyHair", DEST, unreal.Material, unreal.MaterialFactoryNew())
    E = unreal
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_HAIR)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("dither_opacity_mask", True)
    m.set_editor_property("opacity_mask_clip_value", 0.35)
    m.set_editor_property("used_with_skeletal_mesh", True)
    bc = _e(m, E.MaterialExpressionTextureSampleParameter2D, -900, -200, parameter_name="BaseColor",
            texture=unreal.load_asset("/Engine/EngineResources/DefaultTexture"))
    tint = _e(m, E.MaterialExpressionVectorParameter, -900, 50, parameter_name="Tint", default_value=unreal.LinearColor(1, 1, 1, 1))
    mul = _e(m, E.MaterialExpressionMultiply, -600, -150)
    mel.connect_material_expressions(bc, "RGB", mul, "A"); mel.connect_material_expressions(tint, "", mul, "B")
    mel.connect_material_property(mul, "", MP.MP_BASE_COLOR)
    mel.connect_material_property(bc, "A", MP.MP_OPACITY_MASK)
    tan = _e(m, E.MaterialExpressionConstant3Vector, -600, 100, constant=unreal.LinearColor(0, 1, 0, 0))
    mel.connect_material_property(tan, "", MP.MP_NORMAL)                 # Hair model: Normal input is the strand tangent
    mel.connect_material_property(_e(m, E.MaterialExpressionScalarParameter, -600, 200, parameter_name="Scatter", default_value=0.5), "", MP.MP_METALLIC)
    mel.connect_material_property(_e(m, E.MaterialExpressionScalarParameter, -600, 300, parameter_name="Specular", default_value=0.4), "", MP.MP_SPECULAR)
    mel.connect_material_property(_e(m, E.MaterialExpressionScalarParameter, -600, 400, parameter_name="Roughness", default_value=0.45), "", MP.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def hair_instance(key, tint):
    """MI_hair_<key>_<rrggbb> of M_SkyHair for texture area2/tex/<key>.png with linear tint (r, g, b)."""
    tag = "%02x%02x%02x" % tuple(int(round(max(0.0, min(1.0, c)) * 255)) for c in tint)
    name = "MI_hair_%s_%s" % (key, tag)
    path = DEST + "/" + name
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    tex = _import_tex(key, "color")
    if tex is None:
        return None
    mi = at.create_asset(name, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", hair_material())
    mel.set_material_instance_texture_parameter_value(mi, "BaseColor", tex)
    mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    return mi


def npc_skin(mi):
    """Body / head / hands: subsurface-profile skin (engine default Burley profile)."""
    o = mi.get_editor_property("base_property_overrides")
    if o.get_editor_property("shading_model") == unreal.MaterialShadingModel.MSM_SUBSURFACE_PROFILE and o.get_editor_property("override_shading_model"):
        return
    o.set_editor_property("override_shading_model", True)
    o.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SUBSURFACE_PROFILE)
    mi.set_editor_property("base_property_overrides", o)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)


def lod_terrain():
    """Import area2/export/lodterrain.fbx (tools/lod_terrain.py) as /Game/Area2/lodterrain with one instance per tile."""
    fbx = os.path.join(AREA, "export", "lodterrain.fbx")
    if not os.path.exists(fbx):
        return
    task = unreal.AssetImportTask()
    task.filename = fbx; task.destination_path = "/Game/Area2"; task.automated = True; task.replace_existing = True; task.save = True
    at.import_asset_tasks([task])
    mesh = unreal.load_asset("/Game/Area2/lodterrain")
    if not isinstance(mesh, unreal.StaticMesh):
        log("lodterrain import failed"); return
    hit = 0
    for i, sm in enumerate(mesh.static_materials):
        key = str(sm.material_slot_name)
        if not key.startswith("lodtex_"):
            continue
        mi = instance_for(key)
        if mi:
            mesh.set_material(i, mi); hit += 1
    eal.save_loaded_asset(mesh)
    log("lodterrain: %d/%d tiles textured" % (hit, len(mesh.static_materials)))


def fix_missing_slots():
    """Give mesh slots that never got an MI_ (their colour map was missing at import) one now. Headless only."""
    import ue_assets
    n = 0
    for p in eal.list_assets("/Game/Area2", recursive=False, include_folder=False):
        mesh = unreal.load_asset(p)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        dirty = False
        for i, sm in enumerate(mesh.static_materials):
            mat = sm.material_interface
            if mat is not None and mat.get_name().startswith(("MI_", "M_")):
                continue
            fix = ue_assets.slot_material(str(sm.material_slot_name))
            if fix:
                mesh.set_material(i, fix); dirty = True; n += 1
        if dirty:
            eal.save_loaded_asset(mesh)
    log("fixed %d mesh slots" % n)


def nanite_landscape():
    """Nanite for the mountains/rocks/trees the distant-world layer instances by the thousand. Headless only: toggling Nanite
    on a mesh in the live editor rebuilds it without derived data and the next render-resource init asserts (crash)."""
    n = 0
    for p in eal.list_assets("/Game/Area2", recursive=False, include_folder=False):
        if not p.split("/")[-1].startswith("landscape_"):
            continue
        mesh = unreal.load_asset(p)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        ns = mesh.get_editor_property("nanite_settings")
        if ns.get_editor_property("enabled"):
            continue
        ns.set_editor_property("enabled", True)
        mesh.set_editor_property("nanite_settings", ns)
        eal.save_loaded_asset(mesh); n += 1
    log("nanite enabled on %d landscape meshes" % n)


def ensure_usage(m):
    """Set usage flags up front; otherwise every instance sets them at runtime and dirties/recompiles the master."""
    changed = False
    for flag in ("used_with_nanite", "used_with_instanced_static_meshes"):
        try:
            if not m.get_editor_property(flag):
                m.set_editor_property(flag, True); changed = True
        except Exception as e:
            log("usage %s: %s" % (flag, e))
    if changed:
        mel.recompile_material(m); eal.save_loaded_asset(m)


def convert_all():
    """Point every slot of every /Game/Area2 mesh that uses an old M_<key> at MI_<key>."""
    ensure_usage(master())
    rain_material()
    rain_drops_material()
    rain_streak_mesh()
    night_sky_material()
    water_material()
    if os.environ.get("SKY_LOD_WATER") or not eal.does_asset_exist("/Game/Area2/lodwater"):
        lod_water()
    meshes = changed = 0
    for p in eal.list_assets("/Game/Area2", recursive=False, include_folder=False):
        mesh = unreal.load_asset(p)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        meshes += 1
        dirty = False
        for i, sm in enumerate(mesh.static_materials):
            mat = sm.material_interface
            if not isinstance(mat, unreal.Material):
                continue
            name = mat.get_name()
            if not name.startswith("M_") or name in ("M_Hidden", "M_SkyMaster") or name.startswith("M_terrain"):
                continue
            mi = instance_for(name[2:])
            if mi:
                mesh.set_material(i, mi); dirty = True
        if dirty:
            eal.save_loaded_asset(mesh); changed += 1
    log("converted %d of %d meshes" % (changed, meshes))
    n = 0
    for p in eal.list_assets(DEST, recursive=False, include_folder=False):
        if p.split("/")[-1].split(".")[0].startswith("MI_"):
            mi = unreal.load_asset(p)
            if isinstance(mi, unreal.MaterialInstanceConstant):
                configure(mi, mi.get_name()[3:]); n += 1
    log("reconfigured %d instances" % n)
    if os.environ.get("SKY_LOD_TERRAIN") or not eal.does_asset_exist("/Game/Area2/lodterrain"):
        lod_terrain()
    fix_missing_slots()
    nanite_landscape()
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reimport_textures.py")).read(), {"__name__": "reimport"})


if __name__ in ("__main__", "builtins") or os.environ.get("SKY_CONVERT_MATERIALS"):
    convert_all()
