"""
Excel Integration - Help & Documentation System

Dieses Modul stellt Hilfe-Tooltips, Tastatur-Shortcuts und
Dokumentation für die Excel-Integration bereit.
"""

from typing import Dict, List, Any


# Tastatur-Shortcuts Dokumentation
KEYBOARD_SHORTCUTS = {
    "Navigation": {
        "↑ / ↓ / ← / →": "Zwischen Zellen navigieren",
        "Tab": "Zur nächsten Zelle (rechts)",
        "Shift + Tab": "Zur vorherigen Zelle (links)",
        "Enter": "Zur Zelle darunter",
        "Shift + Enter": "Zur Zelle darüber",
        "Ctrl + Home": "Zur ersten Zelle (A1)",
        "Ctrl + End": "Zur letzten Zelle mit Inhalt"
    },
    "Bearbeitung": {
        "F2": "Zelle bearbeiten",
        "Esc": "Bearbeitung abbrechen",
        "Delete": "Zellinhalt löschen",
        "Ctrl + Z": "Rückgängig (Undo)",
        "Ctrl + Y": "Wiederholen (Redo)",
        "Ctrl + C": "Kopieren",
        "Ctrl + V": "Einfügen",
        "Ctrl + X": "Ausschneiden"
    },
    "Formeln": {
        "=": "Formel beginnen",
        "Ctrl + Enter": "Formel übernehmen",
        "F9": "Formel neu berechnen"
    },
    "Speichern": {
        "Ctrl + S": "Matrix speichern"
    }
}


