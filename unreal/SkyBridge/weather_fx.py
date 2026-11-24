"""Weather effects that live_bridge's rain field does not cover: falling snow and rain splash rings.

Hook (live_bridge.Live, after update_sky in tick_body):
    import weather_fx; weather_fx.update(self, cam, dt)
and weather_fx.clear(self) when the bridge stops.

- Snow: SkyBridgeViewLibrary.SpawnRainField(SM_SnowFlake, M_SnowFlakes, ...) = one ISM actor of tiny planes. The material
  (Custom HLSL WPO) wraps every flake into a SNOW_BOX x SNOW_HEIGHT box around the camera (world-locked like M_RainDrops),
  turns it to face the camera, lets it fall/swirl, and adds a global wind drift that Python integrates (MPC DriftX/Y/Z,
  wrapped to the box so it stays small): a change in wind speed never makes the flakes jump. Opacity = MPC Snowfall,
  faded within ~2 m of the lens and at the box edges. The actor is only moved in whole box periods.
- Splashes: one DecalActor projecting straight down around the player's feet with M_RainSplash (deferred decal, DBuffer
  normal + roughness): procedural expanding impact rings in a world-locked grid, density and opacity = MPC Splash, only
  on near-horizontal surfaces (normal from depth derivatives), faded towards the decal edge. Works on slopes and stairs.
- Wet foliage: nothing here; M_SkyMaster's WetPuddle node already wets foliage instances (see COORDINATION.md).

Assets: /Game/WeatherFX/{MPC_WeatherFX, SM_SnowFlake, M_SnowFlakes, M_RainSplash}. Build/rebuild: build(rebuild=True).
Test overrides: FORCE["snow"|"rain"|"wind"] = value (None = Skyrim's weather).
"""
import math, os, struct, sys, time
import unreal

DEST = "/Game/WeatherFX"
SNOW_BOX, SNOW_HEIGHT = 2000.0, 1200.0       # cm; flakes wrap into this box around the camera
SNOW_COUNT = 14000                           # ~3 flakes per cubic metre
SNOW_SCALE = (0.035, 0.035, 1.0)             # on the 1 m engine plane: ~3.5 cm flakes (x0.7-1.3 per instance)
SPLASH_RADIUS, SPLASH_DEPTH = 1100.0, 450.0  # decal half extents (cm): 22 m across, +-4.5 m vertically around the feet
FORCE = {"snow": None, "rain": None, "wind": None}

at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty

_st = {}                                      # runtime state (actors, smoothed values, drift)


def log(msg):
    unreal.log("[WeatherFX] " + msg)


