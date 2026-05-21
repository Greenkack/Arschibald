"""
Demo and Test for streamlit-shadcn-ui Integration

This demo showcases all wrapped components from streamlit-shadcn-ui
and demonstrates fallback behavior when the library is not available.

Run with: streamlit run demo_shadcn_ui_integration.py
"""

import streamlit as st
import pandas as pd
from datetime import date
from components import shadcn_ui_integration as sui

# Page config
st.set_page_config(
    page_title="shadcn/ui Integration Demo",
    page_
    layout="wide"
)

# Title
st.title(" streamlit-shadcn-ui Integration Demo")
st.markdown("---")

# Show availability status
sui.show_availability_status()
st.markdown("---")

# Create tabs for different component categories
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Buttons & Badges",
    "Forms & Inputs",
    "Cards & Alerts",
    "Data Display",
    "All Components"
])

# ============================================================================
# TAB 1: BUTTONS & BADGES
# ============================================================================
with tab1:
    st.header("Buttons & Badges")
    
    st.subheader("Buttons")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Default Button**")
        if sui.button("Click Me", key="btn1", variant="default"):
            st.success("Default button clicked!")
    
    with col2:
        st.write("**Destructive Button**")
        if sui.button("Delete", key="btn2", variant="destructive"):
            st.error("Destructive button clicked!")
    
    with col3:
        st.write("**Outline Button**")
        if sui.button("Outline", key="btn3", variant="outline"):
            st.info("Outline button clicked!")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.write("**Secondary Button**")
        if sui.button("Secondary", key="btn4", variant="secondary"):
            st.info("Secondary button clicked!")
    
    with col5:
        st.write("**Ghost Button**")
        if sui.button("Ghost", key="btn5", variant="ghost"):
            st.info("Ghost button clicked!")
    
    with col6:
        st.write("**Link Button**")
        if sui.button("Link", key="btn6", variant="link"):
            st.info("Link button clicked!")
    
    st.markdown("---")
    
    st.subheader("Button Sizes")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sui.button("Small", key="btn_sm", size="sm")
    
    with col2:
        sui.button("Default", key="btn_default", size="default")
    
    with col3:
        sui.button("Large", key="btn_lg", size="lg")
    
    with col4:
        sui.button("", key="btn_icon", size="icon")
    
    st.markdown("---")
    
    st.subheader("Badges")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write("**Default Badge**")
        sui.badge("Default", variant="default", key="badge1")
    
    with col2:
        st.write("**Secondary Badge**")
        sui.badge("Secondary", variant="secondary", key="badge2")
    
    with col3:
        st.write("**Destructive Badge**")
        sui.badge("Error", variant="destructive", key="badge3")
    
    with col4:
        st.write("**Outline Badge**")
        sui.badge("Outline", variant="outline", key="badge4")

# ============================================================================
# TAB 2: FORMS & INPUTS
# ============================================================================
with tab2:
    st.header("Forms & Inputs")
    
    st.subheader("Text Input")
    text_value = sui.input(
        label="Enter your name",
        placeholder="John Doe",
        key="input1"
    )
    if text_value:
        st.write(f"You entered: {text_value}")
    
    st.subheader("Password Input")
    password = sui.input(
        label="Enter password",
        type="password",
        placeholder="••••••••",
        key="input2"
    )
    
    st.subheader("Email Input")
    email = sui.input(
        label="Enter email",
        type="email",
        placeholder="user@example.com",
        key="input3"
    )
    
    st.subheader("Textarea")
    textarea_value = sui.textarea(
        label="Enter description",
        placeholder="Type your message here...",
        rows=4,
        key="textarea1"
    )
    
    st.markdown("---")
    
    st.subheader("Select Dropdown")
    selected = sui.select(
        label="Choose an option",
        options=["Option 1", "Option 2", "Option 3"],
        placeholder="Select...",
        key="select1"
    )
    if selected:
        st.write(f"Selected: {selected}")
    
    st.subheader("Checkbox")
    checked = sui.checkbox(
        label="I agree to the terms and conditions",
        key="checkbox1"
    )
    st.write(f"Checked: {checked}")
    
    st.subheader("Switch")
    switch_value = sui.switch(
        label="Enable notifications",
        key="switch1"
    )
    st.write(f"Switch: {'On' if switch_value else 'Off'}")
    
    st.markdown("---")
    
    st.subheader("Radio Group")
    radio_value = sui.radio_group(
        label="Select your preference",
        options=["Light Mode", "Dark Mode", "System"],
        default_value="System",
        key="radio1"
    )
    st.write(f"Selected: {radio_value}")
    
    st.subheader("Slider")
    slider_value = sui.slider(
        label="Select a value",
        min_value=0.0,
        max_value=100.0,
        default_value=50.0,
        step=1.0,
        key="slider1"
    )
    st.write(f"Value: {slider_value}")
    
    st.subheader("Date Picker")
    date_value = sui.date_picker(
        label="Select a date",
        default_value=date.today(),
        key="date1"
    )
    st.write(f"Selected date: {date_value}")

