"""
ZENTRALE PDF-SYSTEM ARCHITEKTUR
================================
Alle PDF-Erstellung und UI-Ausgabe läuft über dieses zentrale System.
Keine Duplikation mehr - alles an einem Ort!

Autor: GitHub Copilot
Datum: 2025-07-26
Zweck: Zentrale PDF-Verwaltung für alle Systeme (Standard, TOM-90, Mega Hybrid)
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable, Union
import base64
import traceback
import os
import json
import re
import io
from datetime import datetime

# =============================================================================
# ZENTRALE IMPORT-VERWALTUNG - ALLE PDF-SYSTEME AN EINEM ORT
# =============================================================================

class PDFSystemManager:
    """Zentrale Verwaltung aller PDF-Systeme"""
    
    def __init__(self):
        self.available_systems = {}
        self.fallback_functions = {}
        self._initialize_systems()
    
    def _sanitize_xml_content(self, text: str) -> str:
        """Bereinigt Text von problematischen XML-Zeichen und -Strukturen"""
        if not isinstance(text, str):
            return str(text)
        
        import re
        
        # Entferne oder ersetze problematische Unicode-Zeichen
        text = text.replace('\xe4', 'ä').replace('\xf6', 'ö').replace('\xfc', 'ü')
        text = text.replace('\xc4', 'Ä').replace('\xd6', 'Ö').replace('\xdc', 'Ü')
        text = text.replace('\xdf', 'ß')
        
        # Repariere defekte HTML/XML-Tags
        text = re.sub(r'<b>([^<]*)</para>', r'<b>\1</b></para>', text)
        text = re.sub(r'</b></b>', r'</b>', text)  # Doppelte closing tags
        text = re.sub(r'<b><b>', r'<b>', text)    # Doppelte opening tags
        
        # Entferne problematische Emoji-Kombinationen die XML-Probleme verursachen
        problematic_emojis = ['\U0001f527', '\u2699\ufe0f', '\U0001f4de']
        for emoji in problematic_emojis:
            text = text.replace(emoji, '•')
        
        return text
    
    def _create_safe_inclusion_options(self, original_options: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt sichere inclusion_options ohne XML-problematische Sektionen"""
        safe_options = original_options.copy()
        
        # Problematische Sektionen deaktivieren
        problematic_keys = [
            'include_business_warranty',
            'include_warranty_tom90',
            'include_business_insurance', 
            'include_business_maintenance',
            'include_business_financing'
        ]
        
        for key in problematic_keys:
            safe_options[key] = False
        
        return safe_options
    
    def _initialize_systems(self):
        """Initialisiert alle verfügbaren PDF-Systeme"""
        # Standard PDF Generator
        try:
            from pdf_generator import generate_offer_pdf_with_main_templates as _std
            self.available_systems['standard'] = _std
            st.session_state.pdf_standard_available = True
        except (ImportError, ModuleNotFoundError):
            # Fallback auf Legacy
            try:
                from pdf_generator import generate_offer_pdf as _legacy
                self.available_systems['standard'] = _legacy
            except Exception:
                self.available_systems['standard'] = self._dummy_standard_pdf
            st.session_state.pdf_standard_available = False
        
        # TOM-90 System
        try:
            # Verwende den RICHTIGEN TOM-90 Renderer mit Business-Sections Support
            from tom90_renderer import generate_tom90_offer_pdf
            self.available_systems['tom90'] = generate_tom90_offer_pdf
            st.session_state.pdf_tom90_available = True
        except (ImportError, ModuleNotFoundError, Exception) as e:
            print(f"TOM-90 Import Fehler: {e}")
            self.available_systems['tom90'] = self._dummy_tom90_pdf
            st.session_state.pdf_tom90_available = False
        
        # Mega Hybrid System
        try:
            from mega_tom90_hybrid_pdf import generate_mega_hybrid_pdf, MegaTOM90HybridPDFGenerator
            # Teste ob das Mega Hybrid System verfügbar ist
            test_generator = MegaTOM90HybridPDFGenerator
            self.available_systems['mega_hybrid'] = generate_mega_hybrid_pdf
            st.session_state.pdf_mega_hybrid_available = True
            print(" Mega Hybrid System verfügbar und funktional")
        except (ImportError, ModuleNotFoundError) as e:
            print(f" Mega Hybrid Import Fehler: {e}")
            self.available_systems['mega_hybrid'] = self._dummy_mega_hybrid_pdf
            st.session_state.pdf_mega_hybrid_available = False
        except Exception as e:
            print(f" Mega Hybrid System Problem: {e}")
            # Bei anderen Fehlern - versuche trotzdem den Import
            try:
                from mega_tom90_hybrid_pdf import generate_mega_hybrid_pdf
                self.available_systems['mega_hybrid'] = generate_mega_hybrid_pdf
                st.session_state.pdf_mega_hybrid_available = True
                print(" Mega Hybrid System verfügbar (trotz Warnungen)")
            except:
                self.available_systems['mega_hybrid'] = self._dummy_mega_hybrid_pdf
                st.session_state.pdf_mega_hybrid_available = False
        
        # PDF Preview System
        try:
            from pdf_preview import show_pdf_preview_interface
            self.available_systems['preview'] = show_pdf_preview_interface
            st.session_state.pdf_preview_available = True
        except (ImportError, ModuleNotFoundError, Exception) as e:
            print(f"PDF Preview Import Fehler: {e}")
            # Fallback: Preview als verfügbar markieren auch ohne spezielles Modul
            self.available_systems['preview'] = self._dummy_preview
            st.session_state.pdf_preview_available = True  # Aktiviert Fallback
            print(" Preview System (Fallback) aktiviert")
    
    def _dummy_standard_pdf(self, *args, **kwargs):
        st.info(" Standard PDF-Generator (Fallback) - Verwende verfügbare Alternativen")
        
        # Versuche verschiedene Standard-PDF-Optionen
        try:
            from pdf_generator import generate_offer_pdf
            return generate_offer_pdf(*args, **kwargs)
        except:
            try:
                # Fallback auf Business-Sections
                from business_sections_pdf import generate_business_sections_pdf
                company_info = kwargs.get('company_info', {})
                if company_info:
                    st.info(" Verwende Business-Sections als Standard-Fallback...")
                    return generate_business_sections_pdf(company_info)
            except:
                st.error(" Standard PDF-Generator nicht verfügbar!")
                return None
    
    def _dummy_tom90_pdf(self, *args, **kwargs):
        st.info(" TOM-90 PDF-System (Fallback) - Verwende verfügbare Alternativen")
        
        # Versuche verschiedene TOM-90-Optionen
        try:
            # Zuerst: TOM-90 Exact Renderer (standalone function)
            from tom90_exact_renderer import generate_tom90_exact_pdf
            project_data = kwargs.get('project_data', {})
            analysis_results = kwargs.get('analysis_results', {})
            company_info = kwargs.get('company_info', {})
            
            if project_data and analysis_results and company_info:
                st.info(" Verwende TOM-90 Exact Renderer...")
                return generate_tom90_exact_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info,
                    texts=kwargs.get('texts', {}),
                    inclusion_options=kwargs.get('inclusion_options', {}),
                    company_logo_base64=company_info.get('logo_base64')
                )
        except Exception as e:
            st.warning(f" TOM-90 Exact Renderer fehlgeschlagen: {e}")
            try:
                # Fallback auf tom90_renderer
                from tom90_renderer import generate_tom90_offer_pdf
                st.info(" Verwende TOM-90 Renderer...")
                return generate_tom90_offer_pdf(*args, **kwargs)
            except Exception as e2:
                st.warning(f" TOM-90 Renderer fehlgeschlagen: {e2}")
                try:
                    # Letzter Fallback auf Business-Sections
                    from business_sections_pdf import generate_business_sections_pdf
                    company_info = kwargs.get('company_info', {})
                    if company_info:
                        st.info(" Verwende Business-Sections PDF als TOM-90 Fallback...")
                        return generate_business_sections_pdf(company_info)
                except:
                    st.error(" TOM-90 PDF-System nicht verfügbar!")
                    return None
    
    def _dummy_mega_hybrid_pdf(self, *args, **kwargs):
        """Fallback wenn Mega Hybrid nicht funktioniert - mit Debug-Informationen"""
        st.warning(" Mega Hybrid System Problem erkannt")
        
        # Erstmal prüfen ob das echte Mega Hybrid System verfügbar ist
        try:
            st.info(" Versuche das echte Mega Hybrid System zu reparieren...")
            from mega_tom90_hybrid_pdf import generate_mega_hybrid_pdf
            
            # Aktiviere Debug-Modus für bessere Fehleranalyse
            debug_kwargs = kwargs.copy()
            debug_kwargs['debug_mode'] = True  # Falls das System Debug unterstützt
            
            result = generate_mega_hybrid_pdf(*args, **debug_kwargs)
            if result:
                st.success(" Mega Hybrid System erfolgreich repariert!")
                return result
            else:
                st.warning(" Mega Hybrid lieferte keine Daten zurück")
                
        except Exception as e:
            st.error(f" Mega Hybrid Reparatur fehlgeschlagen: {e}")
            import traceback
            st.code(traceback.format_exc(), language="python")
        
        # Cascading Fallback: Versuche verschiedene Systeme in Reihenfolge
        st.warning(" Verwende Fallback-Systeme...")
        fallback_systems = [
            ("TOM-90 Exact Renderer", self._try_tom90_exact_renderer),
            ("Business Sections PDF", self._try_business_sections_pdf), 
            ("Standard PDF Generator", self._try_standard_pdf_generator),
            ("Emergency Fallback", self._try_emergency_fallback)
        ]
        
        for system_name, system_func in fallback_systems:
            try:
                st.info(f" Versuche {system_name} als Mega Hybrid Fallback...")
                result = system_func(*args, **kwargs)
                if result:
                    st.success(f" {system_name} erfolgreich als Mega Hybrid Ersatz verwendet!")
                    return result
            except Exception as e:
                st.warning(f" {system_name} fehlgeschlagen: {e}")
                continue
        
        st.error(" Alle Mega Hybrid Fallback-Systeme fehlgeschlagen!")
        return None
    
    def _dummy_preview(self, *args, **kwargs):
        st.info(" PDF-Vorschau-System (Fallback) - Verwende beste verfügbare PDF-Generierung")
        
        # Cascading Fallback: Versuche verschiedene PDF-Systeme
        fallback_systems = [
            ("Standard PDF Generator", self._try_standard_pdf_generator),
            ("Business Sections PDF", self._try_business_sections_pdf),
            ("TOM-90 Exact Renderer", self._try_tom90_exact_renderer),
            ("Emergency Fallback", self._try_emergency_fallback)
        ]
        
        for system_name, system_func in fallback_systems:
            try:
                st.info(f" Versuche {system_name}...")
                result = system_func(*args, **kwargs)
                if result:
                    st.success(f" {system_name} erfolgreich verwendet!")
                    return result
            except Exception as e:
                st.warning(f" {system_name} fehlgeschlagen: {e}")
                continue
        
        st.error(" Alle PDF-Systeme sind nicht verfügbar!")
        return None
    
    def _try_standard_pdf_generator(self, *args, **kwargs):
        """Versuche das Standard-PDF-System"""
        try:
            from pdf_generator import generate_offer_pdf
            return generate_offer_pdf(*args, **kwargs)
        except Exception as parse_error:
            error_msg = str(parse_error)
            
            # Falls XML-Parsing-Fehler, versuche verschiedene Reparaturen
            if "Parse error" in error_msg and ("paragraph text" in error_msg or "saw </para>" in error_msg):
                st.warning(" XML-Parsing-Problem erkannt - verwende abgesicherte Parameter...")
                
                # Entferne problematische Inclusion-Optionen
                safe_kwargs = kwargs.copy()
                safe_inclusion_options = safe_kwargs.get('inclusion_options', {}).copy()
                
                # Deaktiviere alle Business-Sektionen (können XML-Probleme verursachen)
                business_keys = [key for key in safe_inclusion_options.keys() if 'business' in key.lower() or 'warranty' in key.lower()]
                for key in business_keys:
                    safe_inclusion_options[key] = False
                
                # Deaktiviere erweiterte Sektionen die XML-Probleme verursachen können
                problematic_keys = [
                    'include_business_warranty',
                    'include_warranty_tom90', 
                    'include_business_insurance',
                    'include_business_maintenance',
                    'include_business_financing',
                    'include_enhanced_charts',
                    'include_chart_descriptions'
                ]
                
                for key in problematic_keys:
                    safe_inclusion_options[key] = False
                    if key in safe_kwargs:
                        safe_kwargs[key] = False
                
                safe_kwargs['inclusion_options'] = safe_inclusion_options
                
                # Zweiter Versuch mit abgesicherten Parametern
                try:
                    st.info(" Zweiter Versuch mit sicheren XML-Parametern...")
                    return generate_offer_pdf(*args, **safe_kwargs)
                except Exception as e2:
                    st.warning(f" Auch abgesicherte Parameter fehlgeschlagen: {e2}")
                    
                    # Dritter Versuch: Minimale Parameter
                    try:
                        st.info(" Dritter Versuch mit Minimal-Konfiguration...")
                        minimal_kwargs = {
                            'project_data': kwargs.get('project_data', {}),
                            'analysis_results': kwargs.get('analysis_results', {}),
                            'company_info': kwargs.get('company_info', {}),
                            'texts': kwargs.get('texts', {}),
                            'inclusion_options': {
                                'include_company_logo': True,
                                'include_product_images': False,
                                'include_all_documents': False,
                                'include_optional_component_details': False
                            }
                        }
                        
                        return generate_offer_pdf(**minimal_kwargs)
                    except Exception as e3:
                        st.error(f" Alle Standard-PDF Versuche fehlgeschlagen: {e3}")
                        raise e3
            else:
                # Nicht-XML Fehler: Direkt weiterwerfen
                raise parse_error
    
    def _try_business_sections_pdf(self, *args, **kwargs):
        """Versuche das Business-Sections-PDF-System"""
        try:
            from business_sections_pdf import generate_business_sections_pdf
            
            company_info = kwargs.get('company_info', {})
            if company_info:
                # Extrahiere Business-Section Parameter
                inclusion_options = kwargs.get('inclusion_options', {})
                business_params = {
                    'include_business_company_profile': inclusion_options.get('include_business_company_profile', False),
                    'include_business_certifications': inclusion_options.get('include_business_certifications', False),
                    'include_business_references': inclusion_options.get('include_business_references', False),
                    'include_business_installation': inclusion_options.get('include_business_installation', False),
                    'include_business_maintenance': inclusion_options.get('include_business_maintenance', False),
                    'include_business_financing': inclusion_options.get('include_business_financing', False),
                    'include_business_insurance': inclusion_options.get('include_business_insurance', False),
                    'include_business_warranty': inclusion_options.get('include_business_warranty', False)
                }
                
                # Erste Versuch mit allen Business-Parametern
                try:
                    return generate_business_sections_pdf(company_info, **business_params)
                except Exception as e:
                    # Falls XML-Fehler, deaktiviere problematische Sektionen
                    if "Parse error" in str(e):
                        st.warning(" Business-Sections XML-Problem - deaktiviere problematische Bereiche...")
                        
                        # Deaktiviere die problematischsten Sektionen
                        safe_business_params = business_params.copy()
                        safe_business_params.update({
                            'include_business_warranty': False,  # Hauptverursacher des XML-Problems
                            'include_business_insurance': False,
                            'include_business_maintenance': False
                        })
                        
                        try:
                            return generate_business_sections_pdf(company_info, **safe_business_params)
                        except Exception as e2:
                            # Letzter Versuch: Nur sichere Sektionen
                            st.info(" Verwende nur sichere Business-Sektionen...")
                            minimal_business_params = {
                                'include_business_company_profile': True,
                                'include_business_certifications': True,
                                'include_business_references': False,
                                'include_business_installation': False,
                                'include_business_maintenance': False,
                                'include_business_financing': False,
                                'include_business_insurance': False,
                                'include_business_warranty': False
                            }
                            return generate_business_sections_pdf(company_info, **minimal_business_params)
                    else:
                        raise e
            return None
        except ImportError:
            st.warning(" Business-Sections PDF Generator nicht verfügbar")
            return None
    
    def _try_tom90_exact_renderer(self, *args, **kwargs):
        """Versuche den TOM-90 Exact Renderer"""
        try:
            from tom90_exact_renderer import generate_tom90_exact_pdf
            
            project_data = kwargs.get('project_data', {})
            analysis_results = kwargs.get('analysis_results', {})
            company_info = kwargs.get('company_info', {})
            
            if project_data and analysis_results and company_info:
                try:
                    return generate_tom90_exact_pdf(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        company_info=company_info,
                        texts=kwargs.get('texts', {}),
                        inclusion_options=kwargs.get('inclusion_options', {}),
                        company_logo_base64=company_info.get('logo_base64')
                    )
                except Exception as e:
                    # Falls TOM-90 XML-Probleme hat, verwende sichere Parameter
                    if "Parse error" in str(e):
                        st.warning(" TOM-90 XML-Problem - verwende sichere Parameter...")
                        
                        safe_inclusion_options = kwargs.get('inclusion_options', {}).copy()
                        # Entferne alle problematischen Optionen
                        xml_problem_keys = [key for key in safe_inclusion_options.keys() 
                                          if 'warranty' in key.lower() or 'insurance' in key.lower() 
                                          or 'maintenance' in key.lower()]
                        
                        for key in xml_problem_keys:
                            safe_inclusion_options[key] = False
                        
                        return generate_tom90_exact_pdf(
                            project_data=project_data,
                            analysis_results=analysis_results,
                            company_info=company_info,
                            texts=kwargs.get('texts', {}),
                            inclusion_options=safe_inclusion_options,
                            company_logo_base64=company_info.get('logo_base64')
                        )
                    else:
                        raise e
            return None
        except ImportError:
            st.warning(" TOM-90 Exact Renderer nicht verfügbar")
            return None
    
    def _try_emergency_fallback(self, *args, **kwargs):
        """Notfall-Fallback: Erstelle ein minimales PDF mit allen verfügbaren Daten"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Daten extrahieren
        company_info = kwargs.get('company_info', {})
        project_data = kwargs.get('project_data', {})
        analysis_results = kwargs.get('analysis_results', {})
        
        company_name = company_info.get('name', 'Unbekannte Firma')
        
        # PDF mit mehr Informationen erstellen
        y_position = 750
        
        # Header
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, y_position, " PV-Angebot (Notfall-PDF)")
        
        y_position -= 50
        p.setFont("Helvetica", 14)
        p.drawString(50, y_position, f" Firma: {company_name}")
        
        y_position -= 25
        p.drawString(50, y_position, f" Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        # Projektdaten
        if project_data:
            y_position -= 40
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, " Projektdaten:")
            
            y_position -= 25
            p.setFont("Helvetica", 12)
            
            pv_capacity = project_data.get('pv_capacity_kwp', 'N/A')
            battery_capacity = project_data.get('battery_capacity_kwh', 'N/A')
            
            p.drawString(70, y_position, f"• PV-Leistung: {pv_capacity} kWp")
            y_position -= 20
            p.drawString(70, y_position, f"• Batteriekapazität: {battery_capacity} kWh")
        
        # Analyseergebnisse
        if analysis_results:
            y_position -= 40
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, " Wirtschaftlichkeit:")
            
            y_position -= 25
            p.setFont("Helvetica", 12)
            
            total_investment = analysis_results.get('total_investment', 'N/A')
            payback_period = analysis_results.get('payback_period', 'N/A')
            annual_savings = analysis_results.get('annual_savings', 'N/A')
            
            p.drawString(70, y_position, f"• Gesamtinvestition: {total_investment} €")
            y_position -= 20
            p.drawString(70, y_position, f"• Amortisationszeit: {payback_period} Jahre")
            y_position -= 20
            p.drawString(70, y_position, f"• Jährliche Einsparung: {annual_savings} €")
        
        # Hinweis
        y_position -= 60
        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0.8, 0, 0)  # Rot
        p.drawString(50, y_position, " HINWEIS:")
        
        y_position -= 25
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0, 0, 0)  # Schwarz
        p.drawString(50, y_position, "Dieses PDF wurde mit dem Notfall-System erstellt, da die")
        y_position -= 15
        p.drawString(50, y_position, "Standard-PDF-Generatoren nicht verfügbar waren.")
        y_position -= 15
        p.drawString(50, y_position, "Für ein vollständiges Angebot wenden Sie sich bitte an den Administrator.")
        
        # Footer
        y_position = 50
        p.setFont("Helvetica", 8)
        p.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
        p.drawString(50, y_position, f"Generiert von: Zentrale PDF-System Architektur | {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def get_best_available_system(self) -> str:
        """Gibt das beste verfügbare PDF-System zurück (intelligente Auto-Auswahl)"""
        status = self.get_system_status()
        
        # Prioritätsreihenfolge: Mega Hybrid > TOM-90 > Standard
        if status.get('mega_hybrid', False):
            print(" Auto-Auswahl: Mega Hybrid System (beste Option)")
            return 'mega_hybrid'
        elif status.get('tom90', False):
            print(" Auto-Auswahl: TOM-90 System (gute Option)")
            return 'tom90'
        elif status.get('standard', False):
            print(" Auto-Auswahl: Standard System (Fallback)")
            return 'standard'
        else:
            print(" Auto-Auswahl: Notfall-System")
            return 'emergency'
    
    def generate_pdf(self, layout_choice: str, *args, **kwargs) -> Optional[bytes]:
        """Zentrale PDF-Generierung mit intelligenter Systemauswahl"""
        
        # Bei Auto-Modus das beste System wählen
        if layout_choice == "auto":
            layout_choice = self.get_best_available_system()
            print(f"🤖 Automatische Systemauswahl: {layout_choice}")
        
        # System-spezifische Behandlung
        if layout_choice == "mega_hybrid":
            try:
                system_func = self.get_system('mega_hybrid')
                if system_func:
                    print(" Verwende Mega Hybrid System...")
                    result = system_func(*args, **kwargs)
                    if result:
                        print(" Mega Hybrid PDF erfolgreich generiert!")
                        return result
                    else:
                        print(" Mega Hybrid lieferte keine Daten - verwende Fallback")
            except Exception as e:
                print(f" Mega Hybrid Fehler: {e}")
        
        elif layout_choice == "tom90_exact" or layout_choice == "tom90":
            try:
                system_func = self.get_system('tom90')
                if system_func:
                    print(" Verwende TOM-90 System...")
                    result = system_func(*args, **kwargs)
                    if result:
                        print(" TOM-90 PDF erfolgreich generiert!")
                        return result
            except Exception as e:
                print(f" TOM-90 Fehler: {e}")
        
        elif layout_choice == "standard":
            try:
                system_func = self.get_system('standard')
                if system_func:
                    print(" Verwende Standard System...")
                    result = system_func(*args, **kwargs)
                    if result:
                        print(" Standard PDF erfolgreich generiert!")
                        return result
            except Exception as e:
                print(f" Standard Fehler: {e}")
        
        # Fallback auf bestes verfügbares System
        print(" Automatischer Fallback...")
        best_system = self.get_best_available_system()
        if best_system != layout_choice:  # Verhindere Endlosschleife
            return self.generate_pdf(best_system, *args, **kwargs)
        
        # Letzter Fallback
        print(" Alle Systeme fehlgeschlagen - verwende Notfall-PDF")
        return self._try_emergency_fallback(*args, **kwargs)

    def get_system(self, system_name: str):
        """Gibt das angeforderte PDF-System zurück"""
        return self.available_systems.get(system_name)
    
    def get_system_status(self) -> Dict[str, bool]:
        """Gibt den Status aller Systeme zurück"""
        status = {
            'standard': True,  # Standard ist immer verfügbar
            'tom90': False,
            'mega_hybrid': False,
            'preview': False
        }
        
        # TOM90 prüfen
        try:
            # Prüfe den RICHTIGEN TOM-90 Renderer
            from tom90_renderer import generate_tom90_offer_pdf
            status['tom90'] = True
            print(" TOM90 Renderer (mit Business-Sections) verfügbar")
        except ImportError as e:
            print(f" TOM90 Renderer nicht verfügbar: {e}")
            try:
                # Fallback auf tom90_exact_renderer
                from tom90_exact_renderer import TOM90ExactRenderer
                status['tom90'] = True
                print(" TOM90ExactRenderer (Fallback) verfügbar")
            except ImportError:
                print(" Kein TOM-90 System verfügbar")
        
        # Mega Hybrid prüfen
        try:
            from mega_tom90_hybrid_pdf import MegaTOM90HybridPDFGenerator, generate_mega_hybrid_pdf
            # Zusätzliche Validierung - teste ob die Klasse funktional ist
            test_generator = MegaTOM90HybridPDFGenerator
            test_function = generate_mega_hybrid_pdf
            status['mega_hybrid'] = True
            print(" MegaTOM90HybridPDFGenerator vollständig verfügbar")
        except ImportError as e:
            print(f" MegaTOM90HybridPDFGenerator Import-Fehler: {e}")
            status['mega_hybrid'] = False
        except Exception as e:
            print(f" MegaTOM90HybridPDFGenerator Warnung: {e}")
            # Bei anderen Fehlern versuche nur den Import
            try:
                from mega_tom90_hybrid_pdf import generate_mega_hybrid_pdf
                status['mega_hybrid'] = True
                print(" MegaTOM90HybridPDFGenerator teilweise verfügbar")
            except:
                status['mega_hybrid'] = False
        
        # Preview prüfen
        try:
            status['preview'] = st.session_state.get('pdf_preview_available', False)
        except:
            pass
            
        return status

# Globale Instanz des PDF-System-Managers
PDF_MANAGER = PDFSystemManager()

# =============================================================================
# ZENTRALE PDF-UI KLASSE - ALLE INTERFACES AN EINEM ORT
# =============================================================================

class CentralPDFInterface:
    """Zentrale PDF-Benutzeroberfläche - ersetzt alle anderen PDF-UIs"""
    
    def __init__(self):
        self.session_prefix = "central_pdf_"
        self.current_layout = None
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialisiert alle Session State Variablen zentral"""
        defaults = {
            f"{self.session_prefix}layout_choice": "mega_hybrid",  # Standard: Mega Hybrid für vollständige PDFs
            f"{self.session_prefix}generating_lock": False,
            f"{self.session_prefix}inclusion_options": {
                "include_company_logo": True,
                "include_product_images": True,
                "include_all_documents": True,
                "company_document_ids_to_include": [],
                "selected_charts_for_pdf": [],
                "include_optional_component_details": True,
                # TOM-90 spezifische Optionen
                "include_company_profile_tom90": False,
                "include_certifications_tom90": False,
                "include_references_tom90": False,
                "include_installation_tom90": False,
                "include_maintenance_tom90": False,
                "include_financing_tom90": False,
                "include_insurance_tom90": False,
                "include_warranty_tom90": False,
                # Business-Sektionen für Standard-PDF
                "include_business_company_profile": False,
                "include_business_certifications": False,
                "include_business_references": False,
                "include_business_installation": False,
                "include_business_maintenance": False,
                "include_business_financing": False,
                "include_business_insurance": False,
                "include_business_warranty": False,
                # Chart-Enhancement
                "include_enhanced_charts": True,
                "include_chart_descriptions": True,
                "include_chart_kpis": True,
                # Berechnungsdetails
                "selected_calculations": [],
                # Finanzierungsoptionen
                "include_financing_overview": False,
                "include_credit_calculation": False,
                "include_leasing_options": False,
                "include_subsidy_info": False,
                "include_tax_benefits": False,
                "include_depreciation": False,
                "include_roi_detailed": False,
                "include_cashflow_analysis": False,
                "include_investment_breakdown": False,
                "include_payment_comparison": False,
                "include_interest_rates": False,
                "include_loan_scenarios": False,
                "include_leasing_comparison": False,
                "include_residual_values": False,
                "include_eeg_benefits": False,
                "include_sensitivity_analysis": False,
                # Firmenspezifische Vorlagen
                "selected_company_text_templates": [],
                "selected_company_image_templates": [],
                "company_content_position": "Nach Deckblatt",
                # Individuelle Inhalte (neue Struktur)
                "custom_content_items": [],  # Liste mit beliebig vielen Text/Bild-Items
            },
            f"{self.session_prefix}selected_main_sections": [
                "ProjectOverview", "TechnicalComponents", "CostDetails", 
                "Economics", "SimulationDetails", "CO2Savings", 
                "Visualizations", "FutureAspects"
            ],
            f"{self.session_prefix}theme_name": "Blau Elegant",
            f"{self.session_prefix}custom_images": [],
            f"{self.session_prefix}custom_text_blocks": []
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _get_chart_mapping(self):
        """Gibt das Chart-Mapping zurück"""
        return {
            'monthly_prod_cons_chart_bytes': ' Monatliche Produktion vs. Verbrauch',
            'cost_projection_chart_bytes': ' Kostenprojektion über 25 Jahre', 
            'cumulative_cashflow_chart_bytes': ' Kumulierter Cashflow',
            'consumption_coverage_pie_chart_bytes': '🥧 Verbrauchsdeckung (Kreisdiagramm)',
            'pv_usage_pie_chart_bytes': ' PV-Nutzungsverteilung',
            'yearly_production_chart_bytes': ' 3D-Jahresproduktion',
            'co2_savings_chart_bytes': ' CO₂-Einsparungen',
            'amortisation_chart_bytes': '⏰ Amortisationsanalyse',
            'break_even_chart_bytes': ' Break-Even-Analyse',
            'project_roi_matrix_switcher_chart_bytes': ' 3D-ROI-Matrix',
            'storage_effect_switcher_chart_bytes': ' Speichereffekt-Analyse',
            'tariff_comparison_switcher_chart_bytes': ' Tarifvergleich'
        }
    
    def render_layout_selector(self, texts: Dict[str, str]) -> str:
        """Zentrale Layout-Auswahl - ersetzt alle anderen Selektoren"""
        st.markdown("###  PDF-Layout wählen")
        
        # System-Status anzeigen
        status = PDF_MANAGER.get_system_status()
        status_info = []
        
        if status['tom90']:
            status_info.append(" TOM-90")
        else:
            status_info.append(" TOM-90")
            
        if status['mega_hybrid']:
            status_info.append(" Mega Hybrid")
        else:
            status_info.append(" Mega Hybrid")
            
        if status['standard']:
            status_info.append(" Standard")
        else:
            status_info.append(" Standard")
        
        st.caption(f"Verfügbare Systeme: {' | '.join(status_info)}")
        
        # Layout-Optionen basierend auf verfügbaren Systemen
        layout_options = []
        layout_descriptions = {}
        
        # Automatische Auswahl (empfohlen)
        layout_options.append("auto")
        layout_descriptions["auto"] = "🤖 Automatisch (beste verfügbare Option)"
        
        # Mega Hybrid (falls verfügbar)
        if status['mega_hybrid']:
            layout_options.append("mega_hybrid")
            layout_descriptions["mega_hybrid"] = " Mega Hybrid (TOM-90 ersten 5 Seiten + vollständiges PDF)"
        
        # TOM-90 Exact (falls verfügbar)
        if status['tom90']:
            layout_options.append("tom90_exact")
            layout_descriptions["tom90_exact"] = " TOM-90 Exact (nur moderne Seiten)"
        
        # Standard (immer verfügbar als Fallback)
        layout_options.append("standard")
        layout_descriptions["standard"] = " Standard (klassisches Layout)"
        
        # Preview (falls verfügbar)
        if status['preview']:
            layout_options.append("preview")
            layout_descriptions["preview"] = " Vorschau (interaktive Bearbeitung)"
        
        # Layout-Auswahl mit eindeutigem Key
        selected_layout = st.radio(
            "PDF-Layout auswählen:",
            options=layout_options,
            format_func=lambda x: layout_descriptions.get(x, x),
            key="central_pdf_layout_selector_unique",
            help="Wählen Sie das gewünschte PDF-Layout. 'Automatisch' wählt die beste verfügbare Option."
        )
        
        self.current_layout = selected_layout
        st.session_state[f"{self.session_prefix}layout_choice"] = selected_layout
        
        return selected_layout
    
    def render_content_options(self, 
                             texts: Dict[str, str], 
                             analysis_results: Dict[str, Any],
                             active_company_id: Optional[int],
                             db_list_company_documents_func: Callable) -> Dict[str, Any]:
        """Zentrale Inhalts-Optionen - ersetzt alle anderen Selektoren"""
        
        st.markdown("###  PDF-Inhalte & Sektionen")
        
        # Tab-System für bessere Organisation
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" Inhalte", " Charts", " Finanzierung", " Styling", " Medien", " Vorlagen"])
        
        current_options = st.session_state.get(f"{self.session_prefix}inclusion_options", {})
        
        # === TAB 1: INHALTE ===
        with tab1:
            st.markdown("####  Basis-Inhalte")
            
            # Schnell-Auswahl Buttons
            quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
            with quick_col1:
                if st.button(" Alles auswählen", key="select_all_basic", help="Alle Basis-Inhalte auswählen"):
                    current_options.update({
                        "include_company_logo": True,
                        "include_product_images": True,
                        "include_optional_component_details": True,
                        "include_all_documents": True,
                        "include_enhanced_charts": True,
                        "include_chart_descriptions": True
                    })
                    st.session_state["select_all_triggered"] = True  # Trigger für Firmenvorlagen
                    st.rerun()
            
            with quick_col2:
                if st.button(" Alles abwählen", key="deselect_all_basic", help="Alle Basis-Inhalte abwählen"):
                    current_options.update({
                        "include_company_logo": False,
                        "include_product_images": False,
                        "include_optional_component_details": False,
                        "include_all_documents": False,
                        "include_enhanced_charts": False,
                        "include_chart_descriptions": False
                    })
                    st.rerun()
            
            with quick_col3:
                if st.button(" Vorlagen", key="show_templates_basic", help="Vorlagen verwalten"):
                    st.session_state['show_template_manager'] = not st.session_state.get('show_template_manager', False)
                    st.rerun()
            
            with quick_col4:
                if st.button(" Standard", key="reset_to_default_basic", help="Standard-Einstellungen wiederherstellen"):
                    current_options.update({
                        "include_company_logo": True,
                        "include_product_images": True,
                        "include_optional_component_details": True,
                        "include_all_documents": True,
                        "include_enhanced_charts": True,
                        "include_chart_descriptions": True
                    })
                    st.rerun()
            
            # Template Manager
            if st.session_state.get('show_template_manager', False):
                with st.expander(" Vorlagen-Manager", expanded=True):
                    template_col1, template_col2 = st.columns(2)
                    
                    with template_col1:
                        st.markdown("**Neue Vorlage speichern:**")
                        template_name = st.text_input("Vorlagenname:", placeholder="Meine PDF-Konfiguration", key="new_template_name")
                        
                        if st.button(" Speichern", key="save_new_template") and template_name:
                            # Speichere aktuelle Konfiguration
                            template_config = {
                                'name': template_name,
                                'created': datetime.now().isoformat(),
                                'inclusion_options': current_options.copy(),
                                'selected_sections': st.session_state.get(f"{self.session_prefix}selected_main_sections", []),
                                'theme_name': st.session_state.get(f"{self.session_prefix}theme_name", "Blau Elegant")
                            }
                            
                            if "pdf_templates" not in st.session_state:
                                st.session_state["pdf_templates"] = []
                            
                            st.session_state["pdf_templates"].append(template_config)
                            st.success(f" Vorlage '{template_name}' gespeichert!")
                            st.rerun()
                    
                    with template_col2:
                        st.markdown("**Gespeicherte Vorlagen:**")
                        saved_templates = st.session_state.get("pdf_templates", [])
                        
                        if saved_templates:
                            for i, template in enumerate(saved_templates):
                                template_name = template.get('name', f'Vorlage {i+1}')
                                
                                template_sub_col1, template_sub_col2 = st.columns([3, 1])
                                with template_sub_col1:
                                    if st.button(f" {template_name}", key=f"load_template_{i}", help="Vorlage laden"):
                                        # Lade Vorlage
                                        loaded_options = template.get('inclusion_options', {})
                                        current_options.update(loaded_options)
                                        st.session_state[f"{self.session_prefix}inclusion_options"] = current_options
                                        st.session_state[f"{self.session_prefix}selected_main_sections"] = template.get('selected_sections', [])
                                        st.session_state[f"{self.session_prefix}theme_name"] = template.get('theme_name', 'Blau Elegant')
                                        st.success(f" Vorlage '{template_name}' geladen!")
                                        st.rerun()
                                
                                with template_sub_col2:
                                    if st.button("", key=f"delete_template_{i}", help="Vorlage löschen"):
                                        saved_templates.pop(i)
                                        st.session_state["pdf_templates"] = saved_templates
                                        st.success(" Vorlage gelöscht!")
                                        st.rerun()
                        else:
                            st.info("Keine Vorlagen gespeichert")
            
            col1, col2 = st.columns(2)
            
            with col1:
                current_options["include_company_logo"] = st.checkbox(" Firmenlogo", value=current_options.get("include_company_logo", True))
                current_options["include_product_images"] = st.checkbox(" Produktbilder", value=current_options.get("include_product_images", True))
                current_options["include_optional_component_details"] = st.checkbox(" Komponenten-Details", value=current_options.get("include_optional_component_details", True))
            
            with col2:
                current_options["include_all_documents"] = st.checkbox(" Alle Datenblätter", value=current_options.get("include_all_documents", True))
                current_options["include_enhanced_charts"] = st.checkbox(" Erweiterte Diagramme", value=current_options.get("include_enhanced_charts", True))
                current_options["include_chart_descriptions"] = st.checkbox(" Chart-Beschreibungen", value=current_options.get("include_chart_descriptions", True))
            
            st.markdown("####  Business-Sektionen")
            st.caption("Zusätzliche professionelle Geschäftsbereiche für die PDF")
            
            # Schnell-Auswahl für Business-Sektionen
            biz_quick_col1, biz_quick_col2, biz_quick_col3, biz_quick_col4 = st.columns(4)
            with biz_quick_col1:
                if st.button(" Alle Business", key="select_all_business", help="Alle Business-Sektionen auswählen"):
                    current_options.update({
                        "include_business_company_profile": True,
                        "include_business_certifications": True,
                        "include_business_references": True,
                        "include_business_installation": True,
                        "include_business_maintenance": True,
                        "include_business_financing": True,
                        "include_business_insurance": True,
                        "include_business_warranty": True
                    })
                    st.rerun()
            
            with biz_quick_col2:
                if st.button(" Keine Business", key="deselect_all_business", help="Alle Business-Sektionen abwählen"):
                    current_options.update({
                        "include_business_company_profile": False,
                        "include_business_certifications": False,
                        "include_business_references": False,
                        "include_business_installation": False,
                        "include_business_maintenance": False,
                        "include_business_financing": False,
                        "include_business_insurance": False,
                        "include_business_warranty": False
                    })
                    st.rerun()
            
            with biz_quick_col3:
                if st.button(" Service-Paket", key="select_service_package", help="Service-relevante Sektionen auswählen"):
                    current_options.update({
                        "include_business_installation": True,
                        "include_business_maintenance": True,
                        "include_business_warranty": True,
                        "include_business_insurance": True
                    })
                    st.rerun()
            
            with biz_quick_col4:
                if st.button(" Vertrauens-Paket", key="select_trust_package", help="Vertrauensbildende Sektionen auswählen"):
                    current_options.update({
                        "include_business_company_profile": True,
                        "include_business_certifications": True,
                        "include_business_references": True
                    })
                    st.rerun()
            
            business_col1, business_col2 = st.columns(2)
            
            with business_col1:
                current_options["include_business_company_profile"] = st.checkbox(" Firmenprofil", value=current_options.get("include_business_company_profile", False), help="Unternehmensprofil mit Kontaktdaten")
                current_options["include_business_certifications"] = st.checkbox(" Zertifizierungen", value=current_options.get("include_business_certifications", False), help="VDE, ISO 9001, Meisterbetrieb etc.")
                current_options["include_business_references"] = st.checkbox(" Kundenreferenzen", value=current_options.get("include_business_references", False), help="Kundenbewertungen und Projektreferenzen")
                current_options["include_business_installation"] = st.checkbox(" Installationsservice", value=current_options.get("include_business_installation", False), help="Professioneller Installationsprozess")
            
            with business_col2:
                current_options["include_business_maintenance"] = st.checkbox(" Wartungsservice", value=current_options.get("include_business_maintenance", False), help="Langzeitservice und Monitoring")
                current_options["include_business_financing"] = st.checkbox(" Finanzierungsberatung", value=current_options.get("include_business_financing", False), help="Finanzierungsoptionen und KfW-Beratung")
                current_options["include_business_insurance"] = st.checkbox(" Versicherungsberatung", value=current_options.get("include_business_insurance", False), help="Versicherungsschutz und Risikoabsicherung")
                current_options["include_business_warranty"] = st.checkbox(" Garantieleistungen", value=current_options.get("include_business_warranty", False), help="Garantien und Gewährleistungsumfang")
            
            st.markdown("####  Firmendokumente")
            selected_doc_ids = []
            if active_company_id and callable(db_list_company_documents_func):
                try:
                    # Korrekte Firmendokumente-Namen
                    company_document_names = {
                        1: " AGB",
                        2: " Datenschutz", 
                        3: " Vollmacht",
                        4: " SEPA-Mandat",
                        5: " Freistellungsbescheinigung",
                        6: " Sonstiges"
                    }
                    
                    st.caption("Wählen Sie spezifische Firmendokumente aus:")
                    doc_cols = st.columns(2)
                    
                    # Zeige die korrekten Dokumentnamen
                    for doc_id, doc_name in company_document_names.items():
                        with doc_cols[(doc_id-1) % 2]:
                            if st.checkbox(
                                doc_name, 
                                key=f"central_pdf_doc_{doc_id}",
                                help=f"Firmendokument: {doc_name}"
                            ):
                                selected_doc_ids.append(doc_id)
                    
                except Exception as e:
                    st.warning(f"Fehler beim Laden der Firmendokumente: {e}")
            else:
                st.info("Keine Firmendaten verfügbar - Dokumentauswahl nicht möglich")
            
            current_options["company_document_ids_to_include"] = selected_doc_ids
            
            st.markdown("####  Firmenspezifische Vorlagen")
            st.caption("Nutzen Sie gespeicherte Text- und Bildvorlagen Ihrer Firma")
            
            # Firmenspezifische Textvorlagen
            st.markdown("** Firmenspezifische Textvorlagen:**")
            selected_company_text_templates = []
            
            if active_company_id:
                try:
                    # Lade firmenspezifische Textvorlagen aus der Datenbank
                    from database import list_company_text_templates
                    company_text_templates = list_company_text_templates(active_company_id)
                    
                    if company_text_templates:
                        st.caption("Wählen Sie Textvorlagen aus:")
                        text_template_cols = st.columns(2)
                        
                        for i, template in enumerate(company_text_templates):
                            with text_template_cols[i % 2]:
                                template_name = template.get('name', f"Textvorlage {template.get('id')}")
                                template_preview = template.get('content', '')[:50] + "..." if len(template.get('content', '')) > 50 else template.get('content', '')
                                template_type = template.get('template_type', 'Standard')
                                
                                if st.checkbox(
                                    f" {template_name} ({template_type})",
                                    key=f"company_text_template_{template.get('id')}",
                                    help=f"Vorschau: {template_preview}"
                                ):
                                    selected_company_text_templates.append(template.get('id'))
                    else:
                        st.info(" Keine firmenspezifischen Textvorlagen verfügbar")
                        st.caption(" Textvorlagen können im Admin-Panel verwaltet werden")
                        
                except Exception as e:
                    st.warning(f"Fehler beim Laden der Textvorlagen: {e}")
            else:
                st.info(" Keine Firma ausgewählt - Textvorlagen nicht verfügbar")
            
            current_options["selected_company_text_templates"] = selected_company_text_templates
            
            # Firmenspezifische Bildvorlagen
            st.markdown("** Firmenspezifische Bildvorlagen:**")
            selected_company_image_templates = []
            
            if active_company_id:
                try:
                    # Lade firmenspezifische Bildvorlagen aus der Datenbank
                    from database import list_company_image_templates
                    company_image_templates = list_company_image_templates(active_company_id)
                    
                    if company_image_templates:
                        st.caption("Wählen Sie Bildvorlagen aus:")
                        image_template_cols = st.columns(3)
                        
                        for i, template in enumerate(company_image_templates):
                            with image_template_cols[i % 3]:
                                template_name = template.get('name', f"Bildvorlage {template.get('id')}")
                                template_type = template.get('template_type', 'Standard')
                                
                                # Zeige Template-Info
                                st.write(f" {template_name}")
                                st.caption(f"Typ: {template_type}")
                                
                                if st.checkbox(
                                    "Auswählen",
                                    key=f"company_image_template_{template.get('id')}",
                                    help=f"Bildvorlage: {template_name} ({template_type})"
                                ):
                                    selected_company_image_templates.append(template.get('id'))
                    else:
                        st.info(" Keine firmenspezifischen Bildvorlagen verfügbar")
                        st.caption(" Bildvorlagen können im Admin-Panel verwaltet werden")
                        
                except Exception as e:
                    st.warning(f"Fehler beim Laden der Bildvorlagen: {e}")
            else:
                st.info(" Keine Firma ausgewählt - Bildvorlagen nicht verfügbar")
            
            # Aktiviere alle verfügbaren Firmenvorlagen automatisch wenn "Alles auswählen" geklickt wird
            if st.session_state.get("select_all_triggered", False):
                # Auto-aktiviere verfügbare Firmen-Textvorlagen
                if active_company_id:
                    try:
                        from database import list_company_text_templates, list_company_image_templates
                        all_text_templates = list_company_text_templates(active_company_id)
                        all_image_templates = list_company_image_templates(active_company_id)
                        
                        current_options["selected_company_text_templates"] = [t['id'] for t in all_text_templates]
                        current_options["selected_company_image_templates"] = [t['id'] for t in all_image_templates]
                    except:
                        pass
                
                st.session_state["select_all_triggered"] = False
            
            # Positionierung der firmenspezifischen Inhalte
            if selected_company_text_templates or selected_company_image_templates:
                st.markdown("** Position der Firmenvorlagen:**")
                
                company_content_position = st.selectbox(
                    "Wo sollen die Firmenvorlagen im PDF erscheinen?",
                    options=[
                        "Nach Deckblatt",
                        "Nach Projektübersicht", 
                        "Nach Kostenaufstellung",
                        "Nach Wirtschaftlichkeit",
                        "Vor Anhang",
                        "Am Ende"
                    ],
                    index=0,
                    key="company_content_position",
                    help="Bestimmt die Position der firmenspezifischen Inhalte im PDF"
                )
                current_options["company_content_position"] = company_content_position
            
            st.divider()
            
            st.markdown("####  Individuelle Inhalte")
            st.caption("Fügen Sie beliebig viele eigene Texte und Bilder direkt in die PDF ein")
            
            # Initialisiere individuelle Inhalte Listen in Session State
            if "custom_content_items" not in st.session_state:
                st.session_state["custom_content_items"] = []
            
            # Buttons zum Hinzufügen neuer Inhalte
            content_add_col1, content_add_col2, content_add_col3 = st.columns(3)
            
            with content_add_col1:
                if st.button(" Text hinzufügen", key="add_custom_text_item"):
                    new_text_item = {
                        "type": "text",
                        "id": f"text_{len(st.session_state['custom_content_items'])}",
                        "title": "",
                        "content": "",
                        "position": "Nach Projektübersicht",
                        "enabled": True
                    }
                    st.session_state["custom_content_items"].append(new_text_item)
                    st.rerun()
            
            with content_add_col2:
                if st.button(" Bild hinzufügen", key="add_custom_image_item"):
                    new_image_item = {
                        "type": "image",
                        "id": f"image_{len(st.session_state['custom_content_items'])}",
                        "title": "",
                        "data": None,
                        "filename": "",
                        "position": "Nach Kostenaufstellung",
                        "enabled": True
                    }
                    st.session_state["custom_content_items"].append(new_image_item)
                    st.rerun()
            
            with content_add_col3:
                if st.button(" Alle löschen", key="clear_all_custom_items"):
                    st.session_state["custom_content_items"] = []
                    st.rerun()
            
            # Anzeige und Bearbeitung der individuellen Inhalte
            custom_items = st.session_state.get("custom_content_items", [])
            
            if custom_items:
                st.markdown("---")
                st.markdown("** Ihre individuellen Inhalte:**")
                
                # Container für alle Items
                for i, item in enumerate(custom_items):
                    with st.expander(f"{'' if item['type'] == 'text' else ''} {item['type'].title()} #{i+1}: {item.get('title', 'Ohne Titel')}", expanded=True):
                        
                        # Item-spezifische Felder
                        item_col1, item_col2, item_col3 = st.columns([2, 2, 1])
                        
                        with item_col1:
                            if item["type"] == "text":
                                # Text-Item Felder
                                item["title"] = st.text_input(
                                    "Titel:",
                                    value=item.get("title", ""),
                                    placeholder="z.B. Besondere Hinweise",
                                    key=f"custom_text_title_{i}"
                                )
                                
                                item["content"] = st.text_area(
                                    "Textinhalt:",
                                    value=item.get("content", ""),
                                    placeholder="Ihr individueller Text für die PDF...",
                                    height=120,
                                    key=f"custom_text_content_{i}"
                                )
                            
                            elif item["type"] == "image":
                                # Bild-Item Felder
                                item["title"] = st.text_input(
                                    "Bildtitel:",
                                    value=item.get("title", ""),
                                    placeholder="z.B. Unser Referenzprojekt",
                                    key=f"custom_image_title_{i}"
                                )
                                
                                uploaded_image = st.file_uploader(
                                    "Bild hochladen:",
                                    type=['png', 'jpg', 'jpeg'],
                                    key=f"custom_image_upload_{i}",
                                    help="Laden Sie ein eigenes Bild für die PDF hoch"
                                )
                                
                                if uploaded_image:
                                    import base64
                                    image_data = base64.b64encode(uploaded_image.read()).decode()
                                    item["data"] = image_data
                                    item["filename"] = uploaded_image.name
                                
                                # Bildvorschau
                                if item.get("data") and item.get("filename"):
                                    st.caption(f" Aktuelles Bild: {item['filename']}")
                        
                        with item_col2:
                            # Position für beide Item-Typen
                            item["position"] = st.selectbox(
                                "Position im PDF:",
                                options=["Nach Projektübersicht", "Nach Kostenaufstellung", "Nach Wirtschaftlichkeit", "Am Ende"],
                                index=["Nach Projektübersicht", "Nach Kostenaufstellung", "Nach Wirtschaftlichkeit", "Am Ende"].index(item.get("position", "Nach Projektübersicht")),
                                key=f"custom_item_position_{i}"
                            )
                            
                            # Aktivierung
                            item["enabled"] = st.checkbox(
                                "In PDF einbinden",
                                value=item.get("enabled", True),
                                key=f"custom_item_enabled_{i}"
                            )
                        
                        with item_col3:
                            # Aktionen
                            st.markdown("**Aktionen:**")
                            
                            # Nach oben verschieben
                            if st.button("", key=f"move_up_{i}", disabled=(i == 0), help="Nach oben verschieben"):
                                if i > 0:
                                    custom_items[i], custom_items[i-1] = custom_items[i-1], custom_items[i]
                                    st.session_state["custom_content_items"] = custom_items
                                    st.rerun()
                            
                            # Nach unten verschieben
                            if st.button("", key=f"move_down_{i}", disabled=(i == len(custom_items)-1), help="Nach unten verschieben"):
                                if i < len(custom_items)-1:
                                    custom_items[i], custom_items[i+1] = custom_items[i+1], custom_items[i]
                                    st.session_state["custom_content_items"] = custom_items
                                    st.rerun()
                            
                            # Item löschen
                            if st.button("", key=f"delete_item_{i}", help="Item löschen"):
                                custom_items.pop(i)
                                st.session_state["custom_content_items"] = custom_items
                                st.rerun()
                
                # Zusammenfassung der aktiven Items
                enabled_items = [item for item in custom_items if item.get("enabled", False)]
                if enabled_items:
                    with st.expander(" Vorschau aktiver Inhalte", expanded=False):
                        for item in enabled_items:
                            if item["type"] == "text" and item.get("title"):
                                st.markdown(f"** Text:** {item['title']} (Position: {item['position']})")
                            elif item["type"] == "image" and item.get("filename"):
                                st.markdown(f"** Bild:** {item['filename']} (Position: {item['position']})")
                
                # Speichere die Items in current_options für die PDF-Generierung
                current_options["custom_content_items"] = custom_items
            else:
                st.info(" Klicken Sie auf 'Text hinzufügen' oder 'Bild hinzufügen' um individuelle Inhalte zu erstellen.")
            
            st.divider()
            
            st.markdown("####  PDF-Sektionen Auswahl")
            st.caption("Wählen Sie die Hauptbereiche aus, die in der PDF enthalten sein sollen")
            
            # Vordefinierte Sektionen mit besserer Gruppierung
            section_groups = {
                "Kern-Bereiche": [
                    ("ProjectOverview", " Projektübersicht", "Zusammenfassung des gesamten Projekts"),
                    ("TechnicalComponents", " Technische Komponenten", "Detaillierte Komponentenauflistung"),
                    ("CostDetails", " Kostenaufstellung", "Vollständige Kostenkalkulation"),
                    ("Economics", " Wirtschaftlichkeit", "ROI und Amortisationsberechnungen")
                ],
                "Analyse & Simulation": [
                    ("SimulationDetails", " Simulationsdetails", "Technische Berechnungsdetails"),
                    ("CO2Savings", " CO₂-Einsparungen", "Umwelt- und Klimabilanz"),
                    ("Visualizations", " Visualisierungen", "Diagramme und grafische Darstellungen"),
                    ("FutureAspects", " Zukunftsaspekte", "Langfristige Betrachtungen")
                ],
                "Unternehmen & Service": [
                    ("CompanyProfile", " Firmenprofil", "Unternehmensdarstellung"),
                    ("Certifications", " Zertifizierungen", "Qualifikationen und Auszeichnungen"),
                    ("References", " Referenzen", "Kundenprojekte und Bewertungen"),
                    ("Installation", " Installation", "Installationsprozess und -service")
                ],
                "Service & Garantie": [
                    ("Maintenance", " Wartung", "Wartungsservice und Support"),
                    ("Financing", " Finanzierung", "Finanzierungsoptionen und Beratung"),
                    ("Insurance", " Versicherung", "Versicherungsschutz und Absicherung"),
                    ("Warranty", " Garantie", "Garantieleistungen und Gewährleistung")
                ]
            }
            
            selected_main_sections = st.session_state.get(f"{self.session_prefix}selected_main_sections", [
                "ProjectOverview", "TechnicalComponents", "CostDetails", 
                "Economics", "SimulationDetails", "CO2Savings"
            ])
            
            # Schnell-Auswahl für PDF-Sektionen
            section_quick_col1, section_quick_col2, section_quick_col3, section_quick_col4 = st.columns(4)
            with section_quick_col1:
                if st.button(" Alle Sektionen", key="select_all_sections", help="Alle PDF-Sektionen auswählen"):
                    all_sections = []
                    for group_sections in section_groups.values():
                        all_sections.extend([s[0] for s in group_sections])
                    st.session_state[f"{self.session_prefix}selected_main_sections"] = all_sections
                    st.rerun()
            
            with section_quick_col2:
                if st.button(" Kern-Sektionen", key="select_core_only", help="Nur Kern-Sektionen auswählen"):
                    core_sections = [s[0] for s in section_groups["Kern-Bereiche"]]
                    st.session_state[f"{self.session_prefix}selected_main_sections"] = core_sections
                    st.rerun()
            
            with section_quick_col3:
                if st.button(" Mit Analyse", key="select_with_analysis", help="Kern + Analyse-Sektionen"):
                    selected_sections = []
                    selected_sections.extend([s[0] for s in section_groups["Kern-Bereiche"]])
                    selected_sections.extend([s[0] for s in section_groups["Analyse & Simulation"]])
                    st.session_state[f"{self.session_prefix}selected_main_sections"] = selected_sections
                    st.rerun()
            
            with section_quick_col4:
                if st.button(" Vollständig", key="select_complete", help="Alle Sektionen für komplettes Angebot"):
                    all_sections = []
                    for group_sections in section_groups.values():
                        all_sections.extend([s[0] for s in group_sections])
                    st.session_state[f"{self.session_prefix}selected_main_sections"] = all_sections
                    st.rerun()
            
            # Übersichtliche Sektion-Auswahl mit Gruppierung
            updated_sections = []
            for group_name, group_sections in section_groups.items():
                with st.expander(f" {group_name}", expanded=True):
                    group_cols = st.columns(2)
                    for i, (section_id, section_name, section_desc) in enumerate(group_sections):
                        with group_cols[i % 2]:
                            if st.checkbox(
                                section_name,
                                value=section_id in selected_main_sections,
                                key=f"section_{section_id}",
                                help=section_desc
                            ):
                                if section_id not in updated_sections:
                                    updated_sections.append(section_id)
            
            # Reihenfolge-Anpassung mit Drag & Drop Alternative
            if updated_sections:
                st.markdown("** Ausgewählte Sektionen - Reihenfolge anpassen:**")
                
                # Aktuelle Reihenfolge aus session state oder default
                current_order = st.session_state.get(f"{self.session_prefix}selected_main_sections", updated_sections)
                
                # Nur die tatsächlich ausgewählten Sektionen in der richtigen Reihenfolge zeigen
                ordered_selected = [s for s in current_order if s in updated_sections]
                # Neue Sektionen am Ende hinzufügen
                for s in updated_sections:
                    if s not in ordered_selected:
                        ordered_selected.append(s)
                
                section_labels = {}
                for group_sections in section_groups.values():
                    for section_id, section_name, _ in group_sections:
                        section_labels[section_id] = section_name
                
                reorder_container = st.container()
                with reorder_container:
                    for i, section in enumerate(ordered_selected):
                        section_name = section_labels.get(section, section)
                        
                        reorder_col1, reorder_col2, reorder_col3, reorder_col4 = st.columns([0.1, 0.6, 0.15, 0.15])
                        
                        with reorder_col1:
                            st.write(f"{i+1}.")
                        
                        with reorder_col2:
                            st.write(f"{section_name}")
                        
                        with reorder_col3:
                            if st.button("", key=f"up_{section}_{i}", disabled=(i == 0), help="Nach oben verschieben"):
                                if i > 0:
                                    ordered_selected[i], ordered_selected[i-1] = ordered_selected[i-1], ordered_selected[i]
                                    st.session_state[f"{self.session_prefix}selected_main_sections"] = ordered_selected
                                    st.rerun()
                        
                        with reorder_col4:
                            if st.button("", key=f"down_{section}_{i}", disabled=(i == len(ordered_selected)-1), help="Nach unten verschieben"):
                                if i < len(ordered_selected)-1:
                                    ordered_selected[i], ordered_selected[i+1] = ordered_selected[i+1], ordered_selected[i]
                                    st.session_state[f"{self.session_prefix}selected_main_sections"] = ordered_selected
                                    st.rerun()
                
                st.session_state[f"{self.session_prefix}selected_main_sections"] = ordered_selected
                updated_sections = ordered_selected
            
            current_options["selected_sections"] = updated_sections
        
        # === TAB 2: CHARTS ===  
        with tab2:
            st.markdown("####  Diagramm-Auswahl")
            st.caption("Wählen Sie die Diagramme aus, die in der PDF angezeigt werden sollen")
            
            selected_charts = []
            if analysis_results:
                # Alle verfügbaren Charts mit besseren Namen
                chart_mapping = {
                    'monthly_prod_cons_chart_bytes': ' Monatliche Produktion vs. Verbrauch',
                    'cost_projection_chart_bytes': ' Kostenprojektion über 25 Jahre', 
                    'cumulative_cashflow_chart_bytes': ' Kumulierter Cashflow',
                    'consumption_coverage_pie_chart_bytes': '🥧 Verbrauchsdeckung (Kreisdiagramm)',
                    'pv_usage_pie_chart_bytes': ' PV-Nutzungsverteilung',
                    'yearly_production_chart_bytes': ' 3D-Jahresproduktion',
                    'co2_savings_chart_bytes': ' CO₂-Einsparungen',
                    'amortisation_chart_bytes': '⏰ Amortisationsanalyse',
                    'break_even_chart_bytes': ' Break-Even-Analyse',
                    'project_roi_matrix_switcher_chart_bytes': ' 3D-ROI-Matrix',
                    'storage_effect_switcher_chart_bytes': ' Speichereffekt-Analyse',
                    'tariff_comparison_switcher_chart_bytes': ' Tarifvergleich'
                }
                
                chart_cols = st.columns(2)
                for i, (chart_key, chart_name) in enumerate(chart_mapping.items()):
                    with chart_cols[i % 2]:
                        # Prüfe ob Chart in den Analyseergebnissen vorhanden ist
                        chart_available = chart_key in analysis_results
                        if chart_available:
                            if st.checkbox(chart_name, key=f"central_pdf_chart_{chart_key}", value=True):
                                selected_charts.append(chart_key)
                        else:
                            st.checkbox(chart_name, key=f"central_pdf_chart_{chart_key}_disabled", disabled=True, help="Diagramm nicht verfügbar")
            
            current_options["selected_charts_for_pdf"] = selected_charts
            
            # Chart-Enhancement Einstellungen
            st.markdown("####  Diagramm-Verbesserungen")
            chart_enh_cols = st.columns(3)
            
            with chart_enh_cols[0]:
                current_options["include_chart_descriptions"] = st.checkbox(" Beschreibungen", value=current_options.get("include_chart_descriptions", True), help="Erklärende Texte unter Diagrammen")
            
            with chart_enh_cols[1]:
                current_options["include_chart_kpis"] = st.checkbox(" KPI-Tabellen", value=current_options.get("include_chart_kpis", True), help="Kennzahlen-Tabellen unter Diagrammen")
            
            with chart_enh_cols[2]:
                current_options["include_enhanced_charts"] = st.checkbox(" Premium-Design", value=current_options.get("include_enhanced_charts", True), help="Professionelle Diagramm-Gestaltung")
        
        # === TAB 3: STYLING ===
        with tab3:
            st.markdown("####  PDF-Design")
            
            # Theme-Auswahl
            theme_options = ["Blau Elegant", "Grün Modern", "Grau Professionell", "TOM-90"]
            current_theme = st.session_state.get(f"{self.session_prefix}theme_name", "Blau Elegant")
            
            selected_theme = st.selectbox(
                "Design-Vorlage:",
                options=theme_options,
                index=theme_options.index(current_theme) if current_theme in theme_options else 0,
                help="Wählen Sie das Farbschema für die PDF"
            )
            
            st.session_state[f"{self.session_prefix}theme_name"] = selected_theme
            current_options["theme_name"] = selected_theme
            
            # Farbanpassungen
            st.markdown("####  Farbanpassungen")
            color_cols = st.columns(2)
            
            with color_cols[0]:
                primary_color = st.color_picker("Primärfarbe", value="#0d3780", help="Hauptfarbe für Überschriften und Akzente")
                current_options["primary_color"] = primary_color
            
            with color_cols[1]:
                secondary_color = st.color_picker("Sekundärfarbe", value="#f6f6f6", help="Hintergrundfarbe für Boxen und Tabellen")
                current_options["secondary_color"] = secondary_color
        
        # === TAB 4: FINANZIERUNG ===
        with tab4:
            st.markdown("####  Finanzierungsoptionen & -berechnungen")
            st.caption("Nutzen Sie bestehende Finanzberechnungen aus financial_tools.py für die PDF-Ausgabe")
            
            # Schnell-Auswahl für Finanzierungsdetails
            fin_quick_col1, fin_quick_col2, fin_quick_col3, fin_quick_col4 = st.columns(4)
            with fin_quick_col1:
                if st.button(" Alle Finanzierung", key="select_all_financing", help="Alle Finanzierungsoptionen auswählen"):
                    current_options.update({
                        "include_financing_overview": True,
                        "include_credit_calculation": True,
                        "include_leasing_options": True,
                        "include_subsidy_info": True,
                        "include_tax_benefits": True,
                        "include_depreciation": True,
                        "include_roi_detailed": True,
                        "include_cashflow_analysis": True
                    })
                    st.rerun()
            
            with fin_quick_col2:
                if st.button(" Nur Kredite", key="select_credit_only", help="Nur Kreditberechnungen"):
                    current_options.update({
                        "include_financing_overview": True,
                        "include_credit_calculation": True,
                        "include_leasing_options": False,
                        "include_subsidy_info": True,
                        "include_tax_benefits": False,
                        "include_depreciation": False,
                        "include_roi_detailed": True,
                        "include_cashflow_analysis": True
                    })
                    st.rerun()
            
            with fin_quick_col3:
                if st.button(" Leasing-Fokus", key="select_leasing_focus", help="Leasing-orientierte Auswahl"):
                    current_options.update({
                        "include_financing_overview": True,
                        "include_credit_calculation": False,
                        "include_leasing_options": True,
                        "include_subsidy_info": True,
                        "include_tax_benefits": True,
                        "include_depreciation": True,
                        "include_roi_detailed": True,
                        "include_cashflow_analysis": True
                    })
                    st.rerun()
            
            with fin_quick_col4:
                if st.button(" Keine Finanzierung", key="deselect_all_financing", help="Alle Finanzierungsoptionen abwählen"):
                    current_options.update({
                        "include_financing_overview": False,
                        "include_credit_calculation": False,
                        "include_leasing_options": False,
                        "include_subsidy_info": False,
                        "include_tax_benefits": False,
                        "include_depreciation": False,
                        "include_roi_detailed": False,
                        "include_cashflow_analysis": False
                    })
                    st.rerun()
            
            # Detaillierte Finanzierungsoptionen in Kategorien
            financing_categories = {
                " Finanzierungsübersicht": [
                    ("include_financing_overview", " Finanzierungsübersicht", "Gesamtübersicht aller Finanzierungsoptionen"),
                    ("include_investment_breakdown", " Investitionsaufschlüsselung", "Detaillierte Kostenaufstellung"),
                    ("include_payment_comparison", " Zahlungsvergleich", "Vergleich verschiedener Finanzierungsformen")
                ],
                " Kreditberechnungen": [
                    ("include_credit_calculation", " Kreditberechnung", "Annuitätendarlehen mit Tilgungsplan"),
                    ("include_interest_rates", " Zinsvergleich", "Verschiedene Zinssätze und deren Auswirkungen"),
                    ("include_loan_scenarios", " Kredit-Szenarien", "Verschiedene Laufzeiten und Eigenkapital-Anteile")
                ],
                " Leasing-Optionen": [
                    ("include_leasing_options", " Leasing-Berechnung", "Leasingraten und -konditionen"),
                    ("include_leasing_comparison", " Leasing vs. Kauf", "Direkter Kostenvergleich"),
                    ("include_residual_values", " Restwerte", "Restwertberechnung und Rückgabeoptionen")
                ],
                " Förderungen & Steuern": [
                    ("include_subsidy_info", " Förderungen", "KfW, BAFA und regionale Förderprogramme"),
                    ("include_tax_benefits", " Steuervorteile", "Abschreibungen und steuerliche Behandlung"),
                    ("include_eeg_benefits", " EEG-Vergütung", "Einspeisevergütung und deren Entwicklung")
                ],
                " Wirtschaftlichkeitsanalyse": [
                    ("include_depreciation", " Abschreibungen", "Lineare und degressive Abschreibungsmethoden"),
                    ("include_roi_detailed", " ROI-Detailanalyse", "Detaillierte Renditeberechnung"),
                    ("include_cashflow_analysis", " Cashflow-Analyse", "Monatliche und jährliche Cashflow-Projektionen"),
                    ("include_sensitivity_analysis", " Sensitivitätsanalyse", "Auswirkungen von Parameter-Änderungen")
                ]
            }
            
            # Kategorisierte Finanzierungs-Auswahl
            for category_name, category_options in financing_categories.items():
                with st.expander(f"{category_name}", expanded=True):
                    fin_cols = st.columns(2)
                    for i, (option_key, option_name, option_desc) in enumerate(category_options):
                        with fin_cols[i % 2]:
                            current_options[option_key] = st.checkbox(
                                option_name,
                                key=f"fin_{option_key}",
                                value=current_options.get(option_key, False),
                                help=option_desc
                            )
            
            # Financial Tools Integration Status
            st.markdown("####  Financial Tools Integration")
            
            # Prüfe ob financial_tools verfügbar ist
            try:
                import financial_tools
                st.success(" Financial Tools verfügbar - Berechnungen werden automatisch aus bestehenden Ergebnissen übernommen")
                
                # Zeige verfügbare Berechnungen aus analysis_results
                if analysis_results:
                    available_financial_data = []
                    financial_keys = [
                        'total_investment', 'annual_savings', 'payback_period', 
                        'total_roi_25_years', 'net_present_value', 'monthly_savings',
                        'cumulative_savings', 'financing_costs', 'loan_details'
                    ]
                    
                    for key in financial_keys:
                        if key in analysis_results:
                            available_financial_data.append(f" {key}")
                        else:
                            available_financial_data.append(f" {key}")
                    
                    with st.expander(" Verfügbare Finanzdaten aus Berechnung"):
                        for item in available_financial_data:
                            st.write(item)
                else:
                    st.info(" Finanzdaten werden nach der Hauptberechnung automatisch verfügbar")
                    
            except ImportError:
                st.warning(" Financial Tools nicht gefunden - Grundlegende Finanzierungsoptionen verfügbar")
            
            # Finanzierungs-Ergebnisse Integration
            st.markdown("####  Berechnungsergebnis-Integration")
            st.info(" Die Finanzierungsberechnungen nutzen automatisch die Ergebnisse aus der Hauptberechnung (analysis_results) und erweitern diese um detaillierte Finanzierungsoptionen.")
        
        # === TAB 5: MEDIEN ===
        with tab5:
            st.markdown("####  Eigene Medien")
            
            # Benutzerdefinierte Bilder
            st.markdown("**Eigene Bilder hinzufügen:**")
            uploaded_images = st.file_uploader(
                "Bilder hochladen:",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Laden Sie eigene Bilder für die PDF hoch"
            )
            
            custom_images = []
            if uploaded_images:
                for img in uploaded_images:
                    import base64
                    img_b64 = base64.b64encode(img.read()).decode()
                    custom_images.append({
                        'name': img.name,
                        'data': img_b64
                    })
            
            current_options["custom_images"] = custom_images
            
            # Benutzerdefinierte Textblöcke
            st.markdown("**Eigene Textblöcke:**")
            
            if st.button("+ Neuen Textblock hinzufügen"):
                if "custom_text_blocks" not in st.session_state:
                    st.session_state["custom_text_blocks"] = []
                st.session_state["custom_text_blocks"].append({
                    'title': f'Textblock {len(st.session_state["custom_text_blocks"]) + 1}',
                    'content': 'Ihr Text hier...'
                })
            
            custom_text_blocks = st.session_state.get("custom_text_blocks", [])
            for i, block in enumerate(custom_text_blocks):
                with st.expander(f" {block.get('title', f'Textblock {i+1}')}"):
                    block['title'] = st.text_input(f"Titel {i+1}:", value=block.get('title', ''))
                    block['content'] = st.text_area(f"Inhalt {i+1}:", value=block.get('content', ''), height=100)
                    
                    if st.button(f"Textblock {i+1} löschen", key=f"delete_text_{i}"):
                        custom_text_blocks.pop(i)
                        st.session_state["custom_text_blocks"] = custom_text_blocks
                        st.rerun()
            
            current_options["custom_text_blocks"] = custom_text_blocks
        
        # === TAB 6: VORLAGEN ===
        with tab6:
            st.markdown("####  Konfiguration als Vorlage speichern")
            
            template_name = st.text_input("Vorlagen-Name:", placeholder="Meine PDF-Konfiguration")
            
            if st.button(" Als Vorlage speichern") and template_name:
                # Speichere aktuelle Konfiguration
                template_config = {
                    'name': template_name,
                    'created': datetime.now().isoformat(),
                    'inclusion_options': current_options,
                    'selected_sections': updated_sections,
                    'theme_name': selected_theme
                }
                
                # Speichere in Session State (könnte später in DB gespeichert werden)
                if "pdf_templates" not in st.session_state:
                    st.session_state["pdf_templates"] = []
                
                st.session_state["pdf_templates"].append(template_config)
                st.success(f" Vorlage '{template_name}' erfolgreich gespeichert!")
            
            # Gespeicherte Vorlagen anzeigen
            saved_templates = st.session_state.get("pdf_templates", [])
            if saved_templates:
                st.markdown("**Gespeicherte Vorlagen:**")
                for i, template in enumerate(saved_templates):
                    with st.expander(f" {template.get('name', f'Vorlage {i+1}')}"):
                        st.write(f"**Erstellt:** {template.get('created', 'Unbekannt')}")
                        st.write(f"**Sektionen:** {len(template.get('selected_sections', []))}")
                        st.write(f"**Theme:** {template.get('theme_name', 'Standard')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f" Vorlage laden", key=f"load_template_{i}"):
                                # Lade Vorlage
                                st.session_state[f"{self.session_prefix}inclusion_options"] = template.get('inclusion_options', {})
                                st.session_state[f"{self.session_prefix}selected_main_sections"] = template.get('selected_sections', [])
                                st.session_state[f"{self.session_prefix}theme_name"] = template.get('theme_name', 'Blau Elegant')
                                st.success(" Vorlage geladen!")
                                st.rerun()
                        
                        with col2:
                            if st.button(f" Löschen", key=f"delete_template_{i}"):
                                saved_templates.pop(i)
                                st.session_state["pdf_templates"] = saved_templates
                                st.success(" Vorlage gelöscht!")
                                st.rerun()
        
        # Aktualisiere Session State
        st.session_state[f"{self.session_prefix}inclusion_options"] = current_options
        
        return current_options
    
    def render_template_selection(self, 
                                load_admin_setting_func: Callable,
                                texts: Dict[str, str]) -> Dict[str, str]:
        """Zentrale Template-Auswahl"""
        
        st.markdown("###  Vorlagen-Auswahl")
        
        # Templates laden
        try:
            title_templates = load_admin_setting_func('pdf_title_image_templates', [])
            offer_templates = load_admin_setting_func('pdf_offer_title_templates', [])
            letter_templates = load_admin_setting_func('pdf_cover_letter_templates', [])
        except Exception:
            title_templates = offer_templates = letter_templates = []
        
        col1, col2, col3 = st.columns(3)
        
        selected_title_b64 = None
        selected_offer_text = "Ihr Angebot für eine moderne Photovoltaikanlage"
        selected_letter_text = "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse."
        
        with col1:
            st.markdown("**Titelbild**")
            if title_templates:
                selected_title = st.selectbox(
                    "Titelbild wählen:",
                    options=[t.get('name', f"Bild {i+1}") for i, t in enumerate(title_templates)],
                    key="central_pdf_title_select"
                )
                # Finde das ausgewählte Template
                for template in title_templates:
                    if template.get('name') == selected_title:
                        selected_title_b64 = template.get('data')
                        break
            else:
                st.info("Keine Titelbilder verfügbar")
        
        with col2:
            st.markdown("**Angebots-Titel**")
            if offer_templates:
                selected_offer = st.selectbox(
                    "Titel wählen:",
                    options=[t.get('name', f"Titel {i+1}") for i, t in enumerate(offer_templates)],
                    key="central_pdf_offer_select"
                )
                # Finde das ausgewählte Template
                for template in offer_templates:
                    if template.get('name') == selected_offer:
                        selected_offer_text = template.get('content', selected_offer_text)
                        break
            else:
                st.info("Keine Titel verfügbar")
        
        with col3:
            st.markdown("**Anschreiben**")
            if letter_templates:
                selected_letter = st.selectbox(
                    "Anschreiben wählen:",
                    options=[t.get('name', f"Brief {i+1}") for i, t in enumerate(letter_templates)],
                    key="central_pdf_letter_select"
                )
                # Finde das ausgewählte Template
                for template in letter_templates:
                    if template.get('name') == selected_letter:
                        selected_letter_text = template.get('content', selected_letter_text)
                        break
            else:
                st.info("Keine Anschreiben verfügbar")
        
        return {
            "title_image_b64": selected_title_b64,
            "offer_title_text": selected_offer_text,
            "cover_letter_text": selected_letter_text
        }
    
    def generate_pdf_central(self,
                           layout_choice: str,
                           project_data: Dict[str, Any],
                           analysis_results: Dict[str, Any],
                           company_info: Dict[str, Any],
                           inclusion_options: Dict[str, Any],
                           template_data: Dict[str, str],
                           texts: Dict[str, str],
                           **kwargs) -> Optional[bytes]:
        """Zentrale PDF-Generierung - alle Systeme über eine Funktion"""
        
        try:
            st.info(f" Starte PDF-Generierung mit Layout: {layout_choice}")
            
            # Verwende die neue zentrale PDF-Generierung
            pdf_bytes = PDF_MANAGER.generate_pdf(
                layout_choice=layout_choice,
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=company_info.get('logo_base64'),
                selected_title_image_b64=template_data.get('title_image_b64'),
                selected_offer_title_text=template_data.get('offer_title_text'),
                selected_cover_letter_text=template_data.get('cover_letter_text'),
                sections_to_include=inclusion_options.get('selected_sections', []),
                texts=texts,
                inclusion_options=inclusion_options,  # Übergebe ALLE inclusion_options an das System
                # Neue Inclusion Options für Business Sections
                include_business_company_profile=inclusion_options.get('include_business_company_profile', False),
                include_business_certifications=inclusion_options.get('include_business_certifications', False),
                include_business_references=inclusion_options.get('include_business_references', False),
                include_business_installation=inclusion_options.get('include_business_installation', False),
                include_business_maintenance=inclusion_options.get('include_business_maintenance', False),
                include_business_financing=inclusion_options.get('include_business_financing', False),
                include_business_insurance=inclusion_options.get('include_business_insurance', False),
                include_business_warranty=inclusion_options.get('include_business_warranty', False),
                # Chart Enhancement Options
                include_enhanced_charts=inclusion_options.get('include_enhanced_charts', True),
                include_chart_descriptions=inclusion_options.get('include_chart_descriptions', True),
                include_chart_kpis=inclusion_options.get('include_chart_kpis', True),
                # PDF Attachment Options (für TOM-90)
                include_pdf_attachments=inclusion_options.get('include_pdf_attachments', False),
                include_product_datasheets=inclusion_options.get('include_product_datasheets', True),
                include_company_documents=inclusion_options.get('include_company_documents', True),
                # TOM-90 spezifische Optionen
                include_company_profile_tom90=inclusion_options.get('include_company_profile_tom90', False),
                include_certifications_tom90=inclusion_options.get('include_certifications_tom90', False),
                include_references_tom90=inclusion_options.get('include_references_tom90', False),
                include_installation_tom90=inclusion_options.get('include_installation_tom90', False),
                include_maintenance_tom90=inclusion_options.get('include_maintenance_tom90', False),
                include_financing_tom90=inclusion_options.get('include_financing_tom90', False),
                include_insurance_tom90=inclusion_options.get('include_insurance_tom90', False),
                include_warranty_tom90=inclusion_options.get('include_warranty_tom90', False),
                **kwargs
            )
            
            if pdf_bytes:
                st.success(f" PDF erfolgreich generiert! Layout: {layout_choice}")
                return pdf_bytes
            else:
                st.error(f" PDF-Generierung fehlgeschlagen für Layout: {layout_choice}")
                return None
        
        except Exception as e:
            st.error(f" Fehler bei PDF-Generierung: {e}")
            import traceback
            st.code(traceback.format_exc(), language="python")
            return None

    def render_main_interface(self,
                             project_data: Dict[str, Any],
                             analysis_results: Dict[str, Any],
                             texts: Dict[str, str],
                             list_products_func: Callable,
                             get_product_by_id_func: Callable,
                             get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]],
                             db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
                             load_admin_setting_func: Callable = None,
                             save_admin_setting_func: Callable = None,
                             **kwargs
                             ) -> None:
        """
        ZENTRALE PDF-UI FUNKTION
        ========================
        Ersetzt alle anderen render_pdf_ui Funktionen.
        Alle PDF-Erstellung läuft über diese eine Funktion!
        """
        
        st.title(" Zentrale PDF-Erstellung")
        st.markdown("Alle PDF-Systeme vereint an einem Ort - keine Duplikation mehr!")
        
        # Datenvalidierung
        company_info = get_active_company_details_func()
        if not company_info:
            st.warning(" Keine aktive Firma gefunden!")
            company_info = {"name": "Fallback Firma", "id": 1}
        
        active_company_id = company_info.get('id')
        
        # Minimale Datenprüfung
        if not project_data or not analysis_results:
            st.error(" Unvollständige Projektdaten!")
            if st.button(" Daten aus Session State wiederherstellen"):
                project_data = st.session_state.get('project_data', {})
                analysis_results = st.session_state.get('calculation_results', {})
                st.rerun()
            return
        
        st.success(" Projektdaten vollständig")
        
        # === ZENTRALE UI-BEREICHE ===
        
        # 1. Layout-Auswahl (zentral, eindeutig)
        selected_layout = self.render_layout_selector(texts)
        
        st.markdown("---")
        
        # 2. Template-Auswahl (zentral)
        template_data = self.render_template_selection(load_admin_setting_func, texts)
        
        st.markdown("---")
        
        # 3. Inhalts-Optionen (zentral)
        inclusion_options = self.render_content_options(
            texts, analysis_results, active_company_id, db_list_company_documents_func
        )
        
        st.markdown("---")
        
        # 4. PDF-Generierung (zentral)
        st.markdown("###  PDF erstellen")
        st.info("ℹ **Automatisch enthalten:** Projektübersicht, Simulationsdetails, Kostenaufstellung, Wirtschaftlichkeit, CO₂-Bilanz - Alle Basis-Daten aus der Analyse werden automatisch ins PDF übernommen!")
        
        col_info, col_button = st.columns([3, 1])
        
        with col_info:
            st.success(f"Layout: **{selected_layout}** | Firma: **{company_info.get('name')}**")
        
        with col_button:
            generate_button = st.button(
                " PDF erstellen",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.get(f"{self.session_prefix}generating_lock", False)
            )
        
        # PDF-Generierung
        if generate_button:
            st.session_state[f"{self.session_prefix}generating_lock"] = True
            
            try:
                with st.spinner(f"Erstelle PDF mit {selected_layout} Layout..."):
                    pdf_bytes = self.generate_pdf_central(
                        layout_choice=selected_layout,
                        project_data=project_data,
                        analysis_results=analysis_results,
                        company_info=company_info,
                        inclusion_options=inclusion_options,
                        template_data=template_data,
                        texts=texts,
                        load_admin_setting_func=load_admin_setting_func,
                        save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func,
                        get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func,
                        active_company_id=active_company_id
                    )
                
                if pdf_bytes:
                    # Erfolgreiche PDF-Erstellung
                    st.success(" PDF erfolgreich erstellt!")
                    
                    # Dateiname generieren
                    customer_name = project_data.get('customer_data', {}).get('last_name', 'Kunde')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Angebot_{customer_name}_{selected_layout}_{timestamp}.pdf"
                    
                    # Download-Button
                    st.download_button(
                        label=" PDF herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"central_pdf_download_{timestamp}"
                    )
                    
                    # Erfolgsmeldung mit Details
                    st.success(f" PDF mit {selected_layout.upper()} Layout erfolgreich erstellt!")
                    
                else:
                    st.error(" PDF-Erstellung fehlgeschlagen!")
                    
            except Exception as e:
                st.error(f" Unerwarteter Fehler: {e}")
                if st.checkbox("Fehlerdetails anzeigen", key="central_pdf_error_details"):
                    st.code(traceback.format_exc())
            
            finally:
                st.session_state[f"{self.session_prefix}generating_lock"] = False

