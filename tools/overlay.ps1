# Turns the Unreal window into a borderless, click-through, ~50% transparent overlay exactly over Skyrim's window.
# Skyrim must be in borderless/windowed mode. To undo, close Unreal and start it again (see start_bridge.ps1).
# Opacity: change 130 below (0-255).
Add-Type @"
using System; using System.Runtime.InteropServices;
public class OV {
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr h,int i);
 [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr h,int i,int v);
 [DllImport("user32.dll")] public static extern bool SetLayeredWindowAttributes(IntPtr h,uint key,byte a,uint f);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h,IntPtr a,int x,int y,int w,int hh,uint f);
}
"@
$sky = (Get-Process SkyrimSE).MainWindowHandle; $ue = (Get-Process UnrealEditor).MainWindowHandle
$r = New-Object OV+RECT; [OV]::GetWindowRect($sky, [ref]$r) | Out-Null
$st = [OV]::GetWindowLong($ue, -16); [OV]::SetWindowLong($ue, -16, ($st -band (-bnot 0x00C00000) -band (-bnot 0x00040000))) | Out-Null
$ex = [OV]::GetWindowLong($ue, -20); [OV]::SetWindowLong($ue, -20, ($ex -bor 0x80000 -bor 0x20 -bor 0x80 -bor 0x08000000)) | Out-Null
[OV]::SetLayeredWindowAttributes($ue, 0, 130, 2) | Out-Null
[OV]::SetWindowPos($ue, [IntPtr](-1), $r.L, $r.T, ($r.R - $r.L), ($r.B - $r.T), 0x0070) | Out-Null   # 0x0010 = SWP_NOACTIVATE: never steal focus (Skyrim pauses when it loses focus)
[OV]::SetForegroundWindow($sky) | Out-Null

