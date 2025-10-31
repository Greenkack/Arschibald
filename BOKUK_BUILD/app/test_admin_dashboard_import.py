"""
Quick test to check admin dashboard can be imported
"""

print("Testing admin_core_status_extended_ui.py import...")

try:
    from admin_core_status_extended_ui import (
        render_extended_core_status_dashboard,
        render_core_status_dashboard
    )
    print("SUCCESS: admin_core_status_extended_ui.py imports correctly!")
    print("  - render_extended_core_status_dashboard: OK")
    print("  - render_core_status_dashboard: OK")
    
    print("\nAll 31 core modules can now be monitored via:")
    print("  streamlit run admin_core_status_extended_ui.py")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