# Funktion-Tooltips mit Beispielen
FUNCTION_TOOLTIPS = {
    # Mathematische Funktionen
    "SUM": {
        "description": "Summiert alle Zahlen in einem Bereich",
        "syntax": "=SUM(Zahl1, [Zahl2], ...)",
        "example": "=SUM(A1:A10) → Summiert A1 bis A10",
        "category": "Mathematik"
    },
    "AVERAGE": {
        "description": "Berechnet den Durchschnitt von Zahlen",
        "syntax": "=AVERAGE(Zahl1, [Zahl2], ...)",
        "example": "=AVERAGE(A1:A10) → Durchschnitt von A1 bis A10",
        "category": "Mathematik"
    },
    "MIN": {
        "description": "Gibt den kleinsten Wert zurück",
        "syntax": "=MIN(Zahl1, [Zahl2], ...)",
        "example": "=MIN(A1:A10) → Kleinster Wert in A1 bis A10",
        "category": "Mathematik"
    },
    "MAX": {
        "description": "Gibt den größten Wert zurück",
        "syntax": "=MAX(Zahl1, [Zahl2], ...)",
        "example": "=MAX(A1:A10) → Größter Wert in A1 bis A10",
        "category": "Mathematik"
    },
    "ROUND": {
        "description": "Rundet eine Zahl auf eine bestimmte Anzahl von Stellen",
        "syntax": "=ROUND(Zahl, Anzahl_Stellen)",
        "example": "=ROUND(3.14159, 2) → 3.14",
        "category": "Mathematik"
    },
    "COUNT": {
        "description": "Zählt die Anzahl der Zahlen in einem Bereich",
        "syntax": "=COUNT(Wert1, [Wert2], ...)",
        "example": "=COUNT(A1:A10) → Anzahl der Zahlen in A1 bis A10",
        "category": "Mathematik"
    },
    
    # Logische Funktionen
    "IF": {
        "description": "Gibt einen Wert zurück wenn eine Bedingung wahr ist, sonst einen anderen",
        "syntax": "=IF(Bedingung, Wert_wenn_wahr, Wert_wenn_falsch)",
        "example": "=IF(A1>10, \"Groß\", \"Klein\") → Prüft ob A1 größer als 10",
        "category": "Logik"
    },
    "AND": {
        "description": "Gibt WAHR zurück wenn alle Bedingungen wahr sind",
        "syntax": "=AND(Bedingung1, [Bedingung2], ...)",
        "example": "=AND(A1>5, B1<10) → Wahr wenn beide Bedingungen erfüllt",
        "category": "Logik"
    },
    "OR": {
        "description": "Gibt WAHR zurück wenn mindestens eine Bedingung wahr ist",
        "syntax": "=OR(Bedingung1, [Bedingung2], ...)",
        "example": "=OR(A1>5, B1<10) → Wahr wenn eine Bedingung erfüllt",
        "category": "Logik"
    },
    "IFERROR": {
        "description": "Gibt einen Wert zurück wenn eine Formel einen Fehler ergibt",
        "syntax": "=IFERROR(Wert, Wert_bei_Fehler)",
        "example": "=IFERROR(A1/B1, 0) → 0 wenn Division durch Null",
        "category": "Logik"
    },
    
    # Lookup-Funktionen
    "VLOOKUP": {
        "description": "Sucht einen Wert in der ersten Spalte und gibt einen Wert aus derselben Zeile zurück",
        "syntax": "=VLOOKUP(Suchkriterium, Bereich, Spaltenindex, [Bereich_Verweis])",
        "example": "=VLOOKUP(A1, B1:D10, 2, FALSE) → Sucht A1 in B1:B10, gibt Wert aus Spalte C zurück",
        "category": "Lookup"
    },
    "HLOOKUP": {
        "description": "Sucht einen Wert in der ersten Zeile und gibt einen Wert aus derselben Spalte zurück",
        "syntax": "=HLOOKUP(Suchkriterium, Bereich, Zeilenindex, [Bereich_Verweis])",
        "example": "=HLOOKUP(A1, B1:J2, 2, FALSE) → Sucht A1 in B1:J1, gibt Wert aus Zeile 2 zurück",
        "category": "Lookup"
    },
    "INDEX": {
        "description": "Gibt einen Wert aus einem Bereich basierend auf Zeilen- und Spaltenindex zurück",
        "syntax": "=INDEX(Bereich, Zeile, [Spalte])",
        "example": "=INDEX(A1:C10, 5, 2) → Wert aus Zeile 5, Spalte 2 des Bereichs",
        "category": "Lookup"
    },
    "MATCH": {
        "description": "Gibt die Position eines Werts in einem Bereich zurück",
        "syntax": "=MATCH(Suchkriterium, Suchbereich, [Vergleichstyp])",
        "example": "=MATCH(\"Apfel\", A1:A10, 0) → Position von 'Apfel' in A1:A10",
        "category": "Lookup"
    },
    
    # Datumsfunktionen
    "TODAY": {
        "description": "Gibt das heutige Datum zurück",
        "syntax": "=TODAY()",
        "example": "=TODAY() → Aktuelles Datum",
        "category": "Datum"
    },
    "DATE": {
        "description": "Erstellt ein Datum aus Jahr, Monat und Tag",
        "syntax": "=DATE(Jahr, Monat, Tag)",
        "example": "=DATE(2024, 12, 25) → 25.12.2024",
        "category": "Datum"
    },
    "YEAR": {
        "description": "Extrahiert das Jahr aus einem Datum",
        "syntax": "=YEAR(Datum)",
        "example": "=YEAR(TODAY()) → Aktuelles Jahr",
        "category": "Datum"
    },
    "MONTH": {
        "description": "Extrahiert den Monat aus einem Datum",
        "syntax": "=MONTH(Datum)",
        "example": "=MONTH(TODAY()) → Aktueller Monat",
        "category": "Datum"
    },
    "DAY": {
        "description": "Extrahiert den Tag aus einem Datum",
        "syntax": "=DAY(Datum)",
        "example": "=DAY(TODAY()) → Aktueller Tag",
        "category": "Datum"
    },
    
    # Textfunktionen
    "TEXT": {
        "description": "Formatiert eine Zahl als Text",
        "syntax": "=TEXT(Wert, Format)",
        "example": "=TEXT(1234.5, \"#,##0.00\") → \"1.234,50\"",
        "category": "Text"
    },
    "CONCATENATE": {
        "description": "Verbindet mehrere Texte zu einem",
        "syntax": "=CONCATENATE(Text1, [Text2], ...)",
        "example": "=CONCATENATE(A1, \" \", B1) → Verbindet A1 und B1 mit Leerzeichen",
        "category": "Text"
    },
    "LEFT": {
        "description": "Gibt die ersten Zeichen eines Textes zurück",
        "syntax": "=LEFT(Text, [Anzahl_Zeichen])",
        "example": "=LEFT(\"Hallo\", 3) → \"Hal\"",
        "category": "Text"
    },
    "RIGHT": {
        "description": "Gibt die letzten Zeichen eines Textes zurück",
        "syntax": "=RIGHT(Text, [Anzahl_Zeichen])",
        "example": "=RIGHT(\"Hallo\", 3) → \"llo\"",
        "category": "Text"
    },
    "MID": {
        "description": "Gibt Zeichen aus der Mitte eines Textes zurück",
        "syntax": "=MID(Text, Startposition, Anzahl_Zeichen)",
        "example": "=MID(\"Hallo\", 2, 3) → \"all\"",
        "category": "Text"
    },
    "LEN": {
        "description": "Gibt die Länge eines Textes zurück",
        "syntax": "=LEN(Text)",
        "example": "=LEN(\"Hallo\") → 5",
        "category": "Text"
    },
    "LOWER": {
        "description": "Konvertiert Text in Kleinbuchstaben",
        "syntax": "=LOWER(Text)",
        "example": "=LOWER(\"HALLO\") → \"hallo\"",
        "category": "Text"
    },
    "UPPER": {
        "description": "Konvertiert Text in Großbuchstaben",
        "syntax": "=UPPER(Text)",
        "example": "=UPPER(\"hallo\") → \"HALLO\"",
        "category": "Text"
    },
    "PROPER": {
        "description": "Konvertiert Text so dass jedes Wort mit Großbuchstaben beginnt",
        "syntax": "=PROPER(Text)",
        "example": "=PROPER(\"hallo welt\") → \"Hallo Welt\"",
        "category": "Text"
    },
    "TRIM": {
        "description": "Entfernt überflüssige Leerzeichen",
        "syntax": "=TRIM(Text)",
        "example": "=TRIM(\"  Hallo  Welt  \") → \"Hallo Welt\"",
        "category": "Text"
    },
    "FIND": {
        "description": "Findet einen Text in einem anderen Text (Groß-/Kleinschreibung beachten)",
        "syntax": "=FIND(Suchtext, Text, [Startposition])",
        "example": "=FIND(\"lo\", \"Hallo\") → 4",
        "category": "Text"
    },
    "SEARCH": {
        "description": "Findet einen Text (Groß-/Kleinschreibung ignorieren)",
        "syntax": "=SEARCH(Suchtext, Text, [Startposition])",
        "example": "=SEARCH(\"LO\", \"Hallo\") → 4",
        "category": "Text"
    },
    "SUBSTITUTE": {
        "description": "Ersetzt Text durch neuen Text",
        "syntax": "=SUBSTITUTE(Text, Alter_Text, Neuer_Text, [Vorkommen])",
        "example": "=SUBSTITUTE(\"Hallo Welt\", \"Welt\", \"Erde\") → \"Hallo Erde\"",
        "category": "Text"
    },
    "REPLACE": {
        "description": "Ersetzt Zeichen in einem Text",
        "syntax": "=REPLACE(Alter_Text, Startposition, Anzahl_Zeichen, Neuer_Text)",
        "example": "=REPLACE(\"Hallo\", 2, 2, \"i\") → \"Hilo\"",
        "category": "Text"
    },
    "TEXTJOIN": {
        "description": "Verbindet Text mit einem Trennzeichen",
        "syntax": "=TEXTJOIN(Trennzeichen, Leere_ignorieren, Text1, [Text2], ...)",
        "example": "=TEXTJOIN(\", \", TRUE, A1:A5) → Verbindet A1 bis A5 mit Komma",
        "category": "Text"
    },
    "EXACT": {
        "description": "Vergleicht zwei Texte (Groß-/Kleinschreibung beachten)",
        "syntax": "=EXACT(Text1, Text2)",
        "example": "=EXACT(\"Hallo\", \"hallo\") → FALSE",
        "category": "Text"
    },
    
    # Statistische Funktionen
    "MEDIAN": {
        "description": "Gibt den Median (mittleren Wert) zurück",
        "syntax": "=MEDIAN(Zahl1, [Zahl2], ...)",
        "example": "=MEDIAN(1, 2, 3, 4, 5) → 3",
        "category": "Statistik"
    },
    "MODE": {
        "description": "Gibt den häufigsten Wert zurück",
        "syntax": "=MODE(Zahl1, [Zahl2], ...)",
        "example": "=MODE(1, 2, 2, 3, 4) → 2",
        "category": "Statistik"
    },
    "STDEV": {
        "description": "Gibt die Standardabweichung zurück (Stichprobe)",
        "syntax": "=STDEV(Zahl1, [Zahl2], ...)",
        "example": "=STDEV(A1:A10) → Standardabweichung von A1 bis A10",
        "category": "Statistik"
    },
    "VAR": {
        "description": "Gibt die Varianz zurück (Stichprobe)",
        "syntax": "=VAR(Zahl1, [Zahl2], ...)",
        "example": "=VAR(A1:A10) → Varianz von A1 bis A10",
        "category": "Statistik"
    },
    "PERCENTILE": {
        "description": "Gibt das k-te Perzentil zurück",
        "syntax": "=PERCENTILE(Array, k)",
        "example": "=PERCENTILE(A1:A10, 0.75) → 75. Perzentil",
        "category": "Statistik"
    },
    "QUARTILE": {
        "description": "Gibt das Quartil zurück",
        "syntax": "=QUARTILE(Array, Quartil)",
        "example": "=QUARTILE(A1:A10, 1) → 1. Quartil (25%)",
        "category": "Statistik"
    },
    "RANK": {
        "description": "Gibt den Rang einer Zahl zurück",
        "syntax": "=RANK(Zahl, Bezug, [Reihenfolge])",
        "example": "=RANK(A1, A1:A10, 0) → Rang von A1 in absteigender Reihenfolge",
        "category": "Statistik"
    },
    "LARGE": {
        "description": "Gibt den k-größten Wert zurück",
        "syntax": "=LARGE(Array, k)",
        "example": "=LARGE(A1:A10, 2) → Zweitgrößter Wert",
        "category": "Statistik"
    },
    "SMALL": {
        "description": "Gibt den k-kleinsten Wert zurück",
        "syntax": "=SMALL(Array, k)",
        "example": "=SMALL(A1:A10, 2) → Zweitkleinster Wert",
        "category": "Statistik"
    },
    
    # Erweiterte IF-Funktionen
    "IFS": {
        "description": "Prüft mehrere Bedingungen und gibt den ersten wahren Wert zurück",
        "syntax": "=IFS(Bedingung1, Wert1, [Bedingung2, Wert2], ...)",
        "example": "=IFS(A1>90, \"A\", A1>80, \"B\", A1>70, \"C\") → Note basierend auf Punktzahl",
        "category": "Logik"
    },
    "SWITCH": {
        "description": "Vergleicht einen Ausdruck mit mehreren Werten",
        "syntax": "=SWITCH(Ausdruck, Wert1, Ergebnis1, [Wert2, Ergebnis2], ..., [Standard])",
        "example": "=SWITCH(A1, 1, \"Eins\", 2, \"Zwei\", \"Andere\") → Text basierend auf Zahl",
        "category": "Logik"
    },
    "CHOOSE": {
        "description": "Wählt einen Wert aus einer Liste basierend auf dem Index",
        "syntax": "=CHOOSE(Index, Wert1, [Wert2], ...)",
        "example": "=CHOOSE(2, \"A\", \"B\", \"C\") → \"B\"",
        "category": "Logik"
    },
    
    # Erweiterte Aggregationsfunktionen
    "AVERAGEIF": {
        "description": "Berechnet den Durchschnitt von Zellen die ein Kriterium erfüllen",
        "syntax": "=AVERAGEIF(Bereich, Kriterium, [Mittelwert_Bereich])",
        "example": "=AVERAGEIF(A1:A10, \">50\", B1:B10) → Durchschnitt von B wo A>50",
        "category": "Mathematik"
    },
    "AVERAGEIFS": {
        "description": "Berechnet den Durchschnitt mit mehreren Kriterien",
        "syntax": "=AVERAGEIFS(Mittelwert_Bereich, Kriterien_Bereich1, Kriterium1, ...)",
        "example": "=AVERAGEIFS(C1:C10, A1:A10, \">50\", B1:B10, \"<100\")",
        "category": "Mathematik"
    },
    "MAXIFS": {
        "description": "Gibt den Maximalwert mit mehreren Kriterien zurück",
        "syntax": "=MAXIFS(Max_Bereich, Kriterien_Bereich1, Kriterium1, ...)",
        "example": "=MAXIFS(C1:C10, A1:A10, \">50\", B1:B10, \"<100\")",
        "category": "Mathematik"
    },
    "MINIFS": {
        "description": "Gibt den Minimalwert mit mehreren Kriterien zurück",
        "syntax": "=MINIFS(Min_Bereich, Kriterien_Bereich1, Kriterium1, ...)",
        "example": "=MINIFS(C1:C10, A1:A10, \">50\", B1:B10, \"<100\")",
        "category": "Mathematik"
    },
    "COUNTIFS": {
        "description": "Zählt Zellen mit mehreren Kriterien",
        "syntax": "=COUNTIFS(Kriterien_Bereich1, Kriterium1, [Kriterien_Bereich2, Kriterium2], ...)",
        "example": "=COUNTIFS(A1:A10, \">50\", B1:B10, \"<100\")",
        "category": "Mathematik"
    },
    "COUNTBLANK": {
        "description": "Zählt leere Zellen",
        "syntax": "=COUNTBLANK(Bereich)",
        "example": "=COUNTBLANK(A1:A10) → Anzahl leerer Zellen",
        "category": "Mathematik"
    },
    
    # Mathematische Funktionen
    "ABS": {
        "description": "Gibt den Absolutwert einer Zahl zurück",
        "syntax": "=ABS(Zahl)",
        "example": "=ABS(-5) → 5",
        "category": "Mathematik"
    },
    "POWER": {
        "description": "Potenziert eine Zahl",
        "syntax": "=POWER(Zahl, Potenz)",
        "example": "=POWER(2, 3) → 8",
        "category": "Mathematik"
    },
    "SQRT": {
        "description": "Gibt die Quadratwurzel zurück",
        "syntax": "=SQRT(Zahl)",
        "example": "=SQRT(16) → 4",
        "category": "Mathematik"
    },
    "MOD": {
        "description": "Gibt den Rest einer Division zurück",
        "syntax": "=MOD(Zahl, Divisor)",
        "example": "=MOD(10, 3) → 1",
        "category": "Mathematik"
    },
    "PI": {
        "description": "Gibt die Zahl Pi zurück",
        "syntax": "=PI()",
        "example": "=PI() → 3.14159...",
        "category": "Mathematik"
    },
    "CEILING": {
        "description": "Rundet eine Zahl auf das nächste Vielfache auf",
        "syntax": "=CEILING(Zahl, Schritt)",
        "example": "=CEILING(4.3, 1) → 5",
        "category": "Mathematik"
    },
    "FLOOR": {
        "description": "Rundet eine Zahl auf das nächste Vielfache ab",
        "syntax": "=FLOOR(Zahl, Schritt)",
        "example": "=FLOOR(4.7, 1) → 4",
        "category": "Mathematik"
    },
    "INT": {
        "description": "Rundet eine Zahl auf die nächste ganze Zahl ab",
        "syntax": "=INT(Zahl)",
        "example": "=INT(4.7) → 4",
        "category": "Mathematik"
    },
    "SIGN": {
        "description": "Gibt das Vorzeichen einer Zahl zurück",
        "syntax": "=SIGN(Zahl)",
        "example": "=SIGN(-5) → -1",
        "category": "Mathematik"
    },
    "RAND": {
        "description": "Gibt eine Zufallszahl zwischen 0 und 1 zurück",
        "syntax": "=RAND()",
        "example": "=RAND() → 0.742...",
        "category": "Mathematik"
    },
    "RANDBETWEEN": {
        "description": "Gibt eine ganzzahlige Zufallszahl im angegebenen Bereich zurück",
        "syntax": "=RANDBETWEEN(Untere_Grenze, Obere_Grenze)",
        "example": "=RANDBETWEEN(1, 100) → Zufallszahl zwischen 1 und 100",
        "category": "Mathematik"
    },
    
    # Prüffunktionen
    "ISBLANK": {
        "description": "Prüft ob ein Wert leer ist",
        "syntax": "=ISBLANK(Wert)",
        "example": "=ISBLANK(A1) → TRUE wenn A1 leer",
        "category": "Information"
    },
    "ISNUMBER": {
        "description": "Prüft ob ein Wert eine Zahl ist",
        "syntax": "=ISNUMBER(Wert)",
        "example": "=ISNUMBER(A1) → TRUE wenn A1 eine Zahl ist",
        "category": "Information"
    },
    "ISTEXT": {
        "description": "Prüft ob ein Wert Text ist",
        "syntax": "=ISTEXT(Wert)",
        "example": "=ISTEXT(A1) → TRUE wenn A1 Text ist",
        "category": "Information"
    },
    "ISERROR": {
        "description": "Prüft ob ein Wert ein Fehler ist",
        "syntax": "=ISERROR(Wert)",
        "example": "=ISERROR(A1/B1) → TRUE bei Division durch Null",
        "category": "Information"
    },
    
    # Erweiterte Datumsfunktionen
    "NOW": {
        "description": "Gibt das aktuelle Datum und die aktuelle Uhrzeit zurück",
        "syntax": "=NOW()",
        "example": "=NOW() → Aktuelles Datum und Uhrzeit",
        "category": "Datum"
    },
    "WEEKDAY": {
        "description": "Gibt den Wochentag zurück",
        "syntax": "=WEEKDAY(Datum, [Typ])",
        "example": "=WEEKDAY(TODAY()) → Wochentag (1=Sonntag, 7=Samstag)",
        "category": "Datum"
    },
    "DATEDIF": {
        "description": "Berechnet die Differenz zwischen zwei Daten",
        "syntax": "=DATEDIF(Startdatum, Enddatum, Einheit)",
        "example": "=DATEDIF(A1, TODAY(), \"D\") → Tage seit A1",
        "category": "Datum"
    },
    "EDATE": {
        "description": "Gibt ein Datum zurück das eine bestimmte Anzahl Monate vor/nach liegt",
        "syntax": "=EDATE(Startdatum, Monate)",
        "example": "=EDATE(TODAY(), 3) → Datum in 3 Monaten",
        "category": "Datum"
    },
    "EOMONTH": {
        "description": "Gibt den letzten Tag des Monats zurück",
        "syntax": "=EOMONTH(Startdatum, Monate)",
        "example": "=EOMONTH(TODAY(), 0) → Letzter Tag des aktuellen Monats",
        "category": "Datum"
    },
    "NETWORKDAYS": {
        "description": "Berechnet die Anzahl der Arbeitstage zwischen zwei Daten",
        "syntax": "=NETWORKDAYS(Startdatum, Enddatum, [Feiertage])",
        "example": "=NETWORKDAYS(A1, B1) → Arbeitstage zwischen A1 und B1",
        "category": "Datum"
    }
}


