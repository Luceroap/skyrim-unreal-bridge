import unreal
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if isinstance(a, unreal.SceneCapture2D):
        cc = a.capture_component2d
        print(a.get_actor_label(), a.get_folder_path(), cc.get_editor_property("capture_every_frame"), cc.get_editor_property("texture_target"))
c = live.sun.light_component
for n in ["cloud_shadow_extent", "cloud_shadow_map_resolution_scale", "cloud_shadow_ray_sample_count_scale", "cloud_shadow_strength"]:
    print(n, c.get_editor_property(n))
sl = live.skylight.light_component
for n in ["cloud_ambient_occlusion", "cloud_ambient_occlusion_extent", "cloud_ambient_occlusion_map_resolution_scale"]:
    print(n, sl.get_editor_property(n))
cc = live.clouds.get_component_by_class(unreal.VolumetricCloudComponent)
for n in ["view_sample_count_scale", "shadow_view_sample_count_scale", "shadow_tracing_distance", "tracing_max_distance", "layer_bottom_altitude", "layer_height"]:
    print(n, cc.get_editor_property(n))
print(cc.get_editor_property("material").get_path_name())
for cv in ["r.VolumetricCloud.ShadowMap.MaxResolution", "r.VolumetricCloud.ShadowMap.RaySampleMaxCount", "r.VolumetricCloud.ShadowMap.RaySampleHorizonMultiplier",
           "r.VolumetricCloud.SkyAO", "r.VolumetricCloud.SkyAO.MaxResolution", "r.VolumetricCloud.ShadowMap.SpatialFiltering", "r.VolumetricCloud.ShadowMap.TemporalFiltering.NewFrameWeight",
           "r.VolumetricRenderTarget.Mode", "r.VolumetricCloud.ViewRaySampleMaxCount", "r.VolumetricCloud.SampleMinCount", "r.VolumetricCloud.DistanceToSampleMaxCount"]:
    print(cv, unreal.SystemLibrary.get_console_variable_float_value(cv))
