---

# ROADMAP.md (vollständig)

```markdown
# ROADMAP – Migration & Ausbau (PV/WP App)

> Ziel: Funktionsgleichheit zur Python/Streamlit-App **plus** robuste Architektur
> für Multi-PDF, Mehrjahres-Simulation, CRM und Admin. Fokus: Korrekte
> Berechnungen, deutsche Formate, reproduzierbarer PDF-Output.

---

## Phase 0 – Stabilisieren (DONE/ONGOING)

- [x] Monorepo (pnpm workspaces), Ordnerstruktur
- [x] Electron Main (tsup watch), Vite Renderer (Tailwind CJS Fix)
- [x] Router + Screens: ModeSelect, CustomerForm, AdditionalOptions, Results, Solar, Heatpump
- [x] ProjectProvider (global state)
- [x] Core: `calcKwp`, `computePVFlow` (Produktion, Direkt, Speicher, Überschuss, Netz)
- [x] Deutsche Formatierung Helpers
- [x] CI Grundgerüst
- [ ] **Electron Packaging** (electron-builder) – *pending*

**Troubleshooting-Historie (wichtig):**

- Electron-Binary Download auf Windows → **ELECTRON_OVERRIDE_DIST_PATH** als Workaround dokumentiert
- PostCSS ESM-Fehler → **postcss.config.cjs** & **tailwind.config.cjs**
- Doppelte Imports/Komponentennamen → beseitigt (Router sauber)

---

## Phase 1 – Preis-Matrix & Tarife (HIGH)

**1. Preis-Matrix (XLSX)**

- [ ] UI „Preis-Matrix hochladen“ (Renderer, Tab in „Administration“)
- [ ] Parsing XLSX → `PriceMatrixTable` (Header = Speicher-Modelle, Spalte A = Modulanzahl)
- [ ] Validierung (exakte Modellnamen wie Produkt-DB)
- [ ] Lookup:
betrag = table[ moduleCount ][ storageModel || "kein Speicher" ]

yaml
Code kopieren
Entspricht Excel `=INDEX(F87:BT181;VERGLEICH(Modulanzahl;F88:F181;0);VERGLEICH(Speicher;F87:BT87;0))`

- [ ] Core-API: `getPriceFromMatrix(moduleCount, storageModel)`
- [ ] Edge Cases: „Kein Speicher“, Rundung/Format, Fehlermeldungen
- [ ] Tests (Golden Master mit Beispielmatrix)

**2. Tarife/Jahrgänge**

- [ ] Admin-Maske: Teileinspeisung/Volleinspeisung je Jahr (ct/kWh)
- [ ] Laden/ Speichern als JSON
- [ ] Core-API: `getFeedInTariff(year, mode)`
- [ ] Ergebnisbindung: Einspeise-Berechnung im Dashboard

---

## Phase 2 – Ergebnisse & Simulationen (HIGH)

- [ ] **Speicherzyklen** parametrisierbar (Default 300) → Settings
- [ ] 10/20-Jahre-Prognose:
- [ ] Strompreissteigerung, Inflation, Wartung, Degradation
- [ ] Output: tabellarisch + Charts
- [ ] **Amortisationszeit** robust (inkl. ggf. „Cheat“-Parameter)
- [ ] Kennzahlen: Autarkiegrad, Eigenverbrauchsquote, etc.

---

## Phase 3 – PDF-Engine (HIGH)

- [ ] Template-Inventar: PV (`nt_nt_0x.pdf`), WP (`hp_nt_0x.pdf`)
- [ ] Koordinaten-Mapping YML→JSON (Schrift, Farbe, Layer, mm-Koords)
- [ ] `packages/pdf`:
- [ ] `templates.ts` (Template/Layers)
- [ ] `coords.ts` (Loader/Validator)
- [ ] `compose.ts` (Overlay, Merge, Metadaten, QR, ICC, Komprimierung)
- [ ] Renderer-UI: PDF Standard/Erweitert/Multi auswählen, Vorschau (Schnell/Seite)
- [ ] Multi-Firma:
- [ ] Rotation (linear/zufällig/kategoriespezifisch)
- [ ] Preis-Staffel je Firma (%)
- [ ] Branding/Logo/Design-Profile
- [ ] Export: ZIP mit n Angeboten

---

## Phase 4 – Wärmepumpe (HIGH)

- [ ] Core: `computeHeatpump(...)` (Heizlast, COP/JAZ, Jahresenergie, Kosten)
- [ ] WP-Produkt-DB (Modelle, Leistungsdaten)
- [ ] Ergebnisbindung ans Dashboard + PDF

---

## Phase 5 – CRM & Schnellkalkulation (MID)

- [ ] Kunden-CRUD (lokal JSON → später SQLite)
- [ ] Angebote/Anhänge persistieren
- [ ] Workflows/Pipeline, Kalender (lokal)
- [ ] Schnellkalkulation (Minimalfelder → Sofort-Ergebnis/Angebot)

---

## Phase 6 – Einstellungen & Admin (MID)

- [ ] PVGIS (on/off), API-Key Eingabe
- [ ] Visualisierung/Design-Profile (Theme/Fonts/Farben)
- [ ] Lokalisierung (JSON-Editor)
- [ ] Daten-Reset UI

---

## Phase 7 – Build & Release (MID)

- [ ] electron-builder: Windows x64
- [ ] App-Update (später), Code Signing (optional)
- [ ] Artefakte in CI

---

## Qualitätskriterien / Tests

- **Goldene Beispiele** (Golden Master) für:
- PV-Produktion + Flüsse (Direkt, Speicher, Überschuss, Netz)
- Preis-Matrix Lookup
- Tarifeinspeisung (Jahr/Modus)
- Mehrjahres-Prognose (mit Parametern)
- **UI Snapshots** für zentrale Screens
- **DE-Format** (1.234,56 €, 12,34 %, 1.234 kWh) konsistent

---

## Optimierungsvorschläge

- **Rechenkerne** (Core) **reine Funktionen**, Side-Effect-frei (für Tests/Performance)
- **Memoization** von teuren Berechnungen pro Eingabe-Hash
- **Zero-Copy**: beim PDF-Merge und Template-Bytes (Buffer Reuse)
- **ICC/Fonts**: Vorab-Einbettung & Caching
- **Stream-basierte ZIP-Erstellung** für Multi-Angebote
- **Config-Schema** (z.B. zod) für alle Admin-Einstellungen + Validierung
- **Persistenz**: SQLite mit Write-Ahead-Log (Performance, Crash-Safety)

---

## Nächste konkrete Schritte (2–3 Tage)

1) **Preis-Matrix UI** (Upload/Validierung/Preview) + Core-Lookup
2) **Tarifverwaltung** (UI + JSON-Persistenz) + Bindung Ergebnis
3) **PDF-Koordinaten-Loader** (JSON) + kleiner Proof-of-Concept Overlay auf 1 Template

---

## Risiken

- PDF-Template-Treue (Koordinaten/Fonts/Skalierung) – frühe POCs notwendig
- Preis-Matrix Modellnamen müssen exakt zur Produkt-DB passen
- Electron Binary Download/Firewall – Workarounds dokumentiert

---

## Definition of Done (MVP)

- Projekt → Solar/WP → Ergebnisse → **korrekte Beträge** (Matrix + Tarife)
- Standard-PDF (7 Seiten) für PV **und** WP generierbar
- Multi-PDF 2 Firmen (Rotation + Staffelung) lauffähig
- Tarife & Einstellungen persistiert; deutsche Formate korrekt
