AutoDoc Examples
================

this example shows using sphinx-badges with standard sphinx AutoDoc directives.


.. badge-filter:: stability:stable stability:beta stability:experimental
    stability:deprecated stability:new area:core area:math area:utils
    :filter-mode: or

    .. currentmodule:: datalib
    .. autoclass:: DataProcessor
        :no-index:
        :members: run, preview


.. badge-filter:: stability:stable stability:beta stability:experimental
    :filter-mode: and

    .. automodule:: mathlib
        :no-index:
        :members: add, experimental_sort, legacy_format