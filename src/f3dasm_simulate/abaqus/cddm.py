from .loading import Loading
from .material import CompositeMaterial, Material, PlasticMaterial
from .microstructure import Microstructure
from .simulator_info import SimulationInfo


class VonMisesPlasticElasticPathLoads(SimulationInfo):

    def __init__(self, material: Material,
                 microstructure: Microstructure, loading: Loading) -> None:
        """Class that contains the information to run a simulation with
        a composite material with two phases. The phases are assumed to be
        elastic or plastic. The plastic phase is assumed to be a von Mises
        material.

        Parameters
        ----------
        material
            material object
        microstructure
            microstructure object
        loading
            loading conditions
        """
        super().__init__(material=material, microstructure=microstructure,
                         loading=loading)

        # Reference to the python script that will be used to run the simulation
        self.sim_path = "benchmark_abaqus_scripts.two_materials_rve"
        self.sim_script = "VonMisesPlasticElasticPathLoads"

    def _run_checks(self) -> None:
        # Check if the material is not plastic
        if not isinstance(self.material, PlasticMaterial):
            assert ValueError("The material must be plastic.")

        # Check if we have a composite material
        if not isinstance(self.material, CompositeMaterial):
            assert ValueError("The material must be a composite.")

        # You can add more checks here
