"""
Demo: Video Fullscreen Background Feature

Zeigt die neuen Video-Optionen:
- Größen: small, medium, large, fullscreen
- Autoplay (automatischer Start)
- Loop (Endlos-Wiederholung)
- Kein Play-Button
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Video Fullscreen Background Demo",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Video Fullscreen Background Demo")
st.markdown("---")

# Info
st.info("""
**Neue Features:**
- 4 Video-Größen: Small, Medium, Large, **Fullscreen**
- Automatischer Start (Autoplay)
- Endlos-Wiederholung (Loop)
- Kein Play-Button mehr
- Video als Hintergrund möglich
""")

# Demo-Einstellungen
st.header("Demo-Einstellungen")

col1, col2, col3 = st.columns(3)

with col1:
    video_size = st.selectbox(
        "Video-Größe",
        options=["small", "medium", "large", "fullscreen"],
        index=3,
        format_func=lambda x: {
            'small': '📱 Klein (640x360)',
            'medium': '💻 Mittel (854x480)',
            'large': '🖥 Groß (1280x720)',
            'fullscreen': '🌐 Fullscreen (100vw x 100vh)'
        }[x]
    )

with col2:
    video_autoplay = st.checkbox("Automatisch starten", value=True)

with col3:
    video_loop = st.checkbox("Endlos wiederholen", value=True)

st.markdown("---")

# Code-Vorschau
st.header("HTML5-Video Code")

# Größen-Styles
size_styles = {
    'small': 'width: 640px; height: 360px; max-width: 90%;',
    'medium': 'width: 854px; height: 480px; max-width: 90%;',
    'large': 'width: 1280px; height: 720px; max-width: 95%;',
    'fullscreen': 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; object-fit: cover; z-index: -1;'
}

video_style = size_styles[video_size]

# Attribute
autoplay_attr = 'autoplay' if video_autoplay else ''
loop_attr = 'loop' if video_loop else ''

# Code generieren
html_code = f'''<video {autoplay_attr} {loop_attr} muted playsinline
    style="{video_style} border-radius: 8px;">
    <source src="data/intro_videos/intro_video.mp4" type="video/mp4">
    Ihr Browser unterstützt das Video-Tag nicht.
</video>'''

st.code(html_code, language='html')

# Erklärung
st.markdown("### Attribute-Erklärung")

attrs = {
    "autoplay": "Video startet automatisch beim Laden",
    "loop": "Video wiederholt sich endlos",
    "muted": "Video ist stummgeschaltet (erforderlich für Autoplay)",
    "playsinline": "Verhindert Fullscreen auf iOS (Video bleibt inline)"
}

for attr, desc in attrs.items():
    if attr in ['autoplay', 'loop']:
        active = (attr == 'autoplay' and video_autoplay) or (attr == 'loop' and video_loop)
        emoji = "✅" if active else "❌"
    else:
        emoji = "✅"  # muted und playsinline immer aktiv
    
    st.markdown(f"{emoji} **{attr}**: {desc}")

st.markdown("---")

# CSS-Styles Erklärung
st.header("CSS-Styles")

css_explanation = {
    'small': {
        'width': '640px - Feste Breite',
        'height': '360px - Feste Höhe',
        'max-width': '90% - Responsive auf kleinen Bildschirmen'
    },
    'medium': {
        'width': '854px - Feste Breite',
        'height': '480px - Feste Höhe',
        'max-width': '90% - Responsive auf kleinen Bildschirmen'
    },
    'large': {
        'width': '1280px - Feste Breite',
        'height': '720px - Feste Höhe (HD)',
        'max-width': '95% - Responsive auf kleinen Bildschirmen'
    },
    'fullscreen': {
        'position': 'fixed - Bleibt im Viewport (scrollt nicht mit)',
        'top': '0 - Oben am Bildschirm',
        'left': '0 - Links am Bildschirm',
        'width': '100vw - 100% Viewport-Breite',
        'height': '100vh - 100% Viewport-Höhe',
        'object-fit': 'cover - Skaliert ohne Verzerrung (füllt gesamten Bereich)',
        'z-index': '-1 - Hinter dem Inhalt (Background)'
    }
}

for prop, desc in css_explanation[video_size].items():
    st.markdown(f"- **{prop}**: {desc}")

st.markdown("---")

# Verwendungsbeispiele
st.header("Verwendungsbeispiele")

tab1, tab2, tab3 = st.tabs(["🖼 Vorschau", "🎯 Use Cases", "⚙️ Admin-Settings"])

with tab1:
    st.subheader(f"Vorschau: {video_size.upper()}")
    
    if video_size == "fullscreen":
        st.warning("⚠️ Fullscreen-Vorschau hier nicht möglich (würde gesamte Demo überdecken)")
        st.info("Im echten Intro-Screen würde das Video den gesamten Bildschirm füllen")
        
        st.markdown("**Visualisierung**:")
        st.markdown("""
        ```
        ┌─────────────────────────────────────┐
        │                                     │
        │         VIDEO FULLSCREEN            │ ← Video im Hintergrund
        │         (position: fixed)           │
        │                                     │
        │     ┌─────────────────────┐         │
        │     │  LOGIN-FORMULAR     │         │ ← Über dem Video
        │     │  (z-index: normal)  │         │
        │     └─────────────────────┘         │
        │                                     │
        └─────────────────────────────────────┘
        ```
        """)
    else:
        st.markdown(f"**Größe**: {size_styles[video_size]}")
        
        # Platzhalter-Box
        box_height = {
            'small': '360px',
            'medium': '480px',
            'large': '720px'
        }[video_size]
        
        st.markdown(f"""
        <div style="{size_styles[video_size]} background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                    color: white; font-size: 24px; font-weight: bold; height: {box_height};">
            VIDEO HIER ({video_size.upper()})
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("Empfohlene Use Cases")
    
    use_cases = {
        "small": [
            "Kleine Video-Vorschau in Seitenleiste",
            "Produkt-Demos (kompakt)",
            "Thumbnails mit Animation"
        ],
        "medium": [
            "Standard-Video-Player",
            "Tutorial-Videos",
            "Produkt-Präsentationen"
        ],
        "large": [
            "HD-Video-Präsentationen",
            "Marketing-Videos",
            "Detaillierte Demos"
        ],
        "fullscreen": [
            "🌟 Intro-Screen Background (empfohlen)",
            "Landing-Page Hintergrund",
            "Immersive Erlebnisse",
            "Hero-Sections"
        ]
    }
    
    for size, cases in use_cases.items():
        is_current = size == video_size
        emoji = "👉" if is_current else "  "
        
        st.markdown(f"{emoji} **{size.upper()}**")
        for case in cases:
            st.markdown(f"  - {case}")

