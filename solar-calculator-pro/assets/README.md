# Application Assets

This directory contains all graphical assets required for building Solar Calculator Pro.

## Required Assets

### Application Icons

#### 1. Main Application Icon (`icon.ico`)

**Format**: ICO (Windows Icon)
**Required Resolutions**:
- 16x16 pixels
- 32x32 pixels
- 48x48 pixels
- 64x64 pixels
- 128x128 pixels
- 256x256 pixels

**Usage**: 
- Application icon in Windows
- Taskbar icon
- Window title bar icon
- Installer icon

**How to Create**:
1. Design a square logo (recommended: 512x512 or 1024x1024 PNG)
2. Use an online converter or tool to create multi-resolution ICO:
   - Online: https://icoconvert.com/
   - GIMP: Export as ICO with multiple sizes
   - ImageMagick: `convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico`

#### 2. File Association Icon (`file-icon.ico`)

**Format**: ICO (Windows Icon)
**Required Resolutions**: Same as main icon
**Usage**: Icon for `.scp` (Solar Calculator Project) files

**Design Tips**:
- Should be related to but distinct from main app icon
- Consider adding a document/file element to the design
- Use consistent color scheme with main icon

### Installer Graphics

#### 3. Installer Header (`installer-header.bmp`)

**Format**: BMP (24-bit)
**Size**: 150 pixels wide × 57 pixels high
**Usage**: Displayed at the top of installer pages

**Design Guidelines**:
- Use your brand colors
- Include company logo or app name
- Keep it simple and professional
- Avoid text that might be hard to read at small size

**Example Layout**:
```
┌─────────────────────────────────────────────┐
│  [Logo]  Solar Calculator Pro               │
└─────────────────────────────────────────────┘
```

#### 4. Installer Sidebar (`installer-sidebar.bmp`)

**Format**: BMP (24-bit)
**Size**: 164 pixels wide × 314 pixels high
**Usage**: Displayed on the left side of welcome and finish pages

**Design Guidelines**:
- Vertical orientation
- Use brand colors and imagery
- Can include:
  - Large app icon or logo
  - Product name
  - Tagline or key features
  - Decorative elements
- Ensure good contrast for readability

**Example Layout**:
```
┌──────────────┐
│              │
│   [Large     │
│    Logo]     │
│              │
│  Solar       │
│  Calculator  │
│  Pro         │
│              │
│  Professional│
│  Solar       │
│  Design      │
│  Software    │
│              │
└──────────────┘
```

## Creating Assets

### Method 1: Using Design Software

**Recommended Tools**:
- Adobe Photoshop
- Adobe Illustrator
- Figma (free)
- Inkscape (free)
- GIMP (free)

**Workflow**:
1. Design at high resolution (2048x2048 for icons)
2. Export to PNG
3. Convert PNG to ICO using tools mentioned above
4. Create BMP files at exact required dimensions

### Method 2: Using Online Tools

**Icon Converters**:
- https://icoconvert.com/
- https://convertio.co/png-ico/
- https://cloudconvert.com/png-to-ico

**Image Editors**:
- https://www.photopea.com/ (Photoshop alternative)
- https://pixlr.com/
- https://www.canva.com/

### Method 3: Using Command Line Tools

#### ImageMagick

Install ImageMagick: https://imagemagick.org/

```bash
# Create ICO from PNG
magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# Create BMP at specific size
magick convert source.png -resize 150x57! installer-header.bmp
magick convert source.png -resize 164x314! installer-sidebar.bmp
```

#### GIMP (Command Line)

```bash
# Convert to ICO
gimp -i -b '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "icon.png" "icon.png")))) (file-ico-save RUN-NONINTERACTIVE image (car (gimp-image-get-active-layer image)) "icon.ico" "icon.ico" 0)) (gimp-quit 0)'
```

## Asset Checklist

Before building, ensure you have:

- [ ] `icon.ico` - Main application icon (multi-resolution)
- [ ] `file-icon.ico` - File association icon (multi-resolution)
- [ ] `installer-header.bmp` - Installer header (150x57, 24-bit BMP)
- [ ] `installer-sidebar.bmp` - Installer sidebar (164x314, 24-bit BMP)

## Placeholder Assets

If you don't have final assets yet, you can use placeholder images:

### Creating Placeholder Icon

