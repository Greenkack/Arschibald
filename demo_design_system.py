"""
Design System Demo
Zeigt alle Design System Komponenten in Aktion
"""

import streamlit as st
from theming.ui_design_system import (
    ColorPalette, Typography, Spacing, BorderStyles, Shadows,
    ComponentVariants, Breakpoints, IconMapping, Animations,
    apply_custom_css, get_component_style
)

st.set_page_config(
    page_title="Design System - ARSCHIBALD",
    page_icon="🎨",
    layout="wide"
)

# Globale CSS Styles anwenden
apply_custom_css()

st.title("ARSCHIBALD Design System")
st.caption("Zentrale Design-Definitionen für konsistente UI-Gestaltung")

st.divider()

# Tabs für verschiedene Bereiche
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Farben",
    "Typografie",
    "Spacing & Layout",
    "Komponenten",
    "Icons",
    "Responsive"
])

# ==================== TAB 1: FARBEN ====================
with tab1:
    st.header("Farb-Palette")
    
    # Primärfarben
    st.subheader("Primärfarben")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: {ColorPalette.PRIMARY}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>PRIMARY</strong><br>{ColorPalette.PRIMARY}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {ColorPalette.PRIMARY_LIGHT}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>PRIMARY LIGHT</strong><br>{ColorPalette.PRIMARY_LIGHT}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: {ColorPalette.PRIMARY_DARK}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>PRIMARY DARK</strong><br>{ColorPalette.PRIMARY_DARK}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: {ColorPalette.SECONDARY}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>SECONDARY</strong><br>{ColorPalette.SECONDARY}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Statusfarben
    st.subheader("Statusfarben")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: {ColorPalette.SUCCESS}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>SUCCESS</strong><br>{ColorPalette.SUCCESS}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {ColorPalette.WARNING}; padding: 40px; border-radius: 8px; text-align: center; color: {ColorPalette.TEXT_PRIMARY};">
            <strong>WARNING</strong><br>{ColorPalette.WARNING}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: {ColorPalette.ERROR}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>ERROR</strong><br>{ColorPalette.ERROR}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: {ColorPalette.INFO}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>INFO</strong><br>{ColorPalette.INFO}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Feature-Farben
    st.subheader("Feature-Spezifische Farben")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: {ColorPalette.SOLAR_YELLOW}; padding: 40px; border-radius: 8px; text-align: center; color: {ColorPalette.TEXT_PRIMARY};">
            <strong>SOLAR</strong><br>{ColorPalette.SOLAR_YELLOW}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: {ColorPalette.HEAT_PUMP_ORANGE}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>HEAT PUMP</strong><br>{ColorPalette.HEAT_PUMP_ORANGE}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: {ColorPalette.CRM_BLUE}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>CRM</strong><br>{ColorPalette.CRM_BLUE}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: {ColorPalette.CONTROLLING_PURPLE}; padding: 40px; border-radius: 8px; text-align: center; color: white;">
            <strong>CONTROLLING</strong><br>{ColorPalette.CONTROLLING_PURPLE}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Status Color Helper
    st.subheader("Status Color Helper")
    status_input = st.selectbox("Status auswählen", ["success", "warning", "error", "info", "active", "pending", "inactive", "cancelled"])
    status_color = ColorPalette.get_status_color(status_input)
    
    st.markdown(f"""
    <div style="background: {status_color}; padding: 20px; border-radius: 8px; text-align: center; color: white;">
        Status: <strong>{status_input}</strong> → Farbe: <strong>{status_color}</strong>
    </div>
    """, unsafe_allow_html=True)

