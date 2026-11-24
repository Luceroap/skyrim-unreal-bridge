import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Carlotta" in e["actor"].get_actor_label())
c = e["comp"]
if not hasattr(nl, "_orig_apply"):
    nl._orig_apply = nl._apply_pose
    def _skip(entry, *a, **k):
        if getattr(nl, "_skip_entry", None) is entry:
            return
        return nl._orig_apply(entry, *a, **k)
    nl._apply_pose = _skip
nl._skip_entry = e
# reference component-space transforms by composing ref locals
cs = {}
names, tfs = [], []
for i in range(c.get_num_bones()):
    n = str(c.get_bone_name(i))
    loc = c.get_ref_pose_transform(i)
    p = str(c.get_parent_bone(n))
    t = loc if p not in cs else unreal.MathLibrary.compose_transforms(loc, cs[p])
    cs[n] = t
    names.append(n); tfs.append(t)
print("set", unreal.SkyBridgeViewLibrary.apply_pose(c, names, tfs))
t = c.get_socket_transform("NPC-L-Hand-_LHnd_", unreal.RelativeTransformSpace.RTS_COMPONENT)
print("hand", t.translation, t.scale3d)
