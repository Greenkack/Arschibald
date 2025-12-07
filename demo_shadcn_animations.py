"""
Demo: shadcn/ui Animations and Transitions

Demonstrates all animation and transition features including:
- Base transitions for interactive elements
- Fade-in animations
- Slide animations
- Skeleton loaders
- Layout shift prevention
"""

import streamlit as st
import time
from utils.shadcn_animations import (
    inject_all_animations,
    inject_base_transitions,
    inject_fade_in_animations,
    inject_slide_animations,
    inject_skeleton_loaders,
    inject_layout_shift_prevention,
    create_skeleton_loader,
    show_loading_skeleton,
    with_fade_in,
    prevent_layout_shift,
    AnimationManager
)
from theming.theme_manager import ThemeManager

# Page config
st.set_page_config(
    page_title="shadcn/ui Animations Demo",
    page_icon="",
    layout="wide"
)

# Initialize theme manager
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager

# Inject all animations
if 'animations_injected' not in st.session_state:
    inject_all_animations(theme_manager)
    st.session_state.animations_injected = True

# Title
st.title(" shadcn/ui Animations & Transitions Demo")
st.markdown("Comprehensive demonstration of all animation features")

# Tabs for different animation types
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Base Transitions",
    " Fade-In Animations",
    " Slide Animations",
    "⏳ Skeleton Loaders",
    " Layout Stability",
    " Complete Examples"
])

# Tab 1: Base Transitions
with tab1:
    st.header("Base Transitions")
    st.markdown("All interactive elements have smooth transitions (200-300ms)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Buttons")
        st.markdown("Hover over buttons to see smooth transitions")
        st.button("Primary Button", key="btn1")
        st.button("Secondary Button", key="btn2", type="secondary")
        
        st.subheader("Inputs")
        st.text_input("Text Input", placeholder="Focus to see transition")
        st.number_input("Number Input", value=0)
        
        st.subheader("Checkboxes & Radio")
        st.checkbox("Checkbox with transition")
        st.radio("Radio buttons", ["Option 1", "Option 2", "Option 3"])
    
    with col2:
        st.subheader("Sliders")
        st.slider("Slider with transition", 0, 100, 50)
        
        st.subheader("Select Boxes")
        st.selectbox("Select with transition", ["Option A", "Option B", "Option C"])
        st.multiselect("Multi-select", ["Item 1", "Item 2", "Item 3"])
        
        st.subheader("Text Area")
        st.text_area("Text area with focus transition", placeholder="Type here...")
    
    st.divider()
    
    st.subheader("Animation Timing")
    anim_mgr = AnimationManager(theme_manager)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.code(f"Fast: {anim_mgr.get_transition('fast')}")
    with col2:
        st.code(f"Base: {anim_mgr.get_transition('base')}")
    with col3:
        st.code(f"Slow: {anim_mgr.get_transition('slow')}")

