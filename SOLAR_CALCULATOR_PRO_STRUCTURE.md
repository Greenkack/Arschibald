# 🏗️ SOLAR CALCULATOR PRO - VOLLSTÄNDIGER STRUKTURBAUM

**Datum**: 28.11.2025  
**Version**: 1.0.0  
**Technologie-Stack**: React + TypeScript + Electron + FastAPI (Python)

---

## 📦 ROOT-STRUKTUR

```
solar-calculator-pro/
├── 📁 .github/                      # GitHub Workflows & CI/CD
│   └── workflows/
│       ├── build.yml                # Build Pipeline
│       ├── ci.yml                   # Continuous Integration
│       ├── performance.yml          # Performance Tests
│       ├── release.yml              # Release Automation
│       └── security.yml             # Security Scanning
│
├── 📁 .husky/                       # Git Hooks (Pre-commit)
│
├── 📁 assets/                       # Statische Ressourcen
│   ├── icon.ico                     # Windows Icon
│   ├── icon.icns                    # macOS Icon
│   ├── icon.png                     # Linux Icon
│   ├── installer-header.bmp         # Installer Header
│   ├── installer-sidebar.bmp        # Installer Sidebar
│   ├── dmg-background.png           # macOS DMG Background
│   └── file-icon.*                  # File Association Icons
│
├── 📁 backend/                      # ⚙️ PYTHON FASTAPI BACKEND
├── 📁 build/                        # Build Konfiguration
│   ├── cert.pfx                     # Windows Zertifikat
│   ├── embedded.provisionprofile    # macOS Provisioning
│   ├── entitlements.mac.plist       # macOS Entitlements
│   ├── entitlements.mac.inherit.plist
│   ├── installer.nsh                # NSIS Installer Script
│   └── notarize.js                  # macOS Notarisierung
│
├── 📁 docs/                         # 📚 DOKUMENTATION
│   ├── ACCESSIBILITY_FEATURES_GUIDE.md
│   ├── ACCESSIBILITY_QUICK_REFERENCE.md
│   ├── CONTRACT_MANAGEMENT_GUIDE.md
│   ├── DOCUMENT_MANAGEMENT_GUIDE.md
│   ├── DRAG_AND_DROP_GUIDE.md
│   ├── I18N_IMPLEMENTATION_GUIDE.md
│   ├── IMAGE_MANAGEMENT_GUIDE.md
│   ├── KEYBOARD_SHORTCUTS_GUIDE.md
│   ├── LEAD_MANAGEMENT_GUIDE.md
│   ├── LICENSE_MANAGEMENT_GUIDE.md
│   ├── PRODUCT_CATALOG_GUIDE.md
│   ├── PRODUCT_IMPORT_EXPORT_GUIDE.md
│   ├── PRODUCT_PRICING_GUIDE.md
│   ├── REPORTING_ANALYTICS_GUIDE.md
│   ├── RESULTS_EXPORT_GUIDE.md
│   ├── RESULTS_REPORTING_GUIDE.md
│   ├── RESULTS_VISUALIZATION_GUIDE.md
│   ├── RESULT_HISTORY_GUIDE.md
│   ├── SALES_PIPELINE_GUIDE.md
│   ├── SEARCH_AND_FILTER_GUIDE.md
│   ├── SYSTEM_CONFIGURATION_GUIDE.md
│   ├── SYSTEM_MAINTENANCE_GUIDE.md
│   ├── THEME_SYSTEM_QUICK_REFERENCE.md
│   ├── USER_PREFERENCES_GUIDE.md
│   └── USER_ROLE_MANAGEMENT_GUIDE.md
│
├── 📁 electron/                     # 🖥️ ELECTRON MAIN PROCESS
├── 📁 frontend/                     # ⚛️ REACT FRONTEND
├── 📁 scripts/                      # 🔧 BUILD & DEPLOY SCRIPTS
│   ├── production-release.js        # Production Release
│   ├── release-production.sh        # Release Shell Script
│   ├── update-website.js            # Website Update
│   └── upload-to-distribution.js    # Upload zu CDN/Server
│
├── 📁 tests/                        # 🧪 UPDATE TESTING
│   └── update-testing/
│       ├── mock-update-server.js    # Mock Update Server
│       ├── package.json
│       ├── README.md
│       ├── test-environment.js
│       ├── test-rollback.js
│       └── test-update-flow.js
│
├── 📄 .coverage                     # Coverage Report
├── 📄 .gitignore                    # Git Ignore
├── 📄 package.json                  # Root Package Config
├── 📄 package-lock.json
├── 📄 README.md                     # Haupt-Readme
├── 📄 QUICK_START.md               # Quick Start Guide
├── 📄 PROGRESS.md                  # Development Progress
├── 📄 INSTALLATION_STATUS.md       # Installation Status
├── 📄 ELECTRON_SETUP_SUMMARY.md    # Electron Setup
├── 📄 verify-setup.js              # Setup Verification
├── 📄 verify-electron-setup.js     # Electron Verification
└── 📄 verify-task-*.js             # Task Verification Scripts
```

---

## ⚛️ FRONTEND STRUKTUR (React + TypeScript + Vite)

