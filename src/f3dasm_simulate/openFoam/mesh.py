from .simulator_part import ParametrizedPart


class Mesh(ParametrizedPart):
    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)
