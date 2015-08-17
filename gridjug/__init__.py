# coding: utf-8
"""
See Also
--------

`GridMap <https://github.com/pygridtools/gridmap>`_
    Easily map Python functions onto a cluster using a DRMAA-compatible grid
    engine like Sun Grid Engine (SGE).

`Jug <http://luispedro.org/software/jug/>`_
    A Task-Based Parallelization Framework

"""

from __future__ import absolute_import, division, print_function


import pkg_resources
from gridjug.gridjug import grid_jug

__version__ = pkg_resources.get_distribution(__name__).version
