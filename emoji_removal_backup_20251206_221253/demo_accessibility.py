"""
Demo: Accessibility Features for shadcn/ui Theme System

This demo showcases all accessibility features including:
- WCAG contrast checking
- Color blindness simulation
- Keyboard navigation
- ARIA labels
- Focus management
- Screen reader support
- Text scaling
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from theming.accessibility import (
    ContrastChecker,
    ColorBlindnessSimulator,
    ColorBlindnessType,
    KeyboardNavigationHelper,
    ARIAHelper,
    FocusManager,
    ScreenReaderHelper,
    TextScalingHelper,
    AccessibilityAuditor,
    ColorBlindnessFriendlyThemeGenerator
)
from theming.theme_manager import ThemeManager


def main():
    st.set_page_config(
        page_title="Accessibility Features Demo",
        page_icon="♿",
        layout="wide"
    )
    
    st.title("♿ Accessibility (A11y) Features Demo")
    st.markdown("Comprehensive accessibility features for the shadcn/ui theme system")
    
    # Inject accessibility CSS
    st.markdown(f"""
    <style>
    {KeyboardNavigationHelper.get_keyboard_nav_css()}
    {FocusManager.get_focus_indicator_css()}
    {ScreenReaderHelper.get_sr_only_css()}
    {TextScalingHelper.get_responsive_text_css()}
    </style>
    """, unsafe_allow_html=True)
    
    # Skip to main content link
    st.markdown(KeyboardNavigationHelper.get_skip_to_main_html(), unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div id="main-content">', unsafe_allow_html=True)
    
    tabs = st.tabs([
        "🎨 Contrast Checker",
        "👁️ Color Blindness",
        "⌨️ Keyboard Nav",
        "🏷️ ARIA Labels",
        "🎯 Focus Management",
        "📢 Screen Reader",
        "📏 Text Scaling",
        "📊 Theme Audit",
        "🎨 CB-Friendly Themes"
    ])
    
    # Tab 1: Contrast Checker
    with tabs[0]:
        demo_contrast_checker()
    
    # Tab 2: Color Blindness Simulation
    with tabs[1]:
        demo_color_blindness()
    
    # Tab 3: Keyboard Navigation
    with tabs[2]:
        demo_keyboard_navigation()
    
    # Tab 4: ARIA Labels
    with tabs[3]:
        demo_aria_labels()
    
    # Tab 5: Focus Management
    with tabs[4]:
        demo_focus_management()
    
    # Tab 6: Screen Reader Support
    with tabs[5]:
        demo_screen_reader()
    
    # Tab 7: Text Scaling
    with tabs[6]:
        demo_text_scaling()
    
    # Tab 8: Theme Audit
    with tabs[7]:
        demo_theme_audit()
    
    # Tab 9: Colorblind-Friendly Themes
    with tabs[8]:
        demo_colorblind_themes()
    
    st.markdown('</div>', unsafe_allow_html=True)


def demo_contrast_checker():
    """Demo contrast checking functionality"""
    st.header("🎨 WCAG Contrast Checker")
    st.markdown("Check if color combinations meet WCAG 2.1 Level AA/AAA standards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        foreground = st.color_picker("Foreground Color", "#000000")
        background = st.color_picker("Background Color", "#ffffff")
        is_large_text = st.checkbox("Large Text (18pt+ or 14pt+ bold)", False)
    
    with col2:
        # Show color preview
        st.markdown(f"""
        <div style="background: {background}; padding: 20px; border-radius: 8px; border: 1px solid #ccc;">
            <p style="color: {foreground}; font-size: {'24px' if is_large_text else '16px'}; margin: 0;">
                Sample Text
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Check contrast
    result = ContrastChecker.check_contrast(foreground, background, is_large_text)
    
    st.markdown("---")
    st.subheader("Results")
    
    # Display ratio
    st.metric("Contrast Ratio", f"{result.ratio:.2f}:1")
    
    # Display compliance
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "WCAG AA (Normal)",
            "✅ Pass" if result.passes_aa_normal else "❌ Fail",
            delta="4.5:1 required"
        )
    
    with col2:
        st.metric(
            "WCAG AA (Large)",
            "✅ Pass" if result.passes_aa_large else "❌ Fail",
            delta="3:1 required"
        )
    
    with col3:
        st.metric(
            "WCAG AAA (Normal)",
            "✅ Pass" if result.passes_aaa_normal else "❌ Fail",
            delta="7:1 required"
        )
    
    with col4:
        st.metric(
            "WCAG AAA (Large)",
            "✅ Pass" if result.passes_aaa_large else "❌ Fail",
            delta="4.5:1 required"
        )
    
    # Recommendation
    if result.passes_aa_normal or (is_large_text and result.passes_aa_large):
        st.success(result.recommendation)
    else:
        st.error(result.recommendation)
    
    # Info box
    with st.expander("ℹ️ About WCAG Contrast Requirements"):
        st.markdown("""
        **WCAG 2.1 Contrast Requirements:**
        
        - **Level AA (Normal Text):** 4.5:1 minimum
        - **Level AA (Large Text):** 3:1 minimum
        - **Level AAA (Normal Text):** 7:1 minimum
        - **Level AAA (Large Text):** 4.5:1 minimum
        
        **Large Text Definition:**
        - 18pt (24px) or larger
        - 14pt (18.66px) or larger if bold
        
        Meeting Level AA is the legal requirement in many jurisdictions.
        Level AAA provides enhanced accessibility.
        """)


