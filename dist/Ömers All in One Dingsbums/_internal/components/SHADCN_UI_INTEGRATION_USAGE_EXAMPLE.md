# streamlit-shadcn-ui Integration - Usage Examples

## Basic Setup

```python
import streamlit as st
from components import shadcn_ui_integration as sui

# Check library availability
sui.show_availability_status()
```

## Example 1: Simple Form

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("Contact Form")

# Form inputs
name = sui.input(
    label="Full Name",
    placeholder="Enter your name",
    key="name"
)

email = sui.input(
    label="Email Address",
    type="email",
    placeholder="you@example.com",
    key="email"
)

message = sui.textarea(
    label="Message",
    placeholder="Type your message here...",
    rows=5,
    key="message"
)

# Submit button
if sui.button("Send Message", variant="default", size="lg", key="submit"):
    if name and email and message:
        sui.alert(
            title="Success!",
            description="Your message has been sent.",
            variant="default"
        )
    else:
        sui.alert(
            title="Error",
            description="Please fill in all fields.",
            variant="destructive"
        )
```

## Example 2: Dashboard with Metrics

```python
import streamlit as st
from components import shadcn_ui_integration as sui
import pandas as pd

st.title("Sales Dashboard")

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    sui.metric(
        label="Total Revenue",
        value="$45,231.89",
        delta="+20.1% from last month"
    )

with col2:
    sui.metric(
        label="Subscriptions",
        value="+2,350",
        delta="+180.1% from last month"
    )

with col3:
    sui.metric(
        label="Sales",
        value="+12,234",
        delta="+19% from last month"
    )

with col4:
    sui.metric(
        label="Active Now",
        value="+573",
        delta="+201 since last hour"
    )

# Data table
st.subheader("Recent Sales")

df = pd.DataFrame({
    "Customer": ["Alice Johnson", "Bob Smith", "Charlie Brown"],
    "Email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
    "Amount": ["$250.00", "$150.00", "$350.00"],
    "Status": ["Completed", "Pending", "Completed"]
})

sui.table(data=df)
```

## Example 3: Settings Page

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("Settings")

# Tabs for different settings sections
selected_tab = sui.tabs(
    options=["Profile", "Account", "Notifications", "Security"],
    default_value="Profile"
)

if selected_tab == "Profile":
    st.subheader("Profile Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sui.input("First Name", default_value="John", key="first_name")
        sui.input("Email", type="email", default_value="john@example.com", key="email_profile")
    
    with col2:
        sui.input("Last Name", default_value="Doe", key="last_name")
        sui.input("Phone", default_value="+1 234 567 8900", key="phone")
    
    sui.textarea("Bio", placeholder="Tell us about yourself...", rows=4, key="bio")
    
    if sui.button("Save Changes", variant="default", key="save_profile"):
        sui.alert(
            title="Success",
            description="Your profile has been updated.",
            variant="default"
        )

elif selected_tab == "Account":
    st.subheader("Account Settings")
    
    sui.input("Username", default_value="johndoe", key="username")
    sui.input("Current Password", type="password", key="current_password")
    sui.input("New Password", type="password", key="new_password")
    sui.input("Confirm Password", type="password", key="confirm_password")
    
    if sui.button("Update Password", variant="default", key="update_password"):
        sui.alert(
            title="Success",
            description="Your password has been updated.",
            variant="default"
        )

elif selected_tab == "Notifications":
    st.subheader("Notification Preferences")
    
    sui.switch("Email notifications", default=True, key="email_notif")
    sui.switch("Push notifications", default=False, key="push_notif")
    sui.switch("SMS notifications", default=False, key="sms_notif")
    
    st.write("**Notification Types**")
    sui.checkbox("Marketing emails", default=True, key="marketing")
    sui.checkbox("Product updates", default=True, key="updates")
    sui.checkbox("Security alerts", default=True, key="security")
    
    if sui.button("Save Preferences", variant="default", key="save_notif"):
        sui.alert(
            title="Success",
            description="Your preferences have been saved.",
            variant="default"
        )

elif selected_tab == "Security":
    st.subheader("Security Settings")
    
    sui.switch("Two-factor authentication", default=False, key="2fa")
    sui.switch("Login alerts", default=True, key="login_alerts")
    
    if sui.button("Enable 2FA", variant="default", key="enable_2fa"):
        sui.alert(
            title="Info",
            description="Two-factor authentication setup will begin.",
            variant="default"
        )
```

