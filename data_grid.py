"""data_grid.py - Interactive Data Grid Component"""
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List

class DataGrid:
    """Interaktive Daten-Grid-Komponente"""
    
    def __init__(self, data: pd.DataFrame, key: str = "data_grid"):
        self.data = data
        self.key = key
        self.edited_data = None
    
    def render(self, editable: bool = False, height: int = 400):
        """Rendere Data Grid"""
        if editable:
            self.edited_data = st.data_editor(
                self.data,
                key=self.key,
                height=height,
                use_container_width=True
            )
            return self.edited_data
        else:
            st.dataframe(self.data, height=height, use_container_width=True)
            return self.data
    
    def get_selected_rows(self) -> List[int]:
        """Hole ausgewählte Zeilen"""
        if f"{self.key}_selection" in st.session_state:
            return st.session_state[f"{self.key}_selection"]
        return []
    
    def export_to_excel(self, file_path: str):
        """Exportiere nach Excel"""
        data_to_export = self.edited_data if self.edited_data is not None else self.data
        data_to_export.to_excel(file_path, index=False)
