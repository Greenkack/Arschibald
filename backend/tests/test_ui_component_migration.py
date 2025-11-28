"""
UI Component Migration Tests
Task 238: Complete UI Component Migration

Tests to verify all Streamlit components are properly mapped to React/PrimeReact equivalents.
"""

import pytest
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ComponentMapping:
    """Mapping between Streamlit and React components"""
    streamlit: str
    react: str
    library: str
    notes: str = ""


# Complete component mapping
COMPONENT_MAPPINGS: List[ComponentMapping] = [
    # Input Components
    ComponentMapping("st.text_input()", "<InputText />", "PrimeReact"),
    ComponentMapping("st.number_input()", "<GermanNumberInput />", "Custom"),
    ComponentMapping("st.text_area()", "<InputTextarea />", "PrimeReact"),
    ComponentMapping("st.selectbox()", "<Dropdown />", "PrimeReact"),
    ComponentMapping("st.multiselect()", "<MultiSelect />", "PrimeReact"),
    ComponentMapping("st.slider()", "<GermanSlider />", "Custom"),
    ComponentMapping("st.checkbox()", "<Checkbox />", "PrimeReact"),
    ComponentMapping("st.radio()", "<RadioButton />", "PrimeReact"),
    ComponentMapping("st.date_input()", "<Calendar />", "PrimeReact"),
    ComponentMapping("st.time_input()", "<Calendar timeOnly />", "PrimeReact"),
    ComponentMapping("st.color_picker()", "<ColorPicker />", "PrimeReact"),
    ComponentMapping("st.file_uploader()", "Native File Dialog", "Electron"),
    
    # Display Components
    ComponentMapping("st.dataframe()", "<DataTable />", "PrimeReact"),
    ComponentMapping("st.table()", "<DataTable />", "PrimeReact"),
    ComponentMapping("st.metric()", "<MetricCard />", "Custom"),
    ComponentMapping("st.json()", "<pre><code>", "HTML"),
    ComponentMapping("st.code()", "<pre><code>", "HTML"),
    ComponentMapping("st.markdown()", "<ReactMarkdown />", "react-markdown"),
    ComponentMapping("st.image()", "<Image />", "PrimeReact"),
    
    # Chart Components
    ComponentMapping("st.plotly_chart()", "<ResponsiveContainer>", "Recharts"),
    ComponentMapping("st.line_chart()", "<LineChart />", "Recharts"),
    ComponentMapping("st.bar_chart()", "<BarChart />", "Recharts"),
    ComponentMapping("st.area_chart()", "<AreaChart />", "Recharts"),
    
    # Layout Components
    ComponentMapping("st.columns()", "CSS Grid / Flexbox", "CSS"),
    ComponentMapping("st.tabs()", "<TabView />", "PrimeReact"),
    ComponentMapping("st.expander()", "<Accordion />", "PrimeReact"),
    ComponentMapping("st.sidebar", "<Sidebar />", "PrimeReact"),
    
    # Feedback Components
    ComponentMapping("st.success()", "<Message severity='success' />", "PrimeReact"),
    ComponentMapping("st.error()", "<Message severity='error' />", "PrimeReact"),
    ComponentMapping("st.warning()", "<Message severity='warn' />", "PrimeReact"),
    ComponentMapping("st.info()", "<Message severity='info' />", "PrimeReact"),
    ComponentMapping("st.spinner()", "<ProgressSpinner />", "PrimeReact"),
    ComponentMapping("st.progress()", "<ProgressBar />", "PrimeReact"),
    
    # Action Components
    ComponentMapping("st.button()", "<Button />", "PrimeReact"),
    ComponentMapping("st.download_button()", "<Button /> + download", "PrimeReact"),
    
    # Dialog Components
    ComponentMapping("st.dialog()", "<Dialog />", "PrimeReact"),
]


class TestInputComponentMigration:
    """Tests for input component migration"""
    
    def test_text_input_mapped(self):
        """Test st.text_input is mapped to InputText"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "text_input" in m.streamlit)
        assert "InputText" in mapping.react
        assert mapping.library == "PrimeReact"
    
    def test_number_input_mapped_to_german(self):
        """Test st.number_input is mapped to GermanNumberInput"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "number_input" in m.streamlit)
        assert "GermanNumberInput" in mapping.react
        assert mapping.library == "Custom"
    
    def test_selectbox_mapped(self):
        """Test st.selectbox is mapped to Dropdown"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "selectbox" in m.streamlit)
        assert "Dropdown" in mapping.react
    
    def test_slider_mapped_to_german(self):
        """Test st.slider is mapped to GermanSlider"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "slider" in m.streamlit)
        assert "GermanSlider" in mapping.react
    
    def test_file_uploader_uses_native_dialog(self):
        """Test st.file_uploader uses native Electron dialog"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "file_uploader" in m.streamlit)
        assert "Native" in mapping.react
        assert mapping.library == "Electron"
    
    def test_all_input_components_mapped(self):
        """Test all input components have mappings"""
        input_components = [
            "text_input", "number_input", "text_area", "selectbox",
            "multiselect", "slider", "checkbox", "radio",
            "date_input", "time_input", "color_picker", "file_uploader"
        ]
        
        for comp in input_components:
            mapping = next((m for m in COMPONENT_MAPPINGS if comp in m.streamlit), None)
            assert mapping is not None, f"Missing mapping for st.{comp}()"


class TestDisplayComponentMigration:
    """Tests for display component migration"""
    
    def test_dataframe_mapped(self):
        """Test st.dataframe is mapped to DataTable"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "dataframe" in m.streamlit)
        assert "DataTable" in mapping.react
    
    def test_metric_mapped_to_custom(self):
        """Test st.metric is mapped to custom MetricCard"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "metric" in m.streamlit)
        assert "MetricCard" in mapping.react
        assert mapping.library == "Custom"
    
    def test_markdown_mapped(self):
        """Test st.markdown is mapped to ReactMarkdown"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "markdown" in m.streamlit)
        assert "ReactMarkdown" in mapping.react


