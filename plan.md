1. **Understand the problem**: We need to optimize `heatpump_pricing.py` by adding `st.cache_data` to `load_heatpump_components()`. This function loads all products from the database and processes them, which takes about 0.0576 seconds per 100 calls in our benchmark, but more importantly, it makes DB calls every time it's invoked.
2. **Review codebase context**: Streamlit's `@st.cache_data` is used across the app to cache expensive DB or API calls. In `heatpump_pricing.py`, `load_heatpump_components()` repeatedly queries `list_products()` without caching.
3. **Implementation details**: Add `import streamlit as st` to the imports of `heatpump_pricing.py` (if not already present), and decorate `load_heatpump_components()` with `@st.cache_data(ttl=3600)`.
4. **Pre-commit checks**: Run `pre_commit_instructions` and follow them to make sure all verification checks are executed.
5. **Verify and submit**: Verify tests pass with the cache decorator and submit the PR.
