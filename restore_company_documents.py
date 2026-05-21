"""Restore company master data, logos and company documents from local data backups.

This repairs the case where the app database lost all companies while the
company document folders under data/company_docs still exist.

The restore is intentionally idempotent:
- companies with IDs found in the backup are upserted
- document/template rows for those companies are rebuilt from the filesystem
- the original active/default company is restored
"""

from __future__ import annotations

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TARGET_DB = DATA_DIR / "app_data.db"
SOURCE_DB_CANDIDATES = [
    DATA_DIR / "app_data.db.backup_20250924_203928",
    DATA_DIR / "app_data.db.backup_20250924_203914",
]
COMPANY_DOCS_DIR = DATA_DIR / "company_docs"
RESTORE_NOTE = "Automatisch rekonstruiert aus data/company_docs und app_data.db.backup_20250924_203928"


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


def pick_source_db() -> Path:
    for candidate in SOURCE_DB_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            with connect(candidate) as conn:
                count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
                if count:
                    return candidate
        except sqlite3.DatabaseError:
            continue
    raise RuntimeError("Keine gültige Backup-DB mit Firmendaten gefunden.")


def backup_target_db() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DATA_DIR / f"app_data.before_company_restore_{timestamp}.db"
    shutil.copy2(TARGET_DB, backup_path)
    return backup_path


def normalize_rel_path(path_value: str | Path) -> str:
    return str(path_value).replace("/", "\\")


def infer_document_type(filename: str) -> str:
    lower = filename.lower()
    if any(token in lower for token in ("agb", "allgemeine_geschäft", "allgemeine_geschaeft", "geschäftsbedingungen", "geschaeftsbedingungen")):
        return "AGB"
    if any(token in lower for token in ("datenschutz", "privacy")):
        return "Datenschutz"
    if any(token in lower for token in ("vollmacht", "netzpru_fung", "netzprüfung", "netzanmeldung")):
        return "Vollmacht"
    return "Sonstiges"


def strip_timestamp(stem: str) -> str:
    return re.sub(r"_?20\d{12}$", "", stem)


def infer_display_name(filename: str, fallback_type: str) -> str:
    stem = strip_timestamp(Path(filename).stem)
    lower = stem.lower()
    if fallback_type == "AGB":
        return "AGB"
    if fallback_type == "Datenschutz":
        return "Datenschutz"
    if fallback_type == "Vollmacht":
        return "Vollmacht"
    if any(token in lower for token in ("marktstammdaten", "mastr")):
        return "MaStR"
    if "7_punkte" in lower or "7__punkte" in lower or "7-punkte" in lower or "7_punkt" in lower:
        return "7 Punkte"
    if "ablauf" in lower:
        return "Ablauf"
    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    return cleaned[:80] or fallback_type