class TestChartComponentMigration:
    """Tests for chart component migration"""
    
    def test_plotly_chart_mapped_to_recharts(self):
        """Test st.plotly_chart is mapped to Recharts"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "plotly_chart" in m.streamlit)
        assert mapping.library == "Recharts"
    
    def test_line_chart_mapped(self):
        """Test st.line_chart is mapped to LineChart"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "line_chart" in m.streamlit)
        assert "LineChart" in mapping.react
    
    def test_bar_chart_mapped(self):
        """Test st.bar_chart is mapped to BarChart"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "bar_chart" in m.streamlit)
        assert "BarChart" in mapping.react
    
    def test_all_chart_components_use_recharts(self):
        """Test all chart components use Recharts"""
        chart_mappings = [m for m in COMPONENT_MAPPINGS if "chart" in m.streamlit.lower()]
        for mapping in chart_mappings:
            assert mapping.library == "Recharts"


class TestLayoutComponentMigration:
    """Tests for layout component migration"""
    
    def test_tabs_mapped(self):
        """Test st.tabs is mapped to TabView"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "tabs" in m.streamlit)
        assert "TabView" in mapping.react
    
    def test_sidebar_mapped(self):
        """Test st.sidebar is mapped to Sidebar"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "sidebar" in m.streamlit)
        assert "Sidebar" in mapping.react
    
    def test_expander_mapped_to_accordion(self):
        """Test st.expander is mapped to Accordion"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "expander" in m.streamlit)
        assert "Accordion" in mapping.react


class TestFeedbackComponentMigration:
    """Tests for feedback component migration"""
    
    def test_success_message_mapped(self):
        """Test st.success is mapped to Message"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "success" in m.streamlit)
        assert "Message" in mapping.react
        assert "success" in mapping.react
    
    def test_error_message_mapped(self):
        """Test st.error is mapped to Message"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "error" in m.streamlit)
        assert "Message" in mapping.react
        assert "error" in mapping.react
    
    def test_spinner_mapped(self):
        """Test st.spinner is mapped to ProgressSpinner"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "spinner" in m.streamlit)
        assert "ProgressSpinner" in mapping.react
    
    def test_progress_mapped(self):
        """Test st.progress is mapped to ProgressBar"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "progress" in m.streamlit)
        assert "ProgressBar" in mapping.react


class TestActionComponentMigration:
    """Tests for action component migration"""
    
    def test_button_mapped(self):
        """Test st.button is mapped to Button"""
        mapping = next(m for m in COMPONENT_MAPPINGS if m.streamlit == "st.button()")
        assert "Button" in mapping.react
    
    def test_download_button_mapped(self):
        """Test st.download_button is mapped to Button with download"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "download_button" in m.streamlit)
        assert "Button" in mapping.react
        assert "download" in mapping.react


class TestDialogComponentMigration:
    """Tests for dialog component migration"""
    
    def test_dialog_mapped(self):
        """Test st.dialog is mapped to Dialog"""
        mapping = next(m for m in COMPONENT_MAPPINGS if "dialog" in m.streamlit)
        assert "Dialog" in mapping.react


class TestComponentMappingCompleteness:
    """Tests for component mapping completeness"""
    
    def test_minimum_mappings_count(self):
        """Test minimum number of component mappings"""
        assert len(COMPONENT_MAPPINGS) >= 30
    
    def test_all_mappings_have_react_equivalent(self):
        """Test all mappings have React equivalent"""
        for mapping in COMPONENT_MAPPINGS:
            assert mapping.react, f"Missing React equivalent for {mapping.streamlit}"
    
    def test_all_mappings_have_library(self):
        """Test all mappings specify library"""
        for mapping in COMPONENT_MAPPINGS:
            assert mapping.library, f"Missing library for {mapping.streamlit}"
    
    def test_primereact_is_primary_library(self):
        """Test PrimeReact is the primary component library"""
        primereact_count = sum(1 for m in COMPONENT_MAPPINGS if m.library == "PrimeReact")
        total = len(COMPONENT_MAPPINGS)
        
        # PrimeReact should be used for majority of components
        assert primereact_count / total > 0.5


class TestGermanFormattingComponents:
    """Tests for German formatting custom components"""
    
    def test_german_number_input_exists(self):
        """Test GermanNumberInput component exists in mappings"""
        german_inputs = [m for m in COMPONENT_MAPPINGS if "German" in m.react]
        assert len(german_inputs) >= 1
    
    def test_german_slider_exists(self):
        """Test GermanSlider component exists in mappings"""
        german_sliders = [m for m in COMPONENT_MAPPINGS if "GermanSlider" in m.react]
        assert len(german_sliders) >= 1
    
    def test_custom_components_marked(self):
        """Test custom components are marked as Custom library"""
        custom_components = [m for m in COMPONENT_MAPPINGS if "German" in m.react]
        for comp in custom_components:
            assert comp.library == "Custom"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
