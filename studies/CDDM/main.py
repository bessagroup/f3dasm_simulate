#                                                                       Modules
# =============================================================================

# Standard
import logging
from time import sleep
from typing import Callable

# Third-party
import f3dasm
import hydra
import pandas as pd
from abaqus_cddm import execute
from config import Config
from f3dasm.logger import logger
from hydra.core.config_store import ConfigStore

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def initial_script(config: Config):
    # Check if we use an existing dataset
    if config.experimentdata.existing_data_path is not False:
        data = f3dasm.ExperimentData.from_file(
            filename=f"{config.experimentdata.existing_data_path}/{config.experimentdata.name}")

    # Else, create the dataset
    else:
        # Create the DesignSpace
        domain = f3dasm.Domain.from_yaml(config.domain)

        # Create the four tasks
        task_a = {'vol_req': 0.45, 'radius_mu': 0.01, 'radius_std': 0.003, 'youngs_modulus': 10,
                  '_target_': 'f3dasm_simulate.abaqus.material.LinearHardeningLaw', 'a': 0.5,
                  'b': 0.5, 'yield_stress': 0.5}
        task_b = {'vol_req': 0.30, 'radius_mu': 0.003, 'radius_std': 0.0, 'youngs_modulus': 1,
                  '_target_': 'f3dasm_simulate.abaqus.material.SwiftHardeningLaw', 'a': 0.5,
                  'b': 0.4, 'yield_stress': 0.5}
        task_c = {'vol_req': 0.15, 'radius_mu': 0.0015, 'radius_std': 0.00005, 'youngs_modulus': 1000,
                  '_target_': 'f3dasm_simulate.abaqus.material.LinearHardeningLaw', 'a': 0.5,
                  'b': 0.4, 'yield_stress': 0.5}
        task_d = {'vol_req': 0.30, 'radius_mu': 0.003, 'radius_std': 0.0, 'youngs_modulus': 1,
                  '_target_': 'f3dasm_simulate.abaqus.material.LinearHardeningLaw', 'a': 0.5,
                  'b': 0.4, 'yield_stress': 3.0}

        # creata a list of tasks where each task is a dictionary of task_a plus a seed number
        seed = range(config.sampler.number_of_samples)
        tasks_a = [{'seed': s, **task_a} for s in seed]
        tasks_b = [{'seed': s, **task_b} for s in seed]
        tasks_c = [{'seed': s, **task_c} for s in seed]
        tasks_d = [{'seed': s, **task_d} for s in seed]

        # combine the lists (big table with all tasks)
        tasks = tasks_a + tasks_b + tasks_c + tasks_d
        tasks_numpy = pd.DataFrame(tasks).to_numpy()

        # Create empty data object
        data = f3dasm.ExperimentData(domain)

        # Fill the data object
        data.add_numpy_arrays(input=tasks_numpy)

        # Open up all the jobs
        data.jobs.mark_all_open()

    # Store the ExperimentData to a csv file
    data.store(config.experimentdata.name)


@hydra.main(config_path=".", config_name="config")
def main(config: Config):
    """Main script to call

    Parameters
    ----------
    config
        Configuration parameters defined in config.yaml
    """
    # Execute the initial_script for the first job
    if config.hpc.jobid == 0:
        initial_script(config)

    elif config.hpc.jobid == -1:  # Sequential
        initial_script(config)
        job(config, execute)

    else:
        sleep(3*config.hpc.jobid)  # Just to asynchronize the jobs
        job(config, execute)


def job(config: Config, execute_callable: Callable) -> None:
    logger.setLevel(logging.DEBUG)
    data = f3dasm.ExperimentData.from_file(filename=config.experimentdata.name)
    logger.debug('Start job execution')
    data.run(execute_callable, mode='sequential', kwargs={'config': config})

    # After finishing, store the ExperimentData to a csv file
    data.store(config.experimentdata.name)


cs = ConfigStore.instance()
cs.store(name="f3dasm_config", node=Config)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
