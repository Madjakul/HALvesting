.. HALvesting documentation master file, created by
   sphinx-quickstart on Mon Mar 27 16:08:27 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

####################################################
HALvesting: Harvests open scientific papers from HAL
####################################################

HALvesting is a Python project designed to harvest research papers from `Hyper Articles en Ligne (HAL) <https://hal.science/>`_ and turn them into a language modeling dataset.

The latest dump can be found on `HuggingFace <https://huggingface.co/datasets/Madjakul/HALvest-D>`_.


Quickstart
==========

.. toctree::
   :maxdepth: 2

   overview.md
   installation.md
   quickstart.md


Code
====

.. toctree::
   :maxdepth: 1

   halvesting/services/api.rst
   halvesting/services/downloader.rst
   halvesting/services/merger.rst
   halvesting/services/enricher.rst
   halvesting/services/filtering.rst
   halvesting/utils/data/preprocessing.rst
   halvesting/utils/data/postprocessing.rst
   halvesting/utils/kenlm_utils.rst
   halvesting/utils/utils.rst


About
=====

.. toctree::
   :maxdepth: 1

   about.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
