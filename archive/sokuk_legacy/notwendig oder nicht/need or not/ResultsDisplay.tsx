import React, { FC } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

interface AnalysisResults {
  [key: string]: number | string | undefined;
}

interface ResultsDisplayProps {
  results: AnalysisResults;
}

/**
 * Darstellungskomponente für die Ergebnisse einer PV‑Berechnung.
 *
 * Diese Komponente erwartet ein Dictionary mit diversen Kennzahlen
 * (`AnalysisResults`) und zeigt eine Auswahl davon als Karten und Tabellen.
 * Passe den Inhalt und die Darstellung nach deinen Anforderungen an.
 */
export const ResultsDisplay: FC<ResultsDisplayProps> = ({ results }) => {
  if (!results) return null;

  // Konvertiere Ergebnis‑Key/Value‑Paare in ein Array zur Iteration
  const entries = Object.entries(results);

  // Wähle die ersten sechs KPIs für Karten aus. Passe diese Auswahl
  // entsprechend deinen Anforderungen an.
  const cardEntries = entries.slice(0, 6);

  return (
    <div className="p-grid">
      {cardEntries.map(([key, value]) => (
        <div key={key} className="p-col-12 p-md-4">
          <Card
            title={key}
            subTitle="KPI"
            className="p-mb-3"
            header={undefined}
            footer={undefined}
          >
            <p className="p-m-0">{value?.toString()}</p>
          </Card>
        </div>
      ))}

      {/* Beispiel: Tabelle für Kostenaufstellung, falls im Ergebnis vorhanden */}
      {Array.isArray(results.cost_breakdown) && (
        <div className="p-col-12">
          <h3>Kostenaufstellung</h3>
          <DataTable value={results.cost_breakdown} responsiveLayout="scroll">
            {Object.keys(results.cost_breakdown[0] || {}).map((col) => (
              <Column key={col} field={col} header={col} />
            ))}
          </DataTable>
        </div>
      )}
    </div>
  );
};