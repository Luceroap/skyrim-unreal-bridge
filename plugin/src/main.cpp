#include "RE/Skyrim.h"
#include "SKSE/SKSE.h"
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cmath>
#include <thread>
#include <windows.h>

#include "../../shared/BridgeShared.h"

namespace
{
	SkyBridge::Packet* g_packet = nullptr;
	std::atomic<bool>  g_run{ true };
	std::uint32_t      g_frame = 0;
	std::uint8_t*      g_world = nullptr;   // live world stream mapping (see ScanWorld below)

	void CopyStr(char* dst, std::size_t cap, const char* src)
	{
		std::memset(dst, 0, cap);
		if (src) {
			std::strncpy(dst, src, cap - 1);
		}
	}

	// Menus during which the player must see Skyrim's own frame (Unreal's view hides menus and the HUD).
	constexpr const char* kSkyrimMenus[] = { "InventoryMenu", "MagicMenu", "MapMenu", "Journal Menu", "TweenMenu", "StatsMenu",
		"Sleep/Wait Menu", "Console", "Dialogue Menu", "Barter Menu", "Container Menu", "Crafting Menu", "Lockpicking Menu",
		"Book Menu", "Favorites Menu", "GiftMenu", "Training Menu", "RaceSex Menu", "MessageBoxMenu", "Tutorial Menu",
		"LevelUp Menu", "Creation Club Menu", "Mod Manager Menu", "Credits Menu" };

	std::uint32_t UiFlags(RE::PlayerCharacter* player)
	{
		std::uint32_t f = 0;
		if (auto* ui = RE::UI::GetSingleton()) {
			if (ui->IsMenuOpen("Main Menu")) f |= SkyBridge::kUiMainMenu;
			if (ui->IsMenuOpen("Loading Menu")) f |= SkyBridge::kUiLoading;
			bool show = ui->GameIsPaused() || (f & (SkyBridge::kUiMainMenu | SkyBridge::kUiLoading));
			for (auto* m : kSkyrimMenus) {
				if (show) break;
				show = ui->IsMenuOpen(m);
			}
			if (show) f |= SkyBridge::kUiShowSkyrim;
		}
		if (player && player->Is3DLoaded()) {
			f |= SkyBridge::kUiInWorld;
			if (player->IsInCombat()) f |= SkyBridge::kUiCombat;
			if (player->IsSneaking()) f |= SkyBridge::kUiSneaking;
			if (auto* st = player->AsActorState(); st && st->IsWeaponDrawn()) f |= SkyBridge::kUiWeaponDrawn;
		} else {
			f |= SkyBridge::kUiShowSkyrim;
		}
		return f;
	}

	void Stat(RE::PlayerCharacter* player, RE::ActorValue av, float out[2])
	{
		auto* o = player->AsActorValueOwner();
		out[0] = o->GetActorValue(av);
		out[1] = o->GetPermanentActorValue(av) + player->GetActorValueModifier(RE::ACTOR_VALUE_MODIFIER::kTemporary, av);
	}

	void Col(const RE::NiColor& c, float out[3]) { out[0] = c.red; out[1] = c.green; out[2] = c.blue; }

	void SampleWeather(SkyBridge::Packet* p, RE::Sky* sky)
	{
		using F = RE::TESWeather::WeatherDataFlag;
		auto cls = [](RE::TESWeather* w, F f) { return w && w->data.flags.any(f) ? 1.0f : 0.0f; };
		const float t = (sky->lastWeather && sky->lastWeather != sky->currentWeather) ? std::clamp(sky->currentWeatherPct, 0.0f, 1.0f) : 1.0f;
		auto blend = [&](F f) { return cls(sky->currentWeather, f) * t + cls(sky->lastWeather, f) * (1.0f - t); };
		p->rain = blend(F::kRainy);
		p->snow = blend(F::kSnow);
		p->cloudy = blend(F::kCloudy);
		p->pleasant = blend(F::kPleasant);
		p->weatherPct = t;
		p->lastWeatherFormID = sky->lastWeather ? sky->lastWeather->GetFormID() : 0;
		if (sky->sun && sky->sun->sunBaseNode) {
			const auto& s = reinterpret_cast<RE::NiAVObject*>(sky->sun->sunBaseNode.get())->world.translate;   // NiBillboardNode : NiNode
			p->sunPos[0] = s.x; p->sunPos[1] = s.y; p->sunPos[2] = s.z;
		}
		using C = RE::TESWeather::ColorTypes;
		Col(sky->skyColor[C::kSunlight], p->sunColor);
		Col(sky->skyColor[C::kAmbient], p->ambientColor);
		Col(sky->skyColor[C::kFogNear], p->fogColor);
		Col(sky->skyColor[C::kSkyUpper], p->skyUpper);
		Col(sky->skyColor[C::kHorizon], p->horizon);
		p->fogNear = sky->fogNear;
		p->fogFar = sky->fogFar;
		p->windSpeed = sky->windSpeed;
	}

