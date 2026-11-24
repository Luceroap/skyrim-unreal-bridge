using UnrealBuildTool;
public class SkyBridgeEditorTarget : TargetRules
{
	public SkyBridgeEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("SkyBridge");
	}
}
