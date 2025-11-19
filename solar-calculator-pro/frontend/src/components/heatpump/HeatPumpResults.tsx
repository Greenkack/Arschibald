import React from 'react';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { ProgressBar } from 'primereact/progressbar';
import { LineChart } from '../charts/LineChart';
import { BarChart } from '../charts/BarChart';
import { PieChart } from '../charts/PieChart';
import './HeatPumpResults.css';

interface BuildingData {
  heatedArea: number;
  buildingType: string;
  buildingYear: string;
  insulationQuality: string;
  currentHeatingSystem: string;
  hotWaterDemand: string;
  oilConsumption: number;
  gasConsumption: number;
  woodConsumption: number;
  systemEfficiency: number;
  heatingHours: number;
  gasMonthlyCost: number;
  oilPricePerTon: number;
  woodPricePerSter: number;
  desiredTemperature: number;
  heatingDays: number;
  outsideTempDesign: number;
  heatingSystemTemp: string;
  location: string;
  climateZone: string;
}

interface HeatPumpModel {
  model: string;
  manufacturer: string;
  type: string;
  heating_power_kw: number[];
  scop: number;
  max_flow_temp: number;
  price_range: string;
  features: string[];
  refrigerant: string;
  rating: number;
  awards: string[];
}

interface HeatPumpResultsProps {
  buildingData: BuildingData;
  heatLoad: number;
  selectedHeatPump: {
    model: HeatPumpModel;
    power: number;
  };
}

