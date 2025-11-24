/**
 * Comparison View Component
 * 
 * Displays side-by-side comparison of multiple calculations.
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Chart } from 'primereact/chart';
import { MultiSelect } from 'primereact/multiselect';
import './ComparisonView.css';

interface ComparisonItem {
  id: number;
  name: string;
  type: string;
  metrics: Array<{
    name: string;
    value: number;
    unit: string;
    formatted_value: string;
    category: string;
  }>;
  created_at: string;
}

interface ComparisonViewProps {
  comparisonId?: string;
  calculationIds?: number[];
  onExport?: (format: string) => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  comparisonId,
  calculationIds,
  onExport
}) => {
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [chartType, setChartType] = useState('bar');

  const availableMetrics = [
    { label: 'Total Cost', value: 'total_cost' },
    { label: 'Annual Savings', value: 'annual_savings' },
    { label: 'Payback Period', value: 'payback_period' },
    { label: 'System Size', value: 'system_size' },
    { label: 'ROI', value: 'roi' },
    { label: 'CO2 Savings', value: 'co2_savings' }
  ];

  useEffect(() => {
    if (comparisonId) {
      loadComparison(comparisonId);
    } else if (calculationIds && calculationIds.length > 0) {
      createComparison(calculationIds);
    }
  }, [comparisonId, calculationIds]);

  const loadComparison = async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/results-visualization/comparisons/${id}`);
      const data = await response.json();
      setComparison(data);
      setSelectedMetrics(data.metrics_to_compare || []);
    } catch (error) {
      console.error('Error loading comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  const createComparison = async (ids: number[]) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/results-visualization/comparisons', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Calculation Comparison',
          calculation_ids: ids,
          metrics_to_compare: ['total_cost', 'annual_savings', 'payback_period'],
          chart_type: 'bar'
        })
      });
      const data = await response.json();
      setComparison(data);
      setSelectedMetrics(data.metrics_to_compare || []);
    } catch (error) {
      console.error('Error creating comparison:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = () => {
    if (!comparison || !comparison.items) return null;

    const labels = comparison.items.map((item: ComparisonItem) => item.name);
    const datasets = selectedMetrics.map((metric, index) => {
      const metricLabel = availableMetrics.find(m => m.value === metric)?.label || metric;
      const data = comparison.items.map((item: ComparisonItem) => {
        const metricData = item.metrics.find(m => m.name.toLowerCase().replace(' ', '_') === metric);
        return metricData ? metricData.value : 0;
      });

      const colors = [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ];

      return {
        label: metricLabel,
        data: data,
        backgroundColor: colors[index % colors.length],
        borderColor: colors[index % colors.length].replace('0.8', '1'),
        borderWidth: 2
      };
    });

    return {
      labels,
      datasets
    };
  };

  const getChartOptions = () => {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Calculation Comparison'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    };
  };

  const getTableData = () => {
    if (!comparison || !comparison.items) return [];

    return comparison.items.map((item: ComparisonItem) => {
      const row: any = {
        name: item.name,
        type: item.type,
        created_at: new Date(item.created_at).toLocaleDateString()
      };

      item.metrics.forEach(metric => {
        row[metric.name] = metric.formatted_value;
      });

      return row;
    });
  };

  const handleExport = (format: string) => {
    if (onExport) {
      onExport(format);
    }
  };

  if (loading) {
    return <div className="comparison-loading">Loading comparison...</div>;
  }

  if (!comparison) {
    return <div className="comparison-empty">No comparison data available</div>;
  }

  const chartData = getChartData();
  const tableData = getTableData();

  return (
    <div className="comparison-view">
      <div className="comparison-header">
        <div className="comparison-title">
          <h2>{comparison.name}</h2>
          {comparison.description && (
            <p className="comparison-description">{comparison.description}</p>
          )}
        </div>

        <div className="comparison-actions">
          <MultiSelect
            value={selectedMetrics}
            options={availableMetrics}
            onChange={(e) => setSelectedMetrics(e.value)}
            placeholder="Select Metrics"
            display="chip"
            className="metrics-selector"
          />

          <Button
            label="Export"
            icon="pi pi-download"
            onClick={() => handleExport('pdf')}
            className="p-button-sm"
          />
        </div>
      </div>

      <div className="comparison-content">
        <Card title="Visual Comparison" className="comparison-chart-card">
          {chartData && (
            <Chart
              type={chartType as any}
              data={chartData}
              options={getChartOptions()}
              style={{ height: '400px' }}
            />
          )}
        </Card>

        <Card title="Detailed Comparison" className="comparison-table-card">
          <DataTable
            value={tableData}
            responsiveLayout="scroll"
            stripedRows
            showGridlines
          >
            <Column field="name" header="Name" sortable />
            <Column field="type" header="Type" sortable />
            {comparison.items[0]?.metrics.map((metric: any) => (
              <Column
                key={metric.name}
                field={metric.name}
                header={metric.name}
                sortable
              />
            ))}
            <Column field="created_at" header="Created" sortable />
          </DataTable>
        </Card>

        <Card title="Summary Statistics" className="comparison-stats-card">
          <div className="stats-grid">
            {selectedMetrics.map(metric => {
              const metricLabel = availableMetrics.find(m => m.value === metric)?.label || metric;
              const values = comparison.items.map((item: ComparisonItem) => {
                const metricData = item.metrics.find(m => 
                  m.name.toLowerCase().replace(' ', '_') === metric
                );
                return metricData ? metricData.value : 0;
              });

              const avg = values.reduce((a, b) => a + b, 0) / values.length;
              const min = Math.min(...values);
              const max = Math.max(...values);

              return (
                <div key={metric} className="stat-item">
                  <h4>{metricLabel}</h4>
                  <div className="stat-values">
                    <div className="stat-value">
                      <span className="stat-label">Average:</span>
                      <span className="stat-number">{avg.toFixed(2)}</span>
                    </div>
                    <div className="stat-value">
                      <span className="stat-label">Min:</span>
                      <span className="stat-number">{min.toFixed(2)}</span>
                    </div>
                    <div className="stat-value">
                      <span className="stat-label">Max:</span>
                      <span className="stat-number">{max.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
};
