"""Keeps the editor's memory bounded while you travel (called from live_bridge.tick).

Pressure level from the free system commit (Skyrim + the editor share 32 GB RAM + page file):
  0 > 8 GB free, 1 > 4 GB, 2 > 2 GB, 3 below. Higher levels shrink the texture pool and bias textures down a mip.
Always on: textures of primitives outside the view stream at a quarter of their wanted resolution
(r.Streaming.HiddenPrimitiveScale), and contrast-adaptive Variable Rate Shading shades flat, low-detail screen areas
at a coarser rate (the desktop counterpart of foveated rendering, which needs an eye tracker).

Unloading: assets loaded in the editor are RF_Standalone, so garbage collection never frees them and every model you
ever passed stayed in memory. Meshes under /Game/Area2 and /Game/Tamriel that no component has used for IDLE[level]
seconds are unloaded with their material instances and textures (only those no remaining component uses); they load
from disk again when needed. Status: area2/memory_status.json; log lines start with 'memory:'."""
import ctypes, json, os, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
LEVEL_FREE_GB = (8.0, 4.0, 2.0)
POOL_MB = (3000, 2400, 1800, 1200)
MIP_BIAS = (0.0, 0.0, 0.5, 1.0)
CHECK_S = 10.0
SWEEP_S = (120.0, 60.0, 25.0, 20.0)
IDLE_S = (300.0, 120.0, 45.0, 20.0)
MAX_UNLOAD = 60                        # packages per sweep: unloading flushes rendering, keep each sweep short
IMPORT_STOP_GB = 18.0                  # stop live imports before the editor approaches the known runaway zone
IMPORT_RESUME_GB = 14.0                # hysteresis prevents import thrashing at the cutoff
MESH_ROOTS = ("/Game/Area2/", "/Game/Tamriel/")
TEX_ROOT = "/Game/Area2Tex/"
ALWAYS = ("r.Streaming.HiddenPrimitiveScale 0.25", "r.Streaming.LimitPoolSizeToVRAM 1",
          "r.VRS.Enable 1", "r.VRS.ContrastAdaptiveShading 1")

_state = dict(init=False, t=0.0, sweep_t=time.time(), level=None, idle={}, deps={}, freed=0, last=None,
              imports_paused=False)


class _MemStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


class _Counters(ctypes.Structure):                       # PROCESS_MEMORY_COUNTERS_EX
    _fields_ = [("cb", ctypes.c_ulong), ("page_fault_count", ctypes.c_ulong), ("peak_working_set", ctypes.c_size_t),
                ("working_set", ctypes.c_size_t), ("quota_peak_paged", ctypes.c_size_t),
                ("quota_paged", ctypes.c_size_t), ("quota_peak_nonpaged", ctypes.c_size_t),
                ("quota_nonpaged", ctypes.c_size_t), ("pagefile_usage", ctypes.c_size_t),
                ("peak_pagefile_usage", ctypes.c_size_t), ("private_usage", ctypes.c_size_t)]


_meminfo = None


def private_gb():
    """Return this editor process's committed private bytes in GB, or None if unavailable."""
    global _meminfo
    try:
        if _meminfo is None:
            k32 = ctypes.WinDLL("kernel32")
            k32.GetCurrentProcess.restype = ctypes.c_void_p      # 64-bit pseudo-handle: default int restype truncates it
            f = k32.K32GetProcessMemoryInfo
            f.argtypes = [ctypes.c_void_p, ctypes.POINTER(_Counters), ctypes.c_ulong]
            f.restype = ctypes.c_int
            _meminfo = (f, k32.GetCurrentProcess(), _Counters())
        f, h, c = _meminfo
        c.cb = ctypes.sizeof(c)
        return c.private_usage / float(1 << 30) if f(h, ctypes.byref(c), c.cb) else None
    except Exception:
        return None


def imports_allowed():
    """Hard-stop live asset imports near the safety ceiling."""
    p = private_gb()
    if p is None:
        return True
    if _state.get("imports_paused"):
        if p <= IMPORT_RESUME_GB:
            _state["imports_paused"] = False
            log("imports resumed at %.1f GB private memory" % p)
    elif p >= IMPORT_STOP_GB:
        _state["imports_paused"] = True
        log("imports paused at %.1f GB private memory" % p)
    return not _state["imports_paused"]


def memory_gb():
    s = _MemStatus(); s.dwLength = ctypes.sizeof(s)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    g = float(1 << 30)
    return s.ullAvailPageFile / g, s.ullAvailPhys / g, s.ullTotalPageFile / g


def log(msg):
    unreal.log("[SkyBridgeLive] memory: " + msg)


def _cvars(cmds):
    for c in cmds:
        unreal.SystemLibrary.execute_console_command(None, c)