# Fehler-Tooltips mit Lösungen
ERROR_TOOLTIPS = {
    "#ERROR!": {
        "title": "Allgemeiner Fehler",
        "description": "Die Formel enthält einen Syntaxfehler oder kann nicht ausgeführt werden.",
        "solutions": [
            "Überprüfen Sie die Formel-Syntax",
            "Stellen Sie sicher dass alle Klammern geschlossen sind",
            "Prüfen Sie ob alle Funktionsnamen korrekt geschrieben sind"
        ]
    },
    "#REF!": {
        "title": "Ungültige Zellreferenz",
        "description": "Die Formel verweist auf eine Zelle die nicht existiert.",
        "solutions": [
            "Überprüfen Sie alle Zellreferenzen in der Formel",
            "Stellen Sie sicher dass die referenzierten Zellen existieren",
            "Prüfen Sie ob Zeilen oder Spalten gelöscht wurden"
        ]
    },
    "#DIV/0!": {
        "title": "Division durch Null",
        "description": "Die Formel versucht durch Null zu teilen.",
        "solutions": [
            "Überprüfen Sie den Nenner der Division",
            "Verwenden Sie IFERROR um den Fehler abzufangen: =IFERROR(A1/B1, 0)",
            "Stellen Sie sicher dass der Nenner nicht leer oder Null ist"
        ]
    },
    "#CIRCULAR!": {
        "title": "Zirkelbezug",
        "description": "Die Formel verweist direkt oder indirekt auf sich selbst.",
        "solutions": [
            "Überprüfen Sie die Formel auf Selbstreferenzen",
            "Prüfen Sie ob andere Zellen auf diese Zelle verweisen",
            "Brechen Sie die Zirkelkette durch Ändern einer Formel"
        ]
    },
    "#NAME?": {
        "title": "Unbekannter Name",
        "description": "Excel erkennt einen Funktionsnamen oder Bereichsnamen nicht.",
        "solutions": [
            "Überprüfen Sie die Schreibweise der Funktion",
            "Stellen Sie sicher dass die Funktion unterstützt wird",
            "Verwenden Sie Anführungszeichen für Text: \"Text\" statt Text"
        ]
    },
    "#VALUE!": {
        "title": "Falscher Werttyp",
        "description": "Die Formel verwendet einen falschen Datentyp.",
        "solutions": [
            "Überprüfen Sie die Datentypen der Argumente",
            "Stellen Sie sicher dass Zahlen als Zahlen und nicht als Text eingegeben sind",
            "Prüfen Sie ob alle Funktionsargumente korrekt sind"
        ]
    }
}


