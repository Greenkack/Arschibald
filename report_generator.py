"""report_generator.py - Report Generation System"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

class ReportGenerator:
    """Report-Generator für verschiedene Formate"""
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """Generiere Text-Summary-Report"""
        report = []
        report.append(f"=" * 80)
        report.append(f"REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"=" * 80)
        report.append("")
        
        for key, value in data.items():
            if isinstance(value, dict):
                report.append(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    report.append(f"  {sub_key}: {sub_value}")
            else:
                report.append(f"{key}: {value}")
        
        report.append("")
        report.append(f"=" * 80)
        
        return "\n".join(report)
    
    def generate_html_report(self, title: str, sections: List[Dict[str, Any]]) -> str:
        """Generiere HTML-Report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #4472C4; }}
        h2 {{ color: #5B9BD5; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4472C4; color: white; }}
        .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">Erstellt am: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
        
        for section in sections:
            html += f"\n    <h2>{section['title']}</h2>\n"
            
            if 'content' in section:
                html += f"    <p>{section['content']}</p>\n"
            
            if 'metrics' in section:
                for metric_key, metric_value in section['metrics'].items():
                    html += f"""    <div class="metric">
        <strong>{metric_key}:</strong> {metric_value}
    </div>\n"""
            
            if 'table' in section:
                df = section['table']
                html += "\n    " + df.to_html(index=False) + "\n"
        
        html += """
</body>
</html>
"""
        return html
    
    def create_chart_base64(self, data: Dict[str, List], chart_type: str = 'bar') -> str:
        """Erstelle Chart als Base64-String"""
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'bar':
            plt.bar(data.keys(), data.values())
        elif chart_type == 'line':
            plt.plot(list(data.keys()), list(data.values()), marker='o')
        elif chart_type == 'pie':
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        
        plt.tight_layout()
        
        # Zu Base64 konvertieren
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def export_report_to_file(self, content: str, file_path: str, format: str = 'html'):
        """Exportiere Report in Datei"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