	// Runs on the game's main thread (queued via the SKSE task interface).
	void Sample()
	{
		auto* p = g_packet;
		auto* player = RE::PlayerCharacter::GetSingleton();
		auto* cam = RE::PlayerCamera::GetSingleton();
		if (!p) {
			return;
		}
		if (!player || !cam || !player->Is3DLoaded()) {
			p->seq++;
			p->uiFlags = UiFlags(player);
			p->seq++;
			return;
		}

		p->seq++;  // odd: writing
		p->frame = ++g_frame;
		p->uiFlags = UiFlags(player);
		Stat(player, RE::ActorValue::kHealth, p->health);
		Stat(player, RE::ActorValue::kMagicka, p->magicka);
		Stat(player, RE::ActorValue::kStamina, p->stamina);

		auto pos = player->GetPosition();
		p->playerPos[0] = pos.x;
		p->playerPos[1] = pos.y;
		p->playerPos[2] = pos.z;
		p->playerAngle[0] = player->GetAngleX();
		p->playerAngle[1] = player->GetAngleY();
		p->playerAngle[2] = player->GetAngleZ();

		if (cam->cameraRoot) {
			const auto& w = cam->cameraRoot->world;
			p->camPos[0] = w.translate.x;
			p->camPos[1] = w.translate.y;
			p->camPos[2] = w.translate.z;
			for (int r = 0; r < 3; ++r)
				for (int c = 0; c < 3; ++c)
					p->camRot[r * 3 + c] = w.rotate.entry[r][c];
		}

		p->fovDeg = cam->worldFOV;

		if (auto* cal = RE::Calendar::GetSingleton()) {
			p->gameHour = cal->GetHour();
			p->gameDays = cal->GetDaysPassed();
		}

		CopyStr(p->crosshair, sizeof p->crosshair, nullptr);          // what the crosshair points at, as "<verb>\t<name>"
		if (auto* cp = RE::CrosshairPickData::GetSingleton()) {
			if (auto ref = cp->target.get()) {
				const char* nm = ref->GetDisplayFullName();
				const char* verb = "Activate";
				if (auto* bo = ref->GetBaseObject()) {
					switch (bo->GetFormType()) {
					case RE::FormType::NPC: verb = ref->IsDead() ? "Search" : "Talk"; break;
					case RE::FormType::Door: verb = "Open"; break;
					case RE::FormType::Container: verb = "Search"; break;
					case RE::FormType::Furniture: verb = "Use"; break;
					case RE::FormType::Weapon: case RE::FormType::Armor: case RE::FormType::Misc: case RE::FormType::Book:
					case RE::FormType::Ingredient: case RE::FormType::AlchemyItem: case RE::FormType::Scroll: case RE::FormType::KeyMaster:
					case RE::FormType::Ammo: case RE::FormType::SoulGem: verb = "Take"; break;
					case RE::FormType::Flora: case RE::FormType::Tree: verb = "Harvest"; break;
					default: break;
					}
				}
				if (nm && *nm) {
					std::string s = std::string(verb) + "\t" + nm;
					CopyStr(p->crosshair, sizeof p->crosshair, s.c_str());
				}
			}
		}

		p->weatherFormID = 0;
		CopyStr(p->weatherEditorID, sizeof p->weatherEditorID, nullptr);
		if (auto* sky = RE::Sky::GetSingleton(); sky && sky->currentWeather) {
			p->weatherFormID = sky->currentWeather->GetFormID();
			CopyStr(p->weatherEditorID, sizeof p->weatherEditorID, sky->currentWeather->GetFormEditorID());
			SampleWeather(p, sky);
		}

		p->cellFormID = 0;
		CopyStr(p->cellName, sizeof p->cellName, nullptr);
		if (auto* cell = player->GetParentCell()) {
			p->cellFormID = cell->GetFormID();
			CopyStr(p->cellName, sizeof p->cellName, cell->GetName());
		}
		CopyStr(p->worldspaceName, sizeof p->worldspaceName, nullptr);
		if (auto* ws = player->GetWorldspace()) {
			CopyStr(p->worldspaceName, sizeof p->worldspaceName, ws->GetName());
		}

		p->seq++;  // even: stable
	}

	// Opt-in: if Data/SKSE/Plugins/SkyrimUnrealBridge.autoload exists, load the newest save from the main menu.
	void AutoLoadLatestSave()
	{
		namespace fs = std::filesystem;
		if (!fs::exists(fs::path("Data/SKSE/Plugins/SkyrimUnrealBridge.autoload"))) {
			return;
		}
		SKSE::GetTaskInterface()->AddTask([] {
			if (auto* mgr = RE::BGSSaveLoadManager::GetSingleton()) {
				mgr->LoadMostRecentSaveGame();
			}
		});
	}

	// Debug/alignment aid: if Data/SKSE/Plugins/SkyrimUnrealBridge.dump exists, write every loaded reference with a model
	// (position, rotation, scale, model path) around the player to <SKSE log dir>/SkyrimUnrealBridge_refs.tsv, then delete the flag.
	// Cumulative: appends refs not seen before to SkyrimUnrealBridge_refs_all.tsv whenever the player has moved >2500 units
	// since the last dump, and logs each dump position to SkyrimUnrealBridge_centers.txt (covered area). The flag file forces a dump.
	std::atomic<bool> g_dumpBroken{ false };

	// Writes every light the renderer currently has active (position, diffuse colour, radius, fade, LOD dimmer) to
	// SkyrimUnrealBridge_lights.tsv. This includes lights added by mods (e.g. light placers), unlike the form data.
	void DumpLightsImpl()
	{
		auto logDir = SKSE::log::log_directory();
		if (!logDir) {
			return;
		}
		auto&         state = RE::BSShaderManager::State::GetSingleton();
		std::ofstream out(*logDir / "SkyrimUnrealBridge_lights.tsv");
		out << "x\ty\tz\tr\tg\tb\tradius\tfade\tdimmer\tslot\n";
		int n = 0;
		for (int slot = 0; slot < 4; ++slot) {
			auto* ssn = state.shadowSceneNode[slot];
			if (!ssn) {
				out << "# slot " << slot << " is null\n";
				continue;
			}
			out << "# slot " << slot << " active lights: " << ssn->GetRuntimeData().activeLights.size() << "\n";
			for (auto& l : ssn->GetRuntimeData().activeLights) {
				if (!l || !l->light) {
					continue;
				}
				auto*       nl = l->light.get();
				const auto& d = nl->GetLightRuntimeData();
				const auto& t = nl->world.translate;
				out << t.x << '\t' << t.y << '\t' << t.z << '\t' << d.diffuse.red << '\t' << d.diffuse.green << '\t' << d.diffuse.blue
					<< '\t' << d.radius.x << '\t' << d.fade << '\t' << l->lodDimmer << '\t' << slot << '\n';
				++n;
			}
		}
		SKSE::log::info("SkyrimUnrealBridge: dumped {} lights", n);
	}

