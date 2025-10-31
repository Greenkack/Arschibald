#!/usr/bin/env python3
"""
Universeller Emoji-Entferner für alle Dateien
"""
import glob
import os
import re


def remove_emojis_from_files(directory=".", file_pattern="*.py"):
    """Entfernt alle Emojis aus Python-Dateien"""

    # Unicode-Emoji-Regex (umfassend)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
        "\U0001F680-\U0001F6FF"  # Transport & Karten
        "\U0001F1E0-\U0001F1FF"  # Flaggen
        "\U00002702-\U000027B0"  # Verschiedene Symbole
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )

    files = glob.glob(os.path.join(directory, file_pattern))
    cleaned_files = 0

    for file_path in files:
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content
            content = emoji_pattern.sub('', content)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                cleaned_files += 1
                print(f"✅ {os.path.basename(file_path)} bereinigt")
            else:
                print(f"ℹ️ {os.path.basename(file_path)} bereits sauber")

        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")

    print(f"\n🎉 {cleaned_files} Dateien bereinigt!")


if __name__ == "__main__":
    remove_emojis_from_files()
