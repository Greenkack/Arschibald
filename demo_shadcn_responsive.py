"""
Demo: shadcn/ui Responsive Design System

Demonstriert alle Features des Responsive Design Systems:
- Media Queries für Breakpoints
- Kollabierbare Sidebar für Mobile
- Gestapelte Layouts für Mobile
- Touch-freundliche Button-Größen
- Verhindert horizontales Scrollen

Run: streamlit run demo_shadcn_responsive.py
"""

import streamlit as st
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle,
    responsive_columns,
    responsive_container,
    ResponsiveDesignSystem
)

# Page Config
st.set_page_config(
    page_title="Responsive Design Demo",
    page_icon="📱",
    layout="wide"
)

# Injiziere Responsive CSS (nur einmal)
if 'responsive_css_injected' not in st.session_state:
    inject_responsive_design()
    st.session_state.responsive_css_injected = True

# Render Mobile Sidebar Toggle
render_mobile_sidebar_toggle()

# Initialize System
system = ResponsiveDesignSystem()

# Sidebar
with st.sidebar:
    st.title("📱 Navigation")
    st.markdown("---")
    
    page = st.radio(
        "Wähle Demo:",
        [
            "Overview",
            "Breakpoints",
            "Responsive Columns",
            "Responsive Grid",
            "Touch Optimization",
            "Visibility Classes",
            "Sidebar Toggle",
            "Complete Example"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Current Viewport")
    breakpoint = system.get_current_breakpoint()
    st.info(f"**Breakpoint:** {breakpoint}")
    
    if system.is_mobile():
        st.success("📱 Mobile View")
    elif system.is_tablet():
        st.info("📱 Tablet View")
    else:
        st.success("🖥️ Desktop View")

# Main Content
st.title("📱 shadcn/ui Responsive Design Demo")
st.markdown("Resize your browser to see responsive behavior!")

if page == "Overview":
    st.header("Overview")
    
    st.markdown("""
    Das Responsive Design System bietet:
    
    - ✅ **Media Queries** für Breakpoints (mobile, tablet, desktop)
    - ✅ **Kollabierbare Sidebar** für Mobile
    - ✅ **Gestapelte Layouts** für Mobile
    - ✅ **Touch-freundliche Größen** (min. 44px)
    - ✅ **Verhindert horizontales Scrollen**
    """)
    
    st.markdown("---")
    
    st.subheader("📐 Breakpoints")
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        **📱 Mobile**
        - 0-767px
        - 1 Spalte
        - Stack Layout
        - Sidebar Toggle
        """)
    
    with cols[1]:
        st.markdown("""
        **📱 Tablet**
        - 768-1023px
        - 2 Spalten
        - Reduzierte Sidebar
        - Touch-optimiert
        """)
    
    with cols[2]:
        st.markdown("""
        **🖥️ Desktop**
        - 1024px+
        - Volle Spalten
        - Normale Sidebar
        - Hover-Effekte
        """)
    
    st.markdown("---")
    
    st.subheader("🚀 Quick Start")
    
    st.code("""
from utils.shadcn_responsive import inject_responsive_design

# Injiziere Responsive CSS
inject_responsive_design()

# Deine App
st.title("Responsive App")
    """, language="python")

elif page == "Breakpoints":
    st.header("📐 Breakpoints")
    
    st.markdown("""
    Das System verwendet drei Breakpoints:
    """)
    
    # Breakpoint Info
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("### 📱 Mobile")
        st.info("**0-767px**")
        st.markdown("""
        - Smartphones
        - 1 Spalte Layout
        - Stack alle Elemente
        - Sidebar Toggle
        - Touch-optimiert
        """)
    
    with cols[1]:
        st.markdown("### 📱 Tablet")
        st.info("**768-1023px**")
        st.markdown("""
        - Tablets
        - 2 Spalten Layout
        - Reduzierte Sidebar
        - Touch-optimiert
        - Moderate Abstände
        """)
    
    with cols[2]:
        st.markdown("### 🖥️ Desktop")
        st.info("**1024px+**")
        st.markdown("""
        - Desktop/Laptop
        - Volle Spalten
        - Normale Sidebar
        - Hover-Effekte
        - Große Abstände
        """)
    
    st.markdown("---")
    
    st.subheader("Current Viewport Info")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Breakpoint", breakpoint.upper())
    
    with col2:
        is_mobile = "✅ Yes" if system.is_mobile() else "❌ No"
        st.metric("Is Mobile?", is_mobile)
    
    with col3:
        is_desktop = "✅ Yes" if system.is_desktop() else "❌ No"
        st.metric("Is Desktop?", is_desktop)

elif page == "Responsive Columns":
    st.header("📊 Responsive Columns")
    
    st.markdown("""
    Columns passen sich automatisch an die Viewport-Größe an:
    - **Desktop:** Alle Spalten nebeneinander
    - **Tablet:** 2 Spalten
    - **Mobile:** 1 Spalte (gestackt)
    """)
    
    st.markdown("---")
    
    st.subheader("2 Columns")
    cols = responsive_columns(2)
    with cols[0]:
        st.info("Column 1")
        st.write("Auf Mobile wird diese Spalte oben angezeigt.")
    with cols[1]:
        st.success("Column 2")
        st.write("Auf Mobile wird diese Spalte unten angezeigt.")
    
    st.markdown("---")
    
    st.subheader("3 Columns")
    cols = responsive_columns(3)
    with cols[0]:
        st.info("Column 1")
    with cols[1]:
        st.warning("Column 2")
    with cols[2]:
        st.success("Column 3")
    
    st.markdown("---")
    
    st.subheader("4 Columns")
    cols = responsive_columns(4)
    for i, col in enumerate(cols):
        with col:
            st.metric(f"Metric {i+1}", f"{(i+1)*100}")
    
    st.markdown("---")
    
    st.subheader("Code Example")
    st.code("""
from utils.shadcn_responsive import responsive_columns

# Erstellt 3 Spalten auf Desktop, stackt auf Mobile
cols = responsive_columns(3)

with cols[0]:
    st.write("Column 1")
with cols[1]:
    st.write("Column 2")
with cols[2]:
    st.write("Column 3")
    """, language="python")

elif page == "Responsive Grid":
    st.header("🎨 Responsive Grid")
    
    st.markdown("""
    Das Grid-System passt sich automatisch an:
    - **Desktop:** 4 Spalten
    - **Tablet:** 2 Spalten
    - **Mobile:** 1 Spalte
    """)
    
    st.markdown("---")
    
    st.subheader("Grid mit Cards")
    
    # Simuliere Grid mit Columns
    cols = responsive_columns(4)
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div style="
                background: var(--background);
                border: 1px solid var(--border);
                border-radius: 0.5rem;
                padding: 1.5rem;
                text-align: center;
            ">
                <h3>Card {i+1}</h3>
                <p>Responsive Card Content</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Grid mit Metrics")
    
    cols = responsive_columns(4)
    
    metrics = [
        ("Users", "1,234", "+12%"),
        ("Revenue", "$45.2K", "+8%"),
        ("Orders", "892", "+15%"),
        ("Growth", "23%", "+5%")
    ]
    
    for i, col in enumerate(cols):
        with col:
            st.metric(metrics[i][0], metrics[i][1], metrics[i][2])

elif page == "Touch Optimization":
    st.header("👆 Touch Optimization")
    
    st.markdown("""
    Alle interaktiven Elemente sind touch-optimiert:
    - **Mindestgröße:** 44px × 44px (Apple HIG & Material Design)
    - **Größeres Padding:** Bessere Touch-Bereiche
    - **Touch-Feedback:** Visual Feedback beim Tap
    - **Verhindert iOS Zoom:** font-size: 16px für Inputs
    """)
    
    st.markdown("---")
    
    st.subheader("Touch-Friendly Buttons")
    
    cols = st.columns(3)
    with cols[0]:
        st.button("Primary Button", type="primary")
    with cols[1]:
        st.button("Secondary Button")
    with cols[2]:
        st.button("Tertiary Button", type="secondary")
    
    st.info("✅ Alle Buttons haben min. 44px Höhe")
    
    st.markdown("---")
    
    st.subheader("Touch-Friendly Inputs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Text Input", placeholder="Touch-friendly")
        st.number_input("Number Input", value=0)
    
    with col2:
        st.selectbox("Select", ["Option 1", "Option 2", "Option 3"])
        st.date_input("Date Input")
    
    st.info("✅ Alle Inputs haben min. 44px Höhe und font-size: 16px")
    
    st.markdown("---")
    
    st.subheader("Touch-Friendly Checkboxes & Radio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Checkbox 1")
        st.checkbox("Checkbox 2")
        st.checkbox("Checkbox 3")
    
    with col2:
        st.radio("Radio", ["Option 1", "Option 2", "Option 3"])
    
    st.info("✅ Checkboxes und Radio Buttons sind 24px × 24px")

elif page == "Visibility Classes":
    st.header("👁️ Visibility Classes")
    
    st.markdown("""
    Zeige oder verstecke Content basierend auf Viewport:
    """)
    
    st.markdown("---")
    
    st.subheader("Hide on Mobile")
    st.markdown("""
    <div class="hide-mobile" style="
        background: var(--success);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    ">
        ❌ Dieser Content ist auf Mobile versteckt
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Show only on Mobile")
    st.markdown("""
    <div class="show-mobile" style="
        background: var(--info);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    ">
        📱 Dieser Content ist nur auf Mobile sichtbar
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Hide on Desktop")
    st.markdown("""
    <div class="hide-desktop" style="
        background: var(--warning);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    ">
        🖥️ Dieser Content ist auf Desktop versteckt
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Available Classes")
    
    st.code("""
<!-- Verstecken -->
<div class="hide-mobile">Versteckt auf Mobile</div>
<div class="hide-tablet">Versteckt auf Tablet</div>
<div class="hide-desktop">Versteckt auf Desktop</div>

<!-- Zeigen -->
<div class="show-mobile">Nur auf Mobile</div>
<div class="show-tablet">Nur auf Tablet</div>
<div class="show-desktop">Nur auf Desktop</div>
    """, language="html")

elif page == "Sidebar Toggle":
    st.header("📱 Sidebar Toggle")
    
    st.markdown("""
    Auf Mobile wird automatisch ein Toggle-Button angezeigt:
    
    - **Position:** Fixed top-left
    - **Größe:** 44px × 44px (touch-friendly)
    - **Overlay:** Dunkler Overlay beim Öffnen
    - **Animation:** Smooth slide transition
    """)
    
    st.markdown("---")
    
    st.subheader("Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ Automatisch auf Mobile**
        - Zeigt sich nur auf Viewports < 768px
        - Hamburger-Icon
        - Fixed Position
        
        **✅ Touch-Optimiert**
        - Min. 44px × 44px
        - Großer Touch-Bereich
        - Visual Feedback
        """)
    
    with col2:
        st.markdown("""
        **✅ Smooth Animations**
        - Slide-in/out Transition
        - Overlay Fade
        - 300ms Duration
        
        **✅ Accessibility**
        - Keyboard-Navigation
        - ARIA-Labels
        - Focus-Indikatoren
        """)
    
    st.markdown("---")
    
    st.subheader("Usage")
    
    st.code("""
from utils.shadcn_responsive import (
    inject_responsive_design,
    render_mobile_sidebar_toggle
)

# Injiziere CSS
inject_responsive_design()

# Render Toggle Button
render_mobile_sidebar_toggle()

# Sidebar Content
with st.sidebar:
    st.title("Navigation")
    st.button("Home")
    st.button("About")
    """, language="python")
    
    st.info("💡 Resize your browser to < 768px to see the toggle button!")

elif page == "Complete Example":
    st.header("🎯 Complete Example")
    
    st.markdown("""
    Ein vollständiges Beispiel mit allen Features:
    """)
    
    st.markdown("---")
    
    # Hero Section
    with responsive_container('desktop'):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            text-align: center;
            margin-bottom: 2rem;
        ">
            <h1>Responsive Dashboard</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">
                Vollständig responsive mit shadcn/ui Design
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics
    st.subheader("📊 Key Metrics")
    cols = responsive_columns(4)
    
    metrics_data = [
        ("Total Users", "12,345", "+12.5%", "👥"),
        ("Revenue", "$45.2K", "+8.3%", "💰"),
        ("Orders", "892", "+15.2%", "📦"),
        ("Growth", "23.4%", "+5.1%", "📈")
    ]
    
    for i, col in enumerate(cols):
        with col:
            metric = metrics_data[i]
            st.markdown(f"""
            <div style="
                background: var(--background);
                border: 1px solid var(--border);
                border-radius: 0.5rem;
                padding: 1.5rem;
                text-align: center;
            ">
                <div style="font-size: 2rem;">{metric[3]}</div>
                <h3 style="margin: 0.5rem 0;">{metric[1]}</h3>
                <p style="color: var(--muted-foreground); margin: 0;">{metric[0]}</p>
                <p style="color: var(--success); margin: 0.5rem 0 0 0;">{metric[2]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Section
    st.subheader("📈 Analytics")
    
    col1, col2 = responsive_columns(2)
    
    with col1:
        st.line_chart({
            "Sales": [100, 120, 140, 130, 150, 170, 160],
            "Target": [110, 115, 130, 140, 145, 160, 165]
        })
    
    with col2:
        st.bar_chart({
            "Product A": [30, 40, 35, 50, 45, 55, 60],
            "Product B": [20, 25, 30, 28, 35, 40, 38]
        })
    
    st.markdown("---")
    
    # Data Table
    st.subheader("📋 Recent Orders")
    
    import pandas as pd
    
    df = pd.DataFrame({
        "Order ID": [f"ORD-{i:04d}" for i in range(1, 6)],
        "Customer": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Wilson"],
        "Amount": ["$120.00", "$85.50", "$200.00", "$150.75", "$95.25"],
        "Status": ["Completed", "Pending", "Completed", "Shipped", "Pending"]
    })
    
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # Action Buttons
    st.subheader("⚡ Quick Actions")
    
    cols = responsive_columns(3)
    
    with cols[0]:
        st.button("📊 View Reports", use_container_width=True)
    with cols[1]:
        st.button("➕ Add Order", use_container_width=True, type="primary")
    with cols[2]:
        st.button("⚙️ Settings", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--muted-foreground); padding: 2rem 0;">
    <p>📱 Responsive Design Demo | shadcn/ui Theme System</p>
    <p>Resize your browser to see responsive behavior!</p>
</div>
""", unsafe_allow_html=True)