```
frontend/
├── 📁 .storybook/                   # Storybook Configuration
│   ├── main.js
│   ├── preview.js
│   └── manager.js
│
├── 📁 node_modules/                 # NPM Dependencies
│
├── 📁 src/                          # 🎯 SOURCE CODE
│   ├── 📄 main.tsx                  # Entry Point
│   ├── 📄 App.tsx                   # Root Component
│   ├── 📄 vite-env.d.ts            # Vite Type Definitions
│   │
│   ├── 📁 components/               # 🧩 REACT COMPONENTS
│   │   ├── 📁 3d/                   # 3D Visualisierung
│   │   │   ├── Animation3DViewer.tsx
│   │   │   ├── Animation3DViewer.css
│   │   │   ├── CollisionDetector.tsx
│   │   │   ├── Export3DPanel.tsx
│   │   │   ├── ModulePlacement.tsx
│   │   │   ├── SceneControls.tsx
│   │   │   ├── ShadingAnalysis.tsx
│   │   │   ├── Visualization3D.tsx
│   │   │   └── Visualization3DAdvanced.tsx
│   │   │
│   │   ├── 📁 accessibility/        # Barrierefreiheit
│   │   │   ├── AccessibilitySettings.tsx
│   │   │   ├── AccessibilitySettings.css
│   │   │   ├── KeyboardShortcutsHelp.tsx
│   │   │   └── KeyboardShortcutsHelp.css
│   │   │
│   │   ├── 📁 admin/                # Admin-Komponenten
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── AdminDashboard.css
│   │   │   ├── AdminPanel.tsx
│   │   │   ├── AdminPanel.css
│   │   │   ├── AdvancedAuthSettings.tsx
│   │   │   ├── BetaTesterManagement.tsx
│   │   │   ├── BrandingManager.tsx
│   │   │   ├── BugTracker.tsx
│   │   │   ├── ComponentTogglePanel.tsx
│   │   │   ├── ConfigurationManager.tsx
│   │   │   ├── FeatureFlags.tsx
│   │   │   ├── SystemConfigurationManager.tsx
│   │   │   └── SystemConfigurationManager.css
│   │   │
│   │   ├── 📁 charts/               # Chart-Komponenten
│   │   │   ├── AmortizationChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   ├── ChartContainer.tsx
│   │   │   ├── EnergyFlowChart.tsx
│   │   │   ├── GermanFormattedChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   ├── PieChart.tsx
│   │   │   └── SavingsChart.tsx
│   │   │
│   │   ├── 📁 combined/             # Hybrid-Systeme (PV+WP)
│   │   │   ├── CombinedSystemCalculator.tsx
│   │   │   ├── CombinedSystemResults.tsx
│   │   │   └── SystemIntegration.tsx
│   │   │
│   │   ├── 📁 common/               # Gemeinsame Komponenten
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── DatePicker.tsx
│   │   │   ├── Dropdown.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Notification.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── TextArea.tsx
│   │   │   └── Tooltip.tsx
│   │   │
│   │   ├── 📁 crm/                  # CRM-Komponenten
│   │   │   ├── ActivityTimeline.tsx
│   │   │   ├── CommunicationHistory.tsx
│   │   │   ├── CustomerForm.tsx
│   │   │   ├── CustomerList.tsx
│   │   │   ├── CustomerManagement.tsx
│   │   │   ├── GoogleCalendarIntegration.tsx
│   │   │   └── NewsPortal.tsx
│   │   │
│   │   ├── 📁 dragdrop/             # Drag & Drop System
│   │   │   ├── DashboardCustomizer.tsx
│   │   │   ├── DashboardCustomizer.css
│   │   │   ├── DraggableCard.tsx
│   │   │   ├── DraggableCard.css
│   │   │   ├── DraggableList.tsx
│   │   │   ├── DraggableList.css
│   │   │   ├── DropZone.tsx
│   │   │   ├── DropZone.css
│   │   │   ├── FileDropZone.tsx
│   │   │   ├── FileDropZone.css
│   │   │   └── index.ts
│   │   │
│   │   ├── 📁 feedback/             # Feedback-System
│   │   │   ├── ErrorDisplay.tsx
│   │   │   ├── SuccessMessage.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── ValidationFeedback.tsx
│   │   │
│   │   ├── 📁 forms/                # Formular-Komponenten
│   │   │   ├── FormBuilder.tsx
│   │   │   ├── FormField.tsx
│   │   │   ├── FormValidation.tsx
│   │   │   ├── HeatPumpForm.tsx
│   │   │   ├── QuickCalculationForm.tsx
│   │   │   └── SolarCalculatorForm.tsx
│   │   │
│   │   ├── 📁 heatpump/             # Wärmepumpen-Komponenten
│   │   │   ├── BuildingDataInput.tsx
│   │   │   ├── EnvironmentalImpact.tsx
│   │   │   ├── FinancingOptions.tsx
│   │   │   ├── HeatPumpCalculator.tsx
│   │   │   ├── HeatPumpConfigurator.tsx
│   │   │   ├── HeatPumpResults.tsx
│   │   │   ├── HeatPumpSizing.tsx
│   │   │   ├── ModelComparison.tsx
│   │   │   └── ProductSelection.tsx
│   │   │
│   │   ├── 📁 i18n/                 # Internationalisierung
│   │   │   ├── LanguageSwitcher.tsx
│   │   │   ├── LanguageSwitcher.css
│   │   │   ├── TranslationManager.tsx
│   │   │   └── TranslationManager.css
│   │   │
│   │   ├── 📁 layout/               # Layout-Komponenten
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Topbar.tsx
│   │   │
│   │   ├── 📁 migration/            # Migrations-UI
│   │   │   ├── MigrationDashboard.tsx
│   │   │   ├── MigrationProgress.tsx
│   │   │   └── MigrationWizard.tsx
│   │   │
│   │   ├── 📁 monitoring/           # Monitoring-Komponenten
│   │   │   ├── PerformanceMonitor.tsx
│   │   │   ├── SystemStatus.tsx
│   │   │   └── UsageStatistics.tsx
│   │   │
│   │   ├── 📁 notifications/        # Benachrichtigungen
│   │   │   ├── NotificationCenter.tsx
│   │   │   ├── NotificationItem.tsx
│   │   │   └── NotificationSettings.tsx
│   │   │
│   │   ├── 📁 pdf/                  # PDF-Komponenten
│   │   │   ├── BatchPdfGenerator.tsx
│   │   │   ├── PdfArchiveManager.tsx
│   │   │   ├── PdfChartPreview.tsx
│   │   │   ├── PdfCompressionSettings.tsx
│   │   │   ├── PdfConfigurator.tsx
│   │   │   ├── PdfHistory.tsx
│   │   │   ├── PdfPreview.tsx
│   │   │   ├── PdfTemplateSelector.tsx
│   │   │   ├── StandardOfferPdf.tsx
│   │   │   └── TemplateCustomizer.tsx
│   │   │
│   │   ├── 📁 pipeline/             # Sales Pipeline
│   │   │   ├── OpportunityDialog.tsx
│   │   │   ├── OpportunityDialog.css
│   │   │   ├── PipelineAnalytics.tsx
│   │   │   ├── PipelineAnalytics.css
│   │   │   ├── PipelineBoard.tsx
│   │   │   └── PipelineBoard.css
│   │   │
│   │   ├── 📁 pricing/              # Preis-Komponenten
│   │   │   ├── DynamicKeyManager.tsx
│   │   │   ├── PriceCalculator.tsx
│   │   │   ├── PriceIncreaseManager.tsx
│   │   │   ├── PriceMatrixExtras.tsx
│   │   │   ├── PriceMatrixUpload.tsx
│   │   │   ├── PriceMatrixValidation.tsx
│   │   │   ├── PriceMatrixVersioning.tsx
│   │   │   └── PricingRules.tsx
│   │   │
│   │   ├── 📁 products/             # Produkt-Komponenten
│   │   │   ├── BatteryManager.tsx
│   │   │   ├── ImportExportPanel.tsx
│   │   │   ├── InverterManager.tsx
│   │   │   ├── ProductCatalog.tsx
│   │   │   ├── ProductDatabase.tsx
│   │   │   ├── ProductImportExport.tsx
│   │   │   ├── ProductList.tsx
│   │   │   ├── ProductRotationManager.tsx
│   │   │   └── PvModuleManager.tsx
│   │   │
│   │   ├── 📁 responsive/           # Responsive Design
│   │   │   ├── AdaptiveCard.tsx
│   │   │   ├── MobileNavigation.tsx
│   │   │   ├── ResponsiveContainer.tsx
│   │   │   ├── ResponsiveGrid.tsx
│   │   │   ├── ResponsiveImage.tsx
│   │   │   ├── ResponsiveTable.tsx
│   │   │   ├── TouchGestures.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── 📁 results/              # Ergebnis-Komponenten
│   │   │   ├── ComparisonView.tsx
│   │   │   ├── ComparisonView.css
│   │   │   ├── ExportOptions.tsx
│   │   │   ├── FinancialResults.tsx
│   │   │   ├── InteractiveDashboard.tsx
│   │   │   ├── InteractiveDashboard.css
│   │   │   ├── ReportGenerator.tsx
│   │   │   ├── ResultHistory.tsx
│   │   │   ├── ResultsVisualization.tsx
│   │   │   └── SolarResults.tsx
│   │   │
│   │   ├── 📁 search/               # Such-Komponenten
│   │   │   ├── AdvancedFilter.tsx
│   │   │   ├── AdvancedFilter.css
│   │   │   ├── GlobalSearch.tsx
│   │   │   └── GlobalSearch.css
│   │   │
│   │   ├── 📁 settings/             # Einstellungen
│   │   │   ├── DatabaseSettings.tsx
│   │   │   ├── EncryptionSettings.tsx
│   │   │   ├── SyncSettings.tsx
│   │   │   ├── SystemSettings.tsx
│   │   │   ├── UserPreferences.tsx
│   │   │   └── UserPreferences.css
│   │   │
│   │   ├── 📁 shortcuts/            # Tastaturkürzel
│   │   │   ├── ContextShortcuts.tsx
│   │   │   ├── GlobalShortcuts.tsx
│   │   │   ├── ShortcutHelp.tsx
│   │   │   ├── ShortcutHelp.css
│   │   │   ├── ShortcutManager.tsx
│   │   │   └── ShortcutManager.css
│   │   │
│   │   ├── 📁 solar/                # Solar-Komponenten
│   │   │   ├── ApiIntegration.tsx
│   │   │   ├── EnergyFlowVisualization.tsx
│   │   │   ├── GridIntegration.tsx
│   │   │   ├── LiveCalculation.tsx
│   │   │   ├── MountingSystemConfigurator.tsx
│   │   │   ├── ShadingAnalysis.tsx
│   │   │   ├── SolarCalculator.tsx
│   │   │   ├── SolarDashboard.tsx
│   │   │   ├── TariffOptimization.tsx
│   │   │   └── WeatherIntegration.tsx
│   │   │
│   │   ├── 📁 steps/                # Multi-Step Wizards
│   │   │   ├── StepIndicator.tsx
│   │   │   ├── StepNavigation.tsx
│   │   │   └── WizardContainer.tsx
│   │   │
│   │   ├── 📁 theme/                # Theme System
│   │   │   ├── CustomThemeCreator.tsx
│   │   │   ├── CustomThemeCreator.css
│   │   │   ├── DarkModeToggle.tsx
│   │   │   ├── DarkModeToggle.css
│   │   │   ├── ThemeImportExport.tsx
│   │   │   ├── ThemeImportExport.css
│   │   │   ├── ThemePanel.tsx
│   │   │   ├── ThemePanel.css
│   │   │   ├── ThemePreview.tsx
│   │   │   ├── ThemePreview.css
│   │   │   ├── ThemeSelector.tsx
│   │   │   ├── ThemeSelector.css
│   │   │   └── index.ts
│   │   │
│   │   ├── 📁 update/               # Update-System
│   │   │   ├── UpdateChecker.tsx
│   │   │   ├── UpdateDownloader.tsx
│   │   │   ├── UpdateNotification.tsx
│   │   │   └── UpdateProgress.tsx
│   │   │
│   │   ├── 📁 wizard/               # Setup-Wizards
│   │   │   ├── DatabaseMigrationWizard.tsx
│   │   │   ├── InitialSetupWizard.tsx
│   │   │   └── OnboardingWizard.tsx
│   │   │
│   │   ├── 📄 FormattedDisplay.tsx  # Deutsche Formatierung
│   │   ├── 📄 GermanCurrencyInput.tsx
│   │   ├── 📄 GermanNumberInput.tsx
│   │   ├── 📄 GermanPercentInput.tsx
│   │   ├── 📄 GermanSlider.tsx
│   │   ├── 📄 PasswordChangeForm.tsx
│   │   ├── 📄 PasswordChangeForm.css
│   │   ├── 📄 ProtectedRoute.tsx
│   │   └── 📄 index.ts
│   │
│   ├── 📁 examples/                 # Demo-Beispiele
│   │   ├── DragAndDropDemo.tsx
│   │   ├── DragAndDropDemo.css
│   │   ├── ResponsiveDemo.tsx
│   │   ├── SearchAndFilterDemo.tsx
│   │   └── SearchAndFilterDemo.css
│   │
│   ├── 📁 hooks/                    # Custom React Hooks
│   │   ├── useApi.ts
│   │   ├── useAuth.ts
│   │   ├── useDebounce.ts
│   │   ├── useDragAndDrop.ts
│   │   ├── useFocusManagement.ts
│   │   ├── useKeyboardNavigation.ts
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useLocalStorage.ts
│   │   ├── usePreferences.ts
│   │   ├── useResponsive.ts
│   │   ├── useScreenReader.ts
│   │   └── useWebSocket.ts
│   │
│   ├── 📁 i18n/                     # Internationalisierung
│   │   ├── i18nConfig.ts
│   │   └── locales/
│   │       ├── de.json              # Deutsche Übersetzungen
│   │       └── en.json              # Englische Übersetzungen
│   │
│   ├── 📁 pages/                    # React Router Pages
│   │   ├── AdminPage.tsx
│   │   ├── CalculatorPage.tsx
│   │   ├── CrmPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── HeatPumpPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── NotFoundPage.tsx
│   │   ├── PdfPage.tsx
│   │   ├── ProductsPage.tsx
│   │   ├── ReportsPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── SolarPage.tsx
│   │
│   ├── 📁 providers/                # React Context Providers
│   │   ├── ApiProvider.tsx
│   │   ├── AuthProvider.tsx
│   │   ├── NotificationProvider.tsx
│   │   ├── ThemeProvider.tsx
│   │   └── WebSocketProvider.tsx
│   │
│   ├── 📁 routes/                   # Routing Configuration
│   │   ├── AppRoutes.tsx
│   │   ├── PrivateRoute.tsx
│   │   └── PublicRoute.tsx
│   │
│   ├── 📁 services/                 # API Services
│   │   ├── api.service.ts           # Basis API Service
│   │   ├── auth.service.ts          # Authentication
│   │   ├── calculation.service.ts   # Berechnungen
│   │   ├── crm.service.ts           # CRM API
│   │   ├── pdf.service.ts           # PDF Generation
│   │   ├── pricing.service.ts       # Pricing API
│   │   ├── product.service.ts       # Produkt-API
│   │   ├── reporting.service.ts     # Reporting
│   │   └── user.service.ts          # User Management
│   │
│   ├── 📁 store/                    # State Management (Zustand/Redux)
│   │   ├── authStore.ts
│   │   ├── calculationStore.ts
│   │   ├── crmStore.ts
│   │   ├── notificationStore.ts
│   │   ├── pdfStore.ts
│   │   ├── pricingStore.ts
│   │   ├── productStore.ts
│   │   ├── shortcutStore.ts
│   │   ├── themeStore.ts
│   │   └── userStore.ts
│   │
│   ├── 📁 styles/                   # Global Styles
│   │   ├── global.css
│   │   ├── responsive.css
│   │   ├── theme.css
│   │   ├── typography.css
│   │   └── variables.css
│   │
│   ├── 📁 test/                     # Frontend Tests
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── 📁 theme/                    # Theme Engine
│   │   ├── themeEngine.ts
│   │   └── themePresets.ts
│   │
│   ├── 📁 types/                    # TypeScript Types
│   │   ├── api.types.ts
│   │   ├── calculation.types.ts
│   │   ├── crm.types.ts
│   │   ├── pdf.types.ts
│   │   ├── pricing.types.ts
│   │   ├── product.types.ts
│   │   └── user.types.ts
│   │
│   └── 📁 utils/                    # Utility Functions
│       ├── accessibilityAudit.ts
│       ├── api.utils.ts
│       ├── date.utils.ts
│       ├── formatting.utils.ts
│       ├── localeFormatter.ts
│       ├── rtlSupport.ts
│       ├── string.utils.ts
│       └── validation.utils.ts
│
├── 📄 .env                          # Environment Variables (Local)
├── 📄 .env.example                  # Environment Template
├── 📄 .eslintrc.cjs                 # ESLint Config
├── 📄 .prettierrc                   # Prettier Config
├── 📄 index.html                    # HTML Entry Point
├── 📄 package.json                  # Frontend Dependencies
├── 📄 package-lock.json
├── 📄 tsconfig.json                 # TypeScript Config
├── 📄 tsconfig.node.json            # Node TypeScript Config
├── 📄 vite.config.ts                # Vite Build Config
└── 📄 verify-task-*.js              # Verification Scripts
```

