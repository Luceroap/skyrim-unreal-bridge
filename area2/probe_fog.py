m = unreal.load_asset("/Game/Area2Tex/M_NightSky")
out = []
for n in ("apply_fogging", "use_translucency_vertex_fog", "compute_fog_per_pixel", "apply_cloud_fogging", "is_sky",
          "translucency_pass", "disable_depth_test", "allow_negative_emissive_color"):
    try:
        out.append((n, m.get_editor_property(n)))
    except Exception as e:
        out.append((n, "ERR"))
print(out)
c = live.sky_dome.static_mesh_component
print("bounds", c.bounds.sphere_radius if hasattr(c, "bounds") else None, live.sky_dome.get_actor_location())
