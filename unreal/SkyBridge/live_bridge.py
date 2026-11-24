"""SkyBridge Live: runs inside the Unreal editor (no compiled module, so nothing for Windows to block).
Reads the plugin's two shared-memory streams and mirrors Skyrim into the editor level:
  * camera (player view)  -> editor viewport camera
  * world stream (objects, lights, time, weather) -> static mesh actors, point lights, sun/sky/fog
Missing models are written to area2/requests.txt; tools/asset_service.py converts them and lists them in area2/ready.txt,
and this script imports them on the fly. Start with:  UnrealEditor.exe SkyBridge.uproject -ExecutePythonScript=<this file>
"""
import ctypes, ctypes.wintypes as wt, json, math, os, struct, sys, time
import unreal

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
sys.path.insert(0, os.path.join(ROOT, "unreal", "SkyBridge"))      # so `import ue_assets` works inside the editor
import atmosphere
AREA = os.path.join(ROOT, "area2")
U = 1.4287                                   # Skyrim units -> cm
MAX_SPAWN_PER_TICK = 30
WORLD_RADIUS = 14000.0                       # must match the plugin
RAIN_BOX, RAIN_HEIGHT = 1600.0, 1200.0       # must match remaster_materials.RAIN_BOX/RAIN_HEIGHT
SEA_LEVEL = -14000.0 * U                     # Skyrim's sea level (cm): planet surface for the atmosphere and clouds

# ---- shared memory layout (see shared/BridgeShared.h)
PKT_FMT = "<4I21f2I64s64s64sI11fI21f"; PKT_SIZE = struct.calcsize(PKT_FMT)   # version 2 (a v1 writer leaves the tail 0)
MAX_MODELS, MAX_REFS, MAX_LIGHTS, MODEL_LEN = 4096, 16384, 512, 128
HDR_FMT = "<8I"; HDR = struct.calcsize(HDR_FMT)
REF_FMT = "<II3f9ffI"; REF = struct.calcsize(REF_FMT)
LIGHT_FMT = "<9f"; LIGHT = struct.calcsize(LIGHT_FMT)
MODELS_OFF = HDR; REFS_OFF = MODELS_OFF + MAX_MODELS * MODEL_LEN; LIGHTS_OFF = REFS_OFF + MAX_REFS * REF
WORLD_SIZE = LIGHTS_OFF + MAX_LIGHTS * LIGHT

k32 = ctypes.windll.kernel32
k32.OpenFileMappingW.restype = ctypes.c_void_p
k32.MapViewOfFile.restype = ctypes.c_void_p
k32.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]


def open_map(name):
    h = k32.OpenFileMappingW(4, False, name)
    if not h:
        return None
    return k32.MapViewOfFile(h, 4, 0, 0, 0)


def log(msg):
    unreal.log("[SkyBridgeLive] " + msg)


def V(x, y, z): return unreal.Vector(x, y, z)


def sky_to_ue_pos(p): return V(p[1] * U, p[0] * U, p[2] * U)


def ue_rotation(R):
    """Skyrim row-major rotation R -> UE rotator for a mesh imported through Blender/FBX: A = C * R * diag(1,-1,1)."""
    RF = [R[0], -R[1], R[2], R[3], -R[4], R[5], R[6], -R[7], R[8]]
    row = lambda r: (1, 0, 2)[r]                                   # C swaps rows 0 and 1
    at = lambda r, c: RF[row(r) * 3 + c]
    xa = V(at(0, 0), at(1, 0), at(2, 0)); za = V(at(0, 2), at(1, 2), at(2, 2))
    return unreal.MathLibrary.make_rot_from_xz(xa, za)