---

## ⚙️ BACKEND STRUKTUR (FastAPI + Python)

```
backend/
├── 📁 .github-workflows-example.yml # CI/CD Template
├── 📁 .pytest_cache/                # Pytest Cache
├── 📁 __pycache__/                  # Python Cache
│
├── 📁 api/                          # 🌐 REST API ENDPOINTS
│   ├── 📄 .gitkeep
│   └── 📁 v1/                       # API Version 1
│       ├── additional_components.py
│       ├── admin_dashboard.py       # Admin Dashboard API
│       ├── animation_3d.py          # 3D Animation API
│       ├── api_integration.py       # Drittanbieter-Integration
│       ├── audit.py                 # Audit Log API
│       ├── auth_advanced.py         # Erweiterte Auth
│       ├── backup.py                # Backup API
│       ├── batch_pdf.py             # Batch PDF Generation
│       ├── battery.py               # Batterie API
│       ├── battery_storage.py       # Speicher API
│       ├── branding.py              # Branding API
│       ├── catalog.py               # Produktkatalog API
│       ├── collision_detection.py   # Kollisionserkennung
│       ├── combined_system.py       # Hybrid-Systeme API
│       ├── companies.py             # Firmen-Verwaltung
│       ├── component_toggles.py     # Feature Toggles
│       ├── contracts.py             # Vertrags-API
│       ├── contract_warranty.py     # Garantie-API
│       ├── crm_advanced.py          # Erweitertes CRM
│       ├── crm_dashboard.py         # CRM Dashboard
│       ├── currency.py              # Währungs-API
│       ├── customer_data.py         # Kundendaten API
│       ├── database.py              # Datenbank-Verwaltung
│       ├── database_backup.py       # DB Backup
│       ├── database_optimization.py # DB Optimierung
│       ├── database_type.py         # Multi-DB Support
│       ├── documents.py             # Dokument-API
│       ├── encryption.py            # Verschlüsselung
│       ├── energy_flow_visualization.py # Energie-Fluss
│       ├── exports.py               # Export-API
│       ├── export_3d.py             # 3D Export
│       ├── extended_pv_pdf.py       # Erweiterte PV-PDFs
│       ├── extended_wp_pdf.py       # Erweiterte WP-PDFs
│       ├── feature_flags.py         # Feature Flags
│       ├── financial_analysis.py    # Finanzanalyse
│       ├── google_calendar.py       # Google Kalender
│       ├── grid_integration.py      # Netz-Integration
│       ├── heatpump_building.py     # Gebäudedaten
│       ├── heatpump_financing.py    # WP-Finanzierung
│       ├── heatpump_models.py       # WP-Modelle
│       ├── heatpump_products.py     # WP-Produkte
│       ├── heatpump_results.py      # WP-Ergebnisse
│       ├── i18n.py                  # Internationalisierung
│       ├── images.py                # Bild-Verwaltung
│       ├── import_export.py         # Import/Export
│       ├── integrations.py          # Integrationen
│       ├── inventory.py             # Lagerbestand
│       ├── inverters.py             # Wechselrichter
│       ├── leads.py                 # Lead-Verwaltung
│       ├── license.py               # Lizenz-Verwaltung
│       ├── live_calculation.py      # Live-Berechnung
│       ├── maintenance.py           # Wartung
│       ├── migration.py             # Migrations-API
│       ├── module_features.py       # Modul-Features
│       ├── monitoring.py            # Monitoring
│       ├── mounting_system.py       # Montagesystem
│       ├── multi_pdf_template.py    # Multi-PDF Templates
│       ├── news_portal.py           # News Portal
│       ├── notifications.py         # Benachrichtigungen
│       ├── pdf_advanced.py          # Erweiterte PDFs
│       ├── pdf_archiving.py         # PDF-Archivierung
│       ├── pdf_compression.py       # PDF-Kompression
│       ├── pdf_configuration.py     # PDF-Konfiguration
│       ├── pdf_export.py            # PDF-Export
│       ├── permissions.py           # Berechtigungen
│       ├── pipeline.py              # Sales Pipeline
│       ├── preferences.py           # Benutzereinstellungen
│       ├── price_increase.py        # Preiserhöhung
│       ├── price_matrix_extras.py   # Preismatrix Extras
│       ├── price_matrix_performance.py # Preismatrix Performance
│       ├── price_matrix_validation.py # Preismatrix Validierung
│       ├── price_matrix_versioning.py # Preismatrix Versionierung
│       ├── pricing.py               # Preis-API
│       ├── pricing_advanced.py      # Erweiterte Preise
│       ├── product_advanced.py      # Erweiterte Produkte
│       ├── product_import_export.py # Produkt Im/Export
│       ├── product_rotation.py      # Produkt-Rotation
│       ├── pv_heatpump_integration.py # PV+WP Integration
│       ├── pv_modules.py            # PV-Module
│       ├── quick_calculation.py     # Schnellberechnung
│       ├── reporting.py             # Reporting-API
│       ├── reports.py               # Report-Generierung
│       ├── results_visualization.py # Ergebnis-Visualisierung
│       ├── result_history.py        # Ergebnis-Historie
│       ├── search.py                # Such-API
│       ├── shading.py               # Verschattung
│       ├── standard_offer_pdf.py    # Standard-Angebot PDF
│       ├── standard_pv_pdf.py       # Standard PV-PDF
│       ├── standard_wp_pdf.py       # Standard WP-PDF
│       ├── sync.py                  # Synchronisation
│       ├── system_config.py         # System-Konfiguration
│       ├── system_settings.py       # System-Einstellungen
│       ├── tariff_optimization.py   # Tarif-Optimierung
│       ├── users.py                 # Benutzer-API
│       ├── visualization_3d_advanced.py # 3D-Visualisierung Advanced
│       ├── visualization_advanced.py # Erweiterte Visualisierung
│       └── weather.py               # Wetter-API
│
├── 📁 core/                         # 🔧 CORE MODULES
│   ├── 📄 .gitkeep
│   ├── api_client.py                # API Client
│   ├── async_operations.py          # Async Operations
│   ├── base_service.py              # Basis Service
│   ├── caching.py                   # Caching System
│   ├── database_abstraction.py      # DB Abstraction Layer
│   ├── database_optimization.py     # DB Optimierung
│   ├── encryption.py                # Verschlüsselung
│   ├── errors.py                    # Error Definitions
│   ├── error_wrapper.py             # Error Wrapper
│   ├── german_formatter.py          # Deutsche Formatierung
│   ├── logging_decorator.py         # Logging Decorator
│   ├── performance_monitoring.py    # Performance Monitoring
│   └── validators.py                # Validatoren
│
├── 📁 docs/                         # 📚 BACKEND DOKUMENTATION
│   ├── AUDIT_SYSTEM_GUIDE.md
│   ├── AUDIT_SYSTEM_QUICK_REFERENCE.md
│   ├── DATABASE_BACKUP_GUIDE.md
│   ├── DATABASE_BACKUP_QUICK_REFERENCE.md
│   ├── DATABASE_OPTIMIZATION_GUIDE.md
│   ├── INVENTORY_MANAGEMENT_GUIDE.md
│   ├── INVENTORY_QUICK_REFERENCE.md
│   ├── MIGRATION_SYSTEM_QUICK_REFERENCE.md
│   ├── MULTI_CURRENCY_GUIDE.md
│   ├── MULTI_CURRENCY_QUICK_REFERENCE.md
│   ├── MULTI_DATABASE_QUICK_REFERENCE.md
│   ├── MULTI_DATABASE_SUPPORT_GUIDE.md
│   ├── PRICE_MATRIX_EXTRAS_GUIDE.md
│   ├── PRICE_MATRIX_EXTRAS_QUICK_REFERENCE.md
│   ├── PRICE_MATRIX_PERFORMANCE_GUIDE.md
│   ├── PRICE_MATRIX_VERSIONING_GUIDE.md
│   └── PRICE_MATRIX_VERSIONING_QUICK_REFERENCE.md
│
├── 📁 i18n/                         # 🌍 INTERNATIONALISIERUNG
│   └── i18n_config.py               # i18n Config
│
├── 📁 legacy/                       # 📦 LEGACY CODE
│   └── (deprecated modules)
│
├── 📁 middleware/                   # ⚙️ MIDDLEWARE
│   ├── 📄 .gitkeep
│   └── feature_flag_middleware.py   # Feature Flag Middleware
│
├── 📁 migrations/                   # 🗄️ DATENBANK MIGRATIONEN
│   ├── add_advanced_auth_tables.py
│   ├── add_api_integration_tables.py
│   ├── add_audit_tables.py
│   ├── add_branding_tables.py
│   ├── add_catalog_tables.py
│   ├── add_communication_tables.py
│   ├── add_company_tables.py
│   ├── add_component_toggles.py
│   ├── add_configuration_tables.py
│   ├── add_contract_tables.py
│   ├── add_currency_tables.py
│   ├── add_document_tables.py
│   ├── add_encryption_tables.py
│   ├── add_feature_flags.py
│   ├── add_i18n_tables.py
│   ├── add_image_tables.py
│   ├── add_inventory_tables.py
│   ├── add_lead_management_tables.py
│   ├── add_license_tables.py
│   ├── add_maintenance_tables.py
│   ├── add_notification_tables.py
│   ├── add_permission_system.py
│   ├── add_pipeline_tables.py
│   ├── add_preference_tables.py
│   ├── add_pricing_tables.py
│   ├── add_price_matrix_versioning_tables.py
│   ├── add_reporting_tables.py
│   ├── add_result_history_tables.py
│   ├── add_sync_tables.py
│   ├── add_system_config_tables.py
│   ├── data_transformer.py          # Data Transformer
│   ├── data_validator.py            # Data Validator
│   ├── database_migrator.py         # Migration Engine
│   ├── migrate_cli.py               # CLI Tool
│   ├── progress_tracker.py          # Progress Tracker
│   └── examples/
│       ├── 001_add_user_columns.py
│       └── 002_migrate_user_data.py
│
├── 📁 models/                       # 📊 DATENMODELLE & SCHEMAS
│   ├── 📄 .gitkeep
│   ├── animation_schemas.py
│   ├── api_integration_models.py
│   ├── api_integration_schemas.py
│   ├── audit_models.py
│   ├── audit_schemas.py
│   ├── auth_advanced_models.py
│   ├── auth_advanced_schemas.py
│   ├── battery_schemas.py
│   ├── branding_models.py
│   ├── branding_schemas.py
│   ├── catalog_models.py
│   ├── catalog_schemas.py
│   ├── combined_system_schemas.py
│   ├── communication_models.py
│   ├── communication_schemas.py
│   ├── company_models.py
│   ├── company_schemas.py
│   ├── component_toggle_models.py
│   ├── component_toggle_schemas.py
│   ├── configuration_models.py
│   ├── configuration_schemas.py
│   ├── contract_models.py
│   ├── contract_schemas.py
│   ├── currency_models.py
│   ├── currency_schemas.py
│   ├── document_models.py
│   ├── document_schemas.py
│   ├── encryption_models.py
│   ├── encryption_schemas.py
│   ├── export_schemas.py
│   ├── feature_flag_models.py
│   ├── feature_flag_schemas.py
│   ├── financial_schemas.py
│   ├── grid_schemas.py
│   ├── heatpump_product_schemas.py
│   ├── i18n_models.py
│   ├── i18n_schemas.py
│   ├── image_models.py
│   ├── image_schemas.py
│   ├── import_export_schemas.py
│   ├── integration_schemas.py
│   ├── inventory_models.py
│   ├── inventory_schemas.py
│   ├── inverter_schemas.py
│   ├── lead_models.py
│   ├── lead_schemas.py
│   ├── license_models.py
│   ├── license_schemas.py
│   ├── maintenance_models.py
│   ├── maintenance_schemas.py
│   ├── monitoring_schemas.py
│   ├── notification_models.py
│   ├── notification_schemas.py
│   ├── pdf_config_schemas.py
│   ├── permission_models.py
│   ├── permission_schemas.py
│   ├── pipeline_models.py
│   ├── pipeline_schemas.py
│   ├── preference_models.py
│   ├── preference_schemas.py
│   ├── price_matrix_version_models.py
│   ├── price_matrix_version_schemas.py
│   ├── pricing_models.py
│   ├── pricing_schemas.py
│   ├── product_import_schemas.py
│   ├── reporting_models.py
│   ├── reporting_schemas.py
│   ├── report_schemas.py
│   ├── results_schemas.py
│   ├── result_history_models.py
│   ├── result_history_schemas.py
│   ├── sync_models.py
│   ├── sync_schemas.py
│   ├── system_config_models.py
│   ├── system_config_schemas.py
│   ├── system_settings_schemas.py
│   ├── tariff_schemas.py
│   ├── user_models.py
│   └── user_schemas.py
│
├── 📁 output/                       # 📄 OUTPUT FILES
│   └── (generated PDFs, reports)
│
├── 📁 services/                     # 💼 BUSINESS LOGIC SERVICES
│   ├── 📄 .gitkeep
│   ├── admin_dashboard_service.py
│   ├── animation_3d_service.py
│   ├── api_integration_service.py
│   ├── audit_service.py
│   ├── auth_advanced_service.py
│   ├── backup_scheduler.py
│   ├── backup_service.py
│   ├── batch_pdf_service.py
│   ├── battery_storage_service.py
│   ├── beta_tester_service.py
│   ├── branding_service.py
│   ├── bug_fix_service.py
│   ├── bug_tracker_service.py
│   ├── catalog_service.py
│   ├── collision_detection_service.py
│   ├── combined_system_service.py
│   ├── communication_service.py
│   ├── company_service.py
│   ├── component_toggle_service.py
│   ├── configuration_service.py
│   ├── contract_service.py
│   ├── crm_advanced_service.py
│   ├── currency_service.py
│   ├── customer_data_service.py
│   ├── database_backup_service.py
│   ├── database_management_service.py
│   ├── database_migration_service.py
│   ├── database_optimization_service.py
│   ├── document_service.py
│   ├── encryption_service.py
│   ├── export_3d_service.py
│   ├── export_service.py
│   ├── extended_pv_pdf_service.py
│   ├── extended_wp_pdf_service.py
│   ├── feature_flag_service.py
│   ├── financial_analysis_service.py
│   ├── formula_engine.py
│   ├── grid_integration_service.py
│   ├── heatpump_advanced_service.py
│   ├── heatpump_product_service.py
│   ├── heatpump_sizing_service.py
│   ├── i18n_service.py
│   ├── image_service.py
│   ├── import_export_service.py
│   ├── inventory_service.py
│   ├── inverter_service.py
│   ├── lead_service.py
│   ├── license_service.py
│   ├── maintenance_service.py
│   ├── module_feature_service.py
│   ├── module_placement_algorithms.py
│   ├── monitoring_service.py
│   ├── mounting_system_service.py
│   ├── multi_pdf_template_service.py
│   ├── notification_service.py
│   ├── pdf_advanced_service.py
│   ├── pdf_archiving_service.py
│   ├── pdf_chart_service.py
│   ├── pdf_compression_service.py
│   ├── pdf_configuration_service.py
│   ├── pdf_export_service.py
│   ├── pdf_history_service.py
│   ├── performance_optimization_service.py
│   ├── permission_service.py
│   ├── pipeline_service.py
│   ├── preference_service.py
│   ├── price_increase_service.py
│   ├── price_matrix_extras_service.py
│   ├── price_matrix_performance_service.py
│   ├── price_matrix_validation_service.py
│   ├── price_matrix_version_service.py
│   ├── pricing_advanced_service.py
│   ├── pricing_service.py
│   ├── product_advanced_service.py
│   ├── product_import_export_service.py
│   ├── product_rotation_service.py
│   ├── pv_dynamic_key_manager.py
│   ├── pv_module_service.py
│   ├── pv_pdf_bytes_generator.py
│   ├── reporting_service.py
│   ├── report_generation_service.py
│   ├── results_visualization_service.py
│   ├── result_history_service.py
│   ├── search_service.py
│   ├── shading_analysis_service.py
│   ├── solar_calculator_advanced_service.py
│   ├── standard_pv_pdf_service.py
│   ├── standard_wp_pdf_service.py
│   ├── sync_scheduler.py
│   ├── sync_service.py
│   ├── system_config_service.py
│   ├── system_settings_service.py
│   ├── tariff_optimization_service.py
│   ├── third_party_integration_service.py
│   ├── universal_dynamic_key_manager.py
│   ├── universal_pdf_bytes_generator.py
│   ├── user_service.py
│   ├── visualization_3d_advanced_features.py
│   ├── visualization_advanced_service.py
│   └── weather_service.py
│
├── 📁 tests/                        # 🧪 BACKEND TESTS
│   ├── test_currency_service.py
│   ├── test_database_abstraction.py
│   ├── test_database_backup_service.py
│   ├── test_database_migration_service.py
│   ├── test_database_optimization_service.py
│   ├── test_license_service.py
│   ├── test_migration_system.py
│   ├── test_price_matrix_extras_service.py
│   ├── test_price_matrix_performance_service.py
│   └── test_price_matrix_versioning.py
│
├── 📄 .coverage                     # Coverage Report
├── 📄 .env.example                  # Environment Template
├── 📄 .flake8                       # Flake8 Config
├── 📄 backend.spec                  # PyInstaller Spec
├── 📄 build_backend.py              # Backend Build Script
├── 📄 config.py                     # Backend Config
├── 📄 main.py                       # 🚀 FASTAPI ENTRY POINT
├── 📄 INTEGRATION_GUIDE_EXPORTS.md  # Integration Guide
├── 📄 PACKAGING_README.md           # Packaging Guide
├── 📄 QUICK_START_PACKAGING.md      # Quick Start
├── 📄 pyproject.toml                # Python Project Config
├── 📄 requirements.txt              # Python Dependencies
├── 📄 test_packaging.py             # Packaging Tests
├── 📄 verify_packaging_setup.py     # Packaging Verification
└── 📄 __init__.py                   # Package Init
```

