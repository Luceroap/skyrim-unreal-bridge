print("sky key (elev, fam, wet, snow, rain):", live._sky_key, "interior", getattr(live, "_interior", None))
m = live.night_mid
print("night", m.get_scalar_parameter_value("Night") if m else None, "aurora", m.get_scalar_parameter_value("Aurora") if m else None)
