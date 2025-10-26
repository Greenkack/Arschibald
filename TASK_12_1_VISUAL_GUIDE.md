# Task 12.1 Visual Guide: Template-Auswahl

This guide provides a visual walkthrough of the Template Selection feature.

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📄 PDF-Template-Verwaltung                                     │
│  Verwalten Sie verschiedene PDF-Templates für unterschiedliche  │
│  Angebots-Designs.                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [📋 Template-Auswahl] [➕ Neues Template hinzufügen]          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  📋 Verfügbare Templates                                        │
│                                                                  │
│  Wählen Sie ein Template:                                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Standard Template                              ▼       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Template-Details:                                              │
│  ┌──────────────────────────────┬──────────────────────────┐   │
│  │ Name: Standard Template      │ ID: standard_template    │   │
│  │ Beschreibung: Standard PDF   │ Erstellt: 2025-01-09     │   │
│  │ Status: 🟢 Aktiv             │                          │   │
│  └──────────────────────────────┴──────────────────────────┘   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ▼ 📁 Template-Dateien anzeigen                                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [✓ Dieses Template ist aktiv]  [🗑️ Löschen]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Template Dropdown

```
┌────────────────────────────────────────────────────────┐
│ Standard Template                              ▼       │
├────────────────────────────────────────────────────────┤
│ Standard Template                                      │
│ Modern Template                                        │
│ Corporate Template                                     │
│ Minimal Template                                       │
└────────────────────────────────────────────────────────┘
```

**Features:**

- Shows all available templates
- Currently active template pre-selected
- User-friendly display names
- Dropdown arrow for expansion

### 2. Template Details (Two-Column Layout)

```
┌──────────────────────────────┬──────────────────────────┐
│ Left Column                  │ Right Column             │
├──────────────────────────────┼──────────────────────────┤
│ Name: Standard Template      │ ID: standard_template    │
│ Beschreibung: Standard PDF   │ Erstellt: 2025-01-09     │
│   template for offers        │   12:00:00               │
│ Status: 🟢 Aktiv             │                          │
└──────────────────────────────┴──────────────────────────┘
```

**Left Column:**

- Template name (bold)
- Description (multi-line)
- Status indicator (🟢 Aktiv / ⚪ Inaktiv)

**Right Column:**

- Template ID (monospace)
- Creation date/time

### 3. File Paths Expander (Collapsed)

```
▼ 📁 Template-Dateien anzeigen
```

### 3. File Paths Expander (Expanded)

```
▼ 📁 Template-Dateien anzeigen
┌─────────────────────────────────────────────────────────┐
│ Hintergrund-PDFs (Seite 1-8):                          │
│                                                          │
│ ✅ Seite 1: pdf_templates_static/seite1.pdf            │
│ ✅ Seite 2: pdf_templates_static/seite2.pdf            │
│ ✅ Seite 3: pdf_templates_static/seite3.pdf            │
│ ✅ Seite 4: pdf_templates_static/seite4.pdf            │
│ ✅ Seite 5: pdf_templates_static/seite5.pdf            │
│ ✅ Seite 6: pdf_templates_static/seite6.pdf            │
│ ✅ Seite 7: pdf_templates_static/seite7.pdf            │
│ ✅ Seite 8: pdf_templates_static/seite8.pdf            │
│                                                          │
│ ─────────────────────────────────────────────────────── │
│                                                          │
│ Koordinaten-Dateien (YML):                             │
│                                                          │
│ ✅ Seite 1: coords/seite1.yml                          │
│ ✅ Seite 2: coords/seite2.yml                          │
│ ✅ Seite 3: coords/seite3.yml                          │
│ ✅ Seite 4: coords/seite4.yml                          │
│ ✅ Seite 5: coords/seite5.yml                          │
│ ✅ Seite 6: coords/seite6.yml                          │
│ ✅ Seite 7: coords/seite7.yml                          │
│ ✅ Seite 8: coords/seite8.yml                          │
└─────────────────────────────────────────────────────────┘
```

**Features:**

- Shows all 8 background PDF paths
- Shows all 8 coordinate YML paths
- ✅ = File exists
- ❌ = File missing
- Expandable to save space

