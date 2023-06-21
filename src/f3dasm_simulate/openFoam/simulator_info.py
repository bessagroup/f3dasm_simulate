"""
Example module
"""

#                                                                       Modules
# =============================================================================

import os

# Standard
from pathlib import Path


# Local
from .boundary import Boundary
from .material import Material
from .geometry import Geometry
from .mesh import Mesh
from .solver import Solver
from .simulator_part import SimulatorPart

#                                                        Authorship and Credits
# =============================================================================
__author__ = "Guillaume Broggi (g.broggi@tudelft.nl)"
__credits__ = ["Guillaume Broggi"]
__status__ = "Alpha"
# =============================================================================
#
# =============================================================================


class SimulationInfo(SimulatorPart):
    def __init__(
        self,
        material: Material,
        geometry: Geometry,
        boundary: Boundary,
        mesh: Mesh,
        solver: Solver,
        case_source_path: Path,
        name: str = None,
        output_data_path: Path = Path("jobs"),
    ):
        self.case_source_path = case_source_path.resolve()
        self.output_data_path = output_data_path.resolve()
        self.output_data_path.mkdir(parents=True, exist_ok=True)
        self.material = material
        self.geometry = geometry
        self.boundary = boundary
        self.mesh = mesh
        self.solver = solver

        # self._run_checks()

    # def _run_checks(self):
    #     pass


class SimulatorInfo(SimulatorPart):
    def __init__(self, fork: str, version: str, build_date: str):
        self.name = "opemFoam"
        self.fork = fork
        self.version = version
        self.build_date = build_date

    def to_dict(self) -> dict:
        return self.__dict__


# class FolderInfo:


# def combine_info(
#     abaqus_info: AbaqusInfo, simulation_info: SimulationInfo, folder_info: FolderInfo
# ) -> dict:
#     d = {}
#     d.update(abaqus_info.to_dict())
#     d.update(simulation_info.to_dict())
#     d.update(folder_info.to_dict())
#     return d
