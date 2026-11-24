"""Lighting quality tiers and the time-of-day / weather look, used by live_bridge.

Quality: `area2/quality.txt` holds low | medium | high | ultra | cinematic | auto (default auto: picked from the GPU's
model and VRAM; cinematic = ultra at native resolution, opt-in only).
`python start_bridge.py --quality <tier>` writes it and applies it to the running editor. Each tier is Unreal's
scalability groups (sg.*) plus the settings this scene is sensitive to: Lumen hardware vs software tracing, volumetric
fog grid, volumetric cloud and cloud-shadow sample counts, point-light shadow count and render resolution.

Look (`look`, called from Live.update_sky whenever sun/weather change): colour grading per phase of the day (cool
desaturated moonlight, blue hour, warm golden hour, grey rain), sun glow through haze (directional inscattering),
ground mist at dawn and in fog/rain (second fog layer), atmospheric haze (Mie) and aerial depth on distant mountains,
sun god rays scaled with haze, smoky torch-lit interiors. `flicker` animates nearby fire lights.
"""
import math, os, re, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
QUALITY_FILE = os.path.join(AREA, "quality.txt")
MIE_DEFAULT = 0.003996                       # SkyAtmosphereComponent default Mie scattering scale

# sg = scalability level for Shadow/GI/Reflection/PostProcess/Effects; screen = viewport screen percentage (DLSS/TSR
# upscale below 100); fog = (volumetric fog on, grid pixel size, depth slices); cloud_* = sample-count scales on the
# VolumetricCloudComponent; cshadow = (shadow map max resolution, ray samples, extent km) of the sun's cloud shadow;
# lights = point lights with cubemap shadows; scatter = torch light in volumetric fog; shafts = screen-space sun shafts
# (stand-in for volumetric god rays where volumetric fog is off).
TIERS = {
    "low":    dict(sg=1, hwrt=0, rr=0, vsm=0, screen=58, fog=(0, 16, 64), cloud_view=0.4, cloud_shadow=0.25, cloud_rays=192,
                   cshadow=(512, 24, 30.0), lights=2, scatter=0.0, shafts=1, fast_ap=1, flicker=4),
    "medium": dict(sg=2, hwrt=0, rr=0, vsm=1, screen=67, fog=(1, 16, 64), cloud_view=0.6, cloud_shadow=0.4, cloud_rays=320,
                   cshadow=(1024, 32, 40.0), lights=4, scatter=0.6, shafts=1, fast_ap=1, flicker=6),
    "high":   dict(sg=3, hwrt=0, rr=0, vsm=1, screen=77, fog=(1, 12, 96), cloud_view=0.8, cloud_shadow=0.5, cloud_rays=512,
                   cshadow=(1024, 48, 50.0), lights=6, scatter=1.0, shafts=0, fast_ap=0, flicker=8),
    # Ray Reconstruction at 77% (1972x1109 -> 1440p): 3 ms less DLSS and 4 ms less Lumen than native DLAA, looks the same
    "ultra":  dict(sg=3, hwrt=1, rr=1, vsm=1, screen=77, fog=(1, 8, 128), cloud_view=1.0, cloud_shadow=0.5, cloud_rays=768,
                   cshadow=(1024, 64, 60.0), lights=8, scatter=1.2, shafts=0, fast_ap=0, flicker=10),
    # opt-in only (never picked by auto): ultra at native resolution (DLAA)
    "cinematic": dict(sg=3, hwrt=1, rr=1, vsm=1, screen=100, fog=(1, 8, 128), cloud_view=1.0, cloud_shadow=0.5, cloud_rays=768,
                      cshadow=(1024, 64, 60.0), lights=8, scatter=1.2, shafts=0, fast_ap=0, flicker=10),
}


def log(msg):
    unreal.log("[SkyBridgeLive] " + msg)


def cmd(c):
    unreal.SystemLibrary.execute_console_command(None, c)


def setp(obj, name, value):
    try:
        if hasattr(obj, "override_" + name):
            obj.set_editor_property("override_" + name, True)
        obj.set_editor_property(name, value)
    except Exception as e:
        log("property %s: %s" % (name, e))


def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x


def smooth(a, b, x):
    t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t)


def lerp(a, b, t): return a + (b - a) * t


