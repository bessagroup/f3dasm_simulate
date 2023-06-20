"""
Example module
"""

#                                                                       Modules
# =============================================================================

import os
# Standard
from pathlib import Path

import f3dasm_simulate

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


class SimulationInfo:
    def __init__(self, material: Material,
                 microstructure: Microstructure, loading: Loading):
        self.material = material
        self.microstructure = microstructure
        self.loading = loading

        # Location of the scripts
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

        sim_info['sim_path'] = self.sim_path
        sim_info['sim_script'] = self.sim_script
        return sim_info


class AbaqusInfo:
    def __init__(self, platform: str = "ubuntu", num_cpu: int = 1,
                 print_info: bool = False, simulation_time: float = 1.0,
                 mesh_partition: int = 50, num_steps: int = 100, job_name: str = "job"):
        self.platform = platform
        self.num_cpu = num_cpu
        self.print_info = print_info
        self.simulation_time = simulation_time
        self.mesh_partition = mesh_partition
        self.num_steps = num_steps
        self.job_name = job_name

    def to_dict(self) -> dict:
        return self.__dict__
        # return {'platform': self.platform,
        #         'num_cpu': self.num_cpu,
        #         'print_info': self.print_info,
        #         'simulation_time': self.simulation_time,
        #         'mesh_partition': self.mesh_partition,
        #         'num_steps': self.num_steps}


class FolderInfo:
    def __init__(
            self,
            main_work_directory: str = str(Path().absolute() / Path("Data")),
            script_path: str = os.path.dirname(f3dasm_simulate.__file__) + "/scriptbase",
            current_work_directory: str = 'case_0',
            post_path: str = "basic_analysis_scripts.post_process",
            post_script: str = "PostProcess2D"):

        # TODO: check this: os.path.dirname(rvesimulator.__file__) + "/scriptbase",
        self.main_work_directory = main_work_directory
        self.script_path = script_path
        self.current_work_directory = current_work_directory
        self.post_path = post_path
        self.post_script = post_script
        self.sim_path = None
        self.sim_script = None

    def to_dict(self) -> dict:
        return self.__dict__
        # return {'main_work_directory': self.main_work_directory,
        #         'script_path': self.script_path,
        #         'current_work_directory': self.current_work_directory,
        #         'post_path': self.post_path,
        #         'post_script': self.post_script}


def combine_info(abaqus_info: AbaqusInfo, simulation_info: SimulationInfo, folder_info: FolderInfo) -> dict:
    d = {}
    d.update(abaqus_info.to_dict())
    d.update(simulation_info.to_dict())
    d.update(folder_info.to_dict())
    return d
