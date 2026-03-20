sphinx-badges
=============

Bootstrap-style status badges for `Sphinx <https://www.sphinx-doc.org/>`_
documentation. Attach coloured badges to any API element, and let readers
filter a toctree by badge group with a single click.

Installation
------------

.. code-block:: bash

   pip install git+https://github.com/NickGeneva/sphinx-badges.git

Quick start
-----------

1. Add the extension and configure badges in ``conf.py``:

   .. code-block:: python

      extensions = ["sphinx_badges"]

      badges_group_labels = {"stability": "Stability", "area": "Area"}

      badges_definitions = {
          "stability:stable":       {"label": "Stable",       "color": "#198754", "text_color": "#fff"},
          "stability:experimental": {"label": "Experimental", "color": "#ffc107", "text_color": "#000"},
          "area:core":              {"label": "Core",         "color": "#6f42c1", "text_color": "#fff"},
      }

2. Attach badges to a page and filter a toctree:

   .. code-block:: rst

      my_function
      ===========

      .. badges:: stability:stable area:core

      .. badge-filter:: stability:stable stability:experimental area:core
         :filter-mode: or

         .. toctree::

            api/module_a
            api/module_b


User Guide
----------

For more usage and configuration information

.. toctree::
   :maxdepth: 1

   usage

Examples
--------

.. badge-filter:: stability:stable stability:beta stability:experimental stability:deprecated stability:new area:core area:math area:utils

   .. toctree::
      :maxdepth: 1
      :caption: Example API Reference

      api/stable_function
      api/beta_class
      api/experimental_module
      api/deprecated_helper

.. toctree::
   :maxdepth: 1
   :caption: Example Autodoc Reference
   

   modules/api_summary.rst
