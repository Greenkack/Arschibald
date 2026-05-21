# shadcn/ui Animations Quick Reference

Quick reference for using animations and transitions in the shadcn/ui system.

## Quick Setup

```python
from utils.shadcn_animations import inject_all_animations
from theming.theme_manager import ThemeManager

theme_manager = ThemeManager()
inject_all_animations(theme_manager)
```

## Common Functions

### Inject All Animations

```python
inject_all_animations(theme_manager)
```

### Show Loading Skeleton

```python
from utils.shadcn_animations import show_loading_skeleton

if loading:
    show_loading_skeleton('card', count=3)
```

### Fade-In Content

```python
from utils.shadcn_animations import with_fade_in

def render_content():
    st.write("Content here")

with_fade_in(render_content, direction='up')
```

### Create Custom Skeleton

```python
from utils.shadcn_animations import create_skeleton_loader

create_skeleton_loader('card', 'shimmer', count=2)
```

### Prevent Layout Shifts

```python
from utils.shadcn_animations import prevent_layout_shift

def render_dynamic():
    st.write(dynamic_content)

prevent_layout_shift(render_dynamic, min_height='300px')
```

## CSS Utility Classes

### Fade-In Animations

```html
<div class="animate-fade-in">Content</div>
<div class="animate-fade-in-up">Content</div>
<div class="animate-fade-in-down">Content</div>
<div class="animate-fade-in-left">Content</div>
<div class="animate-fade-in-right">Content</div>
<div class="animate-fade-in-scale">Content</div>
```

### Slide Animations

```html
<div class="animate-slide-in-left">Content</div>
<div class="animate-slide-in-right">Content</div>
<div class="animate-slide-down">Content</div>
<div class="animate-slide-up">Content</div>
```

### Skeleton Loaders

```html
<div class="skeleton-pulse skeleton-text"></div>
<div class="skeleton-shimmer skeleton-card"></div>
<div class="skeleton-wave skeleton-avatar"></div>
```

### Layout Stability

```html
<div class="aspect-ratio-16-9">
    <img src="image.jpg" class="aspect-ratio-content" />
</div>
```

## Skeleton Types

| Type | Description |
|------|-------------|
| `text` | Text line skeleton |
| `heading` | Heading skeleton |
| `avatar` | Circular avatar |
| `button` | Button skeleton |
| `card` | Card skeleton |
| `image` | Image with aspect ratio |

## Animation Speeds

| Speed | Duration | Use Case |
|-------|----------|----------|
| `fast` | 150ms | Quick interactions |
| `base` | 200ms | Standard transitions |
| `slow` | 300ms | Large movements |

## Loading Patterns

```python
# Card loading
show_loading_skeleton('card', count=3)

# List loading
show_loading_skeleton('list', count=5)

# Table loading
show_loading_skeleton('table', count=4)

# Form loading
show_loading_skeleton('form', count=3)
```

## Complete Example

```python
import streamlit as st
from utils.shadcn_animations import (
    inject_all_animations,
    show_loading_skeleton,
    with_fade_in
)
from theming.theme_manager import ThemeManager

# Setup
theme_manager = ThemeManager()
inject_all_animations(theme_manager)

# Loading state
if st.session_state.get('loading'):
    show_loading_skeleton('card', count=3)
else:
    def render_cards():
        for i in range(3):
            st.markdown(f'<div class="shadcn-card">Card {i+1}</div>')
    
    with_fade_in(render_cards, direction='up')
```

## Best Practices

✅ **DO:**
- Inject animations once at app start
- Use skeleton loaders for loading states
- Prevent layout shifts with aspect ratios
- Use theme-based timing values

❌ **DON'T:**
- Inject animations multiple times
- Show blank screens while loading
- Use hardcoded timing values
- Create jarring layout shifts

## See Also

- [Full Reference](../utils/SHADCN_ANIMATIONS_REFERENCE.md)
- [Theme System](../theming/THEME_MANAGER_REFERENCE.md)
- [Components](../components/README.md)
