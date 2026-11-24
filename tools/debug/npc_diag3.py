import sys, math, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
U = 1.4287
stream = {a["id"]: a for a in (npc_live.read_actors() or [])}
for aid, e in list(npc_live._state["actors"].items())[:4]:
    a = stream.get(aid)
    if not a:
        continue
    comp = e["comp"]
    errs = []
    for raw in ("NPC L Hand [LHnd]", "NPC R Hand [RHnd]", "NPC L Foot [Lft ]", "NPC R Foot [Rft ]", "NPC Head [Head]", "NPC L Forearm [LLar]", "NPC R Calf [RClf]"):
        if raw not in a["bones"]:
            continue
        p = a["bones"][raw][0]
        want = unreal.Vector(p[1] * U, p[0] * U, p[2] * U)                       # Skyrim world -> UE world, same mapping as statics
        got = comp.get_bone_location_by_name(npc_live.ue_bone(raw), unreal.BoneSpaces.WORLD_SPACE)
        err = math.dist((want.x, want.y, want.z), (got.x, got.y, got.z))
        errs.append((raw.split(" [")[0], round(err, 1)))
    print(e["actor"].get_actor_label(), "world-position error (cm) of bones vs Skyrim:", errs)
