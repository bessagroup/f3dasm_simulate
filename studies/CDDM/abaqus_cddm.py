import logging
import os

from config import Config
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


def execute(config: Config, jobnumber: int, designparameters: dict):

    config = combine_config_and_designparameters(config=config, designparameters=designparameters)

    # Combine the design parameters with the config parameters
    config = f3dasm_simulate.abaqus.overwrite_inputs.overwrite_config_with_design_parameters(
        config=config, design_dict=designparameters)

    # Set the current work directory to the jobnumber
    config.files.current_work_directory = f"case_{jobnumber}"

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
    simulator.run(main_folder=os.path.dirname(f3dasm_simulate.__file__))

    logging.info(f"case_{jobnumber} finished")

    return folder_info.current_work_directory
