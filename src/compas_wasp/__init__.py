"""
********************************************************************************
compas_wasp
********************************************************************************

.. currentmodule:: compas_wasp


.. toctree::
    :maxdepth: 1

    compas_wasp.datastructures


"""

from __future__ import print_function

import os
import sys


__author__ = ['andrearossi <Your email>']
__copyright__ = 'Andrea Rossi'
__license__ = 'MIT License'
__email__ = 'Your email'
__version__ = '0.1.0'


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


__all__ = ['HOME', 'DATA', 'DOCS', 'TEMP']


