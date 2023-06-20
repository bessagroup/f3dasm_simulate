#                                                                       Modules
# =============================================================================
# Standard
import os
import pickle
import subprocess
import time
from pathlib import Path

# Third-party
from PyFoam import FoamInformation
from PyFoam.Basics.Utilities import execute
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.BasicRunner import BasicRunner


# Local
from .simulator import Simulator

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
        case_source_path: str or Path,
        case_name: str = None,
        output_data_path: str = "jobs",
        job_id: str or int = 0,
    ) -> None:
        """Constructor.

        Parameters
        ----------
        case_source_path : str or Path
            Path to the template case directory.

        """
        self.case_source_path = Path(case_source_path).resolve()

        if not case_name:
            self.case_name = self.case_source_path.stem
        else:
            self.case_name = case_name

        self.output_data_path = Path(output_data_path).resolve()
        self.output_data_path.mkdir(parents=True, exist_ok=True)

        self.job_id = job_id

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

        source = SolutionDirectory(
            name=self.case_source_path.as_posix(),
            paraviewLink=False,
            addLocalConfig=True,
            parallel=False,
        )

        solution_dir = self.output_data_path / f"{self.case_name}_{self.job_id}"

        self.solution_dir = source.cloneCase(name=solution_dir.as_posix())

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
            argv=argv, silent=True, jobId=self.job_id, logname="postProcess"
        )

        runner.start()

    def run(self) -> None:
        # better to call individual fucntion, kept for retro-compability
        self.pre_process()
        self.execute()
        self.post_process()

    def pre_mesh(self) -> None:
        # logic adapted from ClearCase utility
        allclean_path = Path(self.solution_dir.name).resolve() / "Allclean"

        if allclean_path.is_file():
            print("Executing", allclean_path)
            execute(allclean_path.as_posix(), workdir=self.solution_dir.name)

        self.solution_dir.clear(verbose=True)

    def mesh(self) -> None:
        if self.solution_dir.blockMesh() != "":
            # pyfoam is designed as a command line utility, hence options and args
            # should be formated as such
            argv = ["blockMesh", "-case", self.solution_dir.name]

            block_mesh_runner = BasicRunner(
                argv=argv, silent=True, jobId=self.job_id, logname="blockMesh"
            )

            block_mesh_runner.start()

            if not block_mesh_runner.runOK():
                self.error("Problem with blockMesh")

        else:
            self.error("Problem with blockMesh")

    def post_mesh(self) -> None:
        pass
