"""Inline role for sphinx-badges."""

from sphinx.util.docutils import SphinxRole

from .nodes import badge


class BadgeRole(SphinxRole):
    """Inline badge role.

    Usage::

        This function is :badge:`stable`.

        Override the displayed label: :badge:`Stable Release <stable>`.
    """

    def run(self):
        import re

        text = self.text
        # Support "Label <id>" syntax.
        m = re.match(r"^(.+?)\s+<([^>]+)>\s*$", text)
        if m:
            label_override, badge_id = m.group(1).strip(), m.group(2).strip()
        else:
            badge_id = text.strip()
            label_override = None

        node = badge()
        node["badge_id"] = badge_id
        if label_override:
            node["label_override"] = label_override

        # Register in environment metadata.
        if not hasattr(self.env, "badges_all_data"):
            self.env.badges_all_data = {}
        self.env.badges_all_data.setdefault(self.env.docname, set()).add(badge_id)

        return [node], []
