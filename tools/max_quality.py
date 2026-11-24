"""Push the live Unreal editor to its absolute maximum quality for showcase screenshots (ray traced Lumen hit lighting, cinematic scalability,
finest Nanite, densest GI/reflection tracing).  python tools/max_quality.py          apply
                                                  python tools/max_quality.py --off    back to the everyday settings"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

MAX = """r.Lumen.HardwareRayTracing 1
r.Lumen.HardwareRayTracing.LightingMode 2
r.Lumen.Reflections.HardwareRayTracing 1
r.Lumen.ScreenProbeGather.HardwareRayTracing 1
r.Lumen.Reflections.MaxRoughnessToTrace 0.7
r.Lumen.Reflections.DownsampleFactor 1
r.Lumen.ScreenProbeGather.DownsampleFactor 4
r.Lumen.ScreenProbeGather.TracingOctahedronResolution 16
r.Lumen.ScreenProbeGather.FullResolutionJitterWidth 1
r.Lumen.TraceMeshSDFs 1
r.Lumen.DiffuseIndirect.Allow 1
r.RayTracing.Shadows 1
r.RayTracing.AmbientOcclusion 1
r.RayTracing.Reflections 1
r.RayTracing.SkyLight 1
sg.ShadowQuality 4
sg.GlobalIlluminationQuality 4
sg.ReflectionQuality 4
sg.PostProcessQuality 4
sg.TextureQuality 4
sg.EffectsQuality 4
sg.FoliageQuality 4
sg.ViewDistanceQuality 4
sg.ShadingQuality 4
r.Shadow.Virtual.ResolutionLodBiasDirectional -1
r.Shadow.Virtual.ResolutionLodBiasLocal -1
r.Shadow.Virtual.SMRT.RayCountDirectional 16
r.Shadow.Virtual.SMRT.SamplesPerRayDirectional 16
r.Shadow.Virtual.SMRT.RayCountLocal 16
r.Nanite.MaxPixelsPerEdge 0.5
r.VolumetricFog.GridPixelSize 4
r.VolumetricFog.GridSizeZ 128
r.VolumetricCloud.ViewRaySampleMaxCount 768
r.VolumetricCloud.ShadowViewRaySampleMaxCount 768
r.SkyAtmosphere.AerialPerspectiveLUT.Depth 96
r.ScreenPercentage 200
r.SecondaryScreenPercentage.GameViewport 100
r.Streaming.MipBias -1
r.Streaming.MaxEffectiveScreenSize 0
r.Streaming.Boost 5
r.Streaming.LimitPoolSizeToVRAM 0
r.TextureStreaming 1
r.Streaming.HLODStrategy 2
r.TSR.History.UpdateQuality 3
r.TSR.ShadingRejection.SampleCount 8
r.MotionBlurQuality 0
r.AmbientOcclusionLevels 3
r.AmbientOcclusionMaxQuality 100
r.Streaming.PoolSize 8000
r.Streaming.FullyLoadUsedTextures 1
r.MaxAnisotropy 16
r.Tonemapper.Sharpen 0.4"""

if __name__ == "__main__":
    off = len(sys.argv) > 1 and sys.argv[1] == "--off"
    lines = ["r.Lumen.HardwareRayTracing.LightingMode 0", "sg.ShadowQuality 3", "sg.GlobalIlluminationQuality 3", "sg.ReflectionQuality 3", "r.ScreenPercentage 100", "r.Streaming.PoolSize 5000", "r.Streaming.MipBias 0", "r.Streaming.Boost 1", "r.VolumetricFog.GridPixelSize 8", "r.Shadow.Virtual.ResolutionLodBiasDirectional 0", "r.Shadow.Virtual.SMRT.RayCountDirectional 8", "viewmode lit",
             "r.Nanite.MaxPixelsPerEdge 1", "r.Lumen.ScreenProbeGather.DownsampleFactor 16", "r.Lumen.ScreenProbeGather.TracingOctahedronResolution 8",
             "r.VolumetricCloud.ViewRaySampleMaxCount 768"] if off else MAX.splitlines()
    code = "import unreal\nfor c in %r:\n    unreal.SystemLibrary.execute_console_command(None, c)\nprint('applied', len(%r))" % (lines, lines)
    print(ue_exec(code, 60))