# UI-Element Tooltips
UI_TOOLTIPS = {
    "neue_matrix": "Erstellt eine neue leere Matrix mit anpassbarer Größe",
    "speichern": "Speichert alle Änderungen in der Datenbank",
    "laden": "Lädt eine gespeicherte Matrix aus der Datenbank",
    "undo": "Macht die letzte Änderung rückgängig (Strg+Z)",
    "redo": "Wiederholt die letzte rückgängig gemachte Änderung (Strg+Y)",
    "auto_save": "Speichert Änderungen automatisch in regelmäßigen Abständen",
    "formeln_anzeigen": "Zeigt Formeln statt berechneter Werte in den Zellen",
    "kopieren": "Kopiert den Inhalt der aktiven Zelle (Strg+C)",
    "einfuegen": "Fügt den kopierten Inhalt in die aktive Zelle ein (Strg+V)",
    "zell_format": "Ändert die Formatierung der aktiven Zelle (Zahl, Währung, Prozent, etc.)",
    "tastatur_nav": "Aktiviert Navigation mit Pfeiltasten, Tab und Enter",
    "csv_import": "Importiert Daten aus einer CSV-Datei",
    "csv_export": "Exportiert die Matrix als CSV-Datei",
    "excel_export": "Exportiert die Matrix als Excel-Datei (XLSX) mit Formeln",
    "zeile_hinzufuegen": "Fügt eine neue Zeile an der angegebenen Position ein",
    "spalte_hinzufuegen": "Fügt eine neue Spalte an der angegebenen Position ein",
    "zeile_loeschen": "Löscht die angegebene Zeile und passt Formeln automatisch an",
    "spalte_loeschen": "Löscht die angegebene Spalte und passt Formeln automatisch an",
    "formelleiste": "Zeigt und bearbeitet die Formel oder den Wert der aktiven Zelle",
    "zelle_auswaehlen": "Springt zur angegebenen Zelle (z.B. A1, B5)"
}


