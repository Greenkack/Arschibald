"""
DemoStreamlitApp
Streamlit Application
"""
import streamlit as st


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="DemoStreamlitApp",
        page_icon="🚀",
        layout="wide"
    )

    st.title("DemoStreamlitApp")
    st.write("Willkommen zu Ihrer Streamlit-Anwendung!")

    # Add your application logic here
    st.info(
        "Diese Anwendung wurde automatisch "
        "mit KAI Agent generiert."
    )


if __name__ == "__main__":
    main()