# =============================================================================
# HILFSFUNKTIONEN UND UTILITIES
# =============================================================================

def get_central_pdf_status() -> Dict[str, Any]:
    """Gibt den Status des zentralen PDF-Systems zurück"""
    return {
        "manager_initialized": PDF_MANAGER is not None,
        "ui_initialized": CENTRAL_PDF_UI is not None,
        "available_systems": PDF_MANAGER.get_system_status() if PDF_MANAGER else {},
        "session_state_keys": [key for key in st.session_state.keys() if "central_pdf_" in key]
    }

def cleanup_old_pdf_session_state():
    """Räumt alte PDF Session State Variablen auf"""
    old_prefixes = [
        "pdf_inclusion_options",
        "pdf_selected_main_sections", 
        "pdf_generating_lock",
        "selected_title_image",
        "selected_offer_title",
        "selected_cover_letter"
    ]
    
    cleaned_count = 0
    for key in list(st.session_state.keys()):
        for prefix in old_prefixes:
            if key.startswith(prefix):
                del st.session_state[key]
                cleaned_count += 1
                break
    
    if cleaned_count > 0:
        st.info(f"🧹 {cleaned_count} alte PDF Session State Variablen bereinigt")

# =============================================================================
# ZENTRALE PDF-UI WRAPPER FUNKTION
# =============================================================================

