# Migration FAQ - Frequently Asked Questions

## Table of Contents

1. [General Questions](#general-questions)
2. [Pre-Migration Questions](#pre-migration-questions)
3. [Data Migration Questions](#data-migration-questions)
4. [Technical Questions](#technical-questions)
5. [Security Questions](#security-questions)
6. [Troubleshooting Questions](#troubleshooting-questions)
7. [Post-Migration Questions](#post-migration-questions)
8. [Performance Questions](#performance-questions)

## General Questions

### Q: What is this migration about?
**A:** This migration moves your data from the Streamlit-based application to the new Electron desktop application. All your data, settings, and configurations are preserved while upgrading to a modern desktop experience with better performance and features.

### Q: Do I have to migrate?
**A:** No, migration is optional. You can continue using the Streamlit version. However, the Electron version offers:
- Better performance
- Native desktop integration
- Offline capabilities
- Modern UI/UX
- Regular updates and new features

### Q: How long does migration take?
**A:** Migration time depends on your data size:
- **Small** (<1GB): 10-20 minutes
- **Medium** (1-10GB): 30-60 minutes
- **Large** (>10GB): 1-3 hours

The wizard provides an estimate before starting.

### Q: Can I use the application during migration?
**A:** No, you should not use either application during migration. The migration process requires exclusive access to the data. Plan for downtime.

### Q: Will my Streamlit data be deleted?
**A:** No, your original Streamlit data is never modified or deleted. The migration creates a copy in the new location. You can keep both versions.

### Q: Can I migrate multiple times?
**A:** Yes, you can re-run migration as many times as needed. Use the `--force` flag to overwrite existing migrated data.

### Q: Is migration reversible?
**A:** Yes, you can rollback the migration at any time. Your original Streamlit data remains untouched, and you can return to using Streamlit if needed.



## Pre-Migration Questions

### Q: What should I do before migrating?
**A:** Follow the pre-migration checklist:
1. Create a complete backup of your data
2. Stop the Streamlit application
3. Verify data integrity
4. Check available disk space (need 2x current data size)
5. Install the new Electron application
6. Have administrator access ready

### Q: Where is my Streamlit data located?
**A:** Common locations:
- **Windows**: `C:\Users\<username>\AppData\Local\SolarCalculator`
- **macOS**: `~/Library/Application Support/SolarCalculator`
- **Linux**: `~/.local/share/SolarCalculator`

Check your Streamlit config file for the exact location.

### Q: How much disk space do I need?
**A:** You need at least 2x your current data size:
- 1x for the migrated data
- 1x for the backup

Example: If your Streamlit data is 5GB, you need at least 10GB free space.

### Q: Do I need to uninstall Streamlit?
**A:** No, you can keep both applications installed. They don't interfere with each other. This allows you to rollback if needed.

### Q: Can I test migration first?
**A:** Yes, use the `--dry-run` flag with the CLI tool to simulate migration without making changes:
```bash
python migrate_cli.py full --source SRC --target TGT --dry-run
```

### Q: What if I don't have administrator access?
**A:** Administrator access is required for:
- Installing the application
- Accessing system directories
- Creating backups

Contact your IT department if you don't have these permissions.

## Data Migration Questions

### Q: What data gets migrated?
**A:** Everything:
- ✓ All databases (SQLite)
- ✓ Application settings and preferences
- ✓ Project data and calculations
- ✓ User accounts and permissions
- ✓ Uploaded files and attachments
- ✓ PDF templates
- ✓ 3D visualization models
- ✓ Custom themes
- ✓ Recent files and history

### Q: Will my passwords be preserved?
**A:** Yes, passwords are migrated securely:
- Already hashed passwords are preserved
- Plain text passwords are automatically hashed with bcrypt
- All passwords remain functional after migration

### Q: What happens to my custom themes?
**A:** Custom themes are converted to the new format. The migration attempts to preserve all colors and settings, but some manual adjustments may be needed for advanced customizations.

### Q: Are PDF templates migrated?
**A:** Yes, all PDF templates are copied to the new location and remain fully functional. Template paths are automatically updated.

### Q: What about uploaded files and attachments?
**A:** All files are copied to the new location. File paths in the database are automatically updated to point to the new locations.

### Q: Will my 3D models work?
**A:** Yes, 3D visualization data is fully compatible. All models, placements, and configurations are preserved.

### Q: Are calculation formulas preserved?
**A:** Yes, all calculation logic, formulas, and parameters are preserved exactly. Results should be identical.

### Q: What about my project history?
**A:** Complete project history is migrated, including:
- All versions and revisions
- Change logs
- Timestamps
- User attributions



## Technical Questions

### Q: What database format is used?
**A:** Both applications use SQLite. The migration updates the schema to the new version while preserving all data.

### Q: Can I migrate to a network drive?
**A:** Yes, but it's not recommended. Network drives are slower and less reliable. Local storage (SSD preferred) provides the best performance.

### Q: Does migration require internet?
**A:** No, migration is completely offline. No internet connection is required.

### Q: Can I pause and resume migration?
**A:** No, migration must complete in one session. If interrupted, automatic rollback occurs and you'll need to restart.

### Q: What if migration fails halfway?
**A:** Automatic rollback restores your data from the backup. You can then fix any issues and retry the migration.

### Q: Can I migrate only specific data?
**A:** Yes, use selective migration via CLI:
```bash
# Database only
python migrate_cli.py database --source SRC --target TGT

# Settings only
python migrate_cli.py settings --source SRC --target TGT

# Projects only
python migrate_cli.py projects --source SRC --target TGT

# Users only
python migrate_cli.py users --source SRC --target TGT
```

### Q: What Python version is required?
**A:** Python 3.10 or higher is required for the migration tools.

### Q: Can I run migration on a different machine?
**A:** Yes, you can run migration on any machine with Python 3.10+. Copy your data to the migration machine first.

### Q: Does migration modify the source data?
**A:** No, source data is never modified. Migration only reads from the source and writes to the target.

### Q: What happens to database indexes?
**A:** All indexes are recreated in the target database for optimal performance.

## Security Questions

### Q: Is my data encrypted during migration?
**A:** Data is not encrypted during migration itself, but:
- Passwords are hashed with bcrypt
- Backups can be encrypted manually
- Data never leaves your machine

### Q: What happens to user permissions?
**A:** User roles and permissions are preserved and mapped to the new system:
- admin → admin
- user → user
- viewer → viewer

### Q: Is the default admin account secure?
**A:** **NO!** If a default admin account is created (username: admin, password: admin123), you **MUST** change the password immediately after migration.

### Q: Are API keys migrated?
**A:** Yes, API keys are migrated securely. If you're concerned about security, regenerate them after migration.

### Q: Can I audit the migration?
**A:** Yes, comprehensive audit trail includes:
- Detailed migration logs
- Structured migration report (JSON)
- Validation results
- All transformations documented

### Q: What data is logged?
**A:** Logs include:
- Migration steps and progress
- File operations
- Database operations
- Errors and warnings
- **NOT logged**: Passwords, API keys, sensitive data

### Q: How long should I keep the backup?
**A:** Keep the backup for at least 30 days after migration. Once you're confident everything works correctly, you can delete it.



## Troubleshooting Questions

### Q: Migration says "database locked" - what do I do?
**A:** The database is being used by another process:
1. Close all applications using the database
2. Stop the Streamlit application
3. Check for background processes: `lsof database.db` (macOS/Linux) or Process Explorer (Windows)
4. Kill any processes holding the database
5. Retry migration

### Q: Validation failed - should I rollback?
**A:** It depends on the validation results:
- **Minor issues** (record count -1%, file count -2): Usually acceptable
- **Moderate issues** (record count -5%, missing non-critical files): Review carefully
- **Major issues** (record count -20%, critical files missing): Rollback recommended

Review the validation report details before deciding.

### Q: Can I fix issues and re-migrate?
**A:** Yes:
1. Review the migration report to identify issues
2. Fix the problems (repair databases, fix permissions, etc.)
3. Re-run migration with `--force` flag to overwrite:
```bash
python migrate_cli.py full --source SRC --target TGT --force
```

### Q: Where are the migration logs?
**A:** Log locations:
- **Windows**: `C:\Users\<username>\AppData\Local\SolarCalculatorPro\logs\`
- **macOS**: `~/Library/Logs/SolarCalculatorPro/`
- **Linux**: `~/.local/share/SolarCalculatorPro/logs/`

Look for files named `migration_YYYYMMDD_HHMMSS.log`

### Q: Migration is very slow - is this normal?
**A:** Yes, for large databases. Check logs to ensure progress:
```bash
tail -f migration_*.log
```

If logs show activity, migration is progressing. Large databases (>10GB) can take hours.

### Q: Can I cancel migration?
**A:** Yes, but automatic rollback will occur. It's better to let migration complete unless there's a critical issue.

### Q: What if rollback fails?
**A:** Perform manual rollback:
1. Stop the application
2. Delete target directory: `rm -rf /path/to/target`
3. Restore from backup: `cp -R /backup/* /target/`
4. Restart application

### Q: Migration completed but app won't start - what now?
**A:** Check the error logs:
1. Look for error messages in `error.log`
2. Check database integrity: `sqlite3 db.db "PRAGMA integrity_check;"`
3. Verify all required files present
4. Try resetting settings to defaults
5. If nothing works, rollback and contact support

### Q: Some projects won't open after migration - why?
**A:** Possible causes:
- Corrupted project data
- Missing files or attachments
- Path issues

Solutions:
- Re-migrate specific projects
- Restore projects from backup
- Check project directory permissions

### Q: Calculations give different results - is this a bug?
**A:** This shouldn't happen. Verify:
1. Check calculation input data migrated correctly
2. Verify formula parameters preserved
3. Check for rounding differences (German number formatting)
4. Review migration report for calculation-related warnings

If results are significantly different, contact support.



## Post-Migration Questions

### Q: Can I go back to Streamlit?
**A:** Yes, your Streamlit data is untouched. Simply:
1. Stop the Electron application
2. Start Streamlit again
3. Your data is exactly as you left it

### Q: Do I need to keep the backup?
**A:** Keep it for at least 30 days. Once you're confident:
- All data migrated correctly
- Application works properly
- No issues discovered

Then you can safely delete the backup.

### Q: How do I update the Electron app later?
**A:** The application has built-in auto-update:
- Automatic update checks
- Notification when updates available
- One-click update installation
- Your data is preserved during updates

### Q: Can I migrate again if I find issues?
**A:** Yes, you can re-migrate at any time:
1. Fix any identified issues
2. Re-run migration with `--force` flag
3. Existing migrated data will be overwritten

### Q: What if I need help?
**A:** Multiple support options:
1. Check documentation (this FAQ, Migration Guide)
2. Review migration report and logs
3. Search community forum
4. Contact support with:
   - Migration report (JSON)
   - Error logs
   - System information
   - Steps to reproduce issue

### Q: Are there any breaking changes?
**A:** The UI is different but functionality is preserved:
- New modern interface (PrimeReact)
- Same features and capabilities
- Some workflows may be different
- See User Manual for new features

### Q: Can I customize the new application?
**A:** Yes, extensive customization options:
- Themes and colors
- Layout preferences
- Keyboard shortcuts
- Default values
- Number formatting
- Language settings

### Q: What about my custom scripts/integrations?
**A:** The new application provides:
- REST API for integrations
- Same data structures
- Backward-compatible endpoints
- Migration guide for custom code

### Q: Will my reports look the same?
**A:** PDF reports maintain the same structure and data. Some visual improvements may be present, but all information is preserved.

## Performance Questions

### Q: Is the new application faster?
**A:** Yes, generally:
- Faster startup time
- Better database performance
- Optimized calculations
- Smoother UI interactions
- Better memory management

### Q: Why is the new app slower than Streamlit?
**A:** If you experience slowness:
1. Run database optimization: `VACUUM; ANALYZE;`
2. Check system resources (RAM, CPU)
3. Verify SSD vs HDD (SSD recommended)
4. Check for background processes
5. Review performance logs

### Q: How much RAM does the new app use?
**A:** Typical usage:
- Idle: 200-300 MB
- Active use: 400-600 MB
- Large projects: 800 MB - 1.5 GB

This is normal for Electron applications.

### Q: Can I run both applications simultaneously?
**A:** Yes, but not recommended:
- Both can run at the same time
- Don't access the same data simultaneously
- May cause database locking issues
- Use separate data directories if needed

### Q: Does the new app work offline?
**A:** Yes, fully offline capable:
- No internet required for core features
- Local database storage
- Offline calculations
- Internet only needed for:
  - Updates
  - External API integrations (if configured)
  - Cloud backups (if enabled)

### Q: How do I optimize performance?
**A:** Performance tips:
1. Use SSD storage
2. Keep databases optimized (VACUUM)
3. Close unused projects
4. Limit concurrent operations
5. Allocate sufficient RAM (8GB+ recommended)
6. Keep application updated

---

## Still Have Questions?

**Documentation:**
- [Migration Guide](./MIGRATION_GUIDE.md) - Complete migration documentation
- [Quick Reference](./MIGRATION_QUICK_REFERENCE.md) - One-page guide
- [Troubleshooting Flowchart](./MIGRATION_TROUBLESHOOTING_FLOWCHART.md) - Visual troubleshooting
- [User Manual](./USER_MANUAL.md) - Complete application guide

**Support:**
- Email: support@solarcalculatorpro.com
- Forum: https://forum.solarcalculatorpro.com
- Discord: https://discord.gg/solarcalculatorpro
- Phone: +49 XXX XXXXXXX

**Emergency Support:**
- Critical issues: emergency@solarcalculatorpro.com
- Available 24/7 for data loss prevention

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
