# Runs inside the editor via `python tools/ue_run.py area2/perf/probe_tick.py` (globals: unreal, live).
# Installs timing wrappers on live.tick_body and its sub-steps (instance attributes / module attributes only, nothing on
# disk changes), returns at once, then on later frames: TIME_S of perf_counter timing + a CSV profiler capture
# (game/render/GPU/RHI per frame), PROF_S of cProfile, then restores everything and writes area2/perf/tick_probe.json.
# Restore also runs on any exception inside the probe and after a hard deadline.
import time, json, os, sys, cProfile, pstats, io

OUT = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\perf\tick_probe.json"
REQ = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\exec_request.py"
TIME_S, PROF_S = 25.0, 4.0
L = live
pc = time.perf_counter


def _console(c):
    try:
        unreal.SystemLibrary.execute_console_command(None, c)
    except Exception:
        pass


if L.__dict__.get("_perf_probe"):
    print("probe already active, not installing twice")
else:
    st = dict(t0=pc(), frames=[], dts=[], body=[], execf=[], acc={}, cnt={}, mx={}, phase="time", prof=None,
              err=None, csv=False, restored=False)
    patches = []

    def wrap(obj, name, label):
        orig = getattr(obj, name, None)
        if orig is None or not callable(orig):
            return
        d = getattr(obj, "__dict__", {})
        had, own = name in d, d.get(name)

        def w(*a, **k):
            t = pc()
            try:
                return orig(*a, **k)
            finally:
                dd = pc() - t
                st["acc"][label] = st["acc"].get(label, 0.0) + dd
                st["cnt"][label] = st["cnt"].get(label, 0) + 1
                if dd > st["mx"].get(label, 0.0):
                    st["mx"][label] = dd
        patches.append((obj, name, w, had, own))
        setattr(obj, name, w)

    def stop_csv():
        if st["csv"]:
            st["csv"] = False
            _console("csvprofile stop")

    def restore():
        if st["restored"]:
            return
        st["restored"] = True
        if L.__dict__.get("tick_body") is body:
            del L.tick_body
        for obj, name, w, had, own in reversed(patches):
            try:
                if getattr(obj, "__dict__", {}).get(name) is w:
                    if had:
                        setattr(obj, name, own)
                    else:
                        delattr(obj, name)
            except Exception:
                pass
        stop_csv()
        try:
            if st["prof"]:
                st["prof"].disable()
        except Exception:
            pass
        L.__dict__.pop("_perf_probe", None)

    def pct(v, p):
        v = sorted(v)
        return v[min(len(v) - 1, int(p * (len(v) - 1)))] if v else 0.0

    def finish():
        restore()
        n_end = st.get("n_time", len(st["frames"]))
        fr = st["frames"][:n_end]
        iv = [b - a for a, b in zip(fr, fr[1:])]
        body_t = st["body"][:n_end]
        acc, cnt = st.get("time_acc", st["acc"]), st.get("time_cnt", st["cnt"])
        res = dict(
            time_window_s=round(st.get("t_time_end", pc()) - st["t0"], 2), frames=len(fr),
            fps=round((len(fr) - 1) / (fr[-1] - fr[0]), 2) if len(fr) > 1 else 0,
            frame_ms=dict(mean=round(1000 * sum(iv) / max(1, len(iv)), 2), p50=round(1000 * pct(iv, .5), 2),
                          p95=round(1000 * pct(iv, .95), 2), p99=round(1000 * pct(iv, .99), 2),
                          max=round(1000 * max(iv or [0]), 2)),
            slate_dt_ms_mean=round(1000 * sum(st["dts"][:n_end]) / max(1, n_end), 2),
            tick_body_ms=dict(mean=round(1000 * sum(body_t) / max(1, len(body_t)), 2), p50=round(1000 * pct(body_t, .5), 2),
                              p95=round(1000 * pct(body_t, .95), 2), max=round(1000 * max(body_t or [0]), 2)),
            frames_with_foreign_exec=sum(st["execf"][:n_end]),
            parts={k: dict(ms_per_frame=round(1000 * v / max(1, n_end), 3), calls_per_frame=round(cnt[k] / max(1, n_end), 3),
                           ms_per_call=round(1000 * v / max(1, cnt[k]), 3), max_ms=round(1000 * st["mx"][k], 2))
                   for k, v in sorted(acc.items(), key=lambda kv: -kv[1])},
            err=st["err"], actors=len(getattr(L, "actors", {})), quality=getattr(L, "quality", None),
            addons=sorted(getattr(L, "_addons", {}).keys()),
        )
        if st["prof"]:
            np_ = len(st["frames"]) - n_end
            res["prof_frames"] = np_
            for key in ("cumulative", "tottime"):
                s = io.StringIO()
                pstats.Stats(st["prof"], stream=s).sort_stats(key).print_stats(45)
                res["cprofile_" + key] = s.getvalue()
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w") as f:
            json.dump(res, f, indent=1)
        unreal.log("[SkyBridgePerf] tick probe written: %s" % OUT)

    def advance(now):
        el = now - st["t0"]
        if st["phase"] == "time" and el > TIME_S:
            stop_csv()
            st["t_time_end"], st["n_time"] = now, len(st["frames"])
            st["time_acc"], st["time_cnt"] = dict(st["acc"]), dict(st["cnt"])
            st["phase"], st["prof"] = "prof", cProfile.Profile()
        elif st["phase"] == "prof" and el > TIME_S + PROF_S:
            st["phase"] = "done"
            finish()
        elif el > TIME_S + PROF_S + 15:
            st["err"] = "deadline"
            finish()

    orig_body = L.tick_body

    def body(dt):
        foreign = os.path.exists(REQ)
        t = pc()
        try:
            if st["phase"] == "prof" and st["prof"] is not None:
                st["prof"].enable()
                try:
                    return orig_body(dt)
                finally:
                    st["prof"].disable()
            return orig_body(dt)
        finally:
            e = pc()
            if not st["restored"]:
                st["frames"].append(t); st["dts"].append(dt); st["body"].append(e - t); st["execf"].append(foreign)
                try:
                    advance(e)
                except Exception as ex:
                    st["err"] = repr(ex)
                    try:
                        finish()
                    except Exception:
                        restore()

    try:
        for n in ("import_ready", "read_world", "apply_world", "spawn_some", "city_some", "distant_some", "addons_tick",
                  "update_sky", "set_interior", "city_world", "prefetch_step"):
            wrap(L, n, n)
        for mname, fn in (("npc_live", "tick"), ("tamriel_live", "tick"), ("memory_governor", "tick"),
                          ("atmosphere", "flicker"), ("atmosphere", "look"), ("atmosphere", "sweep_captures")):
            m = sys.modules.get(mname)
            if m is not None:
                wrap(m, fn, "%s.%s" % (mname, fn))
        for name, a in getattr(L, "_addons", {}).items():
            if a.get("mod") is not None and hasattr(a["mod"], "update"):
                wrap(a["mod"], "update", "addon:%s" % name)
        L._perf_probe = st
        L.tick_body = body
        _console("csvprofile start")
        st["csv"] = True
        print("installed: %d wrappers, %.0f s timing + %.0f s cProfile -> %s" % (len(patches), TIME_S, PROF_S, OUT))
    except Exception as ex:
        restore()
        print("install failed, restored:", repr(ex))
