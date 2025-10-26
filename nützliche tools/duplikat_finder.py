#!/usr/bin/env python3
"""
Findet doppelte/ähnliche Dateien
"""
import hashlib
import os
from difflib import SequenceMatcher


def find_duplicate_files(directory="."):
    """Findet exakte Duplikate basierend auf Hash"""

    file_hashes = {}
    duplicates = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                if file_hash in file_hashes:
                    duplicates.append((file_path, file_hashes[file_hash]))
                else:
                    file_hashes[file_hash] = file_path

    print("📋 DUPLIKATE GEFUNDEN:")
    for dup1, dup2 in duplicates:
        print(f"🔗 {dup1} ↔️ {dup2}")

    return duplicates


def find_similar_files(directory=".", threshold=0.8):
    """Findet ähnliche Dateien basierend auf Inhalt"""

    files_content = {}

    # Lade alle Dateien
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding='utf-8') as f:
                        files_content[file_path] = f.read()
                except BaseException:
                    continue

    # Vergleiche alle Paare
    file_paths = list(files_content.keys())
    similar_pairs = []

    for i in range(len(file_paths)):
        for j in range(i + 1, len(file_paths)):
            file1, file2 = file_paths[i], file_paths[j]
            similarity = SequenceMatcher(
                None, files_content[file1], files_content[file2]).ratio()

            if similarity > threshold:
                similar_pairs.append((file1, file2, similarity))

    print(f"\n📊 ÄHNLICHE DATEIEN (>{threshold * 100}% Ähnlichkeit):")
    for file1, file2, sim in sorted(
            similar_pairs, key=lambda x: x[2], reverse=True):
        print(
            f"🔍 {sim:.1%} - {os.path.basename(file1)} ↔️ {os.path.basename(file2)}")

    return similar_pairs


if __name__ == "__main__":
    find_duplicate_files()
    find_similar_files()