# Tab 2: Fade-In Animations
with tab2:
    st.header("Fade-In Animations")
    st.markdown("Content appears with smooth fade-in effects")
    
    if st.button("Trigger Fade-In Animations", key="fade_trigger"):
        st.session_state.show_fade_demos = True
    
    if st.session_state.get('show_fade_demos'):
        st.subheader("Different Fade-In Directions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Fade In Up**")
            st.markdown(
                '<div class="animate-fade-in-up" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Content fades in from bottom</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown("**Fade In Down**")
            st.markdown(
                '<div class="animate-fade-in-down" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Content fades in from top</div>',
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown("**Fade In Scale**")
            st.markdown(
                '<div class="animate-fade-in-scale" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Content fades in with scale</div>',
                unsafe_allow_html=True
            )
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Fade In Left**")
            st.markdown(
                '<div class="animate-fade-in-left" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Content fades in from left</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown("**Fade In Right**")
            st.markdown(
                '<div class="animate-fade-in-right" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Content fades in from right</div>',
                unsafe_allow_html=True
            )
        
        st.divider()
        
        st.subheader("Staggered Animations")
        st.markdown("List items appear with staggered timing")
        
        st.markdown('<div class="animate-stagger">', unsafe_allow_html=True)
        for i in range(5):
            st.markdown(
                f'<div style="padding: 1rem; margin-bottom: 0.5rem; background: #f4f4f5; border-radius: 0.5rem;">List Item {i+1}</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Slide Animations
with tab3:
    st.header("Slide Animations")
    st.markdown("Navigation elements slide in smoothly")
    
    if st.button("Trigger Slide Animations", key="slide_trigger"):
        st.session_state.show_slide_demos = True
    
    if st.session_state.get('show_slide_demos'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Slide In Left**")
            st.markdown(
                '<div class="animate-slide-in-left" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Slides in from left</div>',
                unsafe_allow_html=True
            )
            
            st.markdown("**Slide Down**")
            st.markdown(
                '<div class="animate-slide-down" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center; margin-top: 1rem;">Slides down from top</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown("**Slide In Right**")
            st.markdown(
                '<div class="animate-slide-in-right" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Slides in from right</div>',
                unsafe_allow_html=True
            )
            
            st.markdown("**Slide Up**")
            st.markdown(
                '<div class="animate-slide-up" style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center; margin-top: 1rem;">Slides up from bottom</div>',
                unsafe_allow_html=True
            )

# Tab 4: Skeleton Loaders
with tab4:
    st.header("Skeleton Loaders")
    st.markdown("Animated loading states for better UX")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Individual Skeletons")
        
        st.markdown("**Text Skeleton (Pulse)**")
        create_skeleton_loader('text', 'pulse', count=3)
        
        st.markdown("**Heading Skeleton (Shimmer)**")
        create_skeleton_loader('heading', 'shimmer')
        
        st.markdown("**Avatar Skeleton (Wave)**")
        create_skeleton_loader('avatar', 'wave')
        
        st.markdown("**Button Skeleton**")
        create_skeleton_loader('button', 'pulse')
        
        st.markdown("**Card Skeleton**")
        create_skeleton_loader('card', 'shimmer')
    
    with col2:
        st.subheader("Loading Patterns")
        
        st.markdown("**Card Loading Pattern**")
        show_loading_skeleton('card', count=2)
        
        st.markdown("**List Loading Pattern**")
        show_loading_skeleton('list', count=3)
    
    st.divider()
    
    st.subheader("Interactive Loading Demo")
    
    if st.button("Simulate Loading", key="loading_demo"):
        st.session_state.demo_loading = True
        st.session_state.demo_loaded = False
    
    if st.session_state.get('demo_loading'):
        show_loading_skeleton('card', count=3)
        time.sleep(2)
        st.session_state.demo_loading = False
        st.session_state.demo_loaded = True
        st.rerun()
    
    if st.session_state.get('demo_loaded'):
        st.success(" Content loaded successfully!")
        for i in range(3):
            st.markdown(
                f'<div class="animate-fade-in-up" style="padding: 1.5rem; margin-bottom: 1rem; background: #f4f4f5; border-radius: 0.5rem;">Card {i+1} - Loaded Content</div>',
                unsafe_allow_html=True
            )

# Tab 5: Layout Stability
with tab5:
    st.header("Layout Shift Prevention")
    st.markdown("Techniques to prevent jarring layout changes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Aspect Ratio Containers")
        st.markdown("Images maintain aspect ratio without layout shift")
        
        st.markdown(
            '''
            <div class="aspect-ratio-16-9" style="background: #f4f4f5; border-radius: 0.5rem;">
                <div class="aspect-ratio-content" style="display: flex; align-items: center; justify-content: center; color: #71717a;">
                    16:9 Aspect Ratio
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            '''
            <div class="aspect-ratio-4-3" style="background: #f4f4f5; border-radius: 0.5rem;">
                <div class="aspect-ratio-content" style="display: flex; align-items: center; justify-content: center; color: #71717a;">
                    4:3 Aspect Ratio
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    with col2:
        st.subheader("Stable Heights")
        st.markdown("Reserve minimum height for dynamic content")
        
        def render_dynamic():
            st.markdown(
                '<div style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem;">Dynamic content with stable height</div>',
                unsafe_allow_html=True
            )
        
        prevent_layout_shift(render_dynamic, min_height='200px')
    
    st.divider()
    
    st.subheader("Stable Grid Layout")
    st.markdown(
        '''
        <div class="stable-grid">
            <div style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Grid Item 1</div>
            <div style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Grid Item 2</div>
            <div style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">Grid Item 3</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Tab 6: Complete Examples
with tab6:
    st.header("Complete Examples")
    st.markdown("Real-world usage patterns combining multiple animation features")
    
    st.subheader("Example 1: Loading State with Skeleton")
    
    if st.button("Load Data", key="example1"):
        st.session_state.example1_loading = True
        st.session_state.example1_loaded = False
    
    if st.session_state.get('example1_loading'):
        show_loading_skeleton('list', count=4)
        time.sleep(1.5)
        st.session_state.example1_loading = False
        st.session_state.example1_loaded = True
        st.rerun()
    
    if st.session_state.get('example1_loaded'):
        def render_list():
            items = ["User Profile", "Dashboard", "Settings", "Analytics"]
            for item in items:
                st.markdown(
                    f'<div style="padding: 1rem; margin-bottom: 0.5rem; background: #f4f4f5; border-radius: 0.5rem;"> {item}</div>',
                    unsafe_allow_html=True
                )
        
        with_fade_in(render_list, direction='up')
    
    st.divider()
    
    st.subheader("Example 2: Animated Card Grid")
    
    if st.button("Show Cards", key="example2"):
        st.session_state.show_cards = True
    
    if st.session_state.get('show_cards'):
        st.markdown('<div class="animate-stagger stable-grid">', unsafe_allow_html=True)
        
        for i in range(6):
            st.markdown(
                f'''
                <div style="padding: 2rem; background: #f4f4f5; border-radius: 0.5rem; text-align: center;">
                    <h3 style="margin: 0 0 0.5rem 0;">Card {i+1}</h3>
                    <p style="margin: 0; color: #71717a;">Animated card content</p>
                </div>
                ''',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("Example 3: Form with Loading State")
    
    with st.form("demo_form"):
        st.text_input("Name")
        st.text_input("Email")
        st.text_area("Message")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.session_state.form_submitting = True
    
    if st.session_state.get('form_submitting'):
        with st.spinner("Submitting..."):
            time.sleep(1)
            st.session_state.form_submitting = False
            st.session_state.form_submitted = True
            st.rerun()
    
    if st.session_state.get('form_submitted'):
        st.markdown(
            '<div class="animate-fade-in-scale" style="padding: 1rem; background: #22c55e; color: white; border-radius: 0.5rem; text-align: center;"> Form submitted successfully!</div>',
            unsafe_allow_html=True
        )

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #71717a; padding: 2rem;">
        <p>shadcn/ui Animations Demo</p>
        <p>All animations use CSS3 with hardware acceleration for smooth performance</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar info
with st.sidebar:
    st.header("Animation Info")
    
    st.markdown("**Transition Speeds:**")
    anim_mgr = AnimationManager(theme_manager)
    st.code(f"Fast: {anim_mgr.get_transition('fast')}")
    st.code(f"Base: {anim_mgr.get_transition('base')}")
    st.code(f"Slow: {anim_mgr.get_transition('slow')}")
    
    st.markdown("**Easing Function:**")
    st.code(anim_mgr.get_easing())
    
    st.divider()
    
    st.markdown("**Features:**")
    st.markdown("""
    -  Base transitions
    -  Fade-in animations
    -  Slide animations
    -  Skeleton loaders
    -  Layout stability
    """)
