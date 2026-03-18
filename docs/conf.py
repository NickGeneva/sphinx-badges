"""Sphinx configuration for the sphinx-badges example docs."""

import sys
from pathlib import Path

# Make the package importable when building from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# Make the example Python library importable.
sys.path.insert(0, str(Path(__file__).parent / "_python"))

# ── Project ──────────────────────────────────────────────────────────────────
project = "sphinx-badges demo"
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

# ── sphinx-badges configuration ──────────────────────────────────────────────
# Badge style: "rounded" (default, Bootstrap-style), "square" (Material Design),
# or "pill" (fully rounded).
badges_style = "rounded"

# Define (or override) badge colours and labels.
# Group display labels — keys match the prefix used in badge IDs.
badges_group_labels = {
    "stability": "Stability",
    "area": "Area",
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
}

badges_default_color = "#6c757d"

# Move badges above the description inside API blocks (autodoc / py:class /
# py:function).  Set to "bottom" (default) to keep provided ordering
badges_position = "top"

# ── HTML output ──────────────────────────────────────────────────────────────
html_theme = "alabaster"
