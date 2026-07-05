import pytest
import streamlit as st
from heatpump_pricing import load_heatpump_components
import sys

def test_load_components():
    try:
        comps = load_heatpump_components()
        assert "main" in comps
        assert "accessories" in comps
        print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

test_load_components()
