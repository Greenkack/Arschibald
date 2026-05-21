# Solar Calculator Pro - Troubleshooting Guide

**Comprehensive solutions for common issues**

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Startup Problems](#startup-problems)
3. [Calculation Errors](#calculation-errors)
4. [Price Matrix Issues](#price-matrix-issues)
5. [PDF Generation Problems](#pdf-generation-problems)
6. [3D Visualization Issues](#3d-visualization-issues)
7. [Database Problems](#database-problems)
8. [Performance Issues](#performance-issues)
9. [Network and Connectivity](#network-and-connectivity)
10. [User Account Issues](#user-account-issues)
11. [Data Import/Export Problems](#data-importexport-problems)
12. [System Errors](#system-errors)

---

## Installation Issues

### Windows: "Installation Failed" Error

**Symptoms**: Installer shows error message and exits

**Possible Causes**:
- Insufficient permissions
- Antivirus blocking installation
- Corrupted installer file
- Insufficient disk space

**Solutions**:

1. **Run as Administrator**
   ```
   Right-click installer → Run as administrator
   ```

2. **Temporarily Disable Antivirus**
   - Disable antivirus temporarily
   - Run installer
   - Re-enable antivirus after installation

3. **Check Disk Space**
   - Need at least 1 GB free space
   - Clean up disk if needed
   - Try installing to different drive

4. **Re-download Installer**
   - Delete current installer
   - Clear browser cache
   - Download fresh copy
   - Verify file size matches expected

5. **Check Windows Version**
   - Requires Windows 10 or later
   - Update Windows if needed

### macOS: "App Can't Be Opened" Error

**Symptoms**: macOS blocks application from opening

**Solutions**:

1. **Allow in Security Settings**
   ```
   System Preferences → Security & Privacy
   → Click "Open Anyway"
   ```

2. **Remove Quarantine Attribute**
   ```bash
   xattr -d com.apple.quarantine /Applications/Solar\ Calculator\ Pro.app
   ```

3. **Check macOS Version**
   - Requires macOS 10.15 (Catalina) or later
   - Update macOS if needed

### Linux: Dependencies Missing

**Symptoms**: Application won't start, missing library errors

**Solutions**:

1. **Install Dependencies (Ubuntu/Debian)**
   ```bash
   sudo apt-get update
   sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1 \
        libxtst6 xdg-utils libatspi2.0-0 libdrm2 libgbm1 \
        libasound2
   ```

2. **Install Dependencies (Fedora/RHEL)**
   ```bash
   sudo dnf install gtk3 libnotify nss libXScrnSaver libXtst \
        xdg-utils at-spi2-atk libdrm mesa-libgbm alsa-lib
   ```

3. **Make AppImage Executable**
   ```bash
   chmod +x Solar-Calculator-Pro.AppImage
   ```

---

## Startup Problems

### Application Won't Start

**Symptoms**: Double-clicking icon does nothing, or application crashes immediately

**Diagnostic Steps**:

1. **Check if Backend is Running**
   - Windows: Open Task Manager, look for "python" or "backend" process
   - macOS: Open Activity Monitor, search for "python"
   - Linux: Run `ps aux | grep python`

2. **Check Log Files**
   - Windows: `C:\Users\[User]\AppData\Roaming\solar-calculator-pro\logs\`
   - macOS: `~/Library/Application Support/solar-calculator-pro/logs/`
   - Linux: `~/.config/solar-calculator-pro/logs/`
   - Look for `error.log` and `backend.log`

**Solutions**:

1. **Wait for Backend Startup**
   - Backend can take 20-30 seconds to start
   - Look for system tray icon
   - Wait for "Ready" notification

2. **Check Port Availability**
   - Backend uses port 8000
   - Check if another application is using it:
     ```bash
     # Windows
     netstat -ano | findstr :8000
     
     # macOS/Linux
     lsof -i :8000
     ```
   - Kill conflicting process or change port in settings

3. **Reset Configuration**
   - Rename config folder to backup:
     ```bash
     # Windows
     ren "%APPDATA%\solar-calculator-pro" "solar-calculator-pro.bak"
     
     # macOS
     mv ~/Library/Application\ Support/solar-calculator-pro \
        ~/Library/Application\ Support/solar-calculator-pro.bak
     
     # Linux
     mv ~/.config/solar-calculator-pro ~/.config/solar-calculator-pro.bak
     ```
   - Restart application (will create fresh config)

4. **Reinstall Application**
   - Uninstall completely
   - Delete config folder
   - Restart computer
   - Install fresh copy

### "Backend Connection Failed" Error

**Symptoms**: Application opens but shows connection error

**Solutions**:

1. **Wait and Retry**
   - Click "Retry" button
   - Wait 30 seconds between attempts
   - Backend may still be starting

2. **Check Firewall**
   - Windows: Allow app through Windows Firewall
   - macOS: System Preferences → Security → Firewall → Allow
   - Linux: Check iptables/ufw rules

3. **Check Antivirus**
   - Antivirus may be blocking backend
   - Add exception for Solar Calculator Pro
   - Temporarily disable to test

4. **Manual Backend Start** (Advanced)
   ```bash
   # Navigate to installation directory
   cd /path/to/solar-calculator-pro/backend
   
   # Start backend manually
   python main.py
   
   # Or with uvicorn
   uvicorn main:app --port 8000
   ```

### Slow Startup

**Symptoms**: Application takes several minutes to start

**Causes**:
- Large database
- Many projects
- Slow disk
- Insufficient RAM

**Solutions**:

1. **Optimize Database**
   - Once started: Admin → Database → Optimize
   - Rebuilds indexes
   - Cleans up old data

2. **Archive Old Projects**
   - Projects → Filter by old dates
   - Select projects
   - Change status to "Archived"
   - Archived projects load on-demand

3. **Increase RAM**
   - Close other applications
   - Upgrade RAM if possible (minimum 8GB recommended)

4. **Use SSD**
   - Install on SSD instead of HDD
   - Significantly improves startup time

---

## Calculation Errors

### "Price Matrix Not Found" Error

**Symptoms**: Calculation fails with price matrix error

**Solutions**:

1. **Upload Price Matrix**
   - Price Matrix → Upload
   - Select Excel file
   - Confirm upload

2. **Activate Matrix**
   - Price Matrix → Matrix List
   - Find uploaded matrix
   - Click "Activate"
   - Only one matrix can be active

3. **Verify Matrix Structure**
   - Column A must contain module counts
   - Row 1 must contain battery models
   - All prices must be numeric
   - Use German number format (1.234,56)

### "Invalid Module Count" Error

**Symptoms**: System rejects module count

**Causes**:
- Module count not in price matrix
- Roof area too small
- Module dimensions too large

**Solutions**:

1. **Check Price Matrix Coverage**
   - Price Matrix → Preview
   - Verify your module count is in Column A
   - Add missing counts if needed

2. **Adjust Roof Area**
   - Increase roof area if possible
   - Check measurements are correct
   - Consider different roof sections

3. **Try Different Module**
   - Select smaller module
   - Check module dimensions
   - Verify module fits on roof

### "Inverter Sizing Error" Error

**Symptoms**: Cannot find suitable inverter

**Causes**:
- System size outside inverter range
- No compatible inverters in database
- Inverter database not loaded

**Solutions**:

1. **Check System Size**
   - Very small systems: Use microinverters
   - Very large systems: Use multiple inverters
   - Adjust module count if needed

2. **Update Product Database**
   - Products → Inverters
   - Verify inverters are available
   - Import inverter data if missing

3. **Manual Inverter Selection**
   - Disable auto-selection
   - Manually choose inverter
   - System will validate compatibility

### Incorrect Production Estimates

**Symptoms**: Production numbers seem wrong

**Diagnostic**:

1. **Verify Input Data**
   - Check location is correct
   - Verify roof angle
   - Confirm orientation
   - Check for shading

2. **Check Module Specifications**
   - Verify module power rating
   - Check efficiency
   - Confirm module count

3. **Review Performance Ratio**
   - Default is 80%
   - Adjust in advanced settings if needed
   - Consider local conditions

**Solutions**:

1. **Correct Input Errors**
   - Fix any incorrect data
   - Recalculate

2. **Adjust Performance Ratio**
   - Settings → Calculations → Performance Ratio
   - Increase for optimal conditions
   - Decrease for poor conditions

3. **Add Shading Analysis**
   - Enable shading analysis
   - Mark shaded areas
   - System adjusts production

---

## Price Matrix Issues

### Matrix Upload Fails

**Symptoms**: Upload rejected with validation errors

**Common Errors and Solutions**:

1. **"Invalid Structure"**
   - Column A must be labeled (e.g., "Module Count")
   - Row 1 must be labeled (e.g., battery models)
   - No empty rows/columns in data area

2. **"Non-numeric Prices"**
   - All price cells must be numbers
   - Remove currency symbols (€, $)
   - Use German format: 1.234,56
   - No text in price cells

3. **"Duplicate Values"**
   - Module counts must be unique
   - Battery models must be unique
   - Check for hidden duplicates

4. **"Missing 'kein Speicher'"**
   - Last column must be "kein Speicher"
   - Exact spelling required
   - Case-sensitive

**Solutions**:

1. **Use Template**
   - Download template from Price Matrix page
   - Fill in your data
   - Maintains correct structure

2. **Validate in Excel**
   - Check for errors in Excel
   - Use Data Validation
   - Remove formatting

3. **Export and Re-import**
   - Export current matrix
   - Use as template
   - Modify and re-upload

### Price Lookup Returns Wrong Price

**Symptoms**: Calculation shows unexpected price

**Diagnostic Steps**:

1. **Check Active Matrix**
   - Price Matrix → Matrix List
   - Verify correct matrix is active
   - Check upload date

2. **Verify Lookup Values**
   - Note module count from calculation
   - Note battery selection
   - Manually find in matrix
   - Compare with system result

3. **Check for Extras**
   - Base price from matrix
   - Extras added separately
   - Review price breakdown

**Solutions**:

1. **Activate Correct Matrix**
   - Select intended matrix
   - Click "Activate"

2. **Update Matrix**
   - If prices are outdated
   - Upload new matrix
   - Activate new matrix

3. **Review Calculation**
   - Check all inputs
   - Verify selections
   - Review price breakdown

### Matrix Version Confusion

**Symptoms**: Unsure which matrix version is active

**Solutions**:

1. **Check Active Matrix**
   - Price Matrix → Matrix List
   - Active matrix highlighted
   - Shows activation date

2. **View Matrix History**
   - Select matrix
   - Click "History"
   - See all versions
   - Compare versions

3. **Restore Previous Version**
   - Matrix History → Select version
   - Click "Restore"
   - Confirm restoration

---

## PDF Generation Problems

### PDF Generation Fails

**Symptoms**: Error when generating PDF, or PDF is blank

**Solutions**:

1. **Check Disk Space**
   - Need at least 100MB free
   - Clean up disk if needed
   - Try different location

2. **Verify Data Complete**
   - All required fields filled
   - Calculation completed
   - Customer information present

3. **Try Different Template**
   - Some templates more complex
   - Try "Simple Report" template
   - Gradually add sections

4. **Check Logs**
   - Look in `logs/pdf-generation.log`
   - Find specific error
   - Search error in this guide

5. **Restart Application**
   - Close and reopen
   - Try generation again
   - May clear temporary issues

### Logo Not Appearing in PDF

**Symptoms**: PDF generated but logo missing

**Solutions**:

1. **Verify Logo Uploaded**
   - Settings → Branding → Logo
   - Check logo is uploaded
   - Preview logo

2. **Check File Format**
   - Supported: PNG, JPG, SVG
   - Convert if needed
   - Re-upload

3. **Check File Size**
   - Maximum 5MB
   - Compress if larger
   - Use online compression tool

4. **Verify Logo Position**
   - PDF Configuration → Branding
   - Check position is set
   - Try different position

5. **Clear Cache**
   - Settings → Advanced → Clear Cache
   - Restart application
   - Try again

### PDF Charts Not Displaying

**Symptoms**: Charts missing or showing as blank boxes

**Solutions**:

1. **Enable Charts in Template**
   - PDF Configuration → Content
   - Check "Include Charts"
   - Select which charts

2. **Verify Chart Data**
   - Charts need calculation data
   - Complete calculation first
   - Check results have data

3. **Reduce Chart Complexity**
   - Simplify chart settings
   - Reduce data points
   - Try different chart type

4. **Update Graphics Libraries**
   - May need system update
   - Check for app updates
   - Reinstall if persistent

### PDF Too Large

**Symptoms**: PDF file size is very large (>10MB)

**Solutions**:

1. **Reduce Image Quality**
   - PDF Configuration → Advanced
   - Set image quality to "Medium"
   - Reduces file size significantly

2. **Limit 3D Images**
   - 3D renders are large
   - Include only essential views
   - Reduce resolution

3. **Compress PDF**
   - Use PDF compression tool
   - Online: smallpdf.com, ilovepdf.com
   - Desktop: Adobe Acrobat

4. **Remove Unnecessary Sections**
   - Uncheck optional sections
   - Keep only essential content
   - Generate leaner PDF

---

## 3D Visualization Issues

### 3D View Won't Load

**Symptoms**: 3D viewer shows blank screen or loading forever

**Solutions**:

1. **Check WebGL Support**
   - Visit: get.webgl.org
   - Should show spinning cube
   - If not, update graphics drivers

2. **Update Graphics Drivers**
   - Windows: Device Manager → Display Adapters → Update
   - macOS: System Update
   - Linux: Update graphics packages

3. **Enable Hardware Acceleration**
   - Settings → Display → Hardware Acceleration
   - Enable if disabled
   - Restart application

4. **Reduce Quality Settings**
   - 3D Settings → Quality → Low
   - Disable shadows
   - Disable anti-aliasing
   - Try loading again

5. **Check System Requirements**
   - Minimum: Integrated graphics
   - Recommended: Dedicated GPU
   - RAM: 4GB minimum, 8GB recommended

### 3D View is Slow/Laggy

**Symptoms**: 3D view stutters, low frame rate

**Solutions**:

1. **Reduce Quality**
   - Lower quality setting
   - Disable shadows
   - Reduce module count for preview

2. **Close Other Applications**
   - Free up RAM
   - Free up GPU resources
   - Close browser tabs

3. **Update Drivers**
   - Latest graphics drivers
   - Can significantly improve performance

4. **Upgrade Hardware**
   - If persistent
   - Consider dedicated GPU
   - Increase RAM

### Module Placement Issues

**Symptoms**: Modules overlap, float, or won't place

**Solutions**:

1. **Reset Placement**
   - 3D View → Reset Placement
   - System recalculates
   - Uses automatic algorithm

2. **Manual Adjustment**
   - Enable Edit Mode
   - Drag modules to correct position
   - Rotate if needed
   - Save placement

3. **Check Collision Detection**
   - Settings → 3D → Collision Detection
   - Enable if disabled
   - Prevents overlaps

4. **Verify Roof Dimensions**
   - Check roof area is correct
   - Verify roof angle
   - Confirm module dimensions

### Export Fails

**Symptoms**: Cannot export 3D model

**Solutions**:

1. **Check Export Format**
   - Try different format
   - STL is most compatible
   - PNG for images

2. **Reduce Model Complexity**
   - Fewer modules
   - Lower quality
   - Simplify geometry

3. **Check Disk Space**
   - Need space for export file
   - Clean up if needed

4. **Try Different Location**
   - Export to different folder
   - Check folder permissions
   - Try desktop

---

## Database Problems

### "Database Locked" Error

**Symptoms**: Operations fail with database locked message

**Causes**:
- Another instance running
- Crashed process holding lock
- Antivirus scanning database

**Solutions**:

1. **Close Other Instances**
   - Check Task Manager/Activity Monitor
   - Close all Solar Calculator Pro instances
   - Wait 10 seconds
   - Try again

2. **Restart Application**
   - Close completely
   - Wait 30 seconds
   - Reopen

3. **Restart Computer**
   - If persistent
   - Clears all locks
   - Fresh start

4. **Restore from Backup** (Last Resort)
   - If database corrupted
   - Admin → Database → Restore
   - Select recent backup

### Database Corruption

**Symptoms**: Errors accessing data, missing projects, crashes

**Diagnostic**:

1. **Check Database Integrity**
   - Admin → Database → Check Integrity
   - Shows corruption status
   - Lists affected tables

**Solutions**:

1. **Repair Database**
   - Admin → Database → Repair
   - Attempts automatic repair
   - May take several minutes

2. **Restore from Backup**
   - Admin → Database → Restore
   - Select most recent backup
   - Verify data after restore

3. **Export and Reimport**
   - Export all data
   - Create new database
   - Import data
   - Rebuilds structure

### Slow Database Operations

**Symptoms**: Queries take long time, application sluggish

**Solutions**:

1. **Optimize Database**
   - Admin → Database → Optimize
   - Rebuilds indexes
   - Vacuums database
   - Run monthly

2. **Archive Old Data**
   - Archive completed projects
   - Delete old logs
   - Clean up history

3. **Check Disk Speed**
   - Use SSD if possible
   - Check disk health
   - Defragment if HDD

4. **Increase Cache**
   - Settings → Advanced → Database Cache
   - Increase cache size
   - Requires more RAM

---

## Performance Issues

### Application Running Slow

**Symptoms**: General sluggishness, delays in UI

**Diagnostic**:

1. **Check Resource Usage**
   - Task Manager/Activity Monitor
   - Check CPU usage
   - Check RAM usage
   - Check disk activity

**Solutions**:

1. **Close Unused Projects**
   - Close project tabs
   - Keep only active projects open
   - Reduces memory usage

2. **Clear Cache**
   - Settings → Advanced → Clear Cache
   - Clears temporary files
   - Frees up space

3. **Restart Application**
   - Close and reopen
   - Clears memory leaks
   - Fresh start

4. **Optimize Database**
   - See Database Problems section
   - Regular maintenance

5. **Upgrade Hardware**
   - More RAM (8GB minimum)
   - SSD instead of HDD
   - Better CPU

### High Memory Usage

**Symptoms**: Application using lots of RAM

**Normal Usage**:
- Idle: 200-400 MB
- Active: 400-800 MB
- With 3D: 800-1500 MB

**If Excessive (>2GB)**:

1. **Close 3D Viewers**
   - 3D views use most memory
   - Close when not needed

2. **Reduce Open Projects**
   - Each project uses memory
   - Close unused projects

3. **Clear Cache**
   - Settings → Advanced → Clear Cache

4. **Restart Application**
   - Clears memory leaks

5. **Report Bug**
   - If persistent
   - May be memory leak
   - Include diagnostic report

---

## Network and Connectivity

### Cannot Send Emails

**Symptoms**: Email sending fails

**Solutions**:

1. **Check Email Configuration**
   - Admin → Email Settings
   - Verify SMTP server
   - Check port (usually 587 or 465)
   - Verify username/password

2. **Test Connection**
   - Email Settings → Test Connection
   - Shows specific error
   - Follow error message

3. **Check Firewall**
   - Allow outbound SMTP
   - Port 587 or 465
   - Check antivirus

4. **Try Different SMTP**
   - Gmail, Outlook, etc.
   - Use app-specific password
   - Enable "less secure apps" if needed

### Update Check Fails

**Symptoms**: Cannot check for updates

**Solutions**:

1. **Check Internet Connection**
   - Verify internet works
   - Try browser

2. **Check Firewall**
   - Allow application internet access
   - Check proxy settings

3. **Manual Update**
   - Visit website
   - Download latest version
   - Install manually

---

## User Account Issues

### Forgot Password

**Solutions**:

1. **Reset Password**
   - Login screen → "Forgot Password"
   - Enter email
   - Follow reset link

2. **Admin Reset** (If you're admin)
   - Cannot reset own password
   - Need another admin
   - Or reinstall (loses data)

3. **Database Reset** (Last Resort)
   - Backup database first
   - Delete user table
   - Recreate admin account
   - Loses all users

### Cannot Login

**Symptoms**: Correct password rejected

**Solutions**:

1. **Check Caps Lock**
   - Passwords are case-sensitive
   - Check keyboard layout

2. **Clear Browser Cache** (Web version)
   - Clear cookies
   - Try incognito mode

3. **Check Account Status**
   - Account may be disabled
   - Contact admin

4. **Reset Password**
   - Use forgot password feature

---

## Data Import/Export Problems

### Import Fails

**Symptoms**: Import rejected with errors

**Solutions**:

1. **Check File Format**
   - Verify format matches selection
   - Excel: .xlsx
   - CSV: .csv
   - JSON: .json

2. **Validate Data**
   - Use provided template
   - Check required fields
   - Remove special characters

3. **Check File Size**
   - Maximum 100MB
   - Split large files
   - Import in batches

4. **Review Error Log**
   - Shows specific errors
   - Fix data accordingly
   - Retry import

### Export Incomplete

**Symptoms**: Export missing data

**Solutions**:

1. **Check Selection**
   - Verify all items selected
   - Check filters
   - Select "All"

2. **Check Export Options**
   - Include all fields
   - Include related data
   - Check format settings

3. **Try Different Format**
   - Excel vs CSV
   - JSON for complete data

---

## System Errors

### "Unexpected Error Occurred"

**Generic error message**

**Steps**:

1. **Check Error Log**
   - Find in logs folder
   - Note error code
   - Search in this guide

2. **Try Again**
   - May be temporary
   - Retry operation

3. **Restart Application**
   - Close completely
   - Reopen
   - Try again

4. **Report Bug**
   - If persistent
   - Include error log
   - Include steps to reproduce

### Application Crashes

**Symptoms**: Application closes unexpectedly

**Solutions**:

1. **Check Crash Logs**
   - logs/crash.log
   - Note error details

2. **Update Application**
   - May be known bug
   - Install latest version

3. **Check System Resources**
   - Sufficient RAM
   - Sufficient disk space
   - Not overheating

4. **Reinstall**
   - Backup data first
   - Uninstall completely
   - Install fresh copy

---

## Getting Additional Help

### Generating Diagnostic Report

1. Help → Generate Diagnostic Report
2. Save report file
3. Include when contacting support

### Contacting Support

**Email**: support@solarcalculatorpro.com

**Include**:
- Detailed problem description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots
- Diagnostic report
- Your contact information

**Response Time**: Within 24 hours (business days)

---

**Troubleshooting Guide v1.0** | **November 2025**  
*For more information, see the complete User Manual*