### 4. Action Buttons

#### When Template is NOT Active

```
┌─────────────────────────────────────────────────────────┐
│ [✓ Template aktivieren]  [🗑️ Löschen]                  │
└─────────────────────────────────────────────────────────┘
```

#### When Template IS Active

```
┌─────────────────────────────────────────────────────────┐
│ [✓ Dieses Template ist aktiv]  [🗑️ Löschen]            │
└─────────────────────────────────────────────────────────┘
```

---

## User Workflows

### Workflow 1: View Template Details

```
1. User opens Admin Panel
   │
   ├─> Clicks "PDF & Design Einstellungen"
   │
   ├─> Clicks "📄 PDF-Templates" tab
   │
   ├─> Sees dropdown with templates
   │
   ├─> Selects a template from dropdown
   │
   └─> Views template details below
```

### Workflow 2: Activate a Template

```
1. User selects inactive template
   │
   ├─> Sees "✓ Template aktivieren" button
   │
   ├─> Clicks button
   │
   ├─> Success message appears:
   │   "✅ Template 'Modern Template' erfolgreich aktiviert!"
   │
   ├─> UI refreshes
   │
   └─> Template now shows "🟢 Aktiv" status
```

### Workflow 3: Delete a Template

```
1. User selects template to delete
   │
   ├─> Clicks "🗑️ Löschen" button
   │
   ├─> Confirmation dialog appears:
   │   "⚠️ Möchten Sie das Template 'Old Template' wirklich löschen?"
   │
   ├─> User clicks "Ja, löschen"
   │
   ├─> Success message appears:
   │   "✅ Template erfolgreich gelöscht!"
   │
   ├─> UI refreshes
   │
   └─> Template removed from dropdown
```

---

## Visual States

### State 1: No Templates Available

```
┌─────────────────────────────────────────────────────────┐
│  📋 Verfügbare Templates                                │
│                                                          │
│  ℹ️ Noch keine Templates vorhanden.                     │
│     Fügen Sie ein neues Template im Tab                 │
│     'Neues Template hinzufügen' hinzu.                  │
└─────────────────────────────────────────────────────────┘
```

### State 2: Template Selected (Active)

```
┌─────────────────────────────────────────────────────────┐
│  Template-Details:                                      │
│  ┌──────────────────────────────┬──────────────────┐   │
│  │ Name: Standard Template      │ ID: standard_... │   │
│  │ Beschreibung: ...            │ Erstellt: ...    │   │
│  │ Status: 🟢 Aktiv             │                  │   │
│  └──────────────────────────────┴──────────────────┘   │
│                                                          │
│  [✓ Dieses Template ist aktiv]  [🗑️ Löschen]          │
└─────────────────────────────────────────────────────────┘
```

### State 3: Template Selected (Inactive)

```
┌─────────────────────────────────────────────────────────┐
│  Template-Details:                                      │
│  ┌──────────────────────────────┬──────────────────┐   │
│  │ Name: Modern Template        │ ID: modern_...   │   │
│  │ Beschreibung: ...            │ Erstellt: ...    │   │
│  │ Status: ⚪ Inaktiv           │                  │   │
│  └──────────────────────────────┴──────────────────┘   │
│                                                          │
│  [✓ Template aktivieren]  [🗑️ Löschen]                │
└─────────────────────────────────────────────────────────┘
```