with tab3:
    st.subheader("Admin-Panel Einstellungen")
    
    st.markdown("So konfigurierst du das Video im Admin-Panel:")
    
    st.code(f"""
1. Admin-Panel öffnen
2. Intro-Einstellungen
3. Media-Typ: "Video"
4. Video hochladen oder URL eingeben
5. Video-Größe: "{video_size.upper()}"
6. Automatisch starten: {"✓ Aktiviert" if video_autoplay else "❌ Deaktiviert"}
7. Endlos wiederholen: {"✓ Aktiviert" if video_loop else "❌ Deaktiviert"}
8. Speichern
    """)
    
    st.markdown("**Gespeicherte Settings (JSON)**:")
    
    st.json({
        "media_type": "video",
        "video_file_path": "data/intro_videos/intro_video.mp4",
        "video_url": "",
        "video_size": video_size,
        "video_autoplay": video_autoplay,
        "video_loop": video_loop
    })

st.markdown("---")

# Performance-Tipps
st.header("⚡ Performance-Tipps")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### ✅ Empfohlen")
    st.markdown("""
    - **Format**: MP4 (H.264)
    - **Auflösung**: 1920x1080 oder niedriger
    - **Bitrate**: 2-5 Mbps
    - **Dateigröße**: < 10 MB
    - **Dauer**: 10-30 Sekunden (Loop)
    - **Audio**: Optional (wird gemuted)
    """)

with col_b:
    st.markdown("### ❌ Zu vermeiden")
    st.markdown("""
    - **Format**: AVI (unkomprimiert)
    - **Auflösung**: 4K (zu groß)
    - **Bitrate**: > 10 Mbps
    - **Dateigröße**: > 50 MB
    - **Dauer**: > 1 Minute
    - **Audio**: Wichtiger Inhalt (wird stumm)
    """)

st.markdown("---")

# Browser-Kompatibilität
st.header("🌐 Browser-Kompatibilität")

browsers = {
    "Chrome/Edge": {"autoplay": "✅", "loop": "✅", "muted_required": "✅"},
    "Firefox": {"autoplay": "✅", "loop": "✅", "muted_required": "✅"},
    "Safari": {"autoplay": "✅*", "loop": "✅", "muted_required": "✅"},
}

st.markdown("**Autoplay-Unterstützung:**")

for browser, support in browsers.items():
    st.markdown(f"""
    **{browser}**:
    - Autoplay: {support['autoplay']}
    - Loop: {support['loop']}
    - Muted erforderlich: {support['muted_required']}
    """)

st.caption("* Safari benötigt zusätzlich `playsinline` Attribut")

st.markdown("---")

# Footer
st.caption("Demo erstellt mit Streamlit | Video Fullscreen Background Feature")
