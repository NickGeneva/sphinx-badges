"""Custom docutils nodes for sphinx-badges."""

from docutils import nodes


class badge(nodes.General, nodes.Inline, nodes.Element):
    """A single badge node.

    Attributes:
        badge_id (str): The badge identifier (key in ``badges_definitions``).
    """


class badge_list(nodes.General, nodes.Element):
    """Container node for a group of badges produced by ``.. badges::``."""


class badge_filter(nodes.General, nodes.Element):
    """Placeholder node for the interactive toctree filter widget.

    Attributes:
        badge_ids (list[str]): Badge IDs offered as filter buttons.
        filter_mode (str): ``'and'`` (default) or ``'or'``.
    """
