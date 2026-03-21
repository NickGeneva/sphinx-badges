"""Core Sphinx extension wiring for sphinx-badges."""

from __future__ import annotations

import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Any

from docutils import nodes as docutils_nodes
from sphinx.addnodes import desc_content
from sphinx.application import Sphinx

from .autodoc import process_docstring
from .collectors import init_badge_env, merge_badges, purge_badges
from .directives import BadgeFilterDirective, BadgesDirective
from .nodes import badge, badge_filter, badge_list
from .roles import BadgeRole

__version__ = "0.1.1"


def _compose_badge_content(icon: str, base_label: str) -> str:
    """Return inner HTML for a badge, wrapping text in a span when both present."""
    if icon and base_label:
        return (
            f'<span class="sphinx-badge-icon">{icon}</span>'
            f'<span class="sphinx-badge-label">{base_label}</span>'
        )
    return icon or base_label


_DEFAULT_COLOR = "#6c757d"

# Sensible default badge definitions — users override via conf.py.
_DEFAULT_DEFINITIONS: dict[str, dict[str, str]] = {
    "stable": {"label": "Stable", "color": "#198754", "text_color": "#ffffff"},
    "beta": {"label": "Beta", "color": "#0dcaf0", "text_color": "#000000"},
    "experimental": {
        "label": "Experimental",
        "color": "#ffc107",
        "text_color": "#000000",
    },
    "deprecated": {"label": "Deprecated", "color": "#dc3545", "text_color": "#ffffff"},
    "new": {"label": "New", "color": "#0d6efd", "text_color": "#ffffff"},
}

# Map badges_style config value to a CSS class added to each badge element.
_STYLE_CLASS = {
    "rounded": "",
    "square": "sphinx-badge-square",
    "pill": "sphinx-badge-pill",
}

# ---------------------------------------------------------------------------
# Badge ID helpers
# ---------------------------------------------------------------------------


def _parse_badge_id(badge_id: str) -> tuple[str, str]:
    """Split ``'group:name'`` into ``(group, name)``.

    Ungrouped IDs (no colon) return ``('', badge_id)``.
    """
    if ":" in badge_id:
        group, name = badge_id.split(":", 1)
        return group.strip(), name.strip()
    return "", badge_id


def _get_group_config(config: Any, group_key: str) -> dict[str, str]:
    """Return normalised group config for *group_key*.

    ``badges_group_labels`` accepts either a plain string (display label only)
    or a dict with optional keys ``label``, ``icon``, and ``tooltip``.
    """
    raw: dict = getattr(config, "badges_group_labels", {})
    entry = raw.get(group_key)
    fallback_label = group_key.replace("_", " ").title()
    if entry is None:
        return {"label": fallback_label, "icon": "", "tooltip": ""}
    if isinstance(entry, str):
        return {"label": entry, "icon": "", "tooltip": ""}
    return {
        "label": entry.get("label", fallback_label),
        "icon": entry.get("icon", ""),
        "tooltip": entry.get("tooltip", ""),
    }


def _resolve_badge(config: Any, badge_id: str) -> dict[str, str]:
    """Return the effective definition for *badge_id*.

    Lookup order for grouped IDs (``group:name``):

    1. ``badges_definitions['group:name']``  (exact user override)
    2. ``badges_definitions['name']``         (bare-name user override)
    3. built-in defaults keyed by ``'name'``
    4. auto-generated fallback (title-case of name, default colour)

    Icon and tooltip fall back to the group-level config from
    ``badges_group_labels`` when not set on the individual badge.
    """
    user_defs: dict = getattr(config, "badges_definitions", {})
    group, name = _parse_badge_id(badge_id)

    # Layer: exact match → name-only match in user defs → built-in defaults by name.
    defn: dict = {}
    defn.update(_DEFAULT_DEFINITIONS.get(name, {}))  # built-in by name
    defn.update(_DEFAULT_DEFINITIONS.get(badge_id, {}))  # built-in exact
    defn.update(user_defs.get(name, {}))  # user by name
    defn.update(user_defs.get(badge_id, {}))  # user exact

    group_cfg = (
        _get_group_config(config, group) if group else {"icon": "", "tooltip": ""}
    )
    fallback_label = name.replace("_", " ").title() if name else badge_id
    return {
        "label": defn.get("label", fallback_label),
        "color": defn.get(
            "color", getattr(config, "badges_default_color", _DEFAULT_COLOR)
        ),
        "text_color": defn.get("text_color", "#ffffff"),
        "icon": defn.get("icon", group_cfg["icon"]),
        "tooltip": defn.get("tooltip", group_cfg["tooltip"]),
    }


def _badge_classes(config: Any) -> str:
    """Return the full CSS class string for a badge element."""
    style: str = getattr(config, "badges_style", "rounded")
    extra = _STYLE_CLASS.get(style, "")
    return f"sphinx-badge {extra}".strip()


# ---------------------------------------------------------------------------
# Node visitors
# ---------------------------------------------------------------------------


