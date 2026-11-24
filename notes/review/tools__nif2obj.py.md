# Review leads for tools/nif2obj.py (UNVERIFIED)
L78 | bug | Swallowed exception in fallback | Causes silent failure when npc_skin is missing, leading to empty models without error | Raise specific exceptions or log error instead of returning empty | medium
L190 | bug | Texture name replacement breaks file references | Replaces dots with underscores, so MTL will look for "texture_png" but the texture is "texture.png" | Remove the dot replacement in material name processing | high
