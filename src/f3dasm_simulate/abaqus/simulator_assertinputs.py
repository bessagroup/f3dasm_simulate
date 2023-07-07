"""
AssertInputs class is used to assert the inputs of the simulator.
"""

#                                                                       Modules
# =============================================================================

#                                                        Authorship and Credits
# =============================================================================
__author__ = 'Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling', 'Jiaxiang Yi']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def is_inputs_proper_defined(folder_info: dict, sim_info: dict) -> None:
    is_mwd_in_folder_info(folder_info=folder_info)
    is_script_path_in_folder_info(folder_info=folder_info)
    is_cwd_in_folder_info(folder_info=folder_info)
    is_sim_path_in_folder_info(folder_info=folder_info)
    is_sim_script_in_folder_info(folder_info=folder_info)
    is_post_path_in_folder_info(folder_info=folder_info)
    is_post_script_in_folder_info(folder_info=folder_info)
    is_job_name_in_sim_info(sim_info=sim_info)
    is_platform_in_sim_info(sim_info=sim_info)


def is_mwd_in_folder_info(folder_info: dict) -> None:
    assert (
        "main_work_directory" in folder_info.keys()
    ), "main_work_directory should in folder_info dict"


def is_script_path_in_folder_info(folder_info: dict) -> None:
    assert (
        "script_path" in folder_info.keys()
    ), "script_path should in folder_info dict"


def is_cwd_in_folder_info(folder_info: dict) -> None:
    assert (
        "current_work_directory" in folder_info.keys()
    ), "current_work_directory should in folder_info dict"


def is_sim_path_in_folder_info(folder_info: dict) -> None:
    assert (
        "sim_path" in folder_info.keys()
    ), "sim_path should in folder_info dict"


def is_sim_script_in_folder_info(folder_info: dict) -> None:
    assert (
        "sim_script" in folder_info.keys()
    ), "sim_script should in folder_info dict"


def is_post_path_in_folder_info(folder_info: dict) -> None:
    assert (
        "post_path" in folder_info.keys()
    ), "post_path should in folder_info dict"


def is_post_script_in_folder_info(folder_info: dict) -> None:
    assert (
        "post_script" in folder_info.keys()
    ), "post_script should in folder_info dict"


def is_job_name_in_sim_info(sim_info: dict) -> None:
    assert (
        "job_name" in sim_info.keys()
    ), "job_name should in folder_info dict"


def is_platform_in_sim_info(sim_info: dict) -> None:
    assert (
        "platform" in sim_info.keys()
    ), "platform should in folder_info dict"
