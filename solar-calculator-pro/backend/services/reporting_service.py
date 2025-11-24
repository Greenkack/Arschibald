# Reporting and Analytics Service

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import json
import io
import csv

from backend.models.reporting_models import (
    Report, ReportSchedule, ReportExecution, Dashboard, DashboardWidget,
    KPI, KPIValue, PredictionModel as PredictionModelDB, Prediction, DataExport
)
from backend.models.reporting_schemas import (
    ReportDefinition, ReportCreate, ReportExecute, ReportResponse,
    ScheduleCreate, ScheduleResponse, WidgetCreate, WidgetResponse,
    DashboardCreate, DashboardResponse, KPICreate, KPIResponse,
    PredictionRequest, PredictionResponse, ExportRequest, ExportResponse,
    ReportFormat, ExportFormat, AggregationType
)


class ReportingService:
    """Service for reporting and analytics"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Report Builder ====================

    def create_report(self, report_data: ReportCreate, user_id: int) -> Report:
        """Create a new report definition"""
        report = Report(
            name=report_data.definition.name,
            description=report_data.definition.description,
            report_type=report_data.definition.report_type,
            definition=report_data.definition.dict(),
            owner_id=user_id,
            is_public=report_data.is_public,
            tags=report_data.tags
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report

    def execute_report(self, execute_request: ReportExecute, user_id: int) -> ReportResponse:
        """Execute a report and return results"""
        report = self.db.query(Report).filter(Report.id == execute_request.report_id).first()
        
        if not report:
            raise ValueError(f"Report {execute_request.report_id} not found")
        
        # Start execution tracking
        execution = ReportExecution(
            report_id=report.id,
            executed_by=user_id,
            parameters=execute_request.parameters,
            format=execute_request.format,
            status="running"
        )
        self.db.add(execution)
        self.db.commit()
        
        start_time = datetime.now()
        
        try:
            # Build and execute query
            definition = ReportDefinition(**report.definition)
            query_result = self._build_and_execute_query(definition, execute_request.parameters)
            
            # Apply aggregations
            if definition.group_by:
                query_result = self._apply_aggregations(query_result, definition)
            
            # Generate visualizations
            visualizations = []
            for viz_config in definition.visualizations:
                viz_data = self._generate_visualization(query_result, viz_config)
                visualizations.append(viz_data)
            
            # Update execution status
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            execution.status = "success"
            execution.execution_time_ms = int(execution_time)
            execution.row_count = len(query_result)
            self.db.commit()
            
            return ReportResponse(
                id=report.id,
                name=report.name,
                report_type=report.report_type,
                executed_at=datetime.now(),
                data=query_result,
                metadata={
                    "execution_time_ms": execution_time,
                    "row_count": len(query_result),
                    "parameters": execute_request.parameters
                },
                visualizations=visualizations
            )
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            self.db.commit()
            raise

    def _build_and_execute_query(self, definition: ReportDefinition, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build and execute SQL query from report definition"""
        # Build SELECT clause
        select_fields = [f.name for f in definition.fields]
        select_clause = ", ".join(select_fields)
        
        # Build FROM clause
        from_clause = definition.data_source
        
        # Build WHERE clause
        where_conditions = []
        for filter_item in definition.filters:
            condition = self._build_filter_condition(filter_item, parameters)
            where_conditions.append(condition)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Build GROUP BY clause
        group_by_clause = ""
        if definition.group_by:
            group_by_clause = f"GROUP BY {', '.join(definition.group_by)}"
        
        # Build ORDER BY clause
        order_by_clause = ""
        if definition.sorts:
            sort_expressions = [f"{s.field} {s.direction.upper()}" for s in definition.sorts]
            order_by_clause = f"ORDER BY {', '.join(sort_expressions)}"
        
        # Build LIMIT clause
        limit_clause = f"LIMIT {definition.limit}" if definition.limit else ""
        
        # Construct full query
        query = f"""
            SELECT {select_clause}
            FROM {from_clause}
            WHERE {where_clause}
            {group_by_clause}
            {order_by_clause}
            {limit_clause}
        """
        
        # Execute query
        result = self.db.execute(text(query))
        rows = result.fetchall()
        
        # Convert to list of dicts
        return [dict(row._mapping) for row in rows]

    def _build_filter_condition(self, filter_item, parameters: Dict[str, Any]) -> str:
        """Build SQL condition from filter"""
        field = filter_item.field
        operator = filter_item.operator
        value = filter_item.value
        
        # Replace parameter placeholders
        if isinstance(value, str) and value.startswith("$"):
            param_name = value[1:]
            value = parameters.get(param_name, value)
        
        # Build condition based on operator
        if operator == "eq":
            return f"{field} = '{value}'"
        elif operator == "ne":
            return f"{field} != '{value}'"
        elif operator == "gt":
            return f"{field} > {value}"
        elif operator == "lt":
            return f"{field} < {value}"
        elif operator == "gte":
            return f"{field} >= {value}"
        elif operator == "lte":
            return f"{field} <= {value}"
        elif operator == "in":
            values = "', '".join(str(v) for v in value)
            return f"{field} IN ('{values}')"
        elif operator == "between":
            return f"{field} BETWEEN {value[0]} AND {value[1]}"
        elif operator == "like":
            return f"{field} LIKE '%{value}%'"
        else:
            return "1=1"

    def _apply_aggregations(self, data: List[Dict[str, Any]], definition: ReportDefinition) -> List[Dict[str, Any]]:
        """Apply aggregations to grouped data"""
        df = pd.DataFrame(data)
        
        # Group by specified fields
        grouped = df.groupby(definition.group_by)
        
        # Apply aggregations
        agg_dict = {}
        for field in definition.fields:
            if field.aggregation:
                if field.aggregation == AggregationType.SUM:
                    agg_dict[field.name] = 'sum'
                elif field.aggregation == AggregationType.AVG:
                    agg_dict[field.name] = 'mean'
                elif field.aggregation == AggregationType.COUNT:
                    agg_dict[field.name] = 'count'
                elif field.aggregation == AggregationType.MIN:
                    agg_dict[field.name] = 'min'
                elif field.aggregation == AggregationType.MAX:
                    agg_dict[field.name] = 'max'
                elif field.aggregation == AggregationType.MEDIAN:
                    agg_dict[field.name] = 'median'
        
        if agg_dict:
            result_df = grouped.agg(agg_dict).reset_index()
            return result_df.to_dict('records')
        
        return data

    def _generate_visualization(self, data: List[Dict[str, Any]], viz_config) -> Dict[str, Any]:
        """Generate visualization data"""
        df = pd.DataFrame(data)
        
        return {
            "type": viz_config.chart_type,
            "title": viz_config.title,
            "x_axis": viz_config.x_axis,
            "y_axis": viz_config.y_axis,
            "data": {
                "labels": df[viz_config.x_axis].tolist(),
                "values": df[viz_config.y_axis].tolist()
            },
            "color_scheme": viz_config.color_scheme
        }

    # ==================== Scheduled Reports ====================

    def create_schedule(self, schedule_data: ScheduleCreate) -> ReportSchedule:
        """Create a report schedule"""
        # Calculate next run time
        next_run = self._calculate_next_run(schedule_data.frequency, schedule_data.time_of_day)
        
        schedule = ReportSchedule(
            report_id=schedule_data.report_id,
            frequency=schedule_data.frequency,
            time_of_day=schedule_data.time_of_day,
            recipients=schedule_data.recipients,
            format=schedule_data.format,
            enabled=schedule_data.enabled,
            next_run=next_run
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule

    def _calculate_next_run(self, frequency: str, time_of_day: str) -> datetime:
        """Calculate next run time for schedule"""
        now = datetime.now()
        hour, minute = map(int, time_of_day.split(':'))
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            if frequency == "daily":
                next_run += timedelta(days=1)
            elif frequency == "weekly":
                next_run += timedelta(weeks=1)
            elif frequency == "monthly":
                next_run += timedelta(days=30)
            elif frequency == "quarterly":
                next_run += timedelta(days=90)
            elif frequency == "yearly":
                next_run += timedelta(days=365)
        
        return next_run

    def get_due_schedules(self) -> List[ReportSchedule]:
        """Get schedules that are due to run"""
        now = datetime.now()
        return self.db.query(ReportSchedule).filter(
            and_(
                ReportSchedule.enabled == True,
                ReportSchedule.next_run <= now
            )
        ).all()

    # ==================== Dashboard Widgets ====================

    def create_dashboard(self, dashboard_data: DashboardCreate, user_id: int) -> Dashboard:
        """Create a new dashboard"""
        dashboard = Dashboard(
            name=dashboard_data.name,
            description=dashboard_data.description,
            owner_id=user_id,
            is_public=dashboard_data.is_public,
            layout=dashboard_data.layout
        )
        
        self.db.add(dashboard)
        self.db.commit()
        self.db.refresh(dashboard)
        
        return dashboard

    def create_widget(self, widget_data: WidgetCreate) -> DashboardWidget:
        """Create a dashboard widget"""
        widget = DashboardWidget(
            dashboard_id=widget_data.dashboard_id,
            config=widget_data.config.dict(),
            position_x=widget_data.position_x,
            position_y=widget_data.position_y
        )
        
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        
        return widget

    def get_widget_data(self, widget_id: int) -> Dict[str, Any]:
        """Get data for a widget"""
        widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        
        if not widget:
            raise ValueError(f"Widget {widget_id} not found")
        
        config = widget.config
        query = config.get('query', {})
        
        # Execute widget query
        result = self.db.execute(text(query.get('sql', 'SELECT 1')))
        rows = result.fetchall()
        
        return {
            "widget_id": widget_id,
            "data": [dict(row._mapping) for row in rows],
            "last_updated": datetime.now()
        }

    # ==================== KPI Tracking ====================

    def create_kpi(self, kpi_data: KPICreate, user_id: int) -> KPI:
        """Create a new KPI"""
        kpi = KPI(
            name=kpi_data.name,
            metric=kpi_data.metric,
            target=kpi_data.target.dict(),
            data_source=kpi_data.data_source,
            calculation=kpi_data.calculation,
            owner_id=user_id
        )
        
        self.db.add(kpi)
        self.db.commit()
        self.db.refresh(kpi)
        
        return kpi

    def calculate_kpi(self, kpi_id: int) -> KPIResponse:
        """Calculate current KPI value"""
        kpi = self.db.query(KPI).filter(KPI.id == kpi_id).first()
        
        if not kpi:
            raise ValueError(f"KPI {kpi_id} not found")
        
        # Execute calculation query
        calculation = kpi.calculation
        query = calculation.get('sql', '')
        result = self.db.execute(text(query))
        row = result.fetchone()
        
        current_value = float(row[0]) if row else 0.0
        target_value = float(kpi.target['target_value'])
        achievement_percentage = (current_value / target_value * 100) if target_value > 0 else 0
        
        # Determine trend
        recent_values = self.db.query(KPIValue).filter(
            KPIValue.kpi_id == kpi_id
        ).order_by(KPIValue.calculated_at.desc()).limit(2).all()
        
        trend = "stable"
        if len(recent_values) >= 2:
            if recent_values[0].value > recent_values[1].value:
                trend = "up"
            elif recent_values[0].value < recent_values[1].value:
                trend = "down"
        
        # Save KPI value
        kpi_value = KPIValue(
            kpi_id=kpi_id,
            value=current_value,
            target_value=target_value,
            achievement_percentage=achievement_percentage,
            period_start=datetime.now().replace(day=1),
            period_end=datetime.now()
        )
        self.db.add(kpi_value)
        self.db.commit()
        
        return KPIResponse(
            id=kpi.id,
            name=kpi.name,
            metric=kpi.metric,
            current_value=current_value,
            target_value=target_value,
            achievement_percentage=achievement_percentage,
            trend=trend,
            period=kpi.target['period'],
            last_updated=datetime.now()
        )

    # ==================== Predictive Analytics ====================

    def create_prediction(self, prediction_request: PredictionRequest, user_id: int) -> PredictionResponse:
        """Create predictions using machine learning"""
        # Fetch historical data
        query = f"SELECT * FROM {prediction_request.data_source} ORDER BY created_at DESC LIMIT 1000"
        result = self.db.execute(text(query))
        rows = result.fetchall()
        df = pd.DataFrame([dict(row._mapping) for row in rows])
        
        # Prepare features and target
        X = df[prediction_request.feature_fields].values
        y = df[prediction_request.target_field].values
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        if prediction_request.model_type == "linear_regression":
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X_scaled, y)
        
        # Generate predictions
        future_dates = pd.date_range(
            start=datetime.now(),
            periods=prediction_request.prediction_period,
            freq='D'
        )
        
        # Create future feature values (simplified - would need more sophisticated approach)
        last_features = X_scaled[-1:]
        future_X = np.repeat(last_features, prediction_request.prediction_period, axis=0)
        
        predictions = model.predict(future_X)
        
        # Calculate confidence intervals
        std_dev = np.std(y - model.predict(X_scaled))
        z_score = 1.96  # 95% confidence
        margin = z_score * std_dev
        
        prediction_data = []
        confidence_intervals = []
        
        for i, (date, pred) in enumerate(zip(future_dates, predictions)):
            prediction_data.append({
                "date": date.isoformat(),
                "predicted_value": float(pred)
            })
            confidence_intervals.append({
                "date": date.isoformat(),
                "lower_bound": float(pred - margin),
                "upper_bound": float(pred + margin)
            })
        
        # Calculate accuracy metrics
        y_pred = model.predict(X_scaled)
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        r2 = model.score(X_scaled, y)
        
        accuracy_metrics = {
            "mse": float(mse),
            "rmse": float(rmse),
            "r2_score": float(r2)
        }
        
        # Feature importance
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            for feature, importance in zip(prediction_request.feature_fields, model.feature_importances_):
                feature_importance[feature] = float(importance)
        
        # Save model
        model_db = PredictionModelDB(
            name=f"{prediction_request.target_field}_prediction",
            model_type=prediction_request.model_type,
            data_source=prediction_request.data_source,
            target_field=prediction_request.target_field,
            feature_fields=prediction_request.feature_fields,
            model_data={"scaler": "saved", "model": "saved"},  # Would serialize properly
            accuracy_metrics=accuracy_metrics,
            created_by=user_id
        )
        self.db.add(model_db)
        self.db.commit()
        
        # Save predictions
        prediction_db = Prediction(
            model_id=model_db.id,
            predictions=prediction_data,
            confidence_intervals=confidence_intervals,
            prediction_period=prediction_request.prediction_period
        )
        self.db.add(prediction_db)
        self.db.commit()
        
        return PredictionResponse(
            model_type=prediction_request.model_type,
            predictions=prediction_data,
            confidence_intervals=confidence_intervals,
            accuracy_metrics=accuracy_metrics,
            feature_importance=feature_importance,
            generated_at=datetime.now()
        )

    # ==================== Data Export ====================

    def export_data(self, export_request: ExportRequest, user_id: int) -> ExportResponse:
        """Export data in specified format"""
        # Build query
        fields = export_request.fields if export_request.fields else ["*"]
        select_clause = ", ".join(fields)
        
        where_conditions = []
        for filter_item in export_request.filters:
            condition = self._build_filter_condition(filter_item, {})
            where_conditions.append(condition)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"SELECT {select_clause} FROM {export_request.data_source} WHERE {where_clause}"
        
        # Execute query
        result = self.db.execute(text(query))
        rows = result.fetchall()
        data = [dict(row._mapping) for row in rows]
        
        # Generate file
        file_name = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_request.format.value}"
        file_path = f"/tmp/{file_name}"
        
        if export_request.format == ExportFormat.CSV:
            self._export_csv(data, file_path, export_request.include_headers, export_request.german_formatting)
        elif export_request.format == ExportFormat.EXCEL:
            self._export_excel(data, file_path, export_request.german_formatting)
        elif export_request.format == ExportFormat.JSON:
            self._export_json(data, file_path)
        
        # Get file size
        import os
        file_size = os.path.getsize(file_path)
        
        # Save export record
        export_record = DataExport(
            data_source=export_request.data_source,
            filters=[f.dict() for f in export_request.filters],
            fields=export_request.fields,
            format=export_request.format,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            row_count=len(data),
            exported_by=user_id,
            expires_at=datetime.now() + timedelta(days=7)
        )
        self.db.add(export_record)
        self.db.commit()
        
        return ExportResponse(
            file_name=file_name,
            file_size=file_size,
            download_url=f"/api/v1/exports/download/{export_record.id}",
            expires_at=export_record.expires_at,
            format=export_request.format
        )

    def _export_csv(self, data: List[Dict[str, Any]], file_path: str, include_headers: bool, german_formatting: bool):
        """Export data to CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                if include_headers:
                    writer.writeheader()
                
                for row in data:
                    if german_formatting:
                        row = self._format_row_german(row)
                    writer.writerow(row)

    def _export_excel(self, data: List[Dict[str, Any]], file_path: str, german_formatting: bool):
        """Export data to Excel"""
        df = pd.DataFrame(data)
        if german_formatting:
            # Apply German formatting to numeric columns
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col] = df[col].apply(lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        df.to_excel(file_path, index=False)

    def _export_json(self, data: List[Dict[str, Any]], file_path: str):
        """Export data to JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def _format_row_german(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Format row values with German number formatting"""
        formatted_row = {}
        for key, value in row.items():
            if isinstance(value, (int, float)):
                formatted_row[key] = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                formatted_row[key] = value
        return formatted_row
