; Ömers All in One DingsBums - Vollständiges Setup-Script
; Installiert ALLES: Python, Streamlit, Dependencies, App-Dateien
; Eine Setup.exe für komplette Installation

#define MyAppName "Ömers All in One DingsBums"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ömers Company"
#define MyAppExeName "Ömers All in One DingsBums.exe"
#define MyAppURL "https://www.example.com"

[Setup]
; App-Informationen
AppId={{OEMERS-ALL-IN-ONE-DINGSBUMS-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=setup_output
OutputBaseFilename=Oemers_All_in_One_DingsBums_Complete_Setup
SetupIconFile=data\company_logos\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; Rechte
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Erscheinungsbild
WizardStyle=modern
DisableWelcomePage=no

; Platzanforderungen
DiskSpanning=no
; Großzügiger Platz für Python + alle Dependencies
ExtraDiskSpaceRequired=2000000000

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
german.WelcomeLabel1=Willkommen zum [name] Setup
german.WelcomeLabel2=Dieses Setup installiert die vollständige "Ömers All in One DingsBums" Anwendung inklusive:%n%n• Python 3.13 (Embedded)%n• Streamlit und alle Dependencies%n• Alle App-Komponenten%n• Datenbanken und Assets%n• PDF-Templates%n• CRM-System%n%nDateigröße: ~1.5 GB%n%nKlicken Sie auf Weiter zum Fortfahren.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; === HAUPTANWENDUNG (PyInstaller Build) ===
Source: "dist\Ömers All in One Dingsbums\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; === PYTHON EMBEDDED (falls benötigt) ===
; Kommentar: Python Embedded kann heruntergeladen und hier eingebunden werden
; Source: "python-embedded\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

; ===================================================================
; === ALLE KRITISCHEN PYTHON-DATEIEN (KERN-MODULE) ===
; ===================================================================
Source: "gui.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "de.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "locales.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "database.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "database_backup.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "database_clean.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "calculations.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "calculations_heatpump.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "financial_calculations.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "pdf_generator.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "product_rotation_engine.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "price_modification_engine.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "product_db.py"; DestDir: "{app}"; Flags: ignoreversion

; === CRM HAUPT-MODUL ===
Source: "crm.py"; DestDir: "{app}"; Flags: ignoreversion

; === PDF SYSTEM ===
Source: "pdf_preview.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "doc_output.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "central_pdf_system.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "pdf_helpers.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "pdf_styles.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "placeholders.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "dynamic_overlay.py"; DestDir: "{app}"; Flags: ignoreversion

; === PREISSYSTEM ===
Source: "dynamic_pricing_engine.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "price_matrix_lookup.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "price_matrix_store.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "price_matrix_validation.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "matrix_extras_calculator.py"; DestDir: "{app}"; Flags: ignoreversion

; === ADMIN PANELS ===
Source: "admin_panel.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "admin_*.py"; DestDir: "{app}"; Flags: ignoreversion

; === ANALYSIS & CHARTS ===
Source: "analysis.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "advanced_charts.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "chart_builder.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "chart_styling.py"; DestDir: "{app}"; Flags: ignoreversion

; === 3D VISUALIZATION ===
Source: "pv3d.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "solar_3d_view_*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "pv_visuals.py"; DestDir: "{app}"; Flags: ignoreversion

; === HEATPUMP SYSTEM ===
Source: "heatpump_*.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "heating_*.py"; DestDir: "{app}"; Flags: ignoreversion

; === UTILITIES ===
Source: "utils.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "german_formatting.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "excel_*.py"; DestDir: "{app}"; Flags: ignoreversion

; === MONITORING & TRACING ===
Source: "app_tracing.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_evaluation.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_health_monitor.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "monitoring_*.py"; DestDir: "{app}"; Flags: ignoreversion

; === WEITERE KERN-MODULE ===
Source: "info_platform.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "options.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "authentication.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "session_security.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "quick_calc.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "intro_screen.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "report_generator.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "services_integration.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "payment_terms.py"; DestDir: "{app}"; Flags: ignoreversion

; ===================================================================
; === ALLE PYTHON-DATEIEN IM ROOT (KOMPLETT) ===
; ===================================================================
; Nutze Wildcard für ALLE .py Dateien im Root
Source: "*.py"; DestDir: "{app}"; Flags: ignoreversion

; === ALLE JSON DATEIEN ===
Source: "*.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE MARKDOWN DOKUMENTATION ===
Source: "*.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE BATCH & SHELL SCRIPTS ===
Source: "*.bat"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.ps1"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.sh"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE CONFIG DATEIEN ===
Source: "*.toml"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.yaml"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.yml"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.ini"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.cfg"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.conf"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE TEXT & CSV DATEIEN ===
Source: "*.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.csv"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE SPEC & ISS DATEIEN ===
Source: "*.spec"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.iss"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE ICO & IMAGE DATEIEN ===
Source: "*.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.jpg"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.jpeg"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.gif"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.svg"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === ALLE 3D MODEL DATEIEN ===
Source: "*.stl"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.obj"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.gltf"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.glb"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.bin"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === WEITERE DATEITYPEN ===
Source: "*.db"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.sqlite"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.sqlite3"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.xml"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.html"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.css"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.js"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "*.zip"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; ===================================================================
; === ALLE DATENVERZEICHNISSE (KOMPLETT MIT WILDCARDS) ===
; ===================================================================
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "coords\*"; DestDir: "{app}\coords"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "coords_multi\*"; DestDir: "{app}\coords_multi"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "coords_wp\*"; DestDir: "{app}\coords_wp"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "pdf_templates_static\*"; DestDir: "{app}\pdf_templates_static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "pdf_template_engine\*"; DestDir: "{app}\pdf_template_engine"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".streamlit\*"; DestDir: "{app}\.streamlit"; Flags: ignoreversion recursesubdirs createallsubdirs

; ===================================================================
; === ALLE KOMPONENTEN-ORDNER ===
; ===================================================================
Source: "components\*"; DestDir: "{app}\components"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "crm\*"; DestDir: "{app}\crm"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "widgets\*"; DestDir: "{app}\widgets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "pages\*"; DestDir: "{app}\pages"; Flags: ignoreversion recursesubdirs createallsubdirs

; === UI & THEMING ===
Source: "ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "theming\*"; DestDir: "{app}\theming"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === PRICING SYSTEM ===
Source: "pricing\*"; DestDir: "{app}\pricing"; Flags: ignoreversion recursesubdirs createallsubdirs

; === CONTROLLING ===
Source: "controlling\*"; DestDir: "{app}\controlling"; Flags: ignoreversion recursesubdirs createallsubdirs

; === MIGRATIONS ===
Source: "migrations\*"; DestDir: "{app}\migrations"; Flags: ignoreversion recursesubdirs createallsubdirs

; === CLI ===
Source: "cli\*"; DestDir: "{app}\cli"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === TEMPLATES ===
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === JSON DATEN ===
Source: "json\*"; DestDir: "{app}\json"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === EXCEL DATEN ===
Source: "excel\*"; DestDir: "{app}\excel"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === CONFIGS ===
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "schema.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "settings.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === AGENT & AI ===
Source: "Agent\*"; DestDir: "{app}\Agent"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "agent_workspace\*"; DestDir: "{app}\agent_workspace"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "agent_ui.py"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "ai_companion.py"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === KNOWLEDGE BASE ===
Source: "knowledge_base\*"; DestDir: "{app}\knowledge_base"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === DOCS ===
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === ALERTS ===
Source: "alerts\*"; DestDir: "{app}\alerts"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === PV MOUNTING ===
Source: "unterkonstruktion_pv\*"; DestDir: "{app}\unterkonstruktion_pv"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === MULTI-PDF POSITIONING ===
Source: "multi_pdf_positioning\*"; DestDir: "{app}\multi_pdf_positioning"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; === APP ICON ===
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; === KUNDEN-DOKUMENTE (leer erstellen) ===
; Wird beim ersten Start erstellt

[Dirs]
Name: "{app}\customer_documents"; Permissions: users-full
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Starte App nach Installation (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Prüfe ob genug Platz vorhanden ist
  if GetSpaceOnDisk(ExpandConstant('{app}'), False, nil, nil, nil) < 2000000000 then
  begin
    MsgBox('Nicht genügend Speicherplatz. Es werden mindestens 2 GB benötigt.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Hier könnten weitere Post-Install-Aktionen durchgeführt werden
    // z.B. Datenbank initialisieren, Konfiguration erstellen
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\customer_documents"
Type: filesandirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.pyc"
