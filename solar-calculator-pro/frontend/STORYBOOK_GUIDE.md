# Storybook Component Documentation Guide

## Overview

This project uses Storybook for component documentation, development, and testing. Storybook provides an isolated environment to develop and showcase UI components.

## Getting Started

### Installation

Storybook dependencies are included in `package.json`. To install:

```bash
npm install
```

### Running Storybook

Start the Storybook development server:

```bash
npm run storybook
```

This will start Storybook on `http://localhost:6006`

### Building Storybook

To build a static version of Storybook for deployment:

```bash
npm run build-storybook
```

The static files will be generated in `storybook-static/`

## Project Structure

```
frontend/
├── .storybook/
│   ├── main.ts          # Storybook configuration
│   ├── preview.ts       # Global decorators and parameters
│   └── manager.ts       # Storybook UI customization
├── src/
│   └── components/
│       ├── common/
│       │   ├── FormInput.tsx
│       │   ├── FormInput.stories.tsx
│       │   ├── Modal.tsx
│       │   └── Modal.stories.tsx
│       ├── charts/
│       │   ├── LineChart.tsx
│       │   └── LineChart.stories.tsx
│       └── ...
```

## Writing Stories

### Basic Story Structure

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { MyComponent } from './MyComponent';

const meta = {
  title: 'Category/MyComponent',
  component: MyComponent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    propName: {
      control: 'text',
      description: 'Description of the prop',
    },
  },
} satisfies Meta<typeof MyComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    propName: 'value',
  },
};
```

### Story Categories

Components are organized into the following categories:

- **Common**: Reusable UI components (buttons, inputs, modals)
- **Forms**: Form-specific components
- **Charts**: Data visualization components
- **Layout**: Layout and navigation components
- **Admin**: Admin panel components
- **CRM**: Customer relationship management components
- **Solar**: Solar calculator components
- **HeatPump**: Heat pump calculator components
- **PDF**: PDF generation components
- **Pricing**: Price matrix components
- **Products**: Product management components
- **3D**: 3D visualization components

### Documentation Best Practices

#### 1. Component Description

Add a comprehensive JSDoc comment above the meta object:

```typescript
/**
 * ComponentName provides [brief description].
 * 
 * ## Features
 * - Feature 1
 * - Feature 2
 * 
 * ## Use Cases
 * - Use case 1
 * - Use case 2
 * 
 * ## Accessibility
 * - Accessibility feature 1
 * - Accessibility feature 2
 */
const meta = {
  // ...
};
```

#### 2. Prop Documentation

Document all props with descriptions and controls:

```typescript
argTypes: {
  label: {
    control: 'text',
    description: 'Label text displayed above the input',
  },
  disabled: {
    control: 'boolean',
    description: 'Whether the component is disabled',
  },
  size: {
    control: 'select',
    options: ['small', 'medium', 'large'],
    description: 'Component size variant',
  },
}
```

#### 3. Multiple Story Variants

Create stories for different states and use cases:

```typescript
export const Default: Story = { /* ... */ };
export const WithError: Story = { /* ... */ };
export const Disabled: Story = { /* ... */ };
export const Loading: Story = { /* ... */ };
```

#### 4. Interactive Stories

For complex interactions, create interactive stories:

```typescript
export const Interactive = () => {
  const [value, setValue] = useState('');
  
  return (
    <MyComponent
      value={value}
      onChange={setValue}
    />
  );
};
```

## Accessibility Documentation

Every component story should include accessibility information:

### Required Accessibility Features

1. **Keyboard Navigation**
   - Document keyboard shortcuts
   - Explain tab order
   - Describe focus management

2. **Screen Reader Support**
   - ARIA labels and descriptions
   - Role attributes
   - Live regions for dynamic content

3. **Visual Accessibility**
   - Color contrast ratios
   - Focus indicators
   - High contrast mode support

### Example Accessibility Documentation

```typescript
/**
 * ## Accessibility
 * - **Keyboard**: Tab to focus, Enter to activate, ESC to close
 * - **Screen Reader**: Proper ARIA labels and role="dialog"
 * - **Focus**: Focus trap within modal, returns to trigger on close
 * - **Contrast**: Meets WCAG AA standards (4.5:1 minimum)
 */
