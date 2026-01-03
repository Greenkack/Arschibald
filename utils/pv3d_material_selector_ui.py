"""
PV Module Material Selector UI

This module provides a Streamlit UI component for selecting module materials
and colors. It allows users to choose from predefined materials grouped by
surface finish.

Key Features:
    - Material selection grouped by finish (Matt, Glänzend, Spezial)
    - Color preview for each material
    - Apply to all modules or individual modules
    - Session state integration

Requirements: 6.1, 6.3
"""

import streamlit as st
from typing import Optional, List
from utils.pv3d_module_colors import (
    ModuleMaterial,
    SurfaceFinish,
    ALL_MATERIALS,
    MATERIALS_BY_FINISH,
    DEFAULT_MATERIAL,
    get_material_by_name,
    get_selected_material_from_session,
    set_selected_material_in_session,
    set_module_material_in_session,
    hex_to_rgb
)


def render_material_selector(
    apply_to_all: bool = True,
    module_index: Optional[int] = None,
    key_prefix: str = "material_selector"
) -> Optional[ModuleMaterial]:
    """
    Render material selector UI component.
    
    This function creates a Streamlit UI for selecting module materials,
    grouped by surface finish with color previews.
    
    Args:
        apply_to_all: If True, apply to all modules. If False, apply to single module
        module_index: Index of module to apply material to (if apply_to_all=False)
        key_prefix: Prefix for Streamlit widget keys (for multiple selectors)
    
    Returns:
        Selected material or None if no selection made
    
    Requirements:
        - 6.1: Material selection UI
        - 6.3: Store selection in session state
    
    Example:
        >>> # In Streamlit app
        >>> material = render_material_selector(apply_to_all=True)
        >>> if material:
        >>>     st.success(f"Material '{material.name}' ausgewählt!")
    """
    # Get current material from session
    current_material = get_selected_material_from_session(st.session_state)
    
    # Create tabs for material groups
    tab_matte, tab_glossy, tab_special = st.tabs([
        "🔲 Matt",
        "✨ Glänzend", 
        "🔬 Spezial"
    ])
    
    selected_material = None
    
    # Tab 1: Matte materials
    with tab_matte:
        st.markdown("**Matte Oberflächen** - Standard PV-Module mit geringer Reflexion")
        selected_material = _render_material_group(
            materials=MATERIALS_BY_FINISH[SurfaceFinish.MATTE],
            current_material=current_material,
            key_prefix=f"{key_prefix}_matte"
        )
    
    # Tab 2: Glossy materials
    with tab_glossy:
        st.markdown("**Glänzende Oberflächen** - Module mit hoher Reflexion")
        selected_material = selected_material or _render_material_group(
            materials=MATERIALS_BY_FINISH[SurfaceFinish.GLOSSY],
            current_material=current_material,
            key_prefix=f"{key_prefix}_glossy"
        )
    
    # Tab 3: Special materials
    with tab_special:
        st.markdown("**Spezial-Oberflächen** - Transparente und bifaziale Module")
        selected_material = selected_material or _render_material_group(
            materials=MATERIALS_BY_FINISH[SurfaceFinish.GLASS_GLASS],
            current_material=current_material,
            key_prefix=f"{key_prefix}_special"
        )
    
    # Apply material if selected
    if selected_material:
        if apply_to_all:
            # Requirement 6.3: Apply to all modules
            set_selected_material_in_session(st.session_state, selected_material)
            st.success(f"✅ Material '{selected_material.name}' auf alle Module angewendet")
        elif module_index is not None:
            # Apply to single module
            set_module_material_in_session(st.session_state, module_index, selected_material)
            st.success(f"✅ Material '{selected_material.name}' auf Modul #{module_index + 1} angewendet")
    
    return selected_material


