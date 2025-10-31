#!/usr/bin/env python3
"""
Analysiert Log-Dateien und findet Probleme
"""
import glob
import os
import re
from collections import defaultdict
from datetime import datetime


def analyze_logs():
    """Analysiert alle Log-Dateien"""

    log_patterns = [
        "*.log",
        "logs/*.log",
        "streamlit.log",
        "app.log",
        "error.log"
    ]

    all_logs = []
    for pattern in log_patterns:
        all_logs.extend(glob.glob(pattern, recursive=True))

    if not all_logs:
        print("📋 Keine Log-Dateien gefunden")
        return

    print(f"📋 LOG-ANALYSE ({len(all_logs)} Dateien):")

    # Statistiken sammeln
    error_patterns = {
        'ERROR': r'ERROR|Error|error',
        'WARNING': r'WARNING|Warning|warning|WARN',
        'CRITICAL': r'CRITICAL|Critical|FATAL|Fatal',
        'EXCEPTION': r'Exception|exception|Traceback',
        'TIMEOUT': r'timeout|Timeout|TIMEOUT',
        'MEMORY': r'memory|Memory|RAM|OutOfMemory',
    }

    stats = defaultdict(int)
    recent_errors = []

    for log_file in all_logs:
        try:
            with open(log_file, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            print(f"\n📄 {os.path.basename(log_file)}:")
            file_stats = {}

            for error_type, pattern in error_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                count = len(matches)
                file_stats[error_type] = count
                stats[error_type] += count

                if count > 0:
                    print(f"  {error_type}: {count}")

            # Letzten Fehler finden
            lines = content.split('\n')
            for line in reversed(lines[-50:]):  # Letzte 50 Zeilen
                if any(re.search(pattern, line, re.IGNORECASE)
                       for pattern in error_patterns.values()):
                    recent_errors.append((log_file, line.strip()))
                    break

        except Exception as e:
            print(f"❌ Fehler beim Lesen von {log_file}: {e}")

    # Gesamtstatistik
    print("\n📊 GESAMTSTATISTIK:")
    for error_type, count in stats.items():
        if count > 0:
            print(f"  {error_type}: {count}")

    # Letzte Fehler
    if recent_errors:
        print("\n🚨 LETZTE FEHLER:")
        for log_file, error_line in recent_errors[-5:]:
            print(f"  📄 {os.path.basename(log_file)}: {error_line[:100]}...")


def clean_old_logs(days_to_keep=7):
    """Löscht alte Log-Dateien"""

    cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)

    log_files = glob.glob("**/*.log", recursive=True)
    deleted_count = 0

    for log_file in log_files:
        try:
            if os.path.getmtime(log_file) < cutoff_time:
                os.remove(log_file)
                deleted_count += 1
                print(f"🗑️ Gelöscht: {log_file}")
        except BaseException:
            pass

    print(f"✅ {deleted_count} alte Log-Dateien gelöscht")


if __name__ == "__main__":
    analyze_logs()
    clean_old_logs()
