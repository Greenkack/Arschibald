#!/usr/bin/env python3
"""
Scannt nach versehentlich committen Secrets/API-Keys
"""
import glob
import re


def scan_for_secrets():
    """Scannt alle Dateien nach Secrets"""

    # Verdächtige Patterns
    secret_patterns = {
        'API Keys': [
            r'api[_-]?key["\'\s]*[:=]["\'\s]*[a-zA-Z0-9]{20,}',
            r'apikey["\'\s]*[:=]["\'\s]*[a-zA-Z0-9]{20,}',
        ],
        'Database URLs': [
            r'mongodb://[^"\'\s]+',
            r'mysql://[^"\'\s]+',
            r'postgres://[^"\'\s]+',
        ],
        'Passwords': [
            r'password["\'\s]*[:=]["\'\s]*[^"\'\s]{8,}',
            r'passwd["\'\s]*[:=]["\'\s]*[^"\'\s]{8,}',
            r'pwd["\'\s]*[:=]["\'\s]*[^"\'\s]{8,}',
        ],
        'Tokens': [
            r'token["\'\s]*[:=]["\'\s]*[a-zA-Z0-9]{20,}',
            r'access[_-]?token["\'\s]*[:=]["\'\s]*[a-zA-Z0-9]{20,}',
        ],
        'Private Keys': [
            r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
            r'ssh-rsa [A-Za-z0-9+/]{100,}',
        ],
        'AWS Keys': [
            r'AKIA[0-9A-Z]{16}',
            r'aws[_-]?secret[_-]?access[_-]?key',
        ]
    }

    # Dateien zum Scannen
    scan_files = []
    for pattern in [
        "*.py",
        "*.json",
        "*.yml",
        "*.yaml",
        "*.env",
        "*.txt",
            "*.md"]:
        scan_files.extend(glob.glob(pattern, recursive=True))

    # Ausschließen
    exclude_patterns = ['.git/', '__pycache__/', 'venv/', 'node_modules/']
    scan_files = [
        f for f in scan_files if not any(
            ex in f for ex in exclude_patterns)]

    print("🔍 SECRET-SCANNER:")
    print(f"📁 Scanne {len(scan_files)} Dateien...")

    findings = []

    for file_path in scan_files:
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for category, patterns in secret_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            'file': file_path,
                            'line': line_num,
                            'category': category,
                            'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                        })
        except BaseException:
            continue

    if findings:
        print(f"\n🚨 {len(findings)} VERDÄCHTIGE SECRETS GEFUNDEN:")
        for finding in findings:
            print(f"  📄 {finding['file']}:{finding['line']}")
            print(f"     🏷️ {finding['category']}: {finding['match']}")
            print()

        print("⚠️ WARNUNG: Entfernen Sie diese Secrets vor dem Commit!")
    else:
        print("✅ Keine Secrets gefunden!")

    return findings


if __name__ == "__main__":
    scan_for_secrets()