```bash
# Using ImageMagick
magick -size 256x256 xc:blue -fill white -pointsize 72 -gravity center -annotate +0+0 "SC" icon.png
magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

### Creating Placeholder BMP

```bash
# Header
magick -size 150x57 xc:lightblue -fill darkblue -pointsize 20 -gravity center -annotate +0+0 "Solar Calculator Pro" installer-header.bmp

# Sidebar
magick -size 164x314 xc:lightblue -fill darkblue -pointsize 24 -gravity center -annotate +0-50 "Solar\nCalculator\nPro" installer-sidebar.bmp
```

## Design Tips

### Icons

1. **Simplicity**: Icons should be recognizable at small sizes
2. **Consistency**: Use consistent style across all icons
3. **Color**: Use 2-3 main colors maximum
4. **Contrast**: Ensure good contrast for visibility
5. **Uniqueness**: Make your icon distinctive and memorable

### Installer Graphics

1. **Branding**: Maintain consistent brand identity
2. **Professionalism**: Use high-quality graphics
3. **Readability**: Ensure text is legible
4. **File Size**: Keep files reasonably small (< 1MB each)
5. **Testing**: Test on different Windows themes (light/dark)

## Color Schemes

### Suggested Color Palettes for Solar Applications

**Palette 1: Sunny**
- Primary: #FDB813 (Golden Yellow)
- Secondary: #FF6B35 (Orange)
- Accent: #004E89 (Deep Blue)

**Palette 2: Eco**
- Primary: #52B788 (Green)
- Secondary: #2D6A4F (Dark Green)
- Accent: #FFB703 (Amber)

**Palette 3: Professional**
- Primary: #0077B6 (Blue)
- Secondary: #023E8A (Navy)
- Accent: #90E0EF (Light Blue)

**Palette 4: Modern**
- Primary: #6C757D (Gray)
- Secondary: #495057 (Dark Gray)
- Accent: #FFC107 (Yellow)

## File Formats

### ICO (Icon)
- Multi-resolution container
- Supports transparency
- Windows native format
- Can contain multiple sizes in one file

### BMP (Bitmap)
- Uncompressed raster format
- 24-bit color depth required
- No transparency support
- Exact pixel dimensions required

## Validation

### Checking ICO Files

```bash
# Using ImageMagick
magick identify icon.ico

# Should show multiple resolutions:
# icon.ico[0] ICO 256x256 ...
# icon.ico[1] ICO 128x128 ...
# icon.ico[2] ICO 64x64 ...
# etc.
```

### Checking BMP Files

```bash
# Using ImageMagick
magick identify installer-header.bmp
# Should show: installer-header.bmp BMP 150x57 ...

magick identify installer-sidebar.bmp
# Should show: installer-sidebar.bmp BMP 164x314 ...
```

## Troubleshooting

### Icon Not Showing in Windows

1. Clear icon cache:
   ```cmd
   ie4uinit.exe -show
   ```

2. Rebuild icon cache:
   ```cmd
   ie4uinit.exe -ClearIconCache
   ```

3. Restart Windows Explorer:
   ```cmd
   taskkill /f /im explorer.exe
   start explorer.exe
   ```

### BMP Format Issues

- Ensure 24-bit color depth (not 32-bit)
- Use exact pixel dimensions
- Save without compression
- Avoid transparency (not supported in BMP)

### Build Errors

If you get errors about missing assets:

1. Check file names match exactly (case-sensitive)
2. Verify files are in correct directory
3. Ensure correct file formats
4. Check file permissions

## Resources

### Design Inspiration

- [Dribbble - App Icons](https://dribbble.com/tags/app_icon)
- [Behance - Icon Design](https://www.behance.net/search/projects?search=icon%20design)
- [IconFinder](https://www.iconfinder.com/)

### Tools

- [GIMP](https://www.gimp.org/) - Free image editor
- [Inkscape](https://inkscape.org/) - Free vector editor
- [ImageMagick](https://imagemagick.org/) - Command-line image processing
- [IcoFX](https://icofx.ro/) - Icon editor (paid)

### Tutorials

- [Creating Windows Icons](https://docs.microsoft.com/en-us/windows/apps/design/style/iconography/app-icon-design)
- [NSIS Installer Graphics](https://nsis.sourceforge.io/Docs/Modern%20UI%202/Readme.html)
- [Icon Design Best Practices](https://material.io/design/iconography/product-icons.html)

## Support

For questions about assets:
- Check the [Windows Build Guide](../docs/WINDOWS_BUILD_GUIDE.md)
- Open an issue on GitHub
- Contact: support@yourcompany.com

---

**Last Updated**: 2024
**Version**: 1.0.0
