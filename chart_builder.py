"""chart_builder.py - Chart Building System"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional, Union

class ChartBuilder:
    """Chart-Builder für verschiedene Visualisierungen"""
    
    def __init__(self):
        self.color_scheme = px.colors.qualitative.Set2
    
    def create_bar_chart(self, data: Dict[str, Union[int, float]], title: str = "", 
                        x_label: str = "", y_label: str = "") -> go.Figure:
        """Erstelle Balkendiagramm"""
        fig = go.Figure(data=[
            go.Bar(x=list(data.keys()), y=list(data.values()), marker_color=self.color_scheme[0])
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white"
        )
        
        return fig
    
    def create_line_chart(self, data: Dict[str, Union[int, float]], title: str = "",
                         x_label: str = "", y_label: str = "") -> go.Figure:
        """Erstelle Liniendiagramm"""
        fig = go.Figure(data=[
            go.Scatter(x=list(data.keys()), y=list(data.values()), 
                      mode='lines+markers', line=dict(color=self.color_scheme[1]))
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white"
        )
        
        return fig
    
    def create_pie_chart(self, data: Dict[str, Union[int, float]], title: str = "") -> go.Figure:
        """Erstelle Kreisdiagramm"""
        fig = go.Figure(data=[
            go.Pie(labels=list(data.keys()), values=list(data.values()), 
                  marker=dict(colors=self.color_scheme))
        ])
        
        fig.update_layout(
            title=title,
            template="plotly_white"
        )
        
        return fig
    
    def create_multi_series_chart(self, data: Dict[str, Dict[str, Union[int, float]]], 
                                 title: str = "", chart_type: str = 'bar') -> go.Figure:
        """Erstelle Multi-Series Chart"""
        fig = go.Figure()
        
        for i, (series_name, series_data) in enumerate(data.items()):
            if chart_type == 'bar':
                fig.add_trace(go.Bar(
                    name=series_name,
                    x=list(series_data.keys()),
                    y=list(series_data.values()),
                    marker_color=self.color_scheme[i % len(self.color_scheme)]
                ))
            elif chart_type == 'line':
                fig.add_trace(go.Scatter(
                    name=series_name,
                    x=list(series_data.keys()),
                    y=list(series_data.values()),
                    mode='lines+markers',
                    line=dict(color=self.color_scheme[i % len(self.color_scheme)])
                ))
        
        fig.update_layout(
            title=title,
            barmode='group' if chart_type == 'bar' else None,
            template="plotly_white"
        )
        
        return fig
    
    def create_heatmap(self, data: pd.DataFrame, title: str = "") -> go.Figure:
        """Erstelle Heatmap"""
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='RdYlGn'
        ))
        
        fig.update_layout(
            title=title,
            template="plotly_white"
        )
        
        return fig
    
    def create_gauge_chart(self, value: float, title: str = "", 
                          max_value: float = 100, threshold: Optional[float] = None) -> go.Figure:
        """Erstelle Gauge Chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            delta={'reference': threshold if threshold else value * 0.9},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': self.color_scheme[0]},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "lightgray"},
                    {'range': [max_value * 0.5, max_value * 0.75], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold if threshold else max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(template="plotly_white")
        
        return fig
