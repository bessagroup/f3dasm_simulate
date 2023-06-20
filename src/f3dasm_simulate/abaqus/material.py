"""
Material module for the simulation
"""

#                                                                       Modules
# =============================================================================

# Standard
from abc import ABC
from typing import List

# Third party
import matplotlib.pyplot as plt
import numpy as np

# Local
from .simulator_part import SimulatorPart

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


#                                                                  Base Classes
# =============================================================================

class Material(SimulatorPart):
    def to_dict(self) -> dict:
        """Return a dictionary representation of the material.

        Returns
        -------
            Dictionary representation of the material for the SimulatorInfo
        """
        ...


class CompositeMaterial(SimulatorPart):
    def __init__(self, matrix_material: Material, fiber_material: Material):
        self.matrix_material = matrix_material
        self.fiber_material = fiber_material

    def to_dict(self) -> dict:
        # Set the right suffix for the keys
        self.matrix_material.suffix = "_matrix"
        self.fiber_material.suffix = "_fiber"

        # Create the combined material dictionary
        # This doesnt work with two materials that have a hardening law
        return {**self.matrix_material.to_dict(),
                **self.fiber_material.to_dict()}


class HardeningLaw(ABC):
    def __init__(self, *args, **kwargs):
        self._calculate_hardening_table()

    @property
    def hardening_law_table(self) -> List[float]:
        return self._calculate_hardening_table()

    def _calculate_hardening_table(self) -> List[float]:
        ...

    def plot(self, **kwargs):
        "plot the hardening law"
        hardening_law_table = self.hardening_law_table
        fig, ax = plt.subplots(**kwargs)
        ax.plot(
            hardening_law_table[1, :],
            hardening_law_table[0, :],
            label="hardening_law",
        )
        plt.legend()
        plt.xlabel(r"$\varepsilon$")
        plt.ylabel(r"$\sigma$")
        plt.xlim([0, 1])
        plt.grid("-.")
        plt.show()

#                                                                Hardening laws
# =============================================================================


class LinearHardeningLaw(HardeningLaw):
    def __init__(self, a: float = 0.5, yield_stress: float = 0.5):
        self.a = a
        self.yield_stress = yield_stress

        super().__init__()

    def _calculate_hardening_table(self) -> List[float]:
        # get the arguements
        yield_stress = self.yield_stress
        a = self.a
        # dfine the table for hardening law
        hardening_law_table = np.zeros((101, 2))
        hardening_law_table[:, 1] = np.linspace(0, 1, 101)

        # generate the hardening law
        hardening_law_table[:, 0] = (
            yield_stress + a * hardening_law_table[:, 1]
        )
        hardening_law_table[-1, 1] = 10.0
        hardening_law_table[-1, 0] = (
            yield_stress + a * hardening_law_table[-1, 1]
        )

        hardening_law_table = hardening_law_table.T
        return hardening_law_table.tolist()


class SwiftHardeningLaw(HardeningLaw):
    def __init__(self, a: float = 0.2, b: float = 0.4, yield_stress: float = 0.5):
        self.a = a
        self.b = b
        self.yield_stress = yield_stress

        super().__init__()

    def _calculate_hardening_table(self) -> List[float]:
        # get the arguements
        yield_stress = self.yield_stress
        a = self.a
        b = self.b
        # dfine the table for hardening law
        hardening_law_table = np.zeros((101, 2))
        hardening_law_table[:, 1] = np.linspace(0, 1, 101)
        # generate the hardening law
        hardening_law_table[:, 0] = (
            yield_stress + a * (hardening_law_table[:, 1]) ** b
        )
        hardening_law_table[-1, 1] = 10.0
        hardening_law_table[-1, 0] = (
            yield_stress + a * (hardening_law_table[-1, 1]) ** b
        )
        hardening_law_table = hardening_law_table.T
        return hardening_law_table.tolist()


class RambergHardeningLaw(HardeningLaw):
    def __init__(self, a: float = 0.2, b: float = 0.4, yield_stress: float = 0.5):
        self.a = a
        self.b = b
        self.yield_stress = yield_stress

        super().__init__()

    def _calculate_hardening_table(self) -> List[float]:
        # get the arguements
        yield_stress = self.yield_stress
        a = self.a
        b = self.b
        # define the table for hardening law
        hardening_law_table = np.zeros((101, 2))
        hardening_law_table[:, 1] = np.linspace(0, 1, 101)

        # generate the hardening law
        hardening_law_table[:, 0] = yield_stress * (
            1 + a * (hardening_law_table[:, 1])
        ) ** (1 / b)
        hardening_law_table[-1, 1] = 10.0
        hardening_law_table[-1, 0] = yield_stress * (
            1 + a * (hardening_law_table[-1, 1])
        ) ** (1 / b)

        hardening_law_table = hardening_law_table.T
        return hardening_law_table.tolist()

#                                                           Material Subclasses
# =============================================================================


class ElasticMaterial(Material):
    def __init__(self, youngs_modulus: float = 1.0, poisson_ratio: float = 0.19):
        self.youngs_modulus = youngs_modulus
        self.poisson_ratio = poisson_ratio
        self.suffix = ""

    def to_dict(self) -> dict:
        return {f"youngs_modulus{self.suffix}": self.youngs_modulus,
                f"poisson_ratio{self.suffix}": self.poisson_ratio}


class PlasticMaterial(Material):
    def __init__(self, hardening_law: HardeningLaw = LinearHardeningLaw(),
                 youngs_modulus: float = 100.0, poisson_ratio: float = 0.3):
        self.hardening_law = hardening_law
        self.youngs_modulus = youngs_modulus
        self.poisson_ratio = poisson_ratio
        self.suffix = ""

    def to_dict(self) -> dict:
        return {f"youngs_modulus{self.suffix}": self.youngs_modulus,
                f"poisson_ratio{self.suffix}": self.poisson_ratio,
                'hardening_table': self.hardening_law.hardening_law_table}
