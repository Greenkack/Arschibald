# Minimal Streamlit stub for CLI runs to avoid WebSocket/Tornado warnings.
# Provides the tiny subset used by our PDF generator and helpers.
from __future__ import annotations
from contextlib import contextmanager
from typing import Any

class _DummyProgress:
    def update(self, *args: Any, **kwargs: Any) -> None:
        pass

@contextmanager
def spinner(text: str = ""):
    yield

def progress(value: int = 0, text: str | None = None) -> _DummyProgress:
    return _DummyProgress()

# Session state mimic
class _SessionState(dict):
    pass

session_state = _SessionState()

# No-op UI helpers
def warning(*args: Any, **kwargs: Any) -> None:  # noqa: D401
    pass

def info(*args: Any, **kwargs: Any) -> None:  # noqa: D401
    pass

def error(*args: Any, **kwargs: Any) -> None:  # noqa: D401
    pass