---

## 🖥️ ELECTRON STRUKTUR (Main Process)

```
electron/
├── 📄 backend-manager.js            # Backend Process Manager
├── 📄 beta-updater.js               # Beta Update System
├── 📄 crash-reporter.js             # Crash Reporting
├── 📄 deep-link.js                  # Deep Linking
├── 📄 demo-backend-manager.js       # Demo Backend Manager
├── 📄 demo-performance.js           # Performance Demo
├── 📄 main.js                       # 🚀 ELECTRON MAIN ENTRY
├── 📄 menu.js                       # Application Menu
├── 📄 notifications.js              # Native Notifications
├── 📄 performance-manager.js        # Performance Management
├── 📄 preload.js                    # Preload Script (Context Bridge)
├── 📄 resource-cleanup.js           # Resource Cleanup
├── 📄 shortcuts.js                  # Native Keyboard Shortcuts
├── 📄 test-backend-manager.js       # Backend Manager Tests
├── 📄 tray.js                       # System Tray
├── 📄 update-config.js              # Update Configuration
├── 📄 updater.js                    # Auto-Update System
└── 📄 window-manager.js             # Window Management
```

---

## 📊 STATISTIK

### Frontend (React/TypeScript)

- **Komponenten**: 150+ React Components
- **Custom Hooks**: 12 Hooks
- **Services**: 9 API Services
- **Stores**: 10 State Stores
- **Pages**: 12 Router Pages
- **Beispiele**: 5 Demo Components

