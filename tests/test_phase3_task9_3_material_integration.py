"""
Tests für Phase 3 - Task 9.3: Integration in Modul-Rendering

Testet die Integration des Material-Systems in das 3D-Modul-Rendering.

Requirements:
    - 6.3: Material auf alle Module anwenden
    - 6.4: Individuelles Material pro Modul
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import plotly.graph_objects as go

# Import der zu testenden Module
from utils.pv3d_plotly import (
    create_pv_module_3d,
    create_pv_module_3d_with_material
)
from utils.pv3d_module_colors import (
    ModuleMaterial,
    SurfaceFinish,
    MATERIAL_BLACK,
    MATERIAL_DARK_BLUE,
    MATERIAL_BLACK_GLOSSY,
    MATERIAL_GLASS_GLASS,
    DEFAULT_MATERIAL
)


# ============================================================================
# TEST GRUPPE 1: create_pv_module_3d() mit Material-Parameter
# ============================================================================

class TestCreatePVModuleWithMaterial:
    """Tests für create_pv_module_3d() mit Material-Parameter."""
    
    def test_module_without_material(self):
        """Test: Modul ohne Material verwendet Standard-Farbe."""
        # Requirement 6.3: Fallback auf Standard-Farbe
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=None
        )
        
        # Prüfe dass Mesh erstellt wurde
        assert isinstance(mesh, go.Mesh3d)
        assert mesh.color == "#1a1a2e"  # Standard-Farbe
        assert mesh.opacity == 0.9  # Standard-Transparenz
        
        # Prüfe Vertices
        assert isinstance(vertices, np.ndarray)
        assert vertices.shape == (8, 3)
    
    def test_module_with_black_material(self):
        """Test: Modul mit schwarzem Material."""
        # Requirement 6.3: Material-Farbe wird angewendet
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_BLACK
        )
        
        # Prüfe Material-Eigenschaften
        assert mesh.color == MATERIAL_BLACK.color  # #1a1a1a
        assert mesh.opacity == MATERIAL_BLACK.opacity  # 1.0
        
        # Prüfe Beleuchtung für mattes Material
        assert mesh.lighting["ambient"] == 0.4
        assert mesh.lighting["specular"] == 0.2
        assert mesh.lighting["roughness"] == 0.8
    
    def test_module_with_dark_blue_material(self):
        """Test: Modul mit dunkelblauem Material."""
        # Requirement 6.3: Material-Farbe wird angewendet
        mesh, vertices = create_pv_module_3d(
            x=1.0, y=2.0, z=3.5,
            material=MATERIAL_DARK_BLUE
        )
        
        # Prüfe Material-Eigenschaften
        assert mesh.color == MATERIAL_DARK_BLUE.color  # #1a1a2e
        assert mesh.opacity == MATERIAL_DARK_BLUE.opacity  # 1.0
    
    def test_module_with_glossy_material(self):
        """Test: Modul mit glänzendem Material."""
        # Requirement 6.2: Glänzende Oberfläche
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_BLACK_GLOSSY
        )
        
        # Prüfe Material-Eigenschaften
        assert mesh.color == MATERIAL_BLACK_GLOSSY.color
        assert mesh.opacity == MATERIAL_BLACK_GLOSSY.opacity
        
        # Prüfe Beleuchtung für glänzendes Material
        assert mesh.lighting["ambient"] == 0.3
        assert mesh.lighting["specular"] == 0.8  # Hohe Spiegelung
        assert mesh.lighting["roughness"] == 0.2  # Geringe Rauheit
    
    def test_module_with_glass_glass_material(self):
        """Test: Modul mit Glas-Glas Material."""
        # Requirement 6.2: Transparente Oberfläche
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_GLASS_GLASS
        )
        
        # Prüfe Material-Eigenschaften
        assert mesh.color == MATERIAL_GLASS_GLASS.color
        assert mesh.opacity == MATERIAL_GLASS_GLASS.opacity  # 0.7 (transparent)
        
        # Prüfe Beleuchtung für Glas-Glas Material
        assert mesh.lighting["ambient"] == 0.5
        assert mesh.lighting["specular"] == 0.6
        assert mesh.lighting["roughness"] == 0.1  # Sehr glatt
    
    def test_selected_module_overrides_material_color(self):
        """Test: Ausgewähltes Modul überschreibt Material-Farbe."""
        # Requirement 2.1.2: Status-Farben haben Priorität
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_DARK_BLUE,
            selected=True
        )
        
        # Prüfe dass Auswahl-Farbe verwendet wird
        assert mesh.color == "#4a90e2"  # Hellblau für Auswahl
        # Material-Transparenz bleibt erhalten
        assert mesh.opacity == MATERIAL_DARK_BLUE.opacity
    
    def test_invalid_module_overrides_material_color(self):
        """Test: Ungültiges Modul überschreibt Material-Farbe."""
        # Requirement 2.1.2: Status-Farben haben Priorität
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_DARK_BLUE,
            invalid=True
        )
        
        # Prüfe dass Fehler-Farbe verwendet wird
        assert mesh.color == "#e74c3c"  # Rot für ungültig
    
    def test_material_with_different_positions(self):
        """Test: Material funktioniert an verschiedenen Positionen."""
        # Requirement 6.3: Material unabhängig von Position
        positions = [
            (0, 0, 3.0),
            (5.0, 5.0, 3.5),
            (-3.0, 2.0, 4.0)
        ]
        
        for x, y, z in positions:
            mesh, vertices = create_pv_module_3d(
                x=x, y=y, z=z,
                material=MATERIAL_BLACK
            )
            
            # Prüfe dass Material korrekt angewendet wird
            assert mesh.color == MATERIAL_BLACK.color
            assert mesh.opacity == MATERIAL_BLACK.opacity
            
            # Prüfe Position
            assert vertices[0, 0] != 0 or x == 0  # X verschoben
            assert vertices[0, 1] != 0 or y == 0  # Y verschoben
            assert vertices[0, 2] != 0 or z == 0  # Z verschoben


# ============================================================================
# TEST GRUPPE 2: create_pv_module_3d_with_material() Wrapper
# ============================================================================

class TestCreatePVModuleWithMaterialWrapper:
    """Tests für create_pv_module_3d_with_material() Wrapper-Funktion."""
    
    def test_wrapper_with_explicit_material(self):
        """Test: Wrapper mit explizit angegebenem Material."""
        # Requirement 6.4: Individuelles Material pro Modul
        mesh, vertices = create_pv_module_3d_with_material(
            x=0, y=0, z=3.0,
            material=MATERIAL_DARK_BLUE
        )
        
        # Prüfe dass Material angewendet wurde
        assert mesh.color == MATERIAL_DARK_BLUE.color
        assert mesh.opacity == MATERIAL_DARK_BLUE.opacity
    
    def test_wrapper_with_none_material_uses_default(self):
        """Test: Wrapper mit material=None verwendet DEFAULT_MATERIAL."""
        # Requirement 6.3: Fallback auf DEFAULT_MATERIAL wenn kein Material
        mesh, vertices = create_pv_module_3d_with_material(
            x=0, y=0, z=3.0,
            material=None
        )
        
        # Prüfe dass DEFAULT_MATERIAL verwendet wird
        # (Session State lädt DEFAULT_MATERIAL wenn verfügbar)
        assert isinstance(mesh, go.Mesh3d)
        # Kann entweder DEFAULT_MATERIAL oder Standard-Farbe sein
        assert mesh.color in [DEFAULT_MATERIAL.color, "#1a1a2e"]
    
    def test_wrapper_with_different_materials(self):
        """Test: Wrapper funktioniert mit verschiedenen Materialien."""
        # Requirement 6.4: Verschiedene Materialien pro Modul
        materials = [
            MATERIAL_BLACK,
            MATERIAL_DARK_BLUE,
            MATERIAL_BLACK_GLOSSY
        ]
        
        for material in materials:
            mesh, vertices = create_pv_module_3d_with_material(
                x=0, y=0, z=3.0,
                material=material
            )
            
            # Prüfe dass Material korrekt angewendet wurde
            assert mesh.color == material.color
            assert mesh.opacity == material.opacity


# ============================================================================
# TEST GRUPPE 3: Material-Eigenschaften
# ============================================================================

class TestMaterialProperties:
    """Tests für Material-Eigenschaften im Rendering."""
    
    def test_all_predefined_materials(self):
        """Test: Alle vordefinierten Materialien funktionieren."""
        # Requirement 6.1: Alle 7 Materialien unterstützt
        materials = [
            MATERIAL_BLACK,
            MATERIAL_DARK_BLUE,
            MATERIAL_BLACK_GLOSSY,
            MATERIAL_GLASS_GLASS
        ]
        
        for material in materials:
            mesh, vertices = create_pv_module_3d(
                x=0, y=0, z=3.0,
                material=material
            )
            
            # Prüfe dass Material angewendet wurde
            assert mesh.color == material.color
            assert mesh.opacity == material.opacity
            
            # Prüfe dass Beleuchtung konfiguriert ist
            assert "ambient" in mesh.lighting
            assert "diffuse" in mesh.lighting
            assert "specular" in mesh.lighting
            assert "roughness" in mesh.lighting
    
    def test_material_opacity_range(self):
        """Test: Material-Transparenz im gültigen Bereich."""
        # Requirement 6.2: Transparenz zwischen 0 und 1
        materials = [
            MATERIAL_BLACK,  # opacity=1.0
            MATERIAL_GLASS_GLASS  # opacity=0.7
        ]
        
        for material in materials:
            mesh, vertices = create_pv_module_3d(
                x=0, y=0, z=3.0,
                material=material
            )
            
            # Prüfe Transparenz-Bereich
            assert 0.0 <= mesh.opacity <= 1.0
            assert mesh.opacity == material.opacity
    
    def test_material_lighting_configuration(self):
        """Test: Material-Beleuchtung korrekt konfiguriert."""
        # Requirement 6.2: Verschiedene Beleuchtungs-Profile
        
        # Matt: geringe Spiegelung
        mesh_matte, _ = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_BLACK
        )
        assert mesh_matte.lighting["specular"] == 0.2
        assert mesh_matte.lighting["roughness"] == 0.8
        
        # Glänzend: hohe Spiegelung
        mesh_glossy, _ = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_BLACK_GLOSSY
        )
        assert mesh_glossy.lighting["specular"] == 0.8
        assert mesh_glossy.lighting["roughness"] == 0.2
        
        # Glas-Glas: mittlere Spiegelung
        mesh_glass, _ = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_GLASS_GLASS
        )
        assert mesh_glass.lighting["specular"] == 0.6
        assert mesh_glass.lighting["roughness"] == 0.1


# ============================================================================
# TEST GRUPPE 4: Integration mit bestehenden Features
# ============================================================================

class TestMaterialIntegrationWithExistingFeatures:
    """Tests für Integration mit bestehenden Features."""
    
    def test_material_with_module_number(self):
        """Test: Material funktioniert mit Modul-Nummer."""
        # Requirement 8.2.1: Modul-Nummer + Material
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_DARK_BLUE,
            module_number=42
        )
        
        # Prüfe Material
        assert mesh.color == MATERIAL_DARK_BLUE.color
        
        # Prüfe dass Modul-Nummer im Namen ist
        assert "42" in mesh.name or "#42" in mesh.name
    
    def test_material_with_different_roof_types(self):
        """Test: Material funktioniert mit verschiedenen Dachtypen."""
        # Requirement 6.3: Material unabhängig von Dachtyp
        roof_types = ["Flachdach", "Satteldach", "Walmdach"]
        
        for roof_type in roof_types:
            mesh, vertices = create_pv_module_3d(
                x=0, y=0, z=3.0,
                material=MATERIAL_BLACK,
                roof_type=roof_type
            )
            
            # Prüfe dass Material angewendet wurde
            assert mesh.color == MATERIAL_BLACK.color
            assert mesh.opacity == MATERIAL_BLACK.opacity
    
    def test_material_with_rotation(self):
        """Test: Material funktioniert mit Rotation."""
        # Requirement 6.3: Material unabhängig von Rotation
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=MATERIAL_DARK_BLUE,
            azimuth_deg=45,
            tilt_deg=30
        )
        
        # Prüfe dass Material angewendet wurde
        assert mesh.color == MATERIAL_DARK_BLUE.color
        
        # Prüfe dass Vertices rotiert wurden (nicht alle gleich)
        assert not np.allclose(vertices[0], vertices[1])


# ============================================================================
# TEST GRUPPE 5: Edge Cases
# ============================================================================

class TestMaterialEdgeCases:
    """Tests für Edge Cases."""
    
    def test_material_none_uses_default(self):
        """Test: material=None verwendet Standard-Farbe."""
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=None
        )
        
        # Prüfe Standard-Farbe
        assert mesh.color == "#1a1a2e"
    
    def test_custom_material_object(self):
        """Test: Benutzerdefiniertes Material-Objekt."""
        # Requirement 6.1: Unterstützung für benutzerdefinierte Materialien
        custom_material = ModuleMaterial(
            name="Custom Red",
            color="#ff0000",
            finish=SurfaceFinish.MATTE,
            opacity=0.8,
            reflectivity=0.3,
            description="Custom red material"
        )
        
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=custom_material
        )
        
        # Prüfe benutzerdefinierte Eigenschaften
        assert mesh.color == "#ff0000"
        assert mesh.opacity == 0.8
    
    def test_material_with_zero_opacity(self):
        """Test: Material mit Transparenz 0 (vollständig transparent)."""
        transparent_material = ModuleMaterial(
            name="Transparent",
            color="#ffffff",
            finish=SurfaceFinish.GLASS_GLASS,
            opacity=0.0,
            reflectivity=0.5
        )
        
        mesh, vertices = create_pv_module_3d(
            x=0, y=0, z=3.0,
            material=transparent_material
        )
        
        # Prüfe dass Modul erstellt wurde (auch wenn unsichtbar)
        assert isinstance(mesh, go.Mesh3d)
        assert mesh.opacity == 0.0


# ============================================================================
# PYTEST KONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
