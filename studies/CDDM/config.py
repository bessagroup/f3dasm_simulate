from dataclasses import dataclass

from f3dasm_simulate.abaqus.loading import Loading
from f3dasm_simulate.abaqus.material import Material
from f3dasm_simulate.abaqus.microstructure import Microstructure

@dataclass
class FileConfig:
    main_work_directory: str
    script_path: str
    current_work_directory: str
    post_path: str
    post_script: str


@dataclass
class AbaqusConfig:
    platform: str
    num_cpu: int
    print_info: bool
    simulation_time: float
    mesh_partition: int
    num_steps: int
    job_name: str


@dataclass
class Config:
    files: FileConfig
    microstructure: Microstructure
    material: Material
    loading: Loading
    abaqus: AbaqusConfig
    design: dict
