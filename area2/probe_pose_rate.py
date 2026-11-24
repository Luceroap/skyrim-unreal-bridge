import sys, time
nl = sys.modules["npc_live"]
st = dict(t0=time.time(), frames=0, posed={}, last={})
def _cb(dt):
    st["frames"] += 1
    for k, e in nl._state["actors"].items():
        p = e.get("posed_t", 0)
        if st["last"].get(k) != p:
            st["last"][k] = p; st["posed"][k] = st["posed"].get(k, 0) + 1
    if time.time() - st["t0"] > 4.0:
        unreal.unregister_slate_post_tick_callback(st["h"])
        el = time.time() - st["t0"]
        with open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\pose_rate.txt", "w") as f:
            f.write("fps %.1f seq %s\n" % (st["frames"] / el, nl._state.get("seq")))
            for sx, w in nl._state.get("walk", {}).items():
                L = w.get("loop")
                f.write("walk %s: buf %d loop %s\n" % (sx, len(w["buf"]), L and "%.2fs %d poses speed %.0f" % (L["dur"], len(L["poses"]), L["speed"])))
            for k, e in nl._state["actors"].items():
                s = e.get("shown")
                own = s is not None and s["pose"][0] is (e["hist"][-1]["pose"][0] if e.get("hist") else None)
                f.write("%-26s dist %5.0f poses/s %.1f frozen %s speed %.0f walkphase %s\n" % (e["actor"].get_actor_label()[:26], e.get("dist", 0),
                        st["posed"].get(k, 0) / el, e.get("frozen"), e.get("speed", 0), e.get("wph") is not None))
st["h"] = unreal.register_slate_post_tick_callback(_cb)
print("registered")
