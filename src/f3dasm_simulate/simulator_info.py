"""
Example module
"""

#                                                                       Modules
# =============================================================================

# Standard
from pathlib import Path

# Local
from .loading import Loading
from .material import Material
from .microstructure import Microstructure

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class SimulatorInfo:
    def __init__(self, material: Material,
                 microstructure: Microstructure, loading: Loading):
        self.material = material
        self.microstructure = microstructure
        self.loading = loading
        self.sim_path = None
        self.sim_script = None

        self._run_checks()

    def _run_checks(self):
        pass

    def to_dict(self) -> dict:
        sim_info: dict = {}

        sim_info.update(self.material.to_dict())
        sim_info.update(self.microstructure.to_dict())
        sim_info.update(self.loading.to_dict())
        return sim_info


class AbaqusInfo:
    def __init__(self, platform: str = "ubuntu", num_cpu: int = 1,
                 print_info: bool = False, simulation_time: float = 1.0,
                 mesh_partition: int = 50, num_steps: int = 100):
        self.platform = platform
        self.num_cpu = num_cpu
        self.print_info = print_info
        self.simulation_time = simulation_time
        self.mesh_partition = mesh_partition
        self.num_steps = num_steps

    def to_dict(self) -> dict:
        assert NotImplementedError("This method is not implemented yet.")


class FolderInfo:
    def __init__(
            self,
            main_work_directory: Path = Path().absolute() / Path("Data"),
            script_path: str = None,
            current_work_directory: str = None,
            post_path: str = "basic_analysis_scripts.post_process",
            post_script: str = "PostProcess2D"):

        # TODO: check this: os.path.dirname(rvesimulator.__file__) + "/scriptbase",
        self.main_work_directory = main_work_directory
        self.script_path = script_path
        self.current_work_directory = current_work_directory
        self.post_path = post_path
        self.post_script = post_script

    def to_dict(self) -> dict:
        assert NotImplementedError("This method is not implemented yet.")


def create_one_dictionary(folder_info: FolderInfo, abaqus_info: AbaqusInfo, simulation_info: SimulatorInfo) -> dict:
    d = {}
    d.update(folder_info.to_dict())
    d.update(abaqus_info.to_dict())
    d.update(simulation_info.to_dict())
    return d
