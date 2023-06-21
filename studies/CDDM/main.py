#                                                                       Modules
# =============================================================================

# Standard
import logging
from time import sleep
from typing import Callable

# Third-party
import f3dasm
import hydra
from abaqus_cddm import execute
from config import Config
from hydra.core.config_store import ConfigStore
from hydra.utils import instantiate

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
        data = f3dasm.ExperimentData.from_csv(
            filename=f"{config.experimentdata.existing_data_path}/{config.experimentdata.name}")
        job_queue = f3dasm.experiment.JobQueue.from_json(
            json_filename=config.hpc.jobqueue_filename, path=config.experimentdata.existing_data_path)

    # Else, create the dataset
    else:
        # Create the DesignSpace
        # List comprehension with instantiate
        # Workaround: (https://github.com/facebookresearch/hydra/issues/1950)
        input_space = [instantiate(i) for i in config.design.input_space]
        output_space = [instantiate(i) for i in config.design.output_space]
        design = f3dasm.DesignSpace(input_space, output_space)

        # Create the sampler from the hydra yaml file
        sampler_name = f3dasm.sampling.find_sampler(config.experimentdata.sampler)
        sampler: f3dasm.Sampler = sampler_name(design=design, seed=config.experimentdata.seed)

        # Create samples and ExperimentData object
        data = sampler.get_samples(numsamples=config.experimentdata.number_of_samples)

        # Create the JobQueue object
        job_queue = f3dasm.experiment.JobQueue.from_experimentdata(
            filename=config.hpc.jobqueue_filename, experimentdata=data)

    # Store the ExperimentData to a csv file
    data.store(config.experimentdata.name)

    # Write the JobQueue object to a file
    job_queue.write_new_jobfile()


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


def job(config: Config, execute_callable: Callable):
    """Main script that handles the execution of open jobs

    Parameters
    ----------
    config
        Hydra configuration file object
    execute_callable
        function to execute a job. Requires to arguments; the config and any **kwargs from the design
    """

    # Retrieve the queue
    job_queue = f3dasm.experiment.JobQueue(filename=config.hpc.jobqueue_filename)

    # Let the node repeat the execution of jobs
    while True:
        try:
            jobnumber = job_queue.get()
        except f3dasm.experiment.NoOpenJobsError:
            logging.info("There are no open jobs left!")
            break

        data = f3dasm.ExperimentData.from_csv(filename=config.experimentdata.name)
        designparameters = data.get_inputdata_by_index(jobnumber)

        try:
            returnvalue = execute_callable(config, jobnumber, designparameters)
            job_queue.mark_finished(jobnumber)
        except Exception as e:
            logging.exception(f"An exception of type {type(e).__name__} occurred: {e}")
            returnvalue = 'ERROR'
            job_queue.mark_error(jobnumber)

        data.write_outputdata_by_index(filename=config.experimentdata.name, index=jobnumber, value=returnvalue)


cs = ConfigStore.instance()
cs.store(name="f3dasm_config", node=Config)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
