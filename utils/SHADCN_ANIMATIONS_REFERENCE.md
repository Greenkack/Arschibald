# shadcn/ui Animations Reference

Complete reference for the shadcn/ui animations and transitions system.

## Overview

The `shadcn_animations.py` module provides comprehensive animation and transition utilities for creating smooth, modern UI experiences. It includes:

- CSS transitions for interactive elements
- Fade-in animations for content
- Slide animations for navigation
- Skeleton loaders for loading states
- Layout shift prevention

## Requirements Coverage

- **11.1**: CSS-Transitions für alle interaktiven Elemente (200-300ms)
- **11.2**: Fade-In-Animationen für neu geladene Inhalte
- **11.3**: Slide-Animationen für Sidebar und Drawer
- **11.4**: Skeleton-Loader während Lade-Vorgängen
- **11.5**: Keine ruckartigen Layout-Shifts

## Quick Start

### Basic Setup

```python
import streamlit as st
from utils.shadcn_animations import inject_all_animations
from theming.theme_manager import ThemeManager

# Initialize theme manager
theme_manager = ThemeManager()

# Inject all animations at once
inject_all_animations(theme_manager)
```

### Individual Injection

```python
from utils.shadcn_animations import (
    inject_base_transitions,
    inject_fade_in_animations,
    inject_slide_animations,
    inject_skeleton_loaders,
    inject_layout_shift_prevention
)

# Inject only what you need
inject_base_transitions(theme_manager)
inject_fade_in_animations()
```

## Core Functions

### inject_all_animations()

Injects all animation styles at once.

```python
def inject_all_animations(theme_manager: Optional[ThemeManager] = None) -> None
```

**Parameters:**
- `theme_manager` (optional): ThemeManager instance for accessing animation tokens

**Example:**
```python
inject_all_animations(theme_manager)
```

### inject_base_transitions()

Adds smooth transitions to all interactive elements (buttons, inputs, cards, etc.).

```python
def inject_base_transitions(theme_manager: Optional[ThemeManager] = None) -> None
```

**Affected Elements:**
- Buttons (hover, active states)
- Inputs (focus states)
- Checkboxes and radio buttons
- Sliders
- Tabs
- Cards and containers
- Links
- Expanders
- Tooltips
- Modals
- Sidebar

**Example:**
```python
inject_base_transitions(theme_manager)

# Now all buttons have smooth transitions
st.button("Click me")  # Smooth hover and click animations
```

### inject_fade_in_animations()

Provides fade-in effects for dynamically appearing content.

```python
def inject_fade_in_animations() -> None
```

**Available Animations:**
- `fadeIn`: Basic fade with slight upward movement
- `fadeInUp`: Fade in from bottom
- `fadeInDown`: Fade in from top
- `fadeInLeft`: Fade in from left
- `fadeInRight`: Fade in from right
- `fadeInScale`: Fade in with scale effect

**Auto-Applied To:**
- Main content blocks
- Cards (`.shadcn-card`)
- Alerts (`.shadcn-alert`)
- Modals (`.stModal`)

**Manual Application:**
```python
inject_fade_in_animations()

# Use utility classes
st.markdown(
    '<div class="animate-fade-in-up">Content here</div>',
    unsafe_allow_html=True
)
```

### inject_slide_animations()

Adds slide-in/out effects for navigation elements.

```python
def inject_slide_animations() -> None
```

**Available Animations:**
- `slideInLeft`: Slide in from left
- `slideInRight`: Slide in from right
- `slideDown`: Slide down from top
- `slideUp`: Slide up from bottom

**Auto-Applied To:**
- Sidebar
- Drawer components
- Dropdown menus
- Accordion content

**Manual Application:**
```python
inject_slide_animations()

# Use utility classes
st.markdown(
    '<div class="animate-slide-in-left">Sidebar content</div>',
    unsafe_allow_html=True
)
```

### inject_skeleton_loaders()

Provides animated skeleton screens for loading states.

