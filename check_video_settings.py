import sqlite3
import json

conn = sqlite3.connect('data/app_data.db')
cursor = conn.cursor()

# Prüfe intro_settings
rows = cursor.execute("SELECT value FROM app_settings WHERE key = 'intro_settings'").fetchone()

if rows:
    settings = json.loads(rows[0])
    print("=== INTRO SETTINGS ===")
    print(f"media_type: {settings.get('media_type', 'NOT SET')}")
    print(f"video_file_path: {settings.get('video_file_path', 'NOT SET')}")
    print(f"video_url: {settings.get('video_url', 'NOT SET')}")
    print(f"video_size: {settings.get('video_size', 'NOT SET')}")
    print(f"video_autoplay: {settings.get('video_autoplay', 'NOT SET')}")
    print(f"video_loop: {settings.get('video_loop', 'NOT SET')}")
else:
    print("KEINE intro_settings gefunden!")

conn.close()
