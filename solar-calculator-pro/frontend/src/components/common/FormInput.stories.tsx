import type { Meta, StoryObj } from '@storybook/react';
import { FormInput } from './FormInput';

/**
 * FormInput is a reusable input component that wraps PrimeReact InputText
 * with consistent styling and validation support.
 * 
 * ## Features
 * - Label support
 * - Error message display
 * - Required field indicator
 * - Disabled state
 * - Custom placeholder
 * - Full width or custom width
 * 
 * ## Accessibility
 * - Proper label association with htmlFor
 * - Error messages linked with aria-describedby
 * - Required fields indicated with aria-required
 * - Disabled state properly communicated
 */
const meta = {
  title: 'Common/FormInput',
  component: FormInput,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A flexible form input component with built-in validation and accessibility features.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    label: {
      control: 'text',
      description: 'Label text displayed above the input',
    },
    value: {
      control: 'text',
      description: 'Current value of the input',
    },
    onChange: {
      action: 'changed',
      description: 'Callback fired when input value changes',
    },
    error: {
      control: 'text',
      description: 'Error message to display below the input',
    },
    required: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the input is disabled',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text shown when input is empty',
    },
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'tel', 'url'],
      description: 'HTML input type',
    },
  },
} satisfies Meta<typeof FormInput>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default input with label
 */
export const Default: Story = {
  args: {
    label: 'Username',
    value: '',
    placeholder: 'Enter your username',
  },
};

/**
 * Input with error message
 */
export const WithError: Story = {
  args: {
    label: 'Email',
    value: 'invalid-email',
    error: 'Please enter a valid email address',
    placeholder: 'user@example.com',
  },
};

/**
 * Required field indicator
 */
export const Required: Story = {
  args: {
    label: 'Password',
    value: '',
    required: true,
    type: 'password',
    placeholder: 'Enter your password',
  },
};

/**
 * Disabled state
 */
export const Disabled: Story = {
  args: {
    label: 'Account ID',
    value: 'ACC-12345',
    disabled: true,
  },
};

/**
 * Number input type
 */
export const NumberInput: Story = {
  args: {
    label: 'Age',
    value: '',
    type: 'number',
    placeholder: 'Enter your age',
  },
};

/**
 * Email input with validation
 */
export const EmailInput: Story = {
  args: {
    label: 'Email Address',
    value: '',
    type: 'email',
    required: true,
    placeholder: 'your.email@example.com',
  },
};
