import unreal
cls = unreal.PoseableMeshComponent
print([n for n in dir(cls) if any(k in n for k in ("refresh", "dirty", "tick", "update", "finalize", "force"))])
a = unreal.Actor
print([n for n in dir(a) if "tick" in n])
