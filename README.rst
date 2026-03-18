sphinx-badges
=============

Bootstrap-style status badges for `Sphinx <https://www.sphinx-doc.org/>`_ documentation.

Attach coloured badges to any API element, and let readers filter a toctree
by badge group with a single click.

.. image:: https://img.shields.io/pypi/v/sphinx-badges
   :alt: PyPI version

Features
--------

- ``.. badges:: stable experimental`` — block directive that renders one or
  more coloured badge chips inline with the surrounding content.
- ``:badge:`stable``` — inline role for badges inside paragraphs.
- ``.. badge-filter:: stable beta deprecated`` — wraps a ``.. toctree::``
  with interactive filter buttons; clicking a badge shows only toctree
  entries whose target page carries that badge.
- Global badge colour/label configuration via ``badges_definitions`` in
  ``conf.py``.
- Five built-in badges: **stable**, **beta**, **experimental**,
  **deprecated**, **new** (all overridable).
- Graceful degradation for LaTeX, text, and man-page builders.

Installation
------------

.. code-block:: bash

   pip install sphinx-badges

Quick start
-----------

1. Add the extension to ``conf.py``:

   .. code-block:: python

      extensions = ["sphinx_badges"]

2. Optionally customise badge colours:

   .. code-block:: python

      badges_definitions = {
          "stable":       {"label": "Stable",       "color": "#198754", "text_color": "#fff"},
          "experimental": {"label": "Experimental", "color": "#ffc107", "text_color": "#000"},
      }

3. Use in your ``.rst`` files:

   .. code-block:: rst

      my_function
      ===========

      .. badges:: stable new

      Description here.  Also inline: :badge:`stable`.

4. Filter a toctree:

   .. code-block:: rst

      .. badge-filter:: stable beta experimental
         :filter-mode: or

         .. toctree::

            api/module_a
            api/module_b

Licence
-------

MIT
