Userguide
=========

Installation
------------

.. code-block:: bash

   pip install sphinx-badges

Or with uv:

.. code-block:: bash

   uv add sphinx-badges

Add the extension to ``conf.py``::

   extensions = ["sphinx_badges"]

Configuration
-------------

Define badge colours in ``conf.py``:

.. code-block:: python

   badges_definitions = {
       "stable": {
           "label": "Stable",
           "color": "#198754",
           "text_color": "#ffffff",
       },
       "beta": {
           "label": "Beta",
           "color": "#0dcaf0",
           "text_color": "#000000",
       },
   }

   # Colour used for any badge ID not listed above
   badges_default_color = "#6c757d"

Built-in badges (no configuration required):
``stable``, ``beta``, ``experimental``, ``deprecated``, ``new``.

Adding badges to a page
-----------------------

Use the ``.. badges::`` block directive anywhere in a ``.rst`` file:

.. code-block:: rst

   my_function
   ===========

   .. badges:: stable new

   Description of the function.

Use the ``:badge:`` inline role inside a paragraph:

.. code-block:: rst

   This class is :badge:`stable` and :badge:`new`.

Override the displayed label with ``Label <id>`` syntax:

.. code-block:: rst

   :badge:`Stable Release <stable>`

Filtering a toctree
-------------------

Wrap any ``.. toctree::`` with ``.. badge-filter::`` to add interactive
filter buttons above it:

.. code-block:: rst

   .. badge-filter:: stable beta deprecated
      :filter-mode: or

      .. toctree::
         :maxdepth: 1

         api/module_a
         api/module_b
         api/module_c

Options:

``filter-mode``
   ``and`` *(default)* — show entries whose page carries **all** active
   badges simultaneously.

   ``or`` — show entries whose page carries **any** of the active badges.

``badge-order-fixed``
   When present, the badge chips displayed next to each toctree entry or
   autosummary row are re-sorted to match the order in which badge IDs are
   listed on the ``.. badge-filter::`` directive, rather than the order they
   appear in the object's docstring or RST source.

   This is useful when badge IDs are written in inconsistent order across
   docstrings.  Without this option, one entry might show
   ``stability:beta area:core`` while another shows ``area:utils stability:stable``,
   making the table harder to scan.  With ``:badge-order-fixed:`` every row
   follows the same left-to-right order:

   .. code-block:: rst

      .. badge-filter:: area:core area:math area:utils stability:stable stability:beta
         :filter-mode: or
         :badge-order-fixed:

         .. toctree::
            :maxdepth: 1

            api/module_a
            api/module_b

   Regardless of how each object's docstring lists its badges, the chips in
   the table always appear in ``area:…`` then ``stability:…`` order.

   Badges not mentioned in the filter list are appended after the ordered
   ones in their original docstring order.

``group-visibility-toggle``
   Requires grouped mode (all badge IDs carry a ``group:name`` prefix).
   When present, an eye icon button is rendered to the left of each group
   label.  Clicking the button hides all badge chips belonging to that group
   from every entry in the filter content; clicking again restores them.

   This is useful when the filter has many groups and the badge chips in the
   content area become visually noisy — readers can collapse groups they are
   not currently interested in.

   .. code-block:: rst

      .. badge-filter:: area:core area:math stability:stable stability:beta
         :group-visibility-toggle:

         .. toctree::
            :maxdepth: 1

            api/module_a
            api/module_b

   .. note::

      The toggle only hides the badge *chips* annotated on each entry; it
      does not affect which entries are shown or hidden by the active filter
      buttons.

``group-hidden``
   Space-separated list of group keys whose badge chips should be hidden
   when the page first loads.  This is a convenience companion to
   ``:group-visibility-toggle:`` — the named groups start in the
   collapsed (closed-eye) state without requiring the reader to click.

   .. code-block:: rst

      .. badge-filter:: area:core area:math stability:stable stability:beta
         :group-visibility-toggle:
         :group-hidden: area

         .. toctree::
            :maxdepth: 1

            api/module_a
            api/module_b

   In the example above the ``area`` group is hidden on load; the
   ``stability`` group is visible.  Both can be toggled interactively
   because ``:group-visibility-toggle:`` is also set.

   ``:group-hidden:`` can list multiple groups separated by spaces:

   .. code-block:: rst

      :group-hidden: area platform

Badge position in API blocks
----------------------------

By default ``.. badges::`` renders where it appears in the RST source.
Set ``badges_position`` in ``conf.py`` to ``"top"`` to automatically move
all badges to the top of their enclosing API block (``py:class``,
``py:function``, etc.), regardless of where the directive is written:

.. code-block:: python

   badges_position = "top"    # move above the description (recommended)
   badges_position = "bottom" # leave in source order (default)

This applies to both hand-written RST and autodoc-generated pages.

Badge style
-----------

Set ``badges_style`` in ``conf.py`` to change the visual style of all badges:

.. code-block:: python

   badges_style = "rounded"   # default — Bootstrap-style rounded corners
   badges_style = "square"    # Material Design — no border radius
   badges_style = "pill"      # fully pill-shaped

Numpy-style docstrings (autodoc)
---------------------------------