	bool GuardedCall(void (*fn)())
	{
		__try {
			fn();
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	// Plain-function trampoline (no C++ objects with destructors) so it can be wrapped in SEH below.
	void IterateImpl(RE::TES* tes, RE::TESObjectREFR* origin, float radius, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		tes->ForEachReferenceInRange(origin, radius, [=](RE::TESObjectREFR* ref) {
			thunk(ctx, ref);
			return RE::BSContainer::ForEachResult::kContinue;
		});
	}

	bool IterateGuarded(RE::TES* tes, RE::TESObjectREFR* origin, float radius, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		__try {
			IterateImpl(tes, origin, radius, ctx, thunk);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	template <class F>
	bool SafeIterate(RE::TES* tes, RE::TESObjectREFR* origin, float radius, F* f)
	{
		return IterateGuarded(tes, origin, radius, f, [](void* c, RE::TESObjectREFR* r) { (*static_cast<F*>(c))(r); });
	}

	void DumpRefs()
	{
		namespace fs = std::filesystem;
		// Opt-in: recording only happens when this flag file exists (or when a one-shot .dump flag is created).
		if (g_dumpBroken.load() ||
			(!fs::exists("Data/SKSE/Plugins/SkyrimUnrealBridge.autodump") && !fs::exists("Data/SKSE/Plugins/SkyrimUnrealBridge.dump"))) {
			return;
		}
		static bool                           init = false;
		static std::unordered_set<std::uint32_t> seen;
		static float                          lastX = 1e9f, lastY = 1e9f;
		auto*                                 player = RE::PlayerCharacter::GetSingleton();
		auto*                                 tes = RE::TES::GetSingleton();
		auto                                  logDir = SKSE::log::log_directory();
		if (!player || !tes || !logDir || !player->Is3DLoaded()) {
			return;
		}
		const fs::path flag = "Data/SKSE/Plugins/SkyrimUnrealBridge.dump";
		const bool     force = fs::exists(flag);
		if (force) {
			std::error_code ec;
			fs::remove(flag, ec);
		}
		const auto refsPath = *logDir / "SkyrimUnrealBridge_refs_all.tsv";
		if (!init) {
			init = true;
			std::ifstream in(refsPath);
			std::string   line;
			std::getline(in, line);
			while (std::getline(in, line)) {
				try { seen.insert(static_cast<std::uint32_t>(std::stoul(line.substr(0, line.find('\t')), nullptr, 16))); } catch (...) {}
			}
		}
		const auto pos = player->GetPosition();
		if (!force && std::hypot(pos.x - lastX, pos.y - lastY) < 2500.0f) {
			return;
		}
		lastX = pos.x;
		lastY = pos.y;
		const bool newFile = !fs::exists(refsPath);
		std::ofstream out(refsPath, std::ios::app);
		if (newFile) {
			out << "refid\tbaseid\ttype\tmodel\tx\ty\tz\trx\try\trz\tscale\tdisabled\tloaded3d\n";
		}
		std::ofstream(*logDir / "SkyrimUnrealBridge_centers.txt", std::ios::app) << pos.x << ' ' << pos.y << '\n';
		int n = 0;
		auto visit = [&](RE::TESObjectREFR* ref) {
			if (!ref || ref->IsPlayerRef() || seen.contains(ref->GetFormID())) {
				return;
			}
			auto* base = ref->GetBaseObject();
			auto* model = base ? base->As<RE::TESModel>() : nullptr;
			const char* path = model ? model->GetModel() : nullptr;
			if (!base || !path || !*path || ref->GetFormType() == RE::FormType::ActorCharacter) {
				return;
			}
			const auto p = ref->GetPosition();
			const auto a = ref->GetAngle();
			seen.insert(ref->GetFormID());
			out << std::hex << ref->GetFormID() << '\t' << base->GetFormID() << std::dec << '\t'
				<< static_cast<int>(base->GetFormType()) << '\t' << path << '\t' << p.x << '\t' << p.y << '\t' << p.z << '\t'
				<< a.x << '\t' << a.y << '\t' << a.z << '\t' << ref->GetScale() << '\t' << ref->IsDisabled() << '\t'
				<< (ref->Is3DLoaded() ? 1 : 0);
			if (auto* n3d = ref->Get3D(); n3d) {  // actual world rotation of the loaded 3D root (row-major 3x3), to validate rotation conventions
				const auto& m = n3d->world.rotate.entry;
				out << '\t' << m[0][0] << '\t' << m[0][1] << '\t' << m[0][2] << '\t' << m[1][0] << '\t' << m[1][1] << '\t' << m[1][2]
					<< '\t' << m[2][0] << '\t' << m[2][1] << '\t' << m[2][2];
				out << '\t' << n3d->worldBound.center.x << '\t' << n3d->worldBound.center.y << '\t' << n3d->worldBound.center.z
					<< '\t' << n3d->worldBound.radius << '\t' << n3d->world.translate.x << '\t' << n3d->world.translate.y
					<< '\t' << n3d->world.translate.z << '\t' << n3d->world.scale;   // bound sphere + 3D root world pos/scale
			}
			out << '\n';
			++n;
		};
		if (!SafeIterate(tes, player, 15000.0f, &visit)) {
			g_dumpBroken = true;  // the game's cell list hit a bad pointer: stop dumping for this session instead of crashing
			SKSE::log::error("SkyrimUnrealBridge: reference iteration faulted; dumping disabled for this session");
			return;
		}
		SKSE::log::info("SkyrimUnrealBridge: dumped {} references", n);
		if (!GuardedCall(&DumpLightsImpl)) {
			SKSE::log::error("SkyrimUnrealBridge: light dump faulted (skipped)");
		}
	}

	void AutoLoadRetryThread()   // separate thread so waiting for a save to load never blocks the live data stream
	{
		std::this_thread::sleep_for(std::chrono::seconds(12));  // let the main menu come up
		// Keep trying until a world is loaded (a main-menu pop-up can swallow the first call), but only ever call the loader while the
		// main menu is up and nothing is loading, and never twice within ~90 s: a second call during a load hangs the game.
		for (int attempt = 0; attempt < 6; ++attempt) {
			bool menuUp = false;
			{
				std::atomic<bool> done{ false };
				SKSE::GetTaskInterface()->AddTask([&] {
					if (auto* ui = RE::UI::GetSingleton()) {
						menuUp = ui->IsMenuOpen("Main Menu") && !ui->IsMenuOpen("Loading Menu");
					}
					done = true;
				});
				for (int i = 0; i < 100 && !done; ++i) std::this_thread::sleep_for(std::chrono::milliseconds(50));
			}
			if (menuUp) {
				AutoLoadLatestSave();
			}
			for (int i = 0; i < 90 && !(g_packet && g_packet->frame > 0); ++i) std::this_thread::sleep_for(std::chrono::seconds(1));
			if (g_packet && g_packet->frame > 0) {
				break;
			}
		}
	}

	// Remote control of the game's sky: Data/SKSE/Plugins/SkyrimUnrealBridge.sky holds lines like
	//   hour 8            set the game clock
	//   weather SkyrimClear   force a weather by editor id ("weather release" gives control back to the game)
	// The file is consumed (deleted) once read. Runs on the game thread.
	void ApplySkyCommands()
	{
		namespace fs = std::filesystem;
		const fs::path f = "Data/SKSE/Plugins/SkyrimUnrealBridge.sky";
		std::error_code ec;
		if (!fs::exists(f, ec)) {
			return;
		}
		std::vector<std::string> lines;
		{
			std::ifstream in(f);
			std::string l;
			while (std::getline(in, l)) lines.push_back(l);
		}
		fs::remove(f, ec);
		for (auto& l : lines) {
			char arg[128] = {};
			float v = 0;
			if (std::sscanf(l.c_str(), "hour %f", &v) == 1) {
				if (auto* cal = RE::Calendar::GetSingleton(); cal && cal->gameHour) {
					cal->gameHour->value = v;
					SKSE::log::info("SkyrimUnrealBridge: game hour set to {}", v);
				}
			} else if (std::sscanf(l.c_str(), "weather %127s", arg) == 1) {
				auto* sky = RE::Sky::GetSingleton();
				if (!sky) continue;
				if (std::string(arg) == "release") {
					sky->ReleaseWeatherOverride();
					SKSE::log::info("SkyrimUnrealBridge: weather override released");
					continue;
				}
				RE::TESWeather* found = nullptr;
				std::string report;
				if (std::string(arg).find_first_not_of("0123456789abcdefABCDEFxX") == std::string::npos) {   // hex form id
					found = RE::TESForm::LookupByID<RE::TESWeather>(static_cast<RE::FormID>(std::strtoul(arg, nullptr, 16)));
				}
				if (auto* dh = RE::TESDataHandler::GetSingleton()) {
					int n = 0;
					for (auto* w : dh->GetFormArray<RE::TESWeather>()) {
						if (!w) continue;
						const char* id = w->GetFormEditorID();
						if (!found && id && _stricmp(id, arg) == 0) found = w;
						if (n++ < 400) report += (id ? id : "?") + std::string(" ") + std::to_string(w->GetFormID()) + "\n";
					}
				}
				if (found) {
					sky->ForceWeather(found, true);
					report = std::string("forced weather ") + arg + " -> " + (found->GetFormEditorID() ? found->GetFormEditorID() : "?") + "\n" + report;
				} else {
					report = std::string("weather '") + arg + "' NOT FOUND; available:\n" + report;
				}
				std::ofstream("Data/SKSE/Plugins/SkyrimUnrealBridge.sky.out") << report;
			}
		}
	}

	void ScanWorld();   // defined below (live world stream)
	void ScanActors();  // defined below (actor pose stream)
	void ScanGear();    // defined below (worn armor, ~1 Hz)

	void PumpThread()
	{
		std::thread(AutoLoadRetryThread).detach();
		auto* tasks = SKSE::GetTaskInterface();
		while (g_run.load()) {
			static int tick = 0;
			++tick;
			tasks->AddTask([] { Sample(); });
			if (tick % 4 == 0) {  // ~30 Hz: actor skeleton poses
				tasks->AddTask([] { ScanActors(); });
			}
			if (tick % 125 == 60) {  // ~1 Hz: worn armor per actor
				tasks->AddTask([] { ScanGear(); ApplySkyCommands(); });
			}
			if (tick % 125 == 0) {  // ~every second: stream the live world (objects + lights) once the cell is stable
				tasks->AddTask([] {
					static int stableW = 0;
					auto* pl = RE::PlayerCharacter::GetSingleton();
					if (g_world) {   // status bits in header.pad: which of the stability conditions currently hold
						auto* hd = reinterpret_cast<SkyBridge::WorldHeader*>(g_world);
						hd->pad |= 0x20u;
						if (pl) hd->pad |= 0x40u;
						if (pl && pl->Is3DLoaded()) hd->pad |= 0x80u;
						if (pl && pl->GetParentCell()) hd->pad |= 0x100u;
						if (pl && pl->GetParentCell() && pl->GetParentCell()->IsAttached()) hd->pad |= 0x200u;
					}
					stableW = (pl && pl->Is3DLoaded() && pl->GetParentCell()) ? stableW + 1 : 0;   // (no IsAttached requirement)
					if (stableW >= 5) {
						ScanWorld();
					}
				});
			}
			if (tick % 250 == 0) {  // ~every 2 s, and only once the world has been stable for a while
				tasks->AddTask([] {
					static int stable = 0;
					auto* pl = RE::PlayerCharacter::GetSingleton();
					stable = (pl && pl->Is3DLoaded() && pl->GetParentCell() && pl->GetParentCell()->IsAttached()) ? stable + 1 : 0;
					if (stable >= 10) {  // ~20 s of a loaded, attached cell
						DumpRefs();
					}
				});
			}
			std::this_thread::sleep_for(std::chrono::milliseconds(8));
		}
	}

	// ---------------------------------------------------------------- live world stream
	struct WorldScratch
	{
		std::vector<SkyBridge::WRef>             refs;
		std::vector<SkyBridge::WLight>           lights;
		std::unordered_map<std::string, std::uint32_t> modelIndex;
		std::vector<std::string>                 models;
	};

	std::string NormalizeModel(const char* path)
	{
		std::string s(path);
		for (auto& c : s) {
			c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
			if (c == '\\') c = '/';
		}
		if (s.rfind("meshes/", 0) == 0) s = s.substr(7);
		return s;
	}

	// Editor/idle/lean/sit markers are invisible helpers; but several crafting stations are real meshes with "marker" in the name.
	bool IsHelperMarker(const std::string& m)
	{
		if (m.find("marker") == std::string::npos) {
			return false;
		}
		static const char* const kKeep[] = { "forge", "tanningrack", "smelter", "grindstone", "workbench", "anvil", "enchant", "alchemy", "cookingpot", "sharpening" };
		for (auto* k : kKeep) {
			if (m.find(k) != std::string::npos) {
				return false;
			}
		}
		return true;
	}

	void RotFromAngles(float rx, float ry, float rz, float out[9])
	{
		const double ax = -rx, ay = -ry, az = -rz;
		const double cx = std::cos(ax), sx = std::sin(ax), cy = std::cos(ay), sy = std::sin(ay), cz = std::cos(az), sz = std::sin(az);
		const double X[9] = { 1, 0, 0, 0, cx, -sx, 0, sx, cx };
		const double Y[9] = { cy, 0, sy, 0, 1, 0, -sy, 0, cy };
		const double Z[9] = { cz, -sz, 0, sz, cz, 0, 0, 0, 1 };
		double XY[9] = {}, R[9] = {};
		for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) for (int k = 0; k < 3; ++k) XY[i * 3 + j] += X[i * 3 + k] * Y[k * 3 + j];
		for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) for (int k = 0; k < 3; ++k) R[i * 3 + j] += XY[i * 3 + k] * Z[k * 3 + j];
		for (int i = 0; i < 9; ++i) out[i] = static_cast<float>(R[i]);
	}

	// Collects the lights the renderer currently has active (position, diffuse colour, radius, fade, LOD dimmer).
	void CollectLightsImpl(WorldScratch* s)
	{
		auto& state = RE::BSShaderManager::State::GetSingleton();
		auto* ssn = state.shadowSceneNode[0];
		if (!ssn) {
			return;
		}
		for (auto& l : ssn->GetRuntimeData().activeLights) {
			if (!l || !l->light || s->lights.size() >= SkyBridge::kMaxLights) {
				continue;
			}
			auto*       nl = l->light.get();
			const auto& d = nl->GetLightRuntimeData();
			const auto& t = nl->world.translate;
			SkyBridge::WLight wl{ { t.x, t.y, t.z }, { d.diffuse.red, d.diffuse.green, d.diffuse.blue }, d.radius.x, d.fade, l->lodDimmer };
			s->lights.push_back(wl);
		}
	}

	bool CollectLightsGuarded(WorldScratch* s)
	{
		__try {
			CollectLightsImpl(s);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	std::atomic<bool> g_worldBroken{ false };

	void IterateCellImpl(RE::TESObjectCELL* cell, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		cell->ForEachReference([=](RE::TESObjectREFR* r) {
			thunk(ctx, r);
			return RE::BSContainer::ForEachResult::kContinue;
		});
	}

	bool GridCellGuarded(RE::GridCellArray* grid, std::uint32_t x, std::uint32_t y, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		__try {
			auto* cell = grid->GetCell(x, y);
			if (!cell || !cell->IsAttached()) {
				return true;
			}
			IterateCellImpl(cell, ctx, thunk);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	bool InteriorCellGuarded(RE::TESObjectCELL* cell, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		__try {
			IterateCellImpl(cell, ctx, thunk);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	// Large references (worldspace RNAM: city walls, castles, towers) are attached through their own path and are not in the
	// grid cells' reference lists; persistent references live in the worldspace's persistent cell. Callers keep only loaded 3D.
	void WorldExtraRefsImpl(RE::TESWorldSpace* ws, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		for (auto& entry : ws->largeRefData.formIDCellMap) {
			if (auto* ref = RE::TESForm::LookupByID<RE::TESObjectREFR>(entry.first)) {
				thunk(ctx, ref);
			}
		}
		if (ws->persistentCell) {
			IterateCellImpl(ws->persistentCell, ctx, thunk);
		}
	}

	bool WorldExtraRefsGuarded(RE::TESWorldSpace* ws, void* ctx, void (*thunk)(void*, RE::TESObjectREFR*))
	{
		__try {
			WorldExtraRefsImpl(ws, ctx, thunk);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	// Runs on the game thread about once a second once the world is stable.
	void ScanWorld()
	{
		auto* player = RE::PlayerCharacter::GetSingleton();
		auto* tes = RE::TES::GetSingleton();
		if (g_world) {
			reinterpret_cast<SkyBridge::WorldHeader*>(g_world)->pad |= 0x10u;   // status bits (header.pad): 0x10 scan called
		}
		if (!g_world || g_worldBroken.load() || !player || !tes || !player->Is3DLoaded()) {
			return;
		}
		reinterpret_cast<SkyBridge::WorldHeader*>(g_world)->pad |= 0x1u;          // 0x1 passed preconditions
		static WorldScratch s;
		s.refs.clear(); s.lights.clear(); s.modelIndex.clear(); s.models.clear();
		static std::uint32_t visited = 0, errors = 0;
		static std::unordered_set<RE::FormID> seenIds;
		visited = 0;
		seenIds.clear();
		auto visit = [&](RE::TESObjectREFR* ref) {
		  ++visited;
		  try {
			if (!ref || ref->IsPlayerRef() || ref->IsDisabled() || s.refs.size() >= SkyBridge::kMaxRefs) {
				return;
			}
			if (!seenIds.insert(ref->GetFormID()).second) {
				return;
			}
			if (ref->GetFormType() == RE::FormType::ActorCharacter) {
				return;
			}
			auto* base = ref->GetBaseObject();
			auto* model = base ? base->As<RE::TESModel>() : nullptr;
			const char* path = model ? model->GetModel() : nullptr;
			if (!path || !*path) {
				return;
			}
			std::string m = NormalizeModel(path);
			if (m.size() < 5 || m.size() >= SkyBridge::kModelLen || IsHelperMarker(m) ||
				m.rfind("effects/", 0) == 0 || m.find("/fx") != std::string::npos || m.rfind("fx", 0) == 0) {
				return;
			}
			auto it = s.modelIndex.find(m);
			std::uint32_t mi;
			if (it == s.modelIndex.end()) {
				if (s.models.size() >= SkyBridge::kMaxModels) return;
				mi = static_cast<std::uint32_t>(s.models.size());
				s.modelIndex.emplace(m, mi);
				s.models.push_back(m);
			} else {
				mi = it->second;
			}
			SkyBridge::WRef r{};
			r.id = ref->GetFormID();
			r.model = mi;
			const auto p = ref->GetPosition();
			const auto a = ref->GetAngle();
			r.pos[0] = p.x; r.pos[1] = p.y; r.pos[2] = p.z;
			RotFromAngles(a.x, a.y, a.z, r.rot);
			r.scale = ref->GetScale();
			r.flags = ref->Is3DLoaded() ? 1u : 0u;
			s.refs.push_back(r);
		  } catch (...) { ++errors; }
		};
		// Walk the loaded cells one at a time. TES::ForEachReferenceInRange aborts the whole scan at the first bad cell pointer
		// (this mod list has one), so everything after it was lost; per-cell guards only skip the bad cell.
		auto thunk = [](void* c, RE::TESObjectREFR* r) { (*static_cast<decltype(visit)*>(c))(r); };
		int cellsOk = 0, cellsBad = 0;
		if (auto* interior = tes->interiorCell) {
			(InteriorCellGuarded(interior, &visit, thunk) ? cellsOk : cellsBad)++;
		} else if (auto* grid = tes->gridCells) {
			const std::uint32_t len = grid->length;
			for (std::uint32_t x = 0; x < len && x < 16; ++x) {
				for (std::uint32_t y = 0; y < len && y < 16; ++y) {
					(GridCellGuarded(grid, x, y, &visit, thunk) ? cellsOk : cellsBad)++;
				}
			}
			if (auto* ws = tes->worldSpace) {
				auto visitLoaded = [&](RE::TESObjectREFR* ref) {
					if (ref && ref->Is3DLoaded()) {
						visit(ref);
					}
				};
				auto thunkLoaded = [](void* c, RE::TESObjectREFR* r) { (*static_cast<decltype(visitLoaded)*>(c))(r); };
				if (!WorldExtraRefsGuarded(ws, &visitLoaded, thunkLoaded)) {
					reinterpret_cast<SkyBridge::WorldHeader*>(g_world)->pad |= 0x800u;   // 0x800: large/persistent refs faulted
				}
			}
		}
		if (cellsBad) {
			reinterpret_cast<SkyBridge::WorldHeader*>(g_world)->pad |= 0x400u;   // 0x400: some cells faulted (skipped)
		}
		if (cellsOk == 0) {
			reinterpret_cast<SkyBridge::WorldHeader*>(g_world)->pad |= 0x2u;     // 0x2: nothing could be iterated
			return;
		}
		CollectLightsGuarded(&s);

		auto* h = reinterpret_cast<SkyBridge::WorldHeader*>(g_world);
		h->seq++;  // odd: writing
		std::memset(g_world + SkyBridge::kWorldModelsOff, 0, std::size_t(SkyBridge::kMaxModels) * SkyBridge::kModelLen);
		for (std::size_t i = 0; i < s.models.size(); ++i) {
			std::memcpy(g_world + SkyBridge::kWorldModelsOff + i * SkyBridge::kModelLen, s.models[i].c_str(), s.models[i].size());
		}
		std::memcpy(g_world + SkyBridge::kWorldRefsOff, s.refs.data(), s.refs.size() * sizeof(SkyBridge::WRef));
		std::memcpy(g_world + SkyBridge::kWorldLightsOff, s.lights.data(), s.lights.size() * sizeof(SkyBridge::WLight));
		h->nRefs = static_cast<std::uint32_t>(s.refs.size());
		h->nModels = static_cast<std::uint32_t>(s.models.size());
		h->nLights = static_cast<std::uint32_t>(s.lights.size());
		h->tick++;
		h->seq++;  // even: stable
	}

	// ---------------------------------------------------------------- actor pose stream (see BridgeShared.h)
	std::uint8_t*                                     g_actors = nullptr;
	std::vector<std::string>                          g_boneNames;
	std::unordered_map<std::string, std::uint16_t>    g_boneIndex;

	int BoneNameIndex(const char* name)
	{
		auto it = g_boneIndex.find(name);
		if (it != g_boneIndex.end()) {
			return it->second;
		}
		if (g_boneNames.size() >= SkyBridge::kMaxBoneNames) {
			return -1;
		}
		const auto idx = static_cast<std::uint16_t>(g_boneNames.size());
		g_boneNames.emplace_back(name);
		g_boneIndex.emplace(name, idx);
		return idx;
	}

	void MatToQuat(const RE::NiMatrix3& m, float q[4])
	{
		const float m00 = m.entry[0][0], m01 = m.entry[0][1], m02 = m.entry[0][2];
		const float m10 = m.entry[1][0], m11 = m.entry[1][1], m12 = m.entry[1][2];
		const float m20 = m.entry[2][0], m21 = m.entry[2][1], m22 = m.entry[2][2];
		const float tr = m00 + m11 + m22;
		float x, y, z, w;
		if (tr > 0.0f) {
			const float s = std::sqrt(tr + 1.0f) * 2.0f;
			w = 0.25f * s; x = (m21 - m12) / s; y = (m02 - m20) / s; z = (m10 - m01) / s;
		} else if (m00 > m11 && m00 > m22) {
			const float s = std::sqrt(1.0f + m00 - m11 - m22) * 2.0f;
			w = (m21 - m12) / s; x = 0.25f * s; y = (m01 + m10) / s; z = (m02 + m20) / s;
		} else if (m11 > m22) {
			const float s = std::sqrt(1.0f + m11 - m00 - m22) * 2.0f;
			w = (m02 - m20) / s; x = (m01 + m10) / s; y = 0.25f * s; z = (m12 + m21) / s;
		} else {
			const float s = std::sqrt(1.0f + m22 - m00 - m11) * 2.0f;
			w = (m10 - m01) / s; x = (m02 + m20) / s; y = (m12 + m21) / s; z = 0.25f * s;
		}
		q[0] = x; q[1] = y; q[2] = z; q[3] = w;
	}

	// Depth-first over the named NiNodes of an actor's 3D tree (geometry skipped); parent index is the nearest listed ancestor.
	void CollectBones(RE::NiAVObject* o, int parent, SkyBridge::ActorPose* ap, int depth)
	{
		if (!o || depth > 64 || ap->nBones >= SkyBridge::kMaxBones) {
			return;
		}
		auto* n = o->AsNode();
		if (!n) {
			return;
		}
		int me = parent;
		const char* nm = n->name.c_str();
		// mod physics / weapon-mount helper nodes (CME, MOV, HDT, Weapon*, ...) do not drive the visible skeleton
		static const char* const kSkip[] = { "CME ", "MOV ", "HDT ", "Weapon", "Default ", "Ankle ", "Reverse ", "Extra", "Back ", "Quiver", "Shield" };
		bool skip = !nm || !*nm || std::strchr(nm, '(') != nullptr;
		for (auto* pre : kSkip) {
			if (!skip && std::strncmp(nm, pre, std::strlen(pre)) == 0) skip = true;
		}
		if (!skip) {
			const int idx = BoneNameIndex(nm);
			if (idx >= 0) {
				auto& b = ap->bones[ap->nBones];
				b.name = static_cast<std::uint16_t>(idx);
				b.parent = static_cast<std::int16_t>(parent);
				b.pos[0] = n->world.translate.x; b.pos[1] = n->world.translate.y; b.pos[2] = n->world.translate.z;
				MatToQuat(n->world.rotate, b.quat);
				me = static_cast<int>(ap->nBones++);
			}
		}
		for (auto& c : n->GetChildren()) {
			CollectBones(c.get(), me, ap, depth + 1);
		}
	}

	void FillActorImpl(RE::Actor* a, SkyBridge::ActorPose* ap)
	{
		std::memset(ap, 0, sizeof(*ap));
		ap->id = a->GetFormID();
		auto* base = a->GetActorBase();
		ap->baseId = base ? base->GetFormID() : 0;
		const bool female = base && base->GetSex() == RE::SEX::kFemale;
		ap->flags = (a->IsPlayerRef() ? SkyBridge::kActorIsPlayer : 0u) | (a->IsDead() ? SkyBridge::kActorDead : 0u) |
		            (female ? SkyBridge::kActorFemale : 0u) |
		            ((a->AsActorState() && a->AsActorState()->IsWeaponDrawn()) ? SkyBridge::kActorWeaponDrawn : 0u);
		const auto p = a->GetPosition();
		ap->pos[0] = p.x; ap->pos[1] = p.y; ap->pos[2] = p.z;
		ap->yaw = a->GetAngle().z;
		ap->scale = a->GetScale();
		if (auto* race = a->GetRace()) {
			const char* s = race->skeletonModels[female ? 1 : 0].GetModel();
			if (s && *s) {
				CopyStr(ap->skeleton, sizeof(ap->skeleton), NormalizeModel(s).c_str());
			}
		}
		CopyStr(ap->name, sizeof(ap->name), a->GetDisplayFullName());
		CollectBones(a->Get3D(), -1, ap, 0);
	}

	bool FillActorGuarded(RE::Actor* a, SkyBridge::ActorPose* ap)
	{
		__try {
			FillActorImpl(a, ap);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	void ActorListImpl(std::vector<RE::Actor*>* out)
	{
		if (auto* lists = RE::ProcessLists::GetSingleton()) {
			for (auto& h : lists->highActorHandles) {
				auto sp = h.get();
				if (sp && sp->Is3DLoaded() && out->size() < SkyBridge::kMaxActors) {
					out->push_back(sp.get());
				}
			}
		}
	}

	bool ActorListGuarded(std::vector<RE::Actor*>* out)
	{
		__try {
			ActorListImpl(out);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	// Runs on the game thread ~30 Hz. Actors are re-read every call, so pointers are only held within this call.
	void ScanActors()
	{
		auto* player = RE::PlayerCharacter::GetSingleton();
		if (!g_actors || !player || !player->Is3DLoaded()) {
			return;
		}
		static std::vector<RE::Actor*>                 list;
		static std::vector<SkyBridge::ActorPose>       poses(SkyBridge::kMaxActors);
		list.clear();
		list.push_back(player);
		ActorListGuarded(&list);
		std::uint32_t n = 0;
		std::unordered_set<RE::Actor*> seen;
		for (auto* a : list) {
			if (n >= SkyBridge::kMaxActors || !seen.insert(a).second) {
				continue;
			}
			if (FillActorGuarded(a, &poses[n]) && poses[n].nBones > 0) {
				++n;
			}
		}
		auto* h = reinterpret_cast<SkyBridge::ActorHeader*>(g_actors);
		h->seq++;  // odd: writing
		for (std::size_t i = 0; i < g_boneNames.size(); ++i) {
			CopyStr(reinterpret_cast<char*>(g_actors + SkyBridge::kActorNamesOff + i * SkyBridge::kBoneNameLen), SkyBridge::kBoneNameLen, g_boneNames[i].c_str());
		}
		std::memcpy(g_actors + SkyBridge::kActorPosesOff, poses.data(), std::size_t(n) * sizeof(SkyBridge::ActorPose));
		h->nBoneNames = static_cast<std::uint32_t>(g_boneNames.size());
		h->nActors = n;
		h->tick++;
		h->seq++;  // even: stable
	}

	// ---- worn gear (~1 Hz)
	std::uint8_t* g_gear = nullptr;

	void FillGearImpl(RE::Actor* a, SkyBridge::ActorGear* g)
	{
		std::memset(g, 0, sizeof(*g));
		g->id = a->GetFormID();
		auto* base = a->GetActorBase();
		g->baseId = base ? base->GetFormID() : 0;
		const bool female = base && base->GetSex() == RE::SEX::kFemale;
		g->flags = female ? SkyBridge::kActorFemale : 0u;
		g->faceId = (base && base->faceNPC) ? base->faceNPC->GetFormID() : g->baseId;
		// Creatures (wolves, dragons, draugr, ...): the body mesh is the "skin" armor of the actor (or its race); report its addons as gear
		if (auto* crace = a->GetRace()) {
			const char* sk = crace->skeletonModels[female ? 1 : 0].GetModel();
			const std::string skn = (sk && *sk) ? NormalizeModel(sk) : std::string();
			if (!skn.empty() && skn.rfind("actors/character/", 0) != 0) {
				g->creature = 1;                                            // creature flag
				RE::TESObjectARMO* skin = (base && base->skin) ? base->skin : crace->skin;
				if (skin) {
					for (auto* arma : skin->armorAddons) {
						if (!arma || !arma->IsValidRace(crace) || g->n >= SkyBridge::kMaxGear) continue;
						const char* mp = arma->bipedModels[female ? 1 : 0].GetModel();
						if (!mp || !*mp) continue;
						const std::string m = NormalizeModel(mp);
						if (m.size() >= SkyBridge::kGearPathLen) continue;
						std::string sw;
						const auto& tm = arma->bipedModels[female ? 1 : 0];
						for (std::uint32_t si = 0; tm.alternateTextures && si < tm.numAlternateTextures; ++si) {
							const auto& at = tm.alternateTextures[si];
							const char* tp = at.textureSet ? at.textureSet->GetTexturePath(RE::BSTextureSet::Texture::kDiffuse) : nullptr;
							if (at.name3D.c_str() && *at.name3D.c_str() && tp && *tp) {
								if (!sw.empty()) sw += ';';
								sw += at.name3D.c_str(); sw += '='; sw += NormalizeModel(tp);
							}
						}
						CopyStr(g->swaps[g->n], SkyBridge::kGearSwapLen, sw.c_str());
						CopyStr(g->paths[g->n++], SkyBridge::kGearPathLen, m.c_str());
					}
				}
			}
		}
		for (int hand = 0; hand < 2; ++hand) {                 // equipped weapon / shield (0 = right, 1 = left)
			auto* eq = a->GetEquippedObject(hand == 1);
			if (!eq) continue;
			const char* mp = nullptr;
			if (auto* w = eq->As<RE::TESObjectWEAP>()) {
				mp = w->GetModel();
			} else if (auto* s = eq->As<RE::TESObjectARMO>()) {   // shield
				for (auto* arma : s->armorAddons) {
					if (arma && (!a->GetRace() || arma->IsValidRace(a->GetRace()))) { mp = arma->bipedModels[female ? 1 : 0].GetModel(); break; }
				}
				if (mp && *mp) g->weaponFlags |= 4u;
			}
			if (mp && *mp) {
				const std::string m = NormalizeModel(mp);
				if (m.size() < SkyBridge::kGearPathLen) {
					CopyStr(g->weapons[hand], SkyBridge::kGearPathLen, m.c_str());
					g->weaponFlags |= (1u << hand);
				}
			}
		}
		auto* changes = a->GetInventoryChanges();
		auto* race = a->GetRace();
		if (!changes || !changes->entryList) {
			return;
		}
		for (auto* e : *changes->entryList) {
			if (!e || !e->object || !e->IsWorn()) {
				continue;
			}
			auto* armo = e->object->As<RE::TESObjectARMO>();
			if (!armo) {
				continue;
			}
			g->wornSlots |= static_cast<std::uint32_t>(armo->GetSlotMask());
			for (auto* arma : armo->armorAddons) {
				if (!arma || (race && !arma->IsValidRace(race)) || g->n >= SkyBridge::kMaxGear) {
					continue;
				}
				const char* mp = arma->bipedModels[female ? 1 : 0].GetModel();
				if (!mp || !*mp) {
					continue;
				}
				const std::string m = NormalizeModel(mp);
				if (m.size() < SkyBridge::kGearPathLen) {
					std::string sw;                               // texture overrides on this addon (e.g. Whiterun vs Riften guard colours)
					const auto& tm = arma->bipedModels[female ? 1 : 0];
					for (std::uint32_t si = 0; tm.alternateTextures && si < tm.numAlternateTextures; ++si) {
						const auto& at = tm.alternateTextures[si];
						const char* tp = at.textureSet ? at.textureSet->GetTexturePath(RE::BSTextureSet::Texture::kDiffuse) : nullptr;
						if (at.name3D.c_str() && *at.name3D.c_str() && tp && *tp) {
							if (!sw.empty()) sw += ';';
							sw += at.name3D.c_str(); sw += '='; sw += NormalizeModel(tp);
						}
					}
					CopyStr(g->swaps[g->n], SkyBridge::kGearSwapLen, sw.c_str());
					CopyStr(g->paths[g->n++], SkyBridge::kGearPathLen, m.c_str());
				}
			}
		}
	}

	bool FillGearGuarded(RE::Actor* a, SkyBridge::ActorGear* g)
	{
		__try {
			FillGearImpl(a, g);
			return true;
		} __except (EXCEPTION_EXECUTE_HANDLER) {
			return false;
		}
	}

	void ScanGear()
	{
		auto* player = RE::PlayerCharacter::GetSingleton();
		if (!g_gear || !player || !player->Is3DLoaded()) {
			return;
		}
		static std::vector<RE::Actor*>             list;
		static std::vector<SkyBridge::ActorGear>   gear(SkyBridge::kMaxActors);
		list.clear();
		list.push_back(player);
		ActorListGuarded(&list);
		std::uint32_t n = 0;
		std::unordered_set<RE::Actor*> seen;
		for (auto* a : list) {
			if (n >= SkyBridge::kMaxActors || !seen.insert(a).second) {
				continue;
			}
			if (FillGearGuarded(a, &gear[n])) {
				++n;
			}
		}
		auto* h = reinterpret_cast<SkyBridge::GearHeader*>(g_gear);
		h->seq++;
		std::memcpy(g_gear + sizeof(SkyBridge::GearHeader), gear.data(), std::size_t(n) * sizeof(SkyBridge::ActorGear));
		h->nActors = n;
		h->tick++;
		h->seq++;
	}

	bool OpenGearMapping()
	{
		HANDLE h = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE, 0, static_cast<DWORD>(SkyBridge::kGearSize), SkyBridge::kGearName);
		if (!h) {
			return false;
		}
		g_gear = static_cast<std::uint8_t*>(MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, SkyBridge::kGearSize));
		if (!g_gear) {
			return false;
		}
		std::memset(g_gear, 0, SkyBridge::kGearSize);
		auto* hd = reinterpret_cast<SkyBridge::GearHeader*>(g_gear);
		hd->magic = SkyBridge::kGearMagic;
		hd->version = 1;
		return true;
	}

	bool OpenActorsMapping()
	{
		HANDLE h = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE, 0, static_cast<DWORD>(SkyBridge::kActorsSize), SkyBridge::kActorsName);
		if (!h) {
			return false;
		}
		g_actors = static_cast<std::uint8_t*>(MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, SkyBridge::kActorsSize));
		if (!g_actors) {
			return false;
		}
		std::memset(g_actors, 0, SkyBridge::kActorsSize);
		auto* hd = reinterpret_cast<SkyBridge::ActorHeader*>(g_actors);
		hd->magic = SkyBridge::kActorsMagic;
		hd->version = 1;
		return true;
	}

	bool OpenWorldMapping()
	{
		HANDLE h = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE, 0, static_cast<DWORD>(SkyBridge::kWorldSize), SkyBridge::kWorldName);
		if (!h) {
			return false;
		}
		g_world = static_cast<std::uint8_t*>(MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, SkyBridge::kWorldSize));
		if (!g_world) {
			return false;
		}
		std::memset(g_world, 0, SkyBridge::kWorldSize);
		auto* hd = reinterpret_cast<SkyBridge::WorldHeader*>(g_world);
		hd->magic = SkyBridge::kWorldMagic;
		hd->version = 1;
		return true;
	}

	bool OpenMapping()
	{
		OpenWorldMapping();
		OpenActorsMapping();
		OpenGearMapping();
		HANDLE h = CreateFileMappingW(INVALID_HANDLE_VALUE, nullptr, PAGE_READWRITE, 0,
			sizeof(SkyBridge::Packet), SkyBridge::kMappingName);
		if (!h) {
			return false;
		}
		g_packet = static_cast<SkyBridge::Packet*>(
			MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(SkyBridge::Packet)));
		if (!g_packet) {
			return false;
		}
		std::memset(g_packet, 0, sizeof(SkyBridge::Packet));
		g_packet->magic = SkyBridge::kMagic;
		g_packet->version = SkyBridge::kVersion;
		return true;
	}
}

SKSEPluginLoad(const SKSE::LoadInterface* a_skse)
{
	SKSE::Init(a_skse);
	if (!OpenMapping()) {
		SKSE::log::error("SkyrimUnrealBridge: failed to create shared memory");
		return true;
	}
	SKSE::log::info("SkyrimUnrealBridge: shared memory ready, packet size {}", sizeof(SkyBridge::Packet));
	SKSE::GetMessagingInterface()->RegisterListener([](SKSE::MessagingInterface::Message* m) {
		if (m->type == SKSE::MessagingInterface::kDataLoaded) {
			std::thread(PumpThread).detach();
			SKSE::log::info("SkyrimUnrealBridge: streaming started");
		}
	});
	return true;
}

// build variant 1 2026-10-27T14:15:04.7369776-07:00

// rebuild 1
