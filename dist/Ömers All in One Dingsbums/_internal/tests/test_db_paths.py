#!/usr/bin/env python3
"""Test script to compare database paths between React app and Python bridge"""

import os


# React app path logic (from connection.ts)
def get_react_db_path():
    if os.name == 'nt':  # Windows
        user_data = os.environ.get('APPDATA', '')
    else:  # macOS/Linux
        user_data = os.environ.get('HOME', '')
        if user_data:
            user_data = os.path.join(user_data, '.local', 'share')

    if user_data:
        db_dir = os.path.join(user_data, 'kakerlake', 'data')
        db_path = os.path.join(db_dir, 'app.sqlite')
    else:
        db_path = os.path.join('data', 'app.sqlite')

    return db_path

# Python bridge path logic


def get_python_bridge_path():
    from solar_calculator_bridge import SolarCalculatorProductBridge
    bridge = SolarCalculatorProductBridge()
    return bridge.db_path


if __name__ == "__main__":
    react_path = get_react_db_path()
    python_path = get_python_bridge_path()

    print(f"React app database path: {react_path}")
    print(f"Python bridge database path: {python_path}")
    print(f"Paths match: {react_path == python_path}")

    # Check if database files exist
    print(f"\nReact database exists: {os.path.exists(react_path)}")
    print(f"Python database exists: {os.path.exists(python_path)}")

    # Show actual file sizes if they exist
    if os.path.exists(react_path):
        size = os.path.getsize(react_path)
        print(f"React database size: {size} bytes")

    if os.path.exists(python_path):
        size = os.path.getsize(python_path)
        print(f"Python database size: {size} bytes")