### State 4: Delete Confirmation

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ Möchten Sie das Template 'Old Template'            │
│     wirklich löschen?                                   │
│                                                          │
│  [Ja, löschen]  [Abbrechen]                            │
└─────────────────────────────────────────────────────────┘
```

### State 5: File Validation (Mixed)

```
▼ 📁 Template-Dateien anzeigen
┌─────────────────────────────────────────────────────────┐
│ Hintergrund-PDFs (Seite 1-8):                          │
│                                                          │
│ ✅ Seite 1: pdf_templates_static/seite1.pdf            │
│ ✅ Seite 2: pdf_templates_static/seite2.pdf            │
│ ❌ Seite 3: pdf_templates_static/seite3.pdf            │
│ ✅ Seite 4: pdf_templates_static/seite4.pdf            │
│ ❌ Seite 5: Nicht konfiguriert                         │
│ ✅ Seite 6: pdf_templates_static/seite6.pdf            │
│ ✅ Seite 7: pdf_templates_static/seite7.pdf            │
│ ✅ Seite 8: pdf_templates_static/seite8.pdf            │
└─────────────────────────────────────────────────────────┘
```

---

## Color Scheme

### Status Indicators

- 🟢 **Green Circle**: Active template
- ⚪ **White Circle**: Inactive template
- ✅ **Green Checkmark**: File exists
- ❌ **Red X**: File missing/not configured

### Buttons

- **Primary Button** (Blue): "✓ Template aktivieren"
- **Success Button** (Green): "✓ Dieses Template ist aktiv"
- **Danger Button** (Red): "Ja, löschen"
- **Secondary Button** (Gray): "🗑️ Löschen", "Abbrechen"

### Messages

- **Success** (Green): "✅ Template erfolgreich aktiviert!"
- **Error** (Red): "❌ Fehler beim Aktivieren des Templates."
- **Warning** (Yellow): "⚠️ Möchten Sie wirklich löschen?"
- **Info** (Blue): "ℹ️ Noch keine Templates vorhanden."

---

## Responsive Layout

### Desktop View (Wide)

```
┌─────────────────────────────────────────────────────────┐
│  Template-Details:                                      │
│  ┌──────────────────────────────┬──────────────────┐   │
│  │ Name: Standard Template      │ ID: standard_... │   │
│  │ Beschreibung: Standard PDF   │ Erstellt: 2025   │   │
│  │ Status: 🟢 Aktiv             │                  │   │
│  └──────────────────────────────┴──────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Mobile View (Narrow)

```
┌──────────────────────────────┐
│  Template-Details:           │
│  ┌──────────────────────────┐│
│  │ Name: Standard Template  ││
│  │ Beschreibung: Standard   ││
│  │ Status: 🟢 Aktiv         ││
│  └──────────────────────────┘│
│  ┌──────────────────────────┐│
│  │ ID: standard_template    ││
│  │ Erstellt: 2025-01-09     ││
│  └──────────────────────────┘│
└──────────────────────────────┘
```

---

## Accessibility Features

1. **Keyboard Navigation**
   - Tab through dropdown
   - Enter to select
   - Space to activate buttons

2. **Screen Reader Support**
   - Descriptive labels
   - Status announcements
   - Button purposes clear

3. **Visual Indicators**
   - Color + icon (not just color)
   - Clear status text
   - High contrast

4. **Error Prevention**
   - Confirmation dialogs
   - Clear warnings
   - Undo capability (via backup)

---

## Tips for Users

### Best Practices

1. **Always check file paths** before activating a template
2. **Expand file paths section** to verify all files exist
3. **Use descriptive template names** for easy identification
4. **Keep active template** as your default/most-used
5. **Delete unused templates** to keep list clean

### Common Issues

**Issue:** Template activation fails

- **Solution:** Check that all required files exist

**Issue:** Files show ❌ indicator

- **Solution:** Verify file paths are correct and files exist

**Issue:** Can't delete active template

- **Solution:** Activate a different template first

---

## Integration Points

### Database

```python
# Load templates
pdf_templates = load_setting('pdf_templates', {})

# Structure:
{
    'templates': [
        {
            'id': 'template_id',
            'name': 'Template Name',
            'description': 'Description',
            'page_1_background': 'path/to/pdf',
            'page_1_coords': 'path/to/yml',
            # ... pages 2-8
        }
    ],
    'active_template_id': 'template_id'
}
```

### PDF Generation

When generating PDFs, the system will:

1. Load `active_template_id` from settings
2. Find template in `templates` list
3. Use template's background PDFs and coordinates
4. Generate PDF with selected template

---

## Future Enhancements

Planned improvements:

1. **Template Preview**
   - Thumbnail of first page
   - Full preview modal

2. **Template Cloning**
   - Duplicate existing template
   - Modify and save as new

3. **Template Import/Export**
   - Export as JSON
   - Import from file

4. **Template Validation**
   - Automatic file checking
   - YML format validation

---

**Last Updated:** 2025-01-09
**Version:** 1.0
