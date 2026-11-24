import unreal
def props(obj, words):
    names = [n for n in dir(obj) if any(w in n for w in words)]
    print(type(obj).__name__, names)
props(live.fog.component, ["fog", "inscatter", "second", "volumetric", "start", "cutoff"])
props(live.sun.light_component, ["shaft", "scatter", "bloom", "volumetric", "temperature", "specular", "cascade", "dynamic_shadow", "shadow"])
props(live.clouds.get_component_by_class(unreal.VolumetricCloudComponent), ["sample", "shadow", "tracing"])
atm = unreal.EditorLevelLibrary.get_all_level_actors()
for a in atm:
    if isinstance(a, unreal.SkyAtmosphere):
        props(a.get_component_by_class(unreal.SkyAtmosphereComponent), ["mie", "rayleigh", "aerial", "height", "multi", "trace", "absorption"])
        break
props(live.skylight.light_component, ["lower", "occlusion", "intensity", "capture", "volumetric"])
s = live.pp.get_editor_property("settings")
props(s, ["white_", "color_saturation", "color_gain", "color_offset", "temperature", "shadows", "highlights", "toe", "slope", "shoulder", "lumen", "local_exposure", "bloom", "lens", "ambient_occlusion", "dynamic_global"])
print(unreal.SystemLibrary.get_rendering_detail_mode() if hasattr(unreal.SystemLibrary, "get_rendering_detail_mode") else "")
gus = unreal.GameUserSettings.get_game_user_settings()
print("overall", gus.get_overall_scalability_level())
for cv in ["r.Lumen.HardwareRayTracing", "r.RayTracing.Enable", "r.VolumetricFog.GridPixelSize", "r.Shadow.Virtual.Enable", "sg.ShadowQuality", "r.VolumetricCloud.ViewRaySampleMaxCount", "r.LightShaftQuality"]:
    print(cv, unreal.SystemLibrary.get_console_variable_int_value(cv), unreal.SystemLibrary.get_console_variable_float_value(cv))
