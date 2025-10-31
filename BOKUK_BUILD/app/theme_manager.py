from __future__ import annotations

import base64
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "Das Modul 'tomllib' oder 'tomli' wird benötigt, um Theme-Konfigurationen zu laden."
        ) from exc

MODULE_ROOT = Path(__file__).resolve().parent
THEMES_ROOT = MODULE_ROOT / "theming" / "amazing" / "awesome-streamlit-themes"

THEME_EMOJI_MAP: Mapping[str, str] = {
    "healthcare": "🏥",
    "bootstrap": "💼",
    "dark-mode": "🌙",
    "material-design": "📱",
    "saas-startup": "🚀",
    "editorial": "📰",
    "financial": "💰",
    "tailwind": "🎯",
    "cyberpunk": "🌆",
    "toddler": "🧸",
}

IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp", ".gif")

_THEME_OVERRIDES: dict[str, dict[str, str]] = {}

# Global Streamlit theme configuration for native widgets
streamlit_theme: dict[str, Any] = {}

DEFAULT_THEME_KEY = "default"
DEFAULT_THEME_CONFIG: Mapping[str, Any] = {
    "primaryColor": "#2563eb",
    "backgroundColor": "#f8fafc",
    "secondaryBackgroundColor": "#e2e8f0",
    "textColor": "#0f172a",
    "font": "Inter",
    "base": "light",
    "fontFaces": [],
    "sidebar": {
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f1f5f9",
        "textColor": "#0f172a",
    },
}
DEFAULT_THEME_DESCRIPTION = "Universelles Standard-Layout der Anwendung ohne externe Theme-Dateien."


def _build_default_theme() -> ThemeDefinition:
    sidebar_cfg = DEFAULT_THEME_CONFIG.get("sidebar", {})
    return ThemeDefinition(
        key=DEFAULT_THEME_KEY,
        title="Standard",
        description=DEFAULT_THEME_DESCRIPTION,
        base_path=MODULE_ROOT,
        config=DEFAULT_THEME_CONFIG,
        font_faces=DEFAULT_THEME_CONFIG.get("fontFaces", []),
        sidebar_config=sidebar_cfg if isinstance(sidebar_cfg, Mapping) else {},
        emoji="",
        preview_path=None,
    )


@dataclass(frozen=True)
class ThemeDefinition:
    key: str
    title: str
    description: str
    base_path: Path
    config: Mapping[str, Any]
    font_faces: Iterable[Mapping[str, Any]]
    sidebar_config: Mapping[str, Any]
    emoji: str
    preview_path: Path | None

    def menu_label(self) -> str:
        emoji = self.emoji or "🎨"
        return f"{emoji} {self.title}" if emoji else self.title


def _find_preview_image(base_path: Path) -> Path | None:
    preferred_names = [f"{base_path.name}{ext}" for ext in IMAGE_EXTENSIONS]
    preferred_names += [f"preview{ext}" for ext in IMAGE_EXTENSIONS]
    preferred_names += [f"thumbnail{ext}" for ext in IMAGE_EXTENSIONS]

    for name in preferred_names:
        candidate = base_path / name
        if candidate.exists() and candidate.is_file():
            return candidate

    # Fallback: first image in theme folder
    for child in sorted(base_path.iterdir(), key=lambda p: p.name.lower()):
        if child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS:
            return child

    # Look inside static/ if nothing found on top-level
    static_dir = base_path / "static"
    if static_dir.exists() and static_dir.is_dir():
        for child in sorted(
                static_dir.iterdir(),
                key=lambda p: p.name.lower()):
            if child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS:
                return child

    return None


def _guess_mime_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".gif":
        return "image/gif"
    return "application/octet-stream"


def _extract_title(readme_path: Path) -> str:
    try:
        text = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return readme_path.parent.name.replace("-", " ").title()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("# ")
            return heading or readme_path.parent.name.replace("-", " ").title()
    return readme_path.parent.name.replace("-", " ").title()


def _extract_description(readme_path: Path) -> str:
    try:
        text = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    # Skip heading lines
    content_lines = [line for line in lines if not line.startswith("#")]
    if not content_lines:
        return ""
    return content_lines[0]