def get_keyboard_shortcuts() -> Dict[str, Dict[str, str]]:
    """
    Gibt alle Tastatur-Shortcuts zurück
    
    Returns:
        Dictionary mit Kategorien und Shortcuts
    """
    return KEYBOARD_SHORTCUTS


def get_function_tooltip(function_name: str) -> Dict[str, str]:
    """
    Gibt den Tooltip für eine Funktion zurück
    
    Args:
        function_name: Name der Funktion (z.B. "SUM")
        
    Returns:
        Dictionary mit Tooltip-Informationen oder None
    """
    return FUNCTION_TOOLTIPS.get(function_name.upper())


def get_error_tooltip(error_code: str) -> Dict[str, Any]:
    """
    Gibt den Tooltip für einen Fehlercode zurück
    
    Args:
        error_code: Fehlercode (z.B. "#DIV/0!")
        
    Returns:
        Dictionary mit Fehlerinformationen oder None
    """
    return ERROR_TOOLTIPS.get(error_code)


def get_ui_tooltip(element_key: str) -> str:
    """
    Gibt den Tooltip für ein UI-Element zurück
    
    Args:
        element_key: Schlüssel des UI-Elements
        
    Returns:
        Tooltip-Text oder leerer String
    """
    return UI_TOOLTIPS.get(element_key, "")


