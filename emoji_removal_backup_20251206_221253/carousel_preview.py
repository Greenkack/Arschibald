"""
Visual Preview: Admin Carousel Design
ASCII-Art Vorschau des neuen Karussell-Designs
"""

print("\n" + "=" * 80)
print(" " * 20 + "ADMIN-KARUSSELL DESIGN PREVIEW")
print("=" * 80 + "\n")

# Gradient Background
print("╔" + "═" * 78 + "╗")
print("║" + " " * 15 + "🌈 GRADIENT BACKGROUND: Purple → Violet" + " " * 22 + "║")
print("╠" + "═" * 78 + "╣")

# Navigation Header
print("║" + " " * 78 + "║")
print("║" + " " * 20 + "ADMINBEREICH NAVIGATION" + " " * 31 + "║")
print(
    "║" +
    " " *
    10 +
    "Navigieren Sie mit den Pfeiltasten oder klicken Sie direkt" +
    " " *
    9 +
    "║")
print("║" + " " * 78 + "║")
print("╠" + "═" * 78 + "╣")

# Carousel Container
print("║" + " " * 78 + "║")

# Navigation Row
print(
    "║" +
    " " *
    6 +
    "┌──────┐" +
    " " *
    20 +
    "┌──────┐" +
    " " *
    20 +
    "┌──────┐" +
    " " *
    6 +
    "║")
print(
    "║" +
    " " *
    6 +
    "│      │" +
    " " *
    20 +
    "│      │" +
    " " *
    20 +
    "│      │" +
    " " *
    6 +
    "║")
print("║  ◄   │  ◄   │" + " " * 20 + "│CARDS │" + " " * 20 + "│  ►   │   ►  ║")
print(
    "║" +
    " " *
    6 +
    "│      │" +
    " " *
    20 +
    "│      │" +
    " " *
    20 +
    "│      │" +
    " " *
    6 +
    "║")
print(
    "║" +
    " " *
    6 +
    "└──────┘" +
    " " *
    20 +
    "└──────┘" +
    " " *
    20 +
    "└──────┘" +
    " " *
    6 +
    "║")

print("║" + " " * 78 + "║")
print(
    "║" +
    " " *
    3 +
    "┌" +
    "─" *
    17 +
    "┐  ┌" +
    "─" *
    17 +
    "┐  ┌" +
    "─" *
    17 +
    "┐" +
    " " *
    3 +
    "║")

# Card 1 - Inactive
print(
    "║" +
    " " *
    3 +
    "│                 │  │                 │  │                 │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│       🏢       │  │       👥       │  │       │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│                 │  │                 │  │                 │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│ Unternehmens-   │  │  Benutzer-     │  │  Produkt-      │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│  verwaltung     │  │  verwaltung    │  │  verwaltung    │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│                 │  │                 │  │                 │" +
    " " *
    3 +
    "║")

# Highlight Active Card (Card 2 - User Management)
print(
    "║" +
    " " *
    3 +
    "│   [Inactive]    │  │  ⭐ AKTIV ⭐  │  │   [Inactive]   │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "│                 │  │                 │  │                 │" +
    " " *
    3 +
    "║")
print(
    "║" +
    " " *
    3 +
    "└" +
    "─" *
    17 +
    "┘  └" +
    "─" *
    17 +
    "┘  └" +
    "─" *
    17 +
    "┘" +
    " " *
    3 +
    "║")

print("║" + " " * 78 + "║")

# Indicator Dots
print("║" + " " * 26 + "⚪ ◼️ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪ ⚪" + " " * 11 + "║")
print("║" + " " * 31 + "↑ Position 2 von 13" + " " * 28 + "║")

print("║" + " " * 78 + "║")
print("╚" + "═" * 78 + "╝")

print("\n" + "-" * 80)
print("VISUELLE EFFEKTE:")
print("-" * 80)
print()
print("  Inactive Card:              Active Card:")
print("  ┌─────────────┐             ┌─────────────┐")
print("  │ White BG    │             │ Gradient BG │")
print("  │ Gray Text   │             │ White Text  │")
print("  │ Scale: 1.0  │             │ Scale: 1.08 │")
print("  │ No Pulse    │             │ Icon Pulse  │")
print("  └─────────────┘             └─────────────┘")
print()
print("  Hover Effect:               Shimmer Effect:")
print("  • Float up 8px              • Light stripe")
print("  • Scale to 1.02             • Moves L→R")
print("  • Icon rotate 5°            • 0.5s duration")
print("  • Shadow increase           • On hover only")

print("\n" + "-" * 80)
print("🖱️ INTERAKTION:")
print("-" * 80)
print()
print("  [◄ Button]  → Vorheriger Tab (wrap-around)")
print("  [► Button]  → Nächster Tab (wrap-around)")
print("  [Card]      → Direkt zu diesem Tab springen")
print("  [Dot]       → (Optional) Direkt zu Position")

print("\n" + "-" * 80)
print("ALLE 13 ADMIN-BEREICHE:")
print("-" * 80)
print()

areas = [
    ("🏢", "Unternehmensverwaltung", "Position 1"),
    ("👥", "Benutzerverwaltung", "Position 2 ⭐ AKTIV"),
    ("", "Produktverwaltung", "Position 3"),
    ("", "Logo-Management", "Position 4"),
    ("🗄️", "Produktdatenbank", "Position 5"),
    ("🛠️", "Services-Management", "Position 6"),
    ("⚙️", "Allgemeine Einstellungen", "Position 7"),
    ("🖼️", "Intro-Einstellungen", "Position 8"),
    ("", "Tarifverwaltung", "Position 9"),
    ("", "PDF-Design", "Position 10"),
    ("💳", "Zahlungsmodalitäten", "Position 11"),
    ("", "Visualisierung", "Position 12"),
    ("", "Erweitert", "Position 13"),
]

for icon, name, pos in areas:
    marker = " ◄" if "AKTIV" in pos else ""
    print(f"  {icon}  {name:<30} {pos}{marker}")

print("\n" + "=" * 80)
print(" " * 25 + "✨ MODERNES ADMIN-KARUSSELL ✨")
print("=" * 80)
print()