def _textures(mi):
    """Texture paths a material instance uses (cached per instance path)."""
    p = mi.get_path_name()
    t = _state["deps"].get(p)
    if t is None:
        t = set()
        try:
            if isinstance(mi, unreal.MaterialInstance):
                for v in mi.get_editor_property("texture_parameter_values"):
                    x = v.get_editor_property("parameter_value")
                    if x: t.add(x.get_path_name())
            else:
                t = {x.get_path_name() for x in unreal.MaterialEditingLibrary.get_used_textures(mi) if x}
        except Exception:
            pass
        _state["deps"][p] = t
    return t


def _in_use():
    """(mesh paths, material paths, texture paths) referenced by any component in the level."""
    meshes, mats = set(), {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        for c in a.get_components_by_class(unreal.MeshComponent):
            try:
                m = c.get_editor_property("static_mesh") if isinstance(c, unreal.StaticMeshComponent) else None
                if m:
                    meshes.add(m.get_path_name())
                    for sm in m.static_materials:
                        mi = sm.material_interface
                        if mi: mats[mi.get_path_name()] = mi
                for mi in c.get_materials():
                    if mi: mats[mi.get_path_name()] = mi
            except Exception:
                pass
    tex = set()
    for mi in mats.values():
        tex |= _textures(mi)
    return meshes, set(mats), tex


def sweep(live, now, level):
    paths = _collect(live, now, level)                           # package paths only: a Python wrapper keeps its object loaded
    if not paths:
        return 0
    pkgs = [p for p in (unreal.find_object(None, s) for s in paths) if p]
    try:
        unreal.EditorLoadingAndSavingUtils.unload_packages(pkgs)
    except Exception as e:
        log("unload failed: %s" % e); return 0
    del pkgs
    unreal.SystemLibrary.collect_garbage()
    _state["freed"] += len(paths)
    return len(paths)


def _collect(live, now, level):
    meshes, mats, tex = _in_use()
    idle = _state["idle"]
    cands = []
    for name, m in list(live.mesh_cache.items()):
        if not m:
            continue
        try:
            p = m.get_path_name()
        except Exception:                                       # stale wrapper: drop it, the next live.mesh() reloads
            live.mesh_cache.pop(name, None); continue
        if not p.startswith(MESH_ROOTS) or p in meshes:
            idle.pop(name, None); continue
        since = idle.setdefault(name, now)
        if now - since >= IDLE_S[level]:
            cands.append((name, m))
    if not cands:
        return []
    cands = cands[:MAX_UNLOAD]
    assets = []
    for name, m in cands:
        live.mesh_cache.pop(name, None)
        idle.pop(name, None)
        assets.append(m)
        for sm in m.static_materials:
            mi = sm.material_interface
            if mi and mi.get_path_name() not in mats and mi.get_path_name().startswith(TEX_ROOT + "MI_"):
                assets.append(mi)
                for t in _textures(mi):
                    if t not in tex and t.startswith(TEX_ROOT):
                        o = unreal.find_object(None, t)
                        if o: assets.append(o)
    paths = []
    for a in assets:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(a, True)         # a dirty package would open a save prompt
            pk = a.get_outer().get_path_name()
            _state["deps"].pop(a.get_path_name(), None)
            if pk not in paths:
                paths.append(pk)
        except Exception:
            pass
    return paths


def tick(live):
    now = time.time()
    if not _state["init"]:
        _state["init"] = True
        _cvars(ALWAYS)
        log("governor on (" + ", ".join(ALWAYS) + ")")
    if now - _state["t"] < CHECK_S or "nomemgov" in getattr(live, "_flags", ()):
        return
    _state["t"] = now
    free, phys, total = memory_gb()
    level = sum(free < g for g in LEVEL_FREE_GB)
    if level != _state["level"]:
        _cvars(["r.Streaming.PoolSize %d" % POOL_MB[level], "r.Streaming.MipBias %g" % MIP_BIAS[level]])
        log("level %d (commit free %.1f GB, RAM free %.1f GB): texture pool %d MB, mip bias %g" %
            (level, free, phys, POOL_MB[level], MIP_BIAS[level]))
        _state["level"] = level
    n = None
    if now - _state["sweep_t"] >= SWEEP_S[level]:
        _state["sweep_t"] = now
        t0 = time.time()
        n = sweep(live, now, level)
        if n:
            log("unloaded %d unused packages in %.2f s (total %d)" % (n, time.time() - t0, _state["freed"]))
    st = dict(time=time.strftime("%H:%M:%S"), level=level, commit_free_gb=round(free, 2), ram_free_gb=round(phys, 2),
              pool_mb=POOL_MB[level], cached_meshes=sum(1 for m in live.mesh_cache.values() if m),
              idle_meshes=len(_state["idle"]), unloaded_total=_state["freed"],
              imports_paused=_state["imports_paused"])
    try:
        json.dump(st, open(os.path.join(AREA, "memory_status.json"), "w"), indent=1)
    except Exception:
        pass
