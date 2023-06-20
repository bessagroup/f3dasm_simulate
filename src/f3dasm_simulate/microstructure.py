"""
Microstructure module for the f3dasm_simulate package.
"""

#                                                                       Modules
# =============================================================================

from typing import Tuple

from .circle_particles import CircleParticles
from .simulator_part import SimulatorPart
from .sphere_particles import SphereParticles

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


#                                                              Abstract Classes
# =============================================================================


class Microstructure(SimulatorPart):
    def __init__(self, size: float = 0.048, radius_mu: float = 0.003, radius_std: float = 0.0,
                 vol_req: float = 0.3, seed: int = 42):
        self.size = size
        self.radius_mu = radius_mu
        self.radius_std = radius_std
        self.vol_req = vol_req
        self.seed = seed

        self._create_microstructure()

    def _create_microstructure(self) -> Tuple[dict, float]:
        ...

    def to_dict(self) -> dict:
        """Return a dictionary representation of the microstructure.

        Returns
        -------
            Dictionary representation of the microstructure
            for the SimulatorInfo
        """
        microstructure_info, vol_frac = self._create_microstructure()
        return {**microstructure_info, "vol_frac": vol_frac}

#                                                               Implementations
# =============================================================================


class CircleMicrostructure(Microstructure):
    def _create_microstructure(self) -> Tuple[dict, float]:
        self.microstructure_generator = CircleParticles(
            length=self.size,
            width=self.size,
            radius_mu=self.radius_mu,
            radius_std=self.radius_std,
            vol_req=self.vol_req,
            dist_min_factor=1.2,
        )
        self.microstructure_generator.generate_microstructure(seed=self.seed)
        microstructure_info = self.microstructure_generator.to_abaqus_format(
            file_name="micro_structure.json"
        )
        self.microstructure_generator.plot_microstructure(save_figure=True)

        return microstructure_info, self.microstructure_generator.vol_frac


class SphereMicrostructure(Microstructure):
    def _create_microstructure(self) -> Tuple[dict, float]:
        self.microstructure_generator = SphereParticles(
            length=self.size,
            width=self.size,
            height=self.size,
            radius_mu=self.radius_mu,
            radius_std=self.radius_std,
            vol_req=self.vol_req,
        )
        self.microstructure_generator.generate_microstructure(seed=self.seed)
        microstructure_info = self.microstructure_generator.to_abaqus_format(
            file_name="micro_structure.json"
        )
        return microstructure_info, self.microstructure_generator.vol_frac