def load_backup_document_metadata(src_conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for row in src_conn.execute(
        """
        SELECT company_id, document_type, display_name, file_name, absolute_file_path
        FROM company_documents
        """
    ).fetchall():
        rel = normalize_rel_path(row["absolute_file_path"])
        metadata[rel] = dict(row)
        metadata[normalize_rel_path(Path(str(row["company_id"])) / str(row["file_name"]))] = dict(row)
    return metadata


def restore_companies(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection) -> list[int]:
    companies = [dict(row) for row in src_conn.execute("SELECT * FROM companies ORDER BY id").fetchall()]
    if not companies:
        raise RuntimeError("Backup enthält keine Firmen.")

    dst_cols = table_columns(dst_conn, "companies")
    src_cols = table_columns(src_conn, "companies")
    common_cols = [col for col in dst_cols if col in src_cols]
    placeholders = ", ".join("?" for _ in common_cols)
    assignments = ", ".join(f"{col}=excluded.{col}" for col in common_cols if col != "id")
    sql = f"""
        INSERT INTO companies ({', '.join(common_cols)})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET {assignments}
    """
    for company in companies:
        dst_conn.execute(sql, [company.get(col) for col in common_cols])
    return [int(company["id"]) for company in companies]


def restore_documents(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection, company_ids: list[int]) -> int:
    metadata = load_backup_document_metadata(src_conn)
    dst_conn.execute(
        f"DELETE FROM company_documents WHERE company_id IN ({', '.join('?' for _ in company_ids)})",
        company_ids,
    )

    inserted = 0
    for company_id in company_ids:
        company_dir = COMPANY_DOCS_DIR / str(company_id)
        if not company_dir.exists():
            continue
        for pdf_path in sorted(company_dir.glob("*.pdf")):
            rel = normalize_rel_path(Path(str(company_id)) / pdf_path.name)
            known = metadata.get(rel, {})
            inferred_type = infer_document_type(pdf_path.name)
            # Eindeutige Dateinamen sind verlässlicher als alte Metadaten.
            doc_type = inferred_type if inferred_type != "Sonstiges" else (known.get("document_type") or inferred_type)
            display_name = known.get("display_name") or infer_display_name(pdf_path.name, doc_type)
            dst_conn.execute(
                """
                INSERT INTO company_documents
                    (company_id, document_type, display_name, file_name, absolute_file_path, uploaded_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(absolute_file_path) DO UPDATE SET
                    company_id=excluded.company_id,
                    document_type=excluded.document_type,
                    display_name=excluded.display_name,
                    file_name=excluded.file_name,
                    uploaded_at=CURRENT_TIMESTAMP
                """,
                (company_id, doc_type, display_name, pdf_path.name, rel),
            )
            inserted += 1
    return inserted


def restore_text_templates(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection, company_ids: list[int]) -> int:
    dst_conn.execute(
        f"DELETE FROM company_text_templates WHERE company_id IN ({', '.join('?' for _ in company_ids)})",
        company_ids,
    )
    rows = [dict(row) for row in src_conn.execute("SELECT * FROM company_text_templates ORDER BY id").fetchall()]
    count = 0
    for row in rows:
        if int(row["company_id"]) not in company_ids:
            continue
        dst_conn.execute(
            """
            INSERT INTO company_text_templates
                (company_id, name, content, template_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), COALESCE(?, CURRENT_TIMESTAMP))
            """,
            (
                row["company_id"],
                row["name"],
                row.get("content") or "",
                row.get("template_type") or "offer_text",
                row.get("created_at"),
                row.get("updated_at"),
            ),
        )
        count += 1
    return count


def restore_image_templates(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection, company_ids: list[int]) -> int:
    dst_conn.execute(
        f"DELETE FROM company_image_templates WHERE company_id IN ({', '.join('?' for _ in company_ids)})",
        company_ids,
    )
    rows = [dict(row) for row in src_conn.execute("SELECT * FROM company_image_templates ORDER BY id").fetchall()]
    count = 0
    for row in rows:
        if int(row["company_id"]) not in company_ids:
            continue
        rel = normalize_rel_path(row["file_path"])
        if not (COMPANY_DOCS_DIR / rel).exists():
            print(f"WARNUNG: Bildvorlage fehlt auf Datenträger und wird übersprungen: {rel}")
            continue
        dst_conn.execute(
            """
            INSERT INTO company_image_templates
                (company_id, name, template_type, file_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), COALESCE(?, CURRENT_TIMESTAMP))
            """,
            (
                row["company_id"],
                row["name"],
                row.get("template_type") or "title_image",
                rel,
                row.get("created_at"),
                row.get("updated_at"),
            ),
        )
        count += 1
    return count


def restore_active_company(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection) -> int | None:
    default_row = src_conn.execute("SELECT id FROM companies WHERE is_default = 1 ORDER BY id LIMIT 1").fetchone()
    active_id = int(default_row["id"]) if default_row else None
    if active_id is not None:
        dst_conn.execute("UPDATE companies SET is_default = CASE WHEN id = ? THEN 1 ELSE 0 END", (active_id,))
        dst_conn.execute(
            """
            INSERT INTO admin_settings (key, value, last_modified)
            VALUES ('active_company_id', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, last_modified=CURRENT_TIMESTAMP
            """,
            (str(active_id),),
        )
    return active_id


def validate(dst_conn: sqlite3.Connection, company_ids: list[int]) -> None:
    placeholders = ", ".join("?" for _ in company_ids)
    company_count = dst_conn.execute(
        f"SELECT COUNT(*) FROM companies WHERE id IN ({placeholders})", company_ids
    ).fetchone()[0]
    doc_count = dst_conn.execute(
        f"SELECT COUNT(*) FROM company_documents WHERE company_id IN ({placeholders})", company_ids
    ).fetchone()[0]
    missing = []
    for row in dst_conn.execute(
        f"SELECT absolute_file_path FROM company_documents WHERE company_id IN ({placeholders})", company_ids
    ).fetchall():
        rel = normalize_rel_path(row["absolute_file_path"])
        if not (COMPANY_DOCS_DIR / rel).exists():
            missing.append(rel)
    if company_count != len(company_ids):
        raise RuntimeError(f"Validierung fehlgeschlagen: {company_count}/{len(company_ids)} Firmen gefunden")
    if missing:
        raise RuntimeError(f"Validierung fehlgeschlagen: {len(missing)} Dokumentpfade fehlen: {missing[:5]}")
    print(f"VALIDIERUNG OK: {company_count} Firmen, {doc_count} Dokumente, keine fehlenden Dokumentpfade.")


def main() -> None:
    if not TARGET_DB.exists():
        raise FileNotFoundError(TARGET_DB)
    source_db = pick_source_db()
    backup_path = backup_target_db()
    print(f"Sicherungsdatei erstellt: {backup_path}")
    print(f"Quelle: {source_db}")

    src_conn = connect(source_db)
    dst_conn = connect(TARGET_DB)
    try:
        company_ids = restore_companies(src_conn, dst_conn)
        documents = restore_documents(src_conn, dst_conn, company_ids)
        text_templates = restore_text_templates(src_conn, dst_conn, company_ids)
        image_templates = restore_image_templates(src_conn, dst_conn, company_ids)
        active_company_id = restore_active_company(src_conn, dst_conn)
        dst_conn.commit()
        validate(dst_conn, company_ids)
        print("\nWIEDERHERSTELLUNG ABGESCHLOSSEN")
        print(f"Firmen-IDs: {company_ids}")
        print(f"Dokumente registriert: {documents}")
        print(f"Textvorlagen registriert: {text_templates}")
        print(f"Bildvorlagen registriert: {image_templates}")
        print(f"Aktive Standardfirma: {active_company_id}")
        print(RESTORE_NOTE)
    except Exception:
        dst_conn.rollback()
        raise
    finally:
        src_conn.close()
        dst_conn.close()


if __name__ == "__main__":
    main()
