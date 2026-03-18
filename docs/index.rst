sphinx-badges demo
==================

This documentation demonstrates the **sphinx-badges** Sphinx extension.

Quick inline usage with the ``:badge:`` role:
:badge:`stability:stable` :badge:`stability:new`

.. badge-filter:: stability:stable stability:beta stability:experimental stability:deprecated stability:new area:core area:math area:utils

   .. toctree::
      :maxdepth: 1
      :caption: Sample API Reference

      api/stable_function
      api/beta_class
      api/experimental_module
      api/deprecated_helper

.. toctree::
   :maxdepth: 1
   :caption: About

   usage
   api_summary