```python
def inject_skeleton_loaders(theme_manager: Optional[ThemeManager] = None) -> None
```

**Animation Types:**
- `skeleton-pulse`: Pulsing opacity animation
- `skeleton-shimmer`: Shimmer effect across element
- `skeleton-wave`: Wave effect moving across element

**Skeleton Variants:**
- `skeleton-text`: Text line skeleton
- `skeleton-heading`: Heading skeleton
- `skeleton-avatar`: Circular avatar skeleton
- `skeleton-button`: Button skeleton
- `skeleton-card`: Card skeleton
- `skeleton-image`: Image skeleton with aspect ratio

**Example:**
```python
inject_skeleton_loaders(theme_manager)

# Use skeleton classes
st.markdown(
    '<div class="skeleton-shimmer skeleton-card"></div>',
    unsafe_allow_html=True
)
```

### inject_layout_shift_prevention()

Prevents layout shifts during content loading.

```python
def inject_layout_shift_prevention() -> None
```

**Features:**
- Aspect ratio containers for images
- Stable container heights
- Font loading optimization
- Grid and flex layout stability
- Scrollbar layout shift prevention

**Example:**
```python
inject_layout_shift_prevention()

# Use aspect ratio containers
st.markdown(
    '''
    <div class="aspect-ratio-16-9">
        <img src="image.jpg" class="aspect-ratio-content" />
    </div>
    ''',
    unsafe_allow_html=True
)
```

## Helper Functions

### create_skeleton_loader()

Creates a skeleton loader component.

```python
def create_skeleton_loader(
    variant: Literal['text', 'heading', 'avatar', 'button', 'card', 'image'] = 'text',
    animation: Literal['pulse', 'shimmer', 'wave'] = 'pulse',
    count: int = 1,
    width: Optional[str] = None,
    height: Optional[str] = None
) -> None
```

**Parameters:**
- `variant`: Type of skeleton loader
- `animation`: Animation style
- `count`: Number of skeleton elements
- `width`: Custom width (CSS value)
- `height`: Custom height (CSS value)

**Example:**
```python
# Show loading skeleton
create_skeleton_loader('card', 'shimmer', count=3)

# Custom size
create_skeleton_loader('text', 'pulse', width='80%', height='1.5rem')
```

### show_loading_skeleton()

Shows loading skeletons for common UI patterns.

```python
def show_loading_skeleton(
    skeleton_type: Literal['card', 'list', 'table', 'form'] = 'card',
    count: int = 3
) -> None
```

**Parameters:**
- `skeleton_type`: Type of skeleton pattern
- `count`: Number of items to show

**Example:**
```python
# Show loading state
if st.session_state.get('loading'):
    show_loading_skeleton('list', count=5)
else:
    # Show actual content
    for item in items:
        st.write(item)
```

### with_fade_in()

Decorator to wrap content with fade-in animation.

```python
def with_fade_in(
    content_func,
    direction: Literal['up', 'down', 'left', 'right', 'scale'] = 'up'
)
```

**Parameters:**
- `content_func`: Function that renders content
- `direction`: Direction of fade-in animation

**Example:**
```python
def render_content():
    st.write("This content will fade in")
    st.button("Click me")

with_fade_in(render_content, direction='up')
```

### prevent_layout_shift()

Wraps content to prevent layout shifts.

```python
def prevent_layout_shift(content_func, min_height: str = '200px')
```

**Parameters:**
- `content_func`: Function that renders content
- `min_height`: Minimum height to reserve

**Example:**
```python
def render_dynamic_content():
    # Content that might change size
    st.write(dynamic_data)

prevent_layout_shift(render_dynamic_content, min_height='300px')
```

## AnimationManager Class

Manages animation tokens and provides access to theme-based timing values.

```python
class AnimationManager:
    def __init__(self, theme_manager: Optional[ThemeManager] = None)
    def get_transition(self, speed: Literal['fast', 'base', 'slow'] = 'base') -> str
    def get_easing(self) -> str
```

