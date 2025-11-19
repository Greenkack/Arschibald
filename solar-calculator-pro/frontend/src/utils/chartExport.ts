/**
 * Chart Export Utilities
 * 
 * Utilities for exporting charts to various formats (PNG, SVG, PDF)
 * 
 * Requirements: 7.4
 */

import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

export interface ExportOptions {
  filename?: string;
  format?: 'png' | 'svg' | 'pdf';
  quality?: number;
  backgroundColor?: string;
}

/**
 * Export chart as PNG image
 */
export const exportChartAsPNG = async (
  chartElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const {
    filename = 'chart',
    quality = 1.0,
    backgroundColor = '#ffffff',
  } = options;

  try {
    const canvas = await html2canvas(chartElement, {
      backgroundColor,
      scale: 2, // Higher resolution
    });

    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = canvas.toDataURL('image/png', quality);
    link.click();
  } catch (error) {
    console.error('Error exporting chart as PNG:', error);
    throw new Error('Failed to export chart as PNG');
  }
};

/**
 * Export chart as SVG
 */
export const exportChartAsSVG = async (
  chartElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const { filename = 'chart' } = options;

  try {
    // Find SVG element within the chart
    const svgElement = chartElement.querySelector('svg');
    if (!svgElement) {
      throw new Error('No SVG element found in chart');
    }

    // Clone the SVG to avoid modifying the original
    const clonedSvg = svgElement.cloneNode(true) as SVGElement;
    
    // Add XML namespace if not present
    if (!clonedSvg.getAttribute('xmlns')) {
      clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    }

    // Serialize SVG to string
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(clonedSvg);

    // Create blob and download
    const blob = new Blob([svgString], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.download = `${filename}.svg`;
    link.href = url;
    link.click();
    
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting chart as SVG:', error);
    throw new Error('Failed to export chart as SVG');
  }
};

/**
 * Export chart as PDF
 */
export const exportChartAsPDF = async (
  chartElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const {
    filename = 'chart',
    backgroundColor = '#ffffff',
  } = options;

  try {
    const canvas = await html2canvas(chartElement, {
      backgroundColor,
      scale: 2,
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
      unit: 'px',
      format: [canvas.width, canvas.height],
    });

    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error exporting chart as PDF:', error);
    throw new Error('Failed to export chart as PDF');
  }
};

/**
 * Export chart in specified format
 */
export const exportChart = async (
  chartElement: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const { format = 'png' } = options;

  switch (format) {
    case 'png':
      return exportChartAsPNG(chartElement, options);
    case 'svg':
      return exportChartAsSVG(chartElement, options);
    case 'pdf':
      return exportChartAsPDF(chartElement, options);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
};

/**
 * Export chart data as CSV
 */
export const exportChartDataAsCSV = (
  data: any[],
  filename: string = 'chart-data'
): void => {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }

  // Get headers from first data object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Escape values containing commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    ),
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.download = `${filename}.csv`;
  link.href = url;
  link.click();
  
  URL.revokeObjectURL(url);
};

/**
 * Export chart data as JSON
 */
export const exportChartDataAsJSON = (
  data: any[],
  filename: string = 'chart-data'
): void => {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }

  const jsonContent = JSON.stringify(data, null, 2);
  
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.download = `${filename}.json`;
  link.href = url;
  link.click();
  
  URL.revokeObjectURL(url);
};