class Live:
    def __init__(self):
        self.pkt = None; self.world = None
        self.actors = {}                      # ref id -> dict(actor, model, pos, rot)
        self.mesh_cache = {}                  # asset name -> StaticMesh or None
        self.requested = set(); self.pending = []; self.model_paths = {}
        self.light_actors = []
        self.last_tick = -1
        self.sun = self.moon = self.fog = self.skylight = None
        self.last_ready = 0
        self.t_ready = 0.0
        self.spawn_queue = []
        self.preview = {}                     # ref id -> actor placed from area2/large_preview.json until the stream has it
        self.preview_todo = None
        self.ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        self.fov_set = None
        try:
            self.les.editor_set_game_view(True)
            self.les.editor_set_viewport_realtime(True)
            perf = unreal.find_object(None, "/Script/UnrealEd.Default__EditorPerformanceSettings")
            perf.set_editor_property("bThrottleCPUWhenNotForeground", False)    # keep rendering while Skyrim has focus
        except Exception as e:
            log("viewport setup: %s" % e)
        self.eal = unreal.EditorAssetLibrary
        os.makedirs(AREA, exist_ok=True)
        self.build_environment()
        self.spawn_static_world()
        log("ready; waiting for the Skyrim stream")

    # ------------------------------------------------------------------ environment
    def spawn(self, cls, loc=None, rot=None):
        return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc or V(0, 0, 0), rot or unreal.Rotator(0, 0, 0))

    @staticmethod
    def setp(obj, name, value):
        """Set an editor property, plus its override_ flag for post-process settings; tolerate engine-version differences."""
        try:
            if hasattr(obj, "override_" + name):
                obj.set_editor_property("override_" + name, True)
            obj.set_editor_property(name, value)
        except Exception as e:
            log("property %s: %s" % (name, e))

    def build_environment(self):
        """Physically based outdoor lighting (real sun/moon illuminance, atmosphere, volumetric clouds + fog, Lumen)."""
        sp = self.setp
        for cmd in ("r.Editor.Viewport.ScreenPercentageMode.RealTime 0",   # screen percentage + RR: atmosphere.TIERS
                    "r.NGX.DLSS.Enable 1",                                 # at 100% DLSS = DLAA, below it upscales
                    "r.NGX.DLSSRR.Preset 5", "r.NGX.DLSS.Preset 12"):      # RR: transformer E (default is RR2 F); SR fallback: L
            unreal.SystemLibrary.execute_console_command(None, cmd)
        self.sun = self.spawn(unreal.DirectionalLight)
        c = self.sun.light_component
        sp(c, "atmosphere_sun_light", True); sp(c, "atmosphere_sun_light_index", 0)
        sp(c, "cast_cloud_shadows", True); sp(c, "cast_shadows_on_clouds", True)
        sp(c, "light_source_angle", 0.53)                              # the sun's real angular size: soft shadow edges
        c.set_intensity(0.0)
        self.moon = self.spawn(unreal.DirectionalLight, rot=unreal.Rotator(pitch=-40, yaw=200))
        c = self.moon.light_component
        sp(c, "atmosphere_sun_light", True); sp(c, "atmosphere_sun_light_index", 1)
        sp(c, "light_color", unreal.Color(r=200, g=215, b=255, a=255))   # cool blue-white moonlight
        c.set_intensity(0.0)
        # The world sits ~70 m below the UE origin (Skyrim sea level is z -14000 units): with the default planet top at z=0
        # the camera is underground for the atmosphere, so the sky turns flat and the cloud layer never renders.
        atm = self.spawn(unreal.SkyAtmosphere, V(0, 0, SEA_LEVEL))
        self.atmosphere = atm.get_component_by_class(unreal.SkyAtmosphereComponent)
        sp(self.atmosphere, "transform_mode", unreal.SkyAtmosphereTransformMode.PLANET_TOP_AT_COMPONENT_TRANSFORM)
        self.clouds = self.spawn(unreal.VolumetricCloud)
        cc = self.clouds.get_component_by_class(unreal.VolumetricCloudComponent)
        sp(cc, "layer_bottom_altitude", 2.0); sp(cc, "layer_height", 6.0)   # km above sea level: Skyrim's low cloud deck
        self.skylight = self.spawn(unreal.SkyLight)
        c = self.skylight.light_component
        sp(c, "real_time_capture", True); sp(c, "cast_shadows", True)
        c.set_intensity(1.0)
        self.fog = self.spawn(unreal.ExponentialHeightFog)
        c = self.fog.component
        try:
            c.set_volumetric_fog(True)
        except Exception as e:
            log("volumetric fog: %s" % e)
        sp(c, "volumetric_fog_scattering_distribution", 0.6)
        sp(c, "fog_height_falloff", 0.2)                                # the actor follows the camera height (update_sky)
        pp = self.spawn(unreal.PostProcessVolume)
        pp.set_editor_property("unbound", True)
        s = pp.get_editor_property("settings")
        sp(s, "auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
        sp(s, "auto_exposure_bias", 0.0)                               # per weather in update_sky
        sp(s, "override_color_contrast", True); sp(s, "color_contrast", unreal.Vector4(1.08, 1.08, 1.08, 1.0))
        sp(s, "auto_exposure_min_brightness", 1.5)                     # EV100: lower would brighten moonlit nights to day
        sp(s, "auto_exposure_max_brightness", 16.0)
        sp(s, "auto_exposure_speed_up", 2.0); sp(s, "auto_exposure_speed_down", 1.0)
        sp(s, "motion_blur_amount", 0.0)                               # camera teleports every frame
        sp(s, "bloom_intensity", 0.35)
        sp(s, "vignette_intensity", 0.25)
        sp(s, "film_grain_intensity", 0.0)
        sp(s, "ambient_occlusion_intensity", 0.6)
        sp(s, "lumen_scene_lighting_quality", 1.0)                     # 2.0 costs ~5 ms GPU (shared with Skyrim) for little gain
        sp(s, "lumen_scene_detail", 1.0)
        sp(s, "lumen_final_gather_quality", 1.0)
        sp(s, "lumen_reflection_quality", 1.0)
        sp(s, "lumen_max_trace_distance", 40000.0)
        sp(s, "local_exposure_highlight_contrast_scale", 0.6)          # compresses sunlit ground/sky highlights
        sp(s, "local_exposure_shadow_contrast_scale", 0.8)
        pp.set_editor_property("settings", s)
        self.pp = pp
        atmosphere.apply_quality(self)

    def spawn_static_world(self):
        terrain = self.mesh("terrain")
        if terrain:
            a = self.spawn(unreal.StaticMeshActor, V(0, 0, 0), unreal.Rotator(yaw=90))
            a.static_mesh_component.set_static_mesh(terrain)
            a.set_folder_path("SkyBridge/Terrain")
        lod = self.mesh("lodterrain")                                    # distant mountains from Skyrim's terrain LOD
        if lod:
            a = self.spawn(unreal.StaticMeshActor, V(0, 0, 0), unreal.Rotator(yaw=90))
            a.static_mesh_component.set_static_mesh(lod)
            a.set_folder_path("SkyBridge/Terrain")
        lodw = self.mesh("lodwater")                                     # rivers/lakes: water layer of Skyrim's terrain LOD
        if self.spawn_cell_water():                                      # same water at the same heights: the others would z-fight
            return
        if lodw:
            a = self.spawn(unreal.StaticMeshActor, V(0, 0, 0), unreal.Rotator(yaw=90))
            a.static_mesh_component.set_static_mesh(lodw)
            a.static_mesh_component.set_cast_shadow(False)
            a.set_folder_path("SkyBridge/Water")
        plane = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
        wpath_new = "/Game/Area2Tex/M_SkyWater"
        wmat = unreal.load_asset(wpath_new) if self.eal.does_asset_exist(wpath_new) else unreal.load_asset("/Game/Area2Tex/M_Water")
        wpath = os.path.join(AREA, "water.csv")
        if os.path.exists(wpath) and plane and not lodw:
            for line in open(wpath).read().split():
                f = line.split(",")
                if len(f) < 3: continue
                gx, gy, h = float(f[0]), float(f[1]), float(f[2])
                a = self.spawn(unreal.StaticMeshActor, V((gy + 0.5) * 4096 * U, (gx + 0.5) * 4096 * U, h * U))
                a.static_mesh_component.set_static_mesh(plane)
                if wmat: a.static_mesh_component.set_material(0, wmat)
                a.static_mesh_component.set_cast_shadow(False)
                a.set_actor_scale3d(V(4096 * U / 100, 4096 * U / 100, 1))
                a.set_folder_path("SkyBridge/Water")

    def spawn_cell_water(self):
        """Skyrim's own water: one plane per exterior cell with the 'has water' flag at its XCLW height
        (area2/water_wide.csv from tools/distant_world.py --water; ~470 cells around Whiterun: rivers, lakes, Lake Honrich).
        Terrain above the water hides the plane, exactly like in the game."""
        path = os.path.join(AREA, "water_wide.csv")
        plane = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
        wmat = unreal.load_asset("/Game/Area2Tex/M_SkyWater") if self.eal.does_asset_exist("/Game/Area2Tex/M_SkyWater") else None
        if not os.path.exists(path) or not plane or not wmat:
            return False
        self.water_actors = []
        quads = os.path.join(AREA, "water_quads.csv")
        if os.path.exists(quads):                                         # only where Skyrim's terrain is below the water
            a = self.spawn(unreal.Actor)
            sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            root = sds.k2_gather_subobject_data_for_instance(a)[0]
            sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InstancedStaticMeshComponent))
            c = a.get_components_by_class(unreal.InstancedStaticMeshComponent)[0]
            c.set_static_mesh(plane); c.set_material(0, wmat); c.set_cast_shadow(False)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            xs = []
            for line in open(quads).read().split():
                x0, y0, n, h = line.split(",")
                x0, y0, n, h = int(x0), int(y0), int(n), float(h)
                xs.append(unreal.Transform(V((y0 + 64) * U, (x0 + n * 64) * U, h * U), unreal.Rotator(0, 0, 0),
                                           V(128 * U / 100, n * 128 * U / 100, 1)))
            c.add_instances(xs, False, True)
            a.set_actor_label("CellWater"); a.set_folder_path("SkyBridge/Water")
            try:                                                          # per-strip downhill flow (tools/water_flow.py -> water_flow.csv)
                import water_flow_apply
                log("water flow: %s" % water_flow_apply.apply_flow(a))
            except Exception as e:
                log("water flow skipped: %s" % e)
            self.water_actors.append(a)
            log("cell water: %d strips" % len(xs))
            return True
        for line in open(path).read().split():
            gx, gy, h = line.split(",")
            gx, gy, h = int(gx), int(gy), float(h)
            a = self.spawn(unreal.StaticMeshActor, V((gy + 0.5) * 4096 * U, (gx + 0.5) * 4096 * U, h * U))
            c = a.static_mesh_component
            c.set_static_mesh(plane); c.set_material(0, wmat); c.set_cast_shadow(False)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            a.set_actor_scale3d(V(4096 * U / 100, 4096 * U / 100, 1))
            a.set_folder_path("SkyBridge/Water")
            self.water_actors.append(a)
        log("cell water: %d planes" % len(self.water_actors))
        return True

    # weather family -> (direct-sun factor, fog density, cloud coverage, cloud density, storm clouds, rain, snow)
    # fog density is at camera height (the fog actor follows the camera); coverage stays below 1 so overcast skies keep
    # visible cloud shapes instead of one flat grey sheet
    # Cloud values are on m_SimpleVolumetricCloud's own scale: coverage is a bias (engine default -0.2 = fair-weather cumulus,
    # 0.15-0.2 = broken rain clouds, 0.45 = one flat overcast sheet), density defaults to 0.008 (1.0 renders nothing).
    WEATHER = {"clear": (1.0, 0.003, -0.25, 0.008, 0.0, 0.0, 0.0), "cloud": (0.75, 0.005, 0.0, 0.010, 0.0, 0.0, 0.0),
               "overcast": (0.45, 0.008, 0.3, 0.012, 0.0, 0.0, 0.0), "fog": (0.4, 0.04, 0.2, 0.012, 0.0, 0.0, 0.0),
               "rain": (0.3, 0.02, 0.18, 0.013, 0.0, 1.0, 0.0), "storm": (0.15, 0.03, 0.3, 0.018, 0.5, 1.0, 0.0),
               "snow": (0.4, 0.015, 0.25, 0.012, 0.2, 0.0, 1.0)}

    @staticmethod
    def weather_family(w):
        w = w.lower()
        for k, keys in (("storm", ("storm", "blizzard")), ("rain", ("rain",)), ("snow", ("snow",)), ("fog", ("fog", "mist")),
                        ("overcast", ("overcast",)), ("cloud", ("cloud",))):
            if any(s in w for s in keys): return k
        return "clear"

    def weather_setup(self):
        """Dynamic cloud material, weather parameter collection and the rain curtains (created on first use)."""
        self.wx = {"wet": 0.0, "rain": 0.0, "snow": 0.0, "t": time.time(), "fam": None}
        self.mpc = unreal.load_asset("/Game/Area2Tex/MPC_Weather")
        self.cloud_mid = None
        try:
            cc = self.clouds.get_component_by_class(unreal.VolumetricCloudComponent)
            parent = cc.get_editor_property("material")
            self.cloud_mid = unreal.MaterialInstanceDynamic.create(parent, cc) if hasattr(unreal.MaterialInstanceDynamic, "create") else \
                unreal.MaterialLibrary.create_dynamic_material_instance(unreal.EditorLevelLibrary.get_editor_world(), parent)
            cc.set_material(self.cloud_mid)
        except Exception as e:
            log("cloud material: %s" % e)
        self.night_mid = self.sky_dome = None
        try:
            import remaster_materials
            nm = remaster_materials.night_sky_material()
            a = self.spawn(unreal.StaticMeshActor)
            c = a.static_mesh_component
            c.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere"))
            c.set_mobility(unreal.ComponentMobility.MOVABLE)
            c.set_cast_shadow(False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            c.set_editor_property("affect_distance_field_lighting", False)
            a.set_actor_scale3d(V(2.0e6, 2.0e6, 2.0e6))                  # 1000 km radius: behind all of Skyrim's LOD terrain
            self.night_mid = c.create_dynamic_material_instance(0, nm)
            a.set_actor_label("NightSky"); a.set_folder_path("SkyBridge/Weather")
            self.sky_dome = a
        except Exception as e:
            log("night sky: %s" % e)
        self.rain_actors = []
        self.rain_field = None
        cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
        drops, streak = "/Game/Area2Tex/M_RainDrops", "/Game/Area2Tex/SM_RainStreak"
        if self.eal.does_asset_exist(streak) and self.eal.does_asset_exist(drops) and hasattr(unreal.SkyBridgeViewLibrary, "spawn_rain_field"):
            # 12000 streaks, 7 mm x 35 cm, wrapped by the material into a 16 x 16 x 12 m box around the camera
            self.rain_field = unreal.SkyBridgeViewLibrary.spawn_rain_field(unreal.load_asset(streak), unreal.load_asset(drops), 12000,
                                                                         RAIN_BOX, RAIN_HEIGHT, V(0.007, 0.007, 0.35))
            if self.rain_field:
                self.rain_field.set_folder_path("SkyBridge/Weather")
                self.rain_field.set_is_temporarily_hidden_in_editor(True)
                self.rain_actors.append(self.rain_field)
        rm = unreal.load_asset("/Game/Area2Tex/M_RainCurtain")
        if rm and cyl and not self.rain_field:
            for s in (8.0, 20.0):                                         # near and far curtain: radius 400 / 1000 cm
                a = self.spawn(unreal.StaticMeshActor)
                c = a.static_mesh_component
                c.set_static_mesh(cyl); c.set_material(0, rm); c.set_cast_shadow(False)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
                a.set_actor_scale3d(V(s, s, 25.0)); a.set_folder_path("SkyBridge/Weather")
                a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
                self.rain_actors.append(a)

    def set_weather_param(self, name, value):
        if self.mpc:
            try:
                unreal.MaterialLibrary.set_scalar_parameter_value(unreal.EditorLevelLibrary.get_editor_world(), self.mpc, name, value)
            except Exception as e:
                log("weather param %s: %s" % (name, e)); self.mpc = None

    def set_interior(self, interior):
        """Interior cells have no sky: no sun/moon/clouds/rain, so daylight cannot leak through gaps in the walls."""
        if interior == getattr(self, "_interior", None):
            return
        self._interior = interior
        for a in [self.clouds, getattr(self, "sky_dome", None)] + getattr(self, "distant_actors", []):
            if a: a.set_is_temporarily_hidden_in_editor(interior)
        # interior cells sit at coordinates that overlap the outside world: hide terrain, water and the exterior previews
        outdoor = ("SkyBridge/Terrain", "SkyBridge/Water", "SkyBridge/LargeRefs")
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if str(a.get_folder_path()) in outdoor:
                a.set_is_temporarily_hidden_in_editor(interior)
        s = self.pp.get_editor_property("settings")                      # let the eye adapt to lamp-lit rooms
        s.set_editor_property("auto_exposure_min_brightness", -1.5 if interior else 1.5)
        self.pp.set_editor_property("settings", s)
        self.sun.light_component.set_visibility(not interior)
        self.moon.light_component.set_visibility(not interior)
        self.skylight.light_component.set_intensity(0.15 if interior else 1.0)
        for a in getattr(self, "rain_actors", []):
            a.set_is_temporarily_hidden_in_editor(True)
        if hasattr(self, "wx"): self.wx["rain_on"] = None
        self._sky_key = None

    def streamed_weather(self, v):
        """Packet v2: Skyrim's own weather classification (blended over its transition), sun position/colour and fog."""
        rain, snow, cloudy, pleasant = v[37], v[38], v[39], v[40]
        storm = max(0.0, rain - 0.5) * 2.0 if "storm" in v[27].split(b"\0")[0].decode("latin1").lower() else 0.0
        clear = max(0.0, 1.0 - max(rain, snow, cloudy))
        # the volumetric clouds already shadow the sun; dimming it hard as well leaves them unlit = one flat grey sheet
        mul = 1.0 * clear + 0.6 * cloudy * (1 - rain) + 0.3 * rain + 0.4 * snow * (1 - rain)
        mul = max(0.1, min(1.0, mul - 0.15 * storm))
        fog_far = v[62]
        fog = 0.003 if fog_far <= 0 else max(0.002, min(0.05, 0.001 + 500.0 / fog_far))
        cov = min(0.3, -0.25 + 0.25 * cloudy + 0.43 * rain + 0.45 * snow + 0.12 * storm)   # see WEATHER for the scale
        dens = 0.008 + 0.002 * cloudy + 0.005 * rain + 0.004 * snow + 0.005 * storm
        return mul, fog, cov, dens, storm, rain, snow

    def update_sky(self, hour, weather, cam=None, v=None):
        if not hasattr(self, "wx"):
            self.weather_setup()
        if v is not None:
            self.city_world(v[29].split(b"\0")[0].decode("latin1"))
        if getattr(self, "_interior", False):
            weather = "clear"; v = None
        rise, sett = 5.5, 20.5
        t = (hour - rise) / (sett - rise)
        day = 0 < t < 1
        elev = 70.0 * math.sin(math.pi * t) if day else -25.0
        yaw = (t - 0.5) * 2 * 90.0 if day else 0.0
        if v is not None and any(v[43:46]):
            d = [v[43] - v[10], v[44] - v[11], v[45] - v[12]]           # Skyrim's sun disc relative to the camera
            n = math.sqrt(sum(c * c for c in d)) or 1.0
            elev = math.degrees(math.asin(max(-1.0, min(1.0, d[2] / n))))
            yaw = math.degrees(math.atan2(-d[0], -d[1]))                # UE light points from the sun: X<->Y swapped, negated
        fam = self.weather_family(weather)
        mul, fog, cov, dens, storm, rain, snow = self.WEATHER[fam] if v is None else self.streamed_weather(v)
        if v is not None:
            fam = "s%.2f/%.4f/%.2f/%.3f" % (cov, dens, storm, fog)       # re-apply clouds/fog whenever the blend moves
            sc = [c ** 2.2 for c in v[46:49]]                            # Skyrim's colours are sRGB; UE lights are linear
            if max(sc) > 0.0001:
                m = max(sc)
                col = unreal.LinearColor(sc[0] / m, sc[1] / m, sc[2] / m, 1.0)
                key = tuple(round(c, 2) for c in (col.r, col.g, col.b))
                if key != getattr(self, "_sun_col", None):
                    self._sun_col = key
                    self.sun.light_component.set_light_color(col)
            fc = [0.6 * c ** 2.2 for c in v[52:55]]                      # linear, and dimmer: full-strength fog washes the view white
            if max(fc) > 0.0001:
                key = tuple(round(c, 3) for c in fc)
                if key != getattr(self, "_fog_col", None):
                    self._fog_col = key
                    try:
                        self.fog.component.set_fog_inscattering_color(unreal.LinearColor(fc[0], fc[1], fc[2], 1.0))
                    except Exception:
                        pass
        # wetness builds up over ~1 min of rain and dries over ~4 min; snow cover accumulates over ~2 min
        now = time.time(); dt = min(1.0, now - self.wx["t"]); self.wx["t"] = now
        wx = self.wx
        wx["wet"] = min(1.0, wx["wet"] + dt / 60.0) if rain > 0 else max(0.0, wx["wet"] - dt / 240.0)
        wx["snow"] = min(1.0, wx["snow"] + dt / 120.0) if snow > 0 else max(0.0, wx["snow"] - dt / 300.0)
        wx["rain"] += (rain - wx["rain"]) * min(1.0, dt / 3.0)
        if cam is not None and wx["rain"] > 0.02:
            if self.rain_field:                                          # whole box periods only: the material wrap is unchanged
                p = V(round(cam.x / RAIN_BOX) * RAIN_BOX, round(cam.y / RAIN_BOX) * RAIN_BOX, round(cam.z / RAIN_HEIGHT) * RAIN_HEIGHT)
                if p != getattr(self, "_rain_at", None):
                    self._rain_at = p
                    self.rain_field.set_actor_location(p, False, False)
            else:
                for a in self.rain_actors:
                    a.set_actor_location(V(cam.x, cam.y, cam.z - 600.0), False, False)
        if cam is not None and self.sky_dome and abs(cam.x - getattr(self, "_dome_x", 1e12)) + abs(cam.y - getattr(self, "_dome_y", 0)) > 100000.0:
            self._dome_x, self._dome_y = cam.x, cam.y
            self.sky_dome.set_actor_location(V(cam.x, cam.y, cam.z), False, False)
        if cam is not None and abs(cam.z - 1500.0 - getattr(self, "_fog_z", 1e9)) > 500.0:
            self._fog_z = cam.z - 1500.0                                  # keep the fog layer at the player's altitude
            self.fog.set_actor_location(V(cam.x, cam.y, self._fog_z), False, False)
        visible = wx["rain"] > 0.02
        if visible != wx.get("rain_on"):
            wx["rain_on"] = visible
            for a in self.rain_actors: a.set_is_temporarily_hidden_in_editor(not visible)
        key = (round(elev, 1), fam, round(wx["wet"], 2), round(wx["snow"], 2), round(wx["rain"], 2))
        if key == getattr(self, "_sky_key", None):
            return
        self._sky_key = key
        self.sun.set_actor_rotation(unreal.Rotator(pitch=-elev, yaw=yaw), False)
        dayf = max(0.0, min(1.0, (elev + 2.0) / 10.0))                  # fade in/out around the horizon
        self.sun.light_component.set_intensity(100000.0 * mul * dayf)  # lux; the atmosphere tints and dims it near the horizon
        self.moon.light_component.set_intensity(0.0 if dayf > 0.5 else 0.6 * max(mul, 0.3))
        if self.night_mid:
            # stars once the sun is ~8 degrees down, only through a clear sky; Skyrim draws auroras in its northern
            # clear-night weathers (SkyrimClearSN_*, '*Aurora*')
            w = weather.lower().replace("_", "")
            clear = max(0.0, min(1.0, -cov / 0.25)) * (1.0 - min(1.0, rain + snow))
            night = max(0.0, min(1.0, (2.0 - elev) / 10.0)) * clear
            self.night_mid.set_scalar_parameter_value("Night", night)
            self.night_mid.set_scalar_parameter_value("Aurora", 1.0 if "aurora" in w or "clearsn" in w else 0.0)
        self.set_weather_param("Wetness", wx["wet"]); self.set_weather_param("Snow", wx["snow"]); self.set_weather_param("Rain", wx["rain"])
        if fam != wx["fam"]:
            wx["fam"] = fam
            if self.cloud_mid:
                self.cloud_mid.set_scalar_parameter_value("Cloud_GlobalCoverage", cov)
                self.cloud_mid.set_scalar_parameter_value("Cloud_GlobalDensity", dens)
                self.cloud_mid.set_scalar_parameter_value("StormClouds", storm)
            try:
                self.fog.component.set_fog_density(fog)
                self.fog.component.set_editor_property("volumetric_fog_extinction_scale", 1.0 + 1.5 * (1.0 - mul))
            except Exception:
                pass
            # auto-exposure would lift a rainy day to sunny brightness: keep bad weather darker (EV bias -0.3 clear .. -0.5
            # storm); clear days at +0.3 blew out pale ground and sky
            s = self.pp.get_editor_property("settings")
            s.set_editor_property("auto_exposure_bias", -0.3 - 0.25 * (1.0 - mul))
            self.pp.set_editor_property("settings", s)
        atmosphere.look(self, elev, hour, mul, fog, rain, snow, storm, weather, getattr(self, "_interior", False))

    # ------------------------------------------------------------------ assets
    @staticmethod
    def asset_name(model):
        # requests.txt/ready.txt are whitespace-separated: 'clutter/dining set/x.nif' -> clutter_dining_set_x
        return model[:-4].replace("/", "_").replace(" ", "_") if model.endswith(".nif") else model

    @staticmethod
    def spaced_ok(nif):
        """False for a nif path with a space until the converter names its outputs the same way (it creates
        area2/spaced_names_ok.txt); a request before that would land in failed.txt for good."""
        if " " not in nif:
            return True
        t = time.time()
        if t - Live._sp_t > 30.0:
            Live._sp_t, Live._sp_ok = t, os.path.exists(os.path.join(AREA, "spaced_names_ok.txt"))
        return Live._sp_ok
    _sp_t, _sp_ok = 0.0, False

    def mesh(self, name):
        if self.mesh_cache.get(name) is False:
            return None
        if self.mesh_cache.get(name) is not None:
            return self.mesh_cache[name]
        path = "/Game/Area2/" + name
        m = unreal.load_asset(path) if self.eal.does_asset_exist(path) else None
        if m is not None:
            try:
                if not unreal.SkyBridgeViewLibrary.ensure_mesh_renderable(m):
                    log("mesh has no render data, skipped: " + name)
                    self.mesh_cache[name] = False
                    return None
            except AttributeError:
                pass
        self.mesh_cache[name] = m
        return m

    def request(self, name, model):
        getattr(self, "prefetch", set()).discard(name)                   # needed now: import_ready may take it
        if name in self.requested or not self.spaced_ok(model): return
        self.requested.add(name)
        self.model_paths[name] = model                                   # asset name -> real nif path for the asset service
        import json
        with open(os.path.join(AREA, "models.json"), "w") as f:
            json.dump(self.model_paths, f)
        with open(os.path.join(AREA, "requests.txt"), "a") as f:
            f.write(name + "\n")

    def import_ready(self):
        """Import models that the asset service finished converting (names listed in area2/ready.txt)."""
        p = os.path.join(AREA, "ready.txt")
        if not os.path.exists(p): return
        done = self.__dict__.setdefault("ready_done", set())             # by name: the service may rewrite the file shorter
        # Imports caused the historical 50+ GB runaway. Keep the editor responsive and stop before the safety ceiling.
        try:
            import memory_governor
            if not memory_governor.imports_allowed():
                return
        except Exception:
            pass
        budget = 1                                                        # one blocking import per second
        for name in open(p).read().split():
            if budget <= 0: break
            if name in done or name not in self.requested or name in getattr(self, "prefetch", ()):
                continue                                                  # only what this session needs (prefetch waits)
            done.add(name)
            fbx = os.path.join(AREA, "export", name + ".fbx")
            if not os.path.exists(fbx): continue
            if self.eal.does_asset_exist("/Game/Area2/" + name): continue   # re-importing a mesh in use crashes the renderer
            budget -= 1
            try:
                import ue_assets
                ue_assets.import_model(name)
                self.mesh_cache.pop(name, None)
                log("imported " + name)
            except Exception as e:
                log("import failed for %s: %s" % (name, e))

    # ------------------------------------------------------------------ streams
    def read_world(self):
        if self.world is None:
            self.world = open_map("Local\\SkyrimUnrealBridge_world_v1")
            if self.world is None: return None
        for _ in range(4):
            hdr = struct.unpack(HDR_FMT, ctypes.string_at(self.world, HDR))
            if hdr[0] != 0x444C5257 or hdr[2] & 1: continue
            data = ctypes.string_at(self.world, WORLD_SIZE)
            hdr2 = struct.unpack(HDR_FMT, data[:HDR])
            if hdr2[2] == hdr[2]: return data, hdr2
        return None

    def apply_world(self, data, hdr):
        _, _, _, tick, nref, nmod, nlight, _ = hdr
        models = []
        for i in range(nmod):
            b = data[MODELS_OFF + i * MODEL_LEN: MODELS_OFF + (i + 1) * MODEL_LEN]
            models.append(b.split(b"\0")[0].decode("latin1"))
        seen, occupied = set(), set()
        queued = {q[0] for q in self.spawn_queue}                      # never queue the same reference twice
        for i in range(nref):
            r = struct.unpack_from(REF_FMT, data, REFS_OFF + i * REF)
            rid, mi, pos, rot, scale = r[0], r[1], r[2:5], r[5:14], r[14]
            occupied.add((round(pos[0] / 16), round(pos[1] / 16), round(pos[2] / 16)))
            if rid in getattr(self, "distant_built", ()):                 # already drawn by the distant layer (same form id);
                continue                                                  # not "seen", so an earlier copy gets removed below
            seen.add(rid)
            cur = self.actors.get(rid)
            if cur is None:
                if rid not in queued and " " not in models[mi]:       # asset names cannot contain spaces
                    self.spawn_queue.append((rid, models[mi], pos, rot, scale))
                    queued.add(rid)
            else:
                moved = abs(cur["pos"][0] - pos[0]) + abs(cur["pos"][1] - pos[1]) + abs(cur["pos"][2] - pos[2]) > 1.0
                turned = any(abs(a - b) > 0.01 for a, b in zip(cur["rot"], rot))
                if moved or turned:
                    if not cur.get("movable"):                            # static until it first moves (cheaper for RT/VSM)
                        cur["actor"].static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE); cur["movable"] = True
                    cur["actor"].set_actor_location_and_rotation(sky_to_ue_pos(pos), ue_rotation(rot), False, False)
                    cur["pos"], cur["rot"] = pos, rot
        self.seen_ids = seen
        for rid in list(self.actors):                                   # objects that left the loaded area / were disabled
            if rid not in seen:
                self.actors.pop(rid)["actor"].destroy_actor()
        for rid in [r for r in self.preview if r in seen]:              # the live stream now delivers this large reference
            self.preview.pop(rid).destroy_actor()
        if self.preview_todo is None:
            p = os.path.join(AREA, "large_preview.json")
            self.preview_todo = json.load(open(p)) if os.path.exists(p) else []
        # drop preview pieces that coincide with a streamed object (same spot, different form id: duplicates z-fight)
        def taken(p): return (round(p[0] / 16), round(p[1] / 16), round(p[2] / 16)) in occupied
        self.preview_todo = [it for it in self.preview_todo if it["id"] not in seen and not taken(it["pos"])]
        if not getattr(self, "_preview_pos", None):
            self._preview_pos = {it["id"]: it["pos"] for it in json.load(open(os.path.join(AREA, "large_preview.json")))} \
                if os.path.exists(os.path.join(AREA, "large_preview.json")) else {}
        for rid in [r for r in self.preview if r in self._preview_pos and taken(self._preview_pos[r])]:
            self.preview.pop(rid).destroy_actor()
        self.spawn_queue = [q for q in self.spawn_queue if q[0] in seen]
        self.apply_lights(data, nlight)

    def apply_lights(self, data, n):
        while len(self.light_actors) > n:
            self.light_actors.pop().destroy_actor()
        if not hasattr(self, "light_vals"): self.light_vals = {}
        if not hasattr(self, "light_base"): self.light_base = {}
        for i in range(n):
            vals = struct.unpack_from(LIGHT_FMT, data, LIGHTS_OFF + i * LIGHT)
            prev = self.light_vals.get(i)
            if i < len(self.light_actors) and prev is not None and \
                    sum(abs(a - b) for a, b in zip(prev[:3], vals[:3])) < 24 and prev[3:6] == vals[3:6] and \
                    abs(prev[6] - vals[6]) < 0.15 * max(prev[6], 1.0) and abs(prev[8] - vals[8]) < 0.2:
                continue                                                  # unchanged or torch flicker: hold steady (no shadow pops)
            self.light_vals[i] = vals
            x, y, z, r, g, b, rad, fade, dim = vals
            if i >= len(self.light_actors):
                a = self.spawn(unreal.PointLight); a.set_folder_path("SkyBridge/Lights")
                atmosphere.light_quality(self, a.light_component, i)            # shadow count / fog scattering per tier
                a.light_component.set_source_radius(6.0)
                self.setp(a.light_component, "intensity_units", unreal.LightUnits.CANDELAS)
                self.light_actors.append(a)
            a = self.light_actors[i]
            a.set_actor_location(V(y * U, x * U, z * U), False, False)
            c = a.light_component
            c.set_light_color(unreal.LinearColor(r, g, b, 1.0))
            c.set_attenuation_radius(max(10.0, rad * U))
            cd = 60.0 * max(dim, 0.0) * (0.5 + rad / 600.0)                # candelas: a torch is roughly 50-100 cd
            c.set_intensity(cd)
            self.light_base[i] = (cd, (r, g, b))                           # atmosphere.flicker animates around this

    def spawn_some(self):
        budget = MAX_SPAWN_PER_TICK
        keep = []
        twins = cities = None                                             # model -> spawned refs, built on first need
        city, meta = getattr(self, "city", {}), getattr(self, "city_meta", {})
        for q in self.spawn_queue:
            rid, model, pos, rot, scale = q
            if budget <= 0:
                keep.append(q); continue
            name = self.asset_name(model)
            m = self.mesh(name)
            if m is None:
                if self.mesh_cache.get(name) is not False:
                    self.request(name, model); keep.append(q)
                continue
            if rid in self.actors:                                        # already spawned (defensive)
                continue
            if twins is None:
                twins = {}
                for d in self.actors.values():
                    twins.setdefault(d["model"], []).append(d)
            if any(self.near(d["pos"], pos, 3.0) and all(abs(x - y) < 0.01 for x, y in zip(d["rot"], rot))
                   for d in twins.get(model, ())):
                continue                                                  # exact twin in the game data: one copy, no z-fighting
            a = self.spawn(unreal.StaticMeshActor, sky_to_ue_pos(pos), ue_rotation(rot))
            a.static_mesh_component.set_static_mesh(m)
            self.fix_slots(a.static_mesh_component, m)
            self.water_slots(a.static_mesh_component, model)
            if abs(scale - 1.0) > 1e-3: a.set_actor_scale3d(V(scale, scale, scale))
            a.set_folder_path("SkyBridge/World")
            self.actors[rid] = d = dict(actor=a, model=model, pos=pos, rot=rot)
            twins.setdefault(model, []).append(d)
            if city:
                if cities is None:
                    cities = {}
                    for c in city:
                        if c in meta: cities.setdefault(meta[c][0], set()).add(c)
                hits = {c for c in cities.get(model, ()) if self.near(meta[c][1], pos)}
                if rid in city: hits.add(rid)
                for cid in hits:                                          # the stream took over this city reference
                    city.pop(cid).destroy_actor()
                    if cid in meta: cities.get(meta[cid][0], set()).discard(cid)
            budget -= 1
        self.spawn_queue = keep
        budget = self.city_some(budget)
        while budget > 0 and self.preview_todo and not getattr(self, "_interior", False):
            it = self.preview_todo.pop()
            m = self.mesh(it["model"])
            if m is None or it["id"] in self.preview or it["id"] in self.actors or it["id"] in getattr(self, "city", {}) or \
                    it["id"] in getattr(self, "distant_built", ()):
                continue                                                  # a second copy in the same spot z-fights (flicker)
            a = self.spawn(unreal.StaticMeshActor, sky_to_ue_pos(it["pos"]), ue_rotation(it["rot"]))
            a.static_mesh_component.set_static_mesh(m)
            self.fix_slots(a.static_mesh_component, m)
            if abs(it["scale"] - 1.0) > 1e-3: a.set_actor_scale3d(V(it["scale"], it["scale"], it["scale"]))
            a.set_folder_path("SkyBridge/LargeRefs")
            self.preview[it["id"]] = a
            budget -= 1

    # ------------------------------------------------------------------ city completion
    CITY_WORLDS = {"Whiterun": "whiterunworld", "Solitude": "solitudeworld", "Windhelm": "windhelmworld",
                   "Markarth": "markarthworld", "Riften": "riftenworld"}
    LOOSE_ITEMS = {"ALCH", "BOOK", "INGR", "MISC", "WEAP", "ARMO", "KEYM", "SLGM", "AMMO", "SCRL"}
    # furniture whose nif is named "...marker" but is the real mesh (the plugin drops every "marker" model)
    REAL_MARKERS = ("forge", "tanningrack", "smelter", "grindstone", "anvil", "workbench", "enchant", "alchemy",
                    "cookingpot", "cookingspit")

    def city_world(self, ws):
        """Entering a city worldspace loads area2/world_<edid>.json (tools/distant_world.py --world <edid>): every placed
        reference from Skyrim.esm/Update.esm, so pieces the stream never delivers (crafting stations with 'marker' in
        the model name, models with spaces) or has not loaded yet are still drawn. Streamed copies replace them."""
        if not getattr(self, "_prefetched", False) and os.path.exists(os.path.join(AREA, "prefetch_on.txt")):   # opt-in: it imported ~100 assets/min and filled RAM
            self._prefetched = True
            self.prefetch_cities()
        self.prefetch_step()
        if not ws:
            ws = self.interior_key()
        else:
            self._int_t = 0                                               # re-detect right away on the next door
        if ws == getattr(self, "_city_ws", None):
            return
        self._city_ws = ws
        for a in getattr(self, "city", {}).values():
            a.destroy_actor()
        self.city, self.city_todo = {}, []
        if "nocity" in self._flags:
            return
        if ws.startswith("int:"):
            self.city_todo = [it for it in self.interiors[ws[4:]]["refs"] if self.city_keep(it)]
            log("interior %s: %d references" % (ws[4:], len(self.city_todo)))
            return
        edid = self.CITY_WORLDS.get(ws)
        p = os.path.join(AREA, "world_%s.json" % edid) if edid else ""
        if not p or not os.path.exists(p):
            return
        self.city_todo = [it for it in json.load(open(p)) if self.city_keep(it)]
        log("city %s: %d references" % (ws, len(self.city_todo)))

    def load_interiors(self):
        """area2/interiors_<prefix>.json (tools/distant_world.py --interiors Whiterun): every reference of those cells."""
        if hasattr(self, "interiors"):
            return
        self.interiors, self.interior_of = {}, {}
        import glob
        for p in sorted(glob.glob(os.path.join(AREA, "interiors_*.json")), key=lambda p: "whiterun" not in p):
            if os.path.basename(p).startswith("interiors_dungeons_"):
                continue                                                  # ~570 cells / 540 MB: loaded per cell below
            for edid, cell in json.load(open(p)).items():
                self.interiors[edid] = cell
                for it in cell["refs"]:
                    self.interior_of[it["id"]] = edid
        # dungeons (distant_world.py --dungeons): only a few probe ids per cell stay in memory until the player is inside
        self.dungeon_cells, self.dungeon_of = {}, {}
        p = os.path.join(AREA, "dungeon_index.json")
        if os.path.exists(p):
            for edid, d in json.load(open(p)).items():
                self.dungeon_cells[edid] = d
                for rid in d["probe"]:
                    self.dungeon_of[rid] = edid

    def load_dungeon(self, edid):
        """Read one dungeon cell from its interiors_dungeons_<n>.json (the rest of that file is dropped again)."""
        if edid not in self.interiors:
            cell = json.load(open(os.path.join(AREA, self.dungeon_cells[edid]["file"])))[edid]
            self.interiors[edid] = cell
            for it in cell["refs"]:
                self.interior_of[it["id"]] = edid

    def interior_key(self):
        """Which known interior cell the player is in: the one most of the streamed references belong to ('int:<edid>'),
        '' while unknown (no match yet, or a cell that was not dumped)."""
        self.load_interiors()
        if time.time() - getattr(self, "_int_t", 0) < 2.0:
            return getattr(self, "_int_key", "")
        self._int_t = time.time()
        votes = {}
        for rid in getattr(self, "seen_ids", ()):
            e = self.interior_of.get(rid)
            if e: votes[e] = votes.get(e, 0) + 1
        best = max(votes, key=votes.get) if votes else None
        if not (best and votes[best] >= 5):
            dv = {}
            for rid in getattr(self, "seen_ids", ()):
                e = self.dungeon_of.get(rid)
                if e: dv[e] = dv.get(e, 0) + 1
            best = max(dv, key=dv.get) if dv else None
            if best and dv[best] >= min(5, len(self.dungeon_cells[best]["probe"])):
                self.load_dungeon(best)
                votes[best] = 5
        self._int_key = "int:" + best if best and votes.get(best, 0) >= 5 else ""
        return self._int_key

    @classmethod
    def city_keep(cls, it):
        m = it["nif"]
        if it["disabled"] or it["parent"] or it["type"] in cls.LOOSE_ITEMS or " " in it["model"]:
            return False                                                  # enable-parented: quest state, trust the stream
        if m.startswith(("effects/", "fx")) or "/fx" in m:
            return False
        return "marker" not in m or any(k in m for k in cls.REAL_MARKERS)

    def prefetch_cities(self):
        """Queue every model of the dumped interiors and the other cities that was never converted, so arriving there does
        not wait for hundreds of conversions. They are imported only when that place needs them (imports stall the editor)."""
        if "nocity" in self._flags:
            return
        self.prefetch = getattr(self, "prefetch", set())
        self.load_interiors()
        new = {}
        lists = [c["refs"] for c in self.interiors.values()]             # interiors first, then the other cities
        for edid in self.CITY_WORLDS.values():
            p = os.path.join(AREA, "world_%s.json" % edid)
            if os.path.exists(p):
                lists.append(json.load(open(p)))
        for items in lists:
            for it in items:
                name = it["model"]
                if name in new or name in self.requested or not self.city_keep(it) or not self.spaced_ok(it["nif"]) or \
                        os.path.exists(os.path.join(ROOT, "unreal", "SkyBridge", "Content", "Area2", name + ".uasset")):
                    continue
                new[name] = it["nif"]
        p = os.path.join(AREA, "dungeon_models.txt")                      # then dungeon pieces, most used first
        if os.path.exists(p):
            for line in open(p):
                f = line.rstrip("\n").split("\t")
                if line.startswith("#") or len(f) < 4 or f[3] == "1" or f[1] in new or f[1] in self.requested or \
                        not self.spaced_ok(f[2]):
                    continue
                if not os.path.exists(os.path.join(ROOT, "unreal", "SkyBridge", "Content", "Area2", f[1] + ".uasset")):
                    new[f[1]] = f[2]
        self.prefetch_todo = list(new.items())
        if new:
            log("prefetch: %d city models to convert in the background" % len(new))

    def prefetch_step(self):
        """The asset service converts everything pending as one batch: feed it 40 at a time, after the previous batch is
        finished, so models the stream needs right now never wait behind hundreds of prefetched ones."""
        todo = getattr(self, "prefetch_todo", None)
        if not todo or time.time() - getattr(self, "_pf_t", 0) < 20.0:
            return
        self._pf_t = time.time()
        finished = set()
        for n in ("ready.txt", "failed.txt"):
            p = os.path.join(AREA, n)
            if os.path.exists(p):
                finished |= set(open(p).read().split())
        if any(n not in finished for n in getattr(self, "_pf_chunk", ())):
            return
        chunk, self.prefetch_todo = dict(todo[:40]), todo[40:]
        chunk = {n: nif for n, nif in chunk.items() if n not in self.requested}
        self._pf_chunk = list(chunk)
        self.prefetch |= set(chunk)
        self.requested |= set(chunk)
        self.model_paths.update(chunk)
        with open(os.path.join(AREA, "models.json"), "w") as f:
            json.dump(self.model_paths, f)
        with open(os.path.join(AREA, "requests.txt"), "a") as f:
            f.write("".join(n + "\n" for n in chunk))

    @staticmethod
    def near(p, q, d=300.0):
        return abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) < d

    def city_some(self, budget):
        todo, waiting = getattr(self, "city_todo", []), []
        if getattr(self, "city_wait", None) and time.time() - getattr(self, "_city_t", 0) > 3.0:
            self._city_t = time.time()                                    # recheck unconverted models every few seconds
            todo[:0], self.city_wait = self.city_wait, []
        streamed = placed = None                                          # nif -> positions, built on first need
        while budget > 0 and todo:
            it = todo.pop()
            rid = it["id"]
            if rid in self.actors or rid in self.city or rid in self.preview or rid in getattr(self, "distant_built", ()):
                continue
            meta = self.__dict__.setdefault("city_meta", {})
            if streamed is None:
                streamed, placed = {}, {}
                for d in self.actors.values():
                    streamed.setdefault(d["model"], []).append(d["pos"])
                for c in self.city:
                    if c in meta: placed.setdefault(meta[c][0], []).append(meta[c][1])
            if any(self.near(p, it["pos"]) for p in streamed.get(it["nif"], ())):
                continue                                                  # a mod moved/replaced it: the stream has its copy
            if any(self.near(p, it["pos"], 3.0) for p in placed.get(it["nif"], ())):
                continue                                                  # exact twin in the game data
            m = self.mesh(it["model"])
            if m is None:
                if self.mesh_cache.get(it["model"]) is not False:          # not converted yet: ask, retry later
                    self.request(it["model"], it["nif"]); waiting.append(it)
                continue
            a = self.spawn(unreal.StaticMeshActor, sky_to_ue_pos(it["pos"]), ue_rotation(it["rot"]))
            a.static_mesh_component.set_static_mesh(m)
            self.fix_slots(a.static_mesh_component, m)
            self.water_slots(a.static_mesh_component, it["nif"])
            if abs(it["scale"] - 1.0) > 1e-3: a.set_actor_scale3d(V(it["scale"], it["scale"], it["scale"]))
            a.set_folder_path("SkyBridge/City")
            self.city[rid] = a
            meta[rid] = (it["nif"], it["pos"])
            placed.setdefault(it["nif"], []).append(it["pos"])
            budget -= 1
        self.city_wait = getattr(self, "city_wait", []) + waiting
        return budget

    # ------------------------------------------------------------------ distant world
    def distant_setup(self):
        """area2/distant_refs.json (tools/distant_world.py): Skyrim's placed mountains/cliffs/rocks/trees well beyond the
        loaded cells, one instanced-mesh actor per model (43k refs, ~130 models). Mountains first (the file is sorted)."""
        p = os.path.join(AREA, "distant_refs.json")
        items = json.load(open(p)) if os.path.exists(p) and "nodistant" not in self._flags else []
        self.distant = {}
        for it in items:
            self.distant.setdefault(it["model"], []).append(it)
        self.distant_todo = list(self.distant)
        self.distant_built = set()                                       # ref ids drawn by the layer: the stream skips them
        self.distant_actors = []
        log("distant world: %d refs, %d models" % (len(items), len(self.distant)))

    @staticmethod
    def water_slots(comp, model):
        """Skyrim water meshes (Whiterun canals, pools, water/water1024) use the water shader, which has no texture: the
        import leaves a 'Null' slot (M_Hidden), so canals rendered as empty black beds. Give those slots M_SkyWater.
        Nanite cannot draw Single Layer Water, so those components are drawn as regular (non-Nanite) meshes."""
        m = model.lower()
        if not any(k in m for k in ("water", "river", "stream")) or "waterfall" in m:
            return
        mat = Live.__dict__.get("_water_mat")
        if mat is None:
            p = "/Game/Area2Tex/M_SkyWater"
            mat = Live._water_mat = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else False
        if not mat:
            return
        hit = False
        for i, sm in enumerate(comp.static_mesh.static_materials):
            if str(sm.material_slot_name).lower() in ("null", "none"):
                comp.set_material(i, mat)
                hit = True
        if hit:
            try:
                comp.set_editor_property("disallow_nanite", True)
            except Exception:
                pass

    @staticmethod
    def fix_slots(comp, mesh):
        """Slots imported before their colour map existed (white, unmasked): override on the component. Editing the mesh
        asset itself while it is rendered is unsafe; remaster_materials.fix_missing_slots does that headless."""
        import ue_assets
        cache = Live.__dict__.get("_slot_fix")
        if cache is None:
            cache = Live._slot_fix = {}
        for i, sm in enumerate(mesh.static_materials):
            mat = sm.material_interface
            slot = str(sm.material_slot_name)
            if mat is not None and mat.get_name().startswith(("MI_", "M_Hidden")) and \
                    not slot.lower().startswith("textures_effects_"):
                continue
            if slot not in cache:
                cache[slot] = ue_assets.slot_material(slot)
            if cache[slot]:
                comp.set_material(i, cache[slot])

    def distant_some(self):
        """Check a few models per tick; build at most one instanced actor (adding thousands of instances takes a moment)."""
        if not hasattr(self, "distant"):
            self.distant_setup()
        for _ in range(min(4, len(self.distant_todo))):
            model = self.distant_todo.pop(0)
            m = self.mesh(model)
            if m is None:
                if self.mesh_cache.get(model) is not False:
                    self.request(model, self.distant[model][0]["nif"])
                    self.distant_todo.append(model)
                continue
            items = self.distant[model]
            a = self.spawn(unreal.Actor)
            sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            root = sds.k2_gather_subobject_data_for_instance(a)[0]
            sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InstancedStaticMeshComponent))
            c = a.get_components_by_class(unreal.InstancedStaticMeshComponent)[0]
            c.set_static_mesh(m)
            self.fix_slots(c, m)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            if items[0]["kind"] in ("tree", "rock"):
                c.set_cull_distances(0, int(300000 if items[0]["kind"] == "tree" else 200000))   # cm; trees ~+0.5 ms GPU at 3 km
            xs = [unreal.Transform(sky_to_ue_pos(it["pos"]), ue_rotation(it["rot"]), V(it["scale"], it["scale"], it["scale"]))
                  for it in items]
            c.add_instances(xs, False, True)
            a.set_actor_label("Distant_" + model[:60])
            a.set_folder_path("SkyBridge/Distant")
            if getattr(self, "_interior", False):
                a.set_is_temporarily_hidden_in_editor(True)
            self.distant_actors.append(a)
            self.distant_built.update(it["id"] for it in items)
            log("distant: %s x%d" % (model, len(items)))
            return

    # ------------------------------------------------------------------ add-on layers
    def addons_tick(self, dt):
        """Optional layer modules (grass_live, lod_objects_live, land_terrain_live, weather_fx, ...), one module name per
        line in area2/addons.txt. Each may define spawn(live) (once), update(live, cam[, dt]) (every tick) and clear(live)
        (when removed from the file). A module that keeps failing is switched off for the session."""
        import importlib, inspect
        now = time.time()
        if now - getattr(self, "_addons_t", 0) > 2.0:
            self._addons_t = now
            try:
                want = [l.strip() for l in open(os.path.join(AREA, "addons.txt")) if l.strip() and not l.startswith("#")]
            except OSError:
                want = []
            self._addons = getattr(self, "_addons", {})
            for name in list(self._addons):
                if name not in want:
                    mod = self._addons.pop(name)["mod"]
                    if mod and hasattr(mod, "clear"):
                        try:
                            mod.clear(self)
                        except Exception as e:
                            log("addon %s clear error: %s" % (name, e))
                    log("addon off: %s" % name)
            for name in want:
                if name in self._addons:
                    continue
                st = self._addons[name] = {"mod": None, "errs": 0, "last": None}
                try:
                    mod = importlib.import_module(name)
                    if hasattr(mod, "spawn"):
                        mod.spawn(self)
                    st["mod"] = mod
                    st["nargs"] = len(inspect.signature(mod.update).parameters) if hasattr(mod, "update") else 0
                    log("addon on: %s" % name)
                except Exception as e:
                    log("addon %s failed to start: %s" % (name, e))
        cam = self.ues.get_level_viewport_camera_info()[0] if getattr(self, "_addons", None) else None
        for name, st in getattr(self, "_addons", {}).items():
            mod = st["mod"]
            if not mod or not hasattr(mod, "update") or st["errs"] >= 20:
                continue
            try:
                mod.update(self, cam, dt) if st["nargs"] >= 3 else mod.update(self, cam)
                st["errs"] = 0
            except Exception as e:
                st["errs"] += 1
                if str(e) != st["last"]:
                    st["last"] = str(e)
                    log("addon %s error: %s" % (name, e))
                if st["errs"] >= 20:
                    log("addon %s switched off after repeated errors" % name)

    # ------------------------------------------------------------------ tick
    def tick(self, dt):
        if getattr(self, "_in_tick", False):                              # an import pumps Slate, which re-enters tick: a
            return                                                        # half-built mesh touched then asserts in the engine
        self._in_tick = True
        try:
            self.tick_body(dt)
        finally:
            self._in_tick = False

    def tick_body(self, dt):
        now0 = time.time()
        if now0 - getattr(self, "_flags_t", 0.0) > 0.5 or not hasattr(self, "_flags"):
            self._flags_t = now0
            try:
                with open(os.path.join(AREA, "debug_flags.txt")) as f:
                    self._flags = f.read().split()
            except Exception:
                self._flags = []
        flags = self._flags
        if now0 - getattr(self, "_hb", 0) > 5.0:                         # heartbeat so a silent exit is visible in the log
            self._hb = now0
            log("alive: %d actors, %d queued, %d lights" % (len(self.actors), len(self.spawn_queue), len(self.light_actors)))
        if now0 - getattr(self, "_sweep_t", now0 - 25.0) > 30.0:
            self._sweep_t = now0
            atmosphere.sweep_captures(self)
        if "notick" in flags: return
        shot = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\shot_request.txt"
        if os.path.exists(shot):
            try:
                os.remove(shot)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, r"C:\Users\Aidan\SkyrimUnrealBridge\shot_ue.png")
                log("screenshot requested")
            except Exception as e:
                log("screenshot failed: %s" % e)
        req = os.path.join(AREA, "exec_request.py")
        if os.path.exists(req):                                           # debug hook: run a script inside the editor
            import io, traceback, contextlib
            src = open(req).read(); os.remove(req)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    exec(src, {"unreal": unreal, "live": self, "V": V, "U": U})
                except Exception:
                    traceback.print_exc(file=buf)
            with open(os.path.join(AREA, "exec_out.txt"), "w") as f:
                f.write(buf.getvalue())
        try:
            if self.pkt is None:
                self.pkt = open_map("Local\\SkyrimUnrealBridge_v1")
            if self.pkt and "nocam" not in flags:
                v = struct.unpack(PKT_FMT, ctypes.string_at(self.pkt, PKT_SIZE))
                if v[0] == 0x42554B53 and v[3] > 0:
                    camp, rot = v[10:13], v[13:22]
                    self.cam_sky = camp
                    self.ws_name = v[29].split(b"\0")[0].decode("latin1")
                    fwd = V(rot[4], rot[1], rot[7]); up = V(rot[5], rot[2], rot[8])     # col1 / col2, X<->Y swapped
                    cam = sky_to_ue_pos(camp)
                    self.ues.set_level_viewport_camera_info(cam, unreal.MathLibrary.make_rot_from_xz(fwd, up))
                    weather = v[27].split(b"\0")[0].decode("latin1")
                    self.set_interior(not v[29].split(b"\0")[0])                  # no worldspace = interior cell
                    ovr = getattr(self, "_sky_override", None)           # (hour, weather name): preview via the exec hook
                    if ovr:
                        self.update_sky(ovr[0], ovr[1], cam, None)
                    else:
                        self.update_sky(v[23], weather, cam, v if v[1] >= 2 else None)
                    atmosphere.flicker(self, cam, now0)
                    if v[22] > 1:
                        fov = round(v[22], 1)                              # Skyrim's FOV is horizontal, like UE's
                        if fov != self.fov_set:
                            self.les.set_level_viewport_fov(fov, self.les.get_active_viewport_config_key())
                            self.fov_set = fov
            now = time.time()
            if now - self.t_ready > 1.0:
                self.t_ready = now
                if "noimport" not in flags: self.import_ready()
                w = self.read_world() if "noworld" not in flags else None
                if w and w[1][3] != self.last_tick:
                    self.last_tick = w[1][3]
                    self.apply_world(*w)
            self.spawn_some()
            if "notamriel" not in flags:                                  # all of Tamriel (tamriel_live.py)
                try:
                    import tamriel_live
                    tamriel_live.tick(self)
                except Exception as e:
                    import traceback
                    tb = traceback.extract_tb(e.__traceback__)[-1]
                    if str(e) != getattr(self, "_tam_err", None):
                        self._tam_err = str(e)
                        log("tamriel error: %s (%s line %d)" % (e, tb.name, tb.lineno))
            if "nodistant" not in flags and not getattr(self, "_tamriel_on", False):
                self.distant_some()                                       # Whiterun-only predecessor of the Tamriel layer
            if "nonpc" not in flags:                                      # NPCs from the actor stream (npc_live.py)
                try:
                    import npc_live
                    npc_live.tick(self)
                except Exception as e:
                    import traceback
                    tb = traceback.extract_tb(e.__traceback__)[-1]
                    if str(e) != getattr(self, "_npc_err", None):
                        self._npc_err = str(e)
                        log("npc error: %s (%s line %d)" % (e, tb.name, tb.lineno))
            self.addons_tick(dt)
            try:                                                          # memory pressure + unloading unused assets
                import memory_governor
                memory_governor.tick(self)
            except Exception as e:
                if str(e) != getattr(self, "_mem_err", None):
                    self._mem_err = str(e)
                    log("memory governor error: %s" % e)
        except Exception as e:
            import traceback
            tb = traceback.extract_tb(e.__traceback__)[-1]
            log("tick error: %s (%s line %d)" % (e, tb.name, tb.lineno))


_live = None
_handle = None


def start():
    global _live, _handle
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    _live = Live()
    _handle = unreal.register_slate_post_tick_callback(_live.tick)


start()