**Example:**
```python
anim_mgr = AnimationManager(theme_manager)

# Get transition timing
fast_transition = anim_mgr.get_transition('fast')  # '150ms cubic-bezier(...)'
base_transition = anim_mgr.get_transition('base')  # '200ms cubic-bezier(...)'
slow_transition = anim_mgr.get_transition('slow')  # '300ms cubic-bezier(...)'

# Get easing function
easing = anim_mgr.get_easing()  # 'cubic-bezier(0.4, 0, 0.2, 1)'
```

## CSS Utility Classes

### Fade-In Classes

```css
.animate-fade-in          /* Basic fade in */
.animate-fade-in-up       /* Fade in from bottom */
.animate-fade-in-down     /* Fade in from top */
.animate-fade-in-left     /* Fade in from left */
.animate-fade-in-right    /* Fade in from right */
.animate-fade-in-scale    /* Fade in with scale */
.animate-stagger          /* Stagger children animations */
```

### Slide Classes

```css
.animate-slide-in-left    /* Slide in from left */
.animate-slide-in-right   /* Slide in from right */
.animate-slide-down       /* Slide down from top */
.animate-slide-up         /* Slide up from bottom */
```

### Skeleton Classes

```css
.skeleton                 /* Base skeleton with pulse */
.skeleton-shimmer         /* Skeleton with shimmer effect */
.skeleton-wave            /* Skeleton with wave effect */
.skeleton-text            /* Text line skeleton */
.skeleton-text-sm         /* Small text skeleton */
.skeleton-text-lg         /* Large text skeleton */
.skeleton-heading         /* Heading skeleton */
.skeleton-avatar          /* Avatar skeleton */
.skeleton-avatar-sm       /* Small avatar skeleton */
.skeleton-avatar-lg       /* Large avatar skeleton */
.skeleton-button          /* Button skeleton */
.skeleton-card            /* Card skeleton */
.skeleton-image           /* Image skeleton */
```

### Layout Classes

```css
.aspect-ratio-16-9        /* 16:9 aspect ratio container */
.aspect-ratio-4-3         /* 4:3 aspect ratio container */
.aspect-ratio-1-1         /* 1:1 aspect ratio container */
.aspect-ratio-content     /* Content inside aspect ratio container */
.stable-height            /* Stable minimum height */
.stable-grid              /* Stable grid layout */
.stable-flex              /* Stable flex layout */
.smooth-height            /* Smooth height transitions */
.lazy-content             /* Content visibility optimization */
.no-fouc                  /* Prevent flash of unstyled content */
```

## Complete Examples

### Example 1: Loading State with Skeleton

```python
import streamlit as st
from utils.shadcn_animations import (
    inject_all_animations,
    show_loading_skeleton
)
from theming.theme_manager import ThemeManager

# Setup
theme_manager = ThemeManager()
inject_all_animations(theme_manager)

# Simulate loading
if 'loading' not in st.session_state:
    st.session_state.loading = True

if st.session_state.loading:
    show_loading_skeleton('card', count=3)
    
    # Simulate data loading
    import time
    time.sleep(2)
    st.session_state.loading = False
    st.rerun()
else:
    # Show actual content
    for i in range(3):
        st.markdown(
            f'<div class="shadcn-card">Card {i+1}</div>',
            unsafe_allow_html=True
        )
```

### Example 2: Animated Content Reveal

```python
from utils.shadcn_animations import inject_fade_in_animations, with_fade_in

inject_fade_in_animations()

# Wrap content with fade-in
def render_hero():
    st.title("Welcome to Our App")
    st.write("This content fades in smoothly")

with_fade_in(render_hero, direction='up')
```

### Example 3: Prevent Layout Shift for Images

```python
from utils.shadcn_animations import inject_layout_shift_prevention

inject_layout_shift_prevention()

# Use aspect ratio container
st.markdown(
    '''
    <div class="aspect-ratio-16-9">
        <img 
            src="https://example.com/image.jpg" 
            class="aspect-ratio-content"
            alt="Example"
        />
    </div>
    ''',
    unsafe_allow_html=True
)
```

