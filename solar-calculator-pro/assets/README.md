# Application Icons

This directory contains the application icons for the Solar Calculator Pro desktop application.

## Required Icon Files

### 1. Main Application Icon
**File:** `icon.png`
- **Size:** 512x512 pixels
- **Format:** PNG with transparency
- **Usage:** Main application icon, used in various contexts

### 2. Windows Icon
**File:** `icon.ico`
- **Sizes:** Multiple sizes embedded (16x16, 32x32, 48x48, 256x256)
- **Format:** ICO
- **Usage:** Windows application icon, taskbar, file associations

### 3. macOS Icon
**File:** `icon.icns`
- **Sizes:** Multiple sizes embedded (16x16 to 1024x1024)
- **Format:** ICNS
- **Usage:** macOS application icon, dock, Finder

### 4. System Tray Icon
**File:** `tray-icon.png`
- **Size:** 22x22 pixels (macOS) or 16x16 pixels (Windows/Linux)
- **Format:** PNG with transparency
- **Usage:** System tray/notification area icon
- **Note:** Should be simple and recognizable at small sizes

## Creating Icons

### From a Single Source Image

If you have a single high-resolution image (e.g., 1024x1024), you can create all required formats:

#### Using Online Tools
1. **PNG to ICO:** https://convertio.co/png-ico/
2. **PNG to ICNS:** https://cloudconvert.com/png-to-icns
3. **Image Resizer:** https://www.iloveimg.com/resize-image

#### Using Command Line Tools

**ImageMagick (Cross-platform):**
```bash
# Install ImageMagick
# Windows: choco install imagemagick
# macOS: brew install imagemagick
# Linux: sudo apt-get install imagemagick

# Create main icon
convert source.png -resize 512x512 icon.png

# Create tray icon
convert source.png -resize 22x22 tray-icon.png

# Create Windows ICO (multiple sizes)
convert source.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

**iconutil (macOS only for ICNS):**
```bash
# Create iconset directory
mkdir icon.iconset

# Create all required sizes
sips -z 16 16     source.png --out icon.iconset/icon_16x16.png
sips -z 32 32     source.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     source.png --out icon.iconset/icon_32x32.png
sips -z 64 64     source.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   source.png --out icon.iconset/icon_128x128.png
sips -z 256 256   source.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   source.png --out icon.iconset/icon_256x256.png
sips -z 512 512   source.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   source.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 source.png --out icon.iconset/icon_512x512@2x.png

# Create ICNS file
iconutil -c icns icon.iconset
```

### Design Guidelines

#### Main Application Icon
- Use your brand colors
- Keep it simple and recognizable
- Should work well at both large and small sizes
- Include a subtle shadow or depth for 3D effect
- Consider using a sun symbol for solar calculator theme

#### Tray Icon
- Must be simple and clear at 16x16 or 22x22 pixels
- Use high contrast
- Avoid fine details
- Consider monochrome or simple two-color design
- Should be recognizable even when very small

### Example Icon Concepts

**Solar Calculator Theme:**
- Sun icon with rays
- Solar panel symbol
- Sun + calculator combination
- Energy/lightning bolt symbol
- House with solar panels

**Color Schemes:**
- Primary: Orange/Yellow (sun)
- Secondary: Blue (sky/energy)
- Accent: Green (eco-friendly)

## Placeholder Icons

If you don't have custom icons yet, you can use placeholder icons:

### Create Simple Placeholder (Node.js)
```javascript
// create-placeholder-icons.js
const { createCanvas } = require('canvas');
const fs = require('fs');

function createPlaceholderIcon(size, filename) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');
  
  // Background
  ctx.fillStyle = '#FF9800';
  ctx.fillRect(0, 0, size, size);
  
  // Sun symbol
  ctx.fillStyle = '#FFF';
  ctx.beginPath();
  ctx.arc(size/2, size/2, size/3, 0, Math.PI * 2);
  ctx.fill();
  
  // Save
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(filename, buffer);
}

createPlaceholderIcon(512, 'icon.png');
createPlaceholderIcon(22, 'tray-icon.png');
```

## Verification

After creating your icons, verify they work:

1. **Check file sizes:**
   ```bash
   ls -lh icon.png icon.ico icon.icns tray-icon.png
   ```

2. **Preview icons:**
   - Windows: Right-click → Properties
   - macOS: Quick Look (Space bar)
   - Linux: File manager preview

3. **Test in application:**
   ```bash
   npm run electron:dev
   ```
   - Check taskbar/dock icon
   - Check system tray icon
   - Check window icon

## Troubleshooting

### Icon Not Showing
- Verify file exists in `assets/` directory
- Check file permissions (should be readable)
- Clear icon cache (Windows: restart Explorer, macOS: restart Dock)
- Rebuild application: `npm run electron:build`

### Icon Looks Blurry
- Ensure source image is high resolution (at least 512x512)
- Use PNG format with transparency
- Don't upscale small images

### Tray Icon Not Visible
- Check icon size (should be 16x16 or 22x22)
- Use high contrast colors
- Test on both light and dark system themes
- Consider creating separate icons for light/dark themes

## Resources

- [Electron Icon Requirements](https://www.electronjs.org/docs/latest/tutorial/application-distribution#icons)
- [macOS Icon Guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Windows Icon Guidelines](https://docs.microsoft.com/en-us/windows/apps/design/style/iconography/app-icon-design)
- [Icon Design Best Practices](https://www.smashingmagazine.com/2016/05/easy-steps-to-better-logo-design/)

## Current Status

- [ ] icon.png (512x512)
- [ ] icon.ico (Windows)
- [ ] icon.icns (macOS)
- [ ] tray-icon.png (16x16 or 22x22)

Once all icons are created, check the boxes above and commit them to the repository.
