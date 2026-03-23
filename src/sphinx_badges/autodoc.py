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
    #
    # RST requires a blank line on both sides of a block directive.  We
    # insert AFTER the first blank (so the existing blank acts as the
    # preceding separator) then add a trailing blank.  For one-liner
    # docstrings with no blank line we append one first.
    first_blank = next((i for i, ln in enumerate(lines) if not ln.strip()), len(lines))
    if first_blank == len(lines):
        lines.append("")
        first_blank = len(lines) - 1
    lines.insert(first_blank + 1, "")  # trailing blank after directive
    lines.insert(first_blank + 1, f".. badges:: {' '.join(badge_ids)}")

    # Register badge metadata so the JS filter can find this page.
    # This must be done here rather than relying solely on BadgesDirective.run()
    # because the injected ``.. badges::`` directive is processed via
    # nested_parse inside autodoc's content generation, where SphinxDirective's
    # self.env property is not reliably accessible.
    #
    # Guard: only write when this object is the *primary* subject of the
    # current page.  Autosummary stubs have docnames whose last path component
    # equals the full Python name (e.g. "generated/datalib.DataProcessor" for
    # the class).  When a stub's nested ``.. autosummary::`` table fires
    # process_docstring for methods, env.docname still points to the class stub
    # — and we must NOT accumulate those method badges on the class page.
    # Hand-written pages (docname basename contains no ".") are always allowed.
    env = app.env
    if env is not None:
        if not hasattr(env, "badges_all_data"):
            env.badges_all_data = {}
        docname = getattr(env, "docname", None)
        if docname:
            doc_last = docname.rsplit("/", 1)[-1]
            if doc_last == full_name or "." not in doc_last:
                lst = env.badges_all_data.setdefault(docname, [])
                for bid in badge_ids:
                    if bid not in lst:
                        lst.append(bid)
