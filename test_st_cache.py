import sys
sys.path.append('.')

import streamlit as st

@st.cache_data
def my_func():
    return [1, 2, 3]

my_func()
