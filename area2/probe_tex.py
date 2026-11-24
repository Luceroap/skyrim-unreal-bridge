for k in ("wrfieldgrass01", "wrslate01", "wrstonefloor02"):
    t = unreal.load_asset("/Game/Area2Tex/" + k)
    if not t:
        print(k, "no asset"); continue
    print(k, t.blueprint_get_size_x(), t.blueprint_get_size_y(),
          "max", t.get_editor_property("max_texture_size"), "lodgroup", t.get_editor_property("lod_group"),
          "bias", t.get_editor_property("lod_bias"), "never_stream", t.get_editor_property("never_stream"),
          "vt", t.get_editor_property("virtual_texture_streaming"), "mipgen", t.get_editor_property("mip_gen_settings"))
for cv in ("r.Streaming.PoolSize", "r.Streaming.LimitPoolSizeToVRAM", "r.Streaming.MipBias", "r.MaxAnisotropy",
           "r.Tonemapper.Sharpen", "r.Streaming.UseFixedPoolSize", "r.VT.PoolSizeScale"):
    print(cv, unreal.SystemLibrary.get_console_variable_float_value(cv) if hasattr(unreal.SystemLibrary, "get_console_variable_float_value") else "?")
