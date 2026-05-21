# Migration Quick Reference

## One-Page Migration Guide

### Before You Start

```
☐ Backup all data
☐ Stop Streamlit application
☐ Check disk space (need 2x current data size)
☐ Install new Electron application
☐ Have administrator access ready
```

### Migration Steps

#### Option 1: UI Wizard (Recommended)
1. Open new application
2. Navigate to Settings → Migration
3. Click "Start Migration"
4. Select source path (Streamlit data)
5. Select target path (or use default)
6. Enable backup and validation
7. Click "Start" and wait
8. Review report when complete

#### Option 2: Command Line
```bash
cd solar-calculator-pro/backend
python migrations/migrate_cli.py full \
  --source /path/to/streamlit/data \
  --target /path/to/electron/data \
  --backup --validate
```

### Typical Duration
- Small data (<1GB): 10-20 minutes
- Medium data (1-10GB): 30-60 minutes
- Large data (>10GB): 1-3 hours

### What Gets Migrated
✓ Databases (SQLite)
✓ Settings and preferences
✓ Project data and calculations
✓ User accounts (passwords hashed)
✓ Files and attachments
✓ PDF templates
✓ 3D models

### Common Issues

**"Database locked"**
→ Close all apps using the database

**"Insufficient disk space"**
→ Free up space or choose different target

**"Permission denied"**
→ Run as administrator/sudo

**"Validation failed"**
→ Review report, minor issues may be OK

### Emergency Rollback

```bash
# Stop application
# Remove target directory
rm -rf /path/to/electron/data

# Restore from backup
cp -R /backup/path/* /path/to/electron/data/

# Restart application
```

### After Migration

```
☐ Login with existing credentials
☐ Verify projects visible
☐ Test calculations
☐ Check settings applied
☐ Generate test PDF
☐ Keep backup for 30 days
☐ Change default admin password (if created)
```

### Get Help

**Logs:** `~/.local/share/SolarCalculatorPro/logs/`
**Report:** `migration_report.json` in target directory
**Support:** support@solarcalculatorpro.com
**Docs:** Full guide at `docs/MIGRATION_GUIDE.md`

### Key Commands

```bash
# Full migration
python migrate_cli.py full --source SRC --target TGT

# Database only
python migrate_cli.py database --source SRC --target TGT

# Validate
python validate_migration.py --target TGT

# Rollback
python migrate_cli.py rollback --target TGT
```

### Important Notes

⚠️ **Do not close application during migration**
⚠️ **Keep backup for at least 30 days**
⚠️ **Change default admin password immediately**
⚠️ **Test thoroughly before deleting Streamlit data**

### Success Indicators

✓ All migration phases completed
✓ Validation passed
✓ No critical errors in report
✓ Application starts normally
✓ Can login and access data
✓ All features working

---

**For detailed information, see:** `docs/MIGRATION_GUIDE.md`
