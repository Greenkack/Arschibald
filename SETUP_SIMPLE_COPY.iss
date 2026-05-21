; Ömers All in One DingsBums - EINFACHES Setup (Kopiert dist-Ordner direkt)

#define MyAppName "Ömers All in One DingsBums"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ömers Company"
#define MyAppExeName "Ömers All in One Dingsbums.exe"

[Setup]
AppId={{OEMERS-ALL-IN-ONE-DINGSBUMS-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=setup_output
OutputBaseFilename=Oemers_All_in_One_DingsBums_Setup
SetupIconFile=data\company_logos\app_icon.ico

; === KEINE KOMPRESSION - ROHE KOPIE ===
Compression=none
SolidCompression=no

; Disk Spanning falls zu groß
DiskSpanning=yes
DiskSliceSize=max

; Keine Speicherplatzprüfung (wir wissen es ist groß)
ExtraDiskSpaceRequired=3000000000

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Kopiere den gesamten dist-Ordner rekursiv (mit externem flag für lange Pfade)
Source: "dist\Ömers All in One Dingsbums\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs external

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

