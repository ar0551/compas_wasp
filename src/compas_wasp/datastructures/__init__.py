"""
********************************************************************************
compas_wasp.datastructures
********************************************************************************

.. currentmodule:: compas_wasp.datastructures


Description...


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Aggregation
    Connection
    Part
    Rule


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:




"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas

from .aggregation import *
from .connection import *
from .part import *
from .rule import *

if not compas.IPY:
    pass

__all__ = [name for name in dir() if not name.startswith('_')]