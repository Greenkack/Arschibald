/**
 * Modern Dashboard with shadcn/ui
 * Complete redesign with modern components
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  TrendingDown, 
  Briefcase, 
  Activity, 
  Euro, 
  CheckCircle,
  ArrowRight,
  Calendar,
  Users,
  FileText
} from 'lucide-react';

interface StatCard {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: string;
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

const DashboardModern: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatCard[]>([]);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const statsData: StatCard[] = [
        {
          title: 'Total Projects',
          value: 42,
          icon: <Briefcase className="h-4 w-4" />,
          color: 'text-blue-600',
          trend: { value: 12, isPositive: true }
        },
        {
          title: 'Active Projects',
          value: 15,
          icon: <Activity className="h-4 w-4" />,
          color: 'text-green-600',
          trend: { value: 5, isPositive: true }
        },
        {
          title: 'Total Revenue',
          value: '€245,000',
          icon: <Euro className="h-4 w-4" />,
          color: 'text-yellow-600',
          trend: { value: 8, isPositive: true }
        },
        {
          title: 'Completed This Month',
          value: 8,
          icon: <CheckCircle className="h-4 w-4" />,
          color: 'text-purple-600',
          trend: { value: 2, isPositive: false }
        }
      ];
      setStats(statsData);

      const projectsData: Project[] = [
        {
          id: 1,
          name: 'Solar Installation - Müller',
          customerName: 'Hans Müller',
          projectType: 'solar',
          status: 'active',
          createdAt: new Date().toISOString(),
          totalValue: 25000
        },
        {
          id: 2,
          name: 'Wärmepumpe - Schmidt',
          customerName: 'Maria Schmidt',
          projectType: 'heatpump',
          status: 'draft',
          createdAt: new Date(Date.now() - 86400000).toISOString(),
          totalValue: 18000
        },
        {
          id: 3,
          name: 'Combined System - Weber',
          customerName: 'Thomas Weber',
          projectType: 'combined',
          status: 'completed',
          createdAt: new Date(Date.now() - 172800000).toISOString(),
          totalValue: 45000
        }
      ];
      setRecentProjects(projectsData);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
      active: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      archived: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status as keyof typeof statusColors]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getProjectTypeIcon = (type: string) => {
    switch (type) {
      case 'solar':
        return '☀️';
      case 'heatpump':
        return '🔥';
      case 'combined':
        return '⚡';
      default:
        return '📋';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's what's happening with your projects.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/project-wizard')}>
            <Calendar className="mr-2 h-4 w-4" />
            Schedule
          </Button>
          <Button onClick={() => navigate('/solar-calculator')}>
            <FileText className="mr-2 h-4 w-4" />
            New Project
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className={stat.color}>
                {stat.icon}
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              {stat.trend && (
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  {stat.trend.isPositive ? (
                    <TrendingUp className="mr-1 h-3 w-3 text-green-600" />
                  ) : (
                    <TrendingDown className="mr-1 h-3 w-3 text-red-600" />
                  )}
                  <span className={stat.trend.isPositive ? 'text-green-600' : 'text-red-600'}>
                    {stat.trend.value}%
                  </span>
                  <span className="ml-1">from last month</span>
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Projects */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Projects</CardTitle>
              <CardDescription>Your latest project activity</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => navigate('/crm')}>
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentProjects.map((project) => (
              <div 
                key={project.id} 
                className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/solar-project-details/${project.id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className="text-3xl">{getProjectTypeIcon(project.projectType)}</div>
                  <div>
                    <div className="font-medium">{project.name}</div>
                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                      <Users className="h-3 w-3" />
                      {project.customerName}
                      <span>•</span>
                      <Calendar className="h-3 w-3" />
                      {new Date(project.createdAt).toLocaleDateString('de-DE')}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {project.totalValue && (
                    <div className="text-right">
                      <div className="font-semibold">
                        {new Intl.NumberFormat('de-DE', { 
                          style: 'currency', 
                          currency: 'EUR' 
                        }).format(project.totalValue)}
                      </div>
                    </div>
                  )}
                  {getStatusBadge(project.status)}
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/solar-calculator')}>
          <CardHeader>
            <CardTitle className="flex items-center">
              ☀️ Solar Calculator
            </CardTitle>
            <CardDescription>
              Calculate solar panel installations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="ghost" className="w-full justify-between">
              Start Calculation
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/heatpump')}>
          <CardHeader>
            <CardTitle className="flex items-center">
              🔥 Heat Pump
            </CardTitle>
            <CardDescription>
              Configure heat pump systems
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="ghost" className="w-full justify-between">
              Start Configuration
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/combined-system')}>
          <CardHeader>
            <CardTitle className="flex items-center">
              ⚡ Combined System
            </CardTitle>
            <CardDescription>
              Complete energy solution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="ghost" className="w-full justify-between">
              Design System
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardModern;