def visit_badge_html(self, node: badge) -> None:
    cfg = self.builder.app.config
    badge_id = node["badge_id"]
    defn = _resolve_badge(cfg, badge_id)
    base_label = node.get("label_override") or defn["label"]
    icon = defn.get("icon", "")
    label = _compose_badge_content(icon, base_label)
    style = f"background-color:{defn['color']};color:{defn['text_color']};"
    cls = _badge_classes(cfg)
    tooltip = defn.get("tooltip", "")
    title_attr = f' title="{tooltip}"' if tooltip else ""
    self.body.append(
        f'<span class="{cls}" data-badge-id="{badge_id}"'
        f' style="{style}"{title_attr}>{label}</span>'
    )
    raise docutils_nodes.SkipNode


def visit_badge_list_html(self, node: badge_list) -> None:
    self.body.append('<span class="sphinx-badge-list">')


def depart_badge_list_html(self, node: badge_list) -> None:
    self.body.append("</span>")


def visit_badge_filter_html(self, node: badge_filter) -> None:
    cfg = self.builder.app.config
    badge_ids: list[str] = node.get("badge_ids", [])
    filter_mode: str = node.get("filter_mode", "and")
    badge_cls = _badge_classes(cfg)

    # Detect grouped mode: ALL badge IDs carry a group prefix.
    parsed = [(bid, *_parse_badge_id(bid)) for bid in badge_ids]
    is_grouped = bool(badge_ids) and all(group for _, group, _ in parsed)

    self.body.append(
        f'<div class="sphinx-badge-filter" '
        f'data-filter-mode="{filter_mode}" '
        f'data-grouped="{str(is_grouped).lower()}">'
    )
    self.body.append('<div class="sphinx-badge-filter-controls">')

    if is_grouped:
        # Build an ordered dict: group_key → [(full_id, name), ...]
        groups: OrderedDict[str, list[tuple[str, str]]] = OrderedDict()
        for full_id, group, name in parsed:
            groups.setdefault(group, []).append((full_id, name))

        for group_key, members in groups.items():
            group_cfg = _get_group_config(cfg, group_key)
            display_label = group_cfg["label"]
            self.body.append('<div class="sphinx-badge-filter-row">')
            self.body.append(
                f'<span class="sphinx-badge-filter-group-label">{display_label}</span>'
            )
            for full_id, _name in members:
                defn = _resolve_badge(cfg, full_id)
                style = f"background-color:{defn['color']};color:{defn['text_color']};"
                icon = defn.get("icon", "")
                base_label = defn["label"]
                btn_label = _compose_badge_content(icon, base_label)
                tooltip = defn.get("tooltip", "")
                title_attr = f' title="{tooltip}"' if tooltip else ""
                self.body.append(
                    f'<button class="sphinx-badge-filter-btn {badge_cls}" '
                    f'data-badge-id="{full_id}" style="{style}" '
                    f'aria-pressed="false"{title_attr}>{btn_label}</button>'
                )
            self.body.append("</div>")  # .sphinx-badge-filter-row

        # "Clear filters" button — JS shows/hides it based on active state.
        self.body.append(
            '<div class="sphinx-badge-filter-row sphinx-badge-filter-reset-row" '
            'style="display:none;">'
            '<button class="sphinx-badge-filter-clear" data-badge-id="__all__">'
            "Clear filters</button>"
            "</div>"
        )

    else:
        # Flat layout (backward-compatible).
        self.body.append(
            '<span class="sphinx-badge-filter-label">Filter by:</span>'
            f'<button class="sphinx-badge-filter-btn {badge_cls}" '
            f'data-badge-id="__all__" aria-pressed="true">All</button>'
        )
        for full_id, _group, _name in parsed:
            defn = _resolve_badge(cfg, full_id)
            style = f"background-color:{defn['color']};color:{defn['text_color']};"
            icon = defn.get("icon", "")
            base_label = defn["label"]
            btn_label = _compose_badge_content(icon, base_label)
            tooltip = defn.get("tooltip", "")
            title_attr = f' title="{tooltip}"' if tooltip else ""
            self.body.append(
                f'<button class="sphinx-badge-filter-btn {badge_cls}" '
                f'data-badge-id="{full_id}" style="{style}" '
                f'aria-pressed="false"{title_attr}>{btn_label}</button>'
            )

    self.body.append("</div>")  # .sphinx-badge-filter-controls
    self.body.append('<div class="sphinx-badge-filter-content">')


def depart_badge_filter_html(self, node: badge_filter) -> None:
    self.body.append("</div>")  # .sphinx-badge-filter-content
    self.body.append("</div>")  # .sphinx-badge-filter


def _maybe_connect_autodoc(app: Sphinx) -> None:
    """Connect autodoc integration after all extensions are loaded.

    Priority 100 ensures the Badges section is stripped before napoleon
    (priority 500) processes the docstring, preventing it from being
    misread as a parameter entry.
    """
    if "sphinx.ext.autodoc" in app.extensions:
        app.connect("autodoc-process-docstring", process_docstring, priority=100)


