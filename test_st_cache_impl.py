import streamlit as st

@st.cache_data(ttl=3600)
def my_func():
    print("Running my_func")
    return [1, 2, 3]

my_func()
my_func()
