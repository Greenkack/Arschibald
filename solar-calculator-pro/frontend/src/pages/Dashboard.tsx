/**
 * Dashboard Page
 * 
 * Main dashboard showing overview and statistics
 * Requirements: 2.3
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Timeline } from 'primereact/timeline';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

interface StatCard {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

interface Project {
  id: number;
  name: string;
  customerName: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;
  totalValue?: number;
}

interface Activity {
  id: number;
  type: 'project_created' | 'project_completed' | 'calculation' | 'pdf_generated' | 'customer_added';
  description: string;
  timestamp: string;
  icon: string;
  color: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatCard[]>([]);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load statistics
      const statsData: StatCard[] = [
        {
          title: 'Total Projects',
          value: 42,
          icon: 'pi pi-briefcase',
          color: '#3B82F6',
          trend: { value: 12, isPositive: true }
        },
        {
          title: 'Active Projects',
          value: 15,
          icon: 'pi pi-chart-line',
          color: '#10B981',
          trend: { value: 5, isPositive: true }
        },
        {
          title: 'Total Revenue',
          value: '€245,000',
          icon: 'pi pi-euro',
          color: '#F59E0B',
          trend: { value: 8, isPositive: true }
        },
        {
          title: 'Completed This Month',
          value: 8,
          icon: 'pi pi-check-circle',
          color: '#8B5CF6',
          trend: { value: 2, isPositive: false }
        }
      ];
      setStats(statsData);

      // Load recent projects
      const projectsData: Project[] = [
        {
          id: 1,
          name: 'Solar Installation - Müller',
          customerName: 'Hans Müller',
          projectType: 'solar',
          status: 'active',
          createdAt: '2024-01-15',
          totalValue: 25000
        },
        {
          id: 2,
          name: 'Heat Pump System - Schmidt',
          customerName: 'Anna Schmidt',
          projectType: 'heatpump',
          status: 'active',
          createdAt: '2024-01-14',
          totalValue: 18000
        },
        {
          id: 3,
          name: 'Combined System - Weber',
          customerName: 'Klaus Weber',
          projectType: 'combined',
          status: 'completed',
          createdAt: '2024-01-12',
          totalValue: 45000
        },
        {
          id: 4,
          name: 'Solar Installation - Fischer',
          customerName: 'Maria Fischer',
          projectType: 'solar',
          status: 'draft',
          createdAt: '2024-01-10',
          totalValue: 22000
        },
        {
          id: 5,
          name: 'Heat Pump - Becker',
          customerName: 'Thomas Becker',
          projectType: 'heatpump',
          status: 'active',
          createdAt: '2024-01-08',
          totalValue: 16000
        }
      ];
      setRecentProjects(projectsData);

      // Load activity timeline
      const activitiesData: Activity[] = [
        {
          id: 1,
          type: 'project_created',
          description: 'New project created: Solar Installation - Müller',
          timestamp: '2024-01-15T10:30:00',
          icon: 'pi pi-plus-circle',
          color: '#3B82F6'
        },
        {
          id: 2,
          type: 'pdf_generated',
          description: 'PDF generated for project: Heat Pump System - Schmidt',
          timestamp: '2024-01-15T09:15:00',
          icon: 'pi pi-file-pdf',
          color: '#EF4444'
        },
        {
          id: 3,
          type: 'project_completed',
          description: 'Project completed: Combined System - Weber',
          timestamp: '2024-01-14T16:45:00',
          icon: 'pi pi-check-circle',
          color: '#10B981'
        },
        {
          id: 4,
          type: 'calculation',
          description: 'Solar calculation performed for new customer',
          timestamp: '2024-01-14T14:20:00',
          icon: 'pi pi-calculator',
          color: '#F59E0B'
        },
        {
          id: 5,
          type: 'customer_added',
          description: 'New customer added: Maria Fischer',
          timestamp: '2024-01-13T11:00:00',
          icon: 'pi pi-user-plus',
          color: '#8B5CF6'
        }
      ];
      setActivities(activitiesData);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      label: 'New Solar Project',
      icon: 'pi pi-sun',
      command: () => navigate('/solar-calculator'),
      className: 'p-button-primary'
    },
    {
      label: 'New Heat Pump',
      icon: 'pi pi-bolt',
      command: () => navigate('/heat-pump'),
      className: 'p-button-success'
    },
    {
      label: 'Price Matrix',
      icon: 'pi pi-table',
      command: () => navigate('/price-matrix'),
      className: 'p-button-warning'
    },
    {
      label: 'Generate PDF',
      icon: 'pi pi-file-pdf',
      command: () => navigate('/solar-calculator'),
      className: 'p-button-danger'
    }
  ];

  const renderStatCard = (stat: StatCard) => (
    <Card key={stat.title} className="stat-card">
      <div className="stat-card-content">
        <div className="stat-icon" style={{ backgroundColor: stat.color }}>
          <i className={stat.icon}></i>
        </div>
        <div className="stat-details">
          <div className="stat-title">{stat.title}</div>
          <div className="stat-value">{stat.value}</div>
          {stat.trend && (
            <div className={`stat-trend ${stat.trend.isPositive ? 'positive' : 'negative'}`}>
              <i className={`pi ${stat.trend.isPositive ? 'pi-arrow-up' : 'pi-arrow-down'}`}></i>
              <span>{stat.trend.value}% vs last month</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );

  const projectTypeTemplate = (rowData: Project) => {
    const typeConfig = {
      solar: { label: 'Solar', icon: 'pi pi-sun', color: '#F59E0B' },
      heatpump: { label: 'Heat Pump', icon: 'pi pi-bolt', color: '#EF4444' },
      combined: { label: 'Combined', icon: 'pi pi-star', color: '#8B5CF6' }
    };
    const config = typeConfig[rowData.projectType];
    
    return (
      <div className="project-type">
        <i className={config.icon} style={{ color: config.color, marginRight: '0.5rem' }}></i>
        <span>{config.label}</span>
      </div>
    );
  };

  const statusTemplate = (rowData: Project) => {
    const statusConfig = {
      draft: { label: 'Draft', severity: 'secondary' },
      active: { label: 'Active', severity: 'info' },
      completed: { label: 'Completed', severity: 'success' },
      archived: { label: 'Archived', severity: 'warning' }
    };
    const config = statusConfig[rowData.status];
    
    return (
      <span className={`status-badge status-${config.severity}`}>
        {config.label}
      </span>
    );
  };

  const valueTemplate = (rowData: Project) => {
    if (!rowData.totalValue) return '-';
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(rowData.totalValue);
  };

  const dateTemplate = (rowData: Project) => {
    return new Date(rowData.createdAt).toLocaleDateString('de-DE');
  };

  const actionsTemplate = (rowData: Project) => (
    <div className="project-actions">
      <Button
        icon="pi pi-eye"
        className="p-button-rounded p-button-text p-button-sm"
        tooltip="View"
        onClick={() => navigate(`/projects/${rowData.id}`)}
      />
      <Button
        icon="pi pi-pencil"
        className="p-button-rounded p-button-text p-button-sm"
        tooltip="Edit"
        onClick={() => navigate(`/projects/${rowData.id}/edit`)}
      />
    </div>
  );

  const customizedMarker = (item: Activity) => (
    <span
      className="activity-marker"
      style={{ backgroundColor: item.color }}
    >
      <i className={item.icon}></i>
    </span>
  );

  const customizedContent = (item: Activity) => (
    <div className="activity-content">
      <div className="activity-description">{item.description}</div>
      <div className="activity-timestamp">
        {new Date(item.timestamp).toLocaleString('de-DE')}
      </div>
    </div>
  );

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="quick-actions">
          {quickActions.map((action, index) => (
            <Button
              key={index}
              label={action.label}
              icon={action.icon}
              className={action.className}
              onClick={action.command}
            />
          ))}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        {stats.map(stat => renderStatCard(stat))}
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content">
        {/* Recent Projects */}
        <Card title="Recent Projects" className="recent-projects-card">
          <DataTable
            value={recentProjects}
            loading={loading}
            paginator
            rows={5}
            emptyMessage="No projects found"
            className="recent-projects-table"
          >
            <Column field="name" header="Project Name" sortable />
            <Column field="customerName" header="Customer" sortable />
            <Column
              field="projectType"
              header="Type"
              body={projectTypeTemplate}
              sortable
            />
            <Column
              field="status"
              header="Status"
              body={statusTemplate}
              sortable
            />
            <Column
              field="totalValue"
              header="Value"
              body={valueTemplate}
              sortable
            />
            <Column
              field="createdAt"
              header="Created"
              body={dateTemplate}
              sortable
            />
            <Column
              body={actionsTemplate}
              exportable={false}
              style={{ width: '8rem' }}
            />
          </DataTable>
        </Card>

        {/* Activity Timeline */}
        <Card title="Recent Activity" className="activity-card">
          <Timeline
            value={activities}
            align="left"
            className="activity-timeline"
            marker={customizedMarker}
            content={customizedContent}
          />
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