def _render_material_group(
    materials: List[ModuleMaterial],
    current_material: ModuleMaterial,
    key_prefix: str
) -> Optional[ModuleMaterial]:
    """
    Render a group of materials with color previews.
    
    Args:
        materials: List of materials to display
        current_material: Currently selected material
        key_prefix: Prefix for widget keys
    
    Returns:
        Selected material or None
    """
    if not materials:
        st.info("Keine Materialien in dieser Kategorie")
        return None
    
    # Create columns for material cards
    cols = st.columns(min(len(materials), 3))
    
    selected_material = None
    
    for idx, material in enumerate(materials):
        col = cols[idx % 3]
        
        with col:
            # Check if this is the current material
            is_current = (material.name == current_material.name)
            
            # Create material card
            with st.container():
                # Color preview
                _render_color_preview(material)
                
                # Material name
                st.markdown(f"**{material.name}**")
                
                # Material description
                st.caption(material.description)
                
                # Material properties
                st.caption(f"Transparenz: {int(material.opacity * 100)}%")
                st.caption(f"Reflexion: {int(material.reflectivity * 100)}%")
                
                # Select button
                button_label = "✓ Ausgewählt" if is_current else "Auswählen"
                button_type = "secondary" if is_current else "primary"
                
                if st.button(
                    button_label,
                    key=f"{key_prefix}_{material.name}",
                    type=button_type,
                    disabled=is_current,
                    use_container_width=True
                ):
                    selected_material = material
    
    return selected_material


def _render_color_preview(material: ModuleMaterial) -> None:
    """
    Render color preview box for material.
    
    Args:
        material: Material to preview
    """
    # Convert hex to RGB
    rgb = hex_to_rgb(material.color)
    
    # Create color preview with CSS
    preview_html = f"""
    <div style="
        width: 100%;
        height: 80px;
        background-color: {material.color};
        border: 2px solid #ddd;
        border-radius: 8px;
        margin-bottom: 10px;
        opacity: {material.opacity};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    "></div>
    """
    
    st.markdown(preview_html, unsafe_allow_html=True)


def render_material_info_panel() -> None:
    """
    Render information panel about current material selection.
    
    Shows currently selected material and its properties.
    
    Requirements:
        - 6.1: Display current material selection
    
    Example:
        >>> # In Streamlit sidebar
        >>> with st.sidebar:
        >>>     render_material_info_panel()
    """
    st.markdown("### 🎨 Aktuelles Material")
    
    # Get current material
    current_material = get_selected_material_from_session(st.session_state)
    
    # Display material info
    with st.container():
        # Color preview
        _render_color_preview(current_material)
        
        # Material details
        st.markdown(f"**Name:** {current_material.name}")
        st.markdown(f"**Farbe:** {current_material.color}")
        st.markdown(f"**Oberfläche:** {current_material.finish.value}")
        st.markdown(f"**Transparenz:** {int(current_material.opacity * 100)}%")
        st.markdown(f"**Reflexion:** {int(current_material.reflectivity * 100)}%")
        
        if current_material.description:
            st.caption(current_material.description)


def render_quick_material_selector(
    key_prefix: str = "quick_selector"
) -> Optional[ModuleMaterial]:
    """
    Render compact material selector (dropdown style).
    
    This is a simpler, more compact version of the material selector
    suitable for sidebars or limited space.
    
    Args:
        key_prefix: Prefix for widget keys
    
    Returns:
        Selected material or None
    
    Example:
        >>> # In Streamlit sidebar
        >>> with st.sidebar:
        >>>     material = render_quick_material_selector()
    """
    st.markdown("### 🎨 Material-Auswahl")
    
    # Get current material
    current_material = get_selected_material_from_session(st.session_state)
    
    # Create material options
    material_names = [m.name for m in ALL_MATERIALS]
    current_index = material_names.index(current_material.name)
    
    # Selectbox
    selected_name = st.selectbox(
        "Material wählen:",
        options=material_names,
        index=current_index,
        key=f"{key_prefix}_selectbox"
    )
    
    # Get selected material
    selected_material = get_material_by_name(selected_name)
    
    if selected_material and selected_material.name != current_material.name:
        # Material changed
        set_selected_material_in_session(st.session_state, selected_material)
        st.success(f"✅ Material geändert zu '{selected_material.name}'")
        return selected_material
    
    # Show color preview
    if selected_material:
        _render_color_preview(selected_material)
        st.caption(selected_material.description)
    
    return None


