"""
shadcn/ui Animations and Transitions

Provides comprehensive animation and transition utilities for the shadcn/ui design system.
Includes CSS transitions, fade-in animations, slide animations, skeleton loaders,
and layout shift prevention.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
"""

import streamlit as st
from typing import Optional, Literal, Dict, Any
from theming.theme_manager import ThemeManager


class AnimationManager:
    """Manages animations and transitions for shadcn/ui components"""
    
    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        """
        Initialize AnimationManager
        
        Args:
            theme_manager: Optional ThemeManager instance for accessing animation tokens
        """
        self.theme_manager = theme_manager
    
    def get_transition(self, speed: Literal['fast', 'base', 'slow'] = 'base') -> str:
        """
        Get transition timing from theme
        
        Args:
            speed: Transition speed ('fast', 'base', or 'slow')
            
        Returns:
            Transition timing string
        """
        if self.theme_manager:
            return self.theme_manager.get_token(f'animations.transition_{speed}')
        
        # Fallback values
        transitions = {
            'fast': '150ms cubic-bezier(0.4, 0, 0.2, 1)',
            'base': '200ms cubic-bezier(0.4, 0, 0.2, 1)',
            'slow': '300ms cubic-bezier(0.4, 0, 0.2, 1)'
        }
        return transitions.get(speed, transitions['base'])
    
    def get_easing(self) -> str:
        """Get default easing function from theme"""
        if self.theme_manager:
            return self.theme_manager.get_token('animations.easing_default')
        return 'cubic-bezier(0.4, 0, 0.2, 1)'


