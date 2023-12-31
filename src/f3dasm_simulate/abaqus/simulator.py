"""
Simulator class for Abaqus
"""

#                                                                       Modules
# =============================================================================

# Standard
import os
import pickle
import subprocess
import time

# Third-party
from f3dasm.datageneration import DataGenerator

# Local
from .simulator_assertinputs import is_inputs_proper_defined
from .simulator_info import (AbaqusInfo, FolderInfo, SimulationInfo,
                             combine_info)
from .utils import create_dir, print_banner, write_json

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class AbaqusSimulator(DataGenerator):
    def __init__(self, simulation_info: SimulationInfo,
                 folder_info: FolderInfo,
                 abaqus_info: AbaqusInfo):
        # TODO: sim_info is a combination of simulation_info and abaqus_info, hence making it redundant
        self.folder_info = folder_info
        self.abaqus_info = abaqus_info
        self.abaqus_input_file = "sim_info.json"

        # Add the sim_path and sim_script to the sim_info
        self.folder_info.sim_path = simulation_info.sim_path
        self.folder_info.sim_script = simulation_info.sim_script

        self.sim_info = combine_info(abaqus_info=abaqus_info,
                                     simulation_info=simulation_info, folder_info=folder_info)

        is_inputs_proper_defined(
            folder_info=folder_info.to_dict(), sim_info=self.sim_info
        )

    def run(self,
            main_folder: str, *args
            ) -> dict:
        """run the simulation"""

        # save the current absolute path
        home_path: str = os.getcwd()

        # TODO: change to pre_process, execute, post_process order
        os.chdir(main_folder)

        self.pre_process(third_folder_name=self.folder_info.current_work_directory)
        self.execute()
        self.post_process()
        results = self.read_back_results()

        # change back to the home path
        os.chdir(home_path)

        return results

    def pre_process(self, folder_index: int = None,
                    sub_folder_index: int = None,
                    third_folder_name: str = 'case_0') -> None:
        # number of samples
        self._create_working_folder(
            folder_index,
            sub_folder_index,
            third_folder_name,
        )

    def execute(
        self,
        max_time: float = None,
        sleep_time: float = 20.0,
        refresh_time: float = 5.0,
    ) -> str:
        """Function that calls the FEM simulator the pre-processing"""

        # hidden name information
        abaqus_py_script = "abaScript.py"

        # write sim_info dict to a json file
        write_json(sim_info=self.sim_info, file_name=self.abaqus_input_file)

        # create new script for running abaqus simulation
        self.make_new_script(
            file_name=abaqus_py_script,
            status="simulation",
        )

        # run abaqus simulation and submit the job
        print_banner("start abaqus simulation")
        # system command for running abaqus
        command = "abaqus cae noGUI=" + str(abaqus_py_script) + " -mesa"

        # run (flag is for advanced usage)
        flag = self._run_abaqus_simulation(
            command=command,
            max_time=max_time,
            sleep_time=sleep_time,
            refresh_time=refresh_time,
        )

        return flag

    def post_process(self, delete_odb: bool = True) -> None:
        """post process

        Parameters
        ----------
        delete_odb : bool, optional
            delete odb file to save memory, by default True
        """

        if self.abaqus_info.platform == "ubuntu":
            print_banner("abaqus post analysis")
            # path with the python-script
            postprocess_script = "getResults.py"
            self.make_new_script(
                file_name=postprocess_script,
                status="post_process",
            )
            command = "abaqus cae noGUI=" + str(postprocess_script) + " -mesa"
            os.system(command)

            # remove files that influence the simulation process
            self.remove_files(directory=os.getcwd())

        # remove the odb file to save memory
        if delete_odb:
            self.remove_files(directory=os.getcwd(), file_types=[".odb"])

    def read_back_results(self, file_name: str = "results.p") -> dict:

        with open(file_name, "rb") as fd:
            results = pickle.load(fd, fix_imports=True, encoding="latin1")

        return results

    def _run_abaqus_simulation(
        self,
        command: str,
        max_time: float = None,
        sleep_time: float = 20.0,
        refresh_time: float = 5.0,
    ) -> str:

        if self.abaqus_info.platform == "ubuntu":

            proc = subprocess.Popen(command, shell=True)

            start_time = time.perf_counter()
            time.sleep(sleep_time)
            while True:

                time.sleep(
                    refresh_time - ((time.perf_counter() - start_time) % refresh_time)
                )
                end_time = time.perf_counter()
                #
                try:
                    file = open(self.abaqus_info.job_name + ".msg")
                    word1 = "THE ANALYSIS HAS BEEN COMPLETED"
                    if word1 in file.read():
                        proc.kill()
                        self.kill_abaqus_process()
                        flag = "finished"
                        break
                except Exception:
                    print(
                        "abaqus license is not enough,"
                        "waiting for license authorization"
                    )
                # over time killing
                if max_time is not None:
                    if (end_time - start_time) > max_time:
                        proc.kill()
                        self.kill_abaqus_process()
                        print("overtime kill")
                        flag = "killed"
                        break
            print(f"simulation time :{(end_time - start_time):2f} s")
            # remove files that influence the simulation process
            self.remove_files(directory=os.getcwd())

        elif self.abaqus_info.platform == "cluster":
            start_time = time.time()
            os.system(command)
            flag = "finished"
            end_time = time.time()
            print(f"simulation time :{(end_time - start_time):2f} s")

        else:
            raise NotImplementedError("platform not be implemented")

        return flag

    def make_new_script(
        self,
        file_name: str,
        status: str = "simulation",
    ) -> None:

        if status == "simulation":
            with open(file_name, "w") as file:
                file.write("import os \n")
                file.write("import sys \n")
                file.write("import json \n")
                file.write(
                    "sys.path.extend(['"
                    + str(self.folder_info.script_path)
                    + "']) \n"
                )
                file.write(
                    "from "
                    + str(self.folder_info.sim_path)
                    + " import "
                    + str(self.folder_info.sim_script)
                    + "\n"
                )
                line = "file = '" + str(self.abaqus_input_file) + "' \n"
                file.write(line)
                file.write("with open(file, 'r') as f:\n")
                file.write("	dict = json.load(f)\n")
                file.write(str(self.folder_info.sim_script) + "(dict)\n")
            file.close()
        elif status == "post_process":
            with open(file_name, "w") as file:
                file.write("import os\n")
                file.write("import sys\n")
                file.write(
                    "sys.path.extend(['"
                    + str(self.folder_info.script_path)
                    + "']) \n"
                )
                file.write(
                    "from "
                    + str(self.folder_info.post_path)
                    + " import "
                    + str(self.folder_info.post_script)
                    + "\n"
                )
                file.write(
                    str(self.folder_info.post_script)
                    + "('"
                    + str(self.abaqus_info.job_name)
                    + "')\n"
                )
            file.close()
        else:
            raise KeyError("provide correct status of simulation \n")

    @staticmethod
    def kill_abaqus_process() -> None:
        """kill abaqus simulation process"""
        standard_solver = "pkill standard"
        os.system(standard_solver)
        ABQcaeK = "pkill ABQcaeK"
        os.system(ABQcaeK)
        SMAPython = "pkill SMAPython"
        os.system(SMAPython)

    @staticmethod
    def remove_files(
        directory: str,
        file_types: list = [
            ".log",
            ".lck",
            ".SMABulk",
            ".rec",
            ".SMAFocus",
            ".exception",
            ".simlog",
            ".023",
            ".exception",
        ],
    ) -> None:
        """remove file

        Parameters
        ----------
        directory : str
            target folder
        file_type : str
            file name
        """
        # get all files in this folder
        all_files = os.listdir(directory)
        for target_file in file_types:
            # get the target file names
            filtered_files = [
                file for file in all_files if file.endswith(target_file)
            ]
            # remove the target files is existed
            for file in filtered_files:
                path_to_file = os.path.join(directory, file)
                if os.path.exists(path_to_file):
                    os.remove(path_to_file)

    def _create_working_folder(
        self,
        folder_index: int = None,
        sub_folder_index: int = None,
        third_folder_name: str = None,
    ) -> None:
        """create folders for excuting abaqus simulations

        Parameters
        ----------
        folder_index : int, optional
            first folder index , by default None
        sub_folder_index : _type_, optional
            second folder index , by default None
        third_folder_index : _type_, optional
            third folder index, by default None

        Raises
        ------
        ValueError
            provide sub_folder_index
        ValueError
            provide third_folder_index
        """
        if folder_index is None:
            if sub_folder_index is None:
                self.folder_info.current_work_directory = third_folder_name

            else:
                if third_folder_name is None:
                    self.folder_info.current_work_directory = "point_" + str(sub_folder_index)
                else:
                    self.folder_info.current_work_directory = (
                        "point_"
                        + str(sub_folder_index)
                        + "/"
                        + third_folder_name
                    )
        else:
            if sub_folder_index is None:
                raise ValueError("provide sub_folder_index")
            elif third_folder_name is None:
                raise ValueError("provide third_folder_index")
            else:
                self.folder_info.current_work_directory = (
                    "gen_"
                    + str(folder_index)
                    + "/point_"
                    + str(sub_folder_index)
                    + "/"
                    + third_folder_name
                )
        new_path = create_dir(
            current_folder=self.folder_info.main_work_directory,
            dir_name=self.folder_info.current_work_directory,
        )
        self.working_folder = new_path
        os.chdir(new_path)