## Example 4: Product Catalog

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("Product Catalog")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    category = sui.select(
        "Category",
        options=["All", "Electronics", "Clothing", "Books"],
        key="category"
    )

with col2:
    price_range = sui.slider(
        "Max Price",
        min_value=0.0,
        max_value=1000.0,
        default_value=500.0,
        key="price"
    )

with col3:
    sort_by = sui.select(
        "Sort By",
        options=["Newest", "Price: Low to High", "Price: High to Low"],
        key="sort"
    )

# Product cards
col1, col2, col3 = st.columns(3)

with col1:
    sui.card(
        title="Wireless Headphones",
        description="High-quality audio",
        content="$199.99"
    )
    sui.badge("New", variant="destructive")
    if sui.button("Add to Cart", variant="outline", key="cart1"):
        st.success("Added to cart!")

with col2:
    sui.card(
        title="Smart Watch",
        description="Fitness tracking",
        content="$299.99"
    )
    sui.badge("Sale", variant="secondary")
    if sui.button("Add to Cart", variant="outline", key="cart2"):
        st.success("Added to cart!")

with col3:
    sui.card(
        title="Laptop Stand",
        description="Ergonomic design",
        content="$49.99"
    )
    if sui.button("Add to Cart", variant="outline", key="cart3"):
        st.success("Added to cart!")
```

## Example 5: User Registration

```python
import streamlit as st
from components import shadcn_ui_integration as sui
from datetime import date

st.title("Create Account")

# Registration form
col1, col2 = st.columns(2)

with col1:
    first_name = sui.input("First Name", placeholder="John", key="reg_first")
    email = sui.input("Email", type="email", placeholder="john@example.com", key="reg_email")
    password = sui.input("Password", type="password", key="reg_password")

with col2:
    last_name = sui.input("Last Name", placeholder="Doe", key="reg_last")
    phone = sui.input("Phone", placeholder="+1 234 567 8900", key="reg_phone")
    confirm_password = sui.input("Confirm Password", type="password", key="reg_confirm")

# Additional info
birth_date = sui.date_picker("Date of Birth", default_value=date(1990, 1, 1), key="reg_dob")

country = sui.select(
    "Country",
    options=["United States", "United Kingdom", "Germany", "France", "Other"],
    key="reg_country"
)

# Preferences
st.write("**Account Type**")
account_type = sui.radio_group(
    "Select account type",
    options=["Personal", "Business"],
    default_value="Personal",
    key="reg_type"
)

# Terms and conditions
terms = sui.checkbox("I agree to the Terms and Conditions", key="reg_terms")
newsletter = sui.checkbox("Subscribe to newsletter", default=True, key="reg_newsletter")

# Submit
col1, col2 = st.columns([3, 1])

with col1:
    if sui.button("Create Account", variant="default", size="lg", key="reg_submit"):
        if all([first_name, last_name, email, password, confirm_password, terms]):
            if password == confirm_password:
                sui.alert(
                    title="Success!",
                    description="Your account has been created successfully.",
                    variant="default"
                )
            else:
                sui.alert(
                    title="Error",
                    description="Passwords do not match.",
                    variant="destructive"
                )
        else:
            sui.alert(
                title="Error",
                description="Please fill in all required fields and accept the terms.",
                variant="destructive"
            )

with col2:
    if sui.button("Cancel", variant="ghost", key="reg_cancel"):
        st.info("Registration cancelled")
```

## Example 6: Data Analysis Tool

```python
import streamlit as st
from components import shadcn_ui_integration as sui
import pandas as pd
import numpy as np

st.title("Data Analysis Tool")

# File upload simulation
sui.alert(
    title="Upload Data",
    description="Upload your CSV file to begin analysis.",
    variant="default"
)

