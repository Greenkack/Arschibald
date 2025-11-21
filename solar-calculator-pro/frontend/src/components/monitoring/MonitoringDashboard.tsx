/**
 * Monitoring Dashboard Component
 * 
 * Displays post-release monitoring data including performance, crashes, feedback, and updates.
 * Requirement: 8.1 - Performance monitoring and tracking
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { TabView, TabPanel } from 'primereact/tabview';
import { Chart } from 'primereact/chart';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Badge } from 'primereact/badge';
import { ProgressBar } from 'primereact/progressbar';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import api from '../../services/api';
import './MonitoringDashboard.css';


interface PerformanceSummary {
  period: {
    start: string;
    end: string;
  };
  system: {
    cpu_percent: number;
    memory_percent: number;
    memory_available_mb: number;
    disk_percent: number;
    disk_free_gb: number;
  };
  metrics: {
    api_calls: number;
    errors: number;
    average_response_time_ms: number;
    peak_memory_mb: number;
  };
}

interface CrashStatistics {
  total_crashes: number;
  unique_errors: number;
  affected_users: number;
  crash_free_rate: number;
  most_common_errors: Array<{
    error_type: string;
    count: number;
  }>;
}

interface FeedbackSummary {
  total_feedback: number;
  by_type: {
    bug: number;
    feature_request: number;
    improvement: number;
    praise: number;
  };
  average_rating: number;
  sentiment: string;
}

interface UpdateAdoptionStats {
  version: string;
  total_users: number;
  updated_users: number;
  adoption_rate: number;
  success_rate: number;
}


export const MonitoringDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState(7);
  const [performanceData, setPerformanceData] = useState<PerformanceSummary | null>(null);
  const [crashStats, setCrashStats] = useState<CrashStatistics | null>(null);
  const [feedbackSummary, setFeedbackSummary] = useState<FeedbackSummary | null>(null);
  const [updateStats, setUpdateStats] = useState<UpdateAdoptionStats | null>(null);
  const [loading, setLoading] = useState(true);

  const timeRangeOptions = [
    { label: 'Last 24 Hours', value: 1 },
    { label: 'Last 7 Days', value: 7 },
    { label: 'Last 30 Days', value: 30 },
    { label: 'Last 90 Days', value: 90 }
  ];

  useEffect(() => {
    loadMonitoringData();
  }, [timeRange]);

  const loadMonitoringData = async () => {
    setLoading(true);
    try {
      const [performance, crashes, feedback] = await Promise.all([
        api.get('/api/v1/monitoring/performance/summary'),
        api.get(`/api/v1/monitoring/crashes/statistics?days=${timeRange}`),
        api.get(`/api/v1/monitoring/feedback/summary?days=${timeRange}`)
      ]);

      setPerformanceData(performance.data);
      setCrashStats(crashes.data);
      setFeedbackSummary(feedback.data);
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthBadge = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) {
      return <Badge value="Critical" severity="danger" />;
    } else if (value >= thresholds.warning) {
      return <Badge value="Warning" severity="warning" />;
    }
    return <Badge value="Healthy" severity="success" />;
  };

  const renderPerformanceTab = () => {
    if (!performanceData) return <div>Loading...</div>;

    const systemMetrics = performanceData.system;

    const cpuChartData = {
      labels: ['CPU Usage'],
      datasets: [{
        data: [systemMetrics.cpu_percent, 100 - systemMetrics.cpu_percent],
        backgroundColor: ['#FF6384', '#E0E0E0']
      }]
    };

    const memoryChartData = {
      labels: ['Memory Usage'],
      datasets: [{
        data: [systemMetrics.memory_percent, 100 - systemMetrics.memory_percent],
        backgroundColor: ['#36A2EB', '#E0E0E0']
      }]
    };

    return (
      <div className="performance-tab">
        <div className="metrics-grid">
          <Card title="CPU Usage" className="metric-card">
            <div className="metric-content">
              <Chart type="doughnut" data={cpuChartData} style={{ width: '200px' }} />
              <div className="metric-value">
                <h2>{systemMetrics.cpu_percent.toFixed(1)}%</h2>
                {getHealthBadge(systemMetrics.cpu_percent, { warning: 70, critical: 90 })}
              </div>
            </div>
          </Card>

          <Card title="Memory Usage" className="metric-card">
            <div className="metric-content">
              <Chart type="doughnut" data={memoryChartData} style={{ width: '200px' }} />
              <div className="metric-value">
                <h2>{systemMetrics.memory_percent.toFixed(1)}%</h2>
                <p>{systemMetrics.memory_available_mb.toFixed(0)} MB available</p>
                {getHealthBadge(systemMetrics.memory_percent, { warning: 80, critical: 95 })}
              </div>
            </div>
          </Card>

          <Card title="Disk Usage" className="metric-card">
            <div className="metric-content">
              <ProgressBar value={systemMetrics.disk_percent} />
              <div className="metric-value">
                <h2>{systemMetrics.disk_percent.toFixed(1)}%</h2>
                <p>{systemMetrics.disk_free_gb.toFixed(1)} GB free</p>
              </div>
            </div>
          </Card>

          <Card title="API Performance" className="metric-card">
            <div className="metric-stats">
              <div className="stat-item">
                <span className="stat-label">API Calls</span>
                <span className="stat-value">{performanceData.metrics.api_calls}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Errors</span>
                <span className="stat-value">{performanceData.metrics.errors}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Response Time</span>
                <span className="stat-value">{performanceData.metrics.average_response_time_ms}ms</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  };

  const renderCrashesTab = () => {
    if (!crashStats) return <div>Loading...</div>;

    const crashFreeRate = crashStats.crash_free_rate;

    return (
      <div className="crashes-tab">
        <div className="crash-summary">
          <Card title="Crash Overview" className="summary-card">
            <div className="crash-metrics">
              <div className="metric-item">
                <h3>{crashStats.total_crashes}</h3>
                <p>Total Crashes</p>
              </div>
              <div className="metric-item">
                <h3>{crashStats.unique_errors}</h3>
                <p>Unique Errors</p>
              </div>
              <div className="metric-item">
                <h3>{crashStats.affected_users}</h3>
                <p>Affected Users</p>
              </div>
              <div className="metric-item">
                <h3>{crashFreeRate.toFixed(2)}%</h3>
                <p>Crash-Free Rate</p>
                {getHealthBadge(100 - crashFreeRate, { warning: 5, critical: 10 })}
              </div>
            </div>
          </Card>
        </div>

        <Card title="Most Common Errors" className="errors-card">
          <DataTable value={crashStats.most_common_errors} responsiveLayout="scroll">
            <Column field="error_type" header="Error Type" />
            <Column field="count" header="Count" />
            <Column 
              header="Actions" 
              body={(rowData) => (
                <Button label="View Details" size="small" />
              )}
            />
          </DataTable>
        </Card>
      </div>
    );
  };

  const renderFeedbackTab = () => {
    if (!feedbackSummary) return <div>Loading...</div>;

    const feedbackChartData = {
      labels: ['Bugs', 'Feature Requests', 'Improvements', 'Praise'],
      datasets: [{
        data: [
          feedbackSummary.by_type.bug,
          feedbackSummary.by_type.feature_request,
          feedbackSummary.by_type.improvement,
          feedbackSummary.by_type.praise
        ],
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
      }]
    };

    return (
      <div className="feedback-tab">
        <div className="feedback-summary">
          <Card title="Feedback Overview" className="summary-card">
            <div className="feedback-metrics">
              <div className="metric-item">
                <h3>{feedbackSummary.total_feedback}</h3>
                <p>Total Feedback</p>
              </div>
              <div className="metric-item">
                <h3>{feedbackSummary.average_rating.toFixed(1)}/5</h3>
                <p>Average Rating</p>
              </div>
              <div className="metric-item">
                <Badge 
                  value={feedbackSummary.sentiment} 
                  severity={
                    feedbackSummary.sentiment === 'positive' ? 'success' :
                    feedbackSummary.sentiment === 'negative' ? 'danger' : 'info'
                  }
                />
                <p>Sentiment</p>
              </div>
            </div>
          </Card>
        </div>

        <Card title="Feedback by Type" className="chart-card">
          <Chart type="pie" data={feedbackChartData} />
        </Card>
      </div>
    );
  };

  const renderUpdatesTab = () => {
    return (
      <div className="updates-tab">
        <Card title="Update Adoption" className="adoption-card">
          <p>Update adoption tracking will be displayed here.</p>
          <Button label="View Version Distribution" />
        </Card>
      </div>
    );
  };

  return (
    <div className="monitoring-dashboard">
      <div className="dashboard-header">
        <h1>📊 Post-Release Monitoring</h1>
        <div className="header-controls">
          <Dropdown
            value={timeRange}
            options={timeRangeOptions}
            onChange={(e) => setTimeRange(e.value)}
            placeholder="Select Time Range"
          />
          <Button 
            icon="pi pi-refresh" 
            label="Refresh" 
            onClick={loadMonitoringData}
            loading={loading}
          />
        </div>
      </div>

      <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
        <TabPanel header="⚡ Performance">
          {renderPerformanceTab()}
        </TabPanel>

        <TabPanel header="💥 Crashes">
          {renderCrashesTab()}
        </TabPanel>

        <TabPanel header="💬 Feedback">
          {renderFeedbackTab()}
        </TabPanel>

        <TabPanel header="🔄 Updates">
          {renderUpdatesTab()}
        </TabPanel>
      </TabView>
    </div>
  );
};