def demo_color_blindness():
    """Demo color blindness simulation"""
    st.header("👁️ Color Blindness Simulation")
    st.markdown("See how colors appear to people with different types of color blindness")
    
    # Color input
    original_color = st.color_picker("Select a color to simulate", "#3b82f6")
    
    # Show original
    st.subheader("Original Color")
    st.markdown(f"""
    <div style="background: {original_color}; height: 100px; border-radius: 8px; 
                display: flex; align-items: center; justify-content: center; color: white; 
                font-size: 24px; font-weight: bold;">
        {original_color}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Simulations")
    
    # Simulate all types
    col1, col2 = st.columns(2)
    
    with col1:
        # Protanopia (Red-blind)
        protanopia = ColorBlindnessSimulator.simulate(original_color, ColorBlindnessType.PROTANOPIA)
        st.markdown("**Protanopia (Red-blind)** - ~1% of males")
        st.markdown(f"""
        <div style="background: {protanopia}; height: 80px; border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: bold;">
            {protanopia}
        </div>
        """, unsafe_allow_html=True)
        
        # Tritanopia (Blue-blind)
        tritanopia = ColorBlindnessSimulator.simulate(original_color, ColorBlindnessType.TRITANOPIA)
        st.markdown("**Tritanopia (Blue-blind)** - ~0.01% of people")
        st.markdown(f"""
        <div style="background: {tritanopia}; height: 80px; border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: bold;">
            {tritanopia}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Deuteranopia (Green-blind)
        deuteranopia = ColorBlindnessSimulator.simulate(original_color, ColorBlindnessType.DEUTERANOPIA)
        st.markdown("**Deuteranopia (Green-blind)** - ~1% of males")
        st.markdown(f"""
        <div style="background: {deuteranopia}; height: 80px; border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: bold;">
            {deuteranopia}
        </div>
        """, unsafe_allow_html=True)
        
        # Achromatopsia (Total color blindness)
        achromatopsia = ColorBlindnessSimulator.simulate(original_color, ColorBlindnessType.ACHROMATOPSIA)
        st.markdown("**Achromatopsia (Total)** - ~0.003% of people")
        st.markdown(f"""
        <div style="background: {achromatopsia}; height: 80px; border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; color: white; 
                    font-weight: bold;">
            {achromatopsia}
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ About Color Blindness"):
        st.markdown("""
        **Types of Color Blindness:**
        
        - **Protanopia:** Red-blind (missing L-cones)
        - **Deuteranopia:** Green-blind (missing M-cones)
        - **Tritanopia:** Blue-blind (missing S-cones)
        - **Achromatopsia:** Total color blindness (no color perception)
        
        **Design Tips:**
        - Don't rely solely on color to convey information
        - Use patterns, shapes, and text labels
        - Ensure sufficient contrast
        - Test with simulation tools
        """)


def demo_keyboard_navigation():
    """Demo keyboard navigation features"""
    st.header("⌨️ Keyboard Navigation")
    st.markdown("All interactive elements should be keyboard accessible")
    
    st.info("💡 Try pressing Tab to navigate through the elements below")
    
    # Demo buttons
    st.subheader("Buttons with Focus Indicators")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Primary Button", key="btn1", use_container_width=True):
            st.success("Primary button clicked!")
    
    with col2:
        if st.button("Secondary Button", key="btn2", use_container_width=True):
            st.info("Secondary button clicked!")
    
    with col3:
        if st.button("Tertiary Button", key="btn3", use_container_width=True):
            st.warning("Tertiary button clicked!")
    
    # Demo inputs
    st.subheader("Form Inputs")
    name = st.text_input("Name", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    
    # Demo select
    option = st.selectbox("Choose an option", ["Option 1", "Option 2", "Option 3"])
    
    # Keyboard shortcuts info
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        **Standard Keyboard Navigation:**
        
        - **Tab:** Move to next focusable element
        - **Shift + Tab:** Move to previous focusable element
        - **Enter/Space:** Activate buttons and links
        - **Arrow Keys:** Navigate within components
        - **Esc:** Close modals and dropdowns
        
        **Focus Indicators:**
        - All interactive elements show a visible focus ring
        - Focus ring color matches theme
        - 2px outline with 2px offset for clarity
        """)


def demo_aria_labels():
    """Demo ARIA labels and attributes"""
    st.header("🏷️ ARIA Labels and Attributes")
    st.markdown("Proper ARIA labels help screen readers understand the UI")
    
    # Button ARIA
    st.subheader("Button with ARIA")
    button_aria = ARIAHelper.get_button_aria(
        label="Save document",
        pressed=False,
        disabled=False
    )
    st.code(f'<button {button_aria}>Save</button>', language="html")
    
    # Input ARIA
    st.subheader("Input with ARIA")
    input_aria = ARIAHelper.get_input_aria(
        label="Email address",
        required=True,
        invalid=False,
        describedby="email-help"
    )
    st.code(f'<input type="email" {input_aria} />', language="html")
    
    # Dialog ARIA
    st.subheader("Dialog with ARIA")
    dialog_aria = ARIAHelper.get_dialog_aria(
        label="Confirm deletion",
        modal=True
    )
    st.code(f'<div {dialog_aria}>...</div>', language="html")
    
    # Alert ARIA
    st.subheader("Alert with ARIA")
    alert_aria = ARIAHelper.get_alert_aria(live="polite")
    st.code(f'<div {alert_aria}>Success message</div>', language="html")
    
    # Navigation ARIA
    st.subheader("Navigation with ARIA")
    nav_aria = ARIAHelper.get_navigation_aria(label="Main navigation")
    st.code(f'<nav {nav_aria}>...</nav>', language="html")
    
    with st.expander("ℹ️ About ARIA"):
        st.markdown("""
        **ARIA (Accessible Rich Internet Applications):**
        
        - **aria-label:** Provides accessible name for element
        - **aria-describedby:** References element that describes this one
        - **aria-pressed:** Indicates toggle button state
        - **aria-expanded:** Indicates if element is expanded
        - **aria-invalid:** Indicates validation error
        - **aria-required:** Indicates required field
        - **aria-live:** Announces dynamic content changes
        - **role:** Defines element's purpose
        
        **Best Practices:**
        - Use semantic HTML first
        - Add ARIA only when needed
        - Test with screen readers
        """)


def demo_focus_management():
    """Demo focus management features"""
    st.header("🎯 Focus Management")
    st.markdown("Proper focus management improves keyboard navigation")
    
    # Focus trap demo
    st.subheader("Focus Trap (for Modals)")
    st.markdown("Focus should be trapped inside modals to prevent navigation outside")
    
    if st.button("Show Focus Trap Example"):
        st.code(FocusManager.get_focus_trap_js("modal-container"), language="javascript")
    
    # Focus indicator CSS
    st.subheader("Enhanced Focus Indicators")
    with st.expander("View CSS"):
        st.code(FocusManager.get_focus_indicator_css(), language="css")
    
    # Demo focus ring
    st.subheader("Focus Ring Demo")
    st.markdown("""
    <div class="focus-ring" tabindex="0" style="padding: 20px; background: #f3f4f6; 
                                                  border-radius: 8px; cursor: pointer;">
        Click or Tab to this element to see the focus ring
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ About Focus Management"):
        st.markdown("""
        **Focus Management Best Practices:**
        
        - **Visible Focus Indicators:** Always show where focus is
        - **Logical Tab Order:** Follow visual flow
        - **Focus Trapping:** Keep focus in modals
        - **Focus Restoration:** Return focus after closing modals
        - **Skip Links:** Allow skipping repetitive content
        
        **High Contrast Mode:**
        - Enhanced focus indicators in high contrast mode
        - 3px outline for better visibility
        """)


def demo_screen_reader():
    """Demo screen reader support"""
    st.header("📢 Screen Reader Support")
    st.markdown("Screen readers help visually impaired users navigate the UI")
    
    # Screen reader only content
    st.subheader("Screen Reader Only Content")
    sr_text = ScreenReaderHelper.wrap_sr_only("This text is only visible to screen readers")
    st.markdown(f"<p>Visible text {sr_text}</p>", unsafe_allow_html=True)
    st.code(sr_text, language="html")
    
    # Live region
    st.subheader("Live Region for Announcements")
    live_region = ScreenReaderHelper.get_live_region_html("announcements", "polite")
    st.code(live_region, language="html")
    
    # Announce message
    if st.button("Announce Message"):
        announcement = ScreenReaderHelper.announce("announcements", "Form submitted successfully")
        st.markdown(announcement, unsafe_allow_html=True)
        st.success("Message announced to screen readers!")
    
    # SR-only CSS
    st.subheader("Screen Reader Only CSS")
    with st.expander("View CSS"):
        st.code(ScreenReaderHelper.get_sr_only_css(), language="css")
    
    with st.expander("ℹ️ About Screen Readers"):
        st.markdown("""
        **Screen Reader Support:**
        
        - **SR-Only Content:** Hidden visually but read by screen readers
        - **Live Regions:** Announce dynamic content changes
        - **Semantic HTML:** Use proper HTML elements
        - **Alt Text:** Provide for all images
        - **Descriptive Links:** Avoid "click here"
        
        **Testing:**
        - NVDA (Windows, free)
        - JAWS (Windows, commercial)
        - VoiceOver (macOS/iOS, built-in)
        - TalkBack (Android, built-in)
        """)


def demo_text_scaling():
    """Demo text scaling support"""
    st.header("📏 Text Scaling Support")
    st.markdown("UI should remain usable when text is scaled up to 200%")
    
    # Show responsive text CSS
    st.subheader("Responsive Text Scaling CSS")
    with st.expander("View CSS"):
        st.code(TextScalingHelper.get_responsive_text_css(), language="css")
    
    # Demo different text sizes
    st.subheader("Text at Different Scales")
    
    scale = st.slider("Text Scale", 100, 200, 100, 10, format="%d%%")
    
    st.markdown(f"""
    <div style="font-size: {scale}%;">
        <h3>Heading at {scale}%</h3>
        <p>This is body text at {scale}% scale. The layout should remain usable 
           and readable even at 200% scale.</p>
        <button style="padding: 10px 20px; font-size: 1em;">Button</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Touch target size
    st.subheader("Minimum Touch Target Size")
    st.markdown("All interactive elements should be at least 44x44 pixels")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <button style="min-width: 44px; min-height: 44px; background: #3b82f6; 
                       color: white; border: none; border-radius: 4px; cursor: pointer;">
            ✓
        </button>
        <p style="font-size: 12px; margin-top: 5px;">44x44px (Good)</p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <button style="min-width: 32px; min-height: 32px; background: #ef4444; 
                       color: white; border: none; border-radius: 4px; cursor: pointer;">
            ✗
        </button>
        <p style="font-size: 12px; margin-top: 5px;">32x32px (Too small)</p>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <button style="min-width: 60px; min-height: 60px; background: #22c55e; 
                       color: white; border: none; border-radius: 4px; cursor: pointer;">
            ✓✓
        </button>
        <p style="font-size: 12px; margin-top: 5px;">60x60px (Excellent)</p>
        """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ About Text Scaling"):
        st.markdown("""
        **Text Scaling Requirements:**
        
        - **WCAG 2.1 Success Criterion 1.4.4:** Text can be resized up to 200%
        - **No loss of content or functionality** at 200% zoom
        - **Responsive units:** Use rem/em instead of px
        - **Flexible layouts:** Avoid fixed widths
        - **Touch targets:** Minimum 44x44 pixels
        
        **User Preferences:**
        - Respect `prefers-reduced-motion`
        - Respect `prefers-contrast`
        - Respect `prefers-color-scheme`
        """)


def demo_theme_audit():
    """Demo theme accessibility audit"""
    st.header("📊 Theme Accessibility Audit")
    st.markdown("Audit themes for accessibility compliance")
    
    try:
        # Load theme manager
        theme_manager = ThemeManager()
        
        # Select theme to audit
        theme_names = list(theme_manager.themes.keys())
        selected_theme = st.selectbox("Select theme to audit", theme_names)
        
        if st.button("Run Accessibility Audit", type="primary"):
            # Get theme data
            theme = theme_manager.get_theme(selected_theme)
            theme_data = {
                'name': theme.name,
                'colors': {
                    'foreground': theme.colors.foreground,
                    'background': theme.colors.background,
                    'primary': theme.colors.primary,
                    'primary_foreground': theme.colors.primary_foreground,
                    'secondary': theme.colors.secondary,
                    'secondary_foreground': theme.colors.secondary_foreground,
                    'muted': theme.colors.muted,
                    'muted_foreground': theme.colors.muted_foreground,
                }
            }
            
            # Run audit
            auditor = AccessibilityAuditor()
            report = auditor.audit_theme(theme_data)
            
            # Display report
            st.markdown(auditor.generate_report_html(report), unsafe_allow_html=True)
            
            # Download report
            if st.button("Download Report"):
                st.download_button(
                    label="Download HTML Report",
                    data=auditor.generate_report_html(report),
                    file_name=f"accessibility_report_{selected_theme}.html",
                    mime="text/html"
                )
    
    except Exception as e:
        st.error(f"Error loading themes: {e}")
        st.info("Make sure theme files exist in theming/themes/ directory")


def demo_colorblind_themes():
    """Demo colorblind-friendly theme generation"""
    st.header("🎨 Colorblind-Friendly Themes")
    st.markdown("Generate themes optimized for color blindness")
    
    try:
        # Load theme manager
        theme_manager = ThemeManager()
        
        # Select base theme
        theme_names = list(theme_manager.themes.keys())
        base_theme_name = st.selectbox("Select base theme", theme_names)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate High Contrast Theme", use_container_width=True):
                theme = theme_manager.get_theme(base_theme_name)
                theme_data = {
                    'name': theme.name,
                    'display_name': theme.display_name,
                    'colors': vars(theme.colors)
                }
                
                hc_theme = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(theme_data)
                
                st.success(f"Generated: {hc_theme['display_name']}")
                st.json(hc_theme['colors'])
        
        with col2:
            if st.button("Generate Colorblind-Safe Theme", use_container_width=True):
                theme = theme_manager.get_theme(base_theme_name)
                theme_data = {
                    'name': theme.name,
                    'display_name': theme.display_name,
                    'colors': vars(theme.colors)
                }
                
                cb_theme = ColorBlindnessFriendlyThemeGenerator.generate_colorblind_safe_theme(theme_data)
                
                st.success(f"Generated: {cb_theme['display_name']}")
                st.json(cb_theme['colors'])
        
        with st.expander("ℹ️ About Colorblind-Friendly Themes"):
            st.markdown("""
            **High Contrast Themes:**
            - Pure black and white for maximum contrast
            - Highly saturated, distinct colors
            - Meets WCAG AAA standards
            - Ideal for low vision users
            
            **Colorblind-Safe Themes:**
            - Uses blue and orange (safe for most types)
            - Avoids red-green combinations
            - Includes patterns and shapes
            - Works for all types of color blindness
            
            **Best Practices:**
            - Don't rely solely on color
            - Use text labels and icons
            - Provide multiple visual cues
            - Test with simulation tools
            """)
    
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
