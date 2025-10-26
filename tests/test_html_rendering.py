"""Test: Ob HTML in Sidebar gerendert wird"""
import streamlit as st

st.sidebar.title("HTML Rendering Test")

# Test 1: Einfaches HTML
st.sidebar.markdown(
    '<div style="color: red;">Test ROT</div>',
    unsafe_allow_html=True)

# Test 2: Mit CSS
st.sidebar.markdown("""
<style>
.test-box {
    background: blue;
    color: white;
    padding: 10px;
    border-radius: 5px;
}
</style>
<div class="test-box">Test BLAU</div>
""", unsafe_allow_html=True)

# Test 3: Normaler Text
st.sidebar.write("Normaler Text")
