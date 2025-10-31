"""Example Usage of Controlled Widget System

This file demonstrates how to use the controlled widget system with
auto-persistence and validation.
"""

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not available. Install with: pip install streamlit")

from datetime import date, timedelta

from core import (
    # Validation
    CustomRule,
    Validator,
    # Persistence
    flush_widget_states,
    # State Management
    get_all_widget_states,
    # Session
    get_current_session,
    get_dirty_widgets,
    get_invalid_widgets,
    recover_widget_states,
    required_date,
    required_email,
    required_number,
    required_text,
    required_url,
    # Widgets
    s_checkbox,
    s_date,
    s_file,
    s_multiselect,
    s_number,
    s_select,
    s_text,
    s_textarea,
)


def example_basic_widgets():
    """Example: Basic widget usage"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("Basic Widgets")

    # Text input
    name = s_text(
        label="Name",
        placeholder="Enter your name",
        help="This will be saved automatically"
    )

    # Number input
    age = s_number(
        label="Age",
        min_value=0,
        max_value=150,
        step=1
    )

    # Checkbox
    agree = s_checkbox(
        label="I agree to the terms",
        value=False
    )

    # Select
    country = s_select(
        options=["USA", "Canada", "UK", "Germany", "France"],
        label="Country"
    )

    # Display values
    st.write(f"Name: {name}")
    st.write(f"Age: {age}")
    st.write(f"Agreed: {agree}")
    st.write(f"Country: {country}")


def example_validated_widgets():
    """Example: Widgets with validation"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("Validated Widgets")

    # Email with validation
    email = s_text(
        label="Email Address",
        placeholder="user@example.com",
        validator=required_email()
    )

    # URL with validation
    website = s_text(
        label="Website",
        placeholder="https://example.com",
        validator=required_url()
    )

    # Number with range validation
    salary = s_number(
        label="Annual Salary",
        min_value=0,
        step=1000,
        validator=required_number(min_value=20000, max_value=500000)
    )

    # Text with length validation
    bio = s_textarea(
        label="Bio",
        placeholder="Tell us about yourself",
        max_chars=500,
        validator=required_text(min_length=10, max_length=500)
    )

    st.write(f"Email: {email}")
    st.write(f"Website: {website}")
    st.write(f"Salary: ${salary:,.0f}")
    st.write(f"Bio length: {len(bio)}")


def example_custom_validation():
    """Example: Custom validation rules"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("Custom Validation")

    # Password strength validator
    def validate_password_strength(value):
        if not value:
            return True
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        return has_upper and has_lower and has_digit and len(value) >= 8

    password = s_text(
        label="Password",
        type="password",
        validator=Validator([
            CustomRule(
                validate_password_strength,
                "Password must be at least 8 characters with uppercase, lowercase, and numbers"
            )
        ])
    )

    # Username validator
    def validate_username(value):
        if not value:
            return True
        return value.isalnum() and len(value) >= 3

    username = s_text(
        label="Username",
        validator=Validator([
            CustomRule(
                validate_username,
                "Username must be alphanumeric and at least 3 characters"
            )
        ])
    )

    # Skills with max selection
    def max_3_skills(value):
        return len(value) <= 3

    skills = s_multiselect(
        options=["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"],
        label="Select up to 3 skills",
        validator=Validator([
            CustomRule(max_3_skills, "Please select at most 3 skills")
        ])
    )

    st.write(f"Username: {username}")
    st.write(f"Password: {'*' * len(password) if password else ''}")
    st.write(f"Skills: {', '.join(skills)}")


def example_date_widgets():
    """Example: Date widgets with validation"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("Date Widgets")

    today = date.today()

    # Date of birth
    dob = s_date(
        label="Date of Birth",
        max_value=today,
        validator=required_date(
            min_date=today - timedelta(days=365 * 100),
            max_date=today - timedelta(days=365 * 18)
        )
    )

    # Start date
    start_date = s_date(
        label="Start Date",
        value=today,
        min_value=today,
        validator=required_date(min_date=today)
    )

    # End date
    end_date = s_date(
        label="End Date",
        value=today + timedelta(days=30),
        min_value=today,
        validator=required_date(min_date=today)
    )

    if dob:
        age = (today - dob).days // 365
        st.write(f"Age: {age} years")

    if start_date and end_date:
        duration = (end_date - start_date).days
        st.write(f"Duration: {duration} days")


