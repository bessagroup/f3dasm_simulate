import logging
from pathlib import Path

import hydra
from config import Config
from hydra.core.config_store import ConfigStore
from hydra.utils import instantiate

import f3dasm_simulate

cs = ConfigStore.instance()
cs.store(name="f3dasm_config", node=Config)

log = logging.getLogger(__name__)


@hydra.main(config_path=".", config_name="config")
def main(config: Config):

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
    simulator.run(main_folder=str(Path().absolute()))


if __name__ == "__main__":
    main()
