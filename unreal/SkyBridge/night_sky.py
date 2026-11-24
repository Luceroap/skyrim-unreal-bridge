"""Moons, planets and aurora for the night sky of the live view (tasteful: two pale moons with phases, three small steady planets).
  apply(live, night=True)   build/spawn on first use, show at night, hide by day, aurora on at night
  remove()                  delete the actors
The objects hang inside the 1000 km star dome and are attached to it, so they follow the camera.  Angles are rough Skyrim-like placements."""
import math
import unreal

DEST = "/Game/NightSky"
FOLDER = "SkyBridge/NightSky"
AURORA, AURORA_SKY = 0.25, 8.0   # soft ribbons (1.0 floods the whole sky); sky brightness while the aurora is on
DIST = 3.0e7                     # cm (300 km): inside the 1000 km dome, far enough that walking around cannot shift them visibly
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary

# name, azimuth, elevation (deg), apparent size (deg), colour, brightness, phase light direction, craters(1)/flat(0)
BODIES = [
    ("Masser", 70.0, 36.0, 3.0, (0.95, 0.94, 0.90), 14.0, (0.80, -0.50, 0.30), 1),
    ("Secunda", 28.0, 52.0, 1.9, (0.85, 0.92, 1.00), 11.0, (-0.30, 0.90, 0.25), 1),
    ("PlanetVenus", 125.0, 18.0, 0.10, (1.00, 0.97, 0.86), 60.0, (1, 0, 0), 0),
    ("PlanetMars", 205.0, 30.0, 0.07, (1.00, 0.55, 0.36), 16.0, (1, 0, 0), 0),
    ("PlanetJupiter", 300.0, 44.0, 0.09, (1.00, 0.93, 0.80), 28.0, (1, 0, 0), 0),
]

MOON_HLSL = """
float2 u = UV * float2(8.0, 4.0);
float n = 0.0; float a = 0.5; float2 q = u;
for (int i = 0; i < 5; i++) {
    n += a * (sin(q.x * 1.7 + sin(q.y * 2.3)) * 0.5 + 0.5) * (sin(q.y * 1.3 + sin(q.x * 1.9 + i)) * 0.5 + 0.5);
    q = q * 2.03 + float2(1.7, 9.2); a *= 0.5;
}
float maria = smoothstep(0.30, 0.65, n);
float3 albedo = lerp(float3(0.32, 0.32, 0.34), float3(0.80, 0.79, 0.76), maria) * Color;
albedo = lerp(albedo, Color, Flat);
float lit = saturate(dot(normalize(N), normalize(SunDir)) * 1.25 + 0.03) + 0.02;
return albedo * lerp(1.0, lit, PhaseOn) * Intensity;
"""


def _e(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def build(rebuild=False):
    path = DEST + "/M_Celestial"
    if eal.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path)
        eal.delete_asset(path)
    E = unreal
    m = at.create_asset("M_Celestial", DEST, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", E.MaterialShadingModel.MSM_UNLIT)
    uv = _e(m, E.MaterialExpressionTextureCoordinate, -900, 0)
    nrm = _e(m, E.MaterialExpressionVertexNormalWS, -900, 100)
    col = _e(m, E.MaterialExpressionVectorParameter, -900, 200, parameter_name="Color", default_value=unreal.LinearColor(1, 1, 1, 1))
    sun = _e(m, E.MaterialExpressionVectorParameter, -900, 320, parameter_name="SunDir", default_value=unreal.LinearColor(1, 0, 0, 0))
    inten = _e(m, E.MaterialExpressionScalarParameter, -900, 440, parameter_name="Intensity", default_value=6.0)
    phase = _e(m, E.MaterialExpressionScalarParameter, -900, 520, parameter_name="PhaseOn", default_value=1.0)
    flat = _e(m, E.MaterialExpressionScalarParameter, -900, 600, parameter_name="Flat", default_value=0.0)
    c = _e(m, E.MaterialExpressionCustom, -450, 200, code=MOON_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3, description="Celestial")
    ins = []
    for n in ("UV", "N", "Color", "SunDir", "Intensity", "PhaseOn", "Flat"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    c.set_editor_property("inputs", ins)
    for src, n in ((uv, "UV"), (nrm, "N"), (col, "Color"), (sun, "SunDir"), (inten, "Intensity"), (phase, "PhaseOn"), (flat, "Flat")):
        mel.connect_material_expressions(src, "", c, n)
    mel.connect_material_property(c, "", E.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def _actors():
    return [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_folder_path() == FOLDER]


def remove():
    n = 0
    for a in _actors():
        a.destroy_actor(); n += 1
    return n


def _spawn(live, mat):
    sphere = unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    base = live.sky_dome.get_actor_location() if getattr(live, "sky_dome", None) else unreal.Vector(0, 0, 0)
    for name, az, el, size, col, br, sdir, craters in BODIES:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, base)
        a.set_actor_label(name); a.set_folder_path(FOLDER)
        c = a.static_mesh_component
        c.set_static_mesh(sphere)
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_cast_shadow(False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        azr, elr = math.radians(az), math.radians(el)
        d = unreal.Vector(math.cos(elr) * math.cos(azr), math.cos(elr) * math.sin(azr), math.sin(elr))
        a.set_actor_location(unreal.Vector(base.x + d.x * DIST, base.y + d.y * DIST, base.z + d.z * DIST), False, False)
        diam = 2.0 * DIST * math.tan(math.radians(size) / 2.0)
        a.set_actor_scale3d(unreal.Vector(diam / 100.0, diam / 100.0, diam / 100.0))
        mi = c.create_dynamic_material_instance(0, mat)
        mi.set_vector_parameter_value("Color", unreal.LinearColor(col[0], col[1], col[2], 1.0))
        mi.set_vector_parameter_value("SunDir", unreal.LinearColor(sdir[0], sdir[1], sdir[2], 0.0))
        mi.set_scalar_parameter_value("Intensity", br)
        mi.set_scalar_parameter_value("PhaseOn", 1.0 if craters else 0.0)
        mi.set_scalar_parameter_value("Flat", 0.0 if craters else 1.0)
        try:
            if getattr(live, "sky_dome", None):
                a.attach_to_actor(live.sky_dome, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        except Exception:
            pass


def apply(live, night=True, aurora=True):
    mat = build()
    if not _actors():
        _spawn(live, mat)
    for a in _actors():
        a.set_is_temporarily_hidden_in_editor(not night)
    try:
        live.night_mid.set_scalar_parameter_value("Aurora", AURORA if (night and aurora) else 0.0)
        if night and aurora:
            live.night_mid.set_scalar_parameter_value("Intensity", AURORA_SKY)
    except Exception:
        pass
    return "moons/planets %s, aurora %s" % ("on" if night else "hidden", "on" if (night and aurora) else "off")
