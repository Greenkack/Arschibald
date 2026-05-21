import React, { FC } from 'react';
import Plot from 'react-plotly.js';

export interface ChartData {
  data: any[];
  layout?: Partial<Plotly.Layout>;
}

interface ChartContainerProps {
  chartType: string;
  chartData: ChartData;
}

/**
 * Universelle Plotly‑Chart‑Komponente.
 *
 * Die Komponente nimmt ein ``chartType`` als Titel und ein ``chartData``‑Objekt
 * entgegen, das die Plotly ``data`` und optional ein ``layout`` enthält. Damit
 * lassen sich verschiedene Diagramme dynamisch darstellen.
 */
export const ChartContainer: FC<ChartContainerProps> = ({ chartType, chartData }) => {
  return (
    <div className="p-mb-4">
      <Plot
        data={chartData.data}
        layout={{
          title: chartType,
          ...chartData.layout,
          xaxis: { title: chartData.layout?.xaxis?.title || '', showtitle: true },
          yaxis: { title: chartData.layout?.yaxis?.title || '', showtitle: true },
        }}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};