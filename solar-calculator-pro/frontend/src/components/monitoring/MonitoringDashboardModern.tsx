/**
 * Monitoring Dashboard Component (Modern - shadcn/ui + Recharts)
 * 
 * Displays post-release monitoring data including performance, crashes, feedback, and updates.
 * Requirement: 8.1 - Performance monitoring and tracking
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { BarChart, RotateCw, Activity, AlertTriangle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import api from '../../services/api';

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

export const MonitoringDashboardModern: React.FC = () => {
  const [activeTab, setActiveTab] = useState('performance');
  const [timeRange, setTimeRange] = useState('7');
  const [performanceData, setPerformanceData] = useState<PerformanceSummary | null>(null);
  const [crashStats, setCrashStats] = useState<CrashStatistics | null>(null);
  const [feedbackSummary, setFeedbackSummary] = useState<FeedbackSummary | null>(null);
  const [updateStats, setUpdateStats] = useState<UpdateAdoptionStats | null>(null);
  const [loading, setLoading] = useState(true);

  const timeRangeOptions = [
    { label: 'Last 24 Hours', value: '1' },
    { label: 'Last 7 Days', value: '7' },
    { label: 'Last 30 Days', value: '30' },
    { label: 'Last 90 Days', value: '90' }
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
      return <Badge variant="destructive">Critical</Badge>;
    } else if (value >= thresholds.warning) {
      return <Badge variant="secondary" className="bg-yellow-500 text-white">Warning</Badge>;
    }
    return <Badge variant="default" className="bg-green-500">Healthy</Badge>;
  };

  const renderPerformanceTab = () => {
    if (!performanceData) return <div className="text-center py-8">Loading...</div>;

    const systemMetrics = performanceData.system;

    const cpuData = [
      { name: 'Used', value: systemMetrics.cpu_percent },
      { name: 'Free', value: 100 - systemMetrics.cpu_percent }
    ];

    const memoryData = [
      { name: 'Used', value: systemMetrics.memory_percent },
      { name: 'Free', value: 100 - systemMetrics.memory_percent }
    ];

    const COLORS = ['#ef4444', '#e5e5e5'];
    const COLORS_BLUE = ['#3b82f6', '#e5e5e5'];

    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* CPU Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">CPU Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie
                    data={cpuData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={50}
                    dataKey="value"
                  >
                    {cpuData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="text-center space-y-2">
              <p className="text-2xl font-bold">{systemMetrics.cpu_percent.toFixed(1)}%</p>
              {getHealthBadge(systemMetrics.cpu_percent, { warning: 70, critical: 90 })}
            </div>
          </CardContent>
        </Card>

        {/* Memory Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Memory Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie
                    data={memoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={50}
                    dataKey="value"
                  >
                    {memoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS_BLUE[index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="text-center space-y-2">
              <p className="text-2xl font-bold">{systemMetrics.memory_percent.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">
                {systemMetrics.memory_available_mb.toFixed(0)} MB available
              </p>
              {getHealthBadge(systemMetrics.memory_percent, { warning: 80, critical: 95 })}
            </div>
          </CardContent>
        </Card>

        {/* Disk Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Disk Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Progress value={systemMetrics.disk_percent} className="h-2" />
              <div className="space-y-2">
                <p className="text-2xl font-bold">{systemMetrics.disk_percent.toFixed(1)}%</p>
                <p className="text-sm text-muted-foreground">
                  {systemMetrics.disk_free_gb.toFixed(1)} GB free
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">API Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">API Calls</span>
                <span className="font-semibold">{performanceData.metrics.api_calls}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Errors</span>
                <span className="font-semibold">{performanceData.metrics.errors}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Avg Response</span>
                <span className="font-semibold">{performanceData.metrics.average_response_time_ms}ms</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderCrashesTab = () => {
    if (!crashStats) return <div className="text-center py-8">Loading...</div>;

    const crashFreeRate = crashStats.crash_free_rate;

    return (
      <div className="space-y-4">
        {/* Crash Overview */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Crashes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{crashStats.total_crashes}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Unique Errors</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{crashStats.unique_errors}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Affected Users</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{crashStats.affected_users}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Crash-Free Rate</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-3xl font-bold">{crashFreeRate.toFixed(2)}%</p>
              {getHealthBadge(100 - crashFreeRate, { warning: 5, critical: 10 })}
            </CardContent>
          </Card>
        </div>

        {/* Most Common Errors */}
        <Card>
          <CardHeader>
            <CardTitle>Most Common Errors</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Error Type</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {crashStats.most_common_errors.map((error, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{error.error_type}</TableCell>
                    <TableCell className="text-right">{error.count}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">View Details</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderFeedbackTab = () => {
    if (!feedbackSummary) return <div className="text-center py-8">Loading...</div>;

    const feedbackChartData = [
      { name: 'Bugs', value: feedbackSummary.by_type.bug, color: '#ef4444' },
      { name: 'Feature Requests', value: feedbackSummary.by_type.feature_request, color: '#3b82f6' },
      { name: 'Improvements', value: feedbackSummary.by_type.improvement, color: '#eab308' },
      { name: 'Praise', value: feedbackSummary.by_type.praise, color: '#10b981' }
    ];

    return (
      <div className="space-y-4">
        {/* Feedback Overview */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{feedbackSummary.total_feedback}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{feedbackSummary.average_rating.toFixed(1)}/5</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Sentiment</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge
                variant={
                  feedbackSummary.sentiment === 'positive' ? 'default' :
                  feedbackSummary.sentiment === 'negative' ? 'destructive' : 'secondary'
                }
                className={feedbackSummary.sentiment === 'positive' ? 'bg-green-500' : ''}
              >
                {feedbackSummary.sentiment.toUpperCase()}
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Feedback by Type */}
        <Card>
          <CardHeader>
            <CardTitle>Feedback by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={feedbackChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={100}
                  dataKey="value"
                >
                  {feedbackChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderUpdatesTab = () => {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Update Adoption</CardTitle>
          <CardDescription>Update adoption tracking will be displayed here.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button>View Version Distribution</Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart className="h-8 w-8" />
            Post-Release Monitoring
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timeRangeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={loadMonitoringData} disabled={loading} className="gap-2">
            <RotateCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance" className="gap-2">
            <Activity className="h-4 w-4" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="crashes" className="gap-2">
            <AlertTriangle className="h-4 w-4" />
            Crashes
          </TabsTrigger>
          <TabsTrigger value="feedback" className="gap-2">
            💬 Feedback
          </TabsTrigger>
          <TabsTrigger value="updates" className="gap-2">
            🔄 Updates
          </TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="mt-4">
          {renderPerformanceTab()}
        </TabsContent>

        <TabsContent value="crashes" className="mt-4">
          {renderCrashesTab()}
        </TabsContent>

        <TabsContent value="feedback" className="mt-4">
          {renderFeedbackTab()}
        </TabsContent>

        <TabsContent value="updates" className="mt-4">
          {renderUpdatesTab()}
        </TabsContent>
      </Tabs>
    </div>
  );
};