@cache
def load_available_themes() -> dict[str, ThemeDefinition]:
    themes: dict[str, ThemeDefinition] = {}

    if THEMES_ROOT.exists():
        for candidate in sorted(
                THEMES_ROOT.iterdir(),
                key=lambda p: p.name.lower()):
            if not candidate.is_dir():
                continue
            config_path = candidate / ".streamlit" / "config.toml"
            if not config_path.exists():
                continue
            try:
                config_data = tomllib.loads(
                    config_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            theme_config = config_data.get("theme", {})
            sidebar_config = theme_config.get(
                "sidebar", {}) if isinstance(
                theme_config, Mapping) else {}
            font_faces: Iterable[Mapping[str, Any]] = theme_config.get(
                "fontFaces", []) if isinstance(theme_config, Mapping) else []

            readme_path = candidate / "README.md"
            title = _extract_title(readme_path)
            description = _extract_description(readme_path)
            emoji = THEME_EMOJI_MAP.get(candidate.name, "🎨")

            themes[candidate.name] = ThemeDefinition(
                key=candidate.name,
                title=title,
                description=description,
                base_path=candidate,
                config=theme_config,
                font_faces=font_faces,
                sidebar_config=sidebar_config if isinstance(sidebar_config, Mapping) else {},
                emoji=emoji,
                preview_path=_find_preview_image(candidate),
            )

    if not themes:
        themes[DEFAULT_THEME_KEY] = _build_default_theme()

    return themes


def _font_src_from_path(font_path: Path) -> str | None:
    if not font_path.exists():
        return None
    try:
        font_bytes = font_path.read_bytes()
    except Exception:
        return None
    encoded = base64.b64encode(font_bytes).decode("ascii")
    suffix = font_path.suffix.lower()
    if suffix == ".woff2":
        mime = "font/woff2"
        fmt = "woff2"
    elif suffix == ".woff":
        mime = "font/woff"
        fmt = "woff"
    elif suffix in {".ttf", ".otf"}:
        mime = "font/ttf"
        fmt = "truetype"
    else:
        mime = "application/octet-stream"
        fmt = "truetype"
    return f"url(data:{mime};base64,{encoded}) format('{fmt}')"


def _build_font_face_css(theme: ThemeDefinition) -> str:
    css_parts: list[str] = []
    for face in theme.font_faces:
        family = str(face.get("family", "")).strip()
        url_value = str(face.get("url", "")).strip()
        if not family or not url_value:
            continue
        font_file_name = Path(url_value).name
        font_path = theme.base_path / "static" / font_file_name
        data_src = _font_src_from_path(font_path)
        if not data_src:
            continue
        style = str(face.get("style", "normal"))
        weight = str(face.get("weight", "400"))
        css_parts.append(
            "@font-face {"  # noqa: ISC001 (keep all in one line for readability)
            f"font-family: '{family}';"
            f"src: {data_src};"
            f"font-style: {style};"
            f"font-weight: {weight};"
            "font-display: swap;"
            "}"
        )
    return "\n".join(css_parts)


def _css_var(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _to_css_boolean(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return default


def _safe_radius(value: Any, default: str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _hex_to_rgb(color: str) -> tuple[int, int, int] | None:
    if not isinstance(color, str):
        return None
    value = color.strip().lstrip("#")
    if len(value) == 3:
        try:
            r, g, b = (int(ch * 2, 16) for ch in value)
        except ValueError:
            return None
        return (r, g, b)
    if len(value) == 6:
        try:
            r = int(value[0:2], 16)
            g = int(value[2:4], 16)
            b = int(value[4:6], 16)
        except ValueError:
            return None
        return (r, g, b)
    return None


def _hex_to_rgba(
        color: str,
        alpha: float,
        fallback: str = "rgba(15, 23, 42, 0.8)") -> str:
    rgb = _hex_to_rgb(color)
    alpha = max(0.0, min(1.0, alpha))
    if rgb is None:
        return fallback
    r, g, b = rgb
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def _mix_rgb(rgb_a: tuple[int, int, int], rgb_b: tuple[int,
             int, int], factor: float) -> tuple[int, int, int]:
    factor = max(0.0, min(1.0, factor))
    return tuple(
        int(round(channel_a * (1 - factor) + channel_b * factor))
        for channel_a, channel_b in zip(rgb_a, rgb_b)
    )


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{component:02x}" for component in rgb)


def _lighten(color: str, amount: float) -> str:
    rgb = _hex_to_rgb(color)
    if rgb is None:
        return color
    mixed = _mix_rgb(rgb, (255, 255, 255), amount)
    return _rgb_to_hex(mixed)


def _darken(color: str, amount: float) -> str:
    rgb = _hex_to_rgb(color)
    if rgb is None:
        return color
    mixed = _mix_rgb(rgb, (0, 0, 0), amount)
    return _rgb_to_hex(mixed)


def _relative_luminance(color: str) -> float | None:
    rgb = _hex_to_rgb(color)
    if rgb is None:
        return None
    r, g, b = [channel / 255.0 for channel in rgb]

    def _linearize(component: float) -> float:
        if component <= 0.03928:
            return component / 12.92
        return ((component + 0.055) / 1.055) ** 2.4
    r_lin, g_lin, b_lin = (_linearize(r), _linearize(g), _linearize(b))
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def _is_light(color: str, threshold: float = 0.6) -> bool:
    luminance = _relative_luminance(color)
    if luminance is None:
        return False
    return luminance >= threshold


def _ensure_dark(color: str, *, fallback: str, intensity: float = 0.65) -> str:
    if not color:
        return fallback
    if not _is_light(color):
        return color
    darkened = _darken(color, intensity)
    if _is_light(darkened):
        return fallback
    return darkened


def _ensure_light(color: str, *, fallback: str = "#f8fafc") -> str:
    if not color:
        return fallback
    if _is_light(color, threshold=0.5):
        return color
    return fallback


def _json_theme_payload(theme: ThemeDefinition) -> str:
    payload = {
        "key": theme.key,
        "title": theme.title,
        "description": theme.description,
        "emoji": theme.emoji,
        "colors": {
            key: value
            for key, value in theme.config.items()
            if isinstance(value, str) and key.endswith("Color")
        },
    }
    return json.dumps(payload)


@cache
def get_theme_payload_json(theme_key: str) -> str:
    themes = load_available_themes()
    theme = themes.get(theme_key)
    if not theme:
        return "{}"
    return _json_theme_payload(theme)


def set_theme_overrides(
        overrides: Mapping[str, Mapping[str, str]] | None) -> None:
    """Register theme-specific color overrides and clear caches for rebuild."""

    global _THEME_OVERRIDES

    if not overrides:
        normalized: dict[str, dict[str, str]] = {}
    else:
        normalized = {
            key: {inner_key: inner_value for inner_key, inner_value in value.items()}
            for key, value in overrides.items()
        }

    if normalized == _THEME_OVERRIDES:
        return

    _THEME_OVERRIDES = normalized

    build_theme_css.cache_clear()
    get_theme_payload_json.cache_clear()


def get_theme_overrides() -> dict[str, dict[str, str]]:
    return {key: dict(value) for key, value in _THEME_OVERRIDES.items()}


def clear_theme_cache() -> None:
    """Clear all theme-related caches to force rebuild."""
    build_theme_css.cache_clear()
    get_theme_payload_json.cache_clear()
    load_available_themes.cache_clear()
    get_theme_preview_data.cache_clear()


@cache
def build_theme_css(theme_key: str) -> str:
    themes = load_available_themes()
    theme = themes.get(theme_key)
    if not theme:
        return ""

    if isinstance(theme.config, Mapping):
        config: dict[str, Any] = dict(theme.config)
    else:
        config = dict(DEFAULT_THEME_CONFIG)

    sidebar_config: dict[str, Any] = {}
    if isinstance(theme.sidebar_config, Mapping):
        sidebar_config.update(theme.sidebar_config)

    overrides = _THEME_OVERRIDES.get(theme_key, {})
    if overrides:
        for override_key, override_value in overrides.items():
            if not isinstance(
                    override_value,
                    str) or not override_value.strip():
                continue
            if override_key.startswith("sidebar."):
                _, _, sidebar_key = override_key.partition(".")
                if sidebar_key:
                    sidebar_config[sidebar_key] = override_value
            else:
                config[override_key] = override_value

    # Update global streamlit theme config so native widgets follow overrides.
    global streamlit_theme
    streamlit_theme = {
        "primaryColor": config.get(
            "primaryColor",
            DEFAULT_THEME_CONFIG["primaryColor"]),
        "backgroundColor": config.get(
            "backgroundColor",
            DEFAULT_THEME_CONFIG["backgroundColor"]),
        "secondaryBackgroundColor": config.get(
            "secondaryBackgroundColor",
            DEFAULT_THEME_CONFIG["secondaryBackgroundColor"]),
        "textColor": config.get(
            "textColor",
            DEFAULT_THEME_CONFIG["textColor"]),
        "font": config.get(
            "font",
            DEFAULT_THEME_CONFIG.get(
                "font",
                "Inter")),
    }

    primary_color = _css_var(
        config.get("primaryColor"),
        DEFAULT_THEME_CONFIG.get(
            "primaryColor",
            "#2563eb"))
    background_color = _css_var(
        config.get("backgroundColor"),
        DEFAULT_THEME_CONFIG.get(
            "backgroundColor",
            "#f8fafc"))
    secondary_background = _css_var(
        config.get("secondaryBackgroundColor"),
        DEFAULT_THEME_CONFIG.get("secondaryBackgroundColor", "#e2e8f0"),
    )
    text_color = _css_var(
        config.get("textColor"),
        DEFAULT_THEME_CONFIG.get(
            "textColor",
            "#0f172a"))
    link_color = _css_var(config.get("linkColor"), primary_color)
    border_color = _css_var(
        config.get("borderColor"),
        DEFAULT_THEME_CONFIG.get(
            "borderColor",
            "#1f2937"))
    code_background = _css_var(
        config.get("codeBackgroundColor"),
        DEFAULT_THEME_CONFIG.get("codeBackgroundColor", "#0b1120"),
    )

    sidebar_background = _css_var(
        sidebar_config.get("backgroundColor"),
        DEFAULT_THEME_CONFIG.get(
            "sidebar",
            {}).get(
            "backgroundColor",
            "#ffffff"),
    )
    sidebar_secondary = _css_var(
        sidebar_config.get("secondaryBackgroundColor"),
        DEFAULT_THEME_CONFIG.get(
            "sidebar",
            {}).get(
            "secondaryBackgroundColor",
            "#f1f5f9"),
    )

    primary_soft = _lighten(primary_color, 0.35)
    primary_strong = _darken(primary_color, 0.25)
    primary_glow = _lighten(primary_color, 0.5)
    primary_depth = _darken(primary_color, 0.4)

    is_dark_theme = not _is_light(background_color, threshold=0.6)

    overlay_base = "#ffffff" if is_dark_theme else "#000000"
    highlight_base = "#ffffff" if is_dark_theme else "#ffffff"
    shadow_base = "#000000"

    overlay_soft = _hex_to_rgba(overlay_base, 0.07 if is_dark_theme else 0.06)
    overlay_medium = _hex_to_rgba(overlay_base, 0.14 if is_dark_theme else 0.1)
    overlay_strong = _hex_to_rgba(
        overlay_base, 0.22 if is_dark_theme else 0.16)
    overlay_extra = _hex_to_rgba(overlay_base, 0.32 if is_dark_theme else 0.22)
    overlay_highlight = _hex_to_rgba(
        highlight_base, 0.38 if is_dark_theme else 0.18)
    overlay_outline = _hex_to_rgba(text_color, 0.28 if is_dark_theme else 0.18)

    shadow_soft_color = _hex_to_rgba(
        shadow_base, 0.42 if is_dark_theme else 0.16)
    shadow_strong_color = _hex_to_rgba(
        shadow_base, 0.58 if is_dark_theme else 0.24)
    shadow_soft = f"0 18px 36px {shadow_soft_color}"
    shadow_strong = f"0 28px 48px {shadow_strong_color}"

    text_muted = _hex_to_rgba(text_color, 0.78 if is_dark_theme else 0.74)
    text_subtle = _hex_to_rgba(text_color, 0.58 if is_dark_theme else 0.56)

    base_radius = _safe_radius(config.get("baseRadius"), "0.75rem")
    show_widget_border = _to_css_boolean(config.get("showWidgetBorder"), False)

    body_font = _css_var(config.get("font"), "Inter, sans-serif")
    heading_font = _css_var(config.get("headingFont"), body_font)
    code_font = _css_var(config.get("codeFont"), "JetBrains Mono, monospace")

    font_css = _build_font_face_css(theme)

    widget_border_css = (
        "border: 1px solid var(--border-color) !important;"
        if show_widget_border
        else "border: 1px solid transparent !important;"
    )

    drawer_panel_background = _hex_to_rgba(
        secondary_background if is_dark_theme else _lighten(
            background_color,
            0.08),
        0.92 if is_dark_theme else 0.96,
        fallback="rgba(30, 41, 59, 0.92)" if is_dark_theme else "rgba(241, 245, 249, 0.96)",
    )
    drawer_panel_glow = _hex_to_rgba(
        primary_glow,
        0.14 if is_dark_theme else 0.18,
        fallback="rgba(37, 99, 235, 0.14)",
    )
    drawer_panel_border = _hex_to_rgba(
        "#ffffff" if is_dark_theme else "#0f172a",
        0.2 if is_dark_theme else 0.12,
        fallback="rgba(255, 255, 255, 0.2)" if is_dark_theme else "rgba(15, 23, 42, 0.12)",
    )
    drawer_panel_shadow = (
        "0 28px 60px rgba(15, 23, 42, 0.55)"
        if is_dark_theme
        else "0 24px 46px rgba(15, 23, 42, 0.18)"
    )
    drawer_handle_background = _hex_to_rgba(
        primary_color, 0.95, fallback="rgba(37, 99, 235, 0.9)")
    drawer_handle_border = _hex_to_rgba(
        primary_depth,
        0.6 if is_dark_theme else 0.35,
        fallback="rgba(15, 23, 42, 0.45)",
    )
    drawer_handle_text = _hex_to_rgba(
        "#ffffff" if is_dark_theme else "#0f172a",
        0.92 if is_dark_theme else 0.88,
        fallback="rgba(255, 255, 255, 0.92)" if is_dark_theme else "rgba(15, 23, 42, 0.88)",
    )
    drawer_placeholder_color = _hex_to_rgba(
        text_color,
        0.72 if is_dark_theme else 0.64,
        fallback="rgba(255, 255, 255, 0.7)" if is_dark_theme else "rgba(15, 23, 42, 0.62)",
    )

    css = f"""
    <style>
    :root {{
        --primary-color: {primary_color};
        --background-color: {background_color};
        --secondary-background: {secondary_background};
        --text-color: {text_color};
        --link-color: {link_color};
        --border-color: {border_color};
        --code-background: {code_background};
        --sidebar-background: {sidebar_background};
        --sidebar-secondary: {sidebar_secondary};
        --primary-soft: {primary_soft};
        --primary-strong: {primary_strong};
        --primary-glow: {primary_glow};
        --primary-depth: {primary_depth};
        --base-radius: {base_radius};
        --shadow-soft: {shadow_soft};
        --shadow-strong: {shadow_strong};
        --overlay-soft: {overlay_soft};
        --overlay-medium: {overlay_medium};
        --overlay-strong: {overlay_strong};
        --overlay-extra: {overlay_extra};
        --overlay-highlight: {overlay_highlight};
        --overlay-outline: {overlay_outline};
        --text-muted: {text_muted};
        --text-subtle: {text_subtle};
        --font-body: {body_font};
        --font-heading: {heading_font};
        --font-code: {code_font};
    }}

    {font_css}

    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {{
        background: var(--background-color) !important;
        color: var(--text-color) !important;
        font-family: var(--font-body), -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    a {{
        color: var(--link-color) !important;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(145deg, var(--sidebar-background), var(--sidebar-secondary)) !important;
        color: var(--text-color) !important;
        border-right: 1px solid var(--border-color) !important;
        backdrop-filter: blur(18px);
        box-shadow: var(--shadow-strong);
    }}

    [data-testid="stSidebar"] .sidebar-surface {{
        display: flex;
        flex-direction: column;
        gap: 2rem;
        position: relative;
        z-index: 1;
        padding: 2.2rem 1.8rem;
    }}

    [data-testid="stSidebar"] .sidebar-brand {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.4rem;
        overflow: hidden;
        padding: 1.4rem 1.6rem;
        border-radius: calc(var(--base-radius) * 1.6);
        background: linear-gradient(140deg, var(--primary-soft), var(--overlay-soft)) !important;
        border: 1px solid var(--overlay-outline) !important;
        box-shadow:
            inset 0 1px 0 var(--overlay-highlight),
            var(--shadow-strong);
        color: var(--text-color) !important;
    }}

    [data-testid="stSidebar"] .sidebar-brand__title {{
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-color) !important;
    }}

    [data-testid="stSidebar"] .sidebar-brand__subtitle {{
        font-size: 0.82rem;
        opacity: 0.8;
        color: var(--text-color) !important;
    }}

    [data-testid="stSidebar"] .sidebar-card {{
        background: linear-gradient(150deg, var(--sidebar-secondary), var(--overlay-medium)) !important;
        border-radius: calc(var(--base-radius) * 1.3);
        padding: 1.6rem 1.45rem;
        border: 1px solid var(--overlay-outline) !important;
        box-shadow:
            inset 0 1px 0 var(--overlay-soft),
            var(--shadow-soft);
        color: var(--text-color) !important;
    }}

    [data-testid="stSidebar"] .sidebar-heading {{
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-weight: 600;
        opacity: 0.8;
        margin-bottom: 0.6rem;
    }}

    [data-testid="stSidebar"] .sidebar-section-title {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        font-weight: 600;
        opacity: 0.65;
        margin-bottom: 0.6rem;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {{
        row-gap: 0.55rem;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        border-radius: calc(var(--base-radius) * 0.8);
        padding: 0.85rem 0.95rem;
    border: 1px solid var(--overlay-outline) !important;
    background: var(--overlay-soft) !important;
        transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
        color: var(--text-color) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        border-color: var(--primary-color) !important;
        transform: translateX(3px);
    background: var(--overlay-medium) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label div[role="radio"][aria-checked="true"] {{
        border: 1px solid var(--primary-soft) !important;
        background: linear-gradient(145deg, var(--primary-soft), var(--overlay-medium)) !important;
        box-shadow:
            inset 0 1px 0 var(--overlay-extra),
            var(--shadow-soft);
    }}

    [data-testid="stSidebar"] .sidebar-divider {{
        height: 1px;
    background: var(--overlay-medium) !important;
        opacity: 0.35;
        margin: 1.4rem 0 1.5rem;
    }}

    [data-testid="stSidebar"] .sidebar-actions {{
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
    }}

    [data-testid="stSidebar"] .sidebar-footer {{
    font-size: 0.75rem;
    opacity: 0.7;
    color: var(--text-muted) !important;
        line-height: 1.45;
    }}

    .main .block-container {{
        padding: 2.4rem 3rem 3.2rem;
        max-width: 1380px;
    }}

    .main .block-container > div:first-child {{
        width: 100%;
    }}

    .main .block-container .stButton button {{
        border-radius: calc(var(--base-radius) * 0.9);
        background: linear-gradient(150deg, var(--primary-soft), var(--primary-color));
        color: #ffffff;
        border: none;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
        box-shadow: var(--shadow-soft);
    }}

    .main .block-container .stButton button:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-strong);
    }}

    .main .block-container .stButton button:active {{
        transform: translateY(0);
        box-shadow: var(--shadow-soft);
    }}

    [data-testid="stSidebar"] .stButton > button {{
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: calc(var(--base-radius) * 1.1);
        background: linear-gradient(155deg, var(--primary-glow), var(--primary-color) 45%, var(--primary-depth));
        color: #f8fafc;
        border: none;
        font-weight: 700;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        font-size: 0.78rem;
        padding: 1rem 1.45rem;
        box-shadow:
            var(--shadow-strong),
            inset 0 1px 0 var(--overlay-extra);
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
        transform: translateY(-1px);
    }}

    [data-testid="stSidebar"] .stButton > button::before {{
        content: "";
        position: absolute;
        inset: 2px;
        border-radius: inherit;
        background: linear-gradient(145deg, var(--overlay-extra), transparent);
        opacity: 0.35;
        pointer-events: none;
        transition: opacity 0.18s ease;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        filter: brightness(1.08);
        transform: translateY(-2px);
        box-shadow:
            var(--shadow-strong),
            inset 0 1px 0 var(--overlay-highlight);
    }}

    [data-testid="stSidebar"] .stButton > button:hover::before {{
        opacity: 0.55;
    }}

    [data-testid="stSidebar"] .stButton > button:active {{
        transform: translateY(2px);
        box-shadow:
            var(--shadow-soft),
            inset 0 8px 18px var(--overlay-strong),
            inset 0 -1px 0 var(--overlay-medium);
    }}

    [data-testid="stSidebar"] .stButton > button:active::before {{
        opacity: 0.2;
    }}

    .main .block-container .stMetric,
    .main .block-container [data-testid="stVerticalBlock"] > div:has(.stMetric) {{
        background: var(--secondary-background);
        border-radius: calc(var(--base-radius) * 1.2);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-soft);
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(10px);
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--primary-color);
    }}

    .main .block-container .stTabs [data-baseweb="tab-list"] {{
        gap: 0.6rem;
    }}

    .main .block-container .stTabs [data-baseweb="tab"] {{
        background: var(--overlay-soft);
        border-radius: calc(var(--base-radius) * 0.8);
        padding: 0.6rem 1.25rem;
        font-weight: 600;
        color: var(--text-color);
        transition: all 0.18s ease;
        border: 1px solid transparent;
    }}

    .main .block-container .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: var(--secondary-background);
        color: var(--primary-color);
        border-color: var(--primary-color);
        box-shadow: var(--shadow-soft);
    }}

    .main .block-container .st-expander {{
        border-radius: calc(var(--base-radius) * 1.2);
        border: 1px solid var(--border-color);
        background: var(--secondary-background);
        box-shadow: var(--shadow-soft);
    }}

    .main .block-container .stDataFrame,
    .main .block-container .stTable {{
        border-radius: calc(var(--base-radius) * 1.2);
        box-shadow: var(--shadow-soft);
    }}

    .main .block-container .stMarkdown h1,
    .main .block-container .stMarkdown h2,
    .main .block-container .stMarkdown h3,
    .main .block-container .stText h1,
    .main .block-container .stText h2,
    .main .block-container .stText h3 {{
        font-family: var(--font-heading), var(--font-body);
        color: var(--text-color);
    }}

    .page-header {{
        display: flex;
        align-items: center;
        gap: 1.35rem;
        margin-bottom: 2rem;
        padding: 1.5rem 1.8rem;
        border-radius: calc(var(--base-radius) * 1.4);
        background: linear-gradient(135deg, var(--overlay-soft), var(--secondary-background)) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-soft);
    }}

    .page-header__icon {{
        font-size: 2rem;
        line-height: 1;
    }}

    .page-header__content {{
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }}

    .page-header__title {{
        font-size: 1.65rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-color) !important;
    }}

    .page-header__subtitle {{
        margin: 0;
        color: var(--text-color) !important;
        opacity: 0.7;
        font-size: 0.96rem;
    }}

    .stAlert {{
        border-radius: calc(var(--base-radius) * 1.1);
        border: 1px solid var(--border-color) !important;
        background: linear-gradient(135deg, var(--overlay-soft), var(--secondary-background)) !important;
        color: var(--text-color) !important;
    }}

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div > input,
    .stDateInput input {{
        border-radius: calc(var(--base-radius) * 0.9);
        background: var(--secondary-background) !important;
        color: var(--text-color) !important;
        {widget_border_css}
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div > input:focus,
    .stDateInput input:focus {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18);
    }}

    pre, code {{
        font-family: var(--font-code), monospace;
        background: var(--code-background) !important;
        border-radius: calc(var(--base-radius) * 0.6);
        padding: 0.4rem 0.6rem;
        color: var(--text-color) !important;
    }}

    .stButton > button {{
        background: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        color: #ffffff !important;
        border-radius: calc(var(--base-radius) * 0.8) !important;
        box-shadow: var(--shadow-soft);
        transition: transform 0.16s ease, box-shadow 0.16s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-strong);
        background: var(--primary-strong) !important;
        border-color: var(--primary-strong) !important;
    }}

    .stButton > button:active {{
        transform: translateY(1px);
        box-shadow: none;
    }}

    .app-drawer {{
        position: fixed;
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        display: flex;
        align-items: stretch;
        gap: 0;
        z-index: 9999;
    }}

    .app-drawer--align-right {{
        right: 0;
        left: auto;
        flex-direction: row;
    }}

    .app-drawer--align-left {{
        left: 0;
        right: auto;
        flex-direction: row-reverse;
    }}

    .app-drawer__handle {{
        pointer-events: auto;
        display: flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.85rem 0.9rem;
        border-radius: 0 18px 18px 0;
        border: 1px solid {drawer_handle_border};
        border-left: none;
        background: {drawer_handle_background};
        color: {drawer_handle_text};
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.68rem;
        font-weight: 600;
        box-shadow:
            var(--shadow-strong),
            inset 0 1px 0 var(--overlay-highlight);
        transition: filter 0.2s ease, transform 0.2s ease;
    }}

    .app-drawer__handle:focus-visible {{
        outline: 2px solid var(--primary-color);
        outline-offset: 3px;
    }}

    .app-drawer__handle:hover {{
        filter: brightness(1.05);
        transform: translateX(-2px);
    }}

    .app-drawer__handle-icon {{
        font-size: 1rem;
        line-height: 1;
    }}

    .app-drawer__handle-text {{
        white-space: nowrap;
        letter-spacing: 0.22em;
    }}

    .app-drawer__panel {{
        width: min(420px, 86vw);
        max-height: 90vh;
        display: flex;
        flex-direction: column;
        background: linear-gradient(160deg, {drawer_panel_background}, {drawer_panel_glow});
        backdrop-filter: blur(28px);
        border-radius: 24px 0 0 24px;
        border: 1px solid {drawer_panel_border};
        border-right: none;
        box-shadow: {drawer_panel_shadow};
        transform: translateX(100%);
        opacity: 0;
        pointer-events: none;
        transition: transform 0.32s ease, opacity 0.26s ease;
        overflow: hidden;
        margin-right: 0;
    }}

    .app-drawer--expanded .app-drawer__panel {{
        transform: translateX(0);
        opacity: 1;
        pointer-events: auto;
        margin-right: 0;
    }}

    .app-drawer__panel-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.15rem 1.35rem 0.85rem;
        border-bottom: 1px solid {drawer_panel_border};
        color: {text_color};
        gap: 1rem;
    }}

    .app-drawer__panel-title {{
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    .app-drawer__close {{
        border: none;
        background: transparent;
        color: {text_color};
        font-size: 1.25rem;
        cursor: pointer;
        line-height: 1;
        transition: transform 0.2s ease, opacity 0.2s ease;
    }}

    .app-drawer__close:hover {{
        opacity: 0.75;
        transform: scale(1.05);
    }}

    .app-drawer__panel-content {{
        padding: 1.35rem 1.5rem 1.6rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        color: {text_color};
    }}

    .app-drawer__placeholder {{
        font-size: 0.92rem;
        color: {drawer_placeholder_color};
        text-align: center;
    }}

    .app-drawer--align-left .app-drawer__handle {{
        border-right: none;
        border-left: 1px solid {drawer_handle_border};
        border-radius: 18px 0 0 18px;
    }}

    .app-drawer--align-left .app-drawer__panel {{
        border-left: none;
        border-right: 1px solid {drawer_panel_border};
        border-radius: 0 24px 24px 0;
        transform: translateX(-100%);
        margin-left: 0;
    }}

    .app-drawer--align-left.app-drawer--expanded .app-drawer__panel {{
        transform: translateX(0);
        margin-left: 0;
    }}

    .app-drawer--align-right.app-drawer--collapsed .app-drawer__panel {{
        margin-right: calc(-1 * min(420px, 86vw));
    }}

    .app-drawer--align-left.app-drawer--collapsed .app-drawer__panel {{
        margin-left: calc(-1 * min(420px, 86vw));
    }}


    @media (max-width: 820px) {{
        .app-drawer__panel {{
            width: min(380px, 92vw);
        }}
        .app-drawer__handle-text {{
            display: none;
        }}
        .app-drawer__handle {{
            border-radius: 14px 0 0 14px;
            padding: 0.75rem 0.8rem;
        }}
    }}

    [data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        border-bottom: 2px solid transparent !important;
        color: var(--text-color) !important;
    }}

    [data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--primary-color) !important;
        border-bottom-color: var(--primary-color) !important;
    }}

    .stProgress > div > div {{
        background: var(--primary-color) !important;
    }}
    </style>
    """
    return css


def get_theme_menu_items() -> list[dict[str, str]]:
    themes = load_available_themes()
    items: list[dict[str, str]] = []
    for key, definition in themes.items():
        items.append({
            "action": f"set_theme::{key}",
            "label": definition.menu_label(),
        })
    return items


def get_theme_title(theme_key: str) -> str:
    theme = load_available_themes().get(theme_key)
    if not theme:
        return theme_key
    return theme.title


def get_theme_description(theme_key: str) -> str:
    theme = load_available_themes().get(theme_key)
    if not theme:
        return ""
    return theme.description


@cache
def get_theme_preview_data(theme_key: str) -> str | None:
    theme = load_available_themes().get(theme_key)
    if not theme or not theme.preview_path:
        return None
    try:
        data = theme.preview_path.read_bytes()
    except Exception:
        return None
    mime = _guess_mime_from_path(theme.preview_path)
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"
