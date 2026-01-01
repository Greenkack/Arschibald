"""grid_controller.py - Grid Controller for Data Management"""
import pandas as pd
from typing import Dict, Any, List, Optional

class GridController:
    """Controller für Grid-Daten-Management"""
    
    def __init__(self, initial_data: Optional[pd.DataFrame] = None):
        self.data = initial_data if initial_data is not None else pd.DataFrame()
        self.filters = {}
        self.sort_config = {}
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Wende Filter auf Daten an"""
        filtered_data = self.data.copy()
        
        for column, value in filters.items():
            if column in filtered_data.columns:
                if isinstance(value, (list, tuple)):
                    filtered_data = filtered_data[filtered_data[column].isin(value)]
                else:
                    filtered_data = filtered_data[filtered_data[column] == value]
        
        return filtered_data
    
    def apply_sort(self, column: str, ascending: bool = True) -> pd.DataFrame:
        """Sortiere Daten"""
        return self.data.sort_values(by=column, ascending=ascending)
    
    def add_row(self, row_data: Dict[str, Any]):
        """Füge neue Zeile hinzu"""
        new_row = pd.DataFrame([row_data])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
    
    def update_row(self, index: int, row_data: Dict[str, Any]):
        """Aktualisiere Zeile"""
        for column, value in row_data.items():
            if column in self.data.columns:
                self.data.at[index, column] = value
    
    def delete_rows(self, indices: List[int]):
        """Lösche Zeilen"""
        self.data = self.data.drop(indices).reset_index(drop=True)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Hole zusammenfassende Statistiken"""
        return {
            'total_rows': len(self.data),
            'columns': list(self.data.columns),
            'numeric_columns': list(self.data.select_dtypes(include=['number']).columns)
        }