def get_all_functions_by_category() -> Dict[str, List[Dict[str, str]]]:
    """
    Gibt alle Funktionen gruppiert nach Kategorie zurück
    
    Returns:
        Dictionary mit Kategorien und Funktionslisten
    """
    categories = {}
    
    for func_name, func_info in FUNCTION_TOOLTIPS.items():
        category = func_info.get("category", "Sonstige")
        
        if category not in categories:
            categories[category] = []
        
        categories[category].append({
            "name": func_name,
            **func_info
        })
    
    return categories


def format_function_help(function_name: str) -> str:
    """
    Formatiert die Hilfe für eine Funktion als Markdown
    
    Args:
        function_name: Name der Funktion
        
    Returns:
        Formatierter Hilfetext
    """
    tooltip = get_function_tooltip(function_name)
    
    if not tooltip:
        return f"Keine Hilfe für {function_name} verfügbar"
    
    help_text = f"""
**{function_name}**

{tooltip['description']}

**Syntax:** `{tooltip['syntax']}`

**Beispiel:** `{tooltip['example']}`

**Kategorie:** {tooltip['category']}
"""
    
    return help_text.strip()


def format_error_help(error_code: str) -> str:
    """
    Formatiert die Hilfe für einen Fehlercode als Markdown
    
    Args:
        error_code: Fehlercode
        
    Returns:
        Formatierter Hilfetext
    """
    tooltip = get_error_tooltip(error_code)
    
    if not tooltip:
        return f"Keine Hilfe für {error_code} verfügbar"
    
    help_text = f"""
**{tooltip['title']}** ({error_code})

{tooltip['description']}

**Lösungsvorschläge:**
"""
    
    for i, solution in enumerate(tooltip['solutions'], 1):
        help_text += f"\n{i}. {solution}"
    
    return help_text.strip()
