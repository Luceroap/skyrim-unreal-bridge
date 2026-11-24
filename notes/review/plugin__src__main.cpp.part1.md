# Review leads for plugin/src/main.cpp.part1 (UNVERIFIED)
L678 | perf | Repeated model path normalization | Normalization done per reference without caching, causing redundant string processing | Cache normalized paths in a map | medium
L310 | perf | Initial reference dump file read | Reading large reference dump file during first dump causes noticeable stutter | Store seen set in binary format for faster loading | low
