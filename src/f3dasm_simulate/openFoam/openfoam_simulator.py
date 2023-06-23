#                                                                       Modules
# =============================================================================
# Standard
import subprocess
from pathlib import Path
import logging

# Third-party
from f3dasm.simulation import Simulator
from PyFoam import FoamInformation
from PyFoam.Basics.Utilities import execute
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.Execution.BasicRunner import BasicRunner


# Local
from .simulator_info import SimulationInfo, SimulatorInfo
from .modified_solution_directory import ModifiedSolutionDirectory

#                                                          Authorship & Credits
# =============================================================================
__author__ = "Guillaume Broggi (g.broggi@tudelft.nl)"
__credits__ = ["Guillaume Broggi"]
__status__ = "Alpha"
# =============================================================================
#
# =============================================================================


class openFoamSimulator(Simulator):
    """openFoam simulator

    pyfoam documetation is available in the .tar source files:
    https://pypi.org/project/PyFoam/#files
    Parameters
    ----------
    Simulator : class
        simulator interface
    """

    # Get the path to openFoam tutorials
    foam_tutorial_path = Path(FoamInformation.foamTutorials())

    def __init__(
        self, simulation_info: SimulationInfo, simulator_info: SimulatorInfo
    ) -> None:
        """Constructor.

        Parameters
        ----------
        case_source_path : str or Path
            Path to the template case directory.

        """
        self.simulation_info = simulation_info
        self.simulator_info = simulator_info

    def pre_process(self, overwrite=True) -> None:
        """Handle the preprocessing thanks to FyFoam:
        1. Clone the case files (CloneCase utility)
        2. Prepare the case (PrepareCase utility)

        Note: see the pyfoam documentation for more details about the utilies

        Parameters
        ----------
        overwrite : bool
            If true, overwrite existing files at destination when cloning.
        """

        # Prepare the files
        source = ModifiedSolutionDirectory(
            name=self.simulation_info.case_source_path.as_posix(),
            paraviewLink=False,
            addLocalConfig=True,
            parallel=False,
        )

        job_name = f"{self.simulation_info.name}_{self.simulation_info.job_id}"

        self.job_path = self.simulation_info.output_data_path / job_name

        logging.info(f"Starting job {job_name} at {self.job_path}")

        self.solution_dir = source.cloneCase(name=self.job_path.as_posix())

        if not self.simulator_info.preprocessors:
            logging.info(
                "The simulator pipeline does not contain preprocessors components."
            )

        for preprocessor in self.simulator_info.preprocessors:
            # Run additional pre functions provided by users, pass otherwise
            try:
                preprocessor["pre_func"](self)
            except KeyError:
                pass

            try:
                if (
                    preprocessor["preprocessor"] == ""
                    or not preprocessor["preprocessor"]
                ):
                    error_msg = "No preprocessor specified."
                    logging.exception(error_msg)
                    raise ValueError(error_msg)

                if not preprocessor["options"]:
                    preprocessor["options"] = []

            except KeyError as e:
                error_msg = "A preprocessor is specified as a dict containing preprocessor and options keys."
                logging.exception(error_msg)
                raise ValueError(error_msg) from e

            if preprocessor["preprocessor"] == "prepareCase":
                # Create parameter files
                self.solution_dir.writeDictionaryContents(
                    directory=".",
                    name="default.parameters",
                    contents=self.simulation_info.get_structured_parameters(),
                )

                args = preprocessor["options"] + [self.job_path.as_posix()]

                # When used as a class, PrepareCase fails to initialize the 0 directory (bug?)
                # Thus, run as a shell command as for Abaqus simulator
                command = " ".join(["pyFoamPrepareCase.py"] + args)

                with open(self.job_path / "prepareCase.logfile", "w") as logfile:
                    proc = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=logfile,
                    )

                # wait for the process to be executed
                proc.wait()

            else:
                argv = [
                    preprocessor["preprocessor"],
                    "-case",
                    self.job_path.as_posix(),
                ] + preprocessor["options"]

                preprocessor_runner = BasicRunner(
                    argv=argv,
                    silent=True,
                    logname=preprocessor["preprocessor"],
                    jobId=self.simulation_info.job_id,
                )

                preprocessor_runner.start()

                if not preprocessor_runner.runOK():
                    logfile = (
                        self.job_path / f"{preprocessor['preprocessor']}.logfile"
                    ).as_posix()
                    error_msg = f"{preprocessor['preprocessor']} preprocessor failed. Check the logs: {logfile}"
                    logging.exception(error_msg)
                    raise Exception(error_msg)

                # Run additional post functions provided by users, pass otherwise
                try:
                    preprocessor["post_func"](self)
                except KeyError:
                    pass

    def execute(self) -> None:
        """Run"""

        if not self.simulator_info.solvers:
            logging.info("The simulator pipeline does not contain solver components.")

        for solver in self.simulator_info.solvers:
            # Run additional pre functions provided by users, pass otherwise
            try:
                solver["pre_func"](self)
            except KeyError:
                pass

            try:
                if solver["solver"] == "" or not solver["solver"]:
                    logging.info(
                        "No openFoam solver specified. Switching to 'auto' mode."
                    )
                    solver["solver"] = "auto"

                if not solver["options"]:
                    solver["options"] = []

            except KeyError as e:
                error_msg = "A solver is specified as a dict containing solver and options keys."
                logging.exception(error_msg)
                raise ValueError(error_msg) from e

            # logic adapted from PyFoamApplication utility
            # if solver is not auto it means it was specified
            # solvers available with an openFoam setup are variable
            # if a given solver is not available the runner will fail and the infomation
            # will be made available through openFoam logs
            if solver["solver"] == "auto":
                try:
                    solver["solver"] = self.solution_dir.getDictionaryContents(
                        "system", "controlDict"
                    )["application"]
                    if solver["solver"]:
                        logging.info(
                            f"Automatic mode will use {solver['solver']} solver."
                        )
                    else:
                        raise ValueError("Solver cannot be None.")

                except (KeyError, ValueError) as e:
                    error_msg = f"Automatic mode failed: no application specified in \
                          {(self.job_path /'system'/'controlDict').as_posix()}"
                    logging.exception(error_msg)
                    raise ValueError(error_msg) from e

            # pyfoam is designed as a command line utility, hence options and args
            # should be formated as such
            argv = [solver["solver"], "-case", self.job_path.as_posix()] + solver[
                "options"
            ]

            if self.simulator_info.running_mode == "analyze":
                solver_runner = AnalyzedRunner(
                    analyzer=BoundingLogAnalyzer(doFiles=True, singleFile=True),
                    argv=argv,
                    silent=True,
                    logname=solver["solver"],
                    jobId=self.simulation_info.job_id,
                )
            elif self.simulator_info.running_mode == "basic":
                solver_runner = BasicRunner(
                    argv=argv,
                    silent=True,
                    logname=solver["solver"],
                    jobId=self.simulation_info.job_id,
                )

            else:
                error_msg = f"Running mode can be analyze or basic,\
                      not {self.simulator_info.running_mode}."
                logging.exception(error_msg)
                raise ValueError(error_msg)

            solver_runner.start()

            if not solver_runner.runOK():
                error_msg = f"{solver['solver']} solver failed. Check the logs: {(self.job_path /({solver['solver']}+ '.logfile')).as_posix()}"
                logging.exception(error_msg)
                raise Exception(error_msg)

            # Run additional post functions provided by users, pass otherwise
            try:
                solver["post_func"](self)
            except KeyError:
                pass

    def post_process(self) -> None:
        """Function that handles the post-processing"""

        if not self.simulator_info.postprocessors:
            logging.info(
                "The simulator pipeline does not contain postprocessor components."
            )

        for postprocessor in self.simulator_info.postprocessors:
            # Run additional pre functions provided by users, pass otherwise
            try:
                postprocessor["pre_func"](self)
            except KeyError:
                pass

            try:
                if (
                    postprocessor["postprocessor"] == ""
                    or not postprocessor["postprocessor"]
                ):
                    error_msg = "No postprocessor specified."
                    logging.exception(error_msg)
                    raise ValueError(error_msg)

                if not postprocessor["options"]:
                    postprocessor["options"] = []

            except KeyError as e:
                error_msg = "A postprocessor is specified as a dict containing postprocessor and options keys."
                logging.exception(error_msg)
                raise ValueError(error_msg) from e

            argv = [
                postprocessor["postprocessor"],
                "-case",
                self.job_path.as_posix(),
            ] + postprocessor["options"]

            postprocessor_runner = BasicRunner(
                argv=argv,
                silent=True,
                logname=postprocessor["postprocessor"],
                jobId=self.simulation_info.job_id,
            )

            postprocessor_runner.start()

            if not postprocessor_runner.runOK():
                error_msg = f"{postprocessor['postprocessor']} postprocessor failed. Check the logs: {(self.job_path  /({postprocessor['postprocessor']}+ '.logfile')).as_posix()}"
                logging.exception(error_msg)
                raise Exception(error_msg)

            # Run additional post functions provided by users, pass otherwise
            try:
                postprocessor["post_func"](self)
            except KeyError:
                pass
