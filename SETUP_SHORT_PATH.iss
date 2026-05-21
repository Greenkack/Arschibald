; OemersBokuk4all - VOLLSTÄNDIGES Setup

#define MyAppName "OemersBokuk4all"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Oemers Company"
#define MyAppExeName "OemersBokuk4all.exe"

[Setup]
AppId={{OEMERS-BOKUK4ALL-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Bokuk4all
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=setup_output
OutputBaseFilename=OemersBokuk4all_Setup
SetupIconFile=data\company_logos\app_icon.ico

; === KEINE KOMPRESSION - VOLLE GRÖSSE ===
Compression=none
SolidCompression=no

; KEINE Aufteilung - alles in EINER .EXE Datei
DiskSpanning=no

; Keine Speicherplatzprüfung 
ExtraDiskSpaceRequired=3000000000

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Kopiere ALLES aus dem kurzen App-Ordner
Source: "dist\OemersBokuk4all\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Launcher BAT für korrektes Working Directory
Source: "OemersBokuk4all_Launcher.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "cmd.exe"; Parameters: "/k ""{app}\OemersBokuk4all_Launcher.bat"""; IconFilename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "cmd.exe"; Parameters: "/k ""{app}\OemersBokuk4all_Launcher.bat"""; IconFilename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "cmd.exe"; Parameters: "/k ""{app}\OemersBokuk4all_Launcher.bat"""; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

