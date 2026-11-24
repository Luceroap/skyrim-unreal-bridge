# Review leads for shared/BridgeShared.h (UNVERIFIED)
L59 | robustness | Hard-coded max path length 128 for model paths (kModelLen) | Truncation of long mod paths may cause missing models or incorrect rendering | Increase kModelLen to 256 | high
L92 | bug | kMaxActors = 96 for actor pose stream | Exceeding 96 actors causes omission, leading to missing actors in Unreal | Increase kMaxActors to 256 | high
L92 | robustness | Hard-coded max path length 96 for skeleton paths (kSkelLen) | Truncation of long skeleton paths (e.g., for custom races) may cause skeleton loading failure | Increase kSkelLen to 256 | high
L129 | robustness | Hard-coded max path length 112 for gear paths (kGearPathLen) | Truncation of long armor/weapon paths may cause missing or incorrect gear (e.g., in high-quality armor mods) | Increase kGearPathLen to 256 | high