def render_module_material_editor(
    module_positions: List[tuple],
    key_prefix: str = "module_editor"
) -> None:
    """
    Render editor for individual module materials.
    
    Allows setting different materials for each module.
    
    Args:
        module_positions: List of module positions
        key_prefix: Prefix for widget keys
    
    Requirements:
        - 6.4: Individual material per module
    
    Example:
        >>> positions = st.session_state.get("placed_module_positions", [])
        >>> render_module_material_editor(positions)
    """
    st.markdown("### 🎨 Individuelle Modul-Materialien")
    
    if not module_positions:
        st.info("Keine Module platziert")
        return
    
    st.caption(f"{len(module_positions)} Module platziert")
    
    # Create expander for each module
    for idx in range(len(module_positions)):
        with st.expander(f"Modul #{idx + 1}"):
            # Get current material for this module
            module_materials = st.session_state.get("module_materials", [])
            
            if idx < len(module_materials):
                current_material_name = module_materials[idx]
                current_material = get_material_by_name(current_material_name)
            else:
                current_material = DEFAULT_MATERIAL
            
            # Show current material
            col1, col2 = st.columns([1, 2])
            
            with col1:
                _render_color_preview(current_material)
            
            with col2:
                st.markdown(f"**{current_material.name}**")
                st.caption(current_material.description)
            
            # Material selector
            material_names = [m.name for m in ALL_MATERIALS]
            current_index = material_names.index(current_material.name)
            
            selected_name = st.selectbox(
                "Material ändern:",
                options=material_names,
                index=current_index,
                key=f"{key_prefix}_module_{idx}"
            )
            
            # Apply if changed
            selected_material = get_material_by_name(selected_name)
            if selected_material and selected_material.name != current_material.name:
                set_module_material_in_session(st.session_state, idx, selected_material)
                st.success(f"✅ Material geändert")
                st.rerun()


def render_material_comparison(
    materials: List[ModuleMaterial],
    key_prefix: str = "comparison"
) -> None:
    """
    Render comparison view for multiple materials.
    
    Shows materials side-by-side for easy comparison.
    
    Args:
        materials: List of materials to compare
        key_prefix: Prefix for widget keys
    
    Example:
        >>> from utils.pv3d_module_colors import MATERIAL_BLACK, MATERIAL_DARK_BLUE
        >>> render_material_comparison([MATERIAL_BLACK, MATERIAL_DARK_BLUE])
    """
    st.markdown("### 🔍 Material-Vergleich")
    
    if not materials:
        st.info("Keine Materialien zum Vergleichen")
        return
    
    # Create columns
    cols = st.columns(len(materials))
    
    for idx, material in enumerate(materials):
        with cols[idx]:
            # Color preview
            _render_color_preview(material)
            
            # Material info
            st.markdown(f"**{material.name}**")
            st.caption(f"Farbe: {material.color}")
            st.caption(f"Oberfläche: {material.finish.value}")
            st.caption(f"Transparenz: {int(material.opacity * 100)}%")
            st.caption(f"Reflexion: {int(material.reflectivity * 100)}%")


def render_material_statistics() -> None:
    """
    Render statistics about material usage.
    
    Shows how many modules use each material.
    
    Requirements:
        - 6.4: Track individual module materials
    
    Example:
        >>> render_material_statistics()
    """
    st.markdown("### 📊 Material-Statistik")
    
    # Get module materials
    module_materials = st.session_state.get("module_materials", [])
    
    if not module_materials:
        st.info("Keine Module platziert")
        return
    
    # Count materials
    material_counts = {}
    for material_name in module_materials:
        material_counts[material_name] = material_counts.get(material_name, 0) + 1
    
    # Display statistics
    total_modules = len(module_materials)
    
    for material_name, count in sorted(material_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_modules) * 100
        
        material = get_material_by_name(material_name)
        if material:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{material_name}**")
            
            with col2:
                st.markdown(f"{count} Module")
            
            with col3:
                st.markdown(f"{percentage:.1f}%")
            
            # Progress bar
            st.progress(percentage / 100)
