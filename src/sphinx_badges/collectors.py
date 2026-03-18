"""Sphinx event handlers for collecting and merging badge metadata."""


def init_badge_env(app):
    """Initialise ``env.badges_all_data`` on the first build."""
    if not hasattr(app.env, "badges_all_data"):
        app.env.badges_all_data = {}


def purge_badges(app, env, docname):
    """Remove stale badge metadata for *docname* before it is re-read."""
    if hasattr(env, "badges_all_data"):
        env.badges_all_data.pop(docname, None)


def merge_badges(app, env, docnames, other):
    """Merge badge metadata from a parallel-read worker environment."""
    if not hasattr(other, "badges_all_data"):
        return
    if not hasattr(env, "badges_all_data"):
        env.badges_all_data = {}
    for docname, badge_ids in other.badges_all_data.items():
        env.badges_all_data.setdefault(docname, set()).update(badge_ids)
