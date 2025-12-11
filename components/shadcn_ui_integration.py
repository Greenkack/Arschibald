"""
streamlit-shadcn-ui Integration Module

This module provides wrapper functions for all streamlit-shadcn-ui components
with fallbacks to native Streamlit components if the library is not available.

Based on components from: https://shadcn.streamlit.app/
"""

import streamlit as st
from typing import Optional, List, Dict, Any, Literal, Callable
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Try to import streamlit-shadcn-ui
try:
    import streamlit_shadcn_ui as ui
    SHADCN_UI_AVAILABLE = True
    logger.info("streamlit-shadcn-ui library loaded successfully")
except ImportError:
    SHADCN_UI_AVAILABLE = False
    logger.warning("streamlit-shadcn-ui not available, using fallbacks")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_available() -> bool:
    """Check if streamlit-shadcn-ui is available"""
    return SHADCN_UI_AVAILABLE


def get_version() -> Optional[str]:
    """Get streamlit-shadcn-ui version"""
    if SHADCN_UI_AVAILABLE:
        try:
            import streamlit_shadcn_ui
            return streamlit_shadcn_ui.__version__
        except AttributeError:
            return "unknown"
    return None


# ============================================================================
# BUTTON COMPONENTS
# ============================================================================

def button(
    text: str,
    key: Optional[str] = None,
    variant: Literal["default", "destructive", "outline", "secondary", "ghost", "link"] = "default",
    size: Literal["default", "sm", "lg", "icon"] = "default",
    disabled: bool = False,
    **kwargs
) -> bool:
    """
    Render a shadcn/ui button
    
    Args:
        text: Button text
        key: Unique key for the button
        variant: Button variant style
        size: Button size
        disabled: Whether button is disabled
        **kwargs: Additional arguments passed to the component
    
    Returns:
        bool: True if button was clicked
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.button(
                text=text,
                key=key,
                variant=variant,
                size=size,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn button: {e}")
            # Fallback to native
    
    # Fallback to native Streamlit button
    return st.button(text, key=key, disabled=disabled)


# ============================================================================
# BADGE COMPONENT
# ============================================================================

def badge(
    text: str,
    variant: Literal["default", "secondary", "destructive", "outline"] = "default",
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui badge
    
    Args:
        text: Badge text
        variant: Badge variant style
        key: Unique key for the badge
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.badge(text=text, variant=variant, key=key, **kwargs)
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn badge: {e}")
    
    # Fallback to styled markdown
    colors = {
        "default": "#18181b",
        "secondary": "#71717a",
        "destructive": "#ef4444",
        "outline": "#e4e4e7"
    }
    color = colors.get(variant, colors["default"])
    
    st.markdown(
        f'<span style="background-color: {color}; color: white; '
        f'padding: 2px 8px; border-radius: 4px; font-size: 12px;">{text}</span>',
        unsafe_allow_html=True
    )


# ============================================================================
# CARD COMPONENT
# ============================================================================

def card(
    title: Optional[str] = None,
    description: Optional[str] = None,
    content: Optional[str] = None,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui card
    
    Args:
        title: Card title
        description: Card description
        content: Card content
        key: Unique key for the card
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.card(
                title=title,
                description=description,
                content=content,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn card: {e}")
    
    # Fallback to native container
    with st.container():
        if title:
            st.subheader(title)
        if description:
            st.caption(description)
        if content:
            st.write(content)


# ============================================================================
# ALERT COMPONENT
# ============================================================================

def alert(
    title: Optional[str] = None,
    description: Optional[str] = None,
    variant: Literal["default", "destructive"] = "default",
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui alert
    
    Args:
        title: Alert title
        description: Alert description
        variant: Alert variant (default or destructive)
        key: Unique key for the alert
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.alert(
                title=title,
                description=description,
                variant=variant,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn alert: {e}")
    
    # Fallback to native Streamlit alerts
    message = f"**{title}**\n\n{description}" if title and description else (title or description or "")
    
    if variant == "destructive":
        st.error(message)
    else:
        st.info(message)


# ============================================================================
# TABS COMPONENT
# ============================================================================

def tabs(
    options: List[str],
    default_value: Optional[str] = None,
    key: Optional[str] = None,
    **kwargs
) -> str:
    """
    Render shadcn/ui tabs
    
    Args:
        options: List of tab labels
        default_value: Default selected tab
        key: Unique key for the tabs
        **kwargs: Additional arguments
    
    Returns:
        str: Selected tab label
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.tabs(
                options=options,
                default_value=default_value,
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn tabs: {e}")
    
    # Fallback to native Streamlit tabs
    tab_objects = st.tabs(options)
    # Return first tab as default (native tabs don't return selection)
    return default_value or options[0] if options else ""


# ============================================================================
# SWITCH COMPONENT
# ============================================================================

def switch(
    label: str,
    default: bool = False,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> bool:
    """
    Render a shadcn/ui switch (toggle)
    
    Args:
        label: Switch label
        default: Default state
        key: Unique key for the switch
        disabled: Whether switch is disabled
        **kwargs: Additional arguments
    
    Returns:
        bool: Switch state
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.switch(
                label=label,
                default=default,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn switch: {e}")
    
    # Fallback to native checkbox
    return st.checkbox(label, value=default, key=key, disabled=disabled)


# ============================================================================
# SLIDER COMPONENT
# ============================================================================

def slider(
    label: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    default_value: Optional[float] = None,
    step: float = 1.0,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> float:
    """
    Render a shadcn/ui slider
    
    Args:
        label: Slider label
        min_value: Minimum value
        max_value: Maximum value
        default_value: Default value
        step: Step size
        key: Unique key for the slider
        disabled: Whether slider is disabled
        **kwargs: Additional arguments
    
    Returns:
        float: Slider value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.slider(
                label=label,
                min_value=min_value,
                max_value=max_value,
                default_value=default_value or min_value,
                step=step,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn slider: {e}")
    
    # Fallback to native slider
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default_value or min_value,
        step=step,
        key=key,
        disabled=disabled
    )


# ============================================================================
# INPUT COMPONENT
# ============================================================================

def input(
    label: str,
    default_value: str = "",
    placeholder: str = "",
    type: Literal["text", "password", "email", "number"] = "text",
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> str:
    """
    Render a shadcn/ui input field
    
    Args:
        label: Input label
        default_value: Default value
        placeholder: Placeholder text
        type: Input type
        key: Unique key for the input
        disabled: Whether input is disabled
        **kwargs: Additional arguments
    
    Returns:
        str: Input value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.input(
                label=label,
                default_value=default_value,
                placeholder=placeholder,
                type=type,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn input: {e}")
    
    # Fallback to native input
    input_type = "default" if type == "text" else type
    return st.text_input(
        label,
        value=default_value,
        placeholder=placeholder,
        type=input_type,
        key=key,
        disabled=disabled
    )


# ============================================================================
# TEXTAREA COMPONENT
# ============================================================================

def textarea(
    label: str,
    default_value: str = "",
    placeholder: str = "",
    rows: int = 3,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> str:
    """
    Render a shadcn/ui textarea
    
    Args:
        label: Textarea label
        default_value: Default value
        placeholder: Placeholder text
        rows: Number of rows
        key: Unique key for the textarea
        disabled: Whether textarea is disabled
        **kwargs: Additional arguments
    
    Returns:
        str: Textarea value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.textarea(
                label=label,
                default_value=default_value,
                placeholder=placeholder,
                rows=rows,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn textarea: {e}")
    
    # Fallback to native textarea
    return st.text_area(
        label,
        value=default_value,
        placeholder=placeholder,
        height=rows * 30,
        key=key,
        disabled=disabled
    )


# ============================================================================
# SELECT COMPONENT
# ============================================================================

def select(
    label: str,
    options: List[str],
    default_value: Optional[str] = None,
    placeholder: str = "Select an option",
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> Optional[str]:
    """
    Render a shadcn/ui select dropdown
    
    Args:
        label: Select label
        options: List of options
        default_value: Default selected value
        placeholder: Placeholder text
        key: Unique key for the select
        disabled: Whether select is disabled
        **kwargs: Additional arguments
    
    Returns:
        Optional[str]: Selected value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.select(
                label=label,
                options=options,
                default_value=default_value,
                placeholder=placeholder,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn select: {e}")
    
    # Fallback to native selectbox
    index = options.index(default_value) if default_value in options else 0
    return st.selectbox(
        label,
        options=options,
        index=index,
        key=key,
        disabled=disabled
    )


# ============================================================================
# CHECKBOX COMPONENT
# ============================================================================

def checkbox(
    label: str,
    default: bool = False,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> bool:
    """
    Render a shadcn/ui checkbox
    
    Args:
        label: Checkbox label
        default: Default state
        key: Unique key for the checkbox
        disabled: Whether checkbox is disabled
        **kwargs: Additional arguments
    
    Returns:
        bool: Checkbox state
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.checkbox(
                label=label,
                default=default,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn checkbox: {e}")
    
    # Fallback to native checkbox
    return st.checkbox(label, value=default, key=key, disabled=disabled)


# ============================================================================
# RADIO GROUP COMPONENT
# ============================================================================

def radio_group(
    label: str,
    options: List[str],
    default_value: Optional[str] = None,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> str:
    """
    Render a shadcn/ui radio group
    
    Args:
        label: Radio group label
        options: List of options
        default_value: Default selected value
        key: Unique key for the radio group
        disabled: Whether radio group is disabled
        **kwargs: Additional arguments
    
    Returns:
        str: Selected value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.radio_group(
                label=label,
                options=options,
                default_value=default_value,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn radio_group: {e}")
    
    # Fallback to native radio
    index = options.index(default_value) if default_value in options else 0
    return st.radio(
        label,
        options=options,
        index=index,
        key=key,
        disabled=disabled
    )


# ============================================================================
# DATE PICKER COMPONENT
# ============================================================================

def date_picker(
    label: str,
    default_value: Optional[Any] = None,
    key: Optional[str] = None,
    disabled: bool = False,
    **kwargs
) -> Any:
    """
    Render a shadcn/ui date picker
    
    Args:
        label: Date picker label
        default_value: Default date value
        key: Unique key for the date picker
        disabled: Whether date picker is disabled
        **kwargs: Additional arguments
    
    Returns:
        Date value
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.date_picker(
                label=label,
                default_value=default_value,
                key=key,
                disabled=disabled,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn date_picker: {e}")
    
    # Fallback to native date_input
    return st.date_input(
        label,
        value=default_value,
        key=key,
        disabled=disabled
    )


# ============================================================================
# LINK COMPONENT
# ============================================================================

def link(
    text: str,
    href: str,
    target: Literal["_self", "_blank"] = "_blank",
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui link
    
    Args:
        text: Link text
        href: Link URL
        target: Link target (_self or _blank)
        key: Unique key for the link
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.link(
                text=text,
                href=href,
                target=target,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn link: {e}")
    
    # Fallback to markdown link
    st.markdown(f'<a href="{href}" target="{target}">{text}</a>', unsafe_allow_html=True)


# ============================================================================
# METRIC COMPONENT
# ============================================================================

def metric(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: Literal["normal", "inverse", "off"] = "normal",
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui metric card
    
    Args:
        label: Metric label
        value: Metric value
        delta: Delta value (change)
        delta_color: Delta color scheme
        key: Unique key for the metric
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.metric(
                label=label,
                value=value,
                delta=delta,
                delta_color=delta_color,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn metric: {e}")
    
    # Fallback to native metric
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )


# ============================================================================
# TABLE COMPONENT
# ============================================================================

def table(
    data: Any,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui table
    
    Args:
        data: Table data (DataFrame or dict)
        key: Unique key for the table
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.table(
                data=data,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn table: {e}")
    
    # Fallback to native dataframe
    st.dataframe(data)


# ============================================================================
# ELEMENT COMPONENT (Generic Container)
# ============================================================================

def element(
    element_type: str,
    content: Optional[str] = None,
    props: Optional[Dict[str, Any]] = None,
    key: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Render a generic shadcn/ui element
    
    Args:
        element_type: Type of element to render
        content: Element content
        props: Element properties
        key: Unique key for the element
        **kwargs: Additional arguments
    
    Returns:
        Element result
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.element(
                element_type=element_type,
                content=content,
                props=props or {},
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn element: {e}")
    
    # Fallback to container
    with st.container():
        if content:
            st.write(content)
        return None


# ============================================================================
# COMPONENT AVAILABILITY CHECK
# ============================================================================

def show_availability_status():
    """Display the availability status of streamlit-shadcn-ui"""
    if SHADCN_UI_AVAILABLE:
        version = get_version()
        st.success(f" streamlit-shadcn-ui is available (version: {version})")
    else:
        st.warning(
            " streamlit-shadcn-ui is not available. "
            "Install it with: `pip install streamlit-shadcn-ui`"
        )
        st.info("Using fallback components based on native Streamlit widgets.")


# ============================================================================
# CAROUSEL COMPONENT
# ============================================================================

def carousel(
    items: List[Dict[str, Any]],
    auto_advance: bool = False,
    interval: int = 5000,
    show_dots: bool = True,
    key: Optional[str] = None,
    **kwargs
) -> int:
    """
    Render a shadcn/ui carousel
    
    Args:
        items: List of carousel items (each item is a dict with 'content', 'title', etc.)
        auto_advance: Whether to auto-advance slides
        interval: Auto-advance interval in milliseconds
        show_dots: Whether to show navigation dots
        key: Unique key for the carousel
        **kwargs: Additional arguments
    
    Returns:
        int: Currently active slide index
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.carousel(
                items=items,
                auto_advance=auto_advance,
                interval=interval,
                show_dots=show_dots,
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn carousel: {e}")
    
    # Fallback to native selectbox-based carousel
    if not items:
        return 0
    
    # Use session state for carousel index
    carousel_key = f"carousel_index_{key or 'default'}"
    if carousel_key not in st.session_state:
        st.session_state[carousel_key] = 0
    
    current_index = st.session_state[carousel_key]
    
    # Display current item
    current_item = items[current_index]
    st.markdown(f"### {current_item.get('title', '')}")
    st.write(current_item.get('content', ''))
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous", key=f"{key}_prev"):
            st.session_state[carousel_key] = (current_index - 1) % len(items)
            st.rerun()
    with col2:
        if show_dots:
            st.write(f"Slide {current_index + 1} of {len(items)}")
    with col3:
        if st.button("Next", key=f"{key}_next"):
            st.session_state[carousel_key] = (current_index + 1) % len(items)
            st.rerun()
    
    return st.session_state[carousel_key]


# ============================================================================
# DRAWER COMPONENT
# ============================================================================

def drawer(
    trigger_label: str,
    content: Callable,
    side: Literal["left", "right", "top", "bottom"] = "right",
    size: Literal["sm", "default", "lg", "full"] = "default",
    key: Optional[str] = None,
    **kwargs
) -> bool:
    """
    Render a shadcn/ui drawer (side panel)
    
    Args:
        trigger_label: Label for the trigger button
        content: Callable that renders drawer content
        side: Side from which drawer slides in
        size: Drawer size
        key: Unique key for the drawer
        **kwargs: Additional arguments
    
    Returns:
        bool: True if drawer is open
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.drawer(
                trigger_label=trigger_label,
                content=content,
                side=side,
                size=size,
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn drawer: {e}")
    
    # Fallback to expander
    drawer_key = f"drawer_open_{key or 'default'}"
    if drawer_key not in st.session_state:
        st.session_state[drawer_key] = False
    
    if st.button(trigger_label, key=f"{key}_trigger"):
        st.session_state[drawer_key] = not st.session_state[drawer_key]
        st.rerun()
    
    if st.session_state[drawer_key]:
        with st.expander("Drawer Content", expanded=True):
            content()
            if st.button("Close", key=f"{key}_close"):
                st.session_state[drawer_key] = False
                st.rerun()
    
    return st.session_state[drawer_key]


# ============================================================================
# SKELETON LOADER COMPONENT
# ============================================================================

def skeleton(
    width: str = "100%",
    height: str = "20px",
    count: int = 1,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui skeleton loader
    
    Args:
        width: Skeleton width (CSS value)
        height: Skeleton height (CSS value)
        count: Number of skeleton lines
        key: Unique key for the skeleton
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.skeleton(
                width=width,
                height=height,
                count=count,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn skeleton: {e}")
    
    # Fallback to styled divs with shimmer animation
    for i in range(count):
        st.markdown(
            f'''
            <div style="
                width: {width};
                height: {height};
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: 4px;
                margin-bottom: 8px;
            "></div>
            <style>
                @keyframes shimmer {{
                    0% {{ background-position: 200% 0; }}
                    100% {{ background-position: -200% 0; }}
                }}
            </style>
            ''',
            unsafe_allow_html=True
        )


# ============================================================================
# PROGRESS COMPONENT
# ============================================================================

def progress(
    value: float,
    max_value: float = 100.0,
    label: Optional[str] = None,
    variant: Literal["default", "circular"] = "default",
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui progress indicator
    
    Args:
        value: Current progress value
        max_value: Maximum value
        label: Progress label
        variant: Progress variant (default linear or circular)
        key: Unique key for the progress
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.progress(
                value=value,
                max_value=max_value,
                label=label,
                variant=variant,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn progress: {e}")
    
    # Fallback to native progress
    if label:
        st.write(label)
    
    percentage = (value / max_value) * 100
    
    if variant == "circular":
        # Circular progress (text-based fallback)
        st.markdown(
            f'''
            <div style="text-align: center; font-size: 24px; font-weight: bold;">
                {percentage:.0f}%
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        # Linear progress
        st.progress(value / max_value)
        st.caption(f"{percentage:.1f}%")


# ============================================================================
# TOOLTIP COMPONENT
# ============================================================================

def tooltip(
    content: str,
    tooltip_text: str,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a shadcn/ui tooltip
    
    Args:
        content: Content to display (trigger element)
        tooltip_text: Tooltip text shown on hover
        key: Unique key for the tooltip
        **kwargs: Additional arguments
    """
    if SHADCN_UI_AVAILABLE:
        try:
            ui.tooltip(
                content=content,
                tooltip_text=tooltip_text,
                key=key,
                **kwargs
            )
            return
        except Exception as e:
            logger.error(f"Error rendering shadcn tooltip: {e}")
    
    # Fallback to title attribute
    st.markdown(
        f'<span title="{tooltip_text}">{content}</span>',
        unsafe_allow_html=True
    )


# ============================================================================
# POPOVER COMPONENT
# ============================================================================

def popover(
    trigger_label: str,
    content: Callable,
    key: Optional[str] = None,
    **kwargs
) -> bool:
    """
    Render a shadcn/ui popover
    
    Args:
        trigger_label: Label for the trigger button
        content: Callable that renders popover content
        key: Unique key for the popover
        **kwargs: Additional arguments
    
    Returns:
        bool: True if popover is open
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.popover(
                trigger_label=trigger_label,
                content=content,
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn popover: {e}")
    
    # Fallback to expander
    popover_key = f"popover_open_{key or 'default'}"
    if popover_key not in st.session_state:
        st.session_state[popover_key] = False
    
    if st.button(trigger_label, key=f"{key}_trigger"):
        st.session_state[popover_key] = not st.session_state[popover_key]
        st.rerun()
    
    if st.session_state[popover_key]:
        with st.container():
            content()
    
    return st.session_state[popover_key]


# ============================================================================
# ACCORDION COMPONENT
# ============================================================================

def accordion(
    items: List[Dict[str, Any]],
    default_open: Optional[int] = None,
    allow_multiple: bool = False,
    key: Optional[str] = None,
    **kwargs
) -> List[int]:
    """
    Render a shadcn/ui accordion
    
    Args:
        items: List of accordion items (each with 'title' and 'content')
        default_open: Index of item to open by default
        allow_multiple: Whether multiple items can be open simultaneously
        key: Unique key for the accordion
        **kwargs: Additional arguments
    
    Returns:
        List[int]: Indices of open items
    """
    if SHADCN_UI_AVAILABLE:
        try:
            result = ui.accordion(
                items=items,
                default_open=default_open,
                allow_multiple=allow_multiple,
                key=key,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error rendering shadcn accordion: {e}")
    
    # Fallback to native expanders
    open_items = []
    for i, item in enumerate(items):
        expanded = (i == default_open) if default_open is not None else False
        with st.expander(item.get('title', f'Item {i+1}'), expanded=expanded):
            st.write(item.get('content', ''))
            if expanded or st.session_state.get(f"{key}_accordion_{i}", False):
                open_items.append(i)
    
    return open_items


# ============================================================================
# COMPONENT REGISTRY
# ============================================================================

COMPONENT_REGISTRY = {
    "button": button,
    "badge": badge,
    "card": card,
    "alert": alert,
    "tabs": tabs,
    "switch": switch,
    "slider": slider,
    "input": input,
    "textarea": textarea,
    "select": select,
    "checkbox": checkbox,
    "radio_group": radio_group,
    "date_picker": date_picker,
    "link": link,
    "metric": metric,
    "table": table,
    "element": element,
    "carousel": carousel,
    "drawer": drawer,
    "skeleton": skeleton,
    "progress": progress,
    "tooltip": tooltip,
    "popover": popover,
    "accordion": accordion,
}


def get_available_components() -> List[str]:
    """Get list of all available component names"""
    return list(COMPONENT_REGISTRY.keys())


def get_component(name: str) -> Optional[Callable]:
    """Get a component function by name"""
    return COMPONENT_REGISTRY.get(name)