# ==================== TAB 2: TYPOGRAFIE ====================
with tab2:
    st.header("Typografie-System")
    
    # Headings
    st.subheader("Headings")
    
    for level in range(1, 7):
        style = Typography.get_heading_style(level)
        size = style['font-size']
        weight = style['font-weight']
        
        st.markdown(f"""
        <h{level} style="font-size: {size}; font-weight: {weight};">
            Heading {level} ({size})
        </h{level}>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Font Sizes
    st.subheader("Font Sizes")
    
    sizes = {
        "H1": Typography.FONT_SIZE_H1,
        "H2": Typography.FONT_SIZE_H2,
        "H3": Typography.FONT_SIZE_H3,
        "H4": Typography.FONT_SIZE_H4,
        "H5": Typography.FONT_SIZE_H5,
        "H6": Typography.FONT_SIZE_H6,
        "Body": Typography.FONT_SIZE_BODY,
        "Body Small": Typography.FONT_SIZE_BODY_SM,
        "Caption": Typography.FONT_SIZE_CAPTION,
        "Tiny": Typography.FONT_SIZE_TINY
    }
    
    for name, size in sizes.items():
        st.markdown(f"""
        <div style="font-size: {size}; margin-bottom: 8px;">
            {name}: {size} - The quick brown fox jumps over the lazy dog
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Font Weights
    st.subheader("Font Weights")
    
    weights = {
        "Light (300)": Typography.WEIGHT_LIGHT,
        "Regular (400)": Typography.WEIGHT_REGULAR,
        "Medium (500)": Typography.WEIGHT_MEDIUM,
        "Semibold (600)": Typography.WEIGHT_SEMIBOLD,
        "Bold (700)": Typography.WEIGHT_BOLD,
        "Extrabold (800)": Typography.WEIGHT_EXTRABOLD
    }
    
    for name, weight in weights.items():
        st.markdown(f"""
        <div style="font-weight: {weight}; margin-bottom: 8px;">
            {name} - The quick brown fox jumps over the lazy dog
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 3: SPACING & LAYOUT ====================
with tab3:
    st.header("Spacing & Layout")
    
    # Spacing Scale
    st.subheader("Spacing Scale")
    
    spacing_values = {
        "XS": Spacing.XS,
        "SM": Spacing.SM,
        "MD": Spacing.MD,
        "LG": Spacing.LG,
        "XL": Spacing.XL,
        "XXL": Spacing.XXL,
        "XXXL": Spacing.XXXL
    }
    
    for name, value in spacing_values.items():
        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <strong>{name} ({value})</strong>
            <div style="background: {ColorPalette.PRIMARY}; width: {value}; height: 40px; border-radius: 4px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Border Radius
    st.subheader("Border Radius")
    
    radius_values = {
        "None": BorderStyles.RADIUS_NONE,
        "Small": BorderStyles.RADIUS_SM,
        "Medium": BorderStyles.RADIUS_MD,
        "Large": BorderStyles.RADIUS_LG,
        "XL": BorderStyles.RADIUS_XL,
        "Full": BorderStyles.RADIUS_FULL
    }
    
    col1, col2, col3 = st.columns(3)
    
    for i, (name, value) in enumerate(radius_values.items()):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style="background: {ColorPalette.PRIMARY}; padding: 20px; border-radius: {value}; text-align: center; color: white; margin-bottom: 16px;">
                {name}<br>({value})
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Shadows
    st.subheader("Box Shadows")
    
    shadow_values = {
        "None": Shadows.SHADOW_NONE,
        "Small": Shadows.SHADOW_SM,
        "Medium": Shadows.SHADOW_MD,
        "Large": Shadows.SHADOW_LG,
        "XL": Shadows.SHADOW_XL,
        "2XL": Shadows.SHADOW_2XL
    }
    
    col1, col2, col3 = st.columns(3)
    
    for i, (name, value) in enumerate(shadow_values.items()):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 16px; box-shadow: {value};">
                {name}
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 4: KOMPONENTEN ====================
with tab4:
    st.header("Component Variants")
    
    # Button Variants
    st.subheader("Button Variants")
    
    button_variants = ["primary", "secondary", "outline", "ghost", "destructive"]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    for i, variant in enumerate(button_variants):
        style = get_component_style("button", variant=variant, size="md")
        
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <button style="
                background: {style.get('background', 'transparent')};
                color: {style['color']};
                border: {style.get('border', 'none')};
                padding: {style['padding']};
                border-radius: 8px;
                font-size: {style['font-size']};
                cursor: pointer;
                width: 100%;
            ">
                {variant.capitalize()}
            </button>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Button Sizes
    st.subheader("Button Sizes")
    
    col1, col2, col3 = st.columns(3)
    
    for i, size in enumerate(["sm", "md", "lg"]):
        style = get_component_style("button", variant="primary", size=size)
        
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <button style="
                background: {style['background']};
                color: {style['color']};
                border: none;
                padding: {style['padding']};
                border-radius: 8px;
                font-size: {style['font-size']};
                height: {style['height']};
                cursor: pointer;
                width: 100%;
            ">
                Size: {size.upper()}
            </button>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Card Variants
    st.subheader("Card Variants")
    
    col1, col2, col3 = st.columns(3)
    
    card_variants = ["elevated", "outlined", "flat"]
    
    for i, variant in enumerate(card_variants):
        style = get_component_style("card", variant=variant)
        
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div style="
                background: {style['background']};
                border: {style.get('border', 'none')};
                box-shadow: {style['box-shadow']};
                padding: 24px;
                border-radius: 8px;
                margin-bottom: 16px;
            ">
                <h4 style="margin: 0 0 8px 0;">Card {variant.capitalize()}</h4>
                <p style="margin: 0; color: {ColorPalette.TEXT_SECONDARY};">
                    Dies ist eine Beispiel-Card mit dem Variant "{variant}".
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Badge Variants
    st.subheader("Badge Variants")
    
    badge_variants = ["default", "secondary", "success", "warning", "error", "outline"]
    
    cols = st.columns(6)
    
    for i, variant in enumerate(badge_variants):
        style = get_component_style("badge", variant=variant)
        
        with cols[i]:
            st.markdown(f"""
            <span style="
                background: {style['background']};
                color: {style['color']};
                border: {style.get('border', 'none')};
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 0.75rem;
                display: inline-block;
            ">
                {variant}
            </span>
            """, unsafe_allow_html=True)

# ==================== TAB 5: ICONS ====================
with tab5:
    st.header("Icon Mapping (Lucide Icons)")
    
    st.info("Icon Library: Lucide Icons (https://lucide.dev/)")
    
    # Feature Icons
    st.subheader("Feature Icons")
    
    feature_icons = {
        "PV-Anlage": IconMapping.SOLAR,
        "Wärmepumpe": IconMapping.HEAT_PUMP,
        "CRM": IconMapping.CRM,
        "Controlling": IconMapping.CONTROLLING,
        "Admin": IconMapping.ADMIN,
        "PDF": IconMapping.PDF,
        "Analysis": IconMapping.ANALYSIS,
        "Calculator": IconMapping.CALCULATOR
    }
    
    cols = st.columns(4)
    
    for i, (feature, icon) in enumerate(feature_icons.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="
                background: {ColorPalette.BACKGROUND_DARK};
                padding: 16px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 16px;
            ">
                <strong>{feature}</strong><br>
                <code>{icon}</code>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # UI Icons
    st.subheader("UI Icons")
    
    ui_icons = {
        "Home": IconMapping.HOME,
        "Menu": IconMapping.MENU,
        "Close": IconMapping.CLOSE,
        "Search": IconMapping.SEARCH,
        "Filter": IconMapping.FILTER,
        "Settings": IconMapping.SETTINGS,
        "User": IconMapping.USER,
        "Logout": IconMapping.LOGOUT
    }
    
    cols = st.columns(4)
    
    for i, (name, icon) in enumerate(ui_icons.items()):
        with cols[i % 4]:
            st.code(f"{name}: {icon}")
    
    st.divider()
    
    # Action Icons
    st.subheader("Action Icons")
    
    action_icons = {
        "Save": IconMapping.SAVE,
        "Edit": IconMapping.EDIT,
        "Delete": IconMapping.DELETE,
        "Add": IconMapping.ADD,
        "Download": IconMapping.DOWNLOAD,
        "Upload": IconMapping.UPLOAD,
        "Refresh": IconMapping.REFRESH
    }
    
    cols = st.columns(4)
    
    for i, (name, icon) in enumerate(action_icons.items()):
        with cols[i % 4]:
            st.code(f"{name}: {icon}")
    
    st.divider()
    
    # Icon Getter Demo
    st.subheader("Icon Getter Demo")
    
    feature_input = st.text_input("Feature eingeben (z.B. 'photovoltaik', 'crm', 'waermepumpe')")
    
    if feature_input:
        icon = IconMapping.get_icon(feature_input)
        st.success(f"Icon für '{feature_input}': {icon}")

# ==================== TAB 6: RESPONSIVE ====================
with tab6:
    st.header("Responsive Breakpoints")
    
    # Breakpoint Übersicht
    st.subheader("Breakpoint Definitionen")
    
    breakpoints = {
        "Mobile": f"< {Breakpoints.MOBILE_MAX}px",
        "Tablet": f"{Breakpoints.TABLET_MIN}px - {Breakpoints.TABLET_MAX}px",
        "Desktop": f"{Breakpoints.DESKTOP_MIN}px - {Breakpoints.DESKTOP_MAX}px",
        "Wide": f">= {Breakpoints.WIDE_MIN}px"
    }
    
    for name, range_str in breakpoints.items():
        st.markdown(f"**{name}**: {range_str}")
    
    st.divider()
    
    # Grid Columns Demo
    st.subheader("Grid Columns pro Breakpoint")
    
    viewport_width = st.slider("Viewport Breite (px)", 320, 1920, 1200)
    columns_count = Breakpoints.get_columns_for_viewport(viewport_width)
    
    st.info(f"Bei {viewport_width}px Breite: **{columns_count} Spalten**")
    
    # Grid Visualisierung
    cols = st.columns(columns_count)
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div style="
                background: {ColorPalette.PRIMARY};
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                color: white;
            ">
                Spalte {i+1}
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Grid Columns Map
    st.subheader("Grid Columns Map")
    
    st.json(Breakpoints.GRID_COLUMNS)

# Footer
st.divider()
st.caption("Design System v1.0.0 - ARSCHIBALD UI Modernization")
st.caption("Keine Emojis, moderne Farben, konsistente Typografie")
