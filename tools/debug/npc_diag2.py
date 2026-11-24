import sys, math, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
acts = npc_live._state["actors"]
print("npc actors:", len(acts), " module file time check; stream now:", len(npc_live.read_actors() or []))
for aid, e in acts.items():
    comp = e["comp"]
    worst = 0.0; n = 0
    if e["ready"]:
        for raw in ("NPC L UpperArm [LUar]", "NPC R UpperArm [RUar]", "NPC L Forearm [LLar]", "NPC L Thigh [LThg]"):
            u = npc_live.ue_bone(raw)
            if u not in e["rest0"]:
                continue
            t = comp.get_bone_transform_by_name(u, unreal.BoneSpaces.COMPONENT_SPACE)
            q = t.rotation
            R0 = e["rest0"][u][0]
            Rrel = npc_live.mul(npc_live.quat_to_mat(q.x, q.y, q.z, q.w), npc_live.tr(R0))
            ang = math.degrees(math.acos(max(-1, min(1, (Rrel[0] + Rrel[4] + Rrel[8] - 1) / 2))))
            worst = max(worst, ang); n += 1
    print("%-28s ready=%s bones=%d  max arm/leg rotation from rest = %.1f deg" % (e["actor"].get_actor_label(), e["ready"], comp.get_num_bones(), worst))
