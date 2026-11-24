## Purpose
Configures Unreal Engine editor performance settings, including CPU throttling when the editor is not in focus and performance monitoring.

## How it is run
Loaded automatically by the Unreal Engine editor at startup. Referenced in HANDOFF_FOR_CURSOR.md as part of editor configuration. Not executed via command line.

## Inputs
`unreal/SkyBridge/Config/DefaultEditorSettings.ini` file contents.

## Outputs
Editor performance settings applied in memory; no physical output files.

## Key functions
Throttle CPU
Monitor Perf

## Depends on
None

## Gotchas
- CPU throttling disabled by default (`bThrottleCPUWhenNotForeground=False`), potentially causing high CPU usage when editor is not active.
- Performance monitoring disabled by default (`bMonitorEditorPerformance=False`), so editor performance metrics are not tracked.

Source: read, not executed.
