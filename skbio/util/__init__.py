"""
Utility functionality (:mod:`skbio.util`)
=========================================

.. currentmodule:: skbio.util

This package provides general exception/warning definitions used throughout
scikit-bio, as well as various utility functionality, including I/O and
unit-testing convenience functions.

Testing functionality
---------------------

Common functionality to support testing in skbio.

.. autosummary::
   :toctree: generated/

   get_data_path
   TestRunner
   assert_ordination_results_equal
   assert_data_frame_almost_equal

Miscellaneous functionality
---------------------------

Generally useful functions that don't fit in more specific locations.

.. autosummary::
   :toctree: generated/

   cardinal_to_ordinal
   create_dir
   find_duplicates
   is_casava_v180_or_later
   remove_files
   safe_md5

Warnings
--------

.. autosummary::
   :toctree: generated/

   EfficiencyWarning
   RepresentationWarning

"""

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

from ._warning import EfficiencyWarning, RepresentationWarning, SkbioWarning
from ._misc import (cardinal_to_ordinal, create_dir, find_duplicates,
                    is_casava_v180_or_later, remove_files, safe_md5)
from ._testing import (get_data_path, TestRunner,
                       assert_ordination_results_equal,
                       assert_data_frame_almost_equal)
from ._decorator import classproperty

__all__ = ['SkbioWarning', 'EfficiencyWarning', 'RepresentationWarning',
           'cardinal_to_ordinal', 'create_dir', 'find_duplicates',
           'is_casava_v180_or_later', 'remove_files', 'safe_md5',
           'get_data_path', 'TestRunner', 'assert_ordination_results_equal',
           'assert_data_frame_almost_equal', 'classproperty']

test = TestRunner(__file__).test
