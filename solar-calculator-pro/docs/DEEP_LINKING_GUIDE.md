# Deep Linking Guide

## Overview

Solar Calculator Pro supports deep linking through a custom URL protocol (`solarcalc://`). This allows external applications, websites, and emails to launch the application and navigate to specific features or open specific content.

## Table of Contents

- [Protocol Registration](#protocol-registration)
- [URL Structure](#url-structure)
- [Available Actions](#available-actions)
- [Usage Examples](#usage-examples)
- [Integration Scenarios](#integration-scenarios)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Protocol Registration

The `solarcalc://` protocol is automatically registered when the application is installed. The registration happens at the operating system level:

- **Windows**: Registry entries are created during installation
- **macOS**: The protocol is registered in the app's Info.plist
- **Linux**: Desktop entry files are created with MIME type associations

### Checking Registration Status

You can check if the protocol is registered using the application's API:

```typescript
const { isProtocolRegistered } = useDeepLink();
const status = await isProtocolRegistered();
console.log('Protocol registered:', status.isRegistered);
```

## URL Structure

Deep links follow this structure:

```
solarcalc://action[/path-segments]?param1=value1&param2=value2
```

### Components

1. **Protocol**: `solarcalc://` (required)
2. **Action**: The action to perform (required)
3. **Path Segments**: Additional path information (optional)
4. **Query Parameters**: Key-value pairs for additional data (optional)

### Examples

```
solarcalc://open-project?id=12345
solarcalc://customer/67890
solarcalc://solar-calculator?roofArea=50&location=Berlin
solarcalc://generate-pdf?project=12345&template=standard
```

## Available Actions

### Project Management

#### `open-project`
Opens a specific project by ID.

**Parameters:**
- `id` (required): Project ID

**Example:**
```
solarcalc://open-project?id=12345
```

#### `open-project-path`
Opens a project from a file path.

**Parameters:**
- `path` (required): Full path to project file

**Example:**
```
solarcalc://open-project-path?path=/path/to/project.json
```

#### `new-project`
Creates a new project.

**Parameters:**
- `type` (optional): Project type (solar, heatpump, combined)
- Additional parameters for pre-filling data

**Example:**
```
solarcalc://new-project?type=solar
```

### Navigation

#### `navigate`
Navigates to a specific page.

**Parameters:**
- `page` (required): Page name
- Additional parameters passed to the page

**Example:**
```
solarcalc://navigate?page=dashboard
```

#### `dashboard`
Opens the dashboard.

**Example:**
```
solarcalc://dashboard
```

#### `settings`
Opens the settings page.

**Parameters:**
- `section` (optional): Specific settings section

**Example:**
```
solarcalc://settings?section=notifications
```

### Calculators

#### `solar-calculator`
Opens the solar calculator with optional pre-filled data.

**Parameters:**
- `roofArea`: Roof area in square meters
- `roofType`: Roof type (flat, gable, hip)
- `roofAngle`: Roof angle in degrees
- `orientation`: Roof orientation (north, south, east, west)
- `location`: Location name
- `annualConsumption`: Annual energy consumption in kWh

**Example:**
```
solarcalc://solar-calculator?roofArea=50&roofType=flat&location=Berlin
```

#### `heat-pump`
Opens the heat pump calculator with optional pre-filled data.

**Parameters:**
- Similar to solar calculator, specific to heat pump calculations

**Example:**
```
solarcalc://heat-pump?buildingArea=150&heatingType=underfloor
```

### CRM

#### `customer`
Opens a specific customer record.

**Parameters:**
- `id` (required): Customer ID

**Example:**
```
solarcalc://customer?id=67890
solarcalc://customer/67890
```

#### `offer`
Opens a specific offer.

**Parameters:**
- `id` (required): Offer ID

**Example:**
```
solarcalc://offer?id=54321
```

### PDF Generation

#### `generate-pdf`
Generates a PDF for a project.

**Parameters:**
- `project` (required): Project ID
- `template` (optional): Template ID

**Example:**
```
solarcalc://generate-pdf?project=12345&template=standard
```

### Data Management

#### `import`
Imports data from a file.

**Parameters:**
- `file` (required): File path
- `type` (optional): Import type

**Example:**
```
solarcalc://import?file=/path/to/data.xlsx&type=customers
```

#### `price-matrix`
Opens the price matrix management.

**Parameters:**
- `id` (optional): Specific matrix ID

**Example:**
```
solarcalc://price-matrix
solarcalc://price-matrix?id=matrix-2024
```

#### `products`
Opens the product catalog.

**Parameters:**
- `category` (optional): Product category
- `search` (optional): Search query

**Example:**
```
solarcalc://products?category=solar-panels&search=Trina
```

### 3D Visualization

#### `3d-view`
Opens the 3D visualization for a project.

**Parameters:**
- `project` (required): Project ID

**Example:**
```
solarcalc://3d-view?project=12345
```

### Email Integration

#### `email`
Opens email compose with pre-filled data.

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body
- `attachment`: Attachment ID

**Example:**
```
solarcalc://email?to=customer@example.com&subject=Solar%20Quote
```

#### `share-project`
Shares a project via email.

**Parameters:**
- `id` (required): Project ID
- `email` (optional): Recipient email

**Example:**
```
solarcalc://share-project?id=12345&email=customer@example.com
```

### Authentication

#### `login`
Opens the login page.

**Parameters:**
- `token` (optional): Authentication token
- `redirect` (optional): Redirect URL after login

**Example:**
```
solarcalc://login?redirect=/dashboard
```

#### `reset-password`
Opens password reset page.

**Parameters:**
- `token` (required): Reset token

**Example:**
```
solarcalc://reset-password?token=abc123xyz
```

#### `verify-email`
Verifies email address.

**Parameters:**
- `token` (required): Verification token

**Example:**
```
solarcalc://verify-email?token=verify123
```

## Usage Examples

### From Email

Include deep links in HTML emails:

```html
<p>View your solar project:</p>
<a href="solarcalc://open-project?id=12345">Open Project</a>

<p>Calculate your savings:</p>
<a href="solarcalc://solar-calculator?roofArea=50&location=Berlin">
  Calculate Now
</a>
```

### From Website

Add deep links to your website:

```html
<a href="solarcalc://dashboard">Launch Solar Calculator Pro</a>

<button onclick="window.location='solarcalc://new-project?type=solar'">
  Start New Project
</button>
```

### From Command Line

Launch the application with a deep link:

**Windows:**
```cmd
start solarcalc://dashboard
```

**macOS:**
```bash
open solarcalc://dashboard
```

**Linux:**
```bash
xdg-open solarcalc://dashboard
```

### Programmatic Generation

Generate deep links in your application:

```typescript
import { useDeepLink } from './hooks/useDeepLink';

const { generateDeepLink, copyDeepLinkToClipboard } = useDeepLink();

// Generate a link
const result = await generateDeepLink('open-project', { id: '12345' });
console.log(result.deepLink); // solarcalc://open-project?id=12345

// Copy to clipboard
await copyDeepLinkToClipboard('solar-calculator', {
  roofArea: '50',
  location: 'Berlin'
});
```

## Integration Scenarios

### Email Marketing

Send personalized project links to customers:

```typescript
const projectLink = await generateDeepLink('open-project', {
  id: customer.projectId
});

await sendEmail({
  to: customer.email,
  subject: 'Your Solar Project is Ready',
  body: `Click here to view your project: ${projectLink}`
});
```

### CRM Integration

Link from your CRM to specific customer records:

```typescript
const customerLink = await generateDeepLink('customer', {}, [customerId]);
// Result: solarcalc://customer/12345
```

### Website Integration

Add "Calculate Now" buttons that pre-fill data:

```html
<a href="solarcalc://solar-calculator?roofArea=50&roofType=flat&location=Berlin">
  Get Your Quote
</a>
```

### Mobile App Integration

Launch the desktop app from a mobile app:

```javascript
// React Native example
import { Linking } from 'react-native';

const openInDesktopApp = (projectId) => {
  const deepLink = `solarcalc://open-project?id=${projectId}`;
  Linking.openURL(deepLink);
};
```

### Automated Workflows

Trigger actions from automation tools:

```bash
# Cron job to open dashboard daily
0 9 * * * open solarcalc://dashboard
```

## Security Considerations

### Input Validation

All deep link parameters are validated before processing:

- Project IDs are verified to exist
- File paths are checked for validity
- Tokens are validated before use
- SQL injection and XSS prevention is applied

### Authentication

Some actions require authentication:

- Opening customer records
- Generating PDFs
- Accessing sensitive data

If the user is not authenticated, they will be redirected to the login page.

### URL Encoding

Always URL-encode parameters:

```typescript
const subject = 'Solar Quote for John Doe';
const encodedSubject = encodeURIComponent(subject);
const link = `solarcalc://email?subject=${encodedSubject}`;
```

### HTTPS Only

When generating deep links from web applications, ensure your website uses HTTPS to prevent man-in-the-middle attacks.

## Troubleshooting

### Protocol Not Registered

**Problem**: Deep links don't open the application.

**Solutions**:
1. Reinstall the application
2. Check if another application has claimed the protocol
3. Manually register the protocol (advanced users)

### Application Doesn't Focus

**Problem**: Application opens but doesn't come to foreground.

**Solutions**:
1. Check operating system permissions
2. Ensure only one instance is running
3. Try clicking the taskbar/dock icon

### Parameters Not Working

**Problem**: Deep link opens but parameters are ignored.

**Solutions**:
1. Check URL encoding
2. Verify parameter names match documentation
3. Check application logs for errors

### Testing Deep Links

Use the built-in test functionality:

```typescript
const { testDeepLink } = useDeepLink();
await testDeepLink('solarcalc://open-project?id=12345');
```

Or use the Deep Link Demo page in the application.

## Best Practices

1. **Always URL-encode parameters** to handle special characters
2. **Validate data** before generating deep links
3. **Provide fallbacks** for users without the app installed
4. **Use descriptive action names** for clarity
5. **Document your deep links** for other developers
6. **Test on all platforms** (Windows, macOS, Linux)
7. **Handle errors gracefully** when deep links fail
8. **Keep URLs short** when possible for better user experience

## API Reference

### React Hook: `useDeepLink()`

```typescript
const {
  generateDeepLink,
  copyDeepLinkToClipboard,
  testDeepLink,
  getRegisteredHandlers,
  isProtocolRegistered,
  isElectron
} = useDeepLink();
```

#### Methods

**`generateDeepLink(action, params, pathSegments)`**
- Returns: `Promise<DeepLinkResult>`
- Generates a deep link URL

**`copyDeepLinkToClipboard(action, params, pathSegments)`**
- Returns: `Promise<DeepLinkResult>`
- Generates and copies deep link to clipboard

**`testDeepLink(urlString)`**
- Returns: `Promise<{ success: boolean; error?: string }>`
- Tests a deep link URL

**`getRegisteredHandlers()`**
- Returns: `Promise<DeepLinkHandlers>`
- Gets list of registered action handlers

**`isProtocolRegistered()`**
- Returns: `Promise<DeepLinkStatus>`
- Checks if protocol is registered with OS

## Support

For issues or questions about deep linking:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Deep Link Demo](#) in the application
3. Contact support with deep link URL and error details
4. Check application logs for detailed error messages

## Version History

- **v1.0.0**: Initial deep linking implementation
  - Basic protocol registration
  - Core action handlers
  - React hook integration
  - Demo component

---

**Last Updated**: 2024
**Version**: 1.0.0
