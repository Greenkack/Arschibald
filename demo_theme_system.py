"""
Demo: Theme System Infrastructure

Demonstrates the complete functionality of Task 1.
"""

from theming import ThemeManager


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_theme_system():
    """Demonstrate theme system capabilities"""
    
    print_section("THEME SYSTEM INFRASTRUCTURE DEMO")
    
    # Initialize
    print("\n Initializing ThemeManager...")
    theme_manager = ThemeManager()
    print(" ThemeManager ready")
    
    # Show available themes
    print_section("AVAILABLE THEMES")
    display_names = theme_manager.get_theme_display_names()
    for theme_name, display_name in display_names.items():
        print(f"  • {theme_name:20} → {display_name}")
    
    # Demonstrate each theme
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        theme = theme_manager.current_theme
        
        print_section(f"THEME: {theme.display_name}")
        
        # Show color palette
        print("\n Color Palette:")
        print(f"  Background:  {theme.colors.background}")
        print(f"  Foreground:  {theme.colors.foreground}")
        print(f"  Primary:     {theme.colors.primary}")
        print(f"  Secondary:   {theme.colors.secondary}")
        print(f"  Success:     {theme.colors.success}")
        print(f"  Warning:     {theme.colors.warning}")
        print(f"  Error:       {theme.colors.error}")
        print(f"  Info:        {theme.colors.info}")
        
        # Show chart colors
        print("\n Chart Colors:")
        print(f"  Chart 1:     {theme.colors.chart_1}")
        print(f"  Chart 2:     {theme.colors.chart_2}")
        print(f"  Chart 3:     {theme.colors.chart_3}")
        print(f"  Chart 4:     {theme.colors.chart_4}")
        print(f"  Chart 5:     {theme.colors.chart_5}")
        
        # Show typography
        print("\n  Typography:")
        print(f"  Font Family: {theme.typography.font_family[:50]}...")
        print(f"  Base Size:   {theme.typography.font_size_base}")
        print(f"  Bold Weight: {theme.typography.font_weight_bold}")
        
        # Show spacing
        print("\n Spacing Scale:")
        print(f"  Small:       {theme.spacing.spacing_2}")
        print(f"  Medium:      {theme.spacing.spacing_4}")
        print(f"  Large:       {theme.spacing.spacing_8}")
        
        # Show shadows
        print("\n Shadows:")
        print(f"  Small:       {theme.shadows.shadow_sm}")
        print(f"  Medium:      {theme.shadows.shadow_md}")
        
        # Show borders
        print("\n Borders:")
        print(f"  Width:       {theme.borders.border_width}")
        print(f"  Radius:      {theme.borders.border_radius_lg}")
        
        # Show animations
        print("\n Animations:")
        print(f"  Transition:  {theme.animations.transition_base}")
        print(f"  Easing:      {theme.animations.easing_default}")
    
    # Demonstrate token access
    print_section("TOKEN ACCESS EXAMPLES")
    theme_manager.set_theme('shadcn-default')
    
    examples = [
        ('colors.primary', 'Primary color'),
        ('typography.font_family', 'Font family'),
        ('spacing.spacing_4', 'Standard spacing'),
        ('shadows.shadow_md', 'Medium shadow'),
        ('borders.border_radius_lg', 'Large border radius'),
        ('animations.transition_base', 'Base transition')
    ]
    
    print("\nAccessing tokens via dot notation:")
    for token_path, description in examples:
        value = theme_manager.get_token(token_path)
        print(f"  {token_path:30} → {value}")
    
    print_section("DEMO COMPLETE")
    print("\n Theme System Infrastructure is fully operational!")
    print(" See USAGE_EXAMPLE.md for integration examples")
    print(" Ready for Task 2: CSS Generator implementation\n")


if __name__ == "__main__":
    demo_theme_system()
