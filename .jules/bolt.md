## 2025-01-25 - Translation Loading Bottleneck
**Learning:** `get_text` in `locales.py` reads and parses a JSON file on every single call without caching, which takes about 1.5ms per call. With 1544+ references across the codebase, this adds significant overhead to Streamlit UI rerenders.
**Action:** Always memoize I/O-bound configuration/translation loaders, especially in Streamlit where components re-evaluate frequently.
