import type { Meta, StoryObj } from '@storybook/react';
import { SolarCalculatorForm } from './SolarCalculatorForm';

/**
 * SolarCalculatorForm is the main input form for solar system calculations.
 * 
 * ## Features
 * - Multi-step form with validation
 * - Roof configuration inputs
 * - Location selection with autocomplete
 * - Module type selection with images
 * - Consumption data inputs
 * - Real-time validation
 * - Progress indicator
 * 
 * ## Form Steps
 * 1. Roof Configuration (area, type, angle, orientation)
 * 2. Location Selection
 * 3. Module Selection
 * 4. Consumption Data
 * 5. Review and Calculate
 * 
 * ## Accessibility
 * - Form field labels and descriptions
 * - Error messages linked to fields
 * - Keyboard navigation between steps
 * - Progress indicator for screen readers
 * - Required field indicators
 */
const meta = {
  title: 'Solar/SolarCalculatorForm',
  component: SolarCalculatorForm,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Multi-step form for solar system calculation inputs.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    onSubmit: {
      action: 'submitted',
      description: 'Callback when form is submitted',
    },
    initialData: {
      description: 'Initial form data for editing',
    },
  },
} satisfies Meta<typeof SolarCalculatorForm>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Empty form for new calculation
 */
export const NewCalculation: Story = {
  args: {},
};

/**
 * Form with pre-filled data
 */
export const EditExisting: Story = {
  args: {
    initialData: {
      roofArea: 50,
      roofType: 'flat',
      roofAngle: 30,
      orientation: 'south',
      location: 'Berlin',
      moduleType: 'standard',
      annualConsumption: 4000,
    },
  },
};

/**
 * Form with validation errors
 */
export const WithErrors: Story = {
  args: {
    initialData: {
      roofArea: -10, // Invalid
      roofType: '',  // Missing
      roofAngle: 95, // Out of range
    },
  },
};
