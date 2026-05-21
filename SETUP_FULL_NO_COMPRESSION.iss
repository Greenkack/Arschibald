; Ömers All in One DingsBums - VOLLSTÄNDIGES Setup (KEINE KOMPRESSION)
; Installiert den kompletten 2.7 GB Build ohne Verkleinerung

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
OutputBaseFilename=Oemers_All_in_One_DingsBums_FULL_Setup
SetupIconFile=data\company_logos\app_icon.ico

; === KEINE KOMPRESSION - VOLLE GRÖSSE ===
Compression=none
SolidCompression=no
InternalCompressLevel=none

; Rechte
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Erscheinungsbild
WizardStyle=modern
DisableWelcomePage=no

; Platzanforderungen - 3 GB für sicheren Install
DiskSpanning=no
ExtraDiskSpaceRequired=3000000000

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
german.WelcomeLabel1=Willkommen zum [name] Setup
german.WelcomeLabel2=Dieses Setup installiert die vollständige "Ömers All in One DingsBums" Anwendung.%n%nDie Installation enthält:%n• Alle Python-Module und Dependencies%n• Streamlit Framework%n• PDF-System mit allen Templates%n• CRM-System%n• 3D-Visualisierung%n• Datenbanken und Assets%n%nINSTALLATIONSGRÖSSE: ~2.7 GB%nSETUP-GRÖSSE: ~2.7 GB (unkomprimiert)%n%nKlicken Sie auf Weiter zum Fortfahren.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; === KOMPLETTER PYINSTALLER BUILD (2.7 GB) ===
; Enthält ALLES: Python, Libraries, Module, Assets, Daten
Source: "dist\Ömers All in One Dingsbums\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\customer_documents"; Permissions: users-full
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Kein spezieller Code nötig - Setup prüft automatisch Speicherplatz

[UninstallDelete]
Type: filesandordirs; Name: "{app}\customer_documents"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"
