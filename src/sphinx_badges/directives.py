"""Directives for sphinx-badges."""

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .nodes import badge, badge_list, badge_filter


class BadgesDirective(SphinxDirective):
    """Add one or more badges to an API element.

    Usage::

        .. badges:: stable experimental

        .. py:function:: my_function()

           Description.

           .. badges:: stable
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {}

    def run(self):
        badge_ids = self.arguments[0].split()

        container = badge_list()
        for bid in badge_ids:
            bid = bid.strip()
            if bid:
                node = badge()
                node["badge_id"] = bid
                container += node

        # Store metadata on the environment for the filter feature.
        if not hasattr(self.env, "badges_all_data"):
            self.env.badges_all_data = {}
        docname = self.env.docname
        self.env.badges_all_data.setdefault(docname, set()).update(badge_ids)

        return [container]


class BadgeFilterDirective(SphinxDirective):
    """Wrap a toctree with interactive badge filter controls.

    Usage::

        .. badge-filter:: stable experimental deprecated
           :filter-mode: or

           .. toctree::
              :maxdepth: 1

              module_a
              module_b
              module_c

    Options:
        filter-mode: ``and`` (default) — show pages that have **all** active
            badges.  ``or`` — show pages that have **any** active badge.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "filter-mode": lambda x: directives.choice(x, ("and", "or")),
    }

    def run(self):
        badge_ids = [b.strip() for b in self.arguments[0].split() if b.strip()]

        node = badge_filter()
        node["badge_ids"] = badge_ids
        node["filter_mode"] = self.options.get("filter-mode", "and")

        # Parse the nested toctree (or any other content).
        self.state.nested_parse(self.content, self.content_offset, node)

        return [node]