export const HeatPumpResults: React.FC<HeatPumpResultsProps> = ({
  buildingData,
  heatLoad,
  selectedHeatPump
}) => {
  // Calculate efficiency metrics
  const calculateEfficiency = () => {
    const scop = selectedHeatPump.model.scop;
    const annualHeatingDemand = heatLoad * buildingData.heatingHours; // kWh
    const electricityConsumption = annualHeatingDemand / scop; // kWh
    const efficiency = (scop - 1) / scop * 100; // Percentage of renewable energy
    
    return {
      scop,
      annualHeatingDemand,
      electricityConsumption,
      efficiency,
      renewableShare: efficiency
    };
  };

  // Calculate cost comparison
  const calculateCostComparison = () => {
    const efficiency = calculateEfficiency();
    const electricityPrice = 0.35; // €/kWh (average German electricity price)
    const gasPrice = 0.12; // €/kWh
    const oilPrice = 0.10; // €/kWh
    
    // Heat pump annual costs
    const heatPumpAnnualCost = efficiency.electricityConsumption * electricityPrice;
    
    // Current system annual costs
    let currentSystemCost = 0;
    if (buildingData.currentHeatingSystem.includes('Gas')) {
      currentSystemCost = efficiency.annualHeatingDemand * gasPrice / buildingData.systemEfficiency;
    } else if (buildingData.currentHeatingSystem.includes('Öl')) {
      currentSystemCost = efficiency.annualHeatingDemand * oilPrice / buildingData.systemEfficiency;
    } else {
      currentSystemCost = efficiency.annualHeatingDemand * 0.08; // Wood/other
    }
    
    const annualSavings = currentSystemCost - heatPumpAnnualCost;
    
    return {
      heatPumpAnnualCost,
      currentSystemCost,
      annualSavings,
      savingsPercentage: (annualSavings / currentSystemCost) * 100
    };
  };

  // Calculate savings projections
  const calculateSavingsProjections = () => {
    const costs = calculateCostComparison();
    const years = [1, 5, 10, 15, 20, 25];
    const priceIncrease = 0.03; // 3% annual price increase
    
    return years.map(year => {
      const cumulativeSavings = Array.from({ length: year }, (_, i) => {
        const yearFactor = Math.pow(1 + priceIncrease, i);
        return costs.annualSavings * yearFactor;
      }).reduce((sum, val) => sum + val, 0);
      
      return {
        year,
        savings: cumulativeSavings,
        heatPumpCost: costs.heatPumpAnnualCost * Math.pow(1 + priceIncrease, year - 1),
        currentSystemCost: costs.currentSystemCost * Math.pow(1 + priceIncrease, year - 1)
      };
    });
  };

  // Calculate environmental impact
  const calculateEnvironmentalImpact = () => {
    const efficiency = calculateEfficiency();
    const co2FactorElectricity = 0.420; // kg CO2/kWh (German electricity mix)
    const co2FactorGas = 0.247; // kg CO2/kWh
    const co2FactorOil = 0.318; // kg CO2/kWh
    
    // Heat pump CO2 emissions
    const heatPumpCO2 = efficiency.electricityConsumption * co2FactorElectricity;
    
    // Current system CO2 emissions
    let currentSystemCO2 = 0;
    if (buildingData.currentHeatingSystem.includes('Gas')) {
      currentSystemCO2 = efficiency.annualHeatingDemand * co2FactorGas / buildingData.systemEfficiency;
    } else if (buildingData.currentHeatingSystem.includes('Öl')) {
      currentSystemCO2 = efficiency.annualHeatingDemand * co2FactorOil / buildingData.systemEfficiency;
    } else {
      currentSystemCO2 = efficiency.annualHeatingDemand * 0.02; // Wood (nearly carbon neutral)
    }
    
    const co2Savings = currentSystemCO2 - heatPumpCO2;
    const co2SavingsPercentage = (co2Savings / currentSystemCO2) * 100;
    
    // Calculate equivalent trees
    const treesEquivalent = co2Savings / 22; // One tree absorbs ~22kg CO2/year
    
    return {
      heatPumpCO2,
      currentSystemCO2,
      co2Savings,
      co2SavingsPercentage,
      treesEquivalent,
      co2Savings25Years: co2Savings * 25
    };
  };

  const efficiency = calculateEfficiency();
  const costs = calculateCostComparison();
  const savingsProjections = calculateSavingsProjections();
  const environmental = calculateEnvironmentalImpact();

  // Prepare chart data
  const savingsChartData = {
    labels: savingsProjections.map(p => `Jahr ${p.year}`),
    datasets: [
      {
        label: 'Kumulierte Einsparungen',
        data: savingsProjections.map(p => p.savings),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true
      }
    ]
  };

  const costComparisonData = {
    labels: ['Wärmepumpe', 'Aktuelles System'],
    datasets: [
      {
        label: 'Jährliche Kosten (€)',
        data: [costs.heatPumpAnnualCost, costs.currentSystemCost],
        backgroundColor: ['#3b82f6', '#ef4444']
      }
    ]
  };

  const energyMixData = {
    labels: ['Erneuerbare Energie', 'Strom aus Netz'],
    datasets: [
      {
        data: [efficiency.renewableShare, 100 - efficiency.renewableShare],
        backgroundColor: ['#10b981', '#6b7280']
      }
    ]
  };

  const co2ComparisonData = {
    labels: ['Wärmepumpe', 'Aktuelles System'],
    datasets: [
      {
        label: 'CO₂-Emissionen (kg/Jahr)',
        data: [environmental.heatPumpCO2, environmental.currentSystemCO2],
        backgroundColor: ['#10b981', '#ef4444']
      }
    ]
  };

  return (
    <div className="heat-pump-results">
      {/* Results Summary */}
      <Card className="results-summary-card">
        <h2>📊 Ergebniszusammenfassung</h2>
        <Divider />
        
        <div className="summary-grid">
          <div className="summary-item">
            <div className="summary-icon">🏠</div>
            <div className="summary-content">
              <div className="summary-label">Heizlast</div>
              <div className="summary-value">{heatLoad.toFixed(2)} kW</div>
            </div>
          </div>

          <div className="summary-item">
            <div className="summary-icon">🔥</div>
            <div className="summary-content">
              <div className="summary-label">Wärmepumpe</div>
              <div className="summary-value">{selectedHeatPump.model.model}</div>
              <div className="summary-subtext">{selectedHeatPump.power} kW</div>
            </div>
          </div>

          <div className="summary-item">
            <div className="summary-icon">⚡</div>
            <div className="summary-content">
              <div className="summary-label">SCOP</div>
              <div className="summary-value">{efficiency.scop.toFixed(2)}</div>
              <div className="summary-subtext">Jahresarbeitszahl</div>
            </div>
          </div>

          <div className="summary-item highlight">
            <div className="summary-icon">💰</div>
            <div className="summary-content">
              <div className="summary-label">Jährliche Einsparung</div>
              <div className="summary-value">{costs.annualSavings.toFixed(0)} €</div>
              <div className="summary-subtext">{costs.savingsPercentage.toFixed(1)}% weniger Kosten</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Efficiency Calculations Display */}
      <Card className="efficiency-card">
        <h3>⚡ Effizienzberechnungen</h3>
        <Divider />
        
        <div className="efficiency-metrics">
          <div className="metric-row">
            <span className="metric-label">Jahreswärmebedarf:</span>
            <span className="metric-value">{efficiency.annualHeatingDemand.toLocaleString('de-DE')} kWh</span>
          </div>
          
          <div className="metric-row">
            <span className="metric-label">Stromverbrauch Wärmepumpe:</span>
            <span className="metric-value">{efficiency.electricityConsumption.toLocaleString('de-DE')} kWh</span>
          </div>
          
          <div className="metric-row">
            <span className="metric-label">Jahresarbeitszahl (SCOP):</span>
            <span className="metric-value">{efficiency.scop.toFixed(2)}</span>
          </div>
          
          <div className="metric-row highlight">
            <span className="metric-label">Anteil erneuerbarer Energie:</span>
            <span className="metric-value">{efficiency.renewableShare.toFixed(1)}%</span>
          </div>
        </div>

        <div className="efficiency-explanation">
          <p>
            <strong>Was bedeutet SCOP {efficiency.scop.toFixed(2)}?</strong><br />
            Für jede kWh Strom erzeugt die Wärmepumpe {efficiency.scop.toFixed(2)} kWh Wärme. 
            Das bedeutet, dass {efficiency.renewableShare.toFixed(1)}% der Wärme aus der Umwelt (Luft, Erde, Wasser) stammt.
          </p>
        </div>

        <div className="energy-mix-chart">
          <h4>Energiemix</h4>
          <PieChart
            data={energyMixData}
            options={{
              plugins: {
                legend: {
                  position: 'bottom'
                },
                tooltip: {
                  callbacks: {
                    label: (context: any) => {
                      return `${context.label}: ${context.parsed.toFixed(1)}%`;
                    }
                  }
                }
              }
            }}
          />
        </div>
      </Card>

      {/* Cost Comparison Charts */}
      <Card className="cost-comparison-card">
        <h3>💰 Kostenvergleich</h3>
        <Divider />
        
        <div className="cost-metrics">
          <div className="cost-item current-system">
            <h4>Aktuelles Heizsystem</h4>
            <div className="cost-value">{costs.currentSystemCost.toFixed(0)} €/Jahr</div>
            <div className="cost-label">{buildingData.currentHeatingSystem}</div>
          </div>

          <div className="cost-arrow">→</div>

          <div className="cost-item heat-pump">
            <h4>Wärmepumpe</h4>
            <div className="cost-value">{costs.heatPumpAnnualCost.toFixed(0)} €/Jahr</div>
            <div className="cost-label">Stromkosten</div>
          </div>
        </div>

        <div className="savings-highlight">
          <div className="savings-amount">
            <span className="savings-label">Jährliche Einsparung:</span>
            <span className="savings-value">{costs.annualSavings.toFixed(0)} €</span>
          </div>
          <ProgressBar 
            value={costs.savingsPercentage} 
            showValue={false}
            className="savings-progress"
          />
          <div className="savings-percentage">
            {costs.savingsPercentage.toFixed(1)}% Kostenreduktion
          </div>
        </div>

        <div className="cost-comparison-chart">
          <h4>Jährliche Betriebskosten im Vergleich</h4>
          <BarChart
            data={costComparisonData}
            options={{
              indexAxis: 'y',
              plugins: {
                legend: {
                  display: false
                },
                tooltip: {
                  callbacks: {
                    label: (context: any) => {
                      return `${context.parsed.x.toLocaleString('de-DE')} €/Jahr`;
                    }
                  }
                }
              },
              scales: {
                x: {
                  beginAtZero: true,
                  ticks: {
                    callback: (value: any) => `${value} €`
                  }
                }
              }
            }}
          />
        </div>
      </Card>

      {/* Savings Projections */}
      <Card className="savings-projections-card">
        <h3>📈 Einsparungsprognose</h3>
        <Divider />
        
        <div className="projections-info">
          <p>
            Kumulierte Einsparungen über die Lebensdauer der Wärmepumpe 
            (unter Berücksichtigung einer jährlichen Preissteigerung von 3%)
          </p>
        </div>

        <div className="projections-highlights">
          <div className="projection-item">
            <div className="projection-period">5 Jahre</div>
            <div className="projection-value">
              {savingsProjections[1].savings.toLocaleString('de-DE', { 
                style: 'currency', 
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </div>
          </div>

          <div className="projection-item">
            <div className="projection-period">10 Jahre</div>
            <div className="projection-value">
              {savingsProjections[2].savings.toLocaleString('de-DE', { 
                style: 'currency', 
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </div>
          </div>

          <div className="projection-item highlight">
            <div className="projection-period">25 Jahre</div>
            <div className="projection-value">
              {savingsProjections[5].savings.toLocaleString('de-DE', { 
                style: 'currency', 
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </div>
          </div>
        </div>

        <div className="savings-chart">
          <LineChart
            data={savingsChartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  display: false
                },
                tooltip: {
                  callbacks: {
                    label: (context: any) => {
                      return `Einsparung: ${context.parsed.y.toLocaleString('de-DE', {
                        style: 'currency',
                        currency: 'EUR',
                        maximumFractionDigits: 0
                      })}`;
                    }
                  }
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: (value: any) => `${(value / 1000).toFixed(0)}k €`
                  }
                }
              }
            }}
          />
        </div>

        <div className="investment-note">
          <i className="pi pi-info-circle"></i>
          <p>
            <strong>Hinweis:</strong> Die Investitionskosten für die Wärmepumpe 
            (ca. {selectedHeatPump.model.price_range}) sind in dieser Berechnung nicht enthalten. 
            Berücksichtigen Sie auch verfügbare Förderungen (bis zu 40% der Investitionskosten).
          </p>
        </div>
      </Card>

      {/* Environmental Impact Display */}
      <Card className="environmental-impact-card">
        <h3>🌱 Umweltauswirkungen</h3>
        <Divider />
        
        <div className="environmental-summary">
          <div className="environmental-metric">
            <div className="metric-icon">🌍</div>
            <div className="metric-content">
              <div className="metric-label">CO₂-Einsparung pro Jahr</div>
              <div className="metric-value">{environmental.co2Savings.toFixed(0)} kg</div>
              <div className="metric-subtext">
                {environmental.co2SavingsPercentage.toFixed(1)}% weniger Emissionen
              </div>
            </div>
          </div>

          <div className="environmental-metric">
            <div className="metric-icon">🌳</div>
            <div className="metric-content">
              <div className="metric-label">Entspricht</div>
              <div className="metric-value">{environmental.treesEquivalent.toFixed(0)} Bäume</div>
              <div className="metric-subtext">
                CO₂-Bindung pro Jahr
              </div>
            </div>
          </div>

          <div className="environmental-metric highlight">
            <div className="metric-icon">♻️</div>
            <div className="metric-content">
              <div className="metric-label">25-Jahres-Bilanz</div>
              <div className="metric-value">{(environmental.co2Savings25Years / 1000).toFixed(1)} t</div>
              <div className="metric-subtext">
                CO₂-Einsparung gesamt
              </div>
            </div>
          </div>
        </div>

        <div className="co2-comparison-chart">
          <h4>CO₂-Emissionen im Vergleich</h4>
          <BarChart
            data={co2ComparisonData}
            options={{
              indexAxis: 'y',
              plugins: {
                legend: {
                  display: false
                },
                tooltip: {
                  callbacks: {
                    label: (context: any) => {
                      return `${context.parsed.x.toLocaleString('de-DE')} kg CO₂/Jahr`;
                    }
                  }
                }
              },
              scales: {
                x: {
                  beginAtZero: true,
                  ticks: {
                    callback: (value: any) => `${value} kg`
                  }
                }
              }
            }}
          />
        </div>

        <div className="environmental-explanation">
          <h4>Warum ist eine Wärmepumpe umweltfreundlicher?</h4>
          <ul>
            <li>
              <strong>Erneuerbare Energie:</strong> {efficiency.renewableShare.toFixed(1)}% der Wärme 
              stammt aus der Umwelt (Luft, Erde oder Wasser)
            </li>
            <li>
              <strong>Effizienz:</strong> Mit 1 kWh Strom werden {efficiency.scop.toFixed(2)} kWh Wärme erzeugt
            </li>
            <li>
              <strong>Zukunftssicher:</strong> Mit zunehmendem Anteil erneuerbarer Energien im Strommix 
              wird die CO₂-Bilanz noch besser
            </li>
            <li>
              <strong>Kein direkter Ausstoß:</strong> Keine Verbrennung vor Ort, keine lokalen Emissionen
            </li>
          </ul>
        </div>

        <div className="environmental-actions">
          <h4>Weitere Optimierungsmöglichkeiten</h4>
          <div className="action-items">
            <div className="action-item">
              <i className="pi pi-sun"></i>
              <div>
                <strong>PV-Anlage kombinieren</strong>
                <p>Erhöhen Sie den Eigenverbrauch und reduzieren Sie die CO₂-Bilanz weiter</p>
              </div>
            </div>
            <div className="action-item">
              <i className="pi pi-bolt"></i>
              <div>
                <strong>Ökostrom nutzen</strong>
                <p>Mit 100% Ökostrom wird die Wärmepumpe nahezu CO₂-neutral</p>
              </div>
            </div>
            <div className="action-item">
              <i className="pi pi-cog"></i>
              <div>
                <strong>Smart Home Integration</strong>
                <p>Optimieren Sie den Betrieb für maximale Effizienz und Kosteneinsparung</p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Technical Details */}
      <Card className="technical-details-card">
        <h3>🔧 Technische Details</h3>
        <Divider />
        
        <div className="technical-grid">
          <div className="technical-section">
            <h4>Gebäudedaten</h4>
            <div className="detail-row">
              <span>Wohnfläche:</span>
              <span>{buildingData.heatedArea} m²</span>
            </div>
            <div className="detail-row">
              <span>Gebäudetyp:</span>
              <span>{buildingData.buildingType}</span>
            </div>
            <div className="detail-row">
              <span>Dämmqualität:</span>
              <span>{buildingData.insulationQuality}</span>
            </div>
            <div className="detail-row">
              <span>Baujahr:</span>
              <span>{buildingData.buildingYear}</span>
            </div>
          </div>

          <div className="technical-section">
            <h4>Wärmepumpe</h4>
            <div className="detail-row">
              <span>Modell:</span>
              <span>{selectedHeatPump.model.model}</span>
            </div>
            <div className="detail-row">
              <span>Hersteller:</span>
              <span>{selectedHeatPump.model.manufacturer}</span>
            </div>
            <div className="detail-row">
              <span>Typ:</span>
              <span>{selectedHeatPump.model.type}</span>
            </div>
            <div className="detail-row">
              <span>Heizleistung:</span>
              <span>{selectedHeatPump.power} kW</span>
            </div>
            <div className="detail-row">
              <span>Max. Vorlauftemperatur:</span>
              <span>{selectedHeatPump.model.max_flow_temp}°C</span>
            </div>
            <div className="detail-row">
              <span>Kältemittel:</span>
              <span>{selectedHeatPump.model.refrigerant}</span>
            </div>
          </div>

          <div className="technical-section">
            <h4>Berechnungsgrundlagen</h4>
            <div className="detail-row">
              <span>Heizlast:</span>
              <span>{heatLoad.toFixed(2)} kW</span>
            </div>
            <div className="detail-row">
              <span>Heizstunden/Jahr:</span>
              <span>{buildingData.heatingHours} h</span>
            </div>
            <div className="detail-row">
              <span>Heiztage/Jahr:</span>
              <span>{buildingData.heatingDays} Tage</span>
            </div>
            <div className="detail-row">
              <span>Klimazone:</span>
              <span>{buildingData.climateZone}</span>
            </div>
            <div className="detail-row">
              <span>Auslegungstemperatur:</span>
              <span>{buildingData.outsideTempDesign}°C</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