### Example 4: Custom Skeleton Pattern

```python
from utils.shadcn_animations import (
    inject_skeleton_loaders,
    create_skeleton_loader
)

inject_skeleton_loaders(theme_manager)

# Custom loading pattern
col1, col2 = st.columns([1, 3])

with col1:
    create_skeleton_loader('avatar-lg', 'pulse')

with col2:
    create_skeleton_loader('heading', 'shimmer')
    create_skeleton_loader('text', 'shimmer', count=3)
    create_skeleton_loader('button', 'pulse')
```

### Example 5: Staggered List Animation

```python
inject_fade_in_animations()

# Staggered animation for list items
st.markdown('<div class="animate-stagger">', unsafe_allow_html=True)

for item in items:
    st.markdown(
        f'<div class="shadcn-card">{item}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)
```

## Best Practices

### 1. Always Inject Animations Early

```python
# ✅ Good: Inject at app start
if 'animations_injected' not in st.session_state:
    inject_all_animations(theme_manager)
    st.session_state.animations_injected = True

# ❌ Bad: Inject multiple times
inject_all_animations()  # Don't call repeatedly
```

### 2. Use Appropriate Animation Speeds

```python
# ✅ Good: Use theme-based speeds
anim_mgr = AnimationManager(theme_manager)
fast = anim_mgr.get_transition('fast')    # Quick interactions
base = anim_mgr.get_transition('base')    # Standard transitions
slow = anim_mgr.get_transition('slow')    # Large movements

# ❌ Bad: Hardcode timing values
transition = '500ms linear'  # Too slow, wrong easing
```

### 3. Show Loading States

```python
# ✅ Good: Show skeleton during loading
if loading:
    show_loading_skeleton('list', count=5)
else:
    render_actual_content()

# ❌ Bad: Show nothing while loading
if not loading:
    render_actual_content()
```

### 4. Prevent Layout Shifts

```python
# ✅ Good: Reserve space for content
prevent_layout_shift(render_dynamic_content, min_height='400px')

# ❌ Bad: Let content jump around
render_dynamic_content()  # Might cause layout shifts
```

### 5. Use Semantic Animation Directions

```python
# ✅ Good: Match animation to content flow
with_fade_in(render_header, direction='down')  # Header from top
with_fade_in(render_sidebar, direction='left')  # Sidebar from left
with_fade_in(render_content, direction='up')   # Content from bottom

# ❌ Bad: Random directions
with_fade_in(render_header, direction='right')  # Doesn't make sense
```

## Performance Considerations

1. **CSS-based animations** are hardware-accelerated and performant
2. **Skeleton loaders** prevent perceived loading time
3. **Layout shift prevention** improves Core Web Vitals
4. **Transition timing** follows Material Design guidelines (200-300ms)
5. **Easing functions** use natural cubic-bezier curves

## Browser Compatibility

All animations use standard CSS3 features supported by:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Animations Not Appearing

```python
# Check if animations are injected
if 'animations_injected' not in st.session_state:
    inject_all_animations(theme_manager)
    st.session_state.animations_injected = True
```

### Skeleton Loaders Not Styled

```python
# Ensure skeleton loaders are injected
inject_skeleton_loaders(theme_manager)
```

### Layout Shifts Still Occurring

```python
# Use aspect ratio containers for images
inject_layout_shift_prevention()

# Reserve minimum height for dynamic content
prevent_layout_shift(content_func, min_height='500px')
```

## Related Documentation

- [Theme System Reference](../theming/THEME_MANAGER_REFERENCE.md)
- [CSS Generator Reference](../theming/CSS_GENERATOR_REFERENCE.md)
- [Component Base Reference](../components/README.md)

## Support

For issues or questions, refer to the main documentation or create an issue in the project repository.
