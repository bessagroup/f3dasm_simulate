import logging
from pathlib import Path

from config import Config
from f3dasm import Design
from hydra.utils import instantiate
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig

import f3dasm_simulate


def combine_config_and_designparameters(config: Config, designparameters: dict) -> DictConfig:

    # convert Config to a ConfigDictdict
    config_ = OmegaConf.structured(config)

    # Combine the design parameters with the config parameters
    config_ = f3dasm_simulate.abaqus.overwrite_inputs.overwrite_config_with_design_parameters(
        config=config_, design_dict=designparameters)

    # convert dict back to Config
    config_ = OmegaConf.create(config_)

    return config_


def execute(design: Design, config: Config) -> Design:

    input_values = design.input_data

    config = combine_config_and_designparameters(config=config, designparameters=input_values)

    # Combine the design parameters with the config parameters
    config = f3dasm_simulate.abaqus.overwrite_inputs.overwrite_config_with_design_parameters(
        config=config, design_dict=input_values)

    # Set the current work directory to the jobnumber
    config.files.current_work_directory = f"case_{design.job_number}"

    # Create the simulation_info
    material = instantiate(config.material)
    microstructure = instantiate(config.microstructure)
    loading = instantiate(config.loading)
    abaqus_info = f3dasm_simulate.abaqus.simulator_info.AbaqusInfo(**config.abaqus)
    folder_info = f3dasm_simulate.abaqus.simulator_info.FolderInfo(**config.files)

    simulation_info = f3dasm_simulate.abaqus.VonMisesPlasticElasticPathLoads(
        material=material, microstructure=microstructure, loading=loading)

    # Create the simulator
    simulator = f3dasm_simulate.abaqus.simulator.AbaqusSimulator(
        simulation_info=simulation_info, folder_info=folder_info, abaqus_info=abaqus_info)

    # Run the simulator
    simulator.run(main_folder=str(Path()))

    logging.info(f"case_{design.job_number} finished")

    design['status'] = folder_info.current_work_directory
    # Return the working directory name
    return design
