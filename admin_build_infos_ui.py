"""
Admin Build Infos Tab - Zeigt Hauptdokumentation und Detaillierte Docs
Passwortgeschützt über admin_security.py
"""
import streamlit as st
import glob
from pathlib import Path
from admin_security import require_admin_auth


def collect_documentation_files():
    """Sammelt alle Markdown-Dokumentationsdateien"""
    root_dir = Path(__file__).parent
    
    # Sammle alle .md Dateien aus Root und docs/
    md_files_root = list(root_dir.glob("*.md"))
    md_files_docs = list((root_dir / "docs").glob("*.md")) if (root_dir / "docs").exists() else []
    
    all_files = md_files_root + md_files_docs
    
    # Kategorisiere in Hauptdokumentation und Detaillierte Docs
    main_docs = []
    detailed_docs = []
    
    keywords_main = ['README', 'OVERVIEW', 'QUICKSTART', 'INSTALLATION', 'GUIDE', 'SETUP']
    
    for file in all_files:
        file_upper = file.name.upper()
        is_main = any(keyword in file_upper for keyword in keywords_main)
        
        doc_info = {
            'path': file,
            'name': file.stem,
            'display_name': file.stem.replace('_', ' ').replace('-', ' ').title(),
            'size_kb': file.stat().st_size / 1024
        }
        
        if is_main:
            main_docs.append(doc_info)
        else:
            detailed_docs.append(doc_info)
    
    # Sortiere alphabetisch
    main_docs.sort(key=lambda x: x['display_name'])
    detailed_docs.sort(key=lambda x: x['display_name'])
    
    return main_docs, detailed_docs


def render_documentation_tab(docs: list[dict], tab_name: str):
    """Rendert einen Dokumentations-Tab mit Suchfunktion"""
    if not docs:
        st.info(f"Keine {tab_name} gefunden.")
        return
    
    st.write(f"### 📚 {tab_name}")
    st.write(f"**{len(docs)}** Dokumente gefunden")
    
    # Suchfeld
    search_query = st.text_input(
        "Dokumentation durchsuchen",
        placeholder="Suchbegriff eingeben...",
        key=f"search_{tab_name}"
    )
    
    # Filtere Dokumente nach Suche
    if search_query:
        filtered_docs = [
            doc for doc in docs
            if search_query.lower() in doc['display_name'].lower()
        ]
    else:
        filtered_docs = docs
    
    if not filtered_docs:
        st.warning(f"Keine Dokumente gefunden für: '{search_query}'")
        return
    
    st.write(f"**{len(filtered_docs)}** Dokumente angezeigt")
    st.divider()
    
    # Zeige Dokumente in Expander
    for doc in filtered_docs:
        with st.expander(f"{doc['display_name']} ({doc['size_kb']:.1f} KB)"):
            try:
                content = doc['path'].read_text(encoding='utf-8')
                
                # Zeige Markdown-Inhalt
                st.markdown(content)
                
                # Download-Button
                st.download_button(
                    label="📥 Herunterladen",
                    data=content,
                    file_name=doc['path'].name,
                    mime="text/markdown",
                    key=f"download_{doc['path'].name}"
                )
                
            except Exception as e:
                st.error(f"Fehler beim Laden: {e}")


def render_build_info_statistics():
    """Zeigt Build-Statistiken und Metadaten"""
    st.write("### Build-Informationen")
    
    try:
        root_dir = Path(__file__).parent
        
        # Zähle Dateien
        py_files = list(root_dir.glob("*.py"))
        md_files = list(root_dir.glob("*.md"))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Python Module", len(py_files))
        
        with col2:
            st.metric("Dokumentationen", len(md_files))
        
        with col3:
            total_size = sum(f.stat().st_size for f in py_files + md_files) / (1024 * 1024)
            st.metric("Gesamtgröße", f"{total_size:.2f} MB")
        
        # Letzte Änderung
        if py_files:
            latest_file = max(py_files, key=lambda f: f.stat().st_mtime)
            latest_time = latest_file.stat().st_mtime
            
            import datetime
            latest_date = datetime.datetime.fromtimestamp(latest_time)
            
            st.info(f"🕐 Letzte Änderung: {latest_date.strftime('%d.%m.%Y %H:%M')} - {latest_file.name}")
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Build-Informationen: {e}")


def render_build_infos_tab():
    """
    Hauptfunktion für den Build Infos Tab
    Zeigt Hauptdokumentation und Detaillierte Docs (passwortgeschützt)
    """
    
    # Prüfe Passwortschutz
    if not require_admin_auth('build_infos', 'Build Infos & Dokumentation'):
        return  # Zugriff verweigert
    
    # Header
    st.title("📋 Build Infos & Dokumentation")
    st.markdown("""
    Dieser Bereich enthält alle technischen Dokumentationen, Build-Informationen 
    und detaillierte Anleitungen zur App-Entwicklung und -Wartung.
    """)
    
    st.divider()
    
    # Build-Statistiken
    with st.expander("Build-Statistiken", expanded=True):
        render_build_info_statistics()
    
    st.divider()
    
    # Sammle Dokumentationen
    main_docs, detailed_docs = collect_documentation_files()
    
    # Erstelle Tabs für Haupt- und Detaillierte Docs
    tab_main, tab_detailed = st.tabs([
        f"📚 Hauptdokumentation ({len(main_docs)})",
        f"📖 Detaillierte Docs ({len(detailed_docs)})"
    ])
    
    with tab_main:
        render_documentation_tab(main_docs, "Hauptdokumentation")
    
    with tab_detailed:
        render_documentation_tab(detailed_docs, "Detaillierte Dokumentation")
    
    # Footer
    st.divider()
    st.caption("🔒 Dieser Bereich ist passwortgeschützt und nur für Administratoren zugänglich.")
