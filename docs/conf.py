"""Sphinx configuration for the sphinx-badges example docs."""

import sys
from pathlib import Path

# Make the package importable when building from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# Make the example Python library importable.
sys.path.insert(0, str(Path(__file__).parent / "_python"))

# ── Project ──────────────────────────────────────────────────────────────────
project = "sphinx-badges"
copyright = "2026, sphinx-badges contributors"
author = "sphinx-badges contributors"
release = "0.1.0"

# ── Extensions ───────────────────────────────────────────────────────────────
extensions = [
    "sphinx_badges",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

autosummary_generate = True  # auto-generate stub pages under generated/

html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css",
]

# ── sphinx-badges configuration ──────────────────────────────────────────────
# Badge style: "rounded" (default, Bootstrap-style), "square" (Material Design),
# or "pill" (fully rounded).
badges_style = "rounded"

# Define (or override) badge colours and labels.
# Group display labels — keys match the prefix used in badge IDs.
# Each entry can be a plain string (label only) or a dict with optional
# "icon" and "tooltip" keys.  The icon is prepended to every badge in
# the group; the tooltip appears on hover.
badges_group_labels = {
    "stability": {
        "label": "Stability",
        "tooltip": "API stability level — how safe this item is to depend on",
    },
    "area": {
        "label": "Area",
        "icon": "📦",
        "tooltip": "Functional area this item belongs to",
    },
    # platform group — icon-only badges (empty label shows just the icon)
    "platform": {
        "label": "Platform",
        "tooltip": "Supported runtime platform",
    },
}

# Badge definitions.  Use "group:name" keys for grouped badges.
# Ungrouped keys (no colon) remain valid for backward compatibility.
badges_definitions = {
    # Stability group
    "stability:stable": {
        "label": "Stable",
        "color": "#198754",
        "text_color": "#ffffff",
    },
    "stability:beta": {"label": "Beta", "color": "#0dcaf0", "text_color": "#000000"},
    "stability:experimental": {
        "label": "Experimental",
        "color": "#ffc107",
        "text_color": "#000000",
        "icon": "🧪",
        "tooltip": "Potentially unstable APIs",
    },
    "stability:deprecated": {
        "label": "Deprecated",
        "color": "#dc3545",
        "text_color": "#ffffff",
    },
    "stability:new": {"label": "New", "color": "#0d6efd", "text_color": "#ffffff"},
    # Area group
    "area:core": {"label": "Core", "color": "#6f42c1", "text_color": "#ffffff"},
    "area:math": {"label": "Math", "color": "#20c997", "text_color": "#000000"},
    "area:utils": {"label": "Utils", "color": "#fd7e14", "text_color": "#ffffff"},
    # Platform group — label is empty so only the per-badge icon is shown
    "platform:python": {
        "label": "",
        "color": "#3572A5",
        "text_color": "#ffffff",
        "icon": "🐍",
        "tooltip": "Python",
    },
    "platform:cli": {
        "label": "CLI",
        "color": "#212529",
        "text_color": "#ffffff",
        "icon": "⌨️",
    },
    "platform:mobile": {
        "label": "Mobile",
        "color": "#3DDC84",
        "text_color": "#ffffff",
        "icon": '<i class="fa-brands fa-android"></i>',
    },
    "platform:web": {
        "label": "",  # icon-only
        "color": "#0d6efd",
        "text_color": "#ffffff",
        "icon": '<i class="fa-brands fa-chrome"></i>',
        "tooltip": "Web",
    },
}

badges_default_color = "#6c757d"

# Move badges above the description inside API blocks (autodoc / py:class /
# py:function).  Set to "bottom" (default) to keep provided ordering
badges_position = "top"

# ── HTML output ──────────────────────────────────────────────────────────────
html_theme = "shibuya"
# html_theme = "pydata_sphinx_theme"
