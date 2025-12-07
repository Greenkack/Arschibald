"""
demo_module_migration.py

Demonstration of migrated modules using shadcn/ui components.
Shows how to use the new shadcn/ui versions of solar_calculator, crm, and admin_panel.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Import migration helpers
from utils.shadcn_migration_helpers import (
    inject_shadcn_styles,
    shadcn_card,
    shadcn_alert,
    shadcn_metric,
    shadcn_badge,
    apply_shadcn_chart_theme,
    shadcn_section,
    get_theme_manager,
    SHADCN_AVAILABLE,
)

# Page config
st.set_page_config(
    page_title="Module Migration Demo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject shadcn/ui styles
inject_shadcn_styles()

# Title
st.title(" Module Migration Demo")
st.markdown("Demonstration of migrated modules using shadcn/ui components")

# Check if shadcn/ui is available
if not SHADCN_AVAILABLE:
    st.error(" shadcn/ui components are not available. Please install the required modules.")
    st.stop()

# Sidebar - Theme selector
with st.sidebar:
    st.markdown("###  Theme Selection")
    
    theme_manager = get_theme_manager()
    if theme_manager:
        current_theme = st.session_state.get('current_theme', 'shadcn-default')
        
        theme_options = [
            'shadcn-default',
            'shadcn-dark',
            'shadcn-ocean',
            'shadcn-forest',
            'shadcn-sunset',
        ]
        
        selected_theme = st.selectbox(
            "Select Theme",
            options=theme_options,
            index=theme_options.index(current_theme) if current_theme in theme_options else 0,
            key="theme_selector"
        )
        
        if selected_theme != current_theme:
            theme_manager.set_theme(selected_theme)
            st.session_state.current_theme = selected_theme
            st.rerun()
    
    st.markdown("---")
    st.markdown("###  Demo Sections")
    
    demo_section = st.radio(
        "Choose Demo",
        [
            "Overview",
            "Cards Demo",
            "Alerts Demo",
            "Metrics Demo",
            "Charts Demo",
            "Complete Example",
        ],
        key="demo_section"
    )

# Main content
if demo_section == "Overview":
    st.markdown("##  Migration Overview")
    
    shadcn_alert(
        "Successfully migrated 3 main modules to shadcn/ui components!",
        alert_type="success",
        title="Migration Complete"
    )
    
    # Show migration stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shadcn_metric(
            label="Modules Migrated",
            value="3",
            icon="",
            size="medium"
        )
    
    with col2:
        shadcn_metric(
            label="Helper Functions",
            value="10+",
            icon="",
            size="medium"
        )
    
    with col3:
        shadcn_metric(
            label="Documentation Pages",
            value="2",
            icon="",
            size="medium"
        )
    
    with col4:
        shadcn_metric(
            label="Code Lines",
            value="1,470+",
            icon="",
            size="medium"
        )
    
    st.markdown("---")
    
    # Migrated modules
    shadcn_card(
        title=" Migrated Modules",
        content="""
        **1. solar_calculator.py → solar_calculator_shadcn.py**
        - Enhanced pricing display with metric cards
        - Automatic chart theming
        - Section rendering with cards
        
        **2. crm.py → crm_shadcn.py**
        - Customer list as modern card grid
        - Dashboard with metrics
        - Styled forms and action buttons
        
        **3. admin_panel.py → admin_panel_shadcn.py**
        - Modern sidebar navigation
        - Settings forms with cards
        - Admin dashboard with metrics
        """,
        variant="elevated",
        icon=""
    )
    
    st.markdown("---")
    
    # Key features
    col1, col2 = st.columns(2)
    
    with col1:
        shadcn_card(
            title=" Key Features",
            content="""
            - **Automatic Fallback**: Works even without shadcn/ui
            - **Theme Support**: 5 built-in themes
            - **Consistent Styling**: Unified design system
            - **Easy Migration**: Simple helper functions
            - **Backward Compatible**: Original modules unchanged
            """,
            variant="outlined"
        )
    
    with col2:
        shadcn_card(
            title=" Benefits",
            content="""
            - **Modern UI**: Professional design
            - **Better UX**: Improved visual hierarchy
            - **Maintainable**: Reusable components
            - **Flexible**: Easy to customize
            - **Production Ready**: Tested and documented
            """,
            variant="outlined"
        )

elif demo_section == "Cards Demo":
    st.markdown("##  Cards Demo")
    
    st.markdown("### Card Variants")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        shadcn_card(
            title="Default Card",
            content="This is a default card with standard styling.",
            footer="Card footer",
            variant="default",
            icon=""
        )
    
    with col2:
        shadcn_card(
            title="Outlined Card",
            content="This is an outlined card with a border.",
            footer="Card footer",
            variant="outlined",
            icon=""
        )
    
    with col3:
        shadcn_card(
            title="Elevated Card",
            content="This is an elevated card with a shadow.",
            footer="Card footer",
            variant="elevated",
            icon=""
        )
    
    st.markdown("---")
    st.markdown("### Card with Rich Content")
    
    shadcn_card(
        title=" Sales Dashboard",
        content="""
        **Monthly Performance**
        
        - Revenue: $45,000 (+12%)
        - Orders: 567 (+8%)
        - Customers: 234 (+15%)
        
        *Last updated: Today at 10:30 AM*
        """,
        footer="View detailed report →",
        variant="elevated",
        icon=""
    )

elif demo_section == "Alerts Demo":
    st.markdown("##  Alerts Demo")
    
    st.markdown("### Alert Types")
    
    shadcn_alert(
        "This is an informational alert. Use it for general information.",
        alert_type="info",
        title="Information"
    )
    
    shadcn_alert(
        "This is a success alert. Use it for successful operations.",
        alert_type="success",
        title="Success"
    )
    
    shadcn_alert(
        "This is a warning alert. Use it for warnings and cautions.",
        alert_type="warning",
        title="Warning"
    )
    
    shadcn_alert(
        "This is an error alert. Use it for errors and failures.",
        alert_type="error",
        title="Error"
    )
    
    st.markdown("---")
    st.markdown("### Alerts with Custom Icons")
    
    shadcn_alert(
        "Database connection established successfully!",
        alert_type="success",
        title="Connected",
        icon=""
    )
    
    shadcn_alert(
        "Your session will expire in 5 minutes.",
        alert_type="warning",
        title="Session Expiring",
        icon="⏰"
    )

elif demo_section == "Metrics Demo":
    st.markdown("##  Metrics Demo")
    
    st.markdown("### Metric Sizes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Small**")
        shadcn_metric(
            label="Users",
            value="1,234",
            delta="+12%",
            icon="",
            size="small"
        )
    
    with col2:
        st.markdown("**Medium**")
        shadcn_metric(
            label="Revenue",
            value="$45K",
            delta="+8%",
            icon="",
            size="medium"
        )
    
    with col3:
        st.markdown("**Large**")
        shadcn_metric(
            label="Orders",
            value="567",
            delta="-3%",
            icon="",
            size="large"
        )
    
    st.markdown("---")
    st.markdown("### Dashboard Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shadcn_metric(
            label="Total Customers",
            value="2,345",
            delta="+15%",
            icon="",
            size="medium"
        )
    
    with col2:
        shadcn_metric(
            label="Active Projects",
            value="89",
            delta="+5",
            icon="",
            size="medium"
        )
    
    with col3:
        shadcn_metric(
            label="Completion Rate",
            value="94%",
            delta="+2%",
            icon="",
            size="medium"
        )
    
    with col4:
        shadcn_metric(
            label="Avg Response Time",
            value="2.3h",
            delta="-0.5h",
            icon="⏱",
            size="medium"
        )

elif demo_section == "Charts Demo":
    st.markdown("##  Charts Demo")
    
    st.markdown("### Themed Charts")
    
    # Create sample data
    import numpy as np
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Line chart
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Sin(x)'))
    fig1.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Cos(x)'))
    fig1.update_layout(title="Line Chart with shadcn/ui Theme")
    
    # Apply theme
    fig1 = apply_shadcn_chart_theme(fig1)
    
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # Bar chart
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    values = [45, 52, 48, 61]
    
    fig2 = go.Figure(data=[go.Bar(x=categories, y=values)])
    fig2.update_layout(title="Bar Chart with shadcn/ui Theme")
    
    # Apply theme
    fig2 = apply_shadcn_chart_theme(fig2)
    
    st.plotly_chart(fig2, use_container_width=True)

elif demo_section == "Complete Example":
    st.markdown("##  Complete Example")
    
    st.markdown("### Full Dashboard with All Components")
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shadcn_metric(
            label="Total Revenue",
            value="$125K",
            delta="+18%",
            icon="",
            size="medium"
        )
    
    with col2:
        shadcn_metric(
            label="New Customers",
            value="234",
            delta="+12",
            icon="",
            size="medium"
        )
    
    with col3:
        shadcn_metric(
            label="Active Orders",
            value="89",
            delta="+5",
            icon="",
            size="medium"
        )
    
    with col4:
        shadcn_metric(
            label="Satisfaction",
            value="4.8/5",
            delta="+0.2",
            icon="",
            size="medium"
        )
    
    st.markdown("---")
    
    # Alert
    shadcn_alert(
        "Your monthly report is ready for review. Click here to view details.",
        alert_type="info",
        title="Report Ready",
        icon=""
    )
    
    st.markdown("---")
    
    # Content cards
    col1, col2 = st.columns(2)
    
    with col1:
        shadcn_card(
            title=" Sales Overview",
            content="""
            **This Month**
            - Revenue: $45,000
            - Orders: 567
            - Avg Order Value: $79.36
            
            **Trends**
            - Revenue up 12% vs last month
            - Orders up 8% vs last month
            """,
            footer="View detailed report →",
            variant="elevated"
        )
    
    with col2:
        shadcn_card(
            title=" Customer Insights",
            content="""
            **Demographics**
            - New Customers: 234
            - Returning: 1,890
            - Churn Rate: 2.3%
            
            **Engagement**
            - Avg Session: 8.5 min
            - Pages/Visit: 4.2
            """,
            footer="View customer analytics →",
            variant="elevated"
        )
    
    st.markdown("---")
    
    # Chart
    x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [35, 38, 42, 45, 48, 52]
    orders = [450, 480, 520, 567, 590, 620]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=revenue, name='Revenue ($K)'))
    fig.add_trace(go.Scatter(x=x, y=orders, name='Orders', yaxis='y2'))
    
    fig.update_layout(
        title="Revenue and Orders Trend",
        yaxis=dict(title='Revenue ($K)'),
        yaxis2=dict(title='Orders', overlaying='y', side='right')
    )
    
    fig = apply_shadcn_chart_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Success message
    shadcn_alert(
        "All systems operational. Dashboard updated successfully.",
        alert_type="success",
        title="System Status"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Module Migration Demo | Built with shadcn/ui components</p>
    <p>See <code>docs/SHADCN_MIGRATION_GUIDE.md</code> for complete documentation</p>
</div>
""", unsafe_allow_html=True)
