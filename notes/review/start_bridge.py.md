# Review leads for start_bridge.py (UNVERIFIED)
L29 | correctness | Shared memory atomicity risk | Bridge reads 16-byte block without ensuring atomicity, risking partial updates during plugin writes | Plugin should use sequence number to verify consistency or bridge should retry | medium
L150 | robustness | Excessive UE execution lock timeout | 600-second lock wait timeout is unreasonable for typical usage (minutes) | Reduce to 30 seconds max | medium
L475 | robustness | Unnecessarily long frame wait | 360-second (6-minute) wait for frame data exceeds practical startup times | Reduce to 60 seconds | medium
L355 | performance | Inefficient INI file read | `set_ini` reads entire file into memory for line-by-line processing (small files only) | Not problematic for current file sizes | low
L168 | performance | Busy-wait in UE execution | 0.3-second sleep in `_ue_exec_locked` loop is inefficient for file check | Use event-based waiting (e.g., `wait_for_file_change`) | low
