import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminDashboard.css';

interface SystemHealth {
  status: string;
  cpu: {
    usage_percent: number;
    count: number;
    status: string;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
    status: string;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    usage_percent: number;
    status: string;
  };
  issues: string[];
  uptime_seconds: number;
}

interface UsageStatistics {
  period: string;
  users: {
    total_users: number;
    active_users: number;
    new_users: number;
  };
  projects: {
    total_projects: number;
    new_projects: number;
    completed_projects: number;
  };
  calculations: {
    total_calculations: number;
  };
  pdfs: {
    total_pdfs: number;
  };
}

interface PerformanceMetrics {
  response_times: {
    average_ms: number;
    p95_ms: number;
  };
  throughput: {
    requests_per_second: number;
  };
  error_rates: {
    error_rate_percent: number;
  };
}

interface Alert {
  id: number;
  severity: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

const AdminDashboard: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStatistics | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('today');
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  const [autoRefresh, setAutoRefresh] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchDashboardData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [selectedPeriod, autoRefresh, refreshInterval]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all dashboard data in parallel
      const [healthRes, statsRes, metricsRes, alertsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/admin/dashboard/health/system`),
        axios.get(`${API_BASE_URL}/admin/dashboard/statistics/usage?period=${selectedPeriod}`),
        axios.get(`${API_BASE_URL}/admin/dashboard/metrics/performance`),
        axios.get(`${API_BASE_URL}/admin/dashboard/alerts`)
      ]);

      setSystemHealth(healthRes.data);
      setUsageStats(statsRes.data);
      setPerformanceMetrics(metricsRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId: number) => {
    try {
      await axios.post(`${API_BASE_URL}/admin/dashboard/alerts/${alertId}/resolve`);
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'status-healthy';
      case 'warning':
        return 'status-warning';
      case 'critical':
        return 'status-critical';
      default:
        return 'status-unknown';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'info':
        return 'severity-info';
      case 'warning':
        return 'severity-warning';
      case 'critical':
        return 'severity-critical';
      default:
        return 'severity-info';
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (loading && !systemHealth) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <div className="dashboard-controls">
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="period-selector"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
          
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          
          <button onClick={fetchDashboardData} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* System Health Section */}
      {systemHealth && (
        <section className="dashboard-section">
          <h2>System Health</h2>
          <div className="health-cards">
            <div className={`health-card ${getStatusColor(systemHealth.status)}`}>
              <h3>Overall Status</h3>
              <div className="status-badge">{systemHealth.status.toUpperCase()}</div>
              <p>Uptime: {formatUptime(systemHealth.uptime_seconds)}</p>
            </div>

            <div className={`health-card ${getStatusColor(systemHealth.cpu.status)}`}>
              <h3>CPU</h3>
              <div className="metric-value">{systemHealth.cpu.usage_percent.toFixed(1)}%</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${systemHealth.cpu.usage_percent}%` }}
                />
              </div>
              <p>{systemHealth.cpu.count} cores</p>
            </div>

            <div className={`health-card ${getStatusColor(systemHealth.memory.status)}`}>
              <h3>Memory</h3>
              <div className="metric-value">{systemHealth.memory.usage_percent.toFixed(1)}%</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${systemHealth.memory.usage_percent}%` }}
                />
              </div>
              <p>{systemHealth.memory.used_gb.toFixed(1)} / {systemHealth.memory.total_gb.toFixed(1)} GB</p>
            </div>

            <div className={`health-card ${getStatusColor(systemHealth.disk.status)}`}>
              <h3>Disk</h3>
              <div className="metric-value">{systemHealth.disk.usage_percent.toFixed(1)}%</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${systemHealth.disk.usage_percent}%` }}
                />
              </div>
              <p>{systemHealth.disk.free_gb.toFixed(1)} GB free</p>
            </div>
          </div>

          {systemHealth.issues.length > 0 && (
            <div className="health-issues">
              <h4>⚠️ Issues Detected:</h4>
              <ul>
                {systemHealth.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* Usage Statistics Section */}
      {usageStats && (
        <section className="dashboard-section">
          <h2>Usage Statistics ({usageStats.period})</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Users</h3>
              <div className="stat-value">{usageStats.users.active_users}</div>
              <p className="stat-label">Active Users</p>
              <p className="stat-detail">
                {usageStats.users.new_users} new | {usageStats.users.total_users} total
              </p>
            </div>

            <div className="stat-card">
              <h3>Projects</h3>
              <div className="stat-value">{usageStats.projects.new_projects}</div>
              <p className="stat-label">New Projects</p>
              <p className="stat-detail">
                {usageStats.projects.completed_projects} completed | {usageStats.projects.total_projects} total
              </p>
            </div>

            <div className="stat-card">
              <h3>Calculations</h3>
              <div className="stat-value">{usageStats.calculations.total_calculations}</div>
              <p className="stat-label">Total Calculations</p>
            </div>

            <div className="stat-card">
              <h3>PDFs</h3>
              <div className="stat-value">{usageStats.pdfs.total_pdfs}</div>
              <p className="stat-label">Generated PDFs</p>
            </div>
          </div>
        </section>
      )}

      {/* Performance Metrics Section */}
      {performanceMetrics && (
        <section className="dashboard-section">
          <h2>Performance Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Response Time</h3>
              <div className="metric-value">{performanceMetrics.response_times.average_ms}ms</div>
              <p className="metric-label">Average</p>
              <p className="metric-detail">P95: {performanceMetrics.response_times.p95_ms}ms</p>
            </div>

            <div className="metric-card">
              <h3>Throughput</h3>
              <div className="metric-value">{performanceMetrics.throughput.requests_per_second}</div>
              <p className="metric-label">Requests/sec</p>
            </div>

            <div className="metric-card">
              <h3>Error Rate</h3>
              <div className="metric-value">{performanceMetrics.error_rates.error_rate_percent.toFixed(2)}%</div>
              <p className="metric-label">Error Rate</p>
            </div>
          </div>
        </section>
      )}

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <section className="dashboard-section">
          <h2>System Alerts ({alerts.length})</h2>
          <div className="alerts-list">
            {alerts.map((alert) => (
              <div key={alert.id} className={`alert-item ${getSeverityColor(alert.severity)}`}>
                <div className="alert-header">
                  <span className="alert-severity">{alert.severity.toUpperCase()}</span>
                  <span className="alert-type">{alert.type}</span>
                  <span className="alert-time">{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
                <h4>{alert.title}</h4>
                <p>{alert.message}</p>
                <button 
                  onClick={() => resolveAlert(alert.id)}
                  className="resolve-button"
                >
                  Resolve
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {alerts.length === 0 && (
        <section className="dashboard-section">
          <div className="no-alerts">
            ✅ No active alerts - System is running smoothly
          </div>
        </section>
      )}
    </div>
  );
};

export default AdminDashboard;
