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
        job_id: str or int = 0,
    ):
        self.case_source_path = case_source_path.resolve()
        self.output_data_path = output_data_path.resolve()

        self.material = material
        self.geometry = geometry
        self.boundary = boundary
        self.mesh = mesh
        self.solver = solver

        if not name:
            self.name = self.case_source_path.stem
        else:
            self.name = name

        self.job_id = job_id

        self._prepare_filesytem()

    def _prepare_filesytem(self):
        self.output_data_path.mkdir(parents=True, exist_ok=True)


class SimulatorInfo(SimulatorPart):
    def __init__(
        self,
        fork: str,
        version: str,
        build_date: str,
        preprocessors: list or None = None,
        solvers: list or None = None,
        postprocessors: list or None = None,
        running_mode: str = "analyze",
        name: str = "openFoam",
    ):
        self.name = name
        self.fork = fork
        self.version = version
        self.build_date = build_date

        if preprocessors:
            self.preprocessors = preprocessors
        else:
            self.preprocessors = list()

        if solvers:
            self.solvers = solvers
        else:
            self.solvers = list()

        if solvers:
            self.postprocessors = postprocessors
        else:
            self.postprocessors = list()

        self.running_mode = running_mode
