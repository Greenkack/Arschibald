/**
 * German Input Components Demo
 * 
 * Demonstration of all custom German number formatting input components.
 * Shows usage examples and features.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import {
  GermanNumberInput,
  GermanCurrencyInput,
  GermanPercentInput,
  GermanSlider
} from '../components';
import '../styles/germanInputComponents.css';

export const GermanInputComponentsDemo: React.FC = () => {
  // State for each component
  const [numberValue, setNumberValue] = useState<number>(1234.56);
  const [currencyValue, setCurrencyValue] = useState<number>(5000);
  const [percentValue, setPercentValue] = useState<number>(0.15); // 15%
  const [sliderValue, setSliderValue] = useState<number>(50);
  const [rangeValue, setRangeValue] = useState<number[]>([20, 80]);

  // Validation error handler
  const handleValidationError = (error: string) => {
    console.error('Validation Error:', error);
  };

  return (
    <div className="german-input-demo" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>German Input Components Demo</h1>
      <p>Demonstration aller benutzerdefinierten Eingabekomponenten mit deutscher Zahlenformatierung.</p>

      <Divider />

      {/* GermanNumberInput Demo */}
      <Card title="GermanNumberInput" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div>
            <h3>Basic Number Input</h3>
            <GermanNumberInput
              value={numberValue}
              onChange={setNumberValue}
              label="Betrag"
              placeholder="Wert eingeben"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {numberValue}
            </p>
          </div>

          <div>
            <h3>With Min/Max Validation</h3>
            <GermanNumberInput
              value={numberValue}
              onChange={setNumberValue}
              label="Betrag (0 - 10.000)"
              min={0}
              max={10000}
              onValidationError={handleValidationError}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Min: 0, Max: 10.000
            </p>
          </div>

          <div>
            <h3>Custom Decimal Places</h3>
            <GermanNumberInput
              value={numberValue}
              onChange={setNumberValue}
              label="Präziser Wert"
              decimalPlaces={4}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              4 Dezimalstellen
            </p>
          </div>

          <div>
            <h3>Disabled State</h3>
            <GermanNumberInput
              value={numberValue}
              onChange={setNumberValue}
              label="Deaktiviert"
              disabled={true}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Nicht editierbar
            </p>
          </div>
        </div>

        <Divider />
        
        <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h4>Features:</h4>
          <ul>
            <li>✅ Deutsche Formatierung (1.234,56)</li>
            <li>✅ Bidirektionale Konvertierung</li>
            <li>✅ Min/Max Validierung</li>
            <li>✅ Anpassbare Dezimalstellen</li>
            <li>✅ Fehlerbehandlung</li>
            <li>✅ Tastatureingabe-Filterung</li>
          </ul>
        </div>
      </Card>

      {/* GermanCurrencyInput Demo */}
      <Card title="GermanCurrencyInput" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div>
            <h3>Euro (Suffix)</h3>
            <GermanCurrencyInput
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Preis"
              currencySymbol="€"
              symbolPosition="suffix"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {currencyValue} EUR
            </p>
          </div>

          <div>
            <h3>Dollar (Prefix)</h3>
            <GermanCurrencyInput
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Price"
              currencySymbol="$"
              symbolPosition="prefix"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Current value: {currencyValue} USD
            </p>
          </div>

          <div>
            <h3>With Min Value</h3>
            <GermanCurrencyInput
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Mindestbetrag"
              min={100}
              onValidationError={handleValidationError}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Minimum: 100,00 €
            </p>
          </div>

          <div>
            <h3>With Max Value</h3>
            <GermanCurrencyInput
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Maximalbetrag"
              max={100000}
              onValidationError={handleValidationError}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Maximum: 100.000,00 €
            </p>
          </div>
        </div>

        <Divider />
        
        <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h4>Features:</h4>
          <ul>
            <li>✅ Währungssymbol (anpassbar)</li>
            <li>✅ Prefix oder Suffix Position</li>
            <li>✅ Immer 2 Dezimalstellen</li>
            <li>✅ Min/Max Validierung</li>
            <li>✅ Automatische Formatierung beim Fokus verlassen</li>
          </ul>
        </div>
      </Card>

      {/* GermanPercentInput Demo */}
      <Card title="GermanPercentInput" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div>
            <h3>Percentage (0-100%)</h3>
            <GermanPercentInput
              value={percentValue}
              onChange={setPercentValue}
              label="Prozentsatz"
              multiplyBy100={true}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {(percentValue * 100).toFixed(2)}%
            </p>
          </div>

          <div>
            <h3>Direct Percentage</h3>
            <GermanPercentInput
              value={15}
              onChange={(val) => console.log('Percent:', val)}
              label="Direkt als Prozent"
              multiplyBy100={false}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Keine Multiplikation mit 100
            </p>
          </div>

          <div>
            <h3>With Range (0-50%)</h3>
            <GermanPercentInput
              value={percentValue}
              onChange={setPercentValue}
              label="Begrenzter Bereich"
              min={0}
              max={50}
              multiplyBy100={true}
              onValidationError={handleValidationError}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Max: 50%
            </p>
          </div>

          <div>
            <h3>Disabled</h3>
            <GermanPercentInput
              value={percentValue}
              onChange={setPercentValue}
              label="Deaktiviert"
              disabled={true}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Nicht editierbar
            </p>
          </div>
        </div>

        <Divider />
        
        <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h4>Features:</h4>
          <ul>
            <li>✅ Prozentzeichen automatisch</li>
            <li>✅ Multiplikation mit 100 optional</li>
            <li>✅ Min/Max Validierung (0-100%)</li>
            <li>✅ Deutsche Formatierung</li>
            <li>✅ Fokus-Verhalten optimiert</li>
          </ul>
        </div>
      </Card>

      {/* GermanSlider Demo */}
      <Card title="GermanSlider" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
          <div>
            <h3>Number Slider</h3>
            <GermanSlider
              value={sliderValue}
              onChange={setSliderValue}
              label="Wert"
              min={0}
              max={100}
              step={1}
              showValue={true}
              showMinMax={true}
              formatType="number"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {sliderValue}
            </p>
          </div>

          <div>
            <h3>Currency Slider</h3>
            <GermanSlider
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Preis"
              min={0}
              max={10000}
              step={100}
              showValue={true}
              showMinMax={true}
              formatType="currency"
              currencySymbol="€"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {currencyValue} EUR
            </p>
          </div>

          <div>
            <h3>Percent Slider</h3>
            <GermanSlider
              value={percentValue * 100}
              onChange={(val) => setPercentValue(val / 100)}
              label="Prozentsatz"
              min={0}
              max={100}
              step={5}
              showValue={true}
              showMinMax={true}
              formatType="percent"
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Wert: {(percentValue * 100).toFixed(2)}%
            </p>
          </div>

          <div>
            <h3>Range Slider</h3>
            <GermanSlider
              value={rangeValue}
              onChange={setRangeValue}
              label="Bereich"
              min={0}
              max={100}
              step={1}
              showValue={true}
              showMinMax={true}
              formatType="number"
              range={true}
            />
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
              Aktueller Bereich: {rangeValue[0]} - {rangeValue[1]}
            </p>
          </div>

          <div>
            <h3>Without Min/Max Labels</h3>
            <GermanSlider
              value={sliderValue}
              onChange={setSliderValue}
              label="Einfacher Slider"
              min={0}
              max={100}
              step={1}
              showValue={true}
              showMinMax={false}
              formatType="number"
            />
          </div>
        </div>

        <Divider />
        
        <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h4>Features:</h4>
          <ul>
            <li>✅ Deutsche Formatierung für Werte</li>
            <li>✅ Verschiedene Format-Typen (number, currency, percent)</li>
            <li>✅ Min/Max Anzeige</li>
            <li>✅ Wert-Anzeige</li>
            <li>✅ Range-Slider Unterstützung</li>
            <li>✅ Anpassbare Schrittweite</li>
          </ul>
        </div>
      </Card>

      {/* Summary */}
      <Card title="Zusammenfassung" style={{ marginBottom: '2rem' }}>
        <div style={{ padding: '1rem' }}>
          <h3>Alle Komponenten erfüllen:</h3>
          <ul style={{ fontSize: '1rem', lineHeight: '1.8' }}>
            <li><strong>Requirement 14.3:</strong> Deutsche Formatierung in allen Input-Feldern</li>
            <li><strong>Requirement 14.6:</strong> Bidirektionale Konvertierung (Anzeige ↔ Berechnung)</li>
            <li><strong>Requirement 14.9:</strong> Validierung und Fehlerbehandlung</li>
          </ul>

          <Divider />

          <h3>Verwendung:</h3>
          <pre style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
{`import {
  GermanNumberInput,
  GermanCurrencyInput,
  GermanPercentInput,
  GermanSlider
} from './components';

// Number Input
<GermanNumberInput
  value={value}
  onChange={setValue}
  label="Betrag"
  min={0}
  max={10000}
/>

// Currency Input
<GermanCurrencyInput
  value={value}
  onChange={setValue}
  label="Preis"
  currencySymbol="€"
/>

// Percent Input
<GermanPercentInput
  value={value}
  onChange={setValue}
  label="Prozentsatz"
  multiplyBy100={true}
/>

// Slider
<GermanSlider
  value={value}
  onChange={setValue}
  label="Wert"
  formatType="currency"
/>`}
          </pre>
        </div>
      </Card>
    </div>
  );
};

export default GermanInputComponentsDemo;
