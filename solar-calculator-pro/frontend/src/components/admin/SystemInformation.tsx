/**
 * System Information Component
 * 
 * Display system information, health status, and statistics
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { TabView, TabPanel } from 'primereact/tabview';
import { Chip } from 'primereact/chip';
import api from '@services/api';

interface SystemInfo {
  app_version: string;
  app_build: string;
  app_environment: string;
  os_name: string;
  os_version: string;
  python_version: string;
  node_version: string | null;
  cpu_count: number;
  cpu_percent: number;
  memory_total_gb: number;
  memory_used_gb: number;
  memory_percent: number;
  disk_total_gb: number;
  disk_used_gb: number;
  disk_percent: number;
  database_type: string;
  database_size_mb: number;
  database_tables: number;
  database_records: number;
  uptime_seconds: number;
  requests_total: number;
  requests_per_minute: number;
  average_response_time_ms: number;
  status: string;
  health_checks: Record<string, boolean>;
  server_time: string;
  last_restart: string;
}

interface SystemHealth {
  status: string;
  checks: Record<string, { status: string; message: string }>;
  timestamp: string;
}

interface SystemStats {
  users_total: number;
  users_active: number;
  projects_total: number;
  calculations_today: number;
  calculations_total: number;
  pdfs_generated_today: number;
  pdfs_generated_total: number;
  storage_used_mb: number;
  api_calls_today: number;
  errors_today: number;
}

const SystemInformation: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSystemInfo();
  }, []);

  const loadSystemInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [infoResponse, healthResponse, statsResponse] = await Promise.all([
        api.get('/api/v1/system-settings/info'),
        api.get('/api/v1/system-settings/health'),
        api.get('/api/v1/system-settings/stats')
      ]);
      
      setSystemInfo(infoResponse.data);
      setSystemHealth(healthResponse.data);
      setSystemStats(statsResponse.data);
    } catch (error: any) {
      setError(`Failed to load system information: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadSystemInfo();
    setRefreshing(false);
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const formatBytes = (mb: number) => {
    if (mb < 1024) {
      return `${mb.toFixed(2)} MB`;
    }
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'danger';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'pi-check-circle';
      case 'degraded':
        return 'pi-exclamation-triangle';
      case 'unhealthy':
        return 'pi-times-circle';
      default:
        return 'pi-info-circle';
    }
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <ProgressSpinner />
        <p>Loading system information...</p>
      </div>
    );
  }

  if (error) {
    return <Message severity="error" text={error} />;
  }

  if (!systemInfo || !systemHealth || !systemStats) {
    return <Message severity="error" text="Failed to load system information" />;
  }

  return (
    <div className="system-information">
      <div className="system-info-header">
        <div className="system-status">
          <Chip 
            label={systemHealth.status.toUpperCase()} 
            icon={`pi ${getStatusIcon(systemHealth.status)}`}
            className={`p-chip-${getStatusColor(systemHealth.status)}`}
          />
        </div>
        <Button
          label="Refresh"
          icon="pi pi-refresh"
          onClick={handleRefresh}
          loading={refreshing}
          className="p-button-sm"
        />
      </div>

      <TabView>
        <TabPanel header="Overview" leftIcon="pi pi-info-circle">
          <div className="info-grid">
            {/* Application Info */}
            <Card title="Application" className="info-card">
              <div className="info-item">
                <span className="info-label">Version:</span>
                <span className="info-value">{systemInfo.app_version}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Build:</span>
                <span className="info-value">{systemInfo.app_build}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Environment:</span>
                <span className="info-value">{systemInfo.app_environment}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Uptime:</span>
                <span className="info-value">{formatUptime(systemInfo.uptime_seconds)}</span>
              </div>
            </Card>

            {/* System Info */}
            <Card title="System" className="info-card">
              <div className="info-item">
                <span className="info-label">OS:</span>
                <span className="info-value">{systemInfo.os_name}</span>
              </div>
              <div className="info-item">
                <span className="info-label">OS Version:</span>
                <span className="info-value">{systemInfo.os_version}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Python:</span>
                <span className="info-value">{systemInfo.python_version}</span>
              </div>
              <div className="info-item">
                <span className="info-label">CPUs:</span>
                <span className="info-value">{systemInfo.cpu_count}</span>
              </div>
            </Card>

            {/* Database Info */}
            <Card title="Database" className="info-card">
              <div className="info-item">
                <span className="info-label">Type:</span>
                <span className="info-value">{systemInfo.database_type}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Size:</span>
                <span className="info-value">{formatBytes(systemInfo.database_size_mb)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Tables:</span>
                <span className="info-value">{systemInfo.database_tables}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Records:</span>
                <span className="info-value">{systemInfo.database_records.toLocaleString()}</span>
              </div>
            </Card>

            {/* Performance Info */}
            <Card title="Performance" className="info-card">
              <div className="info-item">
                <span className="info-label">Total Requests:</span>
                <span className="info-value">{systemInfo.requests_total.toLocaleString()}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Requests/min:</span>
                <span className="info-value">{systemInfo.requests_per_minute.toFixed(2)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Avg Response:</span>
                <span className="info-value">{systemInfo.average_response_time_ms.toFixed(2)} ms</span>
              </div>
              <div className="info-item">
                <span className="info-label">Server Time:</span>
                <span className="info-value">{new Date(systemInfo.server_time).toLocaleString()}</span>
              </div>
            </Card>
          </div>
        </TabPanel>

        <TabPanel header="Resources" leftIcon="pi pi-chart-bar">
          <div className="resources-section">
            {/* CPU Usage */}
            <Card title="CPU Usage" className="resource-card">
              <ProgressBar 
                value={systemInfo.cpu_percent} 
                showValue={true}
                color={systemInfo.cpu_percent > 80 ? '#f44336' : systemInfo.cpu_percent > 60 ? '#ff9800' : '#4caf50'}
              />
              <div className="resource-info">
                <span>{systemInfo.cpu_count} cores</span>
                <span>{systemInfo.cpu_percent.toFixed(1)}% used</span>
              </div>
            </Card>

            {/* Memory Usage */}
            <Card title="Memory Usage" className="resource-card">
              <ProgressBar 
                value={systemInfo.memory_percent} 
                showValue={true}
                color={systemInfo.memory_percent > 80 ? '#f44336' : systemInfo.memory_percent > 60 ? '#ff9800' : '#4caf50'}
              />
              <div className="resource-info">
                <span>{systemInfo.memory_used_gb.toFixed(2)} GB / {systemInfo.memory_total_gb.toFixed(2)} GB</span>
                <span>{systemInfo.memory_percent.toFixed(1)}% used</span>
              </div>
            </Card>

            {/* Disk Usage */}
            <Card title="Disk Usage" className="resource-card">
              <ProgressBar 
                value={systemInfo.disk_percent} 
                showValue={true}
                color={systemInfo.disk_percent > 80 ? '#f44336' : systemInfo.disk_percent > 60 ? '#ff9800' : '#4caf50'}
              />
              <div className="resource-info">
                <span>{systemInfo.disk_used_gb.toFixed(2)} GB / {systemInfo.disk_total_gb.toFixed(2)} GB</span>
                <span>{systemInfo.disk_percent.toFixed(1)}% used</span>
              </div>
            </Card>
          </div>
        </TabPanel>

        <TabPanel header="Health" leftIcon="pi pi-heart">
          <div className="health-checks">
            {Object.entries(systemHealth.checks).map(([key, check]) => (
              <Card key={key} className="health-check-card">
                <div className="health-check-header">
                  <h4>{key.charAt(0).toUpperCase() + key.slice(1)}</h4>
                  <Chip 
                    label={check.status.toUpperCase()} 
                    icon={`pi ${getStatusIcon(check.status)}`}
                    className={`p-chip-${getStatusColor(check.status)}`}
                  />
                </div>
                <p className="health-check-message">{check.message}</p>
              </Card>
            ))}
          </div>
        </TabPanel>

        <TabPanel header="Statistics" leftIcon="pi pi-chart-line">
          <div className="stats-grid">
            <Card title="Users" className="stat-card">
              <div className="stat-value">{systemStats.users_total}</div>
              <div className="stat-label">Total Users</div>
              <div className="stat-secondary">{systemStats.users_active} active</div>
            </Card>

            <Card title="Projects" className="stat-card">
              <div className="stat-value">{systemStats.projects_total}</div>
              <div className="stat-label">Total Projects</div>
            </Card>

            <Card title="Calculations" className="stat-card">
              <div className="stat-value">{systemStats.calculations_total.toLocaleString()}</div>
              <div className="stat-label">Total Calculations</div>
              <div className="stat-secondary">{systemStats.calculations_today} today</div>
            </Card>

            <Card title="PDFs" className="stat-card">
              <div className="stat-value">{systemStats.pdfs_generated_total.toLocaleString()}</div>
              <div className="stat-label">Total PDFs</div>
              <div className="stat-secondary">{systemStats.pdfs_generated_today} today</div>
            </Card>

            <Card title="Storage" className="stat-card">
              <div className="stat-value">{formatBytes(systemStats.storage_used_mb)}</div>
              <div className="stat-label">Storage Used</div>
            </Card>

            <Card title="API Calls" className="stat-card">
              <div className="stat-value">{systemStats.api_calls_today.toLocaleString()}</div>
              <div className="stat-label">API Calls Today</div>
            </Card>

            <Card title="Errors" className="stat-card">
              <div className="stat-value" style={{ color: systemStats.errors_today > 0 ? '#f44336' : '#4caf50' }}>
                {systemStats.errors_today}
              </div>
              <div className="stat-label">Errors Today</div>
            </Card>
          </div>
        </TabPanel>
      </TabView>
    </div>
  );
};

export default SystemInformation;
