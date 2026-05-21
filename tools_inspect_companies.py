import pathlib
import sqlite3

root = pathlib.Path('data')
dbs = [
    root / 'app_data.db',
    root / 'app_data.db.backup_20250924_203914',
    root / 'app_data.db.backup_20250924_203928',
    root / 'app_data_backup_logic_20251207_003607.db',
    root / 'backups' / 'migration_backup_20251108_195019.db',
    root / 'backups' / 'migration_backup_20251108_195359.db',
]

for db in dbs:
    print(f"\n=== {db} exists={db.exists()} ===")
    if not db.exists():
        continue
    try:
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for table in ['companies', 'company_documents', 'company_text_templates', 'company_image_templates']:
            try:
                cur.execute(f'SELECT COUNT(*) AS c FROM {table}')
                print(table, cur.fetchone()['c'])
            except Exception as exc:
                print(table, 'ERR', exc)
        try:
            cur.execute("""
                SELECT id, name, street, zip_code, city, phone, email, website,
                       is_default, length(COALESCE(logo_base64, '')) AS logo_len
                FROM companies
                ORDER BY id
            """)
            for row in cur.fetchall():
                print('COMPANY', dict(row))
        except Exception as exc:
            print('companies list err', exc)
        try:
            cur.execute("""
                SELECT company_id, document_type, display_name, file_name, absolute_file_path
                FROM company_documents
                ORDER BY company_id, id
            """)
            rows = cur.fetchall()
            for row in rows[:160]:
                print('DOC', dict(row))
            if len(rows) > 160:
                print('... more docs', len(rows) - 160)
        except Exception as exc:
            print('docs list err', exc)
        try:
            cur.execute("""
                SELECT id, company_id, name, template_type, substr(content, 1, 80) AS content_preview
                FROM company_text_templates
                ORDER BY company_id, id
            """)
            for row in cur.fetchall():
                print('TEXT_TEMPLATE', dict(row))
        except Exception as exc:
            print('text template list err', exc)
        try:
            cur.execute("""
                SELECT id, company_id, name, template_type, file_path
                FROM company_image_templates
                ORDER BY company_id, id
            """)
            for row in cur.fetchall():
                print('IMAGE_TEMPLATE', dict(row))
        except Exception as exc:
            print('image template list err', exc)
        conn.close()
    except Exception as exc:
        print('DB open err', exc)

print('\n=== FILESYSTEM data/company_docs ===')
base = root / 'company_docs'
for path in sorted(base.rglob('*')):
    if path.is_file():
        print('FILE', path.as_posix())
