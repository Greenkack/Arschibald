/**
 * Pipeline Analytics Component
 * Comprehensive analytics and forecasting for sales pipeline
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Chart } from 'primereact/chart';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Calendar } from 'primereact/calendar';
import { Button } from 'primereact/button';
import { TabView, TabPanel } from 'primereact/tabview';
import api from '../../services/api';
import './PipelineAnalytics.css';

export const PipelineAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [winLossAnalysis, setWinLossAnalysis] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [dateRange, setDateRange] = useState<Date[]>([
    new Date(new Date().setMonth(new Date().getMonth() - 3)),
    new Date()
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const params = {
        start_date: dateRange[0]?.toISOString(),
        end_date: dateRange[1]?.toISOString()
      };
      
      // Load pipeline analytics
      const analyticsResponse = await api.get('/api/v1/pipeline/analytics', { params });
      setAnalytics(analyticsResponse.data);
      
      // Load win/loss analysis
      const winLossResponse = await api.get('/api/v1/pipeline/analytics/win-loss', { params });
      setWinLossAnalysis(winLossResponse.data);
      
      // Generate forecast
      const forecastResponse = await api.post('/api/v1/pipeline/forecast', {
        period_start: new Date().toISOString(),
        period_end: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString()
      });
      setForecast(forecastResponse.data);
      
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Chart data for pipeline by stage
  const getStageChartData = () => {
    if (!analytics) return {};
    
    return {
      labels: analytics.by_stage.map((s: any) => s.name),
      datasets: [
        {
          label: 'Value',
          data: analytics.by_stage.map((s: any) => s.value),
          backgroundColor: [
            '#94A3B8',
            '#60A5FA',
            '#FBBF24',
            '#F59E0B',
            '#10B981',
            '#EF4444'
          ]
        }
      ]
    };
  };

  // Chart data for win/loss
  const getWinLossChartData = () => {
    if (!winLossAnalysis) return {};
    
    return {
      labels: ['Won', 'Lost'],
      datasets: [
        {
          data: [winLossAnalysis.total_won, winLossAnalysis.total_lost],
          backgroundColor: ['#10B981', '#EF4444']
        }
      ]
    };
  };

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  return (
    <div className="pipeline-analytics">
      <div className="analytics-header">
        <h2>Pipeline Analytics</h2>
        <div className="date-filter">
          <Calendar
            value={dateRange}
            onChange={(e) => setDateRange(e.value as Date[])}
            selectionMode="range"
            readOnlyInput
            showIcon
            dateFormat="dd.mm.yy"
          />
          <Button
            label="Refresh"
            icon="pi pi-refresh"
            onClick={loadAnalytics}
          />
        </div>
      </div>

      <TabView>
        <TabPanel header="Overview">
          <div className="metrics-grid">
            <Card title="Total Opportunities" className="metric-card">
              <div className="metric-value">{analytics?.total_opportunities || 0}</div>
            </Card>
            
            <Card title="Total Value" className="metric-card">
              <div className="metric-value">{formatCurrency(analytics?.total_value || 0)}</div>
            </Card>
            
            <Card title="Weighted Value" className="metric-card">
              <div className="metric-value">{formatCurrency(analytics?.weighted_value || 0)}</div>
            </Card>
            
            <Card title="Average Deal Size" className="metric-card">
              <div className="metric-value">{formatCurrency(analytics?.average_deal_size || 0)}</div>
            </Card>
            
            <Card title="Win Rate" className="metric-card">
              <div className="metric-value">{formatPercent(analytics?.win_rate || 0)}</div>
            </Card>
            
            <Card title="Avg Sales Cycle" className="metric-card">
              <div className="metric-value">{Math.round(analytics?.average_sales_cycle_days || 0)} days</div>
            </Card>
          </div>

          <div className="charts-grid">
            <Card title="Pipeline by Stage">
              <Chart type="bar" data={getStageChartData()} />
            </Card>
            
            <Card title="Pipeline by Source">
              <DataTable value={analytics?.by_source || []}>
                <Column field="source" header="Source" />
                <Column field="count" header="Count" />
                <Column 
                  field="value" 
                  header="Value" 
                  body={(rowData) => formatCurrency(rowData.value)}
                />
              </DataTable>
            </Card>
          </div>
        </TabPanel>

        <TabPanel header="Win/Loss Analysis">
          <div className="metrics-grid">
            <Card title="Total Won" className="metric-card success">
              <div className="metric-value">{winLossAnalysis?.total_won || 0}</div>
              <div className="metric-subtitle">
                {formatCurrency(winLossAnalysis?.total_won_value || 0)}
              </div>
            </Card>
            
            <Card title="Total Lost" className="metric-card danger">
              <div className="metric-value">{winLossAnalysis?.total_lost || 0}</div>
              <div className="metric-subtitle">
                {formatCurrency(winLossAnalysis?.total_lost_value || 0)}
              </div>
            </Card>
            
            <Card title="Win Rate" className="metric-card">
              <div className="metric-value">{formatPercent(winLossAnalysis?.win_rate || 0)}</div>
            </Card>
            
            <Card title="Avg Won Deal" className="metric-card">
              <div className="metric-value">
                {formatCurrency(winLossAnalysis?.average_won_deal_size || 0)}
              </div>
            </Card>
          </div>

          <div className="charts-grid">
            <Card title="Win/Loss Distribution">
              <Chart type="pie" data={getWinLossChartData()} />
            </Card>
            
            <Card title="Loss Reasons">
              <DataTable value={winLossAnalysis?.loss_reasons || []}>
                <Column field="reason" header="Reason" />
                <Column field="count" header="Count" />
              </DataTable>
            </Card>
          </div>

          <Card title="Top Competitors">
            <DataTable value={winLossAnalysis?.competitors || []}>
              <Column field="name" header="Competitor" />
              <Column field="count" header="Losses" />
            </DataTable>
          </Card>
        </TabPanel>

        <TabPanel header="Forecast">
          <div className="forecast-header">
            <h3>Pipeline Forecast</h3>
            <p>Next 3 months projection</p>
          </div>

          <div className="metrics-grid">
            <Card title="Expected Opportunities" className="metric-card">
              <div className="metric-value">{forecast?.total_opportunities || 0}</div>
            </Card>
            
            <Card title="Total Value" className="metric-card">
              <div className="metric-value">{formatCurrency(forecast?.total_value || 0)}</div>
            </Card>
            
            <Card title="Weighted Value" className="metric-card">
              <div className="metric-value">{formatCurrency(forecast?.weighted_value || 0)}</div>
            </Card>
            
            <Card title="Expected Wins" className="metric-card success">
              <div className="metric-value">{forecast?.expected_wins || 0}</div>
            </Card>
            
            <Card title="Expected Revenue" className="metric-card success">
              <div className="metric-value">{formatCurrency(forecast?.expected_revenue || 0)}</div>
            </Card>
            
            <Card title="Confidence Level" className="metric-card">
              <div className="metric-value">{formatPercent(forecast?.confidence_level || 0)}</div>
            </Card>
          </div>

          <Card title="Forecast Details">
            <p className="forecast-period">
              Period: {new Date(forecast?.period_start).toLocaleDateString('de-DE')} - {new Date(forecast?.period_end).toLocaleDateString('de-DE')}
            </p>
            <p className="forecast-note">
              This forecast is based on current pipeline data and historical win rates. 
              Confidence level indicates the reliability of the forecast based on data quality and completeness.
            </p>
          </Card>
        </TabPanel>
      </TabView>
    </div>
  );
};
