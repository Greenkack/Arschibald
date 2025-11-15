"""
Seed-Datenbank mit PV-Komponenten
==================================

Fügt Beispieldaten aus der Dokumentation in die Datenbank ein.

Autor: Bokuk2 System
Version: 1.0.0
Datum: 2025-11-06
"""

from pv_mounting_database import create_component, get_statistics
import json


def seed_database():
    """Fügt Beispielkomponenten in die Datenbank ein."""
    
    components = [
        # ==================== K2 Systems - Ziegeldach ====================
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'SingleHook 4S Dachhaken',
            'article_number': '2003144',
            'category': 'Dachhaken',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium EN AW 6063-T66',
            'dimensions': '40/47/54 mm verstellbar',
            'weight_kg': 0.45,
            'price_netto': 9.0,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Für Tonziegel, 3-fach höhenverstellbar',
            'warranty_years': 12,
            'specifications': {
                'height_adjustment': '120-165 mm',
                'rafter_width_min': '48 mm',
                'material_standard': 'EN AW 6063 T66'
            },
            'notes': 'Universeller Dachhaken für Tonziegel mit SingleRail System'
        },
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'SingleRail 36 Montageschiene',
            'article_number': '2004260',
            'category': 'Montageschiene',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium EN AW-6063 T6',
            'dimensions': '36×37 mm, 3,65 m',
            'weight_kg': 1.2,
            'price_netto': 5.0,
            'unit': 'm',
            'quantity_per_module': 1.2,
            'compatibility': 'SingleRail System, seitliche Schienenanbindung',
            'warranty_years': 12,
            'specifications': {
                'profile_size': '36×37 mm',
                'standard_length': '3,65 m',
                'load_capacity': 'Standard'
            },
            'notes': 'Aluminium-Profil für einlagige Montage'
        },
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'Universal End Clamp Endklemme',
            'category': 'Modulklemme (End)',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium (blank/schwarz eloxiert)',
            'dimensions': '30-40 mm Klemmbreite',
            'weight_kg': 0.08,
            'price_netto': 1.5,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Mit Erdungspins, klemmbar 30-47 mm Rahmenhöhe',
            'warranty_years': 12,
            'specifications': {
                'clamp_range': '30-40 mm',
                'grounding': 'Integrated pins'
            },
            'notes': 'Universalklemme mit integriertem Erdungs-Pin'
        },
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'Universal Middle Clamp Mittelklemme',
            'category': 'Modulklemme (Mittel)',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium (blank/schwarz)',
            'dimensions': '30-40 mm',
            'weight_kg': 0.08,
            'price_netto': 1.5,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Moduldicken 30-47 mm, one-turn clamp',
            'warranty_years': 12,
            'specifications': {
                'clamp_range': '30-47 mm',
                'type': 'One-turn clamp'
            },
            'notes': 'Funktioniert als Mittel- oder Endklemme'
        },
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'Holzschrauben 8×80 mm',
            'category': 'Schrauben',
            'roof_type': 'Ziegeldach',
            'material': 'Edelstahl A2',
            'dimensions': '8×80 mm',
            'weight_kg': 0.02,
            'price_netto': 0.5,
            'unit': 'Stk',
            'quantity_per_module': 4.0,
            'compatibility': 'ASSY Tellerkopf VA-Schraube, ohne Vorbohren',
            'specifications': {
                'diameter': '8 mm',
                'length': '80 mm',
                'head_type': 'Tellerkopf',
                'drive': 'T-40'
            },
            'notes': 'Für Sparrenbefestigung der Dachhaken'
        },
        
        # ==================== Würth - Ziegeldach ====================
        {
            'manufacturer': 'Würth',
            'product_name': 'Dachhaken PLUS Aluminium 3-fach verstellbar',
            'article_number': '0865 994 8',
            'category': 'Dachhaken',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium EN AW-6082 T6',
            'dimensions': '3-fach Versatzstufen',
            'weight_kg': 0.40,
            'price_netto': 10.5,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Für Tonziegel, Grundplatte mit drei Versatzstufen',
            'warranty_years': 10,
            'specifications': {
                'adjustment_steps': 3,
                'material_standard': 'EN AW-6082 T6'
            },
            'notes': 'Leichter Alu-Haken mit Schnellmontageadapter'
        },
        {
            'manufacturer': 'Würth',
            'product_name': 'Montageschiene Plus 37',
            'article_number': '0865 750 037',
            'category': 'Montageschiene',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium',
            'dimensions': '37 mm hoch, 25 mm breit',
            'weight_kg': 1.0,
            'price_netto': 5.5,
            'unit': 'm',
            'quantity_per_module': 1.2,
            'compatibility': 'Plus 37 Serie, 3,6m und 4,8m Längen',
            'warranty_years': 10,
            'specifications': {
                'height': '37 mm',
                'width': '25 mm',
                'lengths_available': ['3,6 m', '4,8 m']
            },
            'notes': 'Standard-Profil für normale Lasten'
        },
        {
            'manufacturer': 'Würth',
            'product_name': 'Mittelklemme Comfort',
            'article_number': '0865 799 905',
            'category': 'Modulklemme (Mittel)',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium blank/schwarz',
            'dimensions': 'Höhe einstellbar',
            'weight_kg': 0.07,
            'price_netto': 1.8,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Mit innenliegender Feder, Innen-Klick-System',
            'warranty_years': 10,
            'specifications': {
                'mounting_system': 'Inner click system',
                'spring': 'Internal'
            },
            'notes': 'Schnellmontage durch Klick-System'
        },
        {
            'manufacturer': 'Würth',
            'product_name': 'Endklemme Comfort 30 mm',
            'article_number': '0865 799 913',
            'category': 'Modulklemme (End)',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium blank/schwarz',
            'dimensions': '30 mm',
            'weight_kg': 0.07,
            'price_netto': 1.8,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Comfort Serie, 30-50 mm Varianten',
            'warranty_years': 10,
            'notes': 'Endklemme mit Klick-Montage'
        },
        
        # ==================== K2 Systems - Betondach ====================
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'SingleHook 2 Edelstahl Dachhaken',
            'article_number': '2003175',
            'category': 'Dachhaken',
            'roof_type': 'Betondach',
            'material': 'Edelstahl V2A',
            'dimensions': 'Für Betondachsteine EN 490',
            'weight_kg': 0.65,
            'price_netto': 12.0,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Für flache Betondachsteine, vormontierter Adapter',
            'warranty_years': 12,
            'specifications': {
                'material': 'V2A Stainless Steel',
                'max_rafter_spacing': '1,0 m',
                'standard': 'EN 490'
            },
            'notes': 'Verstärkter Haken für Betondachsteine'
        },
        
        # ==================== Würth - Schiefer/Biberschwanz ====================
        {
            'manufacturer': 'Würth',
            'product_name': 'Dachhaken PLUS Schiefer Edelstahl',
            'article_number': '0865 900 014',
            'category': 'Dachhaken',
            'roof_type': 'Schieferdach',
            'material': 'Edelstahl A2',
            'dimensions': '235×30 mm Grundplatte',
            'weight_kg': 0.55,
            'price_netto': 20.0,
            'unit': 'Stk',
            'quantity_per_module': 2.5,
            'compatibility': 'Lange schmale Grundplatte, mit Schnellmontageadapter',
            'warranty_years': 10,
            'specifications': {
                'plate_size': '235×30 mm',
                'material_grade': 'A2'
            },
            'notes': 'Speziell für Schieferdächer, erfordert Abdichtung'
        },
        {
            'manufacturer': 'Würth',
            'product_name': 'Dachhaken PLUS Biberschwanz',
            'article_number': '0865 900 015',
            'category': 'Dachhaken',
            'roof_type': 'Biberschwanzdach',
            'material': 'Edelstahl',
            'dimensions': '305×30 mm Grundplatte',
            'weight_kg': 0.60,
            'price_netto': 20.0,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Für Biberschwanz-Doppeldeckungen',
            'warranty_years': 10,
            'specifications': {
                'plate_size': '305×30 mm'
            },
            'notes': 'Für flache überlappende Ziegel'
        },
        
        # ==================== Würth - Trapezblech ====================
        {
            'manufacturer': 'Würth',
            'product_name': 'Trapezblechschiene HK PLUS 400 mm',
            'article_number': '0865 750 021',
            'category': 'Trapezblechschiene',
            'roof_type': 'Blechdach (Trapezblech)',
            'material': 'Aluminium mit EPDM-Dichtung',
            'dimensions': '400 mm Länge',
            'weight_kg': 0.25,
            'price_netto': 4.0,
            'unit': 'Stk',
            'quantity_per_module': 4.0,
            'compatibility': 'HK PLUS für direkte Montage in Hochsicke, Dachneigung 5-25°',
            'warranty_years': 10,
            'specifications': {
                'length': '400 mm',
                'pitch_range': '5-25°',
                'sealing': 'EPDM integrated'
            },
            'notes': 'Mit integrierter EPDM-Abdichtung'
        },
        {
            'manufacturer': 'Würth',
            'product_name': 'Dünnblechschraube DBS 6,0×25 mm',
            'category': 'Schrauben',
            'roof_type': 'Blechdach (Trapezblech)',
            'material': 'Edelstahl mit Dichtung',
            'dimensions': '6,0×25 mm',
            'weight_kg': 0.01,
            'price_netto': 0.20,
            'unit': 'Stk',
            'quantity_per_module': 8.0,
            'compatibility': 'Selbstschneidend, für Stahlblech bis 0,7mm, Alublech <0,8mm',
            'specifications': {
                'diameter': '6,0 mm',
                'length': '25 mm',
                'tip_type': 'Self-drilling, chipless'
            },
            'notes': 'Spezialspitze erzeugt keine Späne'
        },
        
        # ==================== K2 Systems - Flachdach ====================
        {
            'manufacturer': 'K2 Systems',
            'product_name': 'MiniRail Kurzschiene',
            'category': 'Trapezblechschiene',
            'roof_type': 'Flachdach',
            'material': 'Aluminium',
            'dimensions': '~39 cm mit EPDM',
            'weight_kg': 0.20,
            'price_netto': 10.0,
            'unit': 'Stk',
            'quantity_per_module': 4.0,
            'compatibility': 'Für Trapezblech und Flachdach, mit Dichtstreifen',
            'warranty_years': 12,
            'specifications': {
                'length': '~390 mm',
                'sealing': 'EPDM strip'
            },
            'notes': 'Kurzschienenkonzept für ballastfreie Montage'
        },
        
        # ==================== Renusol - Universal ====================
        {
            'manufacturer': 'Renusol',
            'product_name': 'Dachhaken Standard Alu',
            'article_number': '420170',
            'category': 'Dachhaken',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium',
            'dimensions': '2-fach verstellbar',
            'weight_kg': 0.42,
            'price_netto': 10.0,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'VS+ System, für Pfannenziegel',
            'warranty_years': 10,
            'specifications': {
                'adjustment': 'Height and side adjustable',
                'system': 'VarioSole+ (VS+)'
            },
            'notes': 'Universalhaken für VarioSole+ System'
        },
        {
            'manufacturer': 'Renusol',
            'product_name': 'Dachhaken Schiefer Edelstahl',
            'article_number': '420155',
            'category': 'Dachhaken',
            'roof_type': 'Schieferdach',
            'material': 'Edelstahl',
            'dimensions': '250×30 mm Grundplatte',
            'weight_kg': 0.53,
            'price_netto': 22.0,
            'unit': 'Stk',
            'quantity_per_module': 2.5,
            'compatibility': 'Lange Grundplatte für Schiefer, vormontiert',
            'warranty_years': 10,
            'specifications': {
                'plate_size': '250×30 mm',
                'weight': '0,53 kg'
            },
            'notes': 'Ohne Schrauben, 6mm VA-Schrauben empfohlen'
        },
        {
            'manufacturer': 'Renusol',
            'product_name': 'RS1 Rail Montageschiene 50×37 mm',
            'category': 'Montageschiene',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium',
            'dimensions': '50×37 mm, 3,6 m',
            'weight_kg': 1.3,
            'price_netto': 5.0,
            'unit': 'm',
            'quantity_per_module': 1.2,
            'compatibility': 'RS1 Rail für mittlere Last',
            'warranty_years': 10,
            'specifications': {
                'profile_size': '50×37 mm',
                'load_rating': 'Medium',
                'standard_length': '3,6 m'
            },
            'notes': 'Standard-Profil für VS+ System'
        },
        
        # ==================== Schletter - Ziegeldach ====================
        {
            'manufacturer': 'Schletter',
            'product_name': 'Rapid2+ Pro Dachhaken',
            'article_number': '100004-000',
            'category': 'Dachhaken',
            'roof_type': 'Ziegeldach',
            'material': 'Alu-Grundplatte, Edelstahl-Bügel',
            'dimensions': 'Verstellbar, Höhe + Seite',
            'weight_kg': 0.85,
            'price_netto': 11.0,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Rapid2+ System, universell für Ziegel',
            'warranty_years': 25,
            'specifications': {
                'adjustment': 'Height and lateral',
                'load_zone': 'High'
            },
            'notes': '25 Jahre Garantie, vormontierter Adapter'
        },
        {
            'manufacturer': 'Schletter',
            'product_name': 'Solo Profil 40×40 mm',
            'category': 'Montageschiene',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium',
            'dimensions': '40×40 mm',
            'weight_kg': 1.4,
            'price_netto': 4.5,
            'unit': 'm',
            'quantity_per_module': 1.2,
            'compatibility': 'Standard-Profil, Längen 1,18m / 2,10m / 3,15m / 4,75m',
            'warranty_years': 25,
            'specifications': {
                'profile_size': '40×40 mm',
                'lengths_available': ['1,18 m', '2,10 m', '3,15 m', '4,75 m']
            },
            'notes': 'Schletter Standardprofil mit Verbindern'
        },
        {
            'manufacturer': 'Schletter',
            'product_name': 'RapidPro Universalklemme',
            'category': 'Modulklemme (Mittel)',
            'roof_type': 'Ziegeldach',
            'material': 'Aluminium EN AW 6063-T66',
            'dimensions': 'Rahmen 30-47 mm, Länge 50 mm',
            'weight_kg': 0.08,
            'price_netto': 1.8,
            'unit': 'Stk',
            'quantity_per_module': 2.0,
            'compatibility': 'Mit integriertem Erdungsstift, vormontiert',
            'warranty_years': 25,
            'specifications': {
                'frame_range': '30-47 mm',
                'clamp_length': '50 mm',
                'grounding': 'Integrated pin'
            },
            'notes': 'Neue Generation RapidPro, ein Torx-Schlüssel'
        },
        
        # ==================== Kabel ====================
        {
            'manufacturer': 'Standard',
            'product_name': 'Solarkabel 4mm² Rot',
            'category': 'Kabel',
            'roof_type': 'Ziegeldach',
            'material': 'Kupfer',
            'dimensions': '4 mm²',
            'weight_kg': 0.05,
            'price_netto': 1.2,
            'unit': 'm',
            'quantity_per_module': 1.0,
            'compatibility': 'UV-beständig, halogenfrei, 90°C Dauertemperatur',
            'specifications': {
                'cross_section': '4 mm²',
                'color': 'Red',
                'temperature_rating': '90°C',
                'uv_resistant': True
            },
            'notes': 'Standard-Solarkabel für DC-Verkabelung'
        },
        {
            'manufacturer': 'Standard',
            'product_name': 'Solarkabel 4mm² Schwarz',
            'category': 'Kabel',
            'roof_type': 'Ziegeldach',
            'material': 'Kupfer',
            'dimensions': '4 mm²',
            'weight_kg': 0.05,
            'price_netto': 1.2,
            'unit': 'm',
            'quantity_per_module': 1.0,
            'compatibility': 'UV-beständig, halogenfrei, 90°C Dauertemperatur',
            'specifications': {
                'cross_section': '4 mm²',
                'color': 'Black',
                'temperature_rating': '90°C',
                'uv_resistant': True
            },
            'notes': 'Standard-Solarkabel für DC-Verkabelung'
        },
        {
            'manufacturer': 'Standard',
            'product_name': 'Solarkabel 6mm² Rot',
            'category': 'Kabel',
            'roof_type': 'Ziegeldach',
            'material': 'Kupfer',
            'dimensions': '6 mm²',
            'weight_kg': 0.07,
            'price_netto': 1.8,
            'unit': 'm',
            'quantity_per_module': 1.0,
            'compatibility': 'Für höhere Ströme oder längere Wege',
            'specifications': {
                'cross_section': '6 mm²',
                'color': 'Red',
                'temperature_rating': '90°C',
                'uv_resistant': True
            },
            'notes': 'Für größere Anlagen ab 15 kWp'
        },
        {
            'manufacturer': 'Standard',
            'product_name': 'Solarkabel 6mm² Schwarz',
            'category': 'Kabel',
            'roof_type': 'Ziegeldach',
            'material': 'Kupfer',
            'dimensions': '6 mm²',
            'weight_kg': 0.07,
            'price_netto': 1.8,
            'unit': 'm',
            'quantity_per_module': 1.0,
            'compatibility': 'Für höhere Ströme oder längere Wege',
            'specifications': {
                'cross_section': '6 mm²',
                'color': 'Black',
                'temperature_rating': '90°C',
                'uv_resistant': True
            },
            'notes': 'Für größere Anlagen ab 15 kWp'
        }
    ]
    
    print("Seeding PV-Komponenten-Datenbank...")
    print(f"{len(components)} Komponenten werden eingefügt...\n")
    
    success_count = 0
    error_count = 0
    
    for comp in components:
        try:
            comp_id = create_component(comp)
            print(f"#{comp_id}: {comp['manufacturer']} - {comp['product_name']}")
            success_count += 1
        except Exception as e:
            print(f"Fehler: {comp['manufacturer']} - {comp['product_name']}: {e}")
            error_count += 1
    
    print(f"\n🎉 Seeding abgeschlossen!")
    print(f"Erfolgreich: {success_count}")
    print(f"Fehler: {error_count}")
    
    # Statistiken anzeigen
    print("\nDatenbank-Statistiken:")
    stats = get_statistics()
    print(f"Gesamt Komponenten: {stats['total_components']}")
    print(f"\nNach Hersteller:")
    for item in stats['by_manufacturer']:
        print(f"  - {item['manufacturer']}: {item['count']}")
    print(f"\nNach Kategorie:")
    for item in stats['by_category']:
        print(f"  - {item['category']}: {item['count']}")


if __name__ == "__main__":
    seed_database()
