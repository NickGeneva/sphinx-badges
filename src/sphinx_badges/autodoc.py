"""autodoc integration — parse numpy-style ``Badges`` sections in docstrings.

When ``sphinx.ext.autodoc`` is active, this module hooks into the
``autodoc-process-docstring`` event and converts::

    Badges
    ------
    stable new

into the RST directive ``.. badges:: stable new`` so that badges are rendered
automatically in generated API pages.

Both ``-`` and ``=`` underlines are accepted, matching standard numpy convention.
"""

from __future__ import annotations

import re
from typing import Any

# Regex for a numpy-style section underline (at least 2 dashes or equals).
_UNDERLINE_RE = re.compile(r"^[-=]{2,}\s*$")


def _extract_badges_section(lines: list[str]) -> tuple[list[str], list[str]]:
    """Scan *lines* for a ``Badges`` section and return ``(badge_ids, cleaned)``.

    The section is removed from ``cleaned``.  Leading/trailing blank lines that
    were only there to separate the section are also removed.
    """
    badge_ids: list[str] = []
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect "Badges" header followed by an underline on the next line.
        if (
            line.strip().lower() == "badges"
            and i + 1 < len(lines)
            and _UNDERLINE_RE.match(lines[i + 1].strip())
        ):
            i += 2  # skip "Badges" + underline

            # Collect non-blank lines as badge ID tokens.
            while i < len(lines) and lines[i].strip():
                badge_ids.extend(lines[i].split())
                i += 1

            # Skip the trailing blank line belonging to the section.
            if i < len(lines) and not lines[i].strip():
                i += 1

            continue  # do NOT append the section to out

        out.append(line)
        i += 1

    return badge_ids, out


def process_docstring(
    app: Any,
    obj_type: str,
    full_name: str,
    obj: Any,
    options: Any,
    lines: list[str],
) -> None:
    """``autodoc-process-docstring`` handler.

    Parses the numpy-style ``Badges`` section from *lines*, removes it, and
    injects a ``.. badges::`` directive immediately after the first paragraph
    so that autosummary can still extract the opening summary line.
    """
    badge_ids, cleaned = _extract_badges_section(lines)
    if not badge_ids:
        return

    # Rewrite lines in-place.
    lines[:] = cleaned

    # Insert ``.. badges:: id1 id2`` after the first paragraph so that
    # autosummary can still extract the opening summary line from the
    # docstring.  The ``badges_position = "top"`` doctree transform handles
    # visual reordering when needed.
    first_blank = next((i for i, ln in enumerate(lines) if not ln.strip()), len(lines))
    lines.insert(first_blank, "")
    lines.insert(first_blank, f".. badges:: {' '.join(badge_ids)}")

    # Register badge metadata on the environment so the filter can find it.
    env = app.env
    if env is not None:
        if not hasattr(env, "badges_all_data"):
            env.badges_all_data = {}
        # autodoc docnames follow the same docname convention as source files.
        docname = getattr(env, "docname", None)
        if docname:
            env.badges_all_data.setdefault(docname, set()).update(badge_ids)
