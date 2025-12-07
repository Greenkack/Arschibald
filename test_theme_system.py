"""
Test script for Theme System Infrastructure

Verifies that all components of Task 1 are working correctly.
"""

from theming import ThemeManager


def test_theme_system():
    """Test Theme System Infrastructure"""
    
    print("=" * 60)
    print("Testing Theme System Infrastructure (Task 1)")
    print("=" * 60)
    
    # Test 1: Initialize ThemeManager
    print("\n1. Initializing ThemeManager...")
    try:
        theme_manager = ThemeManager()
        print("    ThemeManager initialized successfully")
    except Exception as e:
        print(f"    Failed to initialize ThemeManager: {e}")
        return False
    
    # Test 2: Check available themes
    print("\n2. Checking available themes...")
    available_themes = theme_manager.get_available_themes()
    print(f"   Found {len(available_themes)} themes:")
    for theme_name in available_themes:
        print(f"   - {theme_name}")
    
    expected_themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean', 
                       'shadcn-forest', 'shadcn-sunset']
    
    if all(theme in available_themes for theme in expected_themes):
        print("    All 5 expected themes found")
    else:
        print("    Not all expected themes found")
        return False
    
    # Test 3: Load and set default theme
    print("\n3. Loading shadcn-default theme...")
    if theme_manager.set_theme('shadcn-default'):
        print("    Theme set successfully")
    else:
        print("    Failed to set theme")
        return False
    
    # Test 4: Test token access
    print("\n4. Testing token access...")
    test_tokens = [
        ('colors.primary', '#18181b'),
        ('colors.background', '#ffffff'),
        ('typography.font_family', "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
        ('spacing.spacing_4', '1rem'),
        ('shadows.shadow_md', '0 4px 6px -1px rgba(0, 0, 0, 0.1)'),
        ('borders.border_radius_lg', '0.5rem'),
        ('animations.transition_base', '200ms cubic-bezier(0.4, 0, 0.2, 1)')
    ]
    
    all_tokens_ok = True
    for token_path, expected_value in test_tokens:
        value = theme_manager.get_token(token_path)
        if value == expected_value:
            print(f"    {token_path}: {value}")
        else:
            print(f"    {token_path}: expected '{expected_value}', got '{value}'")
            all_tokens_ok = False
    
    if not all_tokens_ok:
        return False
    
    # Test 5: Test all theme data models
    print("\n5. Testing theme data models...")
    theme = theme_manager.current_theme
    
    # Check all token categories exist
    token_categories = ['colors', 'typography', 'spacing', 'shadows', 'borders', 'animations']
    for category in token_categories:
        if hasattr(theme, category):
            print(f"    {category} tokens present")
        else:
            print(f"    {category} tokens missing")
            return False
    
    # Test 6: Test theme switching
    print("\n6. Testing theme switching...")
    for theme_name in ['shadcn-dark', 'shadcn-ocean', 'shadcn-forest', 'shadcn-sunset']:
        if theme_manager.set_theme(theme_name):
            current = theme_manager.current_theme.name
            if current == theme_name:
                print(f"    Switched to {theme_name}")
            else:
                print(f"    Theme switch failed for {theme_name}")
                return False
        else:
            print(f"    Could not set theme {theme_name}")
            return False
    
    # Test 7: Test display names
    print("\n7. Testing theme display names...")
    display_names = theme_manager.get_theme_display_names()
    expected_display_names = {
        'shadcn-default': 'shadcn/ui Default',
        'shadcn-dark': 'shadcn/ui Dark',
        'shadcn-ocean': 'Ocean Blue',
        'shadcn-forest': 'Forest Green',
        'shadcn-sunset': 'Sunset Orange'
    }
    
    all_names_ok = True
    for theme_name, expected_display in expected_display_names.items():
        actual_display = display_names.get(theme_name)
        if actual_display == expected_display:
            print(f"    {theme_name}: '{actual_display}'")
        else:
            print(f"    {theme_name}: expected '{expected_display}', got '{actual_display}'")
            all_names_ok = False
    
    if not all_names_ok:
        return False
    
    # Test 8: Test fallback theme
    print("\n8. Testing fallback theme...")
    fallback = theme_manager.get_fallback_theme()
    if fallback:
        print(f"    Fallback theme available: {fallback.name}")
    else:
        print("    No fallback theme available")
        return False
    
    print("\n" + "=" * 60)
    print(" All tests passed! Theme System Infrastructure is working.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_theme_system()
    exit(0 if success else 1)
