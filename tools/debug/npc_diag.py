import sys, math, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
acts = npc_live._state["actors"]
print("npc actors:", len(acts))
for aid, e in list(acts.items())[:2]:
    comp = e["comp"]
    print("==", e["actor"].get_actor_label())
    for raw in ("NPC L UpperArm [LUar]", "NPC L Forearm [LLar]", "NPC R Thigh [RThg]", "NPC L Hand [LHnd]"):
        u = npc_live.ue_bone(raw)
        t = comp.get_bone_transform_by_name(u, unreal.BoneSpaces.COMPONENT_SPACE)
        R0, t0 = e["rest0"][u]
        q = t.rotation
        Rn = npc_live.quat_to_mat(q.x, q.y, q.z, q.w)
        Rrel = npc_live.mul(Rn, npc_live.tr(R0))
        ang = math.degrees(math.acos(max(-1, min(1, (Rrel[0] + Rrel[4] + Rrel[8] - 1) / 2))))
        print("  %-28s moved %.1f cm, rotated %.1f deg from rest" % (u, math.dist((t.translation.x, t.translation.y, t.translation.z), t0), ang))
