#                                                                       Modules
# =============================================================================
# Standard
import os
import pickle
import subprocess
import time
from pathlib import Path
import psutil


# Third-party
from f3dasm.simulation import Simulator
from PyFoam import FoamInformation
from PyFoam.Basics.Utilities import execute
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.Applications.PrepareCase import PrepareCase


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
        self,
        simulation_info: SimulationInfo,
        # folder_info: FolderInfo,
        simulator_info: SimulatorInfo
        # case_source_path: str or Path,
        # case_name: str = None,
        # output_data_path: str = "jobs",
        # job_id: str or int = 0,
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
        """Handle the preprocessing thanks to pyfoam:
        1. Clone the case files (CloneCase utility)
        2. Prepare the case (PrepareCase utility)

        Note: see the pyfoam documentation for more details about the utilies

        Parameters
        ----------
        overwrite : bool
            If true, overwrite existing files at destination when cloning.
        """

        source = ModifiedSolutionDirectory(
            name=self.simulation_info.case_source_path.as_posix(),
            paraviewLink=False,
            addLocalConfig=True,
            parallel=False,
        )

        solution_dir = (
            self.simulation_info.output_data_path
            / f"{self.simulation_info.name}_{self.simulation_info.job_id}"
        )

        self.solution_dir = source.cloneCase(name=solution_dir.as_posix())

        # Create parameter files
        self.solution_dir.writeDictionaryContents(
            directory=".",
            name="default.parameters",
            contents=self.simulation_info.get_structured_parameters(),
        )

        args = [
            "--no-mesh-create",
            self.solution_dir.name,
        ]

        # For some reason, when used as a class, PrepareCase fails to initialize the
        # 0 directory. Thus, run as a shell command as for Abaqus simulator
        command = " ".join(["pyFoamPrepareCase.py"] + args)

        proc = subprocess.Popen(command, shell=True)

        proc.wait()

        self.pre_mesh()

        self.mesh()

        self.post_mesh()

    def execute(self, solver="auto", solver_options=[]) -> None:
        """Run"""

        # logic adapted from PyFoamApplication utility
        if solver == "auto":
            try:
                solver = self.solution_dir.getDictionaryContents(
                    "system", "controlDict"
                )["application"]
            except KeyError:
                print("No application specified in controDict.")

        # pyfoam is designed as a command line utility, hence options and args
        # should be formated as such
        argv = [solver, "-case", self.solution_dir.name] + solver_options

        runner = AnalyzedRunner(
            analyzer=BoundingLogAnalyzer(doFiles=True, singleFile=True),
            argv=argv,
            silent=True,
            logname=solver,
        )
        runner.start()

    def post_process(self) -> None:
        """Function that handles the post-processing"""
        ...
        argv = [
            "postProcess",
            "-case",
            self.solution_dir.name,
            "-func",
            "streamFunction",
        ]
        runner = BasicRunner(
            argv=argv,
            silent=True,
            jobId=self.simulation_info.job_id,
            logname="postProcess",
        )

        runner.start()

        error_field = self.solution_dir.getDictionaryContents(
            directory="0", name="error"
        )["internalField"].val

        self.results = dict(avg_error=sum(error_field) / len(error_field))

    def run(self) -> None:
        # better to call individual fucntion, kept for retro-compability
        self.pre_process()
        self.execute()
        self.post_process()

    def pre_mesh(self) -> None:
        # # logic adapted from ClearCase utility
        # allclean_path = Path(self.solution_dir.name).resolve() / "Allclean"

        # if allclean_path.is_file():
        #     print("Executing", allclean_path)
        #     execute(allclean_path.as_posix(), workdir=self.solution_dir.name)

        # self.solution_dir.clear(verbose=True)
        pass

    def mesh(self) -> None:
        if self.solution_dir.blockMesh() != "":
            # pyfoam is designed as a command line utility, hence options and args
            # should be formated as such
            argv = ["blockMesh", "-case", self.solution_dir.name]

            block_mesh_runner = BasicRunner(
                argv=argv,
                silent=True,
                jobId=self.simulation_info.job_id,
                logname="blockMesh",
            )

            block_mesh_runner.start()

            if not block_mesh_runner.runOK():
                self.error("Problem with blockMesh")

        else:
            self.error("Problem with blockMesh")

    def post_mesh(self) -> None:
        pass
