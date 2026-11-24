## Purpose
Configures input axes mappings for controllers, mouse, and touch devices in Unreal Engine. Sets dead zones, sensitivity, and inversion parameters to ensure responsive gameplay across supported hardware.

## How it is run
Loaded automatically by Unreal Engine's `InputSettings` subsystem at startup. No other files in the project reference this file (git grep for "DefaultInput.ini" returned no results).

## Inputs
Hardware input axes (e.g., `Gamepad_LeftX`, `MouseX`, `Vive_Left_Trackpad_X`) with associated parameters like DeadZone, Sensitivity, and Exponent.

## Outputs
No files or folders are written. The configuration is used directly by Unreal Engine's input system during runtime for axis handling.

## Key functions
- DeadZone
- Sensitivity
- Exponent
- bInvert
- AxisConfig
- InputSettings
- MouseSensitivity
- GamepadDeadZone
- TouchAxisMapping
- InputAxisName
- InputAxisProperties
- VRInputSupport
- MotionControlsEnabled
- LegacyInputScale
- EnhancedInputCompatibility

## Depends on
Unreal Engine's `InputSettings` class (no other project files depend on this config).

## Gotchas
- Legacy `-AxisConfig` entries (deleted) may conflict with newer `+AxisConfig` entries if modified incorrectly.
- Mouse sensitivity values (0.07) are unusually low compared to standard configurations.
- VR-specific mappings (e.g., `Vive_`, `OculusTouch_`) are included but unused in non-VR builds.

Source: read, not executed.
