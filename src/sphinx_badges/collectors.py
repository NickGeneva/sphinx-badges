"""Sphinx event handlers for collecting and merging badge metadata."""


def init_badge_env(app):
    """Initialise badge metadata stores on the environment."""
    if not hasattr(app.env, "badges_all_data"):
        app.env.badges_all_data = {}


def purge_badges(app, env, docname):
    """Remove stale badge metadata for *docname* before it is re-read."""
    if hasattr(env, "badges_all_data"):
        env.badges_all_data.pop(docname, None)


def merge_badges(app, env, docnames, other):
    """Merge badge metadata from a parallel-read worker environment."""
    if hasattr(other, "badges_all_data"):
        if not hasattr(env, "badges_all_data"):
            env.badges_all_data = {}
        for docname, badge_ids in other.badges_all_data.items():
            lst = env.badges_all_data.setdefault(docname, [])
            existing = set(lst)
            for bid in badge_ids:
                if bid not in existing:
                    lst.append(bid)
                    existing.add(bid)
