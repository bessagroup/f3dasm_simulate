"""
SimulatorPart is a protocol that defines the interface for a simulator part.
"""

#                                                                       Modules
# =============================================================================

from typing import Protocol

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class SimulatorPart(Protocol):
    def to_dict(self) -> dict:
        ...
