from dataclasses import dataclass
from typing import Dict, Union


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
class DesignConfig:
    input_space: Dict
    output_space: Dict


@dataclass
class HPCConfig:
    jobid: int
    jobqueue_filename: str


@dataclass
class ExperimentConfig:
    existing_data_path: Union[bool, str]
    name: str
    sampler: str
    seed: int
    number_of_samples: int


@dataclass
class Config:
    files: FileConfig
    microstructure: dict
    material: dict
    loading: dict
    abaqus: AbaqusConfig
    design: DesignConfig
    hpc: HPCConfig
    experimentdata: ExperimentConfig
