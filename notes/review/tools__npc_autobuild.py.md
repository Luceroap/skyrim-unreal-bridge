# Review leads for tools/npc_autobuild.py (UNVERIFIED)
L5 | bug | hard-coded path | breaks if project moved or user has different username | use config file or environment variable | high
L15 | bug | magic number 3 | unclear meaning, risks future changes breaking logic | define constant (e.g., ACTOR_BATCH_SIZE = 3) | medium
