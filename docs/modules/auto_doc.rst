AutoDoc Examples
================

This page demonstrates ``.. badge-filter::`` used directly with standard
``sphinx.ext.autodoc`` directives (``.. autoclass::`` and
``.. automodule::``), without a separate autosummary table.

Unlike toctree or autosummary filtering — where badges are looked up from a
per-page index — autodoc filtering works entirely in the DOM: badge IDs are
read directly from the rendered badge spans already present on the page.

Each individual member block (method, function, attribute, …) is a
filterable unit.  Class containers (``dl.py.class``) are intentionally kept
visible at all times so their remaining members are always accessible.

Filtering class members (OR mode)
----------------------------------

The filter below wraps ``DataProcessor`` and shows only the two explicitly
listed methods.  Clicking a stability or area button hides methods that do
not carry that badge.  Because OR mode is active, selecting multiple badges
broadens the visible set.

.. badge-filter:: stability:stable stability:beta stability:experimental
    stability:deprecated stability:new area:core area:math area:utils
   :filter-mode: or

   .. currentmodule:: datalib

   .. autoclass:: DataProcessor
      :no-index:
      :members: run, preview, validate, merge, to_dict, filter_records, summarize


Filtering module functions (AND mode)
--------------------------------------

The filter below wraps the ``mathlib`` module.  In AND mode all active
badges must be present simultaneously, so selecting two badges from
different groups quickly narrows the list to a precise match.

.. badge-filter:: stability:stable stability:beta stability:experimental
    stability:deprecated stability:new area:core area:math area:utils
    :filter-mode: and

    .. currentmodule:: datalib

    .. automodule:: datalib
        :no-index:
        :members:
        :inherited-members:
