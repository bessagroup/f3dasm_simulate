from .loading import Loading
from .material import CompositeMaterial, Material, PlasticMaterial
from .microstructure import Microstructure
from .simulator_info import SimulatorInfo


class VonMisesPlasticElasticPathLoads(SimulatorInfo):
    def __init__(self, material: Material,
                 microstructure: Microstructure, loading: Loading):
        super().__init__(material, microstructure, loading)

        # Reference to the python script that will be used to run the simulation
        self.sim_path = "benchmark_abaqus_scripts.two_materials_rve"
        self.sim_script = "VonMisesPlasticElasticPathLoads"

    def _run_checks(self):
        # Check if the material is not plastic
        if not isinstance(self.material, PlasticMaterial):
            assert ValueError("The material must be plastic.")

        # Check if we have a composite material
        if not isinstance(self.material, CompositeMaterial):
            assert ValueError("The material must be a composite.")

        # You can add more checks here
