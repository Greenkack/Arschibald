/**
 * Combined Results Component (Modern - shadcn/ui)
 * 
 * Displays results for combined solar + heat pump system
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Sun, Flame, TrendingUp } from 'lucide-react';

interface CombinedResultsProps {
  results: {
    totalInvestment: number;
    annualSavings: number;
    paybackPeriod: number;
    roi: number;
    co2Reduction: number;
    solarContribution: number;
    heatPumpContribution: number;
  };
}

export const CombinedResults: React.FC<CombinedResultsProps> = ({ results }) => {
  const formatCurrency = (value: number) => {
    return `${value.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Gesamtergebnis
          </CardTitle>
          <CardDescription>
            Kombinierte Analyse für PV-Anlage und Wärmepumpe
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Gesamtinvestition</span>
                <span className="font-semibold">{formatCurrency(results.totalInvestment)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Jährliche Einsparung</span>
                <span className="font-semibold text-green-600">{formatCurrency(results.annualSavings)}</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Amortisationszeit</span>
                <Badge variant="secondary">{results.paybackPeriod} Jahre</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">ROI (25 Jahre)</span>
                <Badge variant="default">{results.roi}%</Badge>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Sun className="h-4 w-4" />
              Beitrag PV-Anlage
            </h4>
            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {results.solarContribution}%
              </div>
              <p className="text-sm text-muted-foreground">Anteil an Gesamtersparnis</p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Flame className="h-4 w-4" />
              Beitrag Wärmepumpe
            </h4>
            <div className="bg-orange-50 dark:bg-orange-950 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {results.heatPumpContribution}%
              </div>
              <p className="text-sm text-muted-foreground">Anteil an Gesamtersparnis</p>
            </div>
          </div>

          <Separator />

          <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">CO₂-Einsparung</h4>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
              {results.co2Reduction.toLocaleString('de-DE')} kg/Jahr
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Entspricht {Math.round(results.co2Reduction / 22)} gepflanzten Bäumen
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
