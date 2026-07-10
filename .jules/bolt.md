## 2025-01-28 - [Initialization]
**Learning:** Agent initialized.
**Action:** Ready to add findings.
## 2025-01-28 - [PVGIS Rate Limiting & Caching]
**Learning:** PVGIS API calls via `get_pvgis_data` lacked both caching and rate-limiting, leading to potential API bans and unnecessary repeated network requests for identical calculations.
**Action:** Implemented an LRU cache based on geographic and system parameters, and added a 1-second rate limit between requests to ensure API stability and improve calculation performance.
