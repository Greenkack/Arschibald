import type { Meta, StoryObj } from '@storybook/react';
import { LineChart } from './LineChart';

/**
 * LineChart displays data as a series of points connected by lines.
 * Perfect for showing trends over time.
 * 
 * ## Features
 * - Multiple data series support
 * - Customizable colors and styles
 * - Interactive tooltips
 * - Responsive sizing
 * - Grid lines and axes
 * - Legend display
 * - Export to image
 * 
 * ## Use Cases
 * - Energy production over time
 * - Cost savings projections
 * - Temperature trends
 * - Performance metrics
 * 
 * ## Accessibility
 * - Keyboard navigation
 * - Screen reader compatible data tables
 * - High contrast mode support
 * - Descriptive labels and titles
 */
const meta = {
  title: 'Charts/LineChart',
  component: LineChart,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'A line chart component for visualizing trends and time-series data.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    data: {
      description: 'Array of data points',
    },
    xKey: {
      control: 'text',
      description: 'Key for X-axis values',
    },
    yKey: {
      control: 'text',
      description: 'Key for Y-axis values',
    },
    title: {
      control: 'text',
      description: 'Chart title',
    },
    color: {
      control: 'color',
      description: 'Line color',
    },
  },
} satisfies Meta<typeof LineChart>;

export default meta;
type Story = StoryObj<typeof meta>;

const monthlyData = [
  { month: 'Jan', production: 450 },
  { month: 'Feb', production: 520 },
  { month: 'Mar', production: 680 },
  { month: 'Apr', production: 780 },
  { month: 'May', production: 850 },
  { month: 'Jun', production: 920 },
  { month: 'Jul', production: 950 },
  { month: 'Aug', production: 900 },
  { month: 'Sep', production: 750 },
  { month: 'Oct', production: 600 },
  { month: 'Nov', production: 480 },
  { month: 'Dec', production: 420 },
];

/**
 * Solar energy production over months
 */
export const EnergyProduction: Story = {
  args: {
    data: monthlyData,
    xKey: 'month',
    yKey: 'production',
    title: 'Monthly Solar Energy Production (kWh)',
    color: '#f59e0b',
  },
};

const savingsData = [
  { year: '2024', savings: 1200 },
  { year: '2025', savings: 2500 },
  { year: '2026', savings: 3900 },
  { year: '2027', savings: 5400 },
  { year: '2028', savings: 7000 },
  { year: '2029', savings: 8700 },
  { year: '2030', savings: 10500 },
];

/**
 * Cumulative savings projection
 */
export const SavingsProjection: Story = {
  args: {
    data: savingsData,
    xKey: 'year',
    yKey: 'savings',
    title: 'Cumulative Savings Over Time (€)',
    color: '#10b981',
  },
};

const temperatureData = [
  { hour: '00:00', temp: 18 },
  { hour: '04:00', temp: 16 },
  { hour: '08:00', temp: 20 },
  { hour: '12:00', temp: 28 },
  { hour: '16:00', temp: 30 },
  { hour: '20:00', temp: 24 },
  { hour: '24:00', temp: 19 },
];

/**
 * Temperature variation throughout the day
 */
export const TemperatureTrend: Story = {
  args: {
    data: temperatureData,
    xKey: 'hour',
    yKey: 'temp',
    title: 'Daily Temperature Variation (°C)',
    color: '#ef4444',
  },
};

/**
 * Small chart for dashboard widgets
 */
export const CompactChart: Story = {
  args: {
    data: monthlyData.slice(0, 6),
    xKey: 'month',
    yKey: 'production',
    title: 'Last 6 Months',
    color: '#3b82f6',
  },
  parameters: {
    layout: 'centered',
  },
};