# ------------------------------------------------------------------ quality tiers
def detect_gpu():
    """(name, VRAM GB) of the adapter with the most dedicated memory (the discrete GPU on hybrid laptops/desktops)."""
    import winreg
    best = ("", 0.0)
    key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
            for i in range(64):
                try:
                    sub = winreg.EnumKey(k, i)
                except OSError:
                    break
                try:
                    with winreg.OpenKey(k, sub) as sk:
                        name = winreg.QueryValueEx(sk, "DriverDesc")[0]
                        mem = winreg.QueryValueEx(sk, "HardwareInformation.qwMemorySize")[0]
                        mem = int.from_bytes(mem, "little") if isinstance(mem, bytes) else int(mem)
                        if mem / 2 ** 30 > best[1]:
                            best = (name, mem / 2 ** 30)
                except OSError:
                    pass
    except OSError:
        pass
    return best


def auto_tier(name, vram):
    """Conservative: Skyrim renders on the same GPU, so auto never picks above medium on NVIDIA RTX cards;
    high/ultra are only used when area2/quality.txt asks for them."""
    n = name.lower()
    m = re.search(r"rtx\s*(\d)0(\d)0", n)
    if m:                                                   # NVIDIA RTX 20..50: 2060 -> 60, 3070 -> 80, 4080 -> 100, 5080 -> 110
        score = int(m.group(2)) * 10 + (int(m.group(1)) - 2) * 10
        if "ti" in n.split(m.group(0))[-1][:4]: score += 5
        return "medium" if score >= 60 and vram >= 6 else "low"
    if vram >= 15: return "high"                            # Radeon RX 7900/9070, Arc: strong raster, weaker ray tracing
    if vram >= 8: return "medium"
    return "low"


def wanted_tier():
    try:
        t = open(QUALITY_FILE).read().split()[0].lower()
    except (OSError, IndexError):
        t = "auto"
    if t in TIERS:
        return t, "quality.txt"
    name, vram = detect_gpu()
    return auto_tier(name, vram), "auto: %s %.0f GB" % (name or "unknown GPU", vram)


def apply_quality(live, tier=None):
    why = "requested"
    if tier not in TIERS:
        tier, why = wanted_tier()
    q = TIERS[tier]
    live.quality, live.qcfg = tier, q
    sg = q["sg"]
    for g in ("Shadow", "GlobalIllumination", "Reflection", "PostProcess", "Effects"):
        cmd("sg.%sQuality %d" % (g, sg))
    fog_on, px, z = q["fog"]
    for c in ("r.Lumen.HardwareRayTracing %d" % q["hwrt"],
              "r.NGX.DLSS.DenoiserMode %d" % q["rr"],               # Ray Reconstruction denoises hardware-traced Lumen
              "r.Editor.Viewport.ScreenPercentage %d" % q["screen"],
              "r.Shadow.Virtual.Enable %d" % q["vsm"],
              "r.VolumetricFog %d" % fog_on, "r.VolumetricFog.GridPixelSize %d" % px, "r.VolumetricFog.GridSizeZ %d" % z,
              "r.LightShaftQuality %d" % q["shafts"],
              "r.SkyAtmosphere.AerialPerspectiveLUT.FastApplyOnOpaque %d" % q["fast_ap"],
              "r.VolumetricCloud.ViewRaySampleMaxCount %d" % q["cloud_rays"],
              # the sun's cloud shadow map ran at 2048 px x 128 samples over 150 km, re-traced every frame: ~12 ms
              "r.VolumetricCloud.ShadowMap.MaxResolution %d" % q["cshadow"][0],
              "r.VolumetricCloud.ShadowMap.RaySampleMaxCount %d" % q["cshadow"][1],
              "r.VolumetricCloud.ShadowMap.TemporalFiltering.NewFrameWeight 0.25",
              "r.VolumetricCloud.SkyAO 0"):                      # sky light cloud occlusion is off on the sky light anyway
        cmd(c)
    sun = live.sun.light_component
    setp(sun, "cloud_shadow_extent", q["cshadow"][2])
    setp(sun, "cloud_shadow_map_resolution_scale", 1.0)
    setp(sun, "cloud_shadow_ray_sample_count_scale", 0.5)
    setp(sun, "cast_shadows_on_clouds", bool(q["hwrt"]))          # terrain shadowing the cloud deck: barely visible
    setp(sun, "enable_light_shaft_bloom", bool(q["shafts"]))
    setp(sun, "bloom_scale", 0.12); setp(sun, "bloom_threshold", 6.0); setp(sun, "bloom_max_brightness", 60.0)
    setp(sun, "cast_volumetric_shadow", bool(fog_on))               # god rays through trees and gaps in buildings
    setp(live.moon.light_component, "cast_shadows_on_clouds", False)
    setp(live.moon.light_component, "cast_cloud_shadows", False)
    cc = live.clouds.get_component_by_class(unreal.VolumetricCloudComponent)
    try:
        cc.set_view_sample_count_scale(q["cloud_view"])
        cc.set_shadow_view_sample_count_scale(q["cloud_shadow"])
        cc.set_reflection_view_sample_count_scale(0.25)
        cc.set_shadow_reflection_view_sample_count_scale(0.25)
        cc.set_tracing_max_distance(30.0 if tier in ("low", "medium") else 50.0)
    except Exception as e:
        log("cloud quality: %s" % e)
    try:
        live.fog.component.set_volumetric_fog(bool(fog_on))
    except Exception:
        pass
    for i, a in enumerate(getattr(live, "light_actors", [])):
        light_quality(live, a.light_component, i)
    live._sky_key = None; live._look = None                       # re-apply the look with the new tier
    log("quality %s (%s)" % (tier, why))
    return tier