### Backend (Python/FastAPI)

- **API Endpoints**: 115+ REST Endpoints
- **Services**: 97 Business Logic Services
- **Models**: 92 Data Models & Schemas
- **Migrations**: 31 Database Migrations
- **Core Modules**: 13 Core Utilities
- **Tests**: 10 Test Suites

### Electron (JavaScript)

- **Main Process Scripts**: 16 Module
- **IPC Channels**: ~30+ Channels
- **Window Manager**: Multi-Window Support
- **Auto-Updater**: Production-Ready

### Gesamt

- **Code-Dateien**: ~500+
- **Dokumentation**: 74 MD-Dateien
- **Technologien**: 15+ (React, TypeScript, Python, FastAPI, Electron, Vite, SQLite, etc.)
- **Sprachen**: 2 (Deutsch, Englisch)

---

## 🔧 BUILD & DEPLOYMENT

### Development

```bash
npm run electron:dev          # Start Development (Frontend + Backend + Electron)
npm run frontend:dev          # Frontend Only
npm run backend:dev           # Backend Only
```

### Production Build

```bash
npm run electron:build        # Build All Platforms
npm run electron:build:win    # Windows Only
npm run electron:build:mac    # macOS Only
npm run electron:build:linux  # Linux Only
```

### Testing

```bash
npm run test                  # All Tests
npm run frontend:test         # Frontend Tests
npm run backend:test          # Backend Tests (pytest)
```

