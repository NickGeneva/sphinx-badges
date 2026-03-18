# sphinx-badges

Bootstrap-style status badges for [Sphinx](https://www.sphinx-doc.org/) documentation.

Attach coloured badges to any API element, and let readers filter a toctree
by badge group with a single click.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-badges)](https://pypi.org/project/sphinx-badges/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Ruff Format](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://github.com/astral-sh/ruff)
[Documentation](https://NickGeneva.github.io/sphinx-badges/)

## Installation

Directly from GitHub (latest development version):

```bash
pip install git+https://github.com/NickGeneva/sphinx-badges.git
```

## Quick start

1. Add the extension to `conf.py`:

   ```python
   extensions = ["sphinx_badges"]
   ```

2. Define grouped badges in `conf.py`:

   ```python
   badges_group_labels = {
       "stability": "Stability",
       "area":      "Area",
   }

   badges_definitions = {
       "stability:stable":       {"label": "Stable",       "color": "#198754", "text_color": "#fff"},
       "stability:experimental": {"label": "Experimental", "color": "#ffc107", "text_color": "#000"},
       "area:core":              {"label": "Core",         "color": "#6f42c1", "text_color": "#fff"},
       "area:utils":             {"label": "Utils",        "color": "#fd7e14", "text_color": "#fff"},
   }
   ```

   Badge IDs use a `group:name` format. `badges_group_labels` maps group keys to the
   display labels shown above each row of filter buttons. Ungrouped IDs (no colon) are
   also supported for simpler setups.

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

## Licence

MIT