With ``sphinx.ext.autodoc`` active, add a ``Badges`` section to any
numpy-style docstring:

.. code-block:: python

   def my_function(x, y):
       """Return the sum.

       Parameters
       ----------
       x : float
           First operand.

       Badges
       ------
       stable new
       """
       return x + y

The extension parses the section, removes it from the rendered output, and
injects ``.. badges:: stable new`` at the top of the docstring automatically.

Autosummary table filter
------------------------

Wrap ``.. autosummary::`` with ``.. badge-filter::`` to add filter controls
above the generated table:

.. code-block:: rst

   .. badge-filter:: stable beta experimental
      :filter-mode: or

      .. autosummary::
         :toctree: generated/

         ...

Clicking a filter button hides rows whose target page does not carry the
selected badge.  Works alongside toctree filtering on the same page.

Group labels and tooltips
-------------------------

Each group in ``badges_group_labels`` can carry a ``tooltip``.  The
tooltip text appears when the user hovers over the **group label** in the
filter widget.  Group labels use the default pointer cursor and are not
text-selectable, keeping them visually distinct from content text.

.. code-block:: python

   badges_group_labels = {
       "stability": {
           "label": "Stability",
           "tooltip": "API stability level",
       },
       "area": {
           "label": "Area",
           "tooltip": "Functional area",
       },
   }

A plain string value (``"stability": "Stability"``) still works and is
equivalent to omitting ``tooltip``.

Icons belong on individual badge definitions in ``badges_definitions``,
not on the group.  This lets each badge in a group carry a distinct icon:

.. code-block:: python

   badges_definitions = {
       "area:core": {"label": "Core", "color": "#6f42c1", "text_color": "#ffffff", "icon": "📦"},
       "area:math": {"label": "Math", "color": "#20c997", "text_color": "#000000", "icon": "📐"},
       "area:utils": {"label": "Utils", "color": "#fd7e14", "text_color": "#ffffff", "icon": "🔧"},
   }

With the config above, the area badges render like this:

.. badges:: area:core area:math area:utils

Icon-only badges
~~~~~~~~~~~~~~~~

Set ``"label": ""`` on an individual badge definition to suppress its
text — only the icon is displayed.  This is useful for compact platform
or tag indicators:

.. code-block:: python

   badges_group_labels = {
       "platform": {
           "label": "Platform",
           "tooltip": "Supported runtime platform",
       },
   }

   badges_definitions = {
       "platform:python": {
           "label": "",        # no text — only the badge-level icon shows
           "color": "#3572A5",
           "text_color": "#ffffff",
           "icon": "🐍",
           "tooltip": "Python",
       },
       "platform:cli": {
           "label": "CLI",     # icon + text
           "color": "#212529",
           "text_color": "#ffffff",
           "icon": "⌨️",
       },
   }

With those definitions:

.. badges:: platform:python platform:cli

Priority order for a badge's prefix: per-badge ``icon`` in
``badges_definitions`` → group-level ``icon`` → no prefix.  Per-badge
``tooltip`` in ``badges_definitions`` overrides the group ``tooltip``.

HTML element icons
~~~~~~~~~~~~~~~~~~

The ``icon`` field accepts any raw HTML string, including icon-font elements
such as `Font Awesome <https://fontawesome.com>`_ or `Bootstrap <https://icons.getbootstrap.com/>`_.
The value is injected verbatim inside the badge ``<span>``, so any self-contained HTML
fragment works:

.. code-block:: python

   badges_definitions = {
       "platform:mobile": {
           "label": "Mobile",
           "color": "#3DDC84",
           "text_color": "#ffffff",
           "icon": '<i class="fa-solid fa-android"></i>',
       },
       "platform:web": {
           "label": "",          # icon-only
           "color": "#0d6efd",
           "text_color": "#ffffff",
           "icon": '<i class="fa-brands fa-chrome"></i>',
           "tooltip": "Web",
       },
   }

With those definitions:

.. badges:: platform:mobile platform:web

To make third-party icons (e.g. FontAwesome) visible you must load its stylesheet.
Add the CDN link to ``conf.py``:

.. code-block:: python

   # conf.py
   html_css_files = [
       "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css",
   ]

Or, if you host the assets locally, copy them into ``docs/_static/`` and
reference the local path instead:

.. code-block:: python

   html_css_files = [
       "fontawesome/css/all.min.css",
   ]

.. note::

   HTML element icons are only needed when you want scalable vector icons from an icon
   font or inline SVG. Emoji strings (``"📦"``) and plain text work as demonstrated
   above.

Inline role with icons
~~~~~~~~~~~~~~~~~~~~~~

The ``:badge:`` role picks up icons and tooltips automatically:

.. code-block:: rst

   This function is :badge:`stability:stable` and targets :badge:`platform:python`.

Which renders as: :badge:`stability:stable` and :badge:`platform:python` — hover each to see its tooltip.

How it works
------------

When the HTML build finishes, the extension writes
``_static/badge-data.js`` containing a mapping of every page to its
badges.  The browser-side JavaScript reads this file, appends badge chips
to each toctree entry, and shows or hides entries as the user clicks the
filter buttons.
