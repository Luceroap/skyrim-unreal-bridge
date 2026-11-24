import sys
nl = sys.modules["npc_live"]
for e in list(nl._state["actors"].values())[:5]:
    c = e["comp"]
    a = e["actor"]
    o, ext = a.get_actor_bounds(False)
    h = c.get_socket_location(nl.ue_bone("NPC Head [Head]"))
    print(a.get_actor_label()[:24], "vis", c.is_visible(), "hidden", a.is_hidden_ed(), "loc", a.get_actor_location(), "scale", a.get_actor_scale3d(),
          "bounds", o, ext, "head", h, "mesh", c.get_skinned_asset().get_name() if c.get_skinned_asset() else None)
