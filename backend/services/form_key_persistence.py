"""
Form Input Key Persistence System

This module provides persistence capabilities for form input keys,
allowing them to be saved to and loaded from storage.

Requirements: 14.7
Task: 223
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import sqlite3
from pathlib import Path


class FormKeyPersistence:
    """
    Handles persistence of form input keys and their associated data.
    """

    def __init__(self, db_path: str = "form_keys.db"):
        """
        Initialize the persistence layer.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create form_inputs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form_inputs (
                key TEXT PRIMARY KEY,
                form_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                input_type TEXT NOT NULL,
                label TEXT NOT NULL,
                current_value TEXT,
                default_value TEXT,
                validation_rules TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(form_id, field_name)
            )
        """)

        # Create form_data table for storing form submissions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id TEXT NOT NULL,
                submission_data TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT
            )
        """)

        # Create value_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS value_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_key TEXT NOT NULL,
                value TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (input_key) REFERENCES form_inputs(key)
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_form_inputs_form_id
            ON form_inputs(form_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_form_data_form_id
            ON form_data(form_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_value_history_input_key
            ON value_history(input_key)
        """)

        conn.commit()
        conn.close()

    def save_form_input(self, form_input_dict: Dict[str, Any]) -> bool:
        """
        Save a form input to the database.

        Args:
            form_input_dict: Dictionary representation of FormInput

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO form_inputs (
                    key, form_id, field_name, input_type, label,
                    current_value, default_value, validation_rules,
                    metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                form_input_dict['key'],
                form_input_dict['form_id'],
                form_input_dict['field_name'],
                form_input_dict['input_type'],
                form_input_dict['label'],
                json.dumps(form_input_dict.get('current_value')),
                json.dumps(form_input_dict.get('default_value')),
                json.dumps(form_input_dict.get('validation_rules', {})),
                json.dumps(form_input_dict.get('metadata', {})),
                form_input_dict['created_at'],
                form_input_dict['updated_at']
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving form input: {e}")
            return False

    def load_form_input(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load a form input from the database.

        Args:
            key: Dynamic key of the form input

        Returns:
            Dictionary representation or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT key, form_id, field_name, input_type, label,
                       current_value, default_value, validation_rules,
                       metadata, created_at, updated_at
                FROM form_inputs
                WHERE key = ?
            """, (key,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return {
                'key': row[0],
                'form_id': row[1],
                'field_name': row[2],
                'input_type': row[3],
                'label': row[4],
                'current_value': json.loads(row[5]) if row[5] else None,
                'default_value': json.loads(row[6]) if row[6] else None,
                'validation_rules': json.loads(row[7]) if row[7] else {},
                'metadata': json.loads(row[8]) if row[8] else {},
                'created_at': row[9],
                'updated_at': row[10]
            }

        except Exception as e:
            print(f"Error loading form input: {e}")
            return None

    def load_form_inputs(self, form_id: str) -> List[Dict[str, Any]]:
        """
        Load all form inputs for a specific form.

        Args:
            form_id: ID of the form

        Returns:
            List of form input dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT key, form_id, field_name, input_type, label,
                       current_value, default_value, validation_rules,
                       metadata, created_at, updated_at
                FROM form_inputs
                WHERE form_id = ?
                ORDER BY created_at
            """, (form_id,))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'key': row[0],
                    'form_id': row[1],
                    'field_name': row[2],
                    'input_type': row[3],
                    'label': row[4],
                    'current_value': json.loads(row[5]) if row[5] else None,
                    'default_value': json.loads(row[6]) if row[6] else None,
                    'validation_rules': json.loads(row[7]) if row[7] else {},
                    'metadata': json.loads(row[8]) if row[8] else {},
                    'created_at': row[9],
                    'updated_at': row[10]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"Error loading form inputs: {e}")
            return []

    def save_form_submission(
        self,
        form_id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[int]:
        """
        Save a form submission.

        Args:
            form_id: ID of the form
            data: Form data to save
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Submission ID or None if failed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO form_data (
                    form_id, submission_data, submitted_at,
                    user_id, session_id
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                form_id,
                json.dumps(data),
                datetime.now().isoformat(),
                user_id,
                session_id
            ))

            submission_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return submission_id

        except Exception as e:
            print(f"Error saving form submission: {e}")
            return None

    def load_form_submissions(
        self,
        form_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Load form submissions for a specific form.

        Args:
            form_id: ID of the form
            limit: Maximum number of submissions to load

        Returns:
            List of submission dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, form_id, submission_data, submitted_at,
                       user_id, session_id
                FROM form_data
                WHERE form_id = ?
                ORDER BY submitted_at DESC
                LIMIT ?
            """, (form_id, limit))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'form_id': row[1],
                    'data': json.loads(row[2]),
                    'submitted_at': row[3],
                    'user_id': row[4],
                    'session_id': row[5]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"Error loading form submissions: {e}")
            return []

    def save_value_history(
        self,
        input_key: str,
        value: Any,
        changed_at: Optional[str] = None
    ) -> bool:
        """
        Save a value change to history.

        Args:
            input_key: Dynamic key of the input
            value: Value that was set
            changed_at: Timestamp of change (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO value_history (input_key, value, changed_at)
                VALUES (?, ?, ?)
            """, (
                input_key,
                json.dumps(value),
                changed_at or datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving value history: {e}")
            return False

    def load_value_history(
        self,
        input_key: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Load value history for an input.

        Args:
            input_key: Dynamic key of the input
            limit: Maximum number of history entries

        Returns:
            List of history entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value, changed_at
                FROM value_history
                WHERE input_key = ?
                ORDER BY changed_at DESC
                LIMIT ?
            """, (input_key, limit))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'value': json.loads(row[0]) if row[0] else None,
                    'changed_at': row[1]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"Error loading value history: {e}")
            return []

    def delete_form_input(self, key: str) -> bool:
        """
        Delete a form input and its history.

        Args:
            key: Dynamic key of the input

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete value history
            cursor.execute("""
                DELETE FROM value_history WHERE input_key = ?
            """, (key,))

            # Delete form input
            cursor.execute("""
                DELETE FROM form_inputs WHERE key = ?
            """, (key,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error deleting form input: {e}")
            return False

    def delete_form(self, form_id: str) -> bool:
        """
        Delete all inputs and data for a form.

        Args:
            form_id: ID of the form

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all input keys for this form
            cursor.execute("""
                SELECT key FROM form_inputs WHERE form_id = ?
            """, (form_id,))
            keys = [row[0] for row in cursor.fetchall()]

            # Delete value history for all inputs
            for key in keys:
                cursor.execute("""
                    DELETE FROM value_history WHERE input_key = ?
                """, (key,))

            # Delete form inputs
            cursor.execute("""
                DELETE FROM form_inputs WHERE form_id = ?
            """, (form_id,))

            # Delete form submissions
            cursor.execute("""
                DELETE FROM form_data WHERE form_id = ?
            """, (form_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error deleting form: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored form data.

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count total inputs
            cursor.execute("SELECT COUNT(*) FROM form_inputs")
            total_inputs = cursor.fetchone()[0]

            # Count total forms
            cursor.execute("SELECT COUNT(DISTINCT form_id) FROM form_inputs")
            total_forms = cursor.fetchone()[0]

            # Count total submissions
            cursor.execute("SELECT COUNT(*) FROM form_data")
            total_submissions = cursor.fetchone()[0]

            # Count total history entries
            cursor.execute("SELECT COUNT(*) FROM value_history")
            total_history = cursor.fetchone()[0]

            conn.close()

            return {
                'total_inputs': total_inputs,
                'total_forms': total_forms,
                'total_submissions': total_submissions,
                'total_history_entries': total_history
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}


# Global persistence instance
_global_persistence = None


def get_form_key_persistence(
    db_path: str = "form_keys.db"
) -> FormKeyPersistence:
    """
    Get the global form key persistence instance.

    Args:
        db_path: Path to the database file

    Returns:
        Global FormKeyPersistence instance
    """
    global _global_persistence
    if _global_persistence is None:
        _global_persistence = FormKeyPersistence(db_path)
    return _global_persistence
