# Admin Panel Product Datasheets Fix

## Problem

```
NameError: name 'PRODUCT_DATASHEETS_BASE_DIR_ADMIN' is not defined
```

Der Fehler trat auf, weil die Variable `PRODUCT_DATASHEETS_BASE_DIR_ADMIN` innerhalb der Funktion `render_product_management` definiert wurde, aber außerhalb ihres Gültigkeitsbereichs verwendet wurde.

## Lösung

### ✅ Variable als globale Konstante definiert

Die Variable wurde von der lokalen Funktionsdefinition in den globalen Bereich verschoben:

```python
# Produktdatenblätter Verzeichnis
PRODUCT_DATASHEETS_BASE_DIR_ADMIN = os.path.join(os.getcwd(), "data", "product_datasheets")
```

### ✅ Lokale Definition entfernt

Die redundante lokale Definition in der `render_product_management` Funktion wurde entfernt und durch eine Verzeichnis-Existenzprüfung ersetzt.

### ✅ Verzeichnis-Management beibehalten

Die Funktionalität zum Erstellen des Verzeichnisses bleibt erhalten:

```python
# Stelle sicher, dass das Verzeichnis existiert
if not os.path.exists(PRODUCT_DATASHEETS_BASE_DIR_ADMIN):
    try:
        os.makedirs(PRODUCT_DATASHEETS_BASE_DIR_ADMIN)
    except OSError as e:
        st.error(f"Fehler Erstellen Verzeichnis '{PRODUCT_DATASHEETS_BASE_DIR_ADMIN}': {e}")
```

## Verifikation

### ✅ Import erfolgreich

```
✅ Admin Panel import successful
✅ PRODUCT_DATASHEETS_BASE_DIR_ADMIN defined: C:\Users\win10\Desktop\Bokuk2\data\product_datasheets
📁 Expected path: C:\Users\win10\Desktop\Bokuk2\data\product_datasheets
✅ Directory exists
```

### ✅ Alle Verwendungen funktionieren

Die Variable ist jetzt in allen Bereichen der Datei verfügbar:

- Beim Speichern von Datenblättern
- Beim Löschen von Datenblättern  
- Bei der Verzeichniserstellung
- Bei Pfad-Operationen

## Status

✅ **Problem vollständig behoben**

Der Tab 'Produktverwaltung' im Admin Panel sollte jetzt ohne Fehler funktionieren.
