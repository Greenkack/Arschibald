# Deep Linking Quick Reference

## Protocol

```
solarcalc://
```

## Common Actions

| Action | Description | Example |
|--------|-------------|---------|
| `open-project` | Open project by ID | `solarcalc://open-project?id=12345` |
| `solar-calculator` | Open solar calculator | `solarcalc://solar-calculator?roofArea=50` |
| `heat-pump` | Open heat pump calculator | `solarcalc://heat-pump?buildingArea=150` |
| `customer` | Open customer record | `solarcalc://customer?id=67890` |
| `offer` | Open offer | `solarcalc://offer?id=54321` |
| `generate-pdf` | Generate PDF | `solarcalc://generate-pdf?project=12345` |
| `dashboard` | Open dashboard | `solarcalc://dashboard` |
| `settings` | Open settings | `solarcalc://settings?section=notifications` |
| `3d-view` | Open 3D visualization | `solarcalc://3d-view?project=12345` |
| `email` | Compose email | `solarcalc://email?to=user@example.com` |

## React Hook Usage

```typescript
import { useDeepLink } from './hooks/useDeepLink';

const { generateDeepLink, copyDeepLinkToClipboard } = useDeepLink();

// Generate link
const result = await generateDeepLink('open-project', { id: '12345' });

// Copy to clipboard
await copyDeepLinkToClipboard('solar-calculator', { roofArea: '50' });
```

## HTML Usage

```html
<a href="solarcalc://open-project?id=12345">Open Project</a>
```

## Command Line

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

## URL Encoding

Always encode special characters:

```typescript
const subject = 'Solar Quote';
const encoded = encodeURIComponent(subject);
const link = `solarcalc://email?subject=${encoded}`;
```

## Testing

```typescript
const { testDeepLink } = useDeepLink();
await testDeepLink('solarcalc://open-project?id=12345');
```

## Security

- All parameters are validated
- Authentication required for sensitive actions
- SQL injection and XSS prevention applied
- Use HTTPS when generating links from web

## Troubleshooting

1. **Protocol not registered**: Reinstall application
2. **Parameters ignored**: Check URL encoding
3. **App doesn't focus**: Check OS permissions

## Support

- View Deep Link Demo in application
- Check application logs
- Contact support with deep link URL and error details
