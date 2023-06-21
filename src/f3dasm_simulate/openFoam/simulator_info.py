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

#                                                        Authorship and Credits
# =============================================================================
__author__ = "Guillaume Broggi (g.broggi@tudelft.nl)"
__credits__ = ["Guillaume Broggi"]
__status__ = "Alpha"
# =============================================================================
#
# =============================================================================


class SimulationInfo:
    def __init__(
        self,
        material: Material,
        geometry: Geometry,
        boundary: Boundary,
        mesh: Mesh,
        solver: Solver,
    ):
        self.material = material
        self.geometry = geometry
        self.boundary = boundary
        self.mesh = mesh
        self.solver = solver

        # Location of the scripts
        self.sim_path = None
        self.sim_script = None

        self._run_checks()

    def _run_checks(self):
        pass

    def to_dict(self) -> dict:
        sim_info = {
            k: v
            for part in (
                self.material,
                self.geometry,
                self.boundary,
                self.mesh,
                self.solver,
            )
            for k, v in part.to_dict().items
        }
        sim_info: dict = {}

        return sim_info


class openFoamInfo:
    def __init__(self, fork: str, version: str, build_date: str):
        self.fork = fork
        self.version = version
        self.build_date = build_date

    def to_dict(self) -> dict:
        return self.__dict__


class FolderInfo:
    def __init__(self, case_source_path: Path, output_data_path: Path = Path("jobs")):
        self.case_source_path = case_source_path.resolve()
        self.output_data_path = output_data_path.resolve()
        self.output_data_path.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        return self.__dict__


# def combine_info(
#     abaqus_info: AbaqusInfo, simulation_info: SimulationInfo, folder_info: FolderInfo
# ) -> dict:
#     d = {}
#     d.update(abaqus_info.to_dict())
#     d.update(simulation_info.to_dict())
#     d.update(folder_info.to_dict())
#     return d
