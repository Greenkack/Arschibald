/**
 * Combined Solar + Heat Pump System Page
 * 
 * Integrated calculation interface for combined PV and heat pump systems
 * with synergy analysis and optimization
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import { useRef } from 'react';
import { CombinedCalculationForm } from '../components/combined/CombinedCalculationForm';
import { CombinedResults } from '../components/combined/CombinedResults';
import { SynergyAnalysis } from '../components/combined/SynergyAnalysis';
import { ComparisonView } from '../components/combined/ComparisonView';
import './CombinedSystem.css';

export const CombinedSystem: React.FC = () => {
  const toast = useRef<Toast>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [combinedResults, setCombinedResults] = useState<any>(null);
  const [solarOnlyResults, setSolarOnlyResults] = useState<any>(null);
  const [heatPumpOnlyResults, setHeatPumpOnlyResults] = useState<any>(null);

  const handleCalculate = async (formData: any) => {
    setLoading(true);
    
    try {
      // TODO: Call backend API for combined calculation
      // For now, simulate the calculation
      const results = await simulateCombinedCalculation(formData);
      
      setCombinedResults(results.combined);
      setSolarOnlyResults(results.solarOnly);
      setHeatPumpOnlyResults(results.heatPumpOnly);
      
      // Move to results tab
      setActiveIndex(1);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Berechnung erfolgreich',
        detail: 'Die kombinierte Systemanalyse wurde erfolgreich durchgeführt',
        life: 3000
      });
    } catch (error: any) {
      console.error('Calculation error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Berechnungsfehler',
        detail: error.message || 'Die Berechnung ist fehlgeschlagen',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  // Simulate combined calculation (replace with actual API call)
  const simulateCombinedCalculation = async (formData: any) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock results
    return {
      combined: {
        solar: {
          systemSize: 10.5,
          annualProduction: 10500,
          selfConsumption: 7350,
          gridFeedIn: 3150
        },
        heatPump: {
          heatLoad: 8.5,
          annualElectricityConsumption: 2550,
          scop: 4.2,
          annualHeatingDemand: 10710
        },
        synergy: {
          pvToHeatPumpConsumption: 1800,
          selfConsumptionIncrease: 17.1,
          autarkyIncrease: 12.5,
          additionalSavings: 540
        },
        economics: {
          totalInvestment: 28500,
          annualSavings: 2850,
          paybackPeriod: 10.0,
          savings25Years: 71250
        },
        environmental: {
          annualCO2Savings: 8500,
          total25YearsCO2Savings: 212500
        }
      },
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
    <div className="combined-system-page">
      <Toast ref={toast} />
      
      <div className="page-header">
        <h1>☀️🔥 Kombiniertes PV + Wärmepumpen-System</h1>
        <p>Optimale Systemauslegung mit Synergieanalyse</p>
      </div>

      <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
        <TabPanel header="📝 Eingabe" leftIcon="pi pi-pencil">
          <CombinedCalculationForm
            onSubmit={handleCalculate}
            loading={loading}
          />
        </TabPanel>

        <TabPanel 
          header="📊 Ergebnisse" 
          leftIcon="pi pi-chart-bar"
          disabled={!combinedResults}
        >
          {combinedResults ? (
            <CombinedResults results={combinedResults} />
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte führen Sie zuerst die Berechnung durch.</p>
            </div>
          )}
        </TabPanel>

        <TabPanel 
          header="🔄 Synergieanalyse" 
          leftIcon="pi pi-sync"
          disabled={!combinedResults}
        >
          {combinedResults ? (
            <SynergyAnalysis results={combinedResults} />
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte führen Sie zuerst die Berechnung durch.</p>
            </div>
          )}
        </TabPanel>

        <TabPanel 
          header="⚖️ Vergleich" 
          leftIcon="pi pi-sliders-h"
          disabled={!combinedResults}
        >
          {combinedResults && solarOnlyResults && heatPumpOnlyResults ? (
            <ComparisonView
              combinedResults={combinedResults}
              solarOnlyResults={solarOnlyResults}
              heatPumpOnlyResults={heatPumpOnlyResults}
            />
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte führen Sie zuerst die Berechnung durch.</p>
            </div>
          )}
        </TabPanel>
      </TabView>
    </div>
  );
};
