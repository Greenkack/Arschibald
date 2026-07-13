## YYYY-MM-DD - [Locales JSON parsing bottleneck]
**Learning:** The load_translations() method reads JSON from disk synchronously whenever requested, and get_text() which invokes load_translations() is called over 1500 times in this app.
**Action:** Always wrap static JSON file reading functions like load_translations with @functools.lru_cache when they are invoked extensively by UI layer functions.
