# Migration Troubleshooting Flowchart

## Quick Diagnosis Guide

### Start Here: What's the Problem?

```
┌─────────────────────────────────────┐
│   Migration Issue Occurred?         │
└─────────────────┬───────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │  When did the issue occur?  │
    └──┬──────────┬──────────┬────┘
       │          │          │
       ▼          ▼          ▼
   Before     During      After
   Start      Migration   Migration
```

## Before Migration Start

### Issue: Can't Start Migration

```
Migration won't start
       │
       ├─→ Source path error?
       │   └─→ Check path exists
       │       └─→ Verify permissions
       │
       ├─→ Target path error?
       │   └─→ Check writable
       │       └─→ Check disk space
       │
       ├─→ Application error?
       │   └─→ Restart application
       │       └─→ Check logs
       │
       └─→ Lock file exists?
           └─→ Remove .migration_lock
               └─→ Retry
```

**Solutions:**
1. Verify source path: `ls /path/to/source`
2. Check permissions: `ls -ld /path/to/target`
3. Check disk space: `df -h`
4. Remove lock: `rm /path/to/target/.migration_lock`

## During Migration

### Issue: Migration Stuck/Frozen

```
Migration not progressing
       │
       ├─→ Check logs
       │   └─→ Still writing?
       │       ├─→ Yes: Wait (large data)
       │       └─→ No: Process hung
       │
       ├─→ Check system resources
       │   └─→ High CPU/Memory?
       │       ├─→ Yes: Normal for large data
       │       └─→ No: May be stuck
       │
       └─→ Wait 10 minutes
           └─→ Still stuck?
               └─→ Cancel and rollback
```

**Solutions:**
1. Check logs: `tail -f migration_*.log`
2. Monitor resources: `top` or Task Manager
3. Wait patiently for large databases
4. If truly stuck: Cancel and retry

### Issue: Database Migration Fails

```
Database error occurred
       │
       ├─→ "Database locked"?
       │   └─→ Close all apps
       │       └─→ Kill processes
       │           └─→ Retry
       │
       ├─→ "Cannot open database"?
       │   └─→ Check file exists
       │       └─→ Check permissions
       │           └─→ Verify not corrupted
       │
       └─→ "Schema error"?
           └─→ Check database version
               └─→ May need manual update
```

**Solutions:**
1. Find processes: `lsof database.db`
2. Kill processes: `kill -9 PID`
3. Check integrity: `sqlite3 db.db "PRAGMA integrity_check;"`
4. Repair if needed: `sqlite3 db.db ".recover"`

### Issue: Settings Migration Fails

```
Settings error occurred
       │
       ├─→ "Invalid JSON/YAML"?
       │   └─→ Validate syntax
       │       └─→ Fix or use defaults
       │
       ├─→ "File not found"?
       │   └─→ Check file exists
       │       └─→ Skip if optional
       │
       └─→ "Parse error"?
           └─→ Check file encoding
               └─→ Convert to UTF-8
```

**Solutions:**
1. Validate JSON: `python -m json.tool file.json`
2. Validate YAML: `yamllint file.yaml`
3. Check encoding: `file -i file.json`
4. Convert: `iconv -f ISO-8859-1 -t UTF-8 file.json`

## After Migration

### Issue: Validation Fails

```
Validation failed
       │
       ├─→ Record count mismatch?
       │   └─→ Check difference
       │       ├─→ Small (<1%): Acceptable
       │       └─→ Large (>5%): Investigate
       │
       ├─→ File count mismatch?
       │   └─→ Check difference
       │       ├─→ Small (<5): Acceptable
       │       └─→ Large: Investigate
       │
       └─→ Checksum mismatch?
           └─→ Critical files?
               ├─→ Yes: Re-migrate
               └─→ No: May be OK
```

**Solutions:**
1. Review validation report
2. Check specific tables/files
3. Re-migrate specific components
4. Accept minor differences if data looks good

### Issue: Application Won't Start

```
App won't start after migration
       │
       ├─→ Check error message
       │   └─→ Database error?
       │       └─→ Check database integrity
       │
       ├─→ Check logs
       │   └─→ Missing files?
       │       └─→ Restore from backup
       │
       └─→ Settings error?
           └─→ Reset to defaults
               └─→ Re-apply settings
```

**Solutions:**
1. Check logs: `cat error.log`
2. Verify databases: `sqlite3 db.db "PRAGMA integrity_check;"`
3. Reset settings: Delete `settings.json`
4. Rollback if needed

### Issue: Data Missing or Incorrect

```
Data problems after migration
       │
       ├─→ Projects missing?
       │   └─→ Check project directory
       │       └─→ Re-migrate projects
       │
       ├─→ Users can't login?
       │   └─→ Check user database
       │       └─→ Reset passwords
       │
       ├─→ Settings not applied?
       │   └─→ Check settings file
       │       └─→ Re-apply manually
       │
       └─→ Calculations wrong?
           └─→ Check calculation data
               └─→ Re-migrate databases
```

**Solutions:**
1. Selective re-migration
2. Manual data fixes
3. Restore specific components from backup
4. Full rollback if necessary

## Decision Tree: Should I Rollback?

```
Should I rollback?
       │
       ├─→ Critical data missing?
       │   └─→ YES: Rollback
       │
       ├─→ Application unusable?
       │   └─→ YES: Rollback
       │
       ├─→ Validation failed badly?
       │   └─→ YES: Rollback
       │
       ├─→ Minor issues only?
       │   └─→ NO: Fix and continue
       │
       └─→ Unsure?
           └─→ Export report
               └─→ Contact support
                   └─→ Wait for guidance
```

## Rollback Decision Matrix

| Issue | Severity | Action |
|-------|----------|--------|
| Database locked | Low | Fix and retry |
| Settings invalid | Low | Use defaults |
| Record count -1% | Low | Accept |
| Record count -10% | Medium | Investigate |
| Record count -50% | High | Rollback |
| App won't start | High | Rollback |
| Data corrupted | Critical | Rollback immediately |
| Validation passed | None | Continue |

## Quick Command Reference

```bash
# Check migration status
tail -f migration_*.log

# Validate migration
python validate_migration.py --target /path

# Rollback
python migrate_cli.py rollback --target /path

# Check database
sqlite3 db.db "PRAGMA integrity_check;"

# Check disk space
df -h /path

# Check processes
ps aux | grep streamlit
lsof database.db

# View report
cat migration_report.json | python -m json.tool
```

## When to Contact Support

Contact support if:
- ✗ Rollback fails
- ✗ Data appears corrupted
- ✗ Multiple migration attempts fail
- ✗ Unsure about validation results
- ✗ Need help interpreting logs
- ✗ Critical business data at risk

**Include with support request:**
- Migration report (JSON)
- Error logs
- Steps to reproduce
- System information
- Screenshots of errors

---

**For detailed solutions, see:** `docs/MIGRATION_GUIDE.md`
