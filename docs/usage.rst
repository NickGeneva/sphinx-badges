Usage
=====

Installation
------------

.. code-block:: bash

   pip install sphinx-badges

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

         mylib.DataProcessor
         mylib.add

Clicking a filter button hides rows whose target page does not carry the
selected badge.  Works alongside toctree filtering on the same page.

How it works
------------

When the HTML build finishes, the extension writes
``_static/badge-data.js`` containing a mapping of every page to its
badges.  The browser-side JavaScript reads this file, appends badge chips
to each toctree entry, and shows or hides entries as the user clicks the
filter buttons.
