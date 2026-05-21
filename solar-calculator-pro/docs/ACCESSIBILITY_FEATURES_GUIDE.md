# Accessibility Features Guide

## Overview

The Solar Calculator Pro application includes comprehensive accessibility features to ensure all users can effectively use the application, regardless of their abilities or assistive technologies.

## Table of Contents

1. [Keyboard Navigation](#keyboard-navigation)
2. [Screen Reader Support](#screen-reader-support)
3. [Focus Management](#focus-management)
4. [Accessibility Settings](#accessibility-settings)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Accessibility Audit Tools](#accessibility-audit-tools)
7. [WCAG Compliance](#wcag-compliance)
8. [Best Practices](#best-practices)

## Keyboard Navigation

### Features

- **Full keyboard navigation** throughout the application
- **Tab order** follows logical reading order
- **Arrow key navigation** for lists and menus
- **Focus trap** in modal dialogs
- **Skip links** to jump to main content

### Custom Hook: `useKeyboardNavigation`

```typescript
import { useKeyboardNavigation } from '@/hooks/useKeyboardNavigation';

const MyComponent = () => {
  const { containerRef, focusFirst, focusLast } = useKeyboardNavigation({
    shortcuts: [
      {
        key: 's',
        ctrl: true,
        handler: () => handleSave(),
        description: 'Save',
        category: 'General',
      },
    ],
    enableFocusTrap: true,
    enableArrowNavigation: true,
    onEscape: () => handleClose(),
  });

  return <div ref={containerRef}>{/* content */}</div>;
};
```

### Global Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Open command palette |
| `Ctrl + /` | Open search |
| `Ctrl + S` | Save current work |
| `Shift + ?` | Show keyboard shortcuts help |
| `Escape` | Close dialog/Cancel |
| `Alt + 1-5` | Navigate to main sections |

## Screen Reader Support

### Features

- **ARIA labels** on all interactive elements
- **Live regions** for dynamic content updates
- **Semantic HTML** structure
- **Descriptive alt text** for images
- **Form field associations** with labels

### Custom Hook: `useScreenReader`

```typescript
import { useScreenReader } from '@/hooks/useScreenReader';

const MyComponent = () => {
  const {
    announce,
    announceError,
    announceSuccess,
    getFieldAriaProps,
  } = useScreenReader({
    announcePageChanges: true,
    announceFormErrors: true,
  });

  const handleSubmit = async () => {
    try {
      await saveData();
      announceSuccess('Data saved successfully');
    } catch (error) {
      announceError('Failed to save data');
    }
  };

  const fieldProps = getFieldAriaProps(
    'Email Address',
    errors.email,
    'Enter your email address',
    true
  );

  return (
    <input
      type="email"
      {...fieldProps}
    />
  );
};
```

### ARIA Utilities

The `useScreenReader` hook provides utilities for:

- **Field ARIA props**: Labels, descriptions, errors
- **Button ARIA props**: Pressed state, expanded state
- **Dialog ARIA props**: Modal, title, description
- **List ARIA props**: List size, item position

## Focus Management

### Features

- **Focus restoration** when closing dialogs
- **Auto-focus** on important elements
- **Focus trap** in modal contexts
- **Visible focus indicators**
- **Focus-visible** detection (keyboard vs mouse)

### Custom Hook: `useFocusManagement`

```typescript
import { useFocusManagement } from '@/hooks/useFocusManagement';

const MyDialog = ({ onClose }) => {
  const {
    containerRef,
    isFocusVisible,
    focusFirst,
    createFocusTrap,
  } = useFocusManagement({
    trapFocus: true,
    restoreFocus: true,
    autoFocus: true,
  });

  useEffect(() => {
    const cleanup = createFocusTrap();
    return cleanup;
  }, [createFocusTrap]);

  return (
    <div ref={containerRef} className={isFocusVisible ? 'focus-visible' : ''}>
      {/* dialog content */}
    </div>
  );
};
```

### Focus Utilities

- `focusFirst()`: Focus first focusable element
- `focusLast()`: Focus last focusable element
- `focusNext()`: Move focus to next element
- `focusPrevious()`: Move focus to previous element
- `getFocusableElements()`: Get all focusable elements
- `isFocusable(element)`: Check if element is focusable

## Accessibility Settings

### Available Settings

#### Visual Settings
- **High Contrast Mode**: Increases contrast for better readability
- **Reduced Motion**: Minimizes animations and transitions
- **Font Size**: Adjustable from 75% to 200%
- **Focus Indicator Style**: Default, Enhanced, or High Contrast

#### Screen Reader Settings
- **Screen Reader Optimized**: Optimizes interface for screen readers
- **Announce Page Changes**: Announces navigation changes
- **Announce Form Errors**: Announces validation errors
- **Verbose Descriptions**: Provides detailed descriptions

#### Keyboard Settings
- **Keyboard Shortcuts**: Enable/disable shortcuts
- **Focus Trap**: Keep focus within dialogs
- **Skip Links**: Show skip navigation links

#### Content Settings
- **Autoplay Media**: Control automatic media playback
- **Flashing Content**: Control flashing/rapid changes

### Using Accessibility Settings

```typescript
import { AccessibilitySettings } from '@/components/accessibility/AccessibilitySettings';

const SettingsPage = () => {
  return (
    <div>
      <h1>Settings</h1>
      <AccessibilitySettings />
    </div>
  );
};
```

### Persistence

All accessibility preferences are:
- Saved to `localStorage`
- Applied immediately on change
- Restored on page load
- Synced across tabs

## Keyboard Shortcuts

### Keyboard Shortcuts Help Component

```typescript
import { KeyboardShortcutsHelp } from '@/components/accessibility/KeyboardShortcutsHelp';

const App = () => {
  return (
    <div>
      {/* Your app content */}
      <KeyboardShortcutsHelp />
    </div>
  );
};
```

### Features

- **Searchable** shortcuts list
- **Categorized** by function
- **Visual key indicators**
- **Quick access** with `Shift + ?`

### Shortcut Categories

1. **Navigation**: Moving between pages
2. **General**: Common actions (save, undo, etc.)
3. **Editing**: Text and content editing
4. **Forms**: Form navigation and submission
5. **Tables**: Table navigation
6. **Help**: Access help and documentation

## Accessibility Audit Tools

### Accessibility Auditor

```typescript
import { accessibilityAuditor } from '@/utils/accessibilityAudit';

// Run audit on entire page
const result = accessibilityAuditor.audit();

console.log('Passed:', result.passed);
console.log('Errors:', result.summary.errors);
console.log('Warnings:', result.summary.warnings);

// Run audit on specific container
const container = document.getElementById('my-component');
const componentResult = accessibilityAuditor.audit(container);

// Generate HTML report
const reportHtml = accessibilityAuditor.generateReport(result);
```

### Audit Checks

The auditor checks for:

1. **Images**: Missing alt text
2. **Forms**: Missing labels, required fields
3. **Headings**: Proper hierarchy, single h1
4. **Links**: Accessible names, descriptive text
5. **Buttons**: Accessible names
6. **Landmarks**: Main, navigation regions
7. **Color Contrast**: Sufficient contrast ratios
8. **Keyboard Access**: Tab order, keyboard handlers
9. **ARIA**: Valid roles and labels
10. **Tab Index**: Proper usage

### Issue Severity Levels

- **Error**: Critical accessibility issue (WCAG failure)
- **Warning**: Potential accessibility issue
- **Info**: Suggestion for improvement

## WCAG Compliance

### Compliance Level

The application aims for **WCAG 2.1 Level AA** compliance.

### Key WCAG Criteria Addressed

#### Perceivable
- **1.1.1**: Text alternatives for images
- **1.3.1**: Info and relationships (semantic HTML)
- **1.4.3**: Contrast ratio (minimum 4.5:1)

#### Operable
- **2.1.1**: Keyboard accessible
- **2.1.2**: No keyboard trap
- **2.4.3**: Focus order
- **2.4.4**: Link purpose
- **2.4.7**: Focus visible

#### Understandable
- **3.2.1**: On focus (no unexpected changes)
- **3.3.1**: Error identification
- **3.3.2**: Labels or instructions

#### Robust
- **4.1.2**: Name, role, value (ARIA)
- **4.1.3**: Status messages

## Best Practices

### For Developers

1. **Use Semantic HTML**
   ```tsx
   // Good
   <button onClick={handleClick}>Submit</button>
   
   // Bad
   <div onClick={handleClick}>Submit</div>
   ```

2. **Provide ARIA Labels**
   ```tsx
   <button aria-label="Close dialog" onClick={onClose}>
     <i className="pi pi-times" />
   </button>
   ```

3. **Associate Labels with Inputs**
   ```tsx
   <label htmlFor="email">Email</label>
   <input id="email" type="email" />
   ```

4. **Use Focus Management Hooks**
   ```tsx
   const { containerRef } = useFocusManagement({
     trapFocus: true,
     restoreFocus: true,
   });
   ```

5. **Announce Dynamic Changes**
   ```tsx
   const { announce } = useScreenReader();
   
   useEffect(() => {
     if (dataLoaded) {
       announce('Data loaded successfully');
     }
   }, [dataLoaded]);
   ```

### For Content Creators

1. **Write Descriptive Alt Text**
   - Describe the content and function
   - Keep it concise (< 150 characters)
   - Don't start with "Image of..."

2. **Use Descriptive Link Text**
   - Avoid "click here" or "read more"
   - Make links meaningful out of context

3. **Maintain Heading Hierarchy**
   - Use only one h1 per page
   - Don't skip heading levels
   - Use headings for structure, not styling

4. **Provide Form Instructions**
   - Label all form fields
   - Indicate required fields
   - Provide clear error messages

### Testing Checklist

- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Test with high contrast mode
- [ ] Test with 200% zoom
- [ ] Test with reduced motion
- [ ] Run accessibility audit
- [ ] Check color contrast
- [ ] Verify focus indicators
- [ ] Test form validation
- [ ] Check ARIA labels

## Resources

### Tools
- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### Screen Readers
- [NVDA](https://www.nvaccess.org/) (Windows, Free)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) (Windows)
- [VoiceOver](https://www.apple.com/accessibility/voiceover/) (macOS, iOS)

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Support

For accessibility issues or questions:
- Email: accessibility@solarcalculatorpro.com
- GitHub Issues: Tag with `accessibility` label
- Documentation: See `/docs/ACCESSIBILITY_QUICK_REFERENCE.md`
