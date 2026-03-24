"""Directives for sphinx-badges."""

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .nodes import badge, badge_filter, badge_list


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
        # Use a list (not a set) so insertion order — which matches docstring
        # order — is preserved for SPHINX_BADGES_DATA in badge-data.js.
        if not hasattr(self.env, "badges_all_data"):
            self.env.badges_all_data = {}
        docname = self.env.docname
        lst = self.env.badges_all_data.setdefault(docname, [])
        for bid in badge_ids:
            if bid not in lst:
                lst.append(bid)

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
        "badge-order-fixed": directives.flag,
        "group-visibility-toggle": directives.flag,
        "group-hidden": directives.unchanged,
    }

    def run(self):
        badge_ids = [b.strip() for b in self.arguments[0].split() if b.strip()]

        node = badge_filter()
        node["badge_ids"] = badge_ids
        node["filter_mode"] = self.options.get("filter-mode", "and")

        # When :badge-order-fixed: is set, store the canonical badge order on
        # the node so the HTML visitor can emit it as a data attribute.  The JS
        # filter widget then re-sorts each entry's badge chips to match this
        # order rather than the docstring insertion order.
        if "badge-order-fixed" in self.options:
            node["badge_order"] = badge_ids

        if "group-visibility-toggle" in self.options:
            node["group_visibility_toggle"] = True

        raw_hidden = self.options.get("group-hidden", "")
        hidden_groups = [g.strip() for g in raw_hidden.split() if g.strip()]
        if hidden_groups:
            node["groups_hidden"] = hidden_groups

        # Parse the nested toctree (or any other content).
        self.state.nested_parse(self.content, self.content_offset, node)

        return [node]
