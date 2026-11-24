"""Switch the live Unreal view to a performance profile.   python tools/perf_profile.py [fast|faster|fastest|everyday]
fast     software Lumen, 75% render scale upscaled by TSR, medium shadows/GI, cheaper fog/clouds        (good looks, ~2-3x the showcase speed)
faster   as fast, 62% scale, low shadows, no DOF/bloom extras, 30 fps cap off                           (smooth while flying around)
fastest  50% scale, minimal everything, still lit by Lumen                                               (when the PC is struggling)
everyday back to the project's normal settings (tools/max_quality.py --off)
Settings are session-only: restarting the editor resets them."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

BASE = """r.Lumen.HardwareRayTracing 0
r.Lumen.Reflections.HardwareRayTracing 0
r.Lumen.ScreenProbeGather.HardwareRayTracing 0
r.Lumen.HardwareRayTracing.LightingMode 0
r.RayTracing.Shadows 0
r.RayTracing.AmbientOcclusion 0
r.RayTracing.Reflections 0
r.RayTracing.SkyLight 0
r.Lumen.Reflections.DownsampleFactor 2
r.Lumen.ScreenProbeGather.DownsampleFactor 16
r.Lumen.ScreenProbeGather.TracingOctahedronResolution 8
r.Shadow.Virtual.ResolutionLodBiasDirectional 1
r.Shadow.Virtual.SMRT.RayCountDirectional 4
r.Shadow.Virtual.SMRT.RayCountLocal 4
r.Nanite.MaxPixelsPerEdge 2
r.VolumetricFog.GridPixelSize 16
r.VolumetricFog.GridSizeZ 64
r.VolumetricCloud.ViewRaySampleMaxCount 192
r.VolumetricCloud.ShadowViewRaySampleMaxCount 96
r.MotionBlurQuality 0
r.Streaming.PoolSize 3000
r.Streaming.MipBias 0
r.Streaming.Boost 1
r.MaxAnisotropy 8
r.TSR.History.UpdateQuality 2
t.MaxFPS 45
viewmode lit"""
LEVELS = {
    "fast": BASE + "\nr.ScreenPercentage 75\nsg.ShadowQuality 2\nsg.GlobalIlluminationQuality 2\nsg.ReflectionQuality 2\nsg.PostProcessQuality 2\nsg.EffectsQuality 2\nsg.FoliageQuality 2\nr.DepthOfFieldQuality 1\nr.BloomQuality 3\nr.AmbientOcclusionLevels 2",
    "faster": BASE + "\nr.ScreenPercentage 62\nsg.ShadowQuality 1\nsg.GlobalIlluminationQuality 1\nsg.ReflectionQuality 1\nsg.PostProcessQuality 1\nsg.EffectsQuality 1\nsg.FoliageQuality 1\nr.DepthOfFieldQuality 0\nr.BloomQuality 2\nr.AmbientOcclusionLevels 1\nr.Lumen.ScreenProbeGather.DownsampleFactor 32",
    "fastest": BASE + "\nr.ScreenPercentage 50\nsg.ShadowQuality 0\nsg.GlobalIlluminationQuality 0\nsg.ReflectionQuality 0\nsg.PostProcessQuality 0\nsg.EffectsQuality 0\nsg.FoliageQuality 0\nr.DepthOfFieldQuality 0\nr.BloomQuality 1\nr.AmbientOcclusionLevels 0\nr.Lumen.ScreenProbeGather.DownsampleFactor 32\nr.Nanite.MaxPixelsPerEdge 4",
}
if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "fast"
    if level == "everyday":
        sys.exit(subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "max_quality.py"), "--off"]).returncode)
    lines = LEVELS[level].splitlines()
    code = ("import unreal\nfor c in %r:\n    unreal.SystemLibrary.execute_console_command(None, c)\n"
            "try:\n    for a in unreal.EditorLevelLibrary.get_all_level_actors():\n        if a.get_folder_path() == 'SkyBridge/Fire': a.destroy_actor()\nexcept Exception: pass\n"
            "print('profile applied:', %r)") % (lines, level)
    print(ue_exec(code, 60))
