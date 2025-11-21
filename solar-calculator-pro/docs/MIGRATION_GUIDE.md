# Migration Guide: Streamlit to Electron Application

## Table of Contents

1. [Overview](#overview)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Migration Process](#migration-process)
4. [Data Migration Details](#data-migration-details)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)
7. [Post-Migration Validation](#post-migration-validation)
8. [FAQ](#faq)

## Overview

This guide provides comprehensive instructions for migrating from the Streamlit-based application to the new Electron desktop application. The migration process preserves all your data, settings, and configurations while upgrading to a modern desktop experience.

### What Gets Migrated

- **Databases** (Requirement 5.1): All SQLite databases including product catalogs, CRM data, and project information
- **Settings** (Requirement 5.2): Application preferences, themes, and configurations
- **Project Data** (Requirement 5.3): Solar calculations, heat pump projects, and 3D visualizations
- **User Data** (Requirement 5.4): User accounts, roles, permissions, and preferences
- **Files**: PDF templates, uploaded documents, and attachments

### Migration Methods

1. **Automatic Migration** (Recommended): Use the built-in migration wizard
2. **Manual Migration**: Use command-line tools for advanced scenarios
3. **Selective Migration**: Migrate specific components only

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Disk Space**: 2x the size of your current data (for backup and migration)
- **RAM**: Minimum 4GB, recommended 8GB
- **Permissions**: Administrator/root access for installation
- **Python**: 3.10+ (for backend migration tools)



## Pre-Migration Checklist

### Essential Steps

#### 1. Backup Your Data (CRITICAL)

**Before starting migration, create a complete backup:**

```bash
# Windows
xcopy /E /I /H "C:\path\to\streamlit\data" "C:\backup\streamlit_backup"

# macOS/Linux
cp -R /path/to/streamlit/data /backup/streamlit_backup
```

**What to backup:**
- [ ] All database files (*.db)
- [ ] Settings and configuration files
- [ ] Project data directories
- [ ] User data and profiles
- [ ] Uploaded files and attachments
- [ ] PDF templates
- [ ] Custom themes

#### 2. Verify Data Integrity

**Check your current data:**

```bash
# Run integrity check
python verify_data_integrity.py --path /path/to/streamlit/data
```

**Verify:**
- [ ] All databases open without errors
- [ ] No corrupted files
- [ ] All required files present
- [ ] Sufficient disk space available

#### 3. Stop Streamlit Application

**Ensure the Streamlit app is not running:**

```bash
# Check for running processes
# Windows
tasklist | findstr streamlit

# macOS/Linux
ps aux | grep streamlit

# Stop if running
# Windows
taskkill /F /IM streamlit.exe

# macOS/Linux
pkill -f streamlit
```



#### 4. System Preparation

**Prepare your system:**

- [ ] Close all unnecessary applications
- [ ] Disable antivirus temporarily (if causing issues)
- [ ] Ensure stable power supply (laptops: plug in)
- [ ] Disable sleep/hibernation during migration
- [ ] Have administrator/root access ready

#### 5. Install New Application

**Install the Electron application:**

```bash
# Windows
solar-calculator-pro-setup.exe

# macOS
open solar-calculator-pro.dmg

# Linux
sudo dpkg -i solar-calculator-pro.deb
# or
chmod +x solar-calculator-pro.AppImage
./solar-calculator-pro.AppImage
```

#### 6. Locate Data Paths

**Find your Streamlit data location:**

**Common locations:**
- Windows: `C:\Users\<username>\AppData\Local\SolarCalculator`
- macOS: `~/Library/Application Support/SolarCalculator`
- Linux: `~/.local/share/SolarCalculator`

**Verify data location:**
```bash
# Check Streamlit config
cat ~/.streamlit/config.toml | grep dataDir
```

### Pre-Migration Checklist Summary

Print this checklist and mark each item:

```
☐ Complete backup created
☐ Backup verified and accessible
☐ Data integrity checked
☐ Streamlit application stopped
☐ Sufficient disk space (2x current data size)
☐ Administrator access available
☐ New application installed
☐ Data paths identified
☐ System prepared (power, sleep disabled)
☐ Migration time scheduled (allow 30-60 minutes)
```



## Migration Process

### Method 1: Automatic Migration (Recommended)

#### Step 1: Launch Migration Wizard

1. Open the new Electron application
2. On first launch, you'll see the migration wizard
3. Or navigate to: **Settings → Migration → Start Migration**

#### Step 2: Configure Migration

**Source Path:**
- Click "Browse" to select your Streamlit data directory
- Or enter path manually: `/path/to/streamlit/data`

**Target Path:**
- Default: Application data directory (recommended)
- Custom: Choose a different location if needed

**Options:**
- ☑ Create backup before migration (RECOMMENDED)
- ☑ Validate data after migration (RECOMMENDED)
- ☐ Migrate settings only (for testing)
- ☐ Skip large files (>100MB)

#### Step 3: Review Migration Plan

The wizard will analyze your data and show:
- Total data size
- Estimated migration time
- Number of databases, projects, users
- Potential issues or warnings

**Review carefully:**
- Verify source path is correct
- Check estimated time
- Note any warnings
- Ensure sufficient disk space

#### Step 4: Execute Migration

Click "Start Migration" and monitor progress:

**Phase 1: Backup (5-10 minutes)**
- Creating backup of source data
- Verifying backup integrity

**Phase 2: Database Migration (10-20 minutes)**
- Migrating SQLite databases
- Converting schema if needed
- Copying all records

**Phase 3: Settings Migration (2-5 minutes)**
- Converting configuration files
- Migrating user preferences
- Updating theme settings

**Phase 4: Project Data Migration (5-15 minutes)**
- Copying project files
- Migrating calculations
- Converting 3D models

**Phase 5: User Data Migration (2-5 minutes)**
- Migrating user accounts
- Hashing passwords (if needed)
- Copying user preferences

**Phase 6: Validation (5-10 minutes)**
- Verifying database integrity
- Checking file counts
- Validating data checksums



#### Step 5: Review Results

After migration completes:

**Success Indicators:**
- ✓ All phases completed
- ✓ Validation passed
- ✓ No critical errors

**Migration Report:**
- View detailed statistics
- Check validation results
- Review any warnings
- Export report (JSON/PDF)

**Next Steps:**
- Click "Finish" to close wizard
- Application will restart
- Login with your credentials
- Verify your data

### Method 2: Command-Line Migration

For advanced users or automated deployments:

#### Full Migration

```bash
# Navigate to backend directory
cd solar-calculator-pro/backend

# Run full migration
python migrations/migrate_cli.py full \
  --source /path/to/streamlit/data \
  --target /path/to/electron/data \
  --backup \
  --validate
```

#### Selective Migration

**Database only:**
```bash
python migrations/migrate_cli.py database \
  --source /path/to/source.db \
  --target /path/to/target.db
```

**Settings only:**
```bash
python migrations/migrate_cli.py settings \
  --source /path/to/source/settings \
  --target /path/to/target/settings
```

**Projects only:**
```bash
python migrations/migrate_cli.py projects \
  --source /path/to/source/projects \
  --target /path/to/target/projects
```

**Users only:**
```bash
python migrations/migrate_cli.py users \
  --source /path/to/source/users \
  --target /path/to/target/users
```

#### CLI Options

```bash
Options:
  --source PATH       Source data path (required)
  --target PATH       Target data path (required)
  --backup           Create backup before migration
  --no-backup        Skip backup creation
  --validate         Validate after migration
  --no-validate      Skip validation
  --force            Overwrite existing data
  --dry-run          Simulate migration without changes
  --verbose          Enable detailed logging
  --quiet            Suppress output
  --log-file PATH    Save logs to file
  --help             Show help message
```



### Method 3: API-Based Migration

For integration with other tools:

```bash
# Start migration via API
curl -X POST http://localhost:8000/api/v1/migration/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source_path": "/path/to/streamlit/data",
    "target_path": "/path/to/electron/data",
    "backup_enabled": true,
    "validate_after_migration": true
  }'

# Check status
curl http://localhost:8000/api/v1/migration/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get report
curl http://localhost:8000/api/v1/migration/report \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Migration Details

### Database Migration

#### What Happens

1. **Schema Detection**: Analyzes source database structure
2. **Table Creation**: Creates tables in target database
3. **Data Copy**: Copies all records with transformations
4. **Index Creation**: Recreates indexes for performance
5. **Validation**: Verifies record counts match

#### Supported Databases

- `product_database.db` - Product catalog
- `crm_database.db` - CRM data
- `projects.db` - Project information
- `users.db` - User accounts
- Custom databases

#### Schema Transformations

**Automatic transformations:**
- Column renaming (old_name → new_name)
- Data type conversions
- Default value additions
- Timestamp standardization (ISO 8601)
- Password hashing (bcrypt)

**Example transformation:**
```python
# Old schema
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  password TEXT,  -- Plain text
  created DATETIME
);

# New schema
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  password_hash TEXT NOT NULL,  -- Bcrypt hashed
  email TEXT,
  role TEXT DEFAULT 'user',
  created_at TEXT NOT NULL,  -- ISO 8601
  updated_at TEXT
);
```



### Settings Migration

#### Configuration Files

**Supported formats:**
- JSON (`.json`)
- YAML (`.yaml`, `.yml`)
- INI (`.ini`)
- TOML (`.toml`)
- Streamlit config (`.streamlit/config.toml`)

#### Settings Mapping

**Streamlit → Electron:**

```yaml
# Streamlit config.toml
[theme]
base = "light"
primaryColor = "#1976d2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

# Electron settings.json
{
  "theme": {
    "mode": "light",
    "colors": {
      "primary": "#1976d2",
      "background": "#ffffff",
      "surface": "#f0f2f6",
      "text": "#262730"
    },
    "font": {
      "family": "sans-serif"
    }
  }
}
```

#### User Preferences

**Migrated preferences:**
- Theme selection
- Language settings
- Number formatting (German locale)
- Chart preferences
- Default values
- Recent files
- Window size/position
- Keyboard shortcuts

### Project Data Migration

#### Project Structure

**Old structure (Streamlit):**
```
projects/
├── project_001/
│   ├── data.json
│   ├── calculations.json
│   └── attachments/
├── project_002/
│   └── ...
```

**New structure (Electron):**
```
projects/
├── project_001/
│   ├── metadata.json
│   ├── solar_data.json
│   ├── calculations.json
│   ├── 3d_model.json
│   ├── pdf_config.json
│   └── attachments/
```



#### Data Transformations

**Project metadata:**
```json
// Old format
{
  "name": "Solar Project 1",
  "customer": "John Doe",
  "status": "active",
  "created": "2024-01-01"
}

// New format
{
  "id": 1,
  "name": "Solar Project 1",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "project_type": "solar",
  "status": "in_progress",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "_migrated": true,
  "_migration_date": "2024-01-15T10:30:00Z"
}
```

**Calculation data:**
- Solar calculations preserved
- Heat pump data converted
- Price matrix references updated
- 3D visualization data migrated
- PDF configurations transferred

### User Data Migration

#### User Accounts

**Password handling:**
- Plain text passwords → bcrypt hashed
- Already hashed passwords → preserved
- Salt generated per user
- Minimum 12 rounds (bcrypt cost factor)

**User roles mapping:**
```
Streamlit → Electron
admin    → admin
user     → user
viewer   → viewer
(none)   → user (default)
```

#### Default Admin Creation

If no users exist after migration:
```json
{
  "username": "admin",
  "password": "admin123",  // MUST CHANGE
  "email": "admin@localhost",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**⚠️ SECURITY WARNING:**
Change the default admin password immediately after migration!

#### User Preferences

**Migrated data:**
- Dashboard layout
- Favorite projects
- Recent searches
- Notification settings
- Email preferences
- Display preferences



## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Migration Won't Start

**Symptoms:**
- "Migration failed to start" error
- Wizard doesn't proceed past first step
- API returns 400/500 error

**Possible Causes & Solutions:**

**1. Source path doesn't exist**
```bash
# Verify path exists
ls -la /path/to/streamlit/data  # macOS/Linux
dir "C:\path\to\streamlit\data"  # Windows

# Solution: Correct the path or restore from backup
```

**2. Insufficient permissions**
```bash
# Check permissions
ls -ld /path/to/streamlit/data  # macOS/Linux

# Solution: Run with administrator/sudo
sudo python migrations/migrate_cli.py ...  # macOS/Linux
# Run PowerShell/CMD as Administrator (Windows)
```

**3. Insufficient disk space**
```bash
# Check available space
df -h /path/to/target  # macOS/Linux
wmic logicaldisk get size,freespace,caption  # Windows

# Solution: Free up space or choose different target
```

**4. Another migration in progress**
```bash
# Check for lock file
ls /path/to/target/.migration_lock

# Solution: Wait for completion or remove lock file
rm /path/to/target/.migration_lock
```

#### Issue 2: Database Migration Fails

**Symptoms:**
- "Database locked" error
- "Unable to open database" error
- Record count mismatch

**Solutions:**

**1. Database is locked**
```bash
# Check for processes using database
lsof /path/to/database.db  # macOS/Linux
handle database.db  # Windows (Sysinternals)

# Solution: Close applications using the database
```

**2. Corrupted database**
```bash
# Check database integrity
sqlite3 database.db "PRAGMA integrity_check;"

# Solution: Repair database or restore from backup
sqlite3 database.db ".recover" | sqlite3 repaired.db
```

**3. Schema incompatibility**
```bash
# Check schema version
sqlite3 database.db "PRAGMA user_version;"

# Solution: Update schema manually or use migration tool
```



#### Issue 3: Settings Migration Fails

**Symptoms:**
- "Invalid JSON" error
- "Cannot parse YAML" error
- Settings not applied after migration

**Solutions:**

**1. Invalid JSON/YAML**
```bash
# Validate JSON
python -m json.tool settings.json

# Validate YAML
python -c "import yaml; yaml.safe_load(open('settings.yaml'))"

# Solution: Fix syntax errors or use default settings
```

**2. Missing settings files**
```bash
# Check for settings
find /path/to/streamlit -name "*.json" -o -name "*.yaml"

# Solution: Create default settings or skip settings migration
```

#### Issue 4: Validation Fails

**Symptoms:**
- "Record count mismatch" warning
- "File count mismatch" warning
- "Checksum mismatch" error

**Solutions:**

**1. Record count mismatch**
```bash
# Check specific table
sqlite3 source.db "SELECT COUNT(*) FROM users;"
sqlite3 target.db "SELECT COUNT(*) FROM users;"

# Solution: Re-run migration for specific database
python migrations/migrate_cli.py database \
  --source source.db --target target.db --force
```

**2. File count mismatch**
```bash
# Count files
find /path/to/source -type f | wc -l
find /path/to/target -type f | wc -l

# Solution: Check for hidden files or system files
# May be acceptable if difference is small (<5 files)
```

**3. Checksum mismatch**
```bash
# Calculate checksums
sha256sum source_file
sha256sum target_file

# Solution: Re-copy specific files
cp source_file target_file
```

#### Issue 5: Migration Hangs or Freezes

**Symptoms:**
- Progress bar stuck
- No log updates for >5 minutes
- Application not responding

**Solutions:**

**1. Large database processing**
```bash
# Check migration logs
tail -f migration_*.log

# Solution: Wait longer (large databases take time)
# Or cancel and use batch processing
```

**2. Network issues (if using network storage)**
```bash
# Check network connectivity
ping storage_server

# Solution: Copy data locally first, then migrate
```

**3. System resources exhausted**
```bash
# Check system resources
top  # macOS/Linux
taskmgr  # Windows

# Solution: Close other applications, increase RAM
```



#### Issue 6: Rollback Fails

**Symptoms:**
- "Backup not found" error
- "Cannot restore data" error
- Partial rollback

**Solutions:**

**1. Backup not found**
```bash
# Check backup location
ls -la /path/to/backups/

# Solution: Use manual backup
cp -R /manual/backup/* /path/to/target/
```

**2. Insufficient permissions for rollback**
```bash
# Solution: Run with elevated privileges
sudo python migrations/migrate_cli.py rollback
```

**3. Manual rollback**
```bash
# 1. Stop application
# 2. Remove target directory
rm -rf /path/to/target/*

# 3. Restore from backup
cp -R /path/to/backup/* /path/to/target/

# 4. Verify restoration
ls -la /path/to/target/
```

### Debug Mode

Enable detailed logging for troubleshooting:

**Via UI:**
1. Settings → Advanced → Enable Debug Mode
2. Restart application
3. Attempt migration again
4. Check logs in: `logs/migration_debug.log`

**Via CLI:**
```bash
python migrations/migrate_cli.py full \
  --source /path/to/source \
  --target /path/to/target \
  --verbose \
  --log-file migration_debug.log
```

**Via Environment Variable:**
```bash
export MIGRATION_DEBUG=1  # macOS/Linux
set MIGRATION_DEBUG=1  # Windows

# Then run migration
```

### Log Files

**Location:**
- Windows: `C:\Users\<username>\AppData\Local\SolarCalculatorPro\logs\`
- macOS: `~/Library/Logs/SolarCalculatorPro/`
- Linux: `~/.local/share/SolarCalculatorPro/logs/`

**Log files:**
- `migration_YYYYMMDD_HHMMSS.log` - Detailed migration log
- `migration_report.json` - Structured report
- `error.log` - Error messages only
- `debug.log` - Debug information (if enabled)

### Getting Help

**Before contacting support:**
1. Check this troubleshooting guide
2. Review migration logs
3. Export migration report
4. Note error messages
5. Document steps to reproduce

**Contact support with:**
- Migration report (JSON)
- Error logs
- System information
- Screenshots of errors
- Steps to reproduce issue



## Rollback Procedures

### When to Rollback

Consider rollback if:
- Migration fails with critical errors
- Data validation fails significantly
- Application doesn't work after migration
- Data appears corrupted or incomplete
- You need to return to Streamlit temporarily

### Automatic Rollback

**Triggered automatically when:**
- Critical migration error occurs
- Validation fails completely
- Database corruption detected
- Insufficient disk space during migration

**What happens:**
1. Migration stops immediately
2. Target directory is cleaned
3. Backup is restored automatically
4. Rollback status added to report
5. User is notified

**Automatic rollback report:**
```json
{
  "rollback": {
    "triggered": true,
    "reason": "Database migration failed",
    "success": true,
    "restored_from": "/path/to/backup",
    "completed_at": "2024-01-15T10:45:00Z"
  }
}
```

### Manual Rollback via UI

**Steps:**

1. **Open Migration Report**
   - Navigate to: Settings → Migration → View Last Migration
   - Or: Help → Migration History

2. **Click "Rollback Migration"**
   - Review rollback confirmation dialog
   - Confirm you want to rollback

3. **Wait for Completion**
   - Progress bar shows rollback status
   - Typically takes 5-10 minutes

4. **Verify Rollback**
   - Check rollback report
   - Verify data restored
   - Test application functionality

5. **Restart Application**
   - Close and reopen application
   - Verify everything works

### Manual Rollback via CLI

**Full rollback:**
```bash
python migrations/migrate_cli.py rollback \
  --target /path/to/electron/data \
  --backup /path/to/backup
```

**Selective rollback:**
```bash
# Rollback database only
python migrations/migrate_cli.py rollback \
  --target /path/to/electron/data \
  --backup /path/to/backup \
  --component database

# Rollback settings only
python migrations/migrate_cli.py rollback \
  --component settings
```



### Manual Rollback (Emergency)

If automatic rollback fails, perform manual rollback:

#### Step 1: Stop Application

```bash
# Windows
taskkill /F /IM "Solar Calculator Pro.exe"

# macOS
killall "Solar Calculator Pro"

# Linux
pkill -f solar-calculator-pro
```

#### Step 2: Remove Target Data

```bash
# Windows
rmdir /S /Q "C:\path\to\electron\data"

# macOS/Linux
rm -rf /path/to/electron/data
```

#### Step 3: Restore from Backup

```bash
# Windows
xcopy /E /I /H "C:\backup\streamlit_backup" "C:\path\to\electron\data"

# macOS/Linux
cp -R /backup/streamlit_backup/* /path/to/electron/data/
```

#### Step 4: Verify Restoration

```bash
# Check file count
find /path/to/electron/data -type f | wc -l

# Check databases
sqlite3 /path/to/electron/data/database.db "PRAGMA integrity_check;"

# Check settings
cat /path/to/electron/data/settings.json
```

#### Step 5: Restart Application

```bash
# Start application normally
# Verify all data is present
# Test core functionality
```

### Rollback Verification

**Checklist after rollback:**

```
☐ Application starts without errors
☐ All databases accessible
☐ Settings loaded correctly
☐ Projects visible and openable
☐ Users can login
☐ Calculations work
☐ PDF generation works
☐ 3D visualization works
☐ No data loss detected
☐ Performance is normal
```

### Partial Rollback

If only specific components failed:

**Rollback database only:**
```bash
# Remove migrated database
rm /path/to/target/database.db

# Restore from backup
cp /path/to/backup/database.db /path/to/target/
```

**Rollback settings only:**
```bash
# Remove migrated settings
rm /path/to/target/settings.json

# Restore from backup
cp /path/to/backup/settings.json /path/to/target/
```

**Rollback projects only:**
```bash
# Remove migrated projects
rm -rf /path/to/target/projects

# Restore from backup
cp -R /path/to/backup/projects /path/to/target/
```

### Post-Rollback Actions

**After successful rollback:**

1. **Review Migration Report**
   - Identify what went wrong
   - Note specific errors
   - Check validation results

2. **Fix Issues**
   - Repair corrupted data
   - Free up disk space
   - Update permissions
   - Close conflicting applications

3. **Retry Migration**
   - Address identified issues
   - Use selective migration if needed
   - Monitor more closely

4. **Contact Support**
   - If rollback fails
   - If issues persist
   - If data appears corrupted



## Post-Migration Validation

### Automatic Validation

The migration process includes automatic validation:

**Database Validation:**
- ✓ Record counts match source
- ✓ Table schemas correct
- ✓ Indexes created
- ✓ Foreign keys intact
- ✓ No corruption detected

**File Validation:**
- ✓ File counts match (±5 files acceptable)
- ✓ Critical files present
- ✓ Checksums match for important files
- ✓ Directory structure correct

**Data Integrity:**
- ✓ User accounts accessible
- ✓ Projects loadable
- ✓ Settings applied
- ✓ Relationships preserved

### Manual Validation Steps

#### 1. Login Test

```
☐ Open application
☐ Login with existing credentials
☐ Verify user profile loads
☐ Check user preferences applied
☐ Test logout and re-login
```

#### 2. Database Verification

```
☐ Open product catalog
☐ Search for products
☐ Verify product details
☐ Check product images
☐ Test product filtering
```

#### 3. Project Verification

```
☐ Open projects list
☐ Verify all projects visible
☐ Open a solar project
☐ Check calculation results
☐ Verify 3D visualization
☐ Test PDF generation
```

#### 4. CRM Verification

```
☐ Open CRM module
☐ Check customer list
☐ Open customer details
☐ Verify offers/quotes
☐ Check communication history
☐ Test task management
```

#### 5. Settings Verification

```
☐ Open settings
☐ Verify theme applied
☐ Check language settings
☐ Verify number formatting (German)
☐ Test custom preferences
☐ Check email configuration
```



#### 6. Functionality Testing

**Solar Calculator:**
```
☐ Create new solar project
☐ Enter roof parameters
☐ Calculate system size
☐ View 3D visualization
☐ Generate PDF report
☐ Save project
```

**Heat Pump Calculator:**
```
☐ Create heat pump project
☐ Enter building data
☐ Calculate efficiency
☐ View cost comparison
☐ Generate report
```

**Price Matrix:**
```
☐ Open price matrix
☐ Test price lookup
☐ Verify calculations
☐ Check special products
☐ Test extras/discounts
```

#### 7. Performance Testing

```
☐ Application starts quickly (<5 seconds)
☐ Database queries fast (<1 second)
☐ UI responsive
☐ No memory leaks
☐ No crashes or freezes
```

### Validation Report

Generate a validation report:

```bash
# Via CLI
python migrations/validate_migration.py \
  --target /path/to/electron/data \
  --report validation_report.json

# Via UI
Settings → Migration → Validate Migration
```

**Report includes:**
- Database integrity checks
- File count comparisons
- Data checksums
- Functionality tests
- Performance metrics
- Issues found
- Recommendations

### Common Validation Issues

**Issue: Some projects won't open**
- **Cause**: Corrupted project data
- **Solution**: Re-migrate specific projects or restore from backup

**Issue: Images not displaying**
- **Cause**: File paths not updated
- **Solution**: Run path update script or re-upload images

**Issue: Calculations give different results**
- **Cause**: Formula or data migration issue
- **Solution**: Verify calculation data, re-run migrations

**Issue: Performance slower than Streamlit**
- **Cause**: Database not optimized
- **Solution**: Run database optimization: `VACUUM; ANALYZE;`



## FAQ

### General Questions

**Q: How long does migration take?**
A: Typically 30-60 minutes depending on data size:
- Small (<1GB): 10-20 minutes
- Medium (1-10GB): 30-60 minutes
- Large (>10GB): 1-3 hours

**Q: Can I use the application during migration?**
A: No, the application should not be used during migration. Wait for completion.

**Q: Will my Streamlit data be deleted?**
A: No, the source data is never modified. A backup is also created.

**Q: Can I migrate multiple times?**
A: Yes, you can re-run migration. Use `--force` flag to overwrite existing data.

**Q: Do I need to uninstall Streamlit?**
A: No, you can keep both applications. Streamlit data remains untouched.

**Q: Can I migrate from an older Streamlit version?**
A: Yes, the migration supports all Streamlit versions. Schema transformations are automatic.

### Data Questions

**Q: Will my passwords be preserved?**
A: Yes, passwords are migrated and automatically hashed with bcrypt if not already hashed.

**Q: What happens to custom themes?**
A: Custom themes are converted to the new format. Some adjustments may be needed.

**Q: Are PDF templates migrated?**
A: Yes, all PDF templates are copied and remain functional.

**Q: What about uploaded files and attachments?**
A: All files are copied to the new location with paths updated.

**Q: Will my 3D models work?**
A: Yes, 3D visualization data is migrated and remains compatible.

**Q: Are calculation formulas preserved?**
A: Yes, all calculation logic and formulas are preserved exactly.

### Technical Questions

**Q: What database format is used?**
A: Both applications use SQLite. The schema is updated during migration.

**Q: Can I migrate to a network drive?**
A: Yes, but local storage is recommended for better performance.

**Q: Does migration require internet?**
A: No, migration is completely offline.

**Q: Can I pause and resume migration?**
A: No, migration must complete in one session. Plan accordingly.

**Q: What if migration fails halfway?**
A: Automatic rollback restores your data. You can retry after fixing issues.

**Q: Can I migrate only specific data?**
A: Yes, use selective migration via CLI to migrate specific components.



### Security Questions

**Q: Is my data encrypted during migration?**
A: Data is not encrypted during migration, but passwords are hashed. Encrypt backups if needed.

**Q: What happens to user permissions?**
A: User roles and permissions are preserved and mapped to the new system.

**Q: Is the default admin account secure?**
A: No! Change the default admin password immediately after migration.

**Q: Are API keys migrated?**
A: Yes, API keys are migrated securely. Regenerate if concerned.

**Q: Can I audit the migration?**
A: Yes, detailed logs and reports provide complete audit trail.

### Troubleshooting Questions

**Q: Migration says "database locked" - what do I do?**
A: Close all applications using the database, including Streamlit.

**Q: Validation failed - should I rollback?**
A: Review the validation report first. Minor issues may be acceptable.

**Q: Can I fix issues and re-migrate?**
A: Yes, fix issues, then re-run migration with `--force` flag.

**Q: Where are the migration logs?**
A: Check application logs directory (see "Log Files" section above).

**Q: Migration is very slow - is this normal?**
A: Large databases take time. Check logs to ensure progress. Wait patiently.

**Q: Can I cancel migration?**
A: Yes, but automatic rollback will occur. Better to let it complete.

### Post-Migration Questions

**Q: Can I go back to Streamlit?**
A: Yes, your Streamlit data is untouched. Just run Streamlit again.

**Q: Do I need to keep the backup?**
A: Keep it for at least 30 days until you're confident everything works.

**Q: How do I update the Electron app later?**
A: Use the built-in auto-update feature. Your data is preserved.

**Q: Can I migrate again if I find issues?**
A: Yes, fix issues and re-run migration. Use `--force` to overwrite.

**Q: What if I need help?**
A: Contact support with migration report and logs. See "Getting Help" section.

**Q: Are there any breaking changes?**
A: The UI is different but all functionality is preserved. See user manual for new features.



## Additional Resources

### Documentation

- **User Manual**: Complete guide to using the new application
  - Location: `docs/USER_MANUAL.md`
  - Topics: All features, workflows, tips

- **API Documentation**: For developers and integrations
  - Location: `docs/API_DOCUMENTATION.md`
  - Topics: Endpoints, authentication, examples

- **Developer Guide**: For customization and development
  - Location: `docs/DEVELOPER_GUIDE.md`
  - Topics: Architecture, setup, contribution

- **Migration UI Guide**: Detailed UI documentation
  - Location: `docs/MIGRATION_UI_QUICK_REFERENCE.md`
  - Topics: Wizard, components, API

- **Backend Migration**: Technical migration details
  - Location: `backend/migrations/README.md`
  - Topics: Scripts, transformations, testing

### Tools and Scripts

**Validation Tools:**
```bash
# Validate data integrity
python tools/validate_data.py --path /path/to/data

# Check database health
python tools/check_database.py --db database.db

# Verify file structure
python tools/verify_structure.py --path /path/to/data
```

**Optimization Tools:**
```bash
# Optimize databases
python tools/optimize_database.py --db database.db

# Clean up old files
python tools/cleanup.py --path /path/to/data --dry-run

# Update file paths
python tools/update_paths.py --old /old/path --new /new/path
```

**Backup Tools:**
```bash
# Create backup
python tools/backup.py --source /path/to/data --target /backup/path

# Restore backup
python tools/restore.py --backup /backup/path --target /path/to/data

# Verify backup
python tools/verify_backup.py --backup /backup/path
```

### Support Channels

**Documentation:**
- User Manual: In-app Help → User Manual
- Online Docs: https://docs.solarcalculatorpro.com
- Video Tutorials: https://tutorials.solarcalculatorpro.com

**Community:**
- Forum: https://forum.solarcalculatorpro.com
- Discord: https://discord.gg/solarcalculatorpro
- GitHub Issues: https://github.com/solarcalculatorpro/issues

**Professional Support:**
- Email: support@solarcalculatorpro.com
- Phone: +49 XXX XXXXXXX
- Live Chat: In-app support button

### Version Information

**Migration System Version:** 1.0.0
**Supported Streamlit Versions:** All versions
**Supported Electron Versions:** 1.0.0+
**Last Updated:** 2024-01-15

### Changelog

**v1.0.0 (2024-01-15)**
- Initial migration system release
- Database migration with schema transformation
- Settings migration with format conversion
- Project data migration
- User data migration with password hashing
- Automatic validation
- Rollback functionality
- CLI and UI tools
- Comprehensive documentation

---

## Quick Reference Card

### Pre-Migration
```
1. ☐ Backup data
2. ☐ Stop Streamlit
3. ☐ Check disk space
4. ☐ Install new app
```

### Migration
```
1. Launch wizard
2. Select source/target
3. Review plan
4. Start migration
5. Monitor progress
```

### Post-Migration
```
1. ☐ Review report
2. ☐ Test login
3. ☐ Verify data
4. ☐ Test features
5. ☐ Keep backup
```

### Emergency Rollback
```bash
# Stop app
# Remove target
# Restore backup
# Restart app
```

### Get Help
```
1. Check logs
2. Review report
3. Check FAQ
4. Contact support
```

---

**End of Migration Guide**

For the latest version of this guide, visit: https://docs.solarcalculatorpro.com/migration

