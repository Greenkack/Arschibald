## 2024-05-18 - [Repeated File I/O in locales.py]
**Learning:** Translations were being loaded from disk repeatedly causing unnecessary file I/O operations and JSON parsing time overheads.
**Action:** Applied `functools.lru_cache` to `load_translations()` to memoize results for subsequent calls.
