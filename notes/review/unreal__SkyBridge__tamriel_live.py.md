# Review leads for unreal/SkyBridge/tamriel_live.py (UNVERIFIED)
L298 | memory | self.built dict never cleared | As the player travels, more actors are built and stored, causing memory to grow without bound | self.built[key] = a | high
L320 | performance | update_visibility loops over self.built (growing) | Visibility updates become slower over time as more models are built | self.built.items() | high
L410 | performance | Reading terrain_ready.txt every tick | Disk I/O per tick (every frame) is heavy | open(os.path.join(TAM, "terrain_ready.txt")) | high
L76 | robustness | Swallowing exceptions when setting import options | Makes it hard to debug import failures | except Exception: | medium