def _e(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def _custom(m, x, y, code, inputs, out, desc):
    c = _e(m, unreal.MaterialExpressionCustom, x, y, code=code, output_type=out, description=desc)
    ins = []
    for n in inputs:
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    c.set_editor_property("inputs", ins)
    return c


def _material(name, rebuild):
    """-> (material, build_graph). delete_all_material_expressions leaves old nodes behind, so a rebuild deletes and
    recreates the asset while no WeatherFX actor uses it (otherwise it clears the graph in place)."""
    path = DEST + "/" + name
    if eal.does_asset_exist(path):
        if not rebuild:
            return unreal.load_asset(path), False
        if _find("WeatherFX_Snow") or _find("WeatherFX_Splash"):
            m = unreal.load_asset(path)
            mel.delete_all_material_expressions(m)
            return m, True
        eal.delete_asset(path)
    m = at.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    if m is None:                                  # the deleted object can linger until garbage collection
        unreal.SystemLibrary.collect_garbage()
        m = at.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    if m is None and eal.does_asset_exist(path):
        m = unreal.load_asset(path)
        mel.delete_all_material_expressions(m)
    return m, True


# ------------------------------------------------------------------ assets
MPC_PARAMS = ("Snowfall", "Splash", "DriftX", "DriftY", "DriftZ")


def collection():
    path = DEST + "/MPC_WeatherFX"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    mpc = at.create_asset("MPC_WeatherFX", DEST, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    params = []
    for n in MPC_PARAMS:
        p = unreal.CollectionScalarParameter()
        p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", 0.0)
        params.append(p)
    mpc.set_editor_property("scalar_parameters", params)
    eal.save_loaded_asset(mpc)
    return mpc


def snow_mesh():
    """Engine plane copy whose bounds cover the whole snow box (the material moves every flake, see rain_streak_mesh)."""
    path = DEST + "/SM_SnowFlake"
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    m = eal.duplicate_asset("/Engine/BasicShapes/Plane", path)
    ext = unreal.Vector(2.0 * SNOW_BOX / SNOW_SCALE[0], 2.0 * SNOW_BOX / SNOW_SCALE[1], 2.0 * SNOW_HEIGHT / SNOW_SCALE[2])
    m.set_editor_property("positive_bounds_extension", ext)
    m.set_editor_property("negative_bounds_extension", ext)
    eal.save_loaded_asset(m)
    return m


# Camera-relative throughout (Rel = instance - camera, VO = vertex - instance) so large world coordinates lose no precision.
SNOW_WPO = """
float r2 = frac(R * 7.31 + 0.17);
float3 d = Rel + Drift;
d.z -= T * (12.0 + 30.0 * R);
d.x += 25.0 * sin(T * (0.5 + 0.7 * R) + R * 40.0);
d.y += 25.0 * cos(T * (0.4 + 0.7 * r2) + r2 * 40.0);
d.xy = (frac(d.xy / Box + 0.5) - 0.5) * Box;
d.z = (frac(d.z / Height + 0.5) - 0.5) * Height;
float3 v = normalize(-d + float3(0, 0, 0.001));
float3 rt = normalize(cross(float3(0, 0, 1), v) + float3(0.0001, 0, 0));
float3 up = cross(v, rt);
float3 p = d + rt * VO.x + up * VO.y;
return p - (Rel + VO);
"""

# pixel: soft round flake, faded near the lens and towards the box edges (where flakes wrap around)
SNOW_OPACITY = """
float2 q = UV - 0.5;
float disc = saturate(1.0 - dot(q, q) * 4.0);
disc *= disc;
float nearf = saturate((Depth - 60.0) / 180.0);
float edge = saturate((Box * 0.5 - length(Rel.xy)) / 350.0) * saturate((Height * 0.5 - abs(Rel.z)) / 250.0);
return disc * nearf * edge * Snow;
"""


def snow_material(rebuild=False):
    m, build_graph = _material("M_SnowFlakes", rebuild)
    if not build_graph:
        return m
    E = unreal
    mpc = collection()
    m.set_editor_property("blend_mode", E.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("translucency_lighting_mode", E.TranslucencyLightingMode.TLM_VOLUMETRIC_NON_DIRECTIONAL)
    m.set_editor_property("enable_responsive_aa", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    # WPO
    obj = _e(m, E.MaterialExpressionObjectPositionWS, -1300, 300)
    cam = _e(m, E.MaterialExpressionCameraPositionWS, -1300, 380)
    wp = _e(m, E.MaterialExpressionWorldPosition, -1300, 460)
    rel = _e(m, E.MaterialExpressionSubtract, -1100, 320)
    mel.connect_material_expressions(obj, "", rel, "A"); mel.connect_material_expressions(cam, "", rel, "B")
    vo = _e(m, E.MaterialExpressionSubtract, -1100, 440)
    mel.connect_material_expressions(wp, "", vo, "A"); mel.connect_material_expressions(obj, "", vo, "B")
    dx, dy, dz = (_e(m, E.MaterialExpressionCollectionParameter, -1300, 560 + 60 * i, collection=mpc, parameter_name=n)
                  for i, n in enumerate(("DriftX", "DriftY", "DriftZ")))
    dxy = _e(m, E.MaterialExpressionAppendVector, -1100, 580)
    mel.connect_material_expressions(dx, "", dxy, "A"); mel.connect_material_expressions(dy, "", dxy, "B")
    drift = _e(m, E.MaterialExpressionAppendVector, -950, 600)
    mel.connect_material_expressions(dxy, "", drift, "A"); mel.connect_material_expressions(dz, "", drift, "B")
    wpo = _custom(m, -700, 400, SNOW_WPO, ("Rel", "VO", "Drift", "T", "R", "Box", "Height"),
                  E.CustomMaterialOutputType.CMOT_FLOAT3, "SnowWrap")
    src = {"Rel": rel, "VO": vo, "Drift": drift, "T": _e(m, E.MaterialExpressionTime, -1100, 740),
           "R": _e(m, E.MaterialExpressionPerInstanceRandom, -1100, 800),
           "Box": _e(m, E.MaterialExpressionConstant, -1100, 860, r=SNOW_BOX),
           "Height": _e(m, E.MaterialExpressionConstant, -1100, 920, r=SNOW_HEIGHT)}
    for n, e in src.items():
        mel.connect_material_expressions(e, "", wpo, n)
    mel.connect_material_property(wpo, "", MP.MP_WORLD_POSITION_OFFSET)
    # opacity (pixel)
    pwp = _e(m, E.MaterialExpressionWorldPosition, -1300, -100)
    pcam = _e(m, E.MaterialExpressionCameraPositionWS, -1300, -20)
    prel = _e(m, E.MaterialExpressionSubtract, -1100, -60)
    mel.connect_material_expressions(pwp, "", prel, "A"); mel.connect_material_expressions(pcam, "", prel, "B")
    op = _custom(m, -700, 0, SNOW_OPACITY, ("UV", "Rel", "Depth", "Box", "Height", "Snow"),
                 E.CustomMaterialOutputType.CMOT_FLOAT1, "SnowOpacity")
    psrc = {"UV": _e(m, E.MaterialExpressionTextureCoordinate, -1100, -160), "Rel": prel,
            "Depth": _e(m, E.MaterialExpressionPixelDepth, -1100, 20),
            "Box": src["Box"], "Height": src["Height"],
            "Snow": _e(m, E.MaterialExpressionCollectionParameter, -1100, 100, collection=mpc, parameter_name="Snowfall")}
    for n, e in psrc.items():
        mel.connect_material_expressions(e, "", op, n)
    op2 = _e(m, E.MaterialExpressionMultiply, -450, 0, const_b=0.9)
    mel.connect_material_expressions(op, "", op2, "A")
    mel.connect_material_property(op2, "", MP.MP_OPACITY)
    col = _e(m, E.MaterialExpressionConstant3Vector, -450, -200, constant=unreal.LinearColor(0.92, 0.94, 0.97, 1.0))
    mel.connect_material_property(col, "", MP.MP_BASE_COLOR)
    mel.connect_material_property(_e(m, E.MaterialExpressionConstant, -450, -120, r=0.6), "", MP.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


# pixel, deferred decal. W = absolute world position (hash grid), Rel = W - camera (precise, for derivatives/fade).
# Three offset layers of 30 cm cells; an active cell (fraction = Rain) drops a ring that expands to 9 cm and fades.
# -> float4(ring normal slope xy, ring mask, flat-surface * distance fade)
SPLASH_HLSL = """
float3 gn = normalize(cross(ddx(Rel), ddy(Rel)));
float flat = saturate((abs(gn.z) - 0.75) * 6.0);
float fd = saturate(1.0 - length(Rel.xy - Feet.xy) / Radius);
fd = fd * fd * (3.0 - 2.0 * fd);
float2 g = 0;
float m = 0;
for (int l = 0; l < 3; l++)
{
    float2 p = W.xy / Cell + float2(0.37, 0.71) * (7.0 * l);
    float2 c = floor(p);
    float2 f = frac(p);
    float h1 = frac(sin(dot(c, float2(127.1, 311.7)) + l * 13.1) * 43758.5453);
    float h2 = frac(sin(dot(c, float2(269.5, 183.3)) + l * 7.7) * 43758.5453);
    float h3 = frac(h1 * 17.13 + h2 * 3.71);
    float h4 = frac(h1 * 5.37 + h2 * 11.9);
    float ph = frac(T * Rate * (0.75 + 0.5 * h3) + h4);
    float act = step(h4, Rain) * step(ph, 0.6);
    ph = ph / 0.6;
    float2 q = f - (0.3 + 0.4 * float2(h1, h2));
    float dd = length(q) + 0.0001;
    float x = (dd - (0.02 + ph * 0.28)) / 0.03;
    float a = exp(-x * x) * (1.0 - ph) * (1.0 - ph) * act;
    g += q / dd * (-2.0 * x * a);
    m = max(m, a);
}
return float4(g, m, flat * fd);
"""


def splash_material(rebuild=False):
    m, build_graph = _material("M_RainSplash", rebuild)
    if not build_graph:
        return m
    E = unreal
    mpc = collection()
    m.set_editor_property("blend_mode", E.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("material_domain", E.MaterialDomain.MD_DEFERRED_DECAL)
    wp = _e(m, E.MaterialExpressionWorldPosition, -1300, 0)
    cam = _e(m, E.MaterialExpressionCameraPositionWS, -1300, 80)
    rel = _e(m, E.MaterialExpressionSubtract, -1100, 40)
    mel.connect_material_expressions(wp, "", rel, "A"); mel.connect_material_expressions(cam, "", rel, "B")
    obj = _e(m, E.MaterialExpressionObjectPositionWS, -1300, 160)          # decal actor = player's feet
    feet = _e(m, E.MaterialExpressionSubtract, -1100, 160)
    mel.connect_material_expressions(obj, "", feet, "A"); mel.connect_material_expressions(cam, "", feet, "B")
    rain = _e(m, E.MaterialExpressionCollectionParameter, -1100, 260, collection=mpc, parameter_name="Splash")
    c = _custom(m, -800, 100, SPLASH_HLSL, ("W", "Rel", "Feet", "T", "Rain", "Cell", "Rate", "Radius"),
                E.CustomMaterialOutputType.CMOT_FLOAT4, "RainSplash")
    src = {"W": wp, "Rel": rel, "Feet": feet, "T": _e(m, E.MaterialExpressionTime, -1100, 320), "Rain": rain,
           "Cell": _e(m, E.MaterialExpressionConstant, -1100, 380, r=30.0),
           "Rate": _e(m, E.MaterialExpressionConstant, -1100, 440, r=1.1),
           "Radius": _e(m, E.MaterialExpressionConstant, -1100, 500, r=SPLASH_RADIUS)}
    for n, e in src.items():
        mel.connect_material_expressions(e, "", c, n)
    gxy = _e(m, E.MaterialExpressionComponentMask, -550, 0, r=True, g=True, b=False, a=False)
    ring = _e(m, E.MaterialExpressionComponentMask, -550, 100, r=False, g=False, b=True, a=False)
    fade = _e(m, E.MaterialExpressionComponentMask, -550, 200, r=False, g=False, b=False, a=True)
    for x in (gxy, ring, fade):
        mel.connect_material_expressions(c, "", x, "")
    gs = _e(m, E.MaterialExpressionMultiply, -400, 0, const_b=0.6)
    mel.connect_material_expressions(gxy, "", gs, "A")
    nrm = _e(m, E.MaterialExpressionAppendVector, -250, 0)
    one = _e(m, E.MaterialExpressionConstant, -400, 60, r=1.0)
    mel.connect_material_expressions(gs, "", nrm, "A"); mel.connect_material_expressions(one, "", nrm, "B")
    mel.connect_material_property(nrm, "", MP.MP_NORMAL)
    o1 = _e(m, E.MaterialExpressionMultiply, -400, 150)
    mel.connect_material_expressions(ring, "", o1, "A"); mel.connect_material_expressions(fade, "", o1, "B")
    o2 = _e(m, E.MaterialExpressionMultiply, -250, 150)
    mel.connect_material_expressions(o1, "", o2, "A"); mel.connect_material_expressions(rain, "", o2, "B")
    o3 = _e(m, E.MaterialExpressionMultiply, -120, 150, const_b=1.6)
    mel.connect_material_expressions(o2, "", o3, "A")
    sat = _e(m, E.MaterialExpressionSaturate, 0, 150)
    mel.connect_material_expressions(o3, "", sat, "")
    mel.connect_material_property(sat, "", MP.MP_OPACITY)
    mel.connect_material_property(_e(m, E.MaterialExpressionConstant, -250, 300, r=0.04), "", MP.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    return m


def build(rebuild=False):
    collection(); snow_mesh()
    return snow_material(rebuild), splash_material(rebuild)


# ------------------------------------------------------------------ runtime
def _world():
    return unreal.EditorLevelLibrary.get_editor_world()


def _set(name, value):
    key = "p_" + name
    if _st.get(key) is not None and abs(_st[key] - value) < 1e-4:
        return
    _st[key] = value
    try:
        unreal.MaterialLibrary.set_scalar_parameter_value(_world(), _st["mpc"], name, value)
    except Exception as e:
        log("param %s: %s" % (name, e))


def _alive(a):
    try:
        return a is not None and a.get_world() is not None
    except Exception:
        return False


def _find(label):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


def _spawn():
    """Lazily create assets + actors (re-uses actors left by an earlier module load in the same level)."""
    if _st.get("failed"):
        return False
    try:
        if not eal.does_asset_exist(DEST + "/M_RainSplash"):
            build()
        _st["mpc"] = collection()
        snow = _find("WeatherFX_Snow")
        if not _alive(snow):
            snow = unreal.SkyBridgeViewLibrary.spawn_rain_field(snow_mesh(), snow_material(), SNOW_COUNT, SNOW_BOX, SNOW_HEIGHT,
                                                                unreal.Vector(*SNOW_SCALE))
            snow.set_actor_label("WeatherFX_Snow")
        splash = _find("WeatherFX_Splash")
        if not _alive(splash):
            splash = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DecalActor, unreal.Vector(0, 0, 0),
                                                                     unreal.Rotator(pitch=-90.0))
            splash.set_actor_label("WeatherFX_Splash")
            dc = splash.decal
            dc.set_decal_material(splash_material())
            dc.set_editor_property("decal_size", unreal.Vector(SPLASH_DEPTH, SPLASH_RADIUS, SPLASH_RADIUS))
            try:
                dc.set_fade_screen_size(0.0)
            except Exception:
                pass
        for a in (snow, splash):
            a.set_folder_path("SkyBridge/WeatherFX")
            a.set_is_temporarily_hidden_in_editor(True)
        _st.update(snow=snow, splash=splash, shown={}, s=0.0, r=0.0, dx=0.0, dy=0.0, dz=0.0, t=time.time())
        log("spawned snow field (%d flakes) and splash decal" % SNOW_COUNT)
        return True
    except Exception as e:
        _st["failed"] = True
        log("spawn failed: %s" % e)
        return False


def _show(name, on):
    if _st["shown"].get(name) != on:
        _st["shown"][name] = on
        _st[name].set_is_temporarily_hidden_in_editor(not on)


def _packet(live):
    mod = sys.modules.get(type(live).__module__)
    if not getattr(live, "pkt", None) or mod is None:
        return None
    import ctypes
    v = struct.unpack(mod.PKT_FMT, ctypes.string_at(live.pkt, mod.PKT_SIZE))
    return v if v[0] == 0x42554B53 and v[1] >= 2 else None


def update(live, cam_loc, dt=None, v=None):
    """Per frame (cheap): smooth Skyrim's snow/rain amounts, integrate wind drift, keep the actors around the camera."""
    if cam_loc is None:
        return
    if "snow" not in _st and not _spawn():
        return
    if not (_alive(_st["snow"]) and _alive(_st["splash"])):    # level was reset (new_blank_map): spawn again
        _st.pop("snow", None)
        if not _spawn():
            return
    now = time.time()
    dt = min(0.25, max(0.0, now - _st["t"] if dt is None else dt)); _st["t"] = now
    if v is None:
        try:
            v = _packet(live)
        except Exception:
            v = None
    interior = bool(getattr(live, "_interior", False))
    snow_t = v[38] if v is not None else 0.0
    rain_t = (live.wx.get("rain", 0.0) if hasattr(live, "wx") else 0.0) if v is None else v[37]
    wind = v[63] if v is not None else 0.2
    if wind > 1.5: wind /= 255.0
    if FORCE["snow"] is not None: snow_t = FORCE["snow"]
    if FORCE["rain"] is not None: rain_t = FORCE["rain"]
    if FORCE["wind"] is not None: wind = FORCE["wind"]
    if interior:
        snow_t = rain_t = 0.0
    k = min(1.0, dt / 3.0)
    _st["s"] += (snow_t - _st["s"]) * k
    _st["r"] += (rain_t - _st["r"]) * k
    snow_on, rain_on = _st["s"] > 0.02 and not interior, _st["r"] > 0.02 and not interior
    _show("snow", snow_on); _show("splash", rain_on)
    if snow_on:
        # wind blows from a slowly turning direction; drift is wrapped to the box (the material wrap hides the jump)
        ang = 0.6 + 0.4 * math.sin(now * 0.01)
        sp = 40.0 + 420.0 * max(0.0, min(1.0, wind))                # cm/s horizontal
        _st["dx"] = (_st["dx"] + math.cos(ang) * sp * dt) % SNOW_BOX
        _st["dy"] = (_st["dy"] + math.sin(ang) * sp * dt) % SNOW_BOX
        _st["dz"] = (_st["dz"] - 95.0 * dt) % SNOW_HEIGHT        # base fall ~1 m/s (+0.1-0.4 per flake in the material)
        _set("DriftX", _st["dx"]); _set("DriftY", _st["dy"]); _set("DriftZ", _st["dz"])
        p = unreal.Vector(round(cam_loc.x / SNOW_BOX) * SNOW_BOX, round(cam_loc.y / SNOW_BOX) * SNOW_BOX,
                          round(cam_loc.z / SNOW_HEIGHT) * SNOW_HEIGHT)
        if p != _st.get("snow_at"):
            _st["snow_at"] = p
            _st["snow"].set_actor_location(p, False, False)
    _set("Snowfall", min(1.0, _st["s"]) if snow_on else 0.0)
    if rain_on:
        feet_z = v[6] * 1.4287 if v is not None else cam_loc.z - 150.0
        if abs(feet_z - cam_loc.z) > 1500.0: feet_z = cam_loc.z - 150.0
        p = unreal.Vector(cam_loc.x, cam_loc.y, feet_z)
        q = _st.get("splash_at")
        if q is None or abs(p.x - q.x) + abs(p.y - q.y) + abs(p.z - q.z) > 60.0:
            _st["splash_at"] = p
            _st["splash"].set_actor_location(p, False, False)
    _set("Splash", min(1.0, _st["r"]) if rain_on else 0.0)


def clear(live=None):
    """Destroy the actors and zero the parameters (assets stay)."""
    uninstall_test_tick()
    for n in ("snow", "splash"):
        a = _st.get(n)
        if _alive(a):
            a.destroy_actor()
    for label in ("WeatherFX_Snow", "WeatherFX_Splash"):
        a = _find(label)
        if a: a.destroy_actor()
    if _st.get("mpc"):
        for n in MPC_PARAMS:
            try:
                unreal.MaterialLibrary.set_scalar_parameter_value(_world(), _st["mpc"], n, 0.0)
            except Exception:
                pass
    _st.clear()


# ------------------------------------------------------------------ testing before live_bridge calls update()
def install_test_tick(live):
    """Drive update() from our own slate tick (until live_bridge has the hook). Camera = the level viewport camera."""
    uninstall_test_tick()
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    def _tick(dt):
        try:
            loc, _ = ues.get_level_viewport_camera_info()
            update(live, loc, dt)
        except Exception as e:
            if str(e) != _st.get("tick_err"):
                _st["tick_err"] = str(e); log("test tick: %s" % e)
    _st["tick"] = unreal.register_slate_post_tick_callback(_tick)


def uninstall_test_tick():
    h = _st.pop("tick", None)
    if h is not None:
        unreal.unregister_slate_post_tick_callback(h)