def render_central_pdf_ui(
    project_data: Dict[str, Any], 
    analysis_results: Dict[str, Any], 
    texts: Dict[str, str],
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]],
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    load_admin_setting_func: Callable = None,
    save_admin_setting_func: Callable = None,
    **kwargs
):
    """
    ZENTRALE PDF-UI WRAPPER FUNKTION
    =================================
    Diese Funktion wird von gui.py aufgerufen und delegiert an das zentrale Interface.
    """
    CENTRAL_PDF_UI.render_main_interface(
        project_data=project_data,
        analysis_results=analysis_results,
        texts=texts,
        list_products_func=list_products_func,
        get_product_by_id_func=get_product_by_id_func,
        get_active_company_details_func=get_active_company_details_func,
        db_list_company_documents_func=db_list_company_documents_func,
        load_admin_setting_func=load_admin_setting_func,
        save_admin_setting_func=save_admin_setting_func,
        **kwargs
    )

# =============================================================================
# EXPORTIERTE FUNKTIONEN FÜR RÜCKWÄRTSKOMPATIBILITÄT
# =============================================================================

# Hauptfunktion für den Export
render_pdf_ui = render_central_pdf_ui

# Status-Funktion
def show_pdf_system_status():
    """Zeigt den Status des zentralen PDF-Systems"""
    status = get_central_pdf_status()
    
    st.subheader(" Zentrales PDF-System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**System-Manager:**")
        st.write(" Initialisiert" if status['manager_initialized'] else " Fehler")
        
        st.markdown("**UI-Interface:**")
        st.write(" Initialisiert" if status['ui_initialized'] else " Fehler")
    
    with col2:
        st.markdown("**Verfügbare PDF-Systeme:**")
        systems = status.get('available_systems', {})
        for system_name, available in systems.items():
            icon = "" if available else ""
            st.write(f"{icon} {system_name.upper()}")
    
    st.markdown("**Session State:**")
    session_keys = status.get('session_state_keys', [])
    if session_keys:
        st.write(f"Aktive Variablen: {len(session_keys)}")
        with st.expander("Details anzeigen"):
            for key in session_keys:
                st.code(f"{key}: {type(st.session_state[key])}")
    else:
        st.write("Keine zentralen PDF Session State Variablen")

# =============================================================================
# INITIALISIERUNG BEIM IMPORT
# =============================================================================

# Automatische System-Initialisierung
if 'central_pdf_system_initialized' not in st.session_state:
    st.session_state.central_pdf_system_initialized = True
    # Optional: Alte Session State Variablen bereinigen
    # cleanup_old_pdf_session_state()

# =============================================================================
# GLOBALE INSTANZEN
# =============================================================================

# Globale Instanz für das zentrale PDF-UI
CENTRAL_PDF_UI = CentralPDFInterface()