# ============================================================================
# TAB 3: CARDS & ALERTS
# ============================================================================
with tab3:
    st.header("Cards & Alerts")
    
    st.subheader("Cards")
    col1, col2 = st.columns(2)
    
    with col1:
        sui.card(
            title="Card Title",
            description="This is a card description",
            content="Card content goes here. You can put any information you want.",
            key="card1"
        )
    
    with col2:
        sui.card(
            title="Another Card",
            description="With different content",
            content="This demonstrates multiple cards side by side.",
            key="card2"
        )
    
    st.markdown("---")
    
    st.subheader("Alerts")
    
    sui.alert(
        title="Information",
        description="This is an informational alert message.",
        variant="default",
        key="alert1"
    )
    
    st.write("")
    
    sui.alert(
        title="Warning",
        description="This is a destructive/warning alert message.",
        variant="destructive",
        key="alert2"
    )
    
    st.markdown("---")
    
    st.subheader("Links")
    sui.link(
        text="Visit shadcn/ui Documentation",
        href="https://shadcn.streamlit.app/",
        target="_blank",
        key="link1"
    )

# ============================================================================
# TAB 4: DATA DISPLAY
# ============================================================================
with tab4:
    st.header("Data Display")
    
    st.subheader("Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sui.metric(
            label="Total Revenue",
            value="$45,231",
            delta="+20.1%",
            key="metric1"
        )
    
    with col2:
        sui.metric(
            label="Active Users",
            value="2,350",
            delta="+180",
            key="metric2"
        )
    
    with col3:
        sui.metric(
            label="Conversion Rate",
            value="3.2%",
            delta="-0.5%",
            delta_color="inverse",
            key="metric3"
        )
    
    st.markdown("---")
    
    st.subheader("Table")
    
    # Sample data
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "David"],
        "Age": [25, 30, 35, 40],
        "City": ["New York", "London", "Paris", "Tokyo"],
        "Score": [95, 87, 92, 88]
    })
    
    sui.table(data=df, key="table1")

# ============================================================================
# TAB 5: ALL COMPONENTS LIST
# ============================================================================
with tab5:
    st.header("All Available Components")
    
    st.write("### Component Registry")
    components = sui.get_available_components()
    
    st.write(f"Total components: **{len(components)}**")
    
    # Display in a nice grid
    cols = st.columns(3)
    for i, component in enumerate(components):
        with cols[i % 3]:
            st.code(f"sui.{component}()")
    
    st.markdown("---")
    
    st.write("### Library Information")
    
    if sui.is_available():
        version = sui.get_version()
        st.success(f" streamlit-shadcn-ui version: {version}")
        st.info("All components are using the native shadcn/ui library.")
    else:
        st.warning(" streamlit-shadcn-ui is not installed")
        st.info("All components are using fallback implementations with native Streamlit widgets.")
    
    st.markdown("---")
    
    st.write("### Installation")
    st.code("pip install streamlit-shadcn-ui", language="bash")
    
    st.write("### Documentation")
    st.markdown("- [streamlit-shadcn-ui Demo](https://shadcn.streamlit.app/)")
    st.markdown("- [GitHub Repository](https://github.com/ObservedObserver/streamlit-shadcn-ui)")

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.header("Demo Controls")
    
    st.write("### Test Interactive Components")
    
    if sui.button("Test Button", key="sidebar_btn"):
        st.balloons()
    
    sui.badge("New Feature", variant="destructive", key="sidebar_badge")
    
    st.markdown("---")
    
    theme = sui.select(
        label="Select Theme",
        options=["Light", "Dark", "Auto"],
        default_value="Light",
        key="sidebar_theme"
    )
    
    notifications = sui.switch(
        label="Enable Notifications",
        default=True,
        key="sidebar_notifications"
    )
    
    st.markdown("---")
    
    st.write("### About")
    st.caption(
        "This demo showcases the streamlit-shadcn-ui integration "
        "with automatic fallbacks to native Streamlit components."
    )

# Footer
st.markdown("---")
st.caption("Built with  using Streamlit and shadcn/ui")
