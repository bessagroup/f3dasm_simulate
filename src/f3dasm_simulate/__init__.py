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
import logging

from . import abaqus

# Third-party


#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================

__version__ = '1.1.0'

# Create a logger
logger = logging.getLogger("f3dasm_simulate")

# Log welcome message and the version of f3dasm_simulate
logger.info(f"Imported f3dasm_simulate (version: {__version__})")
