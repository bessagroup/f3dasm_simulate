"""
Loading conditions for the simulation.
"""

#                                                                       Modules
# =============================================================================

from typing import List

from .amplitudesampler import AmplitudeGenerator
from .simulator_part import SimulatorPart

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class Loading(SimulatorPart):
    def to_dict(self) -> dict:
        """Return a dictionary representation of the loading conditions.

        Returns
        -------
            Dictionary representation of the loading conditions
            for the SimulatorInfo
        """
        ...

#                                                               Implementations
# =============================================================================


class PathLoading(Loading):
    def __init__(self, amplitude_generator: AmplitudeGenerator = AmplitudeGenerator(),
                 strain: List[float] = [0.02, 0.02, 0.02]):
        self.amplitude_generator = amplitude_generator
        self.strain = strain

    def to_dict(self):
        return {'strain_amplitude': self.amplitude_generator.get_amplitude(),
                'strain': self.strain}


class RegularLoading(Loading):
    def __init__(self, strain: List[float] = [0.02, 0.02, 0.02]):
        self.strain = strain

    def to_dict(self):
        return {'strain': self.strain}
