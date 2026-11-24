"""Procedural fire for the live view: Skyrim streams each torch's LIGHT but not its flame, so lit lights get an animated flame here.
  build()      create /Game/FireFX/M_Flame (unlit additive: white-hot core -> orange -> red, wobbling tongue, per-torch phase)
  place(live)  one flame (two crossed planes) at every lit light between MIN_I and MAX_I; re-run after the lights change
  clear()      remove them again
Used by tools/showcase_shot.py; not part of the always-on bridge."""
import math
import unreal

DEST = "/Game/FireFX"
FOLDER = "SkyBridge/Fire"
MIN_I, MAX_I = 20.0, 400.0          # candela range of torch/brazier/candle lights (daylight ones are 0)
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary

FLAME_HLSL = """
float2 p = UV;
p.x = (p.x - 0.5) * 2.0;
float h = lerp(1.0 - p.y, p.y, Flip);            // 0 = base, 1 = tip
float seed = frac(sin(dot(Obj.xy, float2(12.9898, 78.233))) * 43758.5453);
float n = sin(h * 9.0 - T * 7.0 + seed * 20.0) * 0.5 + sin(h * 17.0 - T * 11.0 + seed * 7.0) * 0.25 + sin(h * 31.0 - T * 17.0 + seed * 3.0) * 0.12;
float w = (1.0 - h * 0.80) * 0.78;
float x = p.x + n * 0.20 * h;
float d = abs(x) / max(w, 0.001);
float tip = saturate(1.0 - h * h * 0.95 + 0.12 * n);
float body = saturate(1.0 - d * d) * tip * smoothstep(0.0, 0.07, h);
float flick = 0.82 + 0.18 * sin(T * 23.0 + seed * 50.0) * sin(T * 13.0 + seed * 5.0);
float core = pow(saturate(1.0 - d * 1.5), 2.0) * saturate(1.0 - h * 1.25);
float3 outer = float3(0.95, 0.20, 0.02);
float3 mid = float3(1.0, 0.50, 0.07);
float3 hot = float3(1.0, 0.78, 0.30);
float3 col = lerp(outer, mid, saturate(body * 1.5));
col = lerp(col, hot, core);
return float4(col * (1.6 + 2.4 * core) * flick, saturate(body * 1.1));
"""


def _e(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def build(rebuild=False):
    path = DEST + "/M_Flame"
    if eal.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        eal.delete_asset(path)
    m = at.create_asset("M_Flame", DEST, unreal.Material, unreal.MaterialFactoryNew())
    E = unreal
    m.set_editor_property("blend_mode", E.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("shading_model", E.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    uv = _e(m, E.MaterialExpressionTextureCoordinate, -900, 0)
    t = _e(m, E.MaterialExpressionTime, -900, 120)
    obj = _e(m, E.MaterialExpressionObjectPositionWS, -900, 240)
    flip = _e(m, E.MaterialExpressionScalarParameter, -900, 360, parameter_name="Flip", default_value=0.0)
    c = _e(m, E.MaterialExpressionCustom, -500, 100, code=FLAME_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT4, description="Flame")
    ins = []
    for n in ("UV", "T", "Obj", "Flip"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    c.set_editor_property("inputs", ins)
    for src, n in ((uv, "UV"), (t, "T"), (obj, "Obj"), (flip, "Flip")):
        mel.connect_material_expressions(src, "", c, n)
    rgb = _e(m, E.MaterialExpressionComponentMask, -250, 60, r=True, g=True, b=True, a=False)
    a = _e(m, E.MaterialExpressionComponentMask, -250, 200, r=False, g=False, b=False, a=True)
    mel.connect_material_expressions(c, "", rgb, ""); mel.connect_material_expressions(c, "", a, "")
    mel.connect_material_property(rgb, "", E.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(a, "", E.MaterialProperty.MP_OPACITY)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def _world():
    return unreal.EditorLevelLibrary.get_editor_world()


def clear():
    n = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            if a.get_folder_path() == FOLDER:
                a.destroy_actor(); n += 1
        except Exception:
            pass
    return n


def place(live, flip=0.0, scale=1.0):
    """Spawn flames at the currently lit lights. Returns how many."""
    clear()
    mat = build()
    plane = unreal.load_asset("/Engine/BasicShapes/Plane")
    n = 0
    for la in live.light_actors:
        try:
            comp = la.light_component
            i = comp.intensity
            if not (MIN_I <= i <= MAX_I):
                continue
            loc = la.get_actor_location()
        except Exception:
            continue
        h = 42.0 * scale * max(0.7, min(1.8, math.sqrt(i / 65.0)))     # flame height in cm
        for k, yaw in enumerate((0.0, 90.0)):
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(loc.x, loc.y, loc.z + h * 0.5))
            a.set_folder_path(FOLDER)
            a.set_actor_rotation(unreal.Rotator(roll=90.0, pitch=0.0, yaw=yaw), False)
            a.set_actor_scale3d(unreal.Vector(h / 100.0 * 0.8, h / 100.0, 1.0))
            sm = a.static_mesh_component
            sm.set_static_mesh(plane)
            mi = sm.create_dynamic_material_instance(0, mat)
            mi.set_scalar_parameter_value("Flip", float(flip))
            sm.set_cast_shadow(False)
            a.set_actor_enable_collision(False)
            n += 1
    return n