# Sample data
np.random.seed(42)
df = pd.DataFrame({
    "Date": pd.date_range("2024-01-01", periods=100),
    "Sales": np.random.randint(100, 1000, 100),
    "Customers": np.random.randint(10, 100, 100),
    "Revenue": np.random.randint(1000, 10000, 100)
})

# Analysis options
col1, col2, col3 = st.columns(3)

with col1:
    metric_choice = sui.select(
        "Select Metric",
        options=["Sales", "Customers", "Revenue"],
        key="metric"
    )

with col2:
    date_range = sui.slider(
        "Date Range (days)",
        min_value=7.0,
        max_value=100.0,
        default_value=30.0,
        key="date_range"
    )

with col3:
    show_trend = sui.switch("Show Trend Line", default=True, key="trend")

# Display data
st.subheader("Data Preview")
sui.table(data=df.head(10))

# Statistics
st.subheader("Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    sui.metric("Average Sales", f"${df['Sales'].mean():.2f}")

with col2:
    sui.metric("Total Customers", f"{df['Customers'].sum():,}")

with col3:
    sui.metric("Total Revenue", f"${df['Revenue'].sum():,}")

with col4:
    sui.metric("Growth Rate", "+12.5%", delta="+2.3%")

# Export options
if sui.button("Export Report", variant="default", key="export"):
    sui.alert(
        title="Success",
        description="Report exported successfully.",
        variant="default"
    )
```

## Example 7: Admin Panel

```python
import streamlit as st
from components import shadcn_ui_integration as sui

st.title("Admin Panel")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    
    nav_option = sui.radio_group(
        "Select Section",
        options=["Dashboard", "Users", "Settings", "Logs"],
        default_value="Dashboard",
        key="nav"
    )

# Main content based on navigation
if nav_option == "Dashboard":
    st.subheader("Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sui.metric("Total Users", "1,234", delta="+12%")
    
    with col2:
        sui.metric("Active Sessions", "567", delta="+5%")
    
    with col3:
        sui.metric("Server Load", "45%", delta="-3%")

elif nav_option == "Users":
    st.subheader("User Management")
    
    # Search
    search = sui.input("Search users", placeholder="Enter name or email", key="search")
    
    # User actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if sui.button("Add User", variant="default", key="add_user"):
            st.info("Add user dialog")
    
    with col2:
        if sui.button("Export Users", variant="outline", key="export_users"):
            st.info("Exporting users...")
    
    with col3:
        if sui.button("Bulk Actions", variant="secondary", key="bulk"):
            st.info("Bulk actions menu")

elif nav_option == "Settings":
    st.subheader("System Settings")
    
    sui.switch("Maintenance Mode", default=False, key="maintenance")
    sui.switch("Debug Mode", default=False, key="debug")
    sui.switch("Email Notifications", default=True, key="email_sys")
    
    if sui.button("Save Settings", variant="default", key="save_settings"):
        sui.alert(
            title="Success",
            description="Settings saved successfully.",
            variant="default"
        )

elif nav_option == "Logs":
    st.subheader("System Logs")
    
    log_level = sui.select(
        "Log Level",
        options=["All", "Info", "Warning", "Error"],
        key="log_level"
    )
    
    sui.alert(
        title="System Log",
        description="Displaying recent system logs...",
        variant="default"
    )
```

## Tips and Best Practices

1. **Always use unique keys** for interactive components
2. **Check library availability** at app startup
3. **Use appropriate variants** for different contexts
4. **Combine with native Streamlit** components when needed
5. **Test fallback behavior** by temporarily uninstalling the library
6. **Use columns** for responsive layouts
7. **Group related components** in cards or containers
8. **Provide user feedback** with alerts after actions
9. **Use metrics** for displaying KPIs
10. **Leverage badges** for status indicators

## Resources

- Full API Reference: `SHADCN_UI_INTEGRATION_REFERENCE.md`
- Quick Reference: `SHADCN_UI_INTEGRATION_QUICK_REFERENCE.md`
- Demo App: `demo_shadcn_ui_integration.py`
