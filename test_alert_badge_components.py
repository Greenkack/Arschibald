"""
Quick test script for Alert and Badge components
"""

import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from components import Alert, AlertDialog, Badge, BadgeGroup
    print(" Successfully imported Alert, AlertDialog, Badge, BadgeGroup")
except ImportError as e:
    print(f" Import error: {e}")
    sys.exit(1)

# Test convenience functions
try:
    from components.alert import alert, alert_dialog
    from components.badge import badge, badge_group
    print(" Successfully imported convenience functions")
except ImportError as e:
    print(f" Import error: {e}")
    sys.exit(1)

# Test Alert instantiation
try:
    alert_component = Alert()
    print(" Alert component instantiated")
except Exception as e:
    print(f" Alert instantiation error: {e}")
    sys.exit(1)

# Test AlertDialog instantiation
try:
    dialog_component = AlertDialog()
    print(" AlertDialog component instantiated")
except Exception as e:
    print(f" AlertDialog instantiation error: {e}")
    sys.exit(1)

# Test Badge instantiation
try:
    badge_component = Badge()
    print(" Badge component instantiated")
except Exception as e:
    print(f" Badge instantiation error: {e}")
    sys.exit(1)

# Test BadgeGroup instantiation
try:
    group_component = BadgeGroup()
    print(" BadgeGroup component instantiated")
except Exception as e:
    print(f" BadgeGroup instantiation error: {e}")
    sys.exit(1)

# Test Alert has correct methods
try:
    assert hasattr(alert_component, 'render')
    assert hasattr(alert_component, 'get_token')
    assert hasattr(alert_component, 'inject_css')
    print(" Alert has required methods")
except AssertionError:
    print(" Alert missing required methods")
    sys.exit(1)

# Test AlertDialog has correct methods
try:
    assert hasattr(dialog_component, 'render')
    assert hasattr(dialog_component, '_hex_to_rgb')
    print(" AlertDialog has required methods")
except AssertionError:
    print(" AlertDialog missing required methods")
    sys.exit(1)

# Test Badge has correct methods
try:
    assert hasattr(badge_component, 'render')
    assert hasattr(badge_component, 'get_token')
    print(" Badge has required methods")
except AssertionError:
    print(" Badge missing required methods")
    sys.exit(1)

# Test BadgeGroup has correct methods
try:
    assert hasattr(group_component, 'render')
    print(" BadgeGroup has required methods")
except AssertionError:
    print(" BadgeGroup missing required methods")
    sys.exit(1)

# Test Alert DEFAULT_ICONS
try:
    assert hasattr(Alert, 'DEFAULT_ICONS')
    assert 'info' in Alert.DEFAULT_ICONS
    assert 'success' in Alert.DEFAULT_ICONS
    assert 'warning' in Alert.DEFAULT_ICONS
    assert 'error' in Alert.DEFAULT_ICONS
    print(" Alert has DEFAULT_ICONS with all types")
except AssertionError:
    print(" Alert DEFAULT_ICONS incomplete")
    sys.exit(1)

print("\n" + "="*50)
print("All tests passed! ")
print("="*50)
print("\nComponents are ready to use:")
print("  - Alert (4 types: info, success, warning, error)")
print("  - AlertDialog (modal confirmations)")
print("  - Badge (7 variants, 3 sizes)")
print("  - BadgeGroup (multiple badges)")
print("\nRun demo: streamlit run demo_alert_badge.py")