def light_quality(live, c, i):
    q = live.qcfg
    c.set_editor_property("cast_shadows", i < q["lights"])         # cubemap shadows: 6 passes per light
    c.set_volumetric_scattering_intensity(q["scatter"])
    c.set_cast_volumetric_shadow(False)                            # per-light shadowed fog: the most expensive fog feature


# ------------------------------------------------------------------ look
def look(live, elev, hour, mul, fog, rain, snow, storm, weather, interior):
    """Grading, haze, mist and god rays for the current sun elevation (deg) / weather; called only when they change."""
    q = getattr(live, "qcfg", TIERS["high"])
    clear = clamp((mul - 0.15) / 0.85)                             # 1 clear sky .. 0 storm
    night = 1.0 - smooth(-10.0, -2.0, elev)
    blue = clamp(1.0 - abs(elev + 4.0) / 5.0)                      # blue hour: sun 0-9 deg below the horizon
    golden = clamp(1.0 - abs(elev - 4.0) / 9.0) * smooth(-4.0, 0.0, elev)
    day = smooth(-2.0, 12.0, elev)
    wet = clamp(rain + snow)
    dawn = clamp(1.0 - abs(hour - 6.5) / 2.5)                      # morning ground mist, a little in the evening too
    dusk = clamp(1.0 - abs(hour - 20.5) / 1.5) * 0.4
    fogw = clamp((fog - 0.005) / 0.03)                             # Skyrim's fog weathers / short fog distance
    mist = 0.0 if interior else clamp(max(dawn, dusk) * (0.4 + 0.6 * clear) + fogw + 0.4 * rain)

    s = live.pp.get_editor_property("settings")
    if interior:
        sat, temp, contrast, bloom, vig = 1.0, 6300.0, 1.06, 0.55, 0.35   # torchlight is already deep orange
        gain_sh = unreal.Vector4(1.0, 1.0, 1.0, 1.0)
    else:
        sat = lerp(1.0, 1.1, golden * clear) * lerp(1.0, 0.72, night) * lerp(1.0, 0.82, (1.0 - clear) * day)
        # white balance: higher = warmer picture. Golden hour warmer, moonlight and rain cooler.
        temp = 6500.0 + 450.0 * golden * clear - 1000.0 * night - 300.0 * blue - 350.0 * wet * day
        contrast = 1.03 + 0.05 * clear + 0.03 * golden
        bloom = lerp(0.35, 0.6, night)
        vig = lerp(0.22, 0.38, max(night, 0.5 * (1.0 - clear)))
        b = 0.05 * night + 0.03 * blue                             # moonlit shadows lean blue
        gain_sh = unreal.Vector4(1.0 - b, 1.0 - 0.3 * b, 1.0 + b, 1.0)
    setp(s, "white_temp", temp)
    setp(s, "color_saturation", unreal.Vector4(sat, sat, sat, 1.0))
    setp(s, "color_contrast", unreal.Vector4(contrast, contrast, contrast, 1.0))
    setp(s, "color_gain_shadows", gain_sh)
    setp(s, "bloom_intensity", bloom)
    setp(s, "vignette_intensity", vig)
    live.pp.set_editor_property("settings", s)

    fc = live.fog.component
    sun = live.sun.light_component
    try:
        if interior:
            # smoky hall: a dark, thin height fog so only torch light (volumetric scattering) shows as haze
            fc.set_fog_density(0.02 if q["fog"][0] else 0.004)
            fc.set_fog_height_falloff(0.001)
            fc.set_fog_inscattering_color(unreal.LinearColor(0.004, 0.0035, 0.003, 1.0))
            fc.set_directional_inscattering_color(unreal.LinearColor(0, 0, 0, 1))
            fc.set_volumetric_fog_albedo(unreal.Color(r=235, g=225, b=210, a=255))
            fc.set_volumetric_fog_extinction_scale(0.8)
            fc.set_second_fog_density(0.0)
            live._fog_col = None                                   # update_sky re-applies Skyrim's fog colour outside
        else:
            fc.set_fog_height_falloff(0.2)
            fc.set_volumetric_fog_albedo(unreal.Color(r=255, g=255, b=255, a=255))
            # glow around the sun through haze: strongest when it is low and the air is clear-ish
            sc = getattr(live, "_sun_col", None) or (1.0, 0.85, 0.7)
            g = (0.25 + 1.2 * golden) * day * (0.35 + 0.65 * clear) * (1.0 + mist)
            fcol = getattr(live, "_fog_col", None) or (0.3, 0.32, 0.35)
            k = g * max(fcol) * 2.0
            fc.set_directional_inscattering_color(unreal.LinearColor(sc[0] * k, sc[1] * k, sc[2] * k, 1.0))
            fc.set_directional_inscattering_exponent(lerp(10.0, 5.0, mist))
            fc.set_directional_inscattering_start_distance(2000.0)
            # ground mist: the fog actor sits 15 m below the camera (update_sky), so +13 m is about ground level;
            # halves every ~7 m of height and makes distant valleys fade into white at dawn
            fc.set_second_fog_density(0.045 * mist)
            fc.set_second_fog_height_falloff(1.5)
            fc.set_second_fog_height_offset(1300.0)
    except Exception as e:
        log("fog look: %s" % e)
    try:
        # god rays: more scattering when the sun is low or the air is misty
        sun.set_volumetric_scattering_intensity(1.0 + 1.2 * golden + 1.5 * mist)
        if q["shafts"]:
            sun.set_bloom_scale(0.08 + 0.25 * golden * clear)
    except Exception as e:
        log("sun look: %s" % e)
    atm = getattr(live, "atmosphere", None)
    if atm and not interior:
        try:
            atm.set_mie_scattering_scale(MIE_DEFAULT * (1.0 + 0.8 * golden + 1.2 * (1.0 - clear) + 1.5 * mist))
            atm.set_aerial_pespective_view_distance_scale(lerp(1.8, 2.6, max(mist, 1.0 - clear)))
        except Exception as e:
            log("atmosphere look: %s" % e)