```

## Component Categories

### Common Components

Located in `src/components/common/`:
- FormInput
- Modal
- DataTable
- ConfirmDialog
- ToastNotification
- SkeletonLoader
- LoadingSpinner
- VirtualList
- LazyImage

### Form Components

Located in `src/components/forms/` and root:
- FormContainer
- FormField
- GermanNumberInput
- GermanCurrencyInput
- GermanPercentInput
- GermanSlider
- FormattedDisplay

### Chart Components

Located in `src/components/charts/`:
- LineChart
- BarChart
- PieChart
- AreaChart

### Layout Components

Located in `src/components/layout/`:
- MainLayout
- Header
- Sidebar
- Footer
- MobileDrawer

### Domain-Specific Components

- **Solar**: SolarCalculatorForm, SolarCalculationResults
- **HeatPump**: HeatPumpInputForm, HeatPumpResults
- **CRM**: CustomerList, CustomerForm, TaskList
- **Admin**: UserList, SystemSettings, DatabaseManagement
- **PDF**: PDFGenerator, TemplateGallery, PDFConfiguration
- **Pricing**: MatrixUpload, PriceCalculator, MatrixPreview
- **Products**: ProductCatalog, ProductForm, ProductComparison
- **3D**: Viewer3D, RoofModel, ModulePlacement

## Testing with Storybook

### Visual Testing

Storybook provides visual regression testing capabilities:

```bash
npm run test-storybook
```

### Interaction Testing

Use the `@storybook/addon-interactions` for testing user interactions:

```typescript
export const WithInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    await expect(canvas.getByText('Clicked!')).toBeInTheDocument();
  },
};
```

### Accessibility Testing

The `@storybook/addon-a11y` automatically checks for accessibility issues:

- View the "Accessibility" tab in Storybook
- Fix any violations or warnings
- Document accessibility features in component stories

## Deployment

### Static Deployment

Build and deploy the static Storybook:

```bash
npm run build-storybook
# Deploy storybook-static/ to your hosting service
```

### Chromatic (Optional)

For visual regression testing and review:

```bash
npx chromatic --project-token=<your-token>
```

## Best Practices

### 1. Keep Stories Simple

Each story should demonstrate one specific use case or state.

### 2. Use Real Data

When possible, use realistic data that represents actual use cases.

### 3. Document Edge Cases

Create stories for edge cases:
- Empty states
- Error states
- Loading states
- Maximum/minimum values

### 4. Maintain Consistency

Follow the established patterns for:
- Story naming
- Category organization
- Documentation format
- Code style

### 5. Update Regularly

Keep stories updated when components change:
- Add new props to argTypes
- Update descriptions
- Add new story variants
- Fix broken stories

## Troubleshooting

### Storybook Won't Start

1. Clear cache: `rm -rf node_modules/.cache`
2. Reinstall dependencies: `npm install`
3. Check for port conflicts (default: 6006)

### Stories Not Appearing

1. Check file naming: `*.stories.tsx`
2. Verify story is exported
3. Check Storybook configuration in `.storybook/main.ts`

### Styling Issues

1. Ensure CSS imports in `.storybook/preview.ts`
2. Check for conflicting global styles
3. Use Storybook decorators for consistent styling

## Resources

- [Storybook Documentation](https://storybook.js.org/docs/react/get-started/introduction)
- [Component Story Format (CSF)](https://storybook.js.org/docs/react/api/csf)
- [Storybook Addons](https://storybook.js.org/docs/react/essentials/introduction)
- [Accessibility Testing](https://storybook.js.org/docs/react/writing-tests/accessibility-testing)

## Contributing

When adding new components:

1. Create the component file
2. Create a corresponding `.stories.tsx` file
3. Document all props and use cases
4. Include accessibility information
5. Add interactive examples where appropriate
6. Test in Storybook before committing