def example_file_upload():
    """Example: File upload with validation"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("File Upload")

    # File size validator
    def validate_file_size(file):
        if file is None:
            return True
        return file.size <= 5 * 1024 * 1024  # 5MB

    uploaded_file = s_file(
        label="Upload Document",
        type=["pdf", "docx", "txt"],
        validator=Validator([
            CustomRule(validate_file_size, "File must be less than 5MB")
        ])
    )

    if uploaded_file:
        st.write(f"Filename: {uploaded_file.name}")
        st.write(f"Size: {uploaded_file.size / 1024:.2f} KB")
        st.write(f"Type: {uploaded_file.type}")


def example_state_management():
    """Example: Widget state management"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("State Management")

    # Create some widgets
    name = s_text(label="Name", key="state_name")
    age = s_number(label="Age", key="state_age")
    active = s_checkbox(label="Active", key="state_active")

    # Show state information
    st.subheader("Widget States")

    all_states = get_all_widget_states()
    st.write(f"Total widgets: {len(all_states)}")

    dirty_widgets = get_dirty_widgets()
    if dirty_widgets:
        st.warning(f"Unsaved widgets: {', '.join(dirty_widgets)}")

    invalid_widgets = get_invalid_widgets()
    if invalid_widgets:
        st.error(f"Invalid widgets: {', '.join(invalid_widgets)}")

    # Manual flush button
    if st.button("Save All Changes"):
        flush_widget_states()
        st.success("All changes saved!")


def example_recovery():
    """Example: State recovery"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("State Recovery")

    session = get_current_session()

    # Recover button
    if st.button("Recover Widget States"):
        recovered = recover_widget_states(session.session_id)

        if recovered:
            st.success(f"Recovered {len(recovered)} widget states")

            for widget_key, state_data in recovered.items():
                with st.expander(f"Widget: {widget_key}"):
                    st.write(f"Value: {state_data['value']}")
                    st.write(f"Type: {state_data['type']}")
                    st.write(f"Valid: {state_data['is_valid']}")
                    if state_data['errors']:
                        st.write(f"Errors: {state_data['errors']}")
                    if state_data['warnings']:
                        st.write(f"Warnings: {state_data['warnings']}")
        else:
            st.info("No widget states to recover")


def example_form_with_validation():
    """Example: Complete form with validation"""
    if not STREAMLIT_AVAILABLE:
        return

    st.header("Registration Form")

    with st.form("registration_form"):
        # Personal information
        st.subheader("Personal Information")

        first_name = s_text(
            label="First Name",
            key="reg_first_name",
            validator=required_text(min_length=2, max_length=50)
        )

        last_name = s_text(
            label="Last Name",
            key="reg_last_name",
            validator=required_text(min_length=2, max_length=50)
        )

        email = s_text(
            label="Email",
            key="reg_email",
            validator=required_email()
        )

        # Account information
        st.subheader("Account Information")

        username = s_text(
            label="Username",
            key="reg_username",
            validator=required_text(min_length=3, max_length=20)
        )

        password = s_text(
            label="Password",
            type="password",
            key="reg_password",
            validator=required_text(min_length=8)
        )

        # Preferences
        st.subheader("Preferences")

        country = s_select(
            options=["USA", "Canada", "UK", "Germany", "France", "Other"],
            label="Country",
            key="reg_country"
        )

        interests = s_multiselect(
            options=["Technology", "Sports", "Music", "Art", "Travel", "Food"],
            label="Interests",
            key="reg_interests"
        )

        newsletter = s_checkbox(
            label="Subscribe to newsletter",
            key="reg_newsletter"
        )

        # Submit button
        submitted = st.form_submit_button("Register")

        if submitted:
            # Check validation
            invalid = get_invalid_widgets()

            if invalid:
                st.error("Please fix validation errors before submitting")
            else:
                st.success("Registration successful!")
                st.balloons()

                # Display submitted data
                st.write("Submitted data:")
                st.json({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "username": username,
                    "country": country,
                    "interests": interests,
                    "newsletter": newsletter
                })


def main():
    """Main example application"""
    if not STREAMLIT_AVAILABLE:
        print("Please install Streamlit to run this example:")
        print("pip install streamlit")
        return

    st.title("Controlled Widget System Examples")

    st.sidebar.title("Examples")
    example = st.sidebar.radio(
        "Choose an example:",
        [
            "Basic Widgets",
            "Validated Widgets",
            "Custom Validation",
            "Date Widgets",
            "File Upload",
            "State Management",
            "State Recovery",
            "Complete Form"
        ]
    )

    if example == "Basic Widgets":
        example_basic_widgets()
    elif example == "Validated Widgets":
        example_validated_widgets()
    elif example == "Custom Validation":
        example_custom_validation()
    elif example == "Date Widgets":
        example_date_widgets()
    elif example == "File Upload":
        example_file_upload()
    elif example == "State Management":
        example_state_management()
    elif example == "State Recovery":
        example_recovery()
    elif example == "Complete Form":
        example_form_with_validation()


if __name__ == "__main__":
    main()