def inject_base_transitions(theme_manager: Optional[ThemeManager] = None) -> None:
    """
    Inject base CSS transitions for all interactive elements
    
    This function adds smooth transitions to all interactive elements
    including buttons, inputs, cards, and other UI components.
    
    Args:
        theme_manager: Optional ThemeManager for accessing animation tokens
        
    Requirements: 11.1
    """
    anim_mgr = AnimationManager(theme_manager)
    
    transition_fast = anim_mgr.get_transition('fast')
    transition_base = anim_mgr.get_transition('base')
    transition_slow = anim_mgr.get_transition('slow')
    easing = anim_mgr.get_easing()
    
    css = f"""
    <style>
    /* Base Transitions for Interactive Elements */
    
    /* Buttons */
    button, .stButton > button {{
        transition: all {transition_base} !important;
    }}
    
    button:hover, .stButton > button:hover {{
        transform: translateY(-1px);
        transition: all {transition_fast} !important;
    }}
    
    button:active, .stButton > button:active {{
        transform: translateY(0);
        transition: all {transition_fast} !important;
    }}
    
    /* Inputs */
    input, textarea, select,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        transition: border-color {transition_base}, 
                    box-shadow {transition_base},
                    background-color {transition_base} !important;
    }}
    
    input:focus, textarea:focus, select:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {{
        transition: border-color {transition_fast}, 
                    box-shadow {transition_fast} !important;
    }}
    
    /* Checkboxes and Radio Buttons */
    .stCheckbox, .stRadio {{
        transition: all {transition_base} !important;
    }}
    
    /* Sliders */
    .stSlider {{
        transition: all {transition_base} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        transition: all {transition_base} !important;
    }}
    
    /* Cards and Containers */
    .shadcn-card, .stContainer {{
        transition: box-shadow {transition_base},
                    transform {transition_base},
                    background-color {transition_base} !important;
    }}
    
    /* Links */
    a {{
        transition: color {transition_base},
                    opacity {transition_base} !important;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        transition: background-color {transition_base} !important;
    }}
    
    /* Tooltips */
    [data-baseweb="tooltip"] {{
        transition: opacity {transition_fast},
                    transform {transition_fast} !important;
    }}
    
    /* Modals and Dialogs */
    .stModal {{
        transition: opacity {transition_base},
                    transform {transition_base} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        transition: transform {transition_slow},
                    width {transition_slow} !important;
    }}
    
    /* Smooth scrolling */
    html {{
        scroll-behavior: smooth;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def inject_fade_in_animations() -> None:
    """
    Inject fade-in animations for newly loaded content
    
    Provides smooth fade-in effects for content that appears dynamically.
    
    Requirements: 11.2
    """
    css = """
    <style>
    /* Fade-In Animations */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Apply fade-in to main content */
    .main .block-container {
        animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Apply fade-in to cards */
    .shadcn-card {
        animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Apply fade-in to alerts */
    .shadcn-alert {
        animation: fadeInDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Apply fade-in to modals */
    .stModal {
        animation: fadeInScale 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Utility classes for manual application */
    .animate-fade-in {
        animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-fade-in-up {
        animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-fade-in-down {
        animation: fadeInDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-fade-in-left {
        animation: fadeInLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-fade-in-right {
        animation: fadeInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-fade-in-scale {
        animation: fadeInScale 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Stagger animations for lists */
    .animate-stagger > * {
        animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-stagger > *:nth-child(1) { animation-delay: 0.05s; }
    .animate-stagger > *:nth-child(2) { animation-delay: 0.1s; }
    .animate-stagger > *:nth-child(3) { animation-delay: 0.15s; }
    .animate-stagger > *:nth-child(4) { animation-delay: 0.2s; }
    .animate-stagger > *:nth-child(5) { animation-delay: 0.25s; }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def inject_slide_animations() -> None:
    """
    Inject slide animations for sidebar and drawer components
    
    Provides smooth slide-in/out effects for navigation elements.
    
    Requirements: 11.3
    """
    css = """
    <style>
    /* Slide Animations */
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutLeft {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(-100%);
            opacity: 0;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Sidebar slide animation */
    [data-testid="stSidebar"] {
        animation: slideInLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] {
        animation: slideOutLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Drawer animations */
    .shadcn-drawer-left {
        animation: slideInLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .shadcn-drawer-right {
        animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .shadcn-drawer-top {
        animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .shadcn-drawer-bottom {
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Dropdown menu slide */
    .shadcn-dropdown-menu {
        animation: slideDown 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Accordion slide */
    .shadcn-accordion-content {
        animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Utility classes */
    .animate-slide-in-left {
        animation: slideInLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-slide-in-right {
        animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-slide-down {
        animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-slide-up {
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def inject_skeleton_loaders(theme_manager: Optional[ThemeManager] = None) -> None:
    """
    Inject skeleton loader animations for loading states
    
    Provides animated skeleton screens during content loading.
    
    Args:
        theme_manager: Optional ThemeManager for accessing color tokens
        
    Requirements: 11.4
    """
    # Get colors from theme or use defaults
    if theme_manager:
        bg_color = theme_manager.get_token('colors.muted')
        highlight_color = theme_manager.get_token('colors.background')
    else:
        bg_color = '#f4f4f5'
        highlight_color = '#ffffff'
    
    css = f"""
    <style>
    /* Skeleton Loader Animations */
    
    @keyframes skeleton-pulse {{
        0%, 100% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0.5;
        }}
    }}
    
    @keyframes skeleton-shimmer {{
        0% {{
            background-position: -200% 0;
        }}
        100% {{
            background-position: 200% 0;
        }}
    }}
    
    @keyframes skeleton-wave {{
        0% {{
            transform: translateX(-100%);
        }}
        100% {{
            transform: translateX(100%);
        }}
    }}
    
    /* Base skeleton styles */
    .skeleton {{
        background-color: {bg_color};
        border-radius: 0.375rem;
        animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    
    .skeleton-shimmer {{
        background: linear-gradient(
            90deg,
            {bg_color} 0%,
            {highlight_color} 50%,
            {bg_color} 100%
        );
        background-size: 200% 100%;
        animation: skeleton-shimmer 2s ease-in-out infinite;
    }}
    
    .skeleton-wave {{
        position: relative;
        overflow: hidden;
        background-color: {bg_color};
    }}
    
    .skeleton-wave::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
            90deg,
            transparent,
            {highlight_color},
            transparent
        );
        animation: skeleton-wave 2s ease-in-out infinite;
    }}
    
    /* Skeleton variants */
    .skeleton-text {{
        height: 1rem;
        margin-bottom: 0.5rem;
    }}
    
    .skeleton-text-sm {{
        height: 0.75rem;
        margin-bottom: 0.375rem;
    }}
    
    .skeleton-text-lg {{
        height: 1.25rem;
        margin-bottom: 0.625rem;
    }}
    
    .skeleton-heading {{
        height: 2rem;
        margin-bottom: 1rem;
        width: 60%;
    }}
    
    .skeleton-avatar {{
        width: 3rem;
        height: 3rem;
        border-radius: 9999px;
    }}
    
    .skeleton-avatar-sm {{
        width: 2rem;
        height: 2rem;
        border-radius: 9999px;
    }}
    
    .skeleton-avatar-lg {{
        width: 4rem;
        height: 4rem;
        border-radius: 9999px;
    }}
    
    .skeleton-button {{
        height: 2.5rem;
        width: 6rem;
        border-radius: 0.375rem;
    }}
    
    .skeleton-card {{
        height: 12rem;
        border-radius: 0.5rem;
    }}
    
    .skeleton-image {{
        width: 100%;
        padding-bottom: 56.25%; /* 16:9 aspect ratio */
        border-radius: 0.5rem;
    }}
    
    /* Loading container */
    .skeleton-container {{
        padding: 1rem;
    }}
    
    /* Prevent layout shift during loading */
    .skeleton-preserve-space {{
        min-height: inherit;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def inject_layout_shift_prevention() -> None:
    """
    Inject CSS to prevent layout shifts during content loading
    
    Ensures stable layouts by reserving space for content before it loads.
    
    Requirements: 11.5
    """
    css = """
    <style>
    /* Layout Shift Prevention */
    
    /* Reserve space for images */
    img {{
        max-width: 100%;
        height: auto;
        display: block;
    }}
    
    /* Aspect ratio containers */
    .aspect-ratio-16-9 {{
        position: relative;
        width: 100%;
        padding-bottom: 56.25%;
    }}
    
    .aspect-ratio-4-3 {{
        position: relative;
        width: 100%;
        padding-bottom: 75%;
    }}
    
    .aspect-ratio-1-1 {{
        position: relative;
        width: 100%;
        padding-bottom: 100%;
    }}
    
    .aspect-ratio-content {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }}
    
    /* Prevent content jump */
    .main .block-container {{
        min-height: 100vh;
    }}
    
    /* Stable container heights */
    .stable-height {{
        min-height: 200px;
    }}
    
    /* Font loading optimization */
    @font-face {{
        font-display: swap;
    }}
    
    /* Prevent flash of unstyled content */
    .no-fouc {{
        opacity: 0;
        animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        animation-delay: 0.1s;
    }}
    
    /* Grid layout stability */
    .stable-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }}
    
    /* Flex layout stability */
    .stable-flex {{
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    /* Prevent button size changes */
    button, .stButton > button {{
        min-width: fit-content;
        white-space: nowrap;
    }}
    
    /* Prevent input size changes */
    input, textarea, select {{
        width: 100%;
        box-sizing: border-box;
    }}
    
    /* Stable sidebar width */
    [data-testid="stSidebar"] {{
        min-width: 244px;
        max-width: 550px;
    }}
    
    /* Prevent scrollbar layout shift */
    html {{
        overflow-y: scroll;
    }}
    
    /* Smooth height transitions */
    .smooth-height {{
        transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    /* Content visibility optimization */
    .lazy-content {{
        content-visibility: auto;
        contain-intrinsic-size: 500px;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def inject_all_animations(theme_manager: Optional[ThemeManager] = None) -> None:
    """
    Inject all animation and transition styles at once
    
    Convenience function to inject all animation utilities in one call.
    
    Args:
        theme_manager: Optional ThemeManager for accessing theme tokens
        
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
    """
    inject_base_transitions(theme_manager)
    inject_fade_in_animations()
    inject_slide_animations()
    inject_skeleton_loaders(theme_manager)
    inject_layout_shift_prevention()


def create_skeleton_loader(
    variant: Literal['text', 'heading', 'avatar', 'button', 'card', 'image'] = 'text',
    animation: Literal['pulse', 'shimmer', 'wave'] = 'pulse',
    count: int = 1,
    width: Optional[str] = None,
    height: Optional[str] = None
) -> None:
    """
    Create a skeleton loader component
    
    Args:
        variant: Type of skeleton loader
        animation: Animation style
        count: Number of skeleton elements to render
        width: Custom width (CSS value)
        height: Custom height (CSS value)
        
    Requirements: 11.4
    """
    animation_class = f'skeleton-{animation}' if animation != 'pulse' else 'skeleton'
    variant_class = f'skeleton-{variant}'
    
    style = ''
    if width:
        style += f'width: {width};'
    if height:
        style += f'height: {height};'
    
    html = ''
    for _ in range(count):
        html += f'<div class="{animation_class} {variant_class}" style="{style}"></div>'
    
    st.markdown(html, unsafe_allow_html=True)


def with_fade_in(content_func, direction: Literal['up', 'down', 'left', 'right', 'scale'] = 'up'):
    """
    Decorator to wrap content with fade-in animation
    
    Args:
        content_func: Function that renders content
        direction: Direction of fade-in animation
        
    Requirements: 11.2
    """
    animation_class = f'animate-fade-in-{direction}' if direction != 'scale' else 'animate-fade-in-scale'
    
    html_start = f'<div class="{animation_class}">'
    html_end = '</div>'
    
    st.markdown(html_start, unsafe_allow_html=True)
    content_func()
    st.markdown(html_end, unsafe_allow_html=True)


# Convenience functions for common use cases

def show_loading_skeleton(
    skeleton_type: Literal['card', 'list', 'table', 'form'] = 'card',
    count: int = 3
) -> None:
    """
    Show a loading skeleton for common UI patterns
    
    Args:
        skeleton_type: Type of skeleton pattern to show
        count: Number of items to show
        
    Requirements: 11.4
    """
    if skeleton_type == 'card':
        for _ in range(count):
            create_skeleton_loader('card', 'shimmer')
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    
    elif skeleton_type == 'list':
        for _ in range(count):
            col1, col2 = st.columns([1, 4])
            with col1:
                create_skeleton_loader('avatar', 'pulse')
            with col2:
                create_skeleton_loader('heading', 'shimmer')
                create_skeleton_loader('text', 'shimmer', count=2)
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    
    elif skeleton_type == 'table':
        create_skeleton_loader('heading', 'shimmer', width='40%')
        for _ in range(count):
            create_skeleton_loader('text', 'pulse', count=1, height='3rem')
    
    elif skeleton_type == 'form':
        for _ in range(count):
            create_skeleton_loader('text', 'shimmer', width='30%', height='1rem')
            create_skeleton_loader('button', 'pulse', height='2.5rem')
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)


def prevent_layout_shift(content_func, min_height: str = '200px'):
    """
    Wrap content to prevent layout shifts
    
    Args:
        content_func: Function that renders content
        min_height: Minimum height to reserve
        
    Requirements: 11.5
    """
    st.markdown(
        f'<div class="stable-height" style="min-height: {min_height};">',
        unsafe_allow_html=True
    )
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)
