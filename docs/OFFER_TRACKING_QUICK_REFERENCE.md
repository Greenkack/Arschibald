# Angebotsverfolgung (Offer Tracking) - Quick Reference

## Übersicht

Das Angebotsverfolgung-Modul ermöglicht die systematische Verwaltung und Verfolgung aller Angebote mit automatischen Follow-up-Erinnerungen und Lead-Status-Synchronisation.

## Features

### 1. Status-Workflow
- **Draft** (📝): Angebot in Bearbeitung
- **Sent** (📤): Angebot versendet
- **Accepted** (✅): Angebot angenommen
- **Rejected** (❌): Angebot abgelehnt

### 2. Automatische Follow-ups
- Automatische Erinnerung 7 Tage nach Versand
- Dashboard für ausstehende Follow-ups
- Dringlichkeits-Kennzeichnung (überfällig, dringend, fällig)

### 3. Lead-Status-Synchronisation
- Angebot angenommen → Lead-Status "won"
- Angebot abgelehnt → Lead-Status "lost"

### 4. Ablehnungsgrund-Erfassung
- Vordefinierte Ablehnungsgründe
- Zusätzliche Notizen möglich

### 5. Statistiken & Analytics
- Gesamtanzahl Angebote
- Status-Verteilung
- Conversion Rate
- Durchschnittlicher Angebotswert
- Ausstehende Follow-ups

## Verwendung

### Navigation
Im CRM-Modul auf "📋 Angebote" klicken

### Tabs
1. **📊 Übersicht**: KPIs und Statistiken
2. **📝 Alle Angebote**: Liste mit Filter- und Suchfunktion
3. **⏰ Follow-ups**: Ausstehende Nachfass-Aktionen

## API-Funktionen

### `update_offer_status(conn, project_id, new_status, **kwargs)`
Aktualisiert den Angebotsstatus.

**Parameter:**
- `new_status`: 'draft', 'sent', 'accepted', 'rejected'
- `offer_value`: Angebotswert (optional)
- `rejection_reason`: Ablehnungsgrund (bei rejected)
- `rejection_notes`: Zusätzliche Notizen (bei rejected)

### `get_all_offers(conn, status_filter=None, include_customer_info=True)`
Lädt alle Angebote mit optionalem Filter.

### `get_pending_follow_ups(conn)`
Lädt alle Angebote mit ausstehenden Follow-ups.

### `mark_follow_up_completed(conn, project_id)`
Markiert ein Follow-up als erledigt.

### `get_offer_statistics(conn)`
Berechnet Statistiken über alle Angebote.

## Datenbankfelder (projects Tabelle)

- `offer_status`: Status des Angebots
- `offer_sent_date`: Versanddatum
- `offer_accepted_date`: Annahmedatum
- `offer_rejected_date`: Ablehnungsdatum
- `offer_version`: Versionsnummer
- `offer_value`: Angebotswert
- `rejection_reason`: Ablehnungsgrund
- `rejection_notes`: Ablehnungsnotizen
- `follow_up_date`: Fälligkeitsdatum für Follow-up
- `follow_up_completed`: Follow-up erledigt (0/1)
