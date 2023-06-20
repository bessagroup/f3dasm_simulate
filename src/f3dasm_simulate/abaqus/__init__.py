"""
f3dasm_simulate - Simulation extension of f3dasm
the Bessa Group's conventions

This package contains a template for Python packages following
the Bessa Group's conventions.

Usage:
  import f3dasm_simulate

Author: Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)
"""

#                                                                       Modules
# =============================================================================

# Standard

# Third-party

from . import loading, material, microstructure, simulator, simulator_info
# Local
from .cddm import VonMisesPlasticElasticPathLoads
from ..example_module import add_one

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================
