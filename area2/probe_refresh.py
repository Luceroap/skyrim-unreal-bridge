import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
W = c.get_world_transform()
un = nl.ue_bone("NPC L Hand [LHnd]")
CS = unreal.BoneSpaces.COMPONENT_SPACE


def chk(tag):
    s = c.get_world_transform().inverse_transform_location(c.get_socket_location(un))
    g = c.get_bone_transform_by_name(un, CS).translation
    print("%-28s render (%.1f %.1f %.1f) set (%.1f %.1f %.1f)" % (tag, s.x, s.y, s.z, g.x, g.y, g.z))


chk("before")
mesh = c.get_skinned_asset()
try:
    c.set_skinned_asset_and_update(mesh, False); chk("set_skinned_asset_and_update")
except Exception as ex:
    print("a", ex)
try:
    c.set_forced_lod(1); c.set_forced_lod(0); chk("forced lod toggle")
except Exception as ex:
    print("b", ex)
try:
    c.set_component_tick_enabled(True); c.set_tickable_when_paused(True); chk("tick flags")
except Exception as ex:
    print("c", ex)
try:
    c.set_editor_property("use_screen_render_state_for_update", False)
    c.set_editor_property("visibility_based_anim_tick_option", unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    chk("vis tick option")
except Exception as ex:
    print("d", ex)