def _move_badges_to_top(
    app: Sphinx, doctree: docutils_nodes.document, docname: str
) -> None:
    """Move badge_list nodes to the front of every desc_content block.

    Activated when ``badges_position = "top"`` is set in ``conf.py``.
    Handles both hand-written RST and autodoc-generated pages uniformly.
    """
    if getattr(app.config, "badges_position", "bottom") != "top":
        return
    for container in doctree.traverse(desc_content):
        badge_nodes = [c for c in container.children if isinstance(c, badge_list)]
        if not badge_nodes:
            continue
        for bn in badge_nodes:
            container.remove(bn)
        for i, bn in enumerate(badge_nodes):
            container.insert(i, bn)


def _skip_node(self, node: Any) -> None:
    raise docutils_nodes.SkipNode


# ---------------------------------------------------------------------------
# build-finished: write badge-data.js
# ---------------------------------------------------------------------------


def write_badge_data_js(app: Sphinx, exception: Exception | None) -> None:
    """Write ``_static/badge-data.js`` after the HTML build completes."""
    if exception or getattr(app.builder, "format", None) != "html":
        return

    static_dir = os.path.join(app.outdir, "_static")
    os.makedirs(static_dir, exist_ok=True)

    badge_index = getattr(app.env, "badges_all_data", {})
    serialisable_index = {k: sorted(v) for k, v in badge_index.items()}

    # Collect all known badge IDs from defaults, user defs, and seen badge_index.
    user_defs: dict = getattr(app.config, "badges_definitions", {})
    all_ids: set[str] = set(_DEFAULT_DEFINITIONS) | set(user_defs)
    for page_badges in badge_index.values():
        all_ids.update(page_badges)

    merged_defs: dict[str, dict] = {}
    for bid in all_ids:
        defn = _resolve_badge(app.config, bid)
        group, name = _parse_badge_id(bid)
        merged_defs[bid] = {
            "label": defn["label"],
            "color": defn["color"],
            "text_color": defn["text_color"],
            "group": group,
            "name": name,
            "icon": defn.get("icon", ""),
            "tooltip": defn.get("tooltip", ""),
        }

    badge_style: str = getattr(app.config, "badges_style", "rounded")
    group_labels: dict = getattr(app.config, "badges_group_labels", {})
    show_page_badges: bool = bool(getattr(app.config, "badges_show_page_badges", False))

    out_path = os.path.join(static_dir, "badge-data.js")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("// Auto-generated by sphinx-badges — do not edit.\n")
        fh.write(f"window.SPHINX_BADGES_DATA = {json.dumps(serialisable_index)};\n")
        fh.write(f"window.SPHINX_BADGES_DEFINITIONS = {json.dumps(merged_defs)};\n")
        fh.write(f"window.SPHINX_BADGES_STYLE = {json.dumps(badge_style)};\n")
        fh.write(f"window.SPHINX_BADGES_GROUP_LABELS = {json.dumps(group_labels)};\n")
        fh.write(
            f"window.SPHINX_BADGES_SHOW_PAGE_BADGES = {json.dumps(show_page_badges)};\n"
        )


# ---------------------------------------------------------------------------
# Extension setup
# ---------------------------------------------------------------------------


def setup(app: Sphinx) -> dict[str, Any]:
    # Config values.
    app.add_config_value("badges_definitions", default={}, rebuild="html")
    app.add_config_value("badges_default_color", default=_DEFAULT_COLOR, rebuild="html")
    app.add_config_value("badges_style", default="rounded", rebuild="html")
    app.add_config_value("badges_group_labels", default={}, rebuild="html")
    app.add_config_value("badges_position", default="bottom", rebuild="html")
    app.add_config_value("badges_show_page_badges", default=False, rebuild="html")

    # Nodes.
    app.add_node(
        badge,
        html=(visit_badge_html, None),
        latex=(_skip_node, None),
        text=(_skip_node, None),
        man=(_skip_node, None),
        texinfo=(_skip_node, None),
    )
    app.add_node(
        badge_list,
        html=(visit_badge_list_html, depart_badge_list_html),
        latex=(_skip_node, None),
        text=(_skip_node, None),
        man=(_skip_node, None),
        texinfo=(_skip_node, None),
    )
    app.add_node(
        badge_filter,
        html=(visit_badge_filter_html, depart_badge_filter_html),
        latex=(_skip_node, None),
        text=(_skip_node, None),
        man=(_skip_node, None),
        texinfo=(_skip_node, None),
    )

    app.add_directive("badges", BadgesDirective)
    app.add_directive("badge-filter", BadgeFilterDirective)
    app.add_role("badge", BadgeRole())

    pkg_static = Path(__file__).parent / "_static"
    app.connect(
        "builder-inited",
        lambda a: a.config.html_static_path.append(str(pkg_static)),
    )
    app.add_css_file("sphinx_badges.css")
    app.add_js_file("badge-data.js")
    app.add_js_file("badge-filter.js")

    app.connect("builder-inited", init_badge_env)
    app.connect("builder-inited", _maybe_connect_autodoc)
    app.connect("env-purge-doc", purge_badges)
    app.connect("env-merge-info", merge_badges)
    app.connect("doctree-resolved", _move_badges_to_top)
    app.connect("build-finished", write_badge_data_js)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "env_version": 3,
    }
