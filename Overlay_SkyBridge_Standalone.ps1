# Put the packaged SkyBridge window over Skyrim without stealing Skyrim input focus.
$ErrorActionPreference = 'SilentlyContinue'

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class SkyBridgeOverlay {
    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr p);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr h, int i);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr h, int i, int v);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int w, int hh, uint f);
    [DllImport("user32.dll")] public static extern bool SetLayeredWindowAttributes(IntPtr h, uint key, byte a, uint f);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
}
"@

$skyPid = (Get-Process SkyrimSE -ErrorAction SilentlyContinue | Select-Object -First 1).Id
$bridgePids = @(Get-Process SkyBridge -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
if (-not $skyPid -or $bridgePids.Count -eq 0) { exit 0 }

$handles = [Collections.Generic.List[IntPtr]]::new()
$callback = [SkyBridgeOverlay+EnumProc]{ param($h, $unused)
    [uint32]$pid = 0
    [SkyBridgeOverlay]::GetWindowThreadProcessId($h, [ref]$pid) | Out-Null
    if ($bridgePids -contains [int]$pid -and [SkyBridgeOverlay]::IsWindowVisible($h)) { $handles.Add($h) }
    return $true
}

$skyHandle = [IntPtr]::Zero
$skyCallback = [SkyBridgeOverlay+EnumProc]{ param($h, $unused)
    [uint32]$pid = 0
    [SkyBridgeOverlay]::GetWindowThreadProcessId($h, [ref]$pid) | Out-Null
    if ([int]$pid -eq $skyPid -and [SkyBridgeOverlay]::IsWindowVisible($h)) { $script:skyHandle = $h; return $false }
    return $true
}

for ($try = 0; $try -lt 30 -and $handles.Count -eq 0; $try++) {
    [SkyBridgeOverlay]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
    if ($handles.Count -eq 0) { Start-Sleep -Milliseconds 500 }
}
[SkyBridgeOverlay]::EnumWindows($skyCallback, [IntPtr]::Zero) | Out-Null
if ($handles.Count -eq 0 -or $skyHandle -eq [IntPtr]::Zero) { exit 0 }

$r = New-Object SkyBridgeOverlay+RECT
[SkyBridgeOverlay]::GetWindowRect($skyHandle, [ref]$r) | Out-Null
$bridge = $handles[0]
$style = [SkyBridgeOverlay]::GetWindowLong($bridge, -16)
[SkyBridgeOverlay]::SetWindowLong($bridge, -16, ($style -band (-bnot 0x00C00000) -band (-bnot 0x00040000))) | Out-Null
$ex = [SkyBridgeOverlay]::GetWindowLong($bridge, -20)
[SkyBridgeOverlay]::SetWindowLong($bridge, -20, ($ex -bor 0x00080000 -bor 0x00000020 -bor 0x00000080 -bor 0x08000000)) | Out-Null
[SkyBridgeOverlay]::SetLayeredWindowAttributes($bridge, 0, 255, 2) | Out-Null
[SkyBridgeOverlay]::SetWindowPos($bridge, [IntPtr](-1), $r.L, $r.T, ($r.R - $r.L), ($r.B - $r.T), 0x0070) | Out-Null
[SkyBridgeOverlay]::SetForegroundWindow($skyHandle) | Out-Null