### Linting & Formatting

```bash
npm run lint                  # Lint All
npm run format                # Format All
```

---

## 🎯 KEY FEATURES

### ✅ Vollständig Implementiert

1. **Multi-Language Support** (DE/EN)
2. **3D Visualisierung** mit Kollisionserkennung
3. **PDF-Generierung** (Multi-Template, Batch, Kompression)
4. **CRM-System** (Leads, Pipeline, Kommunikation)
5. **Preismatrix** (Versionierung, Performance, Extras)
6. **Admin-Dashboard** (Monitoring, Konfiguration)
7. **Drag & Drop System**
8. **Theme Engine** (Dark Mode, Custom Themes)
9. **Barrierefreiheit** (ARIA, Keyboard Navigation)
10. **Auto-Update System** (Production-Ready)
11. **Database Management** (Multi-DB, Backup, Migration)
12. **Reporting & Analytics**
13. **Product Management** (Import/Export, Rotation)
14. **License Management**
15. **Responsive Design** (Desktop + Mobile)

### 🔐 Sicherheit

- **Verschlüsselung** (AES-256)
- **Advanced Authentication** (2FA, SSO)
- **Audit Logging**
- **Permission System**
- **Code Signing** (Windows + macOS)

### 📦 Deployment

- **Electron Builder** für Multi-Platform
- **Auto-Updater** mit Rollback
- **CI/CD** via GitHub Actions
- **Code Signing** & Notarisierung

---

**Erstellt am**: 28.11.2025  
**Version**: 1.0.0  
**Status**: ✅ Produktionsbereit
