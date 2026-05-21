import type { Meta, StoryObj } from '@storybook/react';
import { GermanNumberInput } from './GermanNumberInput';
import { useState } from 'react';

/**
 * GermanNumberInput is a specialized input component for German number formatting.
 * It automatically formats numbers with German locale conventions:
 * - Dot (.) as thousand separator
 * - Comma (,) as decimal separator
 * - Exactly 2 decimal places
 * 
 * ## Features
 * - Automatic German number formatting
 * - Bidirectional conversion (display ↔ calculation)
 * - Input validation
 * - Min/max value constraints
 * - Real-time formatting
 * - Keyboard-friendly
 * 
 * ## Examples
 * - Input: 1234.56 → Display: 1.234,56
 * - Input: 1000000 → Display: 1.000.000,00
 * - Input: 0.5 → Display: 0,50
 * 
 * ## Accessibility
 * - Proper label association
 * - Error state indication
 * - Keyboard navigation
 * - Screen reader support
 */
const meta = {
  title: 'Forms/GermanNumberInput',
  component: GermanNumberInput,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A number input component with automatic German formatting (1.234,56).',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: 'number',
      description: 'Numeric value (stored as standard number)',
    },
    onChange: {
      action: 'changed',
      description: 'Callback with numeric value',
    },
    label: {
      control: 'text',
      description: 'Input label',
    },
    min: {
      control: 'number',
      description: 'Minimum allowed value',
    },
    max: {
      control: 'number',
      description: 'Maximum allowed value',
    },
    disabled: {
      control: 'boolean',
      description: 'Disabled state',
    },
  },
} satisfies Meta<typeof GermanNumberInput>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Basic number input with German formatting
 */
export const Default: Story = {
  args: {
    label: 'Betrag',
    value: 1234.56,
  },
};

/**
 * Large number with thousand separators
 */
export const LargeNumber: Story = {
  args: {
    label: 'Systempreis',
    value: 25000.00,
  },
};

/**
 * Small decimal number
 */
export const SmallDecimal: Story = {
  args: {
    label: 'Prozentsatz',
    value: 0.75,
  },
};

/**
 * With min/max constraints
 */
export const WithConstraints: Story = {
  args: {
    label: 'Anzahl Module',
    value: 25,
    min: 10,
    max: 100,
  },
};

/**
 * Disabled state
 */
export const Disabled: Story = {
  args: {
    label: 'Berechneter Wert',
    value: 15750.50,
    disabled: true,
  },
};

/**
 * Interactive example
 */
export const Interactive = () => {
  const [value, setValue] = useState(5000);

  return (
    <div style={{ width: '300px' }}>
      <GermanNumberInput
        label="Investitionssumme (€)"
        value={value}
        onChange={setValue}
        min={0}
        max={100000}
      />
      <div style={{ marginTop: '1rem', padding: '1rem', background: '#f3f4f6', borderRadius: '4px' }}>
        <strong>Gespeicherter Wert:</strong> {value}
        <br />
        <small>Der Wert wird als Standard-Nummer gespeichert</small>
      </div>
    </div>
  );
};

/**
 * Multiple inputs in a form
 */
export const FormExample = () => {
  const [roofArea, setRoofArea] = useState(50.00);
  const [moduleCount, setModuleCount] = useState(30);
  const [systemCost, setSystemCost] = useState(18500.00);

  return (
    <div style={{ width: '400px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <GermanNumberInput
        label="Dachfläche (m²)"
        value={roofArea}
        onChange={setRoofArea}
        min={0}
        max={500}
      />
      <GermanNumberInput
        label="Anzahl Module"
        value={moduleCount}
        onChange={setModuleCount}
        min={1}
        max={200}
      />
      <GermanNumberInput
        label="Systemkosten (€)"
        value={systemCost}
        onChange={setSystemCost}
        min={0}
        max={100000}
      />
      <div style={{ padding: '1rem', background: '#f3f4f6', borderRadius: '4px' }}>
        <h4>Zusammenfassung:</h4>
        <p>Dachfläche: {roofArea} m²</p>
        <p>Module: {moduleCount} Stück</p>
        <p>Kosten: {systemCost.toFixed(2)} €</p>
      </div>
    </div>
  );
};
