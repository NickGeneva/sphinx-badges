RST API Examples
================

This page demonstrates badge filtering with API entries defined entirely in
hand-written RST — no ``autodoc`` or ``autosummary`` involved.  Each child
page carries one or more ``.. badges::`` directives that tag it with
stability and area labels.  The filter widget below reads those tags and
shows or hides entries as you click the buttons.

The badge list for each filter row uses **OR** within a row and **AND**
across rows, matching the typical "show me everything that is stable *and*
in the core area" use-case.

.. badge-filter:: stability:stable stability:beta stability:experimental stability:deprecated
    stability:new area:core area:math area:utils

   .. toctree::
      :maxdepth: 1
      :caption: Example API Reference

      api/stable_function
      api/beta_class
      api/experimental_module
      api/deprecated_helper
