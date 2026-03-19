# sphinx-badges

Bootstrap-style status badges for [Sphinx](https://www.sphinx-doc.org/) documentation.

Attach coloured badges to any API element, filter a toctree or autosummary table
by badge group with a single click, and add per-group icons and tooltips to make
status immediately scannable.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-badges)](https://pypi.org/project/sphinx-badges/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Ruff Format](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://github.com/astral-sh/ruff)

[Documentation](https://NickGeneva.github.io/sphinx-badges/)

## Installation

```bash
pip install sphinx-badges
```

Or with uv:

```bash
uv add sphinx-badges
```

## Quick start

1. Add the extension to `conf.py`:

   ```python
   extensions = ["sphinx_badges"]
   ```

2. Define grouped badges in `conf.py`:

   ```python
   badges_group_labels = {
       "stability": {
           "label": "Stability",
           "tooltip": "API stability level",
           "icon": "⚡",        # prepended to every badge in this group
       },
       "area": {
           "label": "Area",
           "tooltip": "Functional area",
       },
   }

   badges_definitions = {
       "stability:stable":       {"label": "Stable",       "color": "#198754", "text_color": "#fff"},
       "stability:experimental": {"label": "Experimental", "color": "#ffc107", "text_color": "#000"},
       "area:core":              {"label": "Core",         "color": "#6f42c1", "text_color": "#fff"},
       "area:utils":             {"label": "Utils",        "color": "#fd7e14", "text_color": "#fff"},
   }
   ```

   Badge IDs use a `group:name` format. `badges_group_labels` maps group keys to
   display labels shown above each row of filter buttons. Each group can also carry
   an `icon` (prepended to every badge in the group) and a `tooltip` (shown on
   hover). Per-badge `icon` and `tooltip` can be set directly in
   `badges_definitions` to override the group-level values.

   Ungrouped IDs (no colon) are also supported for simpler setups.

3. Attach badges to a page:

   ```rst
   my_function
   ===========

   .. badges:: stability:stable area:core

   Description here.  Also inline: :badge:`stability:stable`.
   ```

4. Filter a toctree by badge group:

   ```rst
   .. badge-filter:: stability:stable stability:experimental area:core area:utils
      :filter-mode: or

      .. toctree::

         api/module_a
         api/module_b
   ```

   Each group renders as its own labelled row of filter buttons.
   `filter-mode` can be `or` (any active badge matches) or `and`
   (all active badges must match; default).

5. Add badges via numpy-style docstrings (autodoc):

   ```python
   def my_function(x, y):
       """Return the sum.

       Badges
       ------
       stability:stable area:core
       """
   ```

## Licence

MIT