# ------------------------------------------------------------------ torches
def flicker(live, cam, now):
    """Fire lights near the camera flicker (intensity only: cached shadow pages stay valid). Cheap: a few lights, 30 Hz."""
    q = getattr(live, "qcfg", None)
    if not q or cam is None or now - getattr(live, "_flk_t", 0.0) < 1.0 / 30.0:
        return
    live._flk_t = now
    base = getattr(live, "light_base", {})
    if now - getattr(live, "_flk_pick", 0.0) > 1.0:                # re-pick the nearest warm lights once a second
        live._flk_pick = now
        picks = []
        for i, a in enumerate(live.light_actors):
            b = base.get(i)
            if not b or b[1][0] < 1.25 * max(b[1][2], 0.05):       # only warm (fire-coloured) lights
                continue
            p = a.get_actor_location()
            d = (p.x - cam.x) ** 2 + (p.y - cam.y) ** 2 + (p.z - cam.z) ** 2
            if d < 3000.0 ** 2:
                picks.append((d, i))
        old = set(getattr(live, "_flk", []))
        live._flk = [i for _, i in sorted(picks)[:q["flicker"]]]
        for i in old - set(live._flk):                              # lights that left the set get their steady value back
            if i < len(live.light_actors) and i in base:
                live.light_actors[i].light_component.set_intensity(base[i][0])
    for i in getattr(live, "_flk", []):
        if i >= len(live.light_actors) or i not in base:
            continue
        p = i * 1.7
        n = 0.5 * math.sin(now * 7.3 + p) + 0.3 * math.sin(now * 13.1 + 2.0 * p) + 0.2 * math.sin(now * 23.7 + 3.0 * p)
        live.light_actors[i].light_component.set_intensity(base[i][0] * (0.9 + 0.1 * n))


# ------------------------------------------------------------------ housekeeping
def sweep_captures(live):
    """Debug capture scripts (area2/*capture*.py) leave SceneCapture2D actors rendering the whole scene every frame
    (~50 ms GPU each) if their 'done' step never runs. Remove any that no script is holding."""
    held = [c[0] for c in getattr(live, "_npc_caps", [])]
    if getattr(live, "_sky_cap", None):
        held.append(live._sky_cap[0])
    n = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(a, unreal.SceneCapture2D) and not any(a == h for h in held):
            a.destroy_actor(); n += 1
    if n:
        log("removed %d stray scene captures" % n)
    if getattr(live, "night_mid", 1) is None and getattr(live, "_night_saved", None) and not getattr(live, "_sky_cap", None):
        live.night_mid = live._night_saved                         # sky_capture.py 'setup' without 'done' disabled the stars
        live._sky_key = None
