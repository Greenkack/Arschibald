# Stubbed progress manager to avoid Streamlit/Tornado side effects when running via CLI.
# Provides the same create_progress_bar signature used by pdf_generator.

from typing import Any

class _DummyProgress:
    def update(self, *args: Any, **kwargs: Any) -> None:
        pass

    def complete(self) -> None:
        pass

def create_progress_bar(text: str = "", container: Any = None) -> _DummyProgress:
    return _DummyProgress()
