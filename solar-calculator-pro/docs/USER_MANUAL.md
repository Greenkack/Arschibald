# Solar Calculator Pro - User Manual

**Version 1.0**  
**Last Updated: November 2025**

---

## Welcome to Solar Calculator Pro

Solar Calculator Pro is a comprehensive desktop application for designing, calculating, and managing solar energy systems, heat pump installations, and combined renewable energy solutions. This manual will guide you through all features and help you get the most out of the application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [First Launch](#first-launch)
4. [User Interface Overview](#user-interface-overview)
5. [Solar Calculator](#solar-calculator)
6. [Heat Pump Calculator](#heat-pump-calculator)
7. [Combined Systems](#combined-systems)
8. [Price Matrix Management](#price-matrix-management)
9. [PDF Generation](#pdf-generation)
10. [3D Visualization](#3d-visualization)
11. [Project Management](#project-management)
12. [CRM System](#crm-system)
13. [Product Database](#product-database)
14. [Admin Panel](#admin-panel)
15. [Settings and Preferences](#settings-and-preferences)
16. [Troubleshooting](#troubleshooting)
17. [Keyboard Shortcuts](#keyboard-shortcuts)
18. [FAQ](#faq)
19. [Support and Contact](#support-and-contact)

---

## Getting Started

### System Requirements

**Minimum Requirements:**
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- RAM: 4 GB
- Storage: 500 MB free space
- Display: 1280x720 resolution

**Recommended Requirements:**
- RAM: 8 GB or more
- Storage: 1 GB free space
- Display: 1920x1080 resolution or higher
- Graphics: Dedicated GPU for 3D visualization


## Installation

### Windows Installation

1. Download the `Solar-Calculator-Pro-Setup.exe` installer
2. Double-click the installer file
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\Solar Calculator Pro`)
   - Select whether to create desktop shortcut
   - Click "Install"
4. Wait for installation to complete
5. Click "Finish" to launch the application

### macOS Installation

1. Download the `Solar-Calculator-Pro.dmg` file
2. Double-click the DMG file to mount it
3. Drag the Solar Calculator Pro icon to the Applications folder
4. Eject the DMG
5. Open Applications folder and double-click Solar Calculator Pro
6. If prompted about security, go to System Preferences > Security & Privacy and click "Open Anyway"

### Linux Installation

**AppImage (Recommended):**
1. Download `Solar-Calculator-Pro.AppImage`
2. Make it executable: `chmod +x Solar-Calculator-Pro.AppImage`
3. Run: `./Solar-Calculator-Pro.AppImage`

**DEB Package (Debian/Ubuntu):**
1. Download `solar-calculator-pro.deb`
2. Install: `sudo dpkg -i solar-calculator-pro.deb`
3. Run from applications menu or terminal: `solar-calculator-pro`

---

## First Launch

### Initial Setup Wizard

When you first launch Solar Calculator Pro, you'll be guided through a setup wizard:

1. **Welcome Screen**: Click "Get Started"
2. **Language Selection**: Choose your preferred language (German/English)
3. **User Account**: Create your admin account
   - Username
   - Email
   - Password (minimum 8 characters)
4. **Company Information** (Optional):
   - Company name
   - Logo upload
   - Contact information
5. **Data Migration** (Optional): Import data from existing Streamlit installation
6. **Finish**: Click "Complete Setup" to start using the application


---

## User Interface Overview

### Main Window Layout

The application window consists of several key areas:

```
┌─────────────────────────────────────────────────────────┐
│  Header (Logo, User Menu, Notifications)               │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │         Main Content Area                    │
│ Menu     │                                              │
│          │                                              │
│          │                                              │
├──────────┴──────────────────────────────────────────────┤
│  Footer (Status, Version Info)                          │
└─────────────────────────────────────────────────────────┘
```

### Header

- **Logo**: Click to return to dashboard
- **Search Bar**: Global search across projects, customers, and products
- **Notifications**: Bell icon shows system notifications and alerts
- **User Menu**: Access profile, settings, and logout

### Sidebar Navigation

The sidebar provides quick access to all major features:

- **Dashboard**: Overview and quick actions
- **Solar Calculator**: Design solar PV systems
- **Heat Pump**: Calculate heat pump systems
- **Combined Systems**: Solar + Heat Pump integration
- **Price Matrix**: Manage pricing data
- **PDF Generation**: Create professional reports
- **3D Visualization**: View and export 3D models
- **Projects**: Manage all your projects
- **CRM**: Customer relationship management
- **Products**: Product database
- **Admin**: System administration (admin users only)
- **Settings**: User preferences and configuration

### Quick Actions

Use the floating action button (+ icon) in the bottom-right corner for quick access to:
- New Project
- New Customer
- New Calculation
- Upload Price Matrix


---

## Solar Calculator

### Overview

The Solar Calculator helps you design photovoltaic systems by calculating optimal system size, energy production, costs, and return on investment.

### Creating a New Solar Calculation

1. Click **Solar Calculator** in the sidebar
2. Click **New Calculation** button
3. Fill in the required information:

#### Step 1: Location and Building

- **Address**: Enter the installation address
- **Roof Type**: Select from:
  - Flat roof
  - Gable roof
  - Hip roof
  - Shed roof
- **Roof Area**: Enter available roof area in m²
- **Roof Angle**: Enter roof pitch in degrees (0-90°)
- **Orientation**: Select roof orientation (North, South, East, West, etc.)

#### Step 2: Energy Consumption

- **Annual Consumption**: Enter yearly electricity consumption in kWh
- **Consumption Profile**: Select typical usage pattern:
  - Residential
  - Commercial
  - Industrial
- **Peak Demand**: Enter maximum power demand in kW (optional)

#### Step 3: Module Selection

- **Module Type**: Choose from available PV modules
  - Filter by manufacturer, power rating, efficiency
  - View detailed specifications
- **Module Count**: System suggests optimal count, or enter manually
- **Module Orientation**: Portrait or Landscape

#### Step 4: Inverter Selection

- **Inverter Type**: String inverter or Microinverters
- **Inverter Model**: System suggests compatible models
- **Inverter Count**: Automatically calculated based on system size

#### Step 5: Battery Storage (Optional)

- **Add Battery**: Toggle to include battery storage
- **Battery Capacity**: Select capacity in kWh
- **Battery Model**: Choose from available models
- **Backup Power**: Enable for emergency power supply

#### Step 6: Additional Options

- **Mounting System**: Select mounting type
- **Monitoring System**: Include monitoring hardware
- **Warranty Extension**: Add extended warranty
- **Installation Services**: Include installation costs

### Viewing Results

After completing the form, click **Calculate** to see results:

**System Overview:**
- Total system size (kWp)
- Number of modules
- Expected annual production (kWh)
- Self-consumption rate (%)
- Grid feed-in (kWh)

**Financial Analysis:**
- Total system cost
- Available subsidies/incentives
- Net cost after incentives
- Annual savings
- Payback period (years)
- 25-year savings
- Return on investment (ROI)

**Environmental Impact:**
- CO₂ savings per year
- Equivalent trees planted
- Cars off the road equivalent

**Charts and Visualizations:**
- Monthly production forecast
- Energy flow diagram
- Cost breakdown
- Savings over time
- ROI timeline


### Saving and Managing Calculations

- **Save Project**: Click "Save" to store the calculation
- **Project Name**: Enter a descriptive name
- **Customer**: Link to existing customer or create new
- **Notes**: Add any relevant notes or comments
- **Tags**: Add tags for easy searching

### Comparing Scenarios

Create multiple calculation scenarios to compare options:

1. Save your first calculation
2. Click "Create Variant"
3. Modify parameters (e.g., different module type, battery size)
4. Save the variant
5. Click "Compare" to view side-by-side comparison

---

## Heat Pump Calculator

### Overview

The Heat Pump Calculator helps you design and analyze heat pump systems for heating and hot water.

### Creating a Heat Pump Calculation

1. Click **Heat Pump** in the sidebar
2. Click **New Calculation**

#### Step 1: Building Information

- **Building Type**: Residential, Commercial, Industrial
- **Building Age**: New construction, Renovated, Existing
- **Living Area**: Enter area in m²
- **Number of Floors**: Enter floor count
- **Insulation Quality**: Poor, Average, Good, Excellent
- **Window Quality**: Single, Double, Triple glazing

#### Step 2: Heating Requirements

- **Current Heating System**: Oil, Gas, Electric, Other
- **Annual Heating Consumption**: Enter in kWh or liters/m³
- **Hot Water Demand**: Number of occupants
- **Desired Indoor Temperature**: Enter in °C
- **Climate Zone**: Automatically detected from location

#### Step 3: Heat Pump Selection

- **Heat Pump Type**:
  - Air-to-Water
  - Ground-Source (Geothermal)
  - Water-to-Water
- **Heat Pump Model**: Choose from available models
- **Heating Capacity**: System suggests appropriate size
- **COP (Coefficient of Performance)**: Displayed for selected model

#### Step 4: Distribution System

- **Heating Distribution**:
  - Underfloor heating
  - Radiators
  - Fan coil units
- **Flow Temperature**: Enter required temperature
- **Buffer Tank**: Include buffer storage (optional)

#### Step 5: Dynamic Tariff (Optional)

- **Enable Dynamic Tariff**: Use time-of-use electricity pricing
- **Tariff Provider**: Select your electricity provider
- **Peak/Off-Peak Hours**: Configure time windows
- **Smart Control**: Enable intelligent heating scheduling

### Viewing Heat Pump Results

**System Performance:**
- Recommended heat pump size (kW)
- Annual heating demand (kWh)
- Seasonal Performance Factor (SPF)
- Annual electricity consumption
- Hot water production capacity

**Cost Analysis:**
- Heat pump system cost
- Installation costs
- Annual operating costs
- Comparison with current system
- Annual savings
- Payback period

**Environmental Benefits:**
- CO₂ reduction vs. current system
- Renewable energy percentage
- Primary energy savings


---

## Combined Systems

### Solar + Heat Pump Integration

Combine solar PV with heat pump for maximum efficiency and savings.

### Creating a Combined System Calculation

1. Click **Combined Systems** in the sidebar
2. Click **New Combined Calculation**
3. Complete both Solar and Heat Pump sections
4. System automatically calculates synergies

### Combined System Benefits

**Energy Synergy:**
- Use solar power to run heat pump
- Maximize self-consumption
- Reduce grid dependency
- Smart energy management

**Financial Benefits:**
- Combined system discounts
- Optimized sizing
- Maximum subsidy utilization
- Enhanced ROI

**Results Display:**
- Combined system overview
- Energy flow diagram
- Self-sufficiency rate
- Total cost and savings
- Comparison with separate systems
- Synergy benefits highlighted

---

## Price Matrix Management

### Overview

The Price Matrix system manages pricing for PV systems based on module count and battery storage selection.

### Understanding the Price Matrix

The price matrix uses an Excel-like structure:
- **Rows**: Number of PV modules (e.g., 10, 15, 20, 25...)
- **Columns**: Battery storage models (or "kein Speicher" for no storage)
- **Cells**: Turnkey system prices including everything

### Uploading a Price Matrix

1. Click **Price Matrix** in the sidebar
2. Click **Upload New Matrix**
3. Select file format:
   - Excel (.xlsx)
   - CSV (.csv)
   - JSON (.json)
4. Drag and drop file or click to browse
5. System validates the matrix structure
6. Review validation results
7. Click **Confirm Upload**

### Matrix Structure Requirements

**Column A (Rows)**: Module counts
- Must be numeric
- Must be in ascending order
- Example: 10, 15, 20, 25, 30...

**Row 1 (Columns)**: Battery models
- Text labels for battery models
- Last column should be "kein Speicher" (no storage)
- Example: "Battery 5kWh", "Battery 10kWh", "kein Speicher"

**Price Cells**:
- All prices in EUR
- German number format: 1.234,56
- Must be numeric values

### Viewing and Managing Matrices

**Matrix List:**
- View all uploaded matrices
- See upload date and status
- Active matrix is highlighted

**Matrix Preview:**
- View matrix data in table format
- Search and filter
- Export to Excel/CSV

**Matrix Activation:**
- Only one matrix can be active at a time
- Click "Activate" to make a matrix active
- Calculations use the active matrix

**Matrix History:**
- View previous versions
- Compare matrices
- Restore previous version


### Price Calculation Process

When you create a solar calculation:

1. System reads module count from your design
2. System reads battery selection (or "kein Speicher")
3. System looks up the intersection in the price matrix
4. Base price is retrieved
5. Additional costs are added:
   - Extra costs (Extrakosten)
   - Surcharges (Aufpreise)
   - Accessories (Zubehör)
   - Special products (Extras)
6. Discounts are applied:
   - Volume discounts (Rabatte)
   - Deductions (Nachlässe)
7. Final price is calculated and displayed

### Editing Matrix Data

1. Select a matrix from the list
2. Click **Edit**
3. Modify cells directly in the table
4. Changes are validated in real-time
5. Click **Save Changes**
6. System creates a new version

### Matrix Extras and Special Products

**Managing Extras:**
1. Go to **Price Matrix** > **Extras**
2. View list of available extras
3. Click **Add Extra** to create new
4. Enter:
   - Name
   - Description
   - Price
   - Applicable conditions
5. Save the extra

**Using Extras in Calculations:**
- Extras appear as checkboxes in calculation form
- Selected extras are added to base price
- Extras are itemized in results and PDF

---

## PDF Generation

### Overview

Generate professional PDF reports for your calculations and projects.

### Creating a PDF

1. Open a saved project or calculation
2. Click **Generate PDF** button
3. Configure PDF options

#### PDF Configuration Options

**Template Selection:**
- Standard Report
- Executive Summary
- Technical Specification
- Financial Analysis
- Custom Template

**Content Sections:**
Select which sections to include:
- ☑ Cover Page
- ☑ Executive Summary
- ☑ System Overview
- ☑ Technical Specifications
- ☑ Financial Analysis
- ☑ Environmental Impact
- ☑ 3D Visualization
- ☑ Charts and Graphs
- ☑ Terms and Conditions

**Branding:**
- Company Logo: Upload or select from library
- Logo Position: Top-left, Top-center, Top-right
- Color Scheme: Primary and secondary colors
- Font Selection: Choose from available fonts

**Custom Text:**
- Header Text: Appears on each page
- Footer Text: Contact information, disclaimers
- Cover Page Text: Custom introduction
- Closing Text: Call to action, next steps

**Language:**
- German (default)
- English
- Other languages (if configured)


### PDF Preview

Before generating the final PDF:

1. Click **Preview** to see how the PDF will look
2. Navigate through pages
3. Zoom in/out to check details
4. Make adjustments if needed
5. Click **Generate** when satisfied

### PDF Generation

1. Click **Generate PDF**
2. Wait for generation (progress bar shown)
3. PDF opens automatically when complete
4. Options appear:
   - **Download**: Save to your computer
   - **Email**: Send directly to customer
   - **Print**: Print the document
   - **Archive**: Save to project history

### PDF History

View all generated PDFs for a project:

1. Open project
2. Go to **PDF History** tab
3. See list of all PDFs with:
   - Generation date
   - Template used
   - File size
   - Download link
4. Click any PDF to view or download

### Email PDF

Send PDF directly to customer:

1. Click **Email** button
2. Enter recipient email (auto-filled from customer data)
3. Add CC/BCC if needed
4. Customize email subject and message
5. Click **Send**
6. Confirmation shown when sent

---

## 3D Visualization

### Overview

Visualize your solar installation in 3D to show customers exactly how the system will look.

### Opening 3D Visualization

1. Open a solar calculation
2. Click **3D View** button
3. 3D viewer loads with your system

### 3D Viewer Controls

**Mouse Controls:**
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Double Click**: Reset view

**Keyboard Controls:**
- **Arrow Keys**: Rotate view
- **+/-**: Zoom in/out
- **R**: Reset view
- **F**: Fit to screen
- **H**: Toggle help overlay

### 3D View Options

**Display Settings:**
- Show/Hide Modules
- Show/Hide Roof
- Show/Hide Mounting System
- Show/Hide Measurements
- Show/Hide Grid Lines
- Wireframe Mode
- Realistic Rendering

**Lighting:**
- Time of Day: Adjust sun position
- Shadows: Enable/disable shadows
- Ambient Light: Adjust brightness

**Camera Presets:**
- Front View
- Side View
- Top View
- Isometric View
- Custom View (save your own)


### Module Placement

**Automatic Placement:**
- System automatically places modules optimally
- Respects roof boundaries
- Avoids obstacles
- Maximizes module count

**Manual Adjustment:**
1. Click **Edit Placement** button
2. Click and drag modules to reposition
3. Rotate modules with rotation handle
4. Delete modules with Delete key
5. Add modules by clicking empty space
6. Click **Save** when done

**Placement Validation:**
- Red outline: Collision detected
- Yellow outline: Suboptimal placement
- Green outline: Valid placement
- Warnings shown for issues

### Exporting 3D Models

**Export Formats:**
- **Image (PNG/JPG)**: High-resolution screenshot
- **STL**: For 3D printing
- **OBJ**: For CAD software
- **GLTF**: For web viewing
- **PDF 3D**: Interactive 3D in PDF

**Export Options:**
1. Click **Export** button
2. Select format
3. Configure options:
   - Resolution (for images)
   - Include textures
   - Include measurements
   - File size optimization
4. Click **Export**
5. Choose save location

### 360° Animation

Create rotating animation for presentations:

1. Click **Create Animation**
2. Configure:
   - Duration (seconds)
   - Rotation speed
   - Start/end angles
   - Frame rate
3. Click **Generate**
4. Preview animation
5. Export as GIF or MP4

---

## Project Management

### Overview

Manage all your solar and heat pump projects in one place.

### Project List

View all projects with:
- Project name
- Customer name
- Project type (Solar, Heat Pump, Combined)
- Status (Draft, Active, Completed, Archived)
- Creation date
- Last modified date

**Filtering and Sorting:**
- Filter by status, type, customer
- Sort by date, name, status
- Search by project name or customer

### Creating a New Project

1. Click **Projects** in sidebar
2. Click **New Project**
3. Enter project details:
   - Project name
   - Customer (select existing or create new)
   - Project type
   - Description
   - Tags
4. Click **Create**
5. Project opens for editing

### Project Details

Each project contains:

**Overview Tab:**
- Project summary
- Key metrics
- Status
- Timeline
- Team members

**Calculations Tab:**
- All calculations for this project
- Create new calculations
- Compare scenarios

**Documents Tab:**
- Generated PDFs
- Uploaded documents
- Photos
- Technical drawings

**Notes Tab:**
- Project notes
- Meeting notes
- Action items
- History log

**Tasks Tab:**
- To-do list
- Assigned tasks
- Deadlines
- Completion status


### Project Status Workflow

Projects move through these statuses:

1. **Draft**: Initial creation, work in progress
2. **Active**: Sent to customer, awaiting decision
3. **Completed**: Customer accepted, project finished
4. **Archived**: Old projects, kept for reference

**Changing Status:**
- Click status dropdown in project header
- Select new status
- Add note explaining change (optional)
- Click **Update**

### Project Collaboration

**Team Members:**
- Add team members to project
- Assign roles (Owner, Editor, Viewer)
- Team members receive notifications
- Activity log tracks all changes

**Sharing Projects:**
- Generate share link
- Set expiration date
- Password protect (optional)
- Track views and downloads

---

## CRM System

### Overview

Manage customer relationships, track leads, and manage the sales pipeline.

### Customer Management

#### Customer List

View all customers with:
- Name and company
- Contact information
- Number of projects
- Total value
- Last contact date
- Status (Lead, Active, Inactive)

#### Adding a New Customer

1. Click **CRM** in sidebar
2. Click **New Customer**
3. Enter customer information:

**Basic Information:**
- First Name, Last Name
- Company Name
- Customer Type (Residential, Commercial, Industrial)

**Contact Information:**
- Email
- Phone
- Mobile
- Address

**Additional Details:**
- Source (How they found you)
- Assigned Sales Rep
- Tags
- Notes

4. Click **Save**

#### Customer Details

Each customer record contains:

**Overview Tab:**
- Contact information
- Quick stats
- Recent activity
- Upcoming tasks

**Projects Tab:**
- All projects for this customer
- Create new project
- Project history

**Communications Tab:**
- Email history
- Phone call logs
- Meeting notes
- Document sharing

**Tasks Tab:**
- Follow-up tasks
- Reminders
- Deadlines

**Notes Tab:**
- General notes
- Important information
- History


### Offer Management

#### Creating an Offer

1. Open customer record
2. Click **Create Offer**
3. Select project/calculation
4. Configure offer:
   - Validity period
   - Payment terms
   - Delivery time
   - Special conditions
5. Generate offer PDF
6. Send to customer

#### Offer Tracking

Track offer status:
- **Sent**: Offer sent to customer
- **Viewed**: Customer opened the offer
- **Under Review**: Customer reviewing
- **Accepted**: Customer accepted
- **Rejected**: Customer declined
- **Expired**: Validity period passed

#### Offer Versioning

- Create multiple versions of an offer
- Track changes between versions
- Compare versions side-by-side
- Revert to previous version

### Task Management

#### Creating Tasks

1. Click **Tasks** in CRM
2. Click **New Task**
3. Enter task details:
   - Title
   - Description
   - Due date
   - Priority (Low, Medium, High, Urgent)
   - Assigned to
   - Related customer/project
4. Click **Create**

#### Task Views

**My Tasks:**
- Tasks assigned to you
- Sorted by due date
- Filter by priority, status

**Team Tasks:**
- All team tasks
- Filter by assignee
- Calendar view available

**Overdue Tasks:**
- Tasks past due date
- Highlighted in red
- Automatic reminders sent

### Communication History

Track all customer communications:

**Email Integration:**
- Emails automatically logged
- Send emails from within app
- Email templates available
- Track opens and clicks

**Call Logging:**
- Log phone calls
- Record call duration
- Add call notes
- Set follow-up reminders

**Meeting Notes:**
- Record meeting details
- Attendees
- Discussion points
- Action items
- Next steps

---

## Product Database

### Overview

Manage your catalog of solar modules, inverters, batteries, heat pumps, and accessories.

### Product Categories

- **PV Modules**: Solar panels
- **Inverters**: String and micro inverters
- **Batteries**: Storage systems
- **Heat Pumps**: All types
- **Mounting Systems**: Rails, clamps, etc.
- **Accessories**: Cables, connectors, monitoring
- **Services**: Installation, maintenance


### Viewing Products

**Product List:**
- Browse all products
- Filter by category, manufacturer
- Search by name or specifications
- Sort by price, power, efficiency

**Product Details:**
- Technical specifications
- Images and datasheets
- Pricing information
- Availability status
- Related products
- Customer reviews

### Adding Products

1. Click **Products** in sidebar
2. Click **Add Product**
3. Enter product information:

**Basic Information:**
- Product name
- Manufacturer
- Model number
- Category
- Description

**Technical Specifications:**
- Power rating
- Efficiency
- Dimensions
- Weight
- Warranty period
- Certifications

**Pricing:**
- Purchase price
- Retail price
- Discount tiers
- Currency

**Images:**
- Upload product images
- Add datasheet PDF
- Add installation manual

4. Click **Save**

### Bulk Import

Import multiple products at once:

1. Click **Import Products**
2. Download template file
3. Fill in product data
4. Upload completed file
5. Review import preview
6. Confirm import

**Supported Formats:**
- Excel (.xlsx)
- CSV (.csv)
- JSON (.json)

### Product Comparison

Compare multiple products:

1. Select products (checkbox)
2. Click **Compare**
3. View side-by-side comparison
4. Export comparison as PDF

---

## Admin Panel

### Overview

System administration and configuration (admin users only).

### User Management

#### Managing Users

1. Click **Admin** > **Users**
2. View all users
3. Click user to edit

**User Roles:**
- **Admin**: Full system access
- **Manager**: Manage projects and users
- **Sales**: Create projects and customers
- **Viewer**: Read-only access

**User Permissions:**
- Customize permissions per user
- Grant/revoke specific features
- Set data access restrictions

#### Creating Users

1. Click **Add User**
2. Enter user details:
   - Username
   - Email
   - Password
   - Role
   - Permissions
3. Click **Create**
4. User receives welcome email


### System Settings

#### General Settings

- Company information
- Default language
- Date/time format
- Number format (German: 1.234,56)
- Currency
- Time zone

#### Email Configuration

- SMTP server settings
- Email templates
- Sender name and address
- Email signature
- Notification preferences

#### Backup Settings

- Automatic backup schedule
- Backup location
- Retention period
- Backup encryption
- Restore options

#### Logging Configuration

- Log level (Debug, Info, Warning, Error)
- Log retention
- Log file location
- Error reporting

### Database Management

#### Database Backup

1. Click **Admin** > **Database**
2. Click **Create Backup**
3. Enter backup name
4. Click **Backup Now**
5. Download backup file

**Automatic Backups:**
- Configure schedule (daily, weekly, monthly)
- Set retention period
- Email notifications

#### Database Restore

1. Click **Restore Database**
2. Select backup file
3. Review restore preview
4. Click **Restore**
5. System restarts with restored data

**Warning**: Restoring will overwrite current data!

#### Database Optimization

- Click **Optimize Database** to:
  - Rebuild indexes
  - Clean up old data
  - Vacuum database
  - Improve performance

### System Information

View system details:
- Application version
- Database version
- Backend status
- Disk space usage
- Memory usage
- Active users
- System uptime

---

## Settings and Preferences

### User Preferences

Access via User Menu > Settings

#### Profile Settings

- Update profile photo
- Change password
- Update email
- Set display name
- Configure signature

#### Display Preferences

**Theme:**
- Light mode
- Dark mode
- Auto (follows system)

**Language:**
- German (Deutsch)
- English
- Other languages

**Number Format:**
- German: 1.234,56
- International: 1,234.56

**Date Format:**
- DD.MM.YYYY (German)
- MM/DD/YYYY (US)
- YYYY-MM-DD (ISO)


#### Notification Preferences

Configure which notifications you receive:

**Email Notifications:**
- New customer inquiries
- Project status changes
- Task assignments
- Offer responses
- System updates

**Desktop Notifications:**
- Enable/disable desktop notifications
- Notification sound
- Notification duration

**In-App Notifications:**
- Show notification badge
- Notification center
- Mark as read

#### Default Values

Set default values for new calculations:
- Default module type
- Default inverter brand
- Default warranty period
- Default payment terms
- Default PDF template

#### Keyboard Shortcuts

Enable/disable keyboard shortcuts
Customize shortcut keys
View shortcut reference

---

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Windows:**
1. Check if backend process is running (Task Manager)
2. Try running as administrator
3. Check antivirus isn't blocking
4. Reinstall application

**macOS:**
1. Check Security & Privacy settings
2. Remove from quarantine: `xattr -d com.apple.quarantine /Applications/Solar\ Calculator\ Pro.app`
3. Reinstall application

**Linux:**
1. Check file permissions
2. Install missing dependencies
3. Check error logs: `~/.config/solar-calculator-pro/logs/`

#### Calculation Errors

**"Price matrix not found":**
- Upload a price matrix in Price Matrix section
- Activate the uploaded matrix
- Ensure matrix has correct structure

**"Invalid module count":**
- Check roof area is sufficient
- Verify module dimensions
- Adjust placement manually

**"Inverter sizing error":**
- System size may be too large/small for available inverters
- Try different module configuration
- Contact support for custom inverter options

#### PDF Generation Fails

1. Check disk space (need at least 100MB free)
2. Verify all required data is present
3. Try different PDF template
4. Check PDF generation logs
5. Restart application

#### 3D Visualization Not Loading

1. Update graphics drivers
2. Enable hardware acceleration in settings
3. Reduce 3D quality settings
4. Try different browser (if web version)
5. Check WebGL support


#### Data Import Issues

**"Invalid file format":**
- Check file extension matches selected format
- Verify file isn't corrupted
- Try exporting from source again
- Use provided template

**"Data validation failed":**
- Review validation errors
- Fix data according to requirements
- Check for special characters
- Ensure all required fields present

#### Performance Issues

**Application running slowly:**
1. Close unused projects
2. Clear cache (Settings > Advanced > Clear Cache)
3. Optimize database (Admin > Database > Optimize)
4. Check available RAM
5. Restart application

**Large PDF generation slow:**
- Reduce image quality in PDF settings
- Remove unnecessary sections
- Generate in background
- Upgrade hardware if persistent

### Error Messages

#### "Backend connection failed"

**Cause**: Cannot connect to Python backend service

**Solution**:
1. Wait 30 seconds for backend to start
2. Check firewall isn't blocking port 8000
3. Restart application
4. Check backend logs: `logs/backend.log`

#### "Database locked"

**Cause**: Another process is accessing database

**Solution**:
1. Close other instances of application
2. Wait a few seconds and retry
3. Restart application
4. If persistent, restore from backup

#### "Authentication failed"

**Cause**: Invalid credentials or session expired

**Solution**:
1. Check username and password
2. Clear browser cache (if web version)
3. Reset password if forgotten
4. Contact admin for account issues

### Getting Help

#### Log Files

Find log files for troubleshooting:

**Windows**: `C:\Users\[Username]\AppData\Roaming\solar-calculator-pro\logs\`
**macOS**: `~/Library/Application Support/solar-calculator-pro/logs/`
**Linux**: `~/.config/solar-calculator-pro/logs/`

**Log Files:**
- `application.log`: Main application log
- `backend.log`: Python backend log
- `error.log`: Error messages only
- `database.log`: Database operations

#### Diagnostic Information

Generate diagnostic report:
1. Go to Help > Generate Diagnostic Report
2. Report includes:
   - System information
   - Application version
   - Error logs
   - Configuration
3. Save report file
4. Send to support


---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New Project |
| `Ctrl/Cmd + S` | Save |
| `Ctrl/Cmd + P` | Print/Generate PDF |
| `Ctrl/Cmd + F` | Search |
| `Ctrl/Cmd + ,` | Settings |
| `Ctrl/Cmd + Q` | Quit Application |
| `F1` | Help |
| `F5` | Refresh |
| `Ctrl/Cmd + Z` | Undo |
| `Ctrl/Cmd + Y` | Redo |

### Navigation Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + 1` | Dashboard |
| `Ctrl/Cmd + 2` | Solar Calculator |
| `Ctrl/Cmd + 3` | Heat Pump |
| `Ctrl/Cmd + 4` | Projects |
| `Ctrl/Cmd + 5` | CRM |
| `Ctrl/Cmd + 6` | Products |
| `Alt + ←` | Go Back |
| `Alt + →` | Go Forward |
| `Ctrl/Cmd + H` | Home/Dashboard |

### Calculator Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Calculate |
| `Ctrl/Cmd + R` | Reset Form |
| `Ctrl/Cmd + D` | Duplicate Calculation |
| `Ctrl/Cmd + E` | Export Results |
| `Tab` | Next Field |
| `Shift + Tab` | Previous Field |

### 3D Viewer Shortcuts

| Shortcut | Action |
|----------|--------|
| `R` | Reset View |
| `F` | Fit to Screen |
| `H` | Toggle Help |
| `G` | Toggle Grid |
| `M` | Toggle Measurements |
| `W` | Wireframe Mode |
| `L` | Toggle Lighting |
| `Arrow Keys` | Rotate View |
| `+/-` | Zoom In/Out |
| `Space` | Play/Pause Animation |

### Text Editing Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + A` | Select All |
| `Ctrl/Cmd + C` | Copy |
| `Ctrl/Cmd + X` | Cut |
| `Ctrl/Cmd + V` | Paste |
| `Ctrl/Cmd + B` | Bold |
| `Ctrl/Cmd + I` | Italic |
| `Ctrl/Cmd + U` | Underline |

---

## FAQ

### General Questions

**Q: Can I use Solar Calculator Pro offline?**
A: Yes, the application works completely offline. Internet is only needed for:
- Software updates
- Weather data integration (optional)
- Email sending
- Cloud backup (optional)

**Q: How many projects can I create?**
A: Unlimited. There's no restriction on the number of projects, customers, or calculations.

**Q: Can multiple users work on the same project?**
A: Yes, with appropriate permissions. Changes are synchronized in real-time.

**Q: Is my data secure?**
A: Yes. All data is stored locally on your computer. Optional cloud backup is encrypted. Passwords are hashed using industry-standard bcrypt.


### Calculation Questions

**Q: How accurate are the solar production estimates?**
A: Estimates are based on industry-standard algorithms and historical weather data. Actual production may vary by ±10% depending on local conditions, shading, and system maintenance.

**Q: Can I customize the calculation formulas?**
A: Admins can adjust certain parameters in the admin panel. Core calculation algorithms cannot be modified to ensure accuracy and consistency.

**Q: Why doesn't my calculation match the price matrix exactly?**
A: The price matrix provides base prices. Final price includes:
- Selected extras and options
- Installation services
- Warranties
- Discounts
- Taxes (if applicable)

**Q: Can I import calculations from the old Streamlit version?**
A: Yes, use the migration tool (Admin > Data Migration) to import projects, customers, and calculations from Streamlit.

### Price Matrix Questions

**Q: What format should my price matrix be in?**
A: Excel (.xlsx) is recommended. The matrix should have:
- Column A: Module counts (numeric, ascending)
- Row 1: Battery models (text labels)
- Cells: Prices in German format (1.234,56)
- Last column: "kein Speicher" for no battery option

**Q: Can I have multiple price matrices?**
A: Yes, you can upload multiple matrices, but only one can be active at a time. Switch between matrices as needed.

**Q: How do I update prices without uploading a new matrix?**
A: Edit the active matrix directly (Price Matrix > Edit). Changes create a new version while preserving history.

**Q: What happens if a price is missing from the matrix?**
A: The system will show a warning and use interpolation or the nearest available price. It's best to ensure complete coverage.

### PDF Questions

**Q: Can I customize the PDF template?**
A: Yes, you can:
- Choose from built-in templates
- Customize colors, fonts, and logos
- Select which sections to include
- Create custom templates (contact support)

**Q: Why is my logo not appearing in the PDF?**
A: Check that:
- Logo file is uploaded (Settings > Branding)
- Logo format is supported (PNG, JPG, SVG)
- Logo file size is under 5MB
- Logo position is set correctly

**Q: Can I generate PDFs in multiple languages?**
A: Yes, select language in PDF configuration. Available languages depend on your installation.

### 3D Visualization Questions

**Q: Why is the 3D view not loading?**
A: Ensure:
- Graphics drivers are up to date
- Hardware acceleration is enabled
- WebGL is supported (check: get.webgl.org)
- Sufficient RAM available (minimum 4GB)

**Q: Can I export the 3D model for use in other software?**
A: Yes, export formats include:
- STL (3D printing, CAD)
- OBJ (3D modeling software)
- GLTF (web, AR/VR)
- Images (PNG, JPG)

**Q: How do I create a presentation animation?**
A: Use the 360° animation feature:
1. Open 3D view
2. Click "Create Animation"
3. Configure rotation and duration
4. Export as GIF or MP4


### CRM Questions

**Q: Can I import customers from another system?**
A: Yes, use the import function (CRM > Import). Supported formats:
- Excel (.xlsx)
- CSV (.csv)
- vCard (.vcf)
- JSON (.json)

**Q: How do I track email communications?**
A: Configure email integration (Admin > Email Settings). Once configured, all emails sent through the app are automatically logged to customer records.

**Q: Can I set up automatic follow-up reminders?**
A: Yes, when creating a task or logging communication, set a follow-up date. You'll receive a notification when it's due.

**Q: How do I generate sales reports?**
A: Go to CRM > Reports, select report type (sales pipeline, conversion rates, etc.), set date range, and generate.

### Technical Questions

**Q: What database does the application use?**
A: SQLite by default (local file-based). Enterprise versions support PostgreSQL and MySQL.

**Q: Can I access the application from multiple computers?**
A: Each installation is independent. For multi-computer access, consider:
- Network database (enterprise feature)
- Cloud sync (enterprise feature)
- Export/import projects between installations

**Q: How do I update the application?**
A: Updates are automatic. When an update is available:
1. Notification appears
2. Click "Download Update"
3. Update downloads in background
4. Restart application to install

**Q: Can I run this on a server for multiple users?**
A: The desktop version is single-user. For multi-user deployment, contact us about the enterprise server version.

**Q: What ports does the application use?**
A: Internal communication uses:
- Port 8000: Backend API (localhost only)
- Port 3000: Frontend (localhost only)
These ports are not exposed externally.

---

## Support and Contact

### Getting Support

**Documentation:**
- User Manual (this document)
- Video Tutorials: [Link to video library]
- Knowledge Base: [Link to knowledge base]
- API Documentation: [Link to API docs]

**Community:**
- User Forum: [Link to forum]
- FAQ: See FAQ section above
- Feature Requests: [Link to feature request portal]

**Technical Support:**
- Email: support@solarcalculatorpro.com
- Phone: +49 (0) 123 456 789
- Hours: Monday-Friday, 9:00-17:00 CET
- Response Time: Within 24 hours

**Emergency Support:**
- Critical issues: emergency@solarcalculatorpro.com
- Available 24/7 for enterprise customers

### Reporting Bugs

When reporting a bug, please include:
1. Detailed description of the issue
2. Steps to reproduce
3. Expected vs. actual behavior
4. Screenshots or screen recording
5. Diagnostic report (Help > Generate Diagnostic Report)
6. Your contact information

Submit bug reports:
- Email: bugs@solarcalculatorpro.com
- Bug Tracker: [Link to bug tracker]


### Feature Requests

Have an idea for a new feature?
1. Check if it's already requested in the feature portal
2. Vote for existing requests
3. Submit new request with:
   - Feature description
   - Use case
   - Expected benefit
   - Priority (nice-to-have vs. critical)

### Training and Onboarding

**Self-Paced Learning:**
- Video tutorial series
- Interactive demos
- Sample projects
- Practice exercises

**Live Training:**
- Webinars (monthly)
- One-on-one training sessions
- Team training (on-site or remote)
- Custom training programs

**Certification:**
- Solar Calculator Pro Certified User
- Advanced Features Certification
- Admin Certification

Contact training@solarcalculatorpro.com for details.

### Updates and Releases

**Release Schedule:**
- Major releases: Quarterly
- Minor updates: Monthly
- Security patches: As needed

**Release Notes:**
- View in-app: Help > Release Notes
- Website: [Link to release notes]
- Email notifications for major releases

**Beta Program:**
- Test new features early
- Provide feedback
- Influence development
- Join: beta@solarcalculatorpro.com

### Social Media and Community

Stay connected:
- Twitter: @SolarCalcPro
- LinkedIn: Solar Calculator Pro
- YouTube: Solar Calculator Pro Channel
- Newsletter: Subscribe at [website]

### Legal and Compliance

**License Agreement:**
- View: Help > License Agreement
- One license per installation
- Enterprise licenses available

**Privacy Policy:**
- View: Help > Privacy Policy
- GDPR compliant
- Data stored locally by default

**Terms of Service:**
- View: Help > Terms of Service

**Data Protection:**
- All data encrypted at rest
- Optional cloud backup encrypted in transit
- No data shared with third parties
- Full data export available

---

## Appendix A: Glossary

**3D Visualization**: Three-dimensional representation of solar installation on roof

**Battery Storage**: Energy storage system for storing excess solar production

**COP (Coefficient of Performance)**: Efficiency rating for heat pumps

**CRM**: Customer Relationship Management system

**Feed-in Tariff**: Payment received for electricity fed into the grid

**Heat Pump**: Device that transfers heat from outside to inside for heating

**Inverter**: Device that converts DC power from solar panels to AC power

**kWh (Kilowatt-hour)**: Unit of energy (1000 watts for one hour)

**kWp (Kilowatt-peak)**: Maximum power output of solar system under standard conditions

**Module**: Solar panel/photovoltaic panel

**NPV (Net Present Value)**: Financial metric for investment analysis

**PDF**: Portable Document Format for reports

**Price Matrix**: Table of system prices based on size and options

**PV (Photovoltaic)**: Technology that converts sunlight to electricity

**ROI (Return on Investment)**: Profitability measure

**Self-Consumption**: Percentage of solar production used directly

**SPF (Seasonal Performance Factor)**: Annual efficiency of heat pump

**Turnkey Price**: Complete system price including all components and installation

---

## Appendix B: Technical Specifications

**Supported File Formats:**

*Import:*
- Excel: .xlsx, .xls
- CSV: .csv
- JSON: .json
- Images: .jpg, .png, .gif, .svg
- Documents: .pdf
- 3D Models: .stl, .obj, .gltf

*Export:*
- PDF: .pdf
- Excel: .xlsx
- CSV: .csv
- Images: .png, .jpg
- 3D Models: .stl, .obj, .gltf, .glb
- Animations: .gif, .mp4

**Database:**
- Type: SQLite (default), PostgreSQL, MySQL (enterprise)
- Max size: Limited by disk space
- Backup format: .db, .sql

**API:**
- Protocol: REST API over HTTP
- Format: JSON
- Authentication: JWT tokens
- Documentation: OpenAPI/Swagger

**System Limits:**
- Max projects: Unlimited
- Max customers: Unlimited
- Max calculations per project: Unlimited
- Max file upload size: 100 MB
- Max PDF size: 50 MB
- Max 3D model complexity: 1 million polygons

---

## Appendix C: Calculation Methodology

### Solar Production Calculation

Production estimates based on:
- Module specifications (power, efficiency)
- Location (latitude, longitude)
- Historical weather data (irradiation)
- Roof parameters (angle, orientation)
- System losses (inverter, cables, soiling)
- Shading analysis (if applicable)

**Formula:**
```
Annual Production (kWh) = System Size (kWp) × Peak Sun Hours × Performance Ratio
```

**Performance Ratio**: Typically 75-85%, accounts for:
- Inverter efficiency: ~96-98%
- Cable losses: ~2%
- Temperature losses: ~5-10%
- Soiling: ~2-5%
- Mismatch: ~1-2%

### Financial Calculations

**Payback Period:**
```
Payback Period = Net System Cost / Annual Savings
```

**ROI (25 years):**
```
ROI = (Total Savings - Net Cost) / Net Cost × 100%
```

**NPV (Net Present Value):**
```
NPV = Σ (Cash Flow / (1 + Discount Rate)^Year) - Initial Investment
```

### Heat Pump Sizing

**Heating Load Calculation:**
```
Heating Load (kW) = Building Area × Specific Heat Loss × Temperature Difference
```

**COP Calculation:**
```
COP = Heat Output / Electrical Input
```

**Annual Electricity Consumption:**
```
Consumption (kWh) = Annual Heating Demand (kWh) / SPF
```

---

**End of User Manual**

*For the latest version of this manual, visit: [website]*

*Last updated: November 2025*
*Version: 1.0*
*© 2025 Solar Calculator Pro. All rights reserved.*
