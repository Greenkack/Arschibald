/**
 * Modern Combined Solar + Heat Pump System Page with shadcn/ui
 * 
 * Integrated calculation interface for combined PV and heat pump systems
 * with synergy analysis and optimization
 */

import React, { useState } from 'react';
import { Sun, Flame, FileText, Repeat, SlidersHorizontal } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CombinedCalculationForm } from '../components/combined/CombinedCalculationForm';
import { CombinedResults } from '../components/combined/CombinedResultsModern';
import { SynergyAnalysis } from '../components/combined/SynergyAnalysisModern';
import { ComparisonView } from '../components/combined/ComparisonViewModern';

interface CombinedResultsData {
  totalInvestment: number;
  annualSavings: number;
  paybackPeriod: number;
  roi: number;
  co2Reduction: number;
  solarContribution: number;
  heatPumpContribution: number;
}

export const CombinedSystemModern: React.FC = () => {
  const [activeTab, setActiveTab] = useState('input');
  const [loading, setLoading] = useState(false);
  const [combinedResults, setCombinedResults] = useState<CombinedResultsData | null>(null);
  const [solarOnlyResults, setSolarOnlyResults] = useState<Record<string, unknown> | null>(null);
  const [heatPumpOnlyResults, setHeatPumpOnlyResults] = useState<Record<string, unknown> | null>(null);

  const handleCalculate = async (formData: Record<string, unknown>) => {
    setLoading(true);
    
    try {
      const results = await simulateCombinedCalculation(formData);
      
      setCombinedResults(results.combined);
      setSolarOnlyResults(results.solarOnly);
      setHeatPumpOnlyResults(results.heatPumpOnly);
      
      setActiveTab('results');
      
      toast.success('Berechnung erfolgreich', {
        description: 'Die kombinierte Systemanalyse wurde erfolgreich durchgeführt',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Die Berechnung ist fehlgeschlagen';
      console.error('Calculation error:', error);
      toast.error('Berechnungsfehler', {
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const simulateCombinedCalculation = async (_formData: Record<string, unknown>) => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      combined: {
        totalInvestment: 28500,
        annualSavings: 2850,
        paybackPeriod: 10.0,
        roi: 250,
        co2Reduction: 8500,
        solarContribution: 60,
        heatPumpContribution: 40
      } as CombinedResultsData,
      solarOnly: {
        systemSize: 10.5,
        annualProduction: 10500,
        annualSavings: 1890,
        paybackPeriod: 11.5
      },
      heatPumpOnly: {
        heatLoad: 8.5,
        annualSavings: 1420,
        paybackPeriod: 9.5
      }
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-red-600 shadow-lg">
              <div className="relative">
                <Sun className="h-5 w-5 text-white absolute -top-1 -left-1" />
                <Flame className="h-5 w-5 text-white absolute top-1 left-1" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Kombiniertes PV + Wärmepumpen-System</h1>
              <p className="text-muted-foreground">
                Optimale Systemauslegung mit Synergieanalyse
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="input" className="gap-2">
                  <FileText className="h-4 w-4" />
                  Eingabe
                </TabsTrigger>
                <TabsTrigger value="results" disabled={!combinedResults} className="gap-2">
                  <Sun className="h-4 w-4" />
                  Ergebnisse
                </TabsTrigger>
                <TabsTrigger value="synergy" disabled={!combinedResults} className="gap-2">
                  <Repeat className="h-4 w-4" />
                  Synergieanalyse
                </TabsTrigger>
                <TabsTrigger value="comparison" disabled={!combinedResults} className="gap-2">
                  <SlidersHorizontal className="h-4 w-4" />
                  Vergleich
                </TabsTrigger>
              </TabsList>

              <TabsContent value="input" className="space-y-4">
                <CombinedCalculationForm
                  onSubmit={handleCalculate}
                  loading={loading}
                />
              </TabsContent>

              <TabsContent value="results" className="space-y-4">
                {combinedResults ? (
                  <CombinedResults results={combinedResults} />
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <Sun className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Berechnung durchführen</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte führen Sie zuerst die Berechnung durch.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="synergy" className="space-y-4">
                {combinedResults ? (
                  <SynergyAnalysis 
                    solarData={solarOnlyResults}
                    heatPumpData={heatPumpOnlyResults}
                  />
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <Repeat className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Synergieanalyse</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte führen Sie zuerst die Berechnung durch.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="comparison" className="space-y-4">
                {combinedResults && solarOnlyResults && heatPumpOnlyResults ? (
                  <ComparisonView
                    combined={combinedResults}
                    solarOnly={solarOnlyResults}
                    heatPumpOnly={heatPumpOnlyResults}
                  />
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <SlidersHorizontal className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Vergleichsansicht</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte führen Sie zuerst die Berechnung durch.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
