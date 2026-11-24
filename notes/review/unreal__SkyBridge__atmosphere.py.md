# Review leads for unreal/SkyBridge/atmosphere.py (UNVERIFIED)
L165 | bug | `except Exception as e:` hiding cloud quality setting failures | Could result in unapplied cloud quality settings with no user feedback | Remove try-except block to propagate errors | high
L307 | perf | `unreal.EditorLevelLibrary.get_all_level_actors()` called per frame | Unnecessary frame-time cost scanning all level actors (potentially thousands) | Cache held scene capture references instead of scanning actors | high
