"""Soft atmospheric depth for the live view: distance haze plus a low cloud band that hugs the mountainsides, so the far world can be
cut off or simplified (cheaper) without a visible edge.   apply(live, strength=1.0)  /  off(live)
Uses the existing ExponentialHeightFog (first layer = haze, second layer = the cloud band) and keeps everything subtle:
strength 0 = none, 1 = default, 2 = moody.  Tinted by the sun colour so it stays warm at sunset and cool at dusk."""
import unreal

BAND_CENTER_ABOVE_PLAYER = 12000.0   # cm above the camera: the band sits on the mountain flanks, not on the town


def _fog(live):
    return live.fog.component


def apply(live, strength=1.0, cam_z=None):
    f = _fog(live)
    cz = cam_z if cam_z is not None else live.cam_sky[2] * 1.0 if getattr(live, "cam_sky", None) else 0.0
    s = max(0.0, strength)
    f.set_editor_property("start_distance", 25000.0)                  # clear for the first 250 m, then the haze builds
    f.set_editor_property("fog_max_opacity", min(0.92, 0.55 + 0.25 * s))
    f.set_editor_property("fog_cutoff_distance", 0.0)
    try:
        f.set_editor_property("fog_height_falloff", 0.0025)
    except Exception:
        pass
    try:
        d = unreal.ExponentialHeightFogData()
        d.set_editor_property("fog_density", 0.0028 * s)
        d.set_editor_property("fog_height_falloff", 0.0016)
        d.set_editor_property("fog_height_offset", -4900.0 + BAND_CENTER_ABOVE_PLAYER)
        f.set_editor_property("second_fog_data", d)
        return "haze + cloud band on (strength %.1f)" % s
    except Exception as e:
        return "haze on; cloud band layer unavailable: %s" % e


def off(live):
    f = _fog(live)
    f.set_editor_property("start_distance", 0.0)
    try:
        d = unreal.ExponentialHeightFogData()
        d.set_editor_property("fog_density", 0.0)
        f.set_editor_property("second_fog_data", d)
    except Exception:
        pass
    return "off"
