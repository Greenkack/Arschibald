# Storybook Quick Reference

## Quick Start

```bash
# Install dependencies
npm install

# Start Storybook
npm run storybook

# Build Storybook
npm run build-storybook

# Test stories
npm run test-storybook
```

## Creating a Story

### 1. Basic Story Template

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { MyComponent } from './MyComponent';

const meta = {
  title: 'Category/MyComponent',
  component: MyComponent,
  tags: ['autodocs'],
} satisfies Meta<typeof MyComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    prop: 'value',
  },
};
```

### 2. With Documentation

```typescript
/**
 * MyComponent does something useful.
 * 
 * ## Features
 * - Feature 1
 * - Feature 2
 * 
 * ## Accessibility
 * - Keyboard navigable
 * - Screen reader support
 */
const meta = {
  title: 'Category/MyComponent',
  component: MyComponent,
  parameters: {
    docs: {
      description: {
        component: 'Detailed description here.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    prop: {
      control: 'text',
      description: 'Prop description',
    },
  },
} satisfies Meta<typeof MyComponent>;
```

### 3. Interactive Story

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

## Control Types

```typescript
argTypes: {
  text: { control: 'text' },
  number: { control: 'number' },
  boolean: { control: 'boolean' },
  select: { 
    control: 'select',
    options: ['option1', 'option2']
  },
  radio: {
    control: 'radio',
    options: ['option1', 'option2']
  },
  color: { control: 'color' },
  date: { control: 'date' },
  object: { control: 'object' },
  array: { control: 'array' },
}
```

## Common Patterns

### Multiple Variants

```typescript
export const Default: Story = { args: { /* ... */ } };
export const WithError: Story = { args: { /* ... */ } };
export const Disabled: Story = { args: { /* ... */ } };
export const Loading: Story = { args: { /* ... */ } };
```

### With Decorators

```typescript
const meta = {
  // ...
  decorators: [
    (Story) => (
      <div style={{ padding: '2rem' }}>
        <Story />
      </div>
    ),
  ],
};
```

### With Actions

```typescript
argTypes: {
  onClick: { action: 'clicked' },
  onChange: { action: 'changed' },
}
```

## Accessibility Testing

Storybook automatically checks accessibility with addon-a11y.

View results in the "Accessibility" tab.

## Keyboard Shortcuts

- `S` - Show/hide sidebar
- `A` - Show/hide addons panel
- `D` - Toggle dark mode
- `F` - Toggle fullscreen
- `/` - Search stories

## File Naming

- Component: `MyComponent.tsx`
- Story: `MyComponent.stories.tsx`
- Tests: `MyComponent.test.tsx`

## Categories

- Common
- Forms
- Charts
- Layout
- Solar
- HeatPump
- CRM
- Admin
- PDF
- Pricing
- Products
- 3D
- Migration
- Update
- Settings

## Best Practices

1. ✅ One story file per component
2. ✅ Multiple story variants
3. ✅ Document props with argTypes
4. ✅ Include accessibility info
5. ✅ Add interactive examples
6. ✅ Test edge cases
7. ✅ Use semantic HTML
8. ✅ Follow naming conventions

## Troubleshooting

### Stories not appearing
- Check file naming: `*.stories.tsx`
- Verify export statement
- Check `.storybook/main.ts` configuration

### Styling issues
- Import CSS in `.storybook/preview.ts`
- Check for conflicting styles
- Use decorators for consistent styling

### Build errors
- Clear cache: `rm -rf node_modules/.cache`
- Reinstall: `npm install`
- Check TypeScript errors

## Resources

- [Storybook Docs](https://storybook.js.org/docs)
- [Component Documentation](./COMPONENT_DOCUMENTATION.md)
- [Storybook Guide](./STORYBOOK_GUIDE.md)
